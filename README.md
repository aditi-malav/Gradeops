# GradeOps
### AI-Powered Automated Exam Grading Platform

GradeOps is a production-oriented SaaS platform that automates the end-to-end workflow of grading scanned examination answer sheets. The system combines OCR, workflow orchestration, semantic similarity models, caching, and parallel processing to deliver accurate, scalable, and cost-efficient automated grading.

The platform consists of:

- **Backend:** FastAPI + PostgreSQL + LangGraph + AI services
- **Frontend:** Streamlit-based instructor dashboard
- **AI Layer:** OCR, semantic grading, and intelligent caching

The project was designed not as a simple academic prototype, but as a robust AI system that applies real-world software engineering principles such as modular architecture, fault tolerance, persistent caching, optimization, and explainable decision-making.

---

# 🚀 Vision

Manual grading of descriptive answer sheets is one of the most time-consuming and repetitive tasks for educators. GradeOps aims to solve this problem by:

- Extracting text from scanned answer sheets
- Automatically routing responses question-wise
- Grading answers using rubrics and semantic similarity
- Generating marks and feedback
- Detecting suspicious similarity patterns
- Reducing instructor workload
- Providing a scalable SaaS foundation for educational institutions

---

# 🏗️ Full System Architecture

```text
Instructor Dashboard (Streamlit Frontend)
                ↓
         FastAPI Backend APIs
                ↓
         PostgreSQL Database
                ↓
      Multi-Provider OCR Engine
 (Groq → OpenRouter → EasyOCR)
                ↓
     Question Analysis Cache
                ↓
  Per-Exam Embedding Precomputation
                ↓
      LangGraph Workflow Engine
        ├── Routing Node
        └── Grading Node
                ↓
         Marks + Feedback
                ↓
     Analytics and Reports
```

---

# 🖥️ Frontend Overview (Streamlit)

The frontend is built using Streamlit to provide a clean, fast, and highly interactive dashboard for instructors and teaching assistants.

## Key Features

- Authentication (Login / Signup)
- Course Management
- Exam Creation
- Question Setup
- PDF Answer Sheet Upload
- OCR Monitoring
- Automated Grading
- Results Visualization
- Analytics Dashboard
- Plagiarism Alerts
- Downloadable Reports

## Frontend Architecture

```text
frontend/
├── app.py
├── pages/
│   ├── login.py
│   ├── dashboard.py
│   ├── courses.py
│   ├── exams.py
│   ├── questions.py
│   ├── upload_answer_sheets.py
│   ├── ocr_monitor.py
│   ├── grading.py
│   ├── results.py
│   └── analytics.py
├── components/
│   ├── sidebar.py
│   ├── metrics_cards.py
│   └── charts.py
└── utils/
    └── api_client.py
```

---

# ⭐ Core Engineering Highlights

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
- Streamlit-based analytical dashboard
- SaaS-oriented product design

---

# 🛠 Technology Stack

## Backend
- FastAPI
- Python 3.13
- SQLAlchemy
- PostgreSQL
- LangGraph

## AI / NLP
- Sentence Transformers (`all-MiniLM-L6-v2`)
- Google Gemini (rare fallback)
- Embedding-based semantic similarity

## OCR Providers
- Groq Vision Models
- OpenRouter Vision Models
- EasyOCR (offline unlimited fallback)

## Frontend
- Streamlit
- Plotly
- Pandas

## Concurrency
- ThreadPoolExecutor

---

# 📁 Project Structure

```text
GradeOps/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── grading.py
│   │   ├── services/
│   │   │   ├── grading_service.py
│   │   │   ├── question_analysis_service.py
│   │   │   ├── routing_service.py
│   │   │   ├── multi_ocr_service.py
│   │   │   ├── groq_ocr_service.py
│   │   │   ├── openrouter_ocr_service.py
│   │   │   ├── easyocr_service.py
│   │   │   └── gemini_client.py
│   │   ├── workflows/
│   │   │   └── grading_workflow.py
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

# 🧠 Key Design Decisions and Rationale

## 1. Workflow-Based Architecture with LangGraph
Grading is modeled as a graph of independent nodes rather than one monolithic function.

## 2. Multi-Provider OCR with Automatic Failover
OCR providers are chained to maximize reliability and free-tier utilization.

## 3. Persistent Question Analysis Cache
Unknown question types are analyzed once and stored permanently.

## 4. Per-Exam Embedding Precomputation
Embeddings are generated once and reused across all answer sheets.

## 5. Parallel Processing
Answer sheets are graded concurrently for significant speedups.

## 6. Hybrid Rule-Based + LLM Classification
Deterministic rules handle common cases; Gemini handles rare new patterns.

## 7. Semantic Rubric-Based Grading
Criterion-level scoring produces explainable marks and feedback.

## 8. Streamlit Dashboard Frontend
Rapidly developed instructor UI for a functional SaaS MVP.

---

# ⚡ Performance Optimizations

| Optimization | Benefit |
|------------|----------|
| Persistent PostgreSQL cache | Avoid repeated LLM analysis |
| In-memory runtime cache | Reduce DB queries |
| Embedding precomputation | Eliminate redundant embeddings |
| Parallel processing | Grade multiple scripts simultaneously |
| Rule-based classification | Minimize API usage |
| Multi-provider OCR | Prevent token exhaustion downtime |
| EasyOCR fallback | Unlimited offline OCR |

---

# 🔌 API Endpoints

## OCR
- `POST /answer-sheets/{answer_sheet_id}/run-ocr`
- `GET /answer-sheets/{answer_sheet_id}/ocr`

## Grading
- `POST /grading/grade-exam/{exam_id}`

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

# 🏆 Why This Project Stands Out

Most student projects focus on:

- CRUD APIs
- Basic OCR
- Simple dashboards

GradeOps demonstrates production-grade engineering concepts including:

- AI workflow orchestration
- Multi-provider fault tolerance
- Persistent knowledge caching
- Embedding optimization
- Explainable grading
- Concurrent processing
- Cost-aware AI integration
- Full-stack SaaS architecture

This reflects system design and optimization skills closer to real-world AI products than typical academic projects.

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

## Product Evolution
- Multi-tenant SaaS architecture
- Subscription billing
- Institution-level dashboards

---

# ▶️ Running the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger UI:
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

> Use AI only where it provides real value, and aggressively eliminate unnecessary API calls through deterministic logic, caching, local computation, and system-level optimization.

This results in a system that is:

- Accurate
- Scalable
- Explainable
- Cost-efficient
- Fault tolerant
- Product-oriented

---

# 👩‍💻 Engineering Focus

This project emphasizes:

- System design
- Optimization
- Full-stack architecture
- Reliability
- Maintainability
- Production readiness

The goal was not simply to integrate AI APIs, but to understand and implement the engineering decisions that make AI systems efficient, robust, and commercially viable.

---

# 📄 License

This project is intended for educational, research, and portfolio purposes.
