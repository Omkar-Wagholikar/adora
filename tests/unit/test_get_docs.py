import tempfile
from pathlib import Path

from tests import *

from brags.config_parser.data_types import ChunkingConfig, RAGConfig
from brags.pipeline.assembler import get_docs


def _splitter_config(splitter: str) -> RAGConfig:
    return ChunkingConfig(chunk_size=500, chunk_overlap=50, splitter=splitter)


class _StubConfig:
    def __init__(self, chunking):
        self.chunking = chunking


class TestGetDocsExtensionRouting(unittest.TestCase):
    def test_txt_file_is_ingested_as_text_not_pdf(self):
        # get_docs used to hardcode PDFPlumberLoader for every non-code
        # splitter regardless of the file's actual extension, so a plain
        # .txt file blew up with a pdfminer PDFSyntaxError instead of being
        # ingested -- even though "PDF, text, etc." is the advertised
        # --docs contract.
        with tempfile.TemporaryDirectory() as tmpdir:
            txt_path = Path(tmpdir) / "sample.txt"
            txt_path.write_text("The secret ingredient is paprika.")

            docs = get_docs(str(txt_path), _StubConfig(_splitter_config("semantic")))

        self.assertTrue(len(docs) >= 1)
        self.assertIn("paprika", "".join(d.page_content for d in docs))
