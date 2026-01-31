
# 🔐 Founder’s Vault  
### Privacy‑First AI Chief of Staff for Founders & Executives

**Founder’s Vault** is a high‑security, fully local AI intelligence system designed for founders, CEOs, and executives who work with sensitive business data.  
It enables deep analysis of **legal documents, investment terms, financial reports, and strategic files** — **without sending data to the cloud or third‑party APIs**.

> 🛡️ Your data never leaves your machine. No tracking. No training. No leakage.

---

## 🚨 The Problem: The Privacy Paradox

Modern leaders rely on AI tools — but most come with dangerous trade‑offs:

- ❌ **Data Leakage** – Proprietary documents uploaded to cloud LLMs may be logged, leaked, or subpoenaed  
- ❌ **Model Training Risk** – Your confidential data may be reused to train future AI models  
- ❌ **API Dependency** – Expensive APIs, downtime risks, and zero control over data residency  

Using cloud AI for confidential work is a **silent risk**.

---

## 💡 The Solution: Founder’s Vault

Founder’s Vault introduces a **Zero‑API, Local‑Only AI Intelligence System** — a digital *Chief of Staff* that runs entirely on your own hardware.

### 🔒 Core Principles
- **100% Local Inference**
- **No external API calls**
- **Ephemeral document ingestion**
- **Grounded & deterministic answers**
- **Enterprise‑grade privacy**

---

## 🧠 What Founder’s Vault Can Do

- 📄 Analyze **contracts, legal PDFs, pitch decks**
- 📊 Perform **financial analysis on CSVs**
- 🔍 Semantic search across confidential files
- 📌 Answer questions *only from your documents*
- 🧮 Run deterministic Pandas‑based calculations
- 💬 Real‑time chat interface with streaming responses

---

## 🏗️ System Architecture

### Privacy‑First Stack

| Component | Purpose |
|--------|--------|
| **Ollama** | Local LLM inference engine |
| **Llama 3.x** | Primary reasoning model |
| **ChromaDB** | Local vector database |
| **FastEmbed** | CPU‑optimized embeddings |
| **PyMuPDF** | Fast PDF parsing |
| **LangChain** | RAG orchestration |
| **Flask + WebSockets** | Real‑time UI |

---

## 🔄 Processing Pipeline

1. **Ingestion** – Secure PDFs & CSVs parsed locally  
2. **Chunking** – Recursive splitter with overlap  
3. **Vectorization** – Stored in local ChromaDB  
4. **Retrieval** – Top‑K semantic matches only  
5. **Grounded Generation** – Model restricted to retrieved context  
6. **Streaming Output** – Transparent reasoning & responses  

> 🚫 Hallucinations are prevented by strict context grounding.

---

## 📁 Folder Structure

```
FOUNDERS_VAULT/
├── app/
│   ├── main/
│   │   ├── routes.py
│   │   └── events.py
│   ├── modules/
│   │   ├── llm_engine.py
│   │   ├── rag_engine.py
│   │   ├── analysis_engine.py
│   │   └── session_store.py
│   ├── static/
│   ├── templates/
│   └── __init__.py
├── uploads/
├── chroma_db/
├── requirements.txt
├── run.py
└── .env
```

---

## 🚀 Installation & Usage

### ✅ Prerequisites
- Python **3.10+**
- Ollama Desktop installed & running
- Model downloaded:
```
ollama pull llama3.2
```

---

### 📦 Setup

```bash
git clone https://github.com/rmn2178/FOUNDERS_VAULT.git
cd FOUNDERS_VAULT

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

---

### 🔐 Environment Configuration

Create a `.env` file:
```
FLASK_SECRET_KEY=your_secure_random_key
UPLOAD_FOLDER=./uploads
```

---

### ▶️ Run the Vault

```bash
python run.py
```

Open: **http://127.0.0.1:5000**

---

## ⚠️ Common Issues & Fixes

| Error | Cause | Fix |
|----|----|----|
| ModuleNotFoundError | LangChain mismatch | Update langchain packages |
| Connection Refused | Ollama not running | Run `ollama serve` |
| WinError 32 | ChromaDB file lock | Stop app & delete chroma_db |
| Jinja Undefined | Variable mismatch | Align route & template names |

---

## 🔮 Future Enhancements

- 🔑 User authentication
- 📜 Audit‑level source citations
- 🔐 Encrypted local vault
- 📊 Advanced financial dashboards
- 🤖 Multi‑agent reasoning
- 🧠 Model switching (Mixtral, Phi, Qwen)

---

## 🧑‍💼 Ideal For

- Startup founders  
- CEOs & CFOs  
- Legal & finance professionals  
- Privacy‑focused teams  
- AI researchers  
- On‑prem enterprise deployments  

---

## 🏁 Final Note

Founder’s Vault is **not another AI chatbot**.

It is a **private intelligence system** — built for people who **cannot afford data leaks**.

> 🔐 *If your data matters, your AI must be local.*
