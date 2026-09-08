"""
test_member1.py
Comprehensive test suite for Member 1 deliverables:
- Ingestion loaders (PDF, DOCX, TXT, Markdown)
- Document chunker and metadata preservation
- Stable chunk ID generation
- ChromaDB persistence and duplicate prevention
- Retrieval interface and schema compliance
- Specific verification for "Gauntlet of Sorrowfell forging"
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from src.ingestion.docx_loader import load_docx
from src.ingestion.loader import load_corpus
from src.ingestion.markdown_loader import load_markdown
from src.ingestion.pdf_loader import load_pdf
from src.ingestion.text_loader import load_txt
from src.processing.chunker import (
    chunk_corpus,
    chunk_document,
    estimate_token_count,
)
from src.processing.metadata import build_chunk_metadata, generate_chunk_id
from src.retrieval.vector_store import ChromaVectorStore

CORPUS_ROOT = Path("data/corpus/Ashen_Era_Archive")


class TestDocumentLoaders(unittest.TestCase):
    """Verify all 4 document loaders preserve source, page, category, and doc_type."""

    def test_markdown_loader(self):
        md_file = CORPUS_ROOT / "wiki" / "gauntlet_of_sorrowfell.md"
        self.assertTrue(md_file.exists(), f"Missing test file: {md_file}")
        doc = load_markdown(md_file, category="wiki")
        self.assertEqual(doc["filename"], "gauntlet_of_sorrowfell.md")
        self.assertEqual(doc["category"], "wiki")
        self.assertEqual(doc["doc_type"], "markdown")
        self.assertIn("Gauntlet of Sorrowfell", doc["text"])
        # Wiki links should be normalized
        self.assertNotIn("[[", doc["text"])

    def test_pdf_loader_pages(self):
        pdf_file = CORPUS_ROOT / "codex" / "codex_vaeloria_ii_armory_of_relics_and_bestiary.pdf"
        self.assertTrue(pdf_file.exists(), f"Missing test file: {pdf_file}")
        pages = load_pdf(pdf_file, category="codex")
        self.assertGreater(len(pages), 10)
        # Check page 11 specifically for Gauntlet of Sorrowfell
        p11 = [p for p in pages if p["page"] == 11][0]
        self.assertEqual(p11["filename"], "codex_vaeloria_ii_armory_of_relics_and_bestiary.pdf")
        self.assertEqual(p11["category"], "codex")
        self.assertEqual(p11["doc_type"], "pdf")
        self.assertEqual(p11["page"], 11)
        self.assertIn("Gauntlet of Sorrowfell", p11["text"])
        self.assertIn("391 AS", p11["text"])

    def test_docx_loader(self):
        docx_file = (
            CORPUS_ROOT
            / "ephemera"
            / "quartermaster_ledger_concerning_gauntlet_of_sorrowfell.docx"
        )
        self.assertTrue(docx_file.exists(), f"Missing test file: {docx_file}")
        doc = load_docx(docx_file, category="ephemera")
        self.assertEqual(doc["category"], "ephemera")
        self.assertEqual(doc["doc_type"], "docx")
        self.assertIn("Quartermaster", doc["text"])
        self.assertIn("Gauntlet of Sorrowfell", doc["text"])

    def test_text_loader(self):
        txt_file = CORPUS_ROOT / "ephemera" / "field_report_concerning_gloamreach.txt"
        self.assertTrue(txt_file.exists(), f"Missing test file: {txt_file}")
        doc = load_txt(txt_file, category="ephemera")
        self.assertEqual(doc["category"], "ephemera")
        self.assertEqual(doc["doc_type"], "txt")
        self.assertGreater(len(doc["text"]), 50)


class TestChunkingAndMetadata(unittest.TestCase):
    """Verify chunk size, overlap, chunk ID stability, and metadata preservation."""

    def test_stable_chunk_id(self):
        cid1 = generate_chunk_id("document.pdf", page=5, chunk_idx=0)
        cid2 = generate_chunk_id("document.pdf", page=5, chunk_idx=0)
        self.assertEqual(cid1, cid2)
        self.assertEqual(cid1, "document_p5_c0")

        cid_nopage = generate_chunk_id("wiki_page.md", page=None, chunk_idx=2)
        self.assertEqual(cid_nopage, "wiki_page_p0_c2")

    def test_metadata_builder(self):
        meta = build_chunk_metadata(
            source="test.pdf",
            category="codex",
            doc_type="pdf",
            page=7,
            chunk_idx=1,
            total_chunks=3,
        )
        self.assertEqual(meta["source"], "test.pdf")
        self.assertEqual(meta["category"], "codex")
        self.assertEqual(meta["doc_type"], "pdf")
        self.assertEqual(meta["page"], 7)
        self.assertEqual(meta["chunk_idx"], 1)
        self.assertEqual(meta["total_chunks"], 3)

    def test_chunking_preserves_metadata(self):
        doc = {
            "filename": "sample_source.pdf",
            "category": "codex",
            "doc_type": "pdf",
            "page": 12,
            "text": "This is a sentence about ancient relics. " * 30,
        }
        chunks = chunk_document(doc)
        self.assertGreaterEqual(len(chunks), 1)
        for c in chunks:
            self.assertEqual(c["source"], "sample_source.pdf")
            self.assertEqual(c["category"], "codex")
            self.assertEqual(c["doc_type"], "pdf")
            self.assertEqual(c["page"], 12)
            self.assertIn("chunk_id", c)
            self.assertIn("metadata", c)

    def test_chunk_token_estimation(self):
        text = "word " * 500
        tokens = estimate_token_count(text)
        self.assertGreaterEqual(tokens, 500)
        self.assertLessEqual(tokens, 800)


class TestVectorStoreAndDeduplication(unittest.TestCase):
    """Verify ChromaDB persistence, querying, and duplicate prevention."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="chroma_test_")
        self.store = ChromaVectorStore(db_path=Path(self.test_dir), collection_name="test_col")

    def tearDown(self):
        del self.store
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_store_and_duplicate_prevention(self):
        chunks = [
            {
                "chunk_id": "item_1",
                "text": "The Gauntlet of Sorrowfell forged in 391 AS at Vharencrag Fortress.",
                "source": "codex.pdf",
                "page": 11,
                "category": "codex",
                "doc_type": "pdf",
                "metadata": {"source": "codex.pdf", "page": 11, "category": "codex", "doc_type": "pdf"},
            },
            {
                "chunk_id": "item_2",
                "text": "The Silent Choir stationed at Vharencrag Fortress.",
                "source": "wiki.md",
                "page": None,
                "category": "wiki",
                "doc_type": "markdown",
                "metadata": {"source": "wiki.md", "page": 0, "category": "wiki", "doc_type": "markdown"},
            },
        ]
        # 128-dim dummy embeddings
        emb1 = [0.1] * 128
        emb2 = [0.5] * 128
        embeddings = [emb1, emb2]

        # First insertion
        added = self.store.add_chunks(chunks, embeddings)
        self.assertEqual(added, 2)
        self.assertEqual(self.store.count(), 2)

        # Re-adding same chunks should add 0 (duplicate prevention)
        re_added = self.store.add_chunks(chunks, embeddings)
        self.assertEqual(re_added, 0)
        self.assertEqual(self.store.count(), 2)

        # Query testing
        results = self.store.query(query_embedding=emb1, n_results=2)
        self.assertEqual(len(results), 2)
        first = results[0]
        # Schema verification
        self.assertEqual(first["chunk_id"], "item_1")
        self.assertEqual(first["source"], "codex.pdf")
        self.assertEqual(first["page"], 11)
        self.assertEqual(first["category"], "codex")
        self.assertIn("score", first)
        self.assertIsInstance(first["score"], float)


class TestGauntletOfSorrowfellTarget(unittest.TestCase):
    """Specifically test: 'Gauntlet of Sorrowfell forging' extraction and metadata accuracy."""

    def test_gauntlet_forging_facts(self):
        # 1. Check codex page 11 (the primary authoritative source)
        pdf_path = CORPUS_ROOT / "codex" / "codex_vaeloria_ii_armory_of_relics_and_bestiary.pdf"
        pages = load_pdf(pdf_path, category="codex")
        p11 = [p for p in pages if p["page"] == 11][0]
        chunks11 = chunk_document(p11)

        self.assertTrue(any("Forged: 391 AS" in c["text"] for c in chunks11))
        self.assertTrue(any("Vharencrag Fortress" in c["text"] for c in chunks11))

        chunk = chunks11[0]
        self.assertEqual(chunk["source"], "codex_vaeloria_ii_armory_of_relics_and_bestiary.pdf")
        self.assertEqual(chunk["page"], 11)
        self.assertEqual(chunk["category"], "codex")
        self.assertEqual(chunk["doc_type"], "pdf")

        # 2. Check wiki article
        wiki_path = CORPUS_ROOT / "wiki" / "gauntlet_of_sorrowfell.md"
        wiki_doc = load_markdown(wiki_path, category="wiki")
        wiki_chunks = chunk_document(wiki_doc)
        self.assertTrue(any("Vharencrag Fortress" in c["text"] for c in wiki_chunks))
        self.assertEqual(wiki_chunks[0]["source"], "gauntlet_of_sorrowfell.md")
        self.assertEqual(wiki_chunks[0]["category"], "wiki")


if __name__ == "__main__":
    unittest.main()
