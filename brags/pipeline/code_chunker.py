"""Syntax-aware code chunking via tree-sitter.

Produces one chunk per function/method/constructor, plus a header-only chunk
(signature + any leading doc-comment, body excluded) per class/struct/
interface/enum/trait, so a class's own chunk doesn't duplicate the full text
of every method that's *also* emitted as its own chunk. Methods carry a
`class_name` metadata field pointing back to their enclosing container.

Files with no recognized definitions (plain scripts, __init__.py, etc.) fall
back to a single whole-file chunk, or -- if the file is large -- to
langchain's generic RecursiveCharacterTextSplitter, so nothing is silently
dropped from the index.
"""

import logging

from langchain.docstore.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger("CodeChunker")

# node types whose subtree a name search must never enter: parameter lists
# would otherwise surface an argument's identifier before a method's own
# name (e.g. Go's `func (g *Greeter) Greet()` -- the receiver parameter list
# `(g *Greeter)` precedes the method's own `field_identifier` in the parse
# tree), and body/argument containers can't contain the definition's own name.
_DESCEND_EXCLUDE = {
    "block", "compound_statement", "statement_block", "class_body",
    "body_statement", "declaration_list", "field_declaration_list",
    "parameter_list", "parameters", "formal_parameters", "method_parameters",
    "argument_list", "interface_body",
}

# subset of the above that specifically marks where a container's *body*
# starts, used to truncate class/struct/etc. chunks to their header.
_BODY_CONTAINER_TYPES = {
    "block", "compound_statement", "statement_block", "class_body",
    "body_statement", "declaration_list", "field_declaration_list",
    "interface_body",
}

# node types that hold a definition's own name, per language.
_NAME_NODE_TYPES = {
    "python": {"identifier"},
    "go": {"identifier", "field_identifier", "type_identifier"},
    "javascript": {"identifier", "property_identifier"},
    "typescript": {"identifier", "property_identifier", "type_identifier"},
    "tsx": {"identifier", "property_identifier", "type_identifier"},
    "java": {"identifier"},
    "rust": {"identifier", "type_identifier"},
    "c": {"identifier", "type_identifier"},
    # "qualified_identifier" deliberately excluded: it's also the node type
    # tree-sitter uses for namespaced *return* types (e.g. `std::string
    # greet()` parses its `std::string` as a qualified_identifier too), so
    # including it here made in-class methods with a namespaced return type
    # pick up the return type as their "name" instead of the real one. Since
    # this leaf-name search never enters a function_definition's declarator
    # specifically (see _find_c_style_function_name below), out-of-line
    # `ClassName::method()` definitions won't get a name from this path --
    # a known limitation, not attempted here.
    "cpp": {"identifier", "field_identifier", "type_identifier"},
    "ruby": {"identifier", "constant"},
}

# node_type -> {symbol_type, container, emit}. `container` nodes get their
# body walked for nested definitions and get header-only chunk content;
# `emit: False` nodes (Rust's `impl` blocks) are walked purely for the
# class_name context they establish, without producing a chunk of their own.
_LANGUAGE_DEFS = {
    "python": {
        "class_definition": {"symbol_type": "class", "container": True, "emit": True},
        "function_definition": {"symbol_type": "function", "container": False, "emit": True},
    },
    "go": {
        "type_declaration": {"symbol_type": "type", "container": True, "emit": True},
        "function_declaration": {"symbol_type": "function", "container": False, "emit": True},
        "method_declaration": {"symbol_type": "method", "container": False, "emit": True},
    },
    "javascript": {
        "class_declaration": {"symbol_type": "class", "container": True, "emit": True},
        "function_declaration": {"symbol_type": "function", "container": False, "emit": True},
        "method_definition": {"symbol_type": "method", "container": False, "emit": True},
    },
    "typescript": {
        "class_declaration": {"symbol_type": "class", "container": True, "emit": True},
        "interface_declaration": {"symbol_type": "interface", "container": True, "emit": True},
        "function_declaration": {"symbol_type": "function", "container": False, "emit": True},
        "method_definition": {"symbol_type": "method", "container": False, "emit": True},
    },
    "java": {
        "class_declaration": {"symbol_type": "class", "container": True, "emit": True},
        "interface_declaration": {"symbol_type": "interface", "container": True, "emit": True},
        "method_declaration": {"symbol_type": "method", "container": False, "emit": True},
        "constructor_declaration": {"symbol_type": "method", "container": False, "emit": True},
    },
    "rust": {
        "struct_item": {"symbol_type": "struct", "container": True, "emit": True},
        "enum_item": {"symbol_type": "enum", "container": True, "emit": True},
        "trait_item": {"symbol_type": "trait", "container": True, "emit": True},
        "impl_item": {"symbol_type": "impl", "container": True, "emit": False},
        "function_item": {"symbol_type": "function", "container": False, "emit": True},
    },
    "c": {
        "struct_specifier": {"symbol_type": "struct", "container": True, "emit": True},
        "function_definition": {"symbol_type": "function", "container": False, "emit": True},
    },
    "cpp": {
        "class_specifier": {"symbol_type": "class", "container": True, "emit": True},
        "struct_specifier": {"symbol_type": "struct", "container": True, "emit": True},
        "function_definition": {"symbol_type": "function", "container": False, "emit": True},
    },
    "ruby": {
        "class": {"symbol_type": "class", "container": True, "emit": True},
        "method": {"symbol_type": "method", "container": False, "emit": True},
    },
}
_LANGUAGE_DEFS["tsx"] = _LANGUAGE_DEFS["typescript"]
_NAME_NODE_TYPES["tsx"] = _NAME_NODE_TYPES["typescript"]

SUPPORTED_LANGUAGES = sorted(_LANGUAGE_DEFS.keys())


def _find_name(node, name_types, exclude_types):
    for child in node.children:
        if child.type in name_types:
            return child.text.decode("utf-8", errors="replace")
    for child in node.children:
        if child.type in exclude_types:
            continue
        found = _find_name(child, name_types, exclude_types)
        if found:
            return found
    return None


_DECLARATOR_WRAPPER_TYPES = {"pointer_declarator", "reference_declarator", "array_declarator"}


def _find_declarator(node):
    """Find a C/C++ function_definition's function_declarator, unwrapping
    pointer/reference/array declarators (e.g. a function returning `char *`).
    """
    for child in node.children:
        if child.type == "function_declarator":
            return child
        if child.type in _DECLARATOR_WRAPPER_TYPES:
            found = _find_declarator(child)
            if found is not None:
                return found
    return None


def _find_go_receiver_type(node):
    """Go methods aren't syntactically nested inside their type the way
    Python/JS/Java methods are -- `func (g *Greeter) Greet() string` sits at
    file scope with the receiver as its first parameter list -- so class_name
    has to be pulled from the receiver instead of the class_stack.
    """
    receiver = next((c for c in node.children if c.type == "parameter_list"), None)
    if receiver is None:
        return None
    return _find_name(receiver, {"type_identifier"}, set())


def _find_c_style_function_name(node, name_types, exclude_types):
    """C/C++ function_definition's name search, scoped to the declarator only.

    A generic whole-node search would hit the return type before the real
    name for namespaced return types (`std::string greet()` parses its
    `std::string` as a qualified_identifier, colliding with name lookups
    that also treat qualified/type identifiers as names) -- restricting the
    search to just the declarator subtree sidesteps the collision entirely
    since the return type is never inside it.
    """
    declarator = _find_declarator(node)
    if declarator is None:
        return None
    return _find_name(declarator, name_types, exclude_types)


def _walk(node, language, defs, name_types, class_stack, source, path, out):
    node_def = defs.get(node.type)
    # Some grammars reuse a construct's node type for its own keyword token
    # too (Ruby's `class` node type names both the whole class-definition
    # construct AND its leading "class" keyword leaf) -- a leaf can never
    # legitimately be the definition itself, so require children.
    if node_def is not None and node.child_count == 0:
        node_def = None

    if node_def is not None:
        if language in ("c", "cpp") and node.type == "function_definition":
            name = _find_c_style_function_name(node, name_types, _DESCEND_EXCLUDE)
        else:
            name = _find_name(node, name_types, _DESCEND_EXCLUDE)
        symbol_type = node_def["symbol_type"]
        if not node_def["container"] and class_stack:
            symbol_type = "method"

        class_name = class_stack[-1] if class_stack else None
        if language == "go" and node.type == "method_declaration":
            class_name = _find_go_receiver_type(node)

        if node_def["emit"]:
            if node_def["container"]:
                body_child = next(
                    (c for c in node.children if c.type in _BODY_CONTAINER_TYPES), None
                )
                end = body_child.start_byte if body_child is not None else node.end_byte
                content = source[node.start_byte:end].decode("utf-8", errors="replace").rstrip()
            else:
                content = source[node.start_byte:node.end_byte].decode("utf-8", errors="replace")

            out.append(Document(
                page_content=content,
                metadata={
                    "source": path,
                    "language": language,
                    "symbol_name": name,
                    "symbol_type": symbol_type,
                    "class_name": class_name,
                    "start_line": node.start_point[0] + 1,
                    "end_line": node.end_point[0] + 1,
                },
            ))

        if node_def["container"]:
            class_stack.append(name)
            for child in node.children:
                _walk(child, language, defs, name_types, class_stack, source, path, out)
            class_stack.pop()
            return
        # leaf definitions (functions/methods) aren't walked further --
        # nested/inner function definitions are rare enough not to be worth
        # the added complexity here.
        return

    for child in node.children:
        _walk(child, language, defs, name_types, class_stack, source, path, out)


def chunk_source(source: bytes, language: str, path: str, chunk_size: int, chunk_overlap: int) -> list[Document]:
    """Parse `source` (in `language`) into one Document per definition found.

    Falls back to a whole-file chunk (or, for large files, a generic
    RecursiveCharacterTextSplitter pass) when no definitions are found.
    """
    if language not in _LANGUAGE_DEFS:
        raise ValueError(f"Unsupported code chunking language: {language}")

    import tree_sitter_language_pack as tsl

    parser = tsl.get_parser(language)
    tree = parser.parse(source)

    docs: list[Document] = []
    _walk(
        tree.root_node, language, _LANGUAGE_DEFS[language], _NAME_NODE_TYPES[language],
        [], source, path, docs,
    )

    if docs:
        return docs

    text = source.decode("utf-8", errors="replace")
    if not text.strip():
        return []

    if len(text) <= chunk_size:
        return [Document(
            page_content=text,
            metadata={
                "source": path, "language": language, "symbol_name": None,
                "symbol_type": "module", "class_name": None,
                "start_line": 1, "end_line": text.count("\n") + 1,
            },
        )]

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return [
        Document(
            page_content=chunk,
            metadata={
                "source": path, "language": language, "symbol_name": None,
                "symbol_type": "block", "class_name": None,
                "start_line": None, "end_line": None,
            },
        )
        for chunk in splitter.split_text(text)
    ]
