# System Architecture

## Overview

Ashen Era Agentic Search is a Track 1C system designed to perform iterative document research instead of relying on a single retrieval step.

The system searches the Ashen Era Archive, evaluates whether the retrieved evidence is sufficient, identifies missing information, reformulates the query when required, and continues searching until sufficient evidence is found or the maximum search-round limit is reached.

## High-Level Flow

```text
User
  |
  v
Streamlit UI
  |
  v
Search Agent
  |
  v
Initial Query Planner
  |
  v
Retrieval Pipeline
  |
  +--> Query Embedding (Voyage AI)
  |
  +--> ChromaDB Vector Search
  |
  +--> Voyage Reranking
  |
  v
Evidence Sufficiency Checker
  |
  +-------------------------------+
  |                               |
  | Insufficient                  | Sufficient
  v                               v
Query Rewriter              Answer Generator
  |                               |
  v                               v
Search Again                 Final Answer
                                  |
                                  v
                           Sources / Citations