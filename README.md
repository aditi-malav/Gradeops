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
## 🧠 Key Design Decisions and Optimizations

The architecture of GradeOps was designed to minimize API usage, reduce redundant computation, and make the system capable of processing large batches of answer sheets efficiently.

---

### Modular Services + LangGraph Workflow

The system is divided into independent services such as OCR, routing, question analysis, grading, and caching. These services are connected through a LangGraph workflow.

```text
OCR → Routing → Grading → Store Results
```

This approach keeps each component focused on a single responsibility and makes the system easier to debug, extend, and maintain.

---

### Multi-Provider OCR with Automatic Failover

OCR providers are chained in sequence:

```text
Groq Vision → OpenRouter Vision → EasyOCR
```

If one provider fails or exhausts its free quota, the next provider is used automatically. EasyOCR serves as an unlimited offline fallback.

This ensures that OCR remains available even when external API limits are reached.

---

### Persistent Question Analysis Cache

Each question is analyzed to determine:

- Question type
- Grading strategy
- Plagiarism strategy
- Similarity thresholds
- Review priority

The result is stored permanently in PostgreSQL using a hash of the question text, expected answer, and rubric.

```text
Question
   ↓
Check Cache
   ↓
Found? → Reuse Stored Result
   ↓
Not Found → Analyze Once
   ↓
Store Permanently
```

This means that even if a completely new question type requires Gemini, it is analyzed only once and the result is reused for all remaining answer sheets and future exams with the same pattern.

This significantly reduces API calls and allows the system to build a growing knowledge base over time.

---

### Rule-Based + LLM Hybrid Classification

Most common question types (MCQ, numerical, true/false, essays, conceptual, code questions) are identified using deterministic rules.

Gemini is used only when the system encounters a pattern that cannot be recognized by existing rules.

This minimizes token usage while preserving flexibility for unusual question formats.

---

### Deterministic Answer Routing

OCR text is split into question-wise answers using regular expressions instead of an LLM.

This makes routing extremely fast, predictable, and completely free of API costs.

---

### Local Semantic Grading

Student answers are graded locally using Sentence Transformers (`all-MiniLM-L6-v2`) and cosine similarity against rubric criteria and expected answers.

This eliminates per-answer API calls and supports criterion-level partial marking with explainable feedback.

---

### Per-Exam Embedding Precomputation

For each question, the system computes once:

- Parsed rubric criteria
- Criterion embeddings
- Expected answer embedding

These are stored in memory and reused for all answer sheets in the exam.

This avoids repeatedly generating the same embeddings and substantially improves grading speed.

---

### Parallel Processing

Answer sheets are processed concurrently using `ThreadPoolExecutor`.

This allows multiple scripts to be graded simultaneously and significantly reduces total processing time for large classes.

---

## ⚡ Optimization Summary

| Optimization | Benefit |
|------------|---------|
| Persistent question cache | New question types analyzed only once |
| In-memory cache | Reduces database lookups |
| Deterministic routing | Eliminates routing API calls |
| Local semantic grading | Eliminates per-answer grading API calls |
| Embedding precomputation | Avoids redundant embedding generation |
| Parallel processing | Faster grading of large batches |
| Multi-provider OCR | Prevents downtime due to API limits |
| EasyOCR fallback | Unlimited offline OCR |

---

## 📈 Scalability Impact

For an exam with 200 answer sheets and 5 questions:

- Question analysis runs only **5 times** instead of **1,000 times**
- Rubric embeddings are computed once per question
- Grading is performed locally without repeated API calls
- Answer sheets are processed in parallel

These design decisions make the system fast, cost-efficient, and capable of handling large exam batches while maintaining grading quality.

---

## 📈 Scalability Impact

These design decisions allow GradeOps to process large exam batches efficiently.

For example, with 200 answer sheets and 5 questions each:

- Question analysis: 5 total analyses (instead of 1,000)
- Rubric embeddings: computed once per question
- Grading: performed locally using embeddings
- OCR: resilient to API quota exhaustion
- Processing: executed in parallel across multiple CPU cores

As a result, the platform remains fast, cost-efficient, and robust while maintaining grading quality.

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


