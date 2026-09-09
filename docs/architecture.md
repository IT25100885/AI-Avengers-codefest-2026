# System Architecture

## Overview

Ashen Era Agentic Search is a Track 1C system designed to search the document archive iteratively rather than relying on a single retrieval step.

The system searches for evidence, checks whether enough information has been found, identifies missing information, reformulates the search query, and searches again until sufficient evidence is available or the maximum number of rounds is reached.

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
Document Retrieval
  |
  v
Evidence Sufficiency Checker
  |
  +---------------------------+
  |                           |
  | Insufficient              | Sufficient
  v                           v
Query Rewriter          Answer Generator
  |                           |
  v                           v
Search Again            Final Answer
                              |
                              v
                       Sources / Citations