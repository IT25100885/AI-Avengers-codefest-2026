# System Architecture

## 1. Overview

**Ashen Era Agentic Search** is an iterative, multi-hop research assistant built for **SLIIT Codefest 2026 Sub-Track 1C: "Searching the Way a Human Does"**.

Standard Retrieval-Augmented Generation (RAG) pipelines follow a single-shot paradigm: query in, vector similarity search, single LLM response. However, realistic archive research—such as investigating the fractured chronicles of the Ashen Era—requires dealing with:
- **Multi-hop dependencies**: E.g., discovering which organization a figure belonged to, and then finding what war that organization won.
- **Source conflicts and hedges**: Lower-authority summaries (wikis, rumors) that hedge key facts or contradict canonical records (codices, gazetteers).
- **Incomplete or unanswerable queries**: Recognizing when evidence is insufficient without hallucinating.

Our system mirrors human research behavior through a closed-loop reasoning process: planning targeted queries, evaluating evidence completeness, reformulating searches to close identified gaps, and synthesizing fully cited answers.

---

## 2. Architecture & Data Flow Diagram

```mermaid
flowchart TD
    subgraph UI["Presentation Layer (Streamlit UI)"]
        User(["User Input"]) --> InputBox["Question & Parameter Controls"]
        InputBox --> ModeToggle{"Execution Mode"}
        ModeToggle -->|Simulation Mode| SimEngine["Pre-recorded Deterministic Traces"]
        ModeToggle -->|Live Agent Pipeline| AgentCore["search_agent.py (Agent Controller)"]
    end

    subgraph Reasoning["Reasoning Agent Layer (Groq: openai/gpt-oss-120b)"]
        AgentCore --> Planner["src.agent.planner<br/>Initial Query Formulation"]
        Planner --> Loop{"Search Loop<br/>(Round <= max_rounds)"}
        
        Checker["src.agent.evidence_checker<br/>Sufficiency & Gap Analysis"]
        Checker --> StatusJudge{"Is Evidence<br/>Sufficient?"}
        
        StatusJudge -->|No Gap / Sufficient| Gen["src.generation.answer_generator<br/>Grounded Answer Synthesis"]
        StatusJudge -->|Gap Identified / Insufficient| Rewriter["src.agent.query_rewriter<br/>Targeted Query Reformulation"]
        Rewriter --> Loop
    end

    subgraph Retrieval["Retrieval Layer (ChromaDB + Voyage AI)"]
        Loop --> Embed["src.retrieval.embedder<br/>Voyage Query Embedding (voyage-4-lite)"]
        Embed --> Chroma["src.retrieval.vector_store<br/>ChromaDB Dense Vector Search"]
        Chroma --> Rerank["src.retrieval.reranker<br/>Voyage Reranker (voyage-3-large)"]
        Rerank -->|Top-5 Re-ranked Passages| Checker
    end

    subgraph Output["Response Delivery"]
        Gen --> FinalCard["Grounded Answer + Citations"]
        FinalCard --> UI_Display["Streamlit Timeline & Step Visualizer"]
        SimEngine --> UI_Display
    end
```

---

## 3. Detailed Multi-Round State Machine

The iterative research loop is governed by clear stopping rules, deduplication guards, and conflict-resolution heuristics.

```mermaid
stateDiagram-v2
    [*] --> InitialPlanning: User submits question
    InitialPlanning --> ExecuteRetrieval: Extract primary named entity / core concept
    
    state ExecuteRetrieval {
        [*] --> DenseRetrieval: Embed query via Voyage AI
        DenseRetrieval --> TopKCandidates: Query ChromaDB (Top-K=5)
        TopKCandidates --> SemanticReranking: Cross-encoder rerank via Voyage
        SemanticReranking --> AccumulateEvidence: Deduplicate & merge with prior rounds
        AccumulateEvidence --> [*]
    }

    ExecuteRetrieval --> SufficiencyEvaluation: Pass accumulated evidence + original question
    
    state SufficiencyEvaluation {
        [*] --> CheckSufficiency: Evaluate against rubric rules
        CheckSufficiency --> EvaluateAuthority: Resolve Codex vs Wiki conflicts
        EvaluateAuthority --> FormulateJudgment: Emit structured JSON judgment
        FormulateJudgment --> [*]
    }

    SufficiencyEvaluation --> SynthesizeAnswer: Status = 'sufficient'
    SufficiencyEvaluation --> CheckBudget: Status = 'insufficient'
    
    state CheckBudget {
        [*] --> BudgetDecision
        BudgetDecision --> Rewriter: Current Round < max_rounds AND New query != empty
        BudgetDecision --> SynthesizeAnswer: Current Round >= max_rounds OR Query unchanged
    }

    Rewriter --> ExecuteRetrieval: Execute reformulated query
    
    state SynthesizeAnswer {
        [*] --> GroundedGeneration: Synthesize final answer from accumulated passages
        GroundedGeneration --> AttachCitations: Extract metadata (doc_name, page, category)
        AttachCitations --> [*]
    }

    SynthesizeAnswer --> [*]: Return answer, steps, and source citations
```

---

## 4. Component Interaction Sequence Diagram

The following sequence diagram illustrates the lifecycle of a multi-hop query across system components:

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Streamlit UI (app.py)
    participant Agent as SearchAgent (search_agent.py)
    participant Planner as Planner (planner.py)
    participant Retrieval as Retrieval Pipeline (search.py)
    participant Checker as EvidenceChecker (evidence_checker.py)
    participant Rewriter as QueryRewriter (query_rewriter.py)
    participant Generator as AnswerGenerator (answer_generator.py)
    participant LLM as Groq LLM (openai/gpt-oss-120b)

    User->>UI: Enter Question (e.g. "What war was won by Isolde Mournvale's org?")
    UI->>Agent: answer_question(question, max_rounds=3, top_k=5)
    
    %% Round 1
    Agent->>Planner: plan_search(question)
    Planner->>LLM: Formulate initial query
    LLM-->>Planner: "Isolde Mournvale"
    Planner-->>Agent: query_round_1
    
    Agent->>Retrieval: search("Isolde Mournvale", top_k=5)
    Retrieval-->>Agent: Passages (The Silent Choir membership confirmed)
    
    Agent->>Checker: check_evidence(question, accumulated_evidence)
    Checker->>LLM: JSON Sufficiency Prompt
    LLM-->>Checker: {"status": "insufficient", "missing_info": "War won by The Silent Choir"}
    Checker-->>Agent: insufficient (Step 1 recorded)
    
    %% Round 2
    Agent->>Rewriter: rewrite_query(question, history, missing_info)
    Rewriter->>LLM: Reformulate query
    LLM-->>Rewriter: "The Silent Choir war won"
    Rewriter-->>Agent: query_round_2
    
    Agent->>Retrieval: search("The Silent Choir war won", top_k=5)
    Retrieval-->>Agent: Passages (Annals p. 28: War of Drowned Light victory)
    
    Agent->>Checker: check_evidence(question, accumulated_evidence)
    Checker->>LLM: JSON Sufficiency Prompt
    LLM-->>Checker: {"status": "sufficient", "reasoning": "Both entity and war identified"}
    Checker-->>Agent: sufficient (Step 2 recorded)
    
    %% Synthesis
    Agent->>Generator: generate_answer(question, accumulated_evidence)
    Generator->>LLM: Grounded answer prompt with source citation rules
    LLM-->>Generator: "The Silent Choir won the War of Drowned Light..."
    Generator-->>Agent: Final answer with formatted source citations
    
    Agent-->>UI: Return response dictionary (answer, search_steps, sources)
    UI-->>User: Render answer box, timeline cards, and expandable source badges
```

---

## 5. Source Authority Hierarchy & Conflict Resolution

The Ashen Era Archive deliberately includes epistemic uncertainty and conflicting accounts. The system enforces an explicit authority hierarchy:

```mermaid
flowchart TD
    Tier1["Tier 1: Canonical Reference Works<br/>(Codex Vaeloria, High Imperial Gazetteers)<br/>Weight: Primary / Absolute Truth"]
    Tier2["Tier 2: Historical Chronicles & Annals<br/>(Annals of the Ashen Era, Archival Ledgers)<br/>Weight: Authoritative Historical Record"]
    Tier3["Tier 3: Summary Overviews & Compendia<br/>(Regional Wikis, Encyclopedic Entries)<br/>Weight: Secondary / Often Hedge or Point to Codex"]
    Tier4["Tier 4: Ephemera & Folklore<br/>(Tavern Ballads, Rumors, Fragmentary Letters)<br/>Weight: Contextual Only / Superseded by Tiers 1-3"]

    Tier1 -->|Overrides| Tier2
    Tier2 -->|Overrides| Tier3
    Tier3 -->|Overrides| Tier4
    
    subgraph ResolutionExample["Cross-Document Pointer Resolution Example"]
        WikiNote["Wiki: 'Founding date is contested between 240 AS and 250 AS; consult Codex Vaeloria.'"]
        CodexText["Codex Vaeloria I (p. 23): 'Gloamreach was formally consecrated in 246 AS.'"]
        WikiNote -.->|Pointer Followed| CodexText
        CodexText ==> FinalFact["Authoritative Answer: 246 AS (Explicitly resolving wiki hedge)"]
    end
```

---

## 6. Component Directory Structure

| Module | File | Core Functionality |
|---|---|---|
| **Agent Controller** | `src/agent/search_agent.py` | Orchestrates multi-round loop, stops when sufficient or budget met, handles dedup guards |
| **Initial Planner** | `src/agent/planner.py` | Distills user question into focused first-turn query targeting primary entity |
| **Sufficiency Checker** | `src/agent/evidence_checker.py` | Returns structured JSON `status`, `reasoning`, and `missing_information` |
| **Query Rewriter** | `src/agent/query_rewriter.py` | Formulates targeted search queries bridging specific gaps across rounds |
| **Answer Generator** | `src/generation/answer_generator.py` | Synthesizes grounded markdown answer citing document names and page numbers |
| **LLM Client** | `src/llm/client.py` | Robust Groq client with exponential backoff retry and markdown-safe JSON parsing |
| **Document Ingestion**| `src/retrieval/ingest.py` | Parsers for PDF, DOCX, TXT, and Markdown files in the Ashen Era Archive |
| **Embedding Engine** | `src/retrieval/embedder.py` | Batch embedding generation using Voyage AI API |
| **Vector Store** | `src/retrieval/vector_store.py` | Persistent ChromaDB collection management with idempotent chunk upsert |
| **Cross-Reranker** | `src/retrieval/reranker.py` | Voyage reranking with defensive fallback to vector similarity scores |
| **Search Pipeline** | `src/retrieval/search.py` | Unified retrieval entry point: embed -> query -> rerank |
| **Web Interface** | `src/app.py` | Modern Streamlit UI with multi-round timeline, dark-mode CSS, and dual backends |
| **Evaluation Suite** | `src/evaluation/evaluate.py` | Automated 8-question benchmark runner evaluating accuracy, reasoning, and citations |

