from tests import *

pytest.importorskip("tree_sitter_language_pack")

from brags.pipeline.code_chunker import chunk_source, SUPPORTED_LANGUAGES  # noqa: E402


PYTHON_SAMPLE = b'''class Greeter:
    """A simple greeter."""

    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, {self.name}!"


def standalone_function(x, y):
    return x + y
'''

GO_SAMPLE = b"""package main

type Greeter struct {
\tName string
}

func (g *Greeter) Greet() string {
\treturn "hi"
}

func StandaloneFunction(x, y int) int {
\treturn x + y
}
"""

CPP_METHOD_WITH_NAMESPACED_RETURN_TYPE = b"""class Greeter {
public:
    std::string greet() {
        return "hi";
    }
};
"""

RUBY_SAMPLE = b"""class Greeter
  def greet
    "hi"
  end
end
"""


class TestCodeChunker(unittest.TestCase):
    def test_supported_languages_include_core_set(self):
        for lang in ("python", "go", "javascript", "typescript", "java", "rust", "c", "cpp", "ruby"):
            self.assertIn(lang, SUPPORTED_LANGUAGES)

    def test_python_class_and_methods(self):
        docs = chunk_source(PYTHON_SAMPLE, "python", "sample.py", chunk_size=1500, chunk_overlap=100)
        by_name = {d.metadata["symbol_name"]: d for d in docs}

        self.assertEqual(by_name["Greeter"].metadata["symbol_type"], "class")
        self.assertIsNone(by_name["Greeter"].metadata["class_name"])
        # header-only: the class chunk must not duplicate its methods' bodies
        self.assertNotIn("def greet", by_name["Greeter"].page_content)

        self.assertEqual(by_name["greet"].metadata["symbol_type"], "method")
        self.assertEqual(by_name["greet"].metadata["class_name"], "Greeter")
        self.assertIn("Hello", by_name["greet"].page_content)

        self.assertEqual(by_name["standalone_function"].metadata["symbol_type"], "function")
        self.assertIsNone(by_name["standalone_function"].metadata["class_name"])

    def test_go_method_receiver_becomes_class_name(self):
        # Go methods aren't syntactically nested inside their type the way
        # Python/JS/Java methods are -- class_name has to be pulled from the
        # receiver `(g *Greeter)`, not from tree nesting.
        docs = chunk_source(GO_SAMPLE, "go", "sample.go", chunk_size=1500, chunk_overlap=100)
        by_name = {d.metadata["symbol_name"]: d for d in docs}

        self.assertEqual(by_name["Greeter"].metadata["symbol_type"], "type")
        self.assertEqual(by_name["Greet"].metadata["symbol_type"], "method")
        self.assertEqual(by_name["Greet"].metadata["class_name"], "Greeter")
        self.assertEqual(by_name["StandaloneFunction"].metadata["symbol_type"], "function")
        self.assertIsNone(by_name["StandaloneFunction"].metadata["class_name"])

    def test_cpp_method_name_not_confused_with_namespaced_return_type(self):
        # Regression test: tree-sitter parses `std::string` (the return type)
        # as a qualified_identifier, the same node type used for out-of-line
        # `Class::method` names -- a naive whole-node name search picked the
        # return type instead of "greet" for any in-class method with a
        # namespaced return type.
        docs = chunk_source(
            CPP_METHOD_WITH_NAMESPACED_RETURN_TYPE, "cpp", "sample.cpp", 1500, 100
        )
        by_name = {d.metadata["symbol_name"]: d for d in docs}
        self.assertIn("greet", by_name)
        self.assertNotIn("std::string", by_name)

    def test_ruby_class_keyword_token_does_not_produce_duplicate_chunk(self):
        # Regression test: Ruby's grammar reuses the "class" node type for
        # both the class-definition construct AND its own leading "class"
        # keyword leaf token, which without a child_count guard produced a
        # spurious second empty chunk for every class.
        docs = chunk_source(RUBY_SAMPLE, "ruby", "sample.rb", 1500, 100)
        class_chunks = [d for d in docs if d.metadata["symbol_type"] == "class"]
        self.assertEqual(len(class_chunks), 1)
        self.assertEqual(class_chunks[0].metadata["symbol_name"], "Greeter")

    def test_no_definitions_falls_back_to_whole_file_chunk(self):
        src = b"x = 1\ny = 2\n"
        docs = chunk_source(src, "python", "constants.py", chunk_size=1500, chunk_overlap=100)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].metadata["symbol_type"], "module")
        self.assertIn("x = 1", docs[0].page_content)

    def test_empty_file_produces_no_chunks(self):
        docs = chunk_source(b"", "python", "empty.py", chunk_size=1500, chunk_overlap=100)
        self.assertEqual(docs, [])

    def test_unsupported_language_raises(self):
        with self.assertRaises(ValueError):
            chunk_source(b"x", "not-a-real-language", "x.foo", 1500, 100)
