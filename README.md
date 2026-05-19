# GradeOps
### AI-Powered Automated Exam Grading Platform

GradeOps is an AI-powered platform that automates the grading of scanned examination answer sheets. It extracts text from uploaded PDFs, routes answers question-wise, evaluates responses using instructor-defined rubrics, and generates marks with feedback.

The project is being built as a well-structured MVP with a production-oriented architecture. The current implementation focuses on core grading functionality while keeping the system modular and extensible for future enhancements.

---

# 🎯 Project Goal

The objective of GradeOps is to reduce the time and effort required for manual grading of descriptive answer sheets by combining:

- OCR for scanned PDFs
- Semantic similarity models
- Workflow orchestration
- Intelligent caching
- Parallel processing
- Explainable rubric-based grading

---

# 🏗️ System Architecture

```text
Streamlit Frontend
        ↓
FastAPI Backend
        ↓
PostgreSQL Database
        ↓
OCR Pipeline
(Groq → OpenRouter → EasyOCR)
        ↓
Question Analysis Cache
        ↓
Embedding Precomputation
        ↓
LangGraph Workflow
   ├── Routing Node
   └── Grading Node
        ↓
Marks + Feedback
```

---

# 🖥️ Frontend (Streamlit)

A lightweight instructor dashboard is being developed using Streamlit.

### Planned Features

- Login and authentication
- Course and exam management
- Question setup
- PDF answer sheet upload
- OCR monitoring
- Automated grading
- Results visualization
- Analytics dashboard

### Frontend Structure

```text
frontend/
├── app.py
├── pages/
├── components/
└── utils/
```

---

# ⚙️ Backend (FastAPI)

The backend handles the complete grading pipeline and exposes APIs for OCR and grading.

### Core Responsibilities

- Authentication and role-based access
- Course, exam, and question management
- PDF upload and storage
- OCR execution
- Answer routing
- Automated grading
- Result storage and retrieval

---

# 🧠 Key Design Decisions

## Modular Service Architecture

Each responsibility is implemented as an independent service (OCR, routing, grading, caching), making the system easier to understand, test, and extend.

## LangGraph Workflow Orchestration

The grading process is modeled as a graph of nodes rather than a single monolithic function, enabling clean separation of responsibilities.

## Multi-Provider OCR

OCR providers are chained to maximize reliability and free-tier utilization:

```text
Groq Vision → OpenRouter Vision → EasyOCR
```

## Persistent Question Analysis Cache

Question patterns are analyzed once and stored in PostgreSQL so future exams can reuse the same logic without repeated LLM calls.

## Per-Exam Embedding Precomputation

Rubric and expected-answer embeddings are generated once and reused across all answer sheets in the exam.

## Parallel Processing

Multiple answer sheets are graded concurrently using thread pools to significantly reduce processing time.

## Rule-Based + LLM Hybrid Classification

Common question types are recognized using deterministic rules, while Gemini is used only for rare, previously unseen patterns.

---

# ⚡ Performance Optimizations

| Optimization | Benefit |
|------------|----------|
| Persistent PostgreSQL cache | Avoid repeated LLM analysis |
| In-memory cache | Reduce database queries |
| Embedding precomputation | Eliminate redundant computations |
| Parallel processing | Faster grading of large batches |
| Rule-based classification | Lower API usage |
| Multi-provider OCR | Improved reliability |
| EasyOCR fallback | Unlimited offline OCR |

---

# 🛠 Technology Stack

## Backend
- FastAPI
- Python
- PostgreSQL
- SQLAlchemy
- LangGraph

## AI / NLP
- Sentence Transformers (`all-MiniLM-L6-v2`)
- Google Gemini (fallback analysis)

## OCR
- Groq Vision
- OpenRouter Vision
- EasyOCR

## Frontend
- Streamlit
- Plotly
- Pandas

---

# 📁 Project Structure

```text
GradeOps/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── workflows/
│   │   ├── models/
│   │   ├── database.py
│   │   └── main.py
│   ├── uploads/
│   └── requirements.txt
│
├── frontend/
│   ├── app.py
│   ├── pages/
│   ├── components/
│   └── utils/
│
└── README.md
```

---

# 🔌 Main API Endpoints

## OCR
- `POST /answer-sheets/{answer_sheet_id}/run-ocr`
- `GET /answer-sheets/{answer_sheet_id}/ocr`

## Grading
- `POST /grading/grade-exam/{exam_id}`

---

# 📊 Example Output

```json
{
  "marks_awarded": 5,
  "max_marks": 5,
  "overall_similarity": 0.86,
  "confidence_score": 0.93,
  "feedback": "Excellent answer. All rubric criteria were satisfied."
}
```

---

# 🚀 Future Improvements

The following enhancements are planned as the project evolves:

- Cross-student plagiarism detection
- Confidence-based manual review queue
- Teaching Assistant approval workflow
- Advanced analytics dashboard
- Export to Excel and PDF reports
- Docker-based deployment
- Cloud deployment
- LMS integrations (Moodle, Canvas, Google Classroom)

---

# 🏆 Why This Project Is Strong

GradeOps demonstrates practical software engineering and AI system design concepts including:

- Workflow orchestration
- Multi-provider fault tolerance
- Persistent caching
- Embedding optimization
- Parallel processing
- Explainable AI grading
- Modular full-stack architecture

The project emphasizes understanding and implementing efficient system design rather than simply calling external APIs.

---

# ▶️ Running the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger Documentation:

http://127.0.0.1:8000/docs

---

# ▶️ Running the Frontend

```bash
cd frontend
pip install streamlit plotly pandas requests
streamlit run app.py
```

---

# 💡 Development Philosophy

> Build a simple implementation today, but structure the code so that future enhancements can be added without major rewrites.

This approach keeps the current system understandable while preserving a strong architectural foundation for future growth.


