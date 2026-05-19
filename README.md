# GradeOps Backend
### AI-Powered Automated Exam Grading Platform

GradeOps is a production-oriented backend system that automates the end-to-end workflow of grading scanned examination answer sheets. The platform combines OCR, workflow orchestration, semantic similarity models, caching, and parallel processing to deliver accurate, scalable, and cost-efficient automated grading.

The project was designed not as a simple academic prototype, but as a robust AI system that applies real-world software engineering principles such as modular architecture, fault tolerance, persistent caching, optimization, and explainable decision-making.

---

# 🚀 Vision

Manual grading of descriptive answer sheets is one of the most time-consuming tasks for educators. GradeOps aims to solve this problem by:

- Extracting text from scanned answer sheets
- Automatically routing responses question-wise
- Grading answers using rubrics and semantic similarity
- Generating marks and feedback
- Reducing instructor workload
- Providing a scalable SaaS foundation for educational institutions

---

# High-Level Architecture

```text
PDF Upload
   ↓
Multi-Provider OCR
(Groq → OpenRouter → EasyOCR)
   ↓
OCR Results Stored in PostgreSQL
   ↓
Question Analysis Cache
   ↓
Per-Exam Embedding Precomputation
   ↓
Enriched Question Metadata
   ↓
Parallel Answer Sheet Processing
   ↓
LangGraph Workflow
   ├── Routing Node
   └── Grading Node
   ↓
Marks + Feedback
```

---

# Core Engineering Highlights

This project demonstrates several advanced engineering concepts rarely found in student projects:

- Multi-provider OCR with automatic failover
- LangGraph-based workflow orchestration
- Persistent PostgreSQL caching
- Per-exam embedding precomputation
- Parallel grading using thread pools
- Rule-based + LLM hybrid reasoning
- Semantic rubric-based grading
- Explainable criterion-level scoring
- Modular service-oriented architecture

---

# 🛠 Technology Stack

## Backend
- FastAPI
- Python 3.13

## Database
- PostgreSQL
- SQLAlchemy

## Workflow Orchestration
- LangGraph

## AI / NLP
- Sentence Transformers (`all-MiniLM-L6-v2`)
- Google Gemini (used only for rare unknown question patterns)

## OCR Providers
- Groq Vision Models
- OpenRouter Vision Models
- EasyOCR (offline unlimited fallback)

## Concurrency
- ThreadPoolExecutor

---

# Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── grading.py
│   │
│   ├── services/
│   │   ├── grading_service.py
│   │   ├── question_analysis_service.py
│   │   ├── routing_service.py
│   │   ├── multi_ocr_service.py
│   │   ├── groq_ocr_service.py
│   │   ├── openrouter_ocr_service.py
│   │   ├── easyocr_service.py
│   │   └── gemini_client.py
│   │
│   ├── workflows/
│   │   └── grading_workflow.py
│   │
│   ├── models/
│   ├── database.py
│   └── main.py
│
├── uploads/
├── requirements.txt
└── README.md
```

---

# Key Design Decisions and Rationale

## 1. LangGraph Workflow Architecture

Rather than embedding all logic inside one large API endpoint, grading is modeled as a workflow of independent nodes.

### Current Nodes
- Routing Node
- Grading Node

### Benefits
- Clear separation of concerns
- Easier debugging
- Extensible architecture
- Production-grade orchestration

---

## 2. Multi-Provider OCR with Automatic Failover

OCR providers are chained in order:

```text
Groq Vision → OpenRouter Vision → EasyOCR
```

If one provider fails due to quota exhaustion or API errors, the next provider is used automatically.

### Benefits
- High reliability
- Maximum free-tier utilization
- Minimal downtime
- Unlimited local fallback

---

## 3. Persistent Question Analysis Cache

Each unique combination of:
- Question text
- Expected answer
- Rubric

is hashed using SHA-256 and stored in PostgreSQL.

### Cached Attributes
- Question type
- Plagiarism strategy
- Similarity thresholds
- Review priority

### Benefits
- Avoids repeated LLM calls
- Builds institutional knowledge
- Reuses patterns across future exams

---

## 4. Per-Exam Embedding Precomputation

Before grading starts, embeddings are generated once for:
- Rubric criteria
- Expected answers

These embeddings are reused for every answer sheet in the exam.

### Benefits
- Massive reduction in repeated computation
- Significant performance gains
- Lower runtime cost

---

## 5. Parallel Answer Sheet Processing

Multiple answer sheets are graded concurrently using `ThreadPoolExecutor`.

### Benefits
- Better hardware utilization
- Faster grading for large classes
- Reduced end-to-end latency

---

## 6. Hybrid Rule-Based + LLM Classification

Most question types are recognized deterministically:
- MCQ
- Numerical
- True/False
- Match the Following
- Code Questions
- Essays
- Conceptual Questions

Gemini is invoked only when the system encounters a completely new pattern.

### Benefits
- Minimal API usage
- Deterministic outputs
- Cost-efficient learning system

---

## 7. Semantic Rubric-Based Grading

Grading combines:
- Criterion-level semantic similarity
- Expected-answer similarity
- Partial marking logic
- Confidence scoring

### Benefits
- Transparent and explainable grading
- Supports realistic instructor rubrics
- Provides detailed feedback

---

## 8. Backward-Compatible Interfaces

Service methods were intentionally designed to accept both legacy and optimized parameters.

### Benefits
- Safe incremental refactoring
- Easier debugging
- Reduced integration risk

---

# Performance Optimizations

| Optimization | Purpose |
|------------|---------|
| Persistent PostgreSQL cache | Avoid repeated LLM analysis |
| In-memory runtime cache | Reduce DB queries |
| Embedding precomputation | Eliminate redundant embeddings |
| Parallel processing | Grade multiple scripts simultaneously |
| Rule-based classification | Minimize API usage |
| Multi-provider OCR | Prevent token exhaustion downtime |
| EasyOCR fallback | Unlimited offline OCR |

---

# Database Tables

## `questions`
Stores:
- `question_number`
- `expected_answer`
- `rubric`
- `max_marks`

## `answer_sheets`
Stores uploaded PDF files and metadata.

## `ocr_results`
Stores extracted text and OCR provider information.

## `question_analysis_cache`
Stores persistent question classification results.

---

# API Endpoints

## OCR

### Run OCR
`POST /answer-sheets/{answer_sheet_id}/run-ocr`

### Retrieve OCR Result
`GET /answer-sheets/{answer_sheet_id}/ocr`

## Grading

### Grade Entire Exam
`POST /grading/grade-exam/{exam_id}`

---

# 📊 Example Grading Output

```json
{
  "marks_awarded": 5,
  "max_marks": 5,
  "overall_similarity": 0.86,
  "confidence_score": 0.93,
  "feedback": "Excellent answer. All rubric criteria were satisfied.",
  "question_type": "conceptual"
}
```

---

# Why This Project Stands Out

Most student projects focus on:
- CRUD operations
- Basic OCR
- Simple API endpoints

GradeOps demonstrates advanced engineering concepts including:
- AI workflow orchestration
- Multi-provider fault tolerance
- Persistent knowledge caching
- Embedding optimization
- Explainable grading
- Concurrent processing
- Cost-aware AI integration

This reflects architectural thinking closer to production SaaS systems than to typical academic projects.

---

# 🛣 Future Roadmap

## Academic Integrity
- Cross-student plagiarism detection
- Cluster-based similarity analysis

## Human-in-the-Loop Review
- Confidence-based moderation queues
- TA approval workflows

## Analytics
- Grade distributions
- Question difficulty analysis
- Learning outcome tracking

## Integrations
- Moodle
- Canvas
- Google Classroom

## Deployment
- Docker containerization
- Kubernetes orchestration
- Cloud deployment (AWS/GCP/Azure)

## Frontend
- Streamlit instructor dashboard
- Role-based interfaces for instructors and TAs

---

# Running the Backend

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

# API Documentation

Swagger UI:

http://127.0.0.1:8000/docs

---

# Development Philosophy

GradeOps was built with a guiding principle:

> Use AI only where it provides real value, and aggressively eliminate unnecessary API calls through deterministic logic, caching, local computation, and system-level optimization.

This results in a system that is:

- Accurate
- Scalable
- Explainable
- Cost-efficient
- Fault tolerant

---

# Engineering Focus

This project emphasizes not only machine learning, but also core software engineering principles:

- System design
- Optimization
- Modular architecture
- Reliability
- Maintainability
- Production readiness

The objective was to understand and implement the engineering decisions that make AI systems efficient and robust, rather than simply integrating APIs.

---
