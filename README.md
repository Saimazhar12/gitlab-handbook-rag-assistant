# 🤖 GitLab Handbook RAG Assistant

> 🚀 **This project is developed as part of my internship task at SafeX Solutions.**

GitLab Handbook RAG Assistant is an AI-powered FAQ chatbot that answers questions using **14 selected pages from the GitLab Team Handbook**. It uses RAG to retrieve relevant information and provides answers with source citations.

## 🌐 Live Demo

[**👉 Try the Live Demo**](https://app-handbook-rag-assistant-4wruu3ujrytnrtj23ukpcq.streamlit.app/)

## 🚀 Features

* **AI-Powered Answers** — Answers questions using information from the GitLab Handbook.
* **RAG Retrieval** — Finds relevant content before generating an answer.
* **Source Citations** — Shows the sources used for each answer.
* **Hallucination Protection** — Refuses questions outside the knowledge base.
* **Evaluation** — Includes 20 test questions for retrieval accuracy.
* **Modern UI** — Custom Streamlit AI/SaaS-style interface.

## 🛠️ Tech Stack

* **Python**
* **LangChain**
* **ChromaDB**
* **Gemini / OpenAI**
* **Streamlit**
* **RAG**

## 📁 Project Structure

```text
data/
  raw/                 Scraped handbook pages
  processed/           Cleaned documents
  eval_report.md       Evaluation results

assets/
  logo.png             Project logo
  generate_logo.py     Logo generator

src/
  sources.py           Handbook source URLs
  scrape.py             Scrape handbook pages
  clean.py              Clean documents
  config.py             Configuration
  ingest.py             Create embeddings & ChromaDB
  rag_chain.py          RAG chatbot logic

app.py                  Streamlit frontend
evaluate.py             Evaluation tests
chroma_db/              Vector database
requirements.txt        Dependencies
.env.example            Environment variables
```

## 🔁 How It Works

1. Scrapes 14 GitLab Handbook pages.
2. Cleans and prepares the content.
3. Splits documents into smaller chunks.
4. Creates embeddings and stores them in ChromaDB.
5. Retrieves relevant information for each question.
6. Sends the retrieved information to Gemini/OpenAI.
7. Generates an answer with source citations.

## ⚙️ Setup Guide

### 1. Install dependencies

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup API Key

Create a `.env` file:

```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_key_here
```

You can also configure OpenAI.

### 3. Build the Knowledge Base

```bash
python src/scrape.py
python src/clean.py
python src/ingest.py
```

### 4. Run evaluation

```bash
python evaluate.py
```

### 5. Run the project

```bash
streamlit run app.py
```

## 📊 Evaluation

The project includes **20 test questions** covering:

* Individual handbook pages
* Cross-page questions
* Out-of-scope questions

Results are saved in:

```text
data/eval_report.md
```


## 👨‍💻 Author

**Saim Azhar**
