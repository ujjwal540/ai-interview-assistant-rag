# 🎯 AI Interview Assistant (RAG)

A Retrieval-Augmented-Generation app that turns a **resume + job description** into:

1. **Tailored interview questions** (behavioral + technical + gap-probing)
2. **A live mock interview chat** (Claude asks, you answer, it reacts)
3. **Answer feedback** — checks your practice answers against your real resume context

## How the pipeline works

```
Resume/JD  →  chunk (LangChain splitter)  →  embed (local, free)  →  FAISS vector store
                                                                          │
User question / interview turn  ───────────────────────────────►  retrieve top-k chunks
                                                                          │
                                                          Claude (Anthropic API) generates
                                                          questions / feedback / next turn
```

- **Embeddings** run locally via `sentence-transformers` — no API key, no cost.
- **Generation** (questions, feedback, mock-interview turns) calls the **Anthropic API** — this is the only key you need.
- You can optionally swap either half to OpenAI (see `.env.example`).

## 1. Project setup

### Create and activate a virtual environment

```bash
# from the project root
python3 -m venv venv

# activate it
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure your API key

```bash
cp .env.example .env
```

Then open `.env` and set:

```
ANTHROPIC_API_KEY=sk-ant-...your-real-key...
```

Get a key at https://console.anthropic.com/ → **Settings → API Keys**.
Everything else in `.env` has a sensible default and can be left as-is.

## 2. Run it

### Option A — Streamlit app (recommended)

```bash
streamlit run app.py
```

Then in the browser: upload a resume, paste a job description, click **Build Index**, and use the three tabs.

### Option B — CLI index build (for scripting/batch use)

```bash
python scripts/build_index.py --resume data/resumes/john.pdf --jd data/job_descriptions/role.txt
```

This persists the FAISS index to `vectorstore/`, which the Streamlit app can then "Load existing index" on startup.

## 3. Project structure

```
ai-interview-assistant-rag/
├── .env.example              # template for API keys & pipeline config
├── .gitignore
├── requirements.txt
├── README.md
├── app.py                    # Streamlit UI (main entry point)
├── src/
│   ├── __init__.py
│   ├── config.py             # loads & validates env vars
│   ├── prompts.py            # all prompt templates
│   ├── ingest.py             # load PDFs/DOCX/TXT, chunk text
│   ├── vectorstore.py        # build/save/load FAISS index + embeddings
│   ├── rag_pipeline.py       # LLM getter + retrieval helper
│   ├── question_generator.py # tailored question generation
│   ├── answer_evaluator.py   # feedback on a practice answer
│   └── mock_interview.py     # stateful mock-interview chat session
├── scripts/
│   └── build_index.py        # CLI to build the vector index
├── data/
│   ├── resumes/               # put resume files here (gitignored)
│   └── job_descriptions/      # put JD files here (gitignored)
└── vectorstore/               # persisted FAISS index (gitignored)
```

## 4. Environment variables reference

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ yes | — | Claude API key for question generation, mock interview, feedback |
| `CLAUDE_MODEL` | no | `claude-sonnet-5` | Model used for generation |
| `EMBEDDING_MODEL` | no | `sentence-transformers/all-MiniLM-L6-v2` | Local embedding model |
| `EMBEDDING_PROVIDER` | no | `local` | `local` (free) or `openai` |
| `LLM_PROVIDER` | no | `anthropic` | `anthropic` or `openai` |
| `OPENAI_API_KEY` | only if using OpenAI | — | Needed only if you switch either provider to `openai` |
| `VECTORSTORE_DIR` | no | `vectorstore` | Where the FAISS index is persisted |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | no | `1000` / `200` | Text splitter settings |
| `RETRIEVER_TOP_K` | no | `4` | How many chunks to retrieve per query |

## 5. Notes & next steps

- Swap `FAISS` for `Chroma`/`Pinecone`/`Weaviate` in `src/vectorstore.py` if you need a hosted or persistent multi-user store.
- Add authentication before deploying the Streamlit app publicly — right now anyone with the URL can use your API key's quota.
- Deactivate the venv when done: `deactivate`.
