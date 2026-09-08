# AI-Avengers — Ashen Era Agentic Search
## SLIIT Codefest 2026 AI Competition

**Sub-track:** 1C — Searching the Way a Human Does  
**Demo Video:** [ADD UNLISTED YOUTUBE LINK AFTER RECORDING]

---

## 1. Problem Statement

The Ashen Era Archive contains hundreds of interconnected documents across PDF, DOCX, Markdown, plain text, and scanned formats.

Many questions cannot be answered using a single search because relevant facts may be spread across multiple documents, and different archive sources may disagree.

For Sub-track 1C, our goal was to build an assistant that searches iteratively like a human researcher: it retrieves evidence, evaluates whether the evidence is sufficient, identifies what is still missing, reformulates its search, and continues until it can produce a grounded answer.

---

## 2. Solution Overview

Our system uses an agentic multi-round document-search pipeline.

The process is:

```text
User Question
      |
      v
Initial Query Planner
      |
      v
Voyage Query Embedding
      |
      v
ChromaDB Retrieval
      |
      v
Voyage Reranking
      |
      v
Evidence Sufficiency Check
      |
      +----------------------+
      |                      |
 Insufficient             Sufficient
      |                      |
      v                      v
Query Rewriter         Answer Generator
      |
      v
Search Again