# GradeOps
### AI-Powered Automated Exam Grading Platform

GradeOps is an AI-powered platform that automates the grading of scanned examination answer sheets. It extracts text from uploaded PDFs, routes answers question-wise, evaluates responses using instructor-defined rubrics, and generates marks with detailed feedback.

The project is being developed as a full-stack MVP with a strong focus on system design, optimization, and modular architecture. The goal is not only to build an automated grading system, but also to understand and implement the engineering decisions that make AI systems efficient, reliable, and scalable.

---

## Project Goal

The objective of GradeOps is to reduce the time and effort required for manual grading of descriptive answer sheets by combining:

- OCR for scanned PDFs
- Semantic similarity models
- Workflow orchestration
- Intelligent caching
- Parallel processing
- Explainable rubric-based grading
- Cross-student plagiarism detection

---

## System Architecture

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
   ├── Grading Node
   └── Verification Node
        ↓
Marks + Feedback + Plagiarism Flags
```

---

## Technology Stack

### Backend
- FastAPI
- Python
- PostgreSQL
- SQLAlchemy
- LangGraph

### AI / NLP
- Sentence Transformers (`all-MiniLM-L6-v2`)
- Google Gemini (used only for rare unknown question patterns)

### OCR
- Groq Vision
- OpenRouter Vision
- EasyOCR

### Frontend
- Streamlit
- Plotly
- Pandas

### Concurrency
- ThreadPoolExecutor

---

## Project Structure

```text
GradeOps/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── grading.py
│   │   │
│   │   ├── routers/
│   │   │   └── users.py
│   │   │
│   │   ├── services/
│   │   │   ├── ocr_service.py
│   │   │   ├── multi_ocr_service.py
│   │   │   ├── groq_ocr_service.py
│   │   │   ├── openrouter_ocr_service.py
│   │   │   ├── easyocr_service.py
│   │   │   ├── gemini_ocr_service.py
│   │   │   ├── gemini_client.py
│   │   │   ├── routing_service.py
│   │   │   ├── grading_service.py
│   │   │   ├── similarity_service.py
│   │   │   ├── plagiarism_service.py
│   │   │   ├── verification_service.py
│   │   │   └── question_analysis_service.py
│   │   │
│   │   ├── workflows/
│   │   │   └── grading_workflow.py
│   │   │
│   │   ├── auth.py
│   │   ├── jwt_handler.py
│   │   ├── database.py
│   │   └── main.py
│   │
│   ├── uploads/
│   ├── .env
│   └── requirements.txt
│
├── frontend/
│   ├── app.py
│   ├── pages/
│   │   ├── login.py
│   │   ├── register.py
│   │   ├── dashboard.py
│   │   ├── courses.py
│   │   ├── exams.py
│   │   ├── questions.py
│   │   ├── upload_pdf.py
│   │   ├── run_ocr.py
│   │   ├── grade_exam.py
│   │   └── results.py
│   │
│   ├── utils/
│   │   ├── api_client.py
│   │   └── session_state.py
│   │
│   └── requirements.txt
│
├── .gitignore
└── README.md
```

---

## Frontend Overview

The frontend is built using Streamlit to provide a clean and interactive dashboard for instructors.

### Current Features

- User registration and login
- Course management
- Exam creation
- Question setup
- PDF answer sheet upload
- OCR execution
- Automated grading
- Results visualization

---

## Backend Overview

The FastAPI backend handles the complete grading pipeline and exposes APIs for OCR and grading.

### Core Responsibilities

- Authentication and role-based access
- Course, exam, and question management
- PDF upload and storage
- OCR execution
- Answer routing
- Automated grading
- Plagiarism detection
- Result retrieval

---

## Key Design Decisions and Optimizations

The architecture was designed to minimize API usage, avoid redundant computation, and process large batches of answer sheets efficiently.

### Modular Services with LangGraph Workflow

Each responsibility (OCR, routing, grading, plagiarism detection, verification, and caching) is implemented as an independent service. These services are coordinated through a LangGraph workflow.

```text
OCR → Routing → Grading → Verification → Store Results
```

This keeps the code modular and makes it easy to add new steps later without rewriting the existing pipeline.

---

### Multi-Provider OCR with Automatic Failover

OCR providers are chained in sequence:

```text
Groq Vision → OpenRouter Vision → EasyOCR
```

If one provider fails or exhausts its free-tier quota, the next provider is used automatically. EasyOCR acts as an unlimited offline fallback.

This ensures OCR remains available even when external APIs are unavailable.

---

### Persistent Question Analysis Cache

Each question is analyzed to determine:

- Question type
- Grading strategy
- Plagiarism strategy
- Similarity thresholds
- Review priority

The result is stored permanently in PostgreSQL using a hash of the question text, expected answer, and rubric.

If a completely new question pattern requires Gemini, it is analyzed only once and then reused for all future answer sheets and exams with the same pattern.

This significantly reduces API calls and allows the system to build a reusable knowledge base over time.

---

### Rule-Based + LLM Hybrid Classification

Common question types such as MCQ, numerical, true/false, code, essay, and conceptual questions are classified using deterministic rules.

Gemini is used only when the system encounters a pattern that cannot be recognized by existing rules.

This combines flexibility with very low API cost.

---

### Deterministic Answer Routing

OCR text is split into question-wise answers using regular expressions instead of an LLM.

This makes routing fast, predictable, and completely free of API usage.

---

### Local Semantic Grading

Student answers are graded locally using Sentence Transformers and cosine similarity against rubric criteria and expected answers.

This eliminates per-answer API calls while supporting:

- Criterion-level scoring
- Partial marking
- Confidence scores
- Detailed feedback

---

### Per-Exam Embedding Precomputation

For each question, the system computes once:

- Parsed rubric criteria
- Criterion embeddings
- Expected answer embedding

These are reused for every answer sheet in the exam, avoiding redundant embedding generation.

---

### Cross-Student Plagiarism Detection

Student answers are compared pairwise using embeddings and question-specific plagiarism strategies.

Highly similar answers are flagged for instructor review, enabling automated academic integrity checks without external APIs.

---

### Parallel Processing

Answer sheets are processed concurrently using `ThreadPoolExecutor`.

This significantly reduces grading time for large classes.

---

## Optimization Summary

| Optimization | Benefit |
|------------|---------|
| Persistent question cache | New question types analyzed only once |
| In-memory cache | Reduces database lookups |
| Deterministic routing | Eliminates routing API calls |
| Local semantic grading | Eliminates per-answer grading API calls |
| Embedding precomputation | Avoids redundant embedding generation |
| Cross-student plagiarism detection | Detects suspicious similarity locally |
| Parallel processing | Faster grading of large batches |
| Multi-provider OCR | Prevents downtime due to API limits |
| EasyOCR fallback | Unlimited offline OCR |

---

## Scalability Example

For an exam with 200 answer sheets and 5 questions:

- Question analysis runs only 5 times instead of 1,000 times
- Rubric embeddings are computed once per question
- Grading is performed locally without repeated API calls
- Answer sheets are processed in parallel

These design decisions make the system fast, cost-efficient, and capable of handling large exam batches while maintaining grading quality.

---

## Main API Endpoints

### OCR
- `POST /answer-sheets/{answer_sheet_id}/run-ocr`
- `GET /answer-sheets/{answer_sheet_id}/ocr`

### Grading
- `POST /grading/grade-exam/{exam_id}`

---

## Example Output

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

## Future Improvements

- Confidence-based manual review queue
- Teaching Assistant approval workflow
- Advanced analytics dashboard
- Export to Excel and PDF reports
- Docker-based deployment
- Cloud deployment

---

## Why This Project Stands Out

GradeOps combines practical AI techniques with strong software engineering principles:

- Workflow orchestration
- Multi-provider fault tolerance
- Persistent caching
- Embedding optimization
- Parallel processing
- Explainable grading
- Cross-student plagiarism detection
- Modular full-stack architecture

The project emphasizes understanding system design and optimization rather than simply integrating external APIs.

---

## Running the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger Documentation:

http://127.0.0.1:8000/docs

---

## Running the Frontend

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

---

## Development Philosophy

> Build a simple implementation today, but structure the code so that future enhancements can be added without major rewrites.

This approach keeps the current system understandable while preserving a strong architectural foundation for future growth.




