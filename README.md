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
## 🧠 Key Design Decisions and Performance Optimizations

The core objective of GradeOps is to process large batches of answer sheets efficiently while minimizing API usage and preserving grading quality. Several architectural decisions were made specifically to ensure the system can scale to hundreds of answer sheets without major redesign.

---

### 1. Modular Service Architecture + LangGraph Workflow

The system is divided into independent services such as OCR, routing, question analysis, grading, and caching. Each service has a single responsibility and can be developed, tested, and replaced independently.

These services are coordinated using LangGraph, where the grading pipeline is modeled as a sequence of nodes rather than a single large function.

```text
OCR → Routing → Grading → Verification → Store Results
```

**Why this decision was taken:**

- Keeps the codebase organized and easier to understand.
- Prevents business logic from becoming tightly coupled.
- Makes debugging simpler because each stage is isolated.
- Allows new workflow nodes (e.g., plagiarism detection) to be added later without rewriting existing logic.

---

### 2. Multi-Provider OCR with Automatic Failover

OCR is one of the most token-intensive stages. To avoid service interruption due to quota exhaustion, multiple OCR providers are chained together.

```text
Groq Vision → OpenRouter Vision → EasyOCR
```

If one provider fails or its free-tier quota is exhausted, the next provider is used automatically. EasyOCR serves as an unlimited offline fallback.

**Why this decision was taken:**

- Prevents grading from stopping when API limits are reached.
- Maximizes the use of free-tier credits.
- Reduces dependence on a single vendor.
- Guarantees that OCR remains available even when all external APIs fail.

---

### 3. Persistent Question Analysis Cache

Each question is analyzed only once to determine:

- Question type
- Grading strategy
- Plagiarism strategy
- Similarity thresholds
- Review priority

The result is stored permanently in PostgreSQL using a SHA-256 hash of the question text, expected answer, and rubric as the cache key.

```text
Question
   ↓
Check Database Cache
   ↓
Found? → Reuse
   ↓
Not Found → Rule-Based Analysis
   ↓
Unknown Pattern → Gemini Fallback
   ↓
Store Permanently
```

**Why this decision was taken:**

Without caching, the same question would be analyzed repeatedly for every answer sheet. For example:

- 200 answer sheets × 5 questions = 1,000 analyses

With caching:

- 5 analyses total

This drastically reduces API usage and processing time while allowing the system to learn reusable handling strategies across future exams.

---

### 4. Rule-Based + LLM Hybrid Classification

Most question types are recognized using deterministic rules, including:

- MCQ
- Multiple Select
- Numerical
- True/False
- Match the Following
- Code Questions
- Essays
- Conceptual Questions

Gemini is used only when the system encounters a completely new pattern that cannot be recognized by existing rules.

**Why this decision was taken:**

- Common cases are handled instantly with no API cost.
- LLM calls are reserved only for rare edge cases.
- New patterns are learned once and cached permanently.
- Balances flexibility with cost efficiency.

---

### 5. Deterministic Answer Routing

The routing service uses regular expressions and rule-based parsing to split OCR text into question-wise answers instead of relying on an LLM.

**Why this decision was taken:**

- Zero API calls.
- Extremely fast.
- Predictable and repeatable behavior.
- Scales efficiently to hundreds of answer sheets.

---

### 6. Local Semantic Grading

The grading engine uses Sentence Transformers (`all-MiniLM-L6-v2`) to generate embeddings and compare student answers against rubric criteria and expected answers.

The grading process is entirely local and does not require an API call for every answer.

```text
Student Answer
      ↓
Generate Embedding Once
      ↓
Compare with Rubric Criteria
      ↓
Award Criterion Marks
      ↓
Compute Confidence
      ↓
Optional Escalation if Needed
```

**Why this decision was taken:**

- Eliminates per-answer API costs.
- Provides strong semantic understanding.
- Supports partial marking.
- Works well for conceptual, essay, and situational questions.
- Enables processing of hundreds of scripts on a standard laptop.

---

### 7. Per-Exam Embedding Precomputation

Before grading begins, the system computes once per question:

- Parsed rubric criteria
- Criterion embeddings
- Expected answer embedding

These are stored in memory and reused for every answer sheet in the exam.

**Why this decision was taken:**

Without caching:

- 200 answer sheets × 4 rubric criteria = 800 criterion embeddings

With precomputation:

- 4 criterion embeddings total

This significantly reduces redundant computation and improves throughput.

---

### 8. Parallel Processing of Answer Sheets

Answer sheets are graded concurrently using `ThreadPoolExecutor`.

```text
200 Answer Sheets
        ↓
ThreadPoolExecutor
        ↓
Multiple Sheets Processed Simultaneously
```

**Why this decision was taken:**

- Makes effective use of available CPU cores.
- Reduces total grading time substantially.
- Allows the platform to handle large batches efficiently.

---

### 9. Confidence-Based LLM Escalation (Planned)

Most grading is performed locally. In future versions, only low-confidence answers will be escalated to an LLM or flagged for manual review.

**Why this decision was taken:**

- Preserves grading quality for ambiguous responses.
- Keeps API usage extremely low.
- Enables human-in-the-loop review for uncertain cases.

---

### 10. Local Plagiarism Detection (Planned)

Plagiarism detection will use embeddings and similarity clustering rather than external APIs.

**Why this decision was taken:**

- No recurring API costs.
- Scales naturally to large cohorts.
- Integrates with the same embedding infrastructure used for grading.

---

## ⚡ Summary of Optimizations

| Optimization | Primary Benefit |
|------------|----------------|
| Persistent PostgreSQL cache | Avoid repeated LLM analysis |
| In-memory runtime cache | Reduce database queries |
| Deterministic routing | Eliminate routing API calls |
| Local semantic grading | Eliminate per-answer grading API calls |
| Embedding precomputation | Avoid redundant embedding generation |
| Parallel processing | Faster grading of large batches |
| Rule-based classification | Lower API usage |
| Multi-provider OCR | Improved reliability |
| EasyOCR fallback | Unlimited offline OCR |

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


