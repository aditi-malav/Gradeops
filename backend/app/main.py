from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from pydantic import BaseModel, EmailStr

from app.database import engine
from app.auth import hash_password, verify_password
from app.jwt_handler import create_access_token

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.jwt_handler import create_access_token, verify_access_token
from app.api.grading import router as grading_router
app = FastAPI()
app.include_router(grading_router)
security = HTTPBearer()

# Request Schema

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str   # "instructor" or "ta"



# Root Endpoint

@app.get("/")
def read_root():
    return {"message": "Welcome to GradeOps API"}



# Database Test Endpoint

@app.get("/test-db")
def test_database():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()

    return {
        "database_connected": True,
        "result": value
    }


# Register Endpoint

@app.post("/register")
def register_user(user: RegisterRequest):
    # Validate role
    if user.role not in ["instructor", "ta"]:
        raise HTTPException(
            status_code=400,
            detail="Role must be 'instructor' or 'ta'"
        )

    # Hash the password
    hashed_password = hash_password(user.password)

    # Simple INSERT query
    insert_sql = """
    INSERT INTO users (email, hashed_password, role)
    VALUES (:email, :hashed_password, :role)
    """

    try:
        with engine.connect() as connection:
            connection.execute(
                text(insert_sql),
                {
                    "email": user.email,
                    "hashed_password": hashed_password,
                    "role": user.role
                }
            )
            connection.commit()

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Registration failed: {str(e)}"
        )

    return {
        "message": "User registered successfully",
        "email": user.email,
        "role": user.role
    }

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.post("/login")
def login_user(credentials: LoginRequest):
    # Find user by email
    query = """
    SELECT id, email, hashed_password, role
    FROM users
    WHERE email = :email
    """

    with engine.connect() as connection:
        result = connection.execute(
            text(query),
            {"email": credentials.email}
        )
        user = result.mappings().first()

    # User not found
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(
        credentials.password,
        user["hashed_password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Login successful
    '''
    return {
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"]
        }
    }
    '''
    access_token = create_access_token(
        {
        "sub": user["email"],   # subject
        "role": user["role"],
        "user_id": user["id"]
    }
    )
    
    #return token
    return {
        "access_token":access_token,
        "token_type": "bearer"
    }



@app.get("/me")
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = verify_access_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )

    return {
        "email": payload.get("sub"),
        "role": payload.get("role"),
        "user_id": payload.get("user_id")
    }
#RBAC

# Instructor-Only Dependency

def require_instructor(
    current_user: dict = Depends(get_current_user)
):
    role = current_user.get("role")

    if role != "instructor":
        raise HTTPException(
            status_code=403,
            detail=f"Instructor access required. Current role: {role}"
        )

    return current_user  

@app.get("/instructor-only")
def instructor_only(
    current_user: dict = Depends(require_instructor)
):
    return {
        "message": "Welcome, Instructor!"
    }

class CreateCourseRequest(BaseModel):
    name: str
    code: str

@app.post("/courses")
def create_course(
    course: CreateCourseRequest,
    current_user: dict = Depends(require_instructor)
):
    insert_sql = """
    INSERT INTO courses (name, code, instructor_id)
    VALUES (:name, :code, :instructor_id)
    """

    try:
        with engine.connect() as connection:
            connection.execute(
                text(insert_sql),
                {
                    "name": course.name,
                    "code": course.code,
                    "instructor_id": current_user["user_id"]
                }
            )
            connection.commit()

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Course creation failed: {str(e)}"
        )

    return {
        "message": "Course created successfully",
        "course": {
            "name": course.name,
            "code": course.code,
            "instructor_id": current_user["user_id"]
        }
    }

@app.get("/courses")
def get_courses(
    current_user: dict = Depends(require_instructor)
):
    query = """
    SELECT id, name, code, instructor_id, created_at
    FROM courses
    WHERE instructor_id = :instructor_id
    ORDER BY created_at DESC
    """

    with engine.connect() as connection:
        result = connection.execute(
            text(query),
            {
                "instructor_id": current_user["user_id"]
            }
        )

        rows = result.mappings().all()

    courses = []

    for row in rows:
        courses.append({
            "id": row["id"],
            "name": row["name"],
            "code": row["code"],
            "instructor_id": row["instructor_id"],
            "created_at": str(row["created_at"])
        })

    return {
        "courses": courses
    }

#create exam inside course
class CreateExamRequest(BaseModel):
    course_id: int
    title: str
    total_marks: int

@app.post("/exams")
def create_exam(
    exam: CreateExamRequest,
    current_user: dict = Depends(require_instructor)
):
    # Verify that the course belongs to the logged-in instructor
    check_query = """
    SELECT id
    FROM courses
    WHERE id = :course_id
      AND instructor_id = :instructor_id
    """

    with engine.connect() as connection:
        result = connection.execute(
            text(check_query),
            {
                "course_id": exam.course_id,
                "instructor_id": current_user["user_id"]
            }
        )
        course = result.mappings().first()

        if not course:
            raise HTTPException(
                status_code=404,
                detail="Course not found or not owned by you"
            )

        # Insert the exam
        insert_query = """
        INSERT INTO exams (course_id, title, total_marks)
        VALUES (:course_id, :title, :total_marks)
        """

        connection.execute(
            text(insert_query),
            {
                "course_id": exam.course_id,
                "title": exam.title,
                "total_marks": exam.total_marks
            }
        )
        connection.commit()

    return {
        "message": "Exam created successfully",
        "exam": {
            "course_id": exam.course_id,
            "title": exam.title,
            "total_marks": exam.total_marks
        }
    }

@app.get("/courses/{course_id}/exams")
def get_exams(
    course_id: int,
    current_user: dict = Depends(require_instructor)
):
    # Ensure the course belongs to the current instructor
    check_query = """
    SELECT id
    FROM courses
    WHERE id = :course_id
      AND instructor_id = :instructor_id
    """

    with engine.connect() as connection:
        result = connection.execute(
            text(check_query),
            {
                "course_id": course_id,
                "instructor_id": current_user["user_id"]
            }
        )
        course = result.mappings().first()

        if not course:
            raise HTTPException(
                status_code=404,
                detail="Course not found or not owned by you"
            )

        # Fetch all exams for the course
        exams_query = """
        SELECT id, course_id, title, total_marks, created_at
        FROM exams
        WHERE course_id = :course_id
        ORDER BY created_at DESC
        """

        result = connection.execute(
            text(exams_query),
            {"course_id": course_id}
        )
        rows = result.mappings().all()

    exams = []
    for row in rows:
        exams.append({
            "id": row["id"],
            "course_id": row["course_id"],
            "title": row["title"],
            "total_marks": row["total_marks"],
            "created_at": str(row["created_at"])
        })

    return {
        "exams": exams
    }


#creating question
class CreateQuestionRequest(BaseModel):
    exam_id: int
    question_number: int
    max_marks: int
    expected_answer: str
    rubric: str



@app.post("/questions")
def create_question(
    question: CreateQuestionRequest,
    current_user: dict = Depends(require_instructor)
):
    # Verify that the exam belongs to the current instructor
    check_query = """
    SELECT e.id
    FROM exams e
    JOIN courses c ON e.course_id = c.id
    WHERE e.id = :exam_id
      AND c.instructor_id = :instructor_id
    """

    with engine.connect() as connection:
        result = connection.execute(
            text(check_query),
            {
                "exam_id": question.exam_id,
                "instructor_id": current_user["user_id"]
            }
        )
        exam = result.mappings().first()

        if not exam:
            raise HTTPException(
                status_code=404,
                detail="Exam not found or not owned by you"
            )

        # Insert the question
        insert_query = """
        INSERT INTO questions (
            exam_id,
            question_number,
            max_marks,
            expected_answer,
            rubric
        )
        VALUES (
            :exam_id,
            :question_number,
            :max_marks,
            :expected_answer,
            :rubric
        )
        """

        connection.execute(
            text(insert_query),
            {
                "exam_id": question.exam_id,
                "question_number": question.question_number,
                "max_marks": question.max_marks,
                "expected_answer": question.expected_answer,
                "rubric": question.rubric
            }
        )
        connection.commit()

    return {
        "message": "Question created successfully",
        "question": {
            "exam_id": question.exam_id,
            "question_number": question.question_number,
            "max_marks": question.max_marks
        }
    }

@app.get("/exams/{exam_id}/questions")
def get_questions(
    exam_id: int,
    current_user: dict = Depends(require_instructor)
):
    # Ensure the exam belongs to the current instructor
    check_query = """
    SELECT e.id
    FROM exams e
    JOIN courses c ON e.course_id = c.id
    WHERE e.id = :exam_id
      AND c.instructor_id = :instructor_id
    """

    with engine.connect() as connection:
        result = connection.execute(
            text(check_query),
            {
                "exam_id": exam_id,
                "instructor_id": current_user["user_id"]
            }
        )
        exam = result.mappings().first()

        if not exam:
            raise HTTPException(
                status_code=404,
                detail="Exam not found or not owned by you"
            )

        query = """
        SELECT
            id,
            exam_id,
            question_number,
            max_marks,
            expected_answer,
            rubric,
            created_at
        FROM questions
        WHERE exam_id = :exam_id
        ORDER BY question_number
        """

        result = connection.execute(
            text(query),
            {"exam_id": exam_id}
        )
        rows = result.mappings().all()

    questions = []
    for row in rows:
        questions.append({
            "id": row["id"],
            "exam_id": row["exam_id"],
            "question_number": row["question_number"],
            "max_marks": row["max_marks"],
            "expected_answer": row["expected_answer"],
            "rubric": row["rubric"],
            "created_at": str(row["created_at"])
        })

    return {
        "questions": questions
    }

import os
import shutil
from uuid import uuid4

from fastapi import UploadFile, File

@app.post("/upload-answer-sheets")
def upload_answer_sheet(
    exam_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(require_instructor)
):
    # Verify that the exam belongs to the current instructor
    check_query = """
    SELECT e.id
    FROM exams e
    JOIN courses c ON e.course_id = c.id
    WHERE e.id = :exam_id
      AND c.instructor_id = :instructor_id
    """

    with engine.connect() as connection:
        result = connection.execute(
            text(check_query),
            {
                "exam_id": exam_id,
                "instructor_id": current_user["user_id"]
            }
        )
        exam = result.mappings().first()

        if not exam:
            raise HTTPException(
                status_code=404,
                detail="Exam not found or not owned by you"
            )

        # Validate file type
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )

        # Ensure upload directory exists
        os.makedirs("uploads", exist_ok=True)

        # Generate unique filename
        unique_filename = f"{uuid4()}_{file.filename}"
        file_path = os.path.join("uploads", unique_filename)

        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Store metadata in database
        insert_query = """
        INSERT INTO answer_sheets (exam_id, filename, file_path)
        VALUES (:exam_id, :filename, :file_path)
        """

        connection.execute(
            text(insert_query),
            {
                "exam_id": exam_id,
                "filename": file.filename,
                "file_path": file_path
            }
        )
        connection.commit()

    return {
        "message": "Answer sheet uploaded successfully",
        "file": {
            "original_filename": file.filename,
            "stored_path": file_path,
            "exam_id": exam_id
        }
    }
    
    
@app.get("/exams/{exam_id}/answer-sheets")
def get_answer_sheets(
    exam_id: int,
    current_user: dict = Depends(require_instructor)
):
    # Verify exam ownership
    check_query = """
    SELECT e.id
    FROM exams e
    JOIN courses c ON e.course_id = c.id
    WHERE e.id = :exam_id
      AND c.instructor_id = :instructor_id
    """

    with engine.connect() as connection:
        result = connection.execute(
            text(check_query),
            {
                "exam_id": exam_id,
                "instructor_id": current_user["user_id"]
            }
        )
        exam = result.mappings().first()

        if not exam:
            raise HTTPException(
                status_code=404,
                detail="Exam not found or not owned by you"
            )

        # Fetch uploaded files
        query = """
        SELECT id, exam_id, filename, file_path, upload_time
        FROM answer_sheets
        WHERE exam_id = :exam_id
        ORDER BY upload_time DESC
        """

        result = connection.execute(
            text(query),
            {"exam_id": exam_id}
        )
        rows = result.mappings().all()

    answer_sheets = []
    for row in rows:
        answer_sheets.append({
            "id": row["id"],
            "exam_id": row["exam_id"],
            "filename": row["filename"],
            "file_path": row["file_path"],
            "upload_time": str(row["upload_time"])
        })

    return {
        "answer_sheets": answer_sheets
    }

# OCR
from app.services.multi_ocr_service import MultiOCRService
import os


@app.post("/answer-sheets/{answer_sheet_id}/run-ocr")
def run_ocr(
    answer_sheet_id: int,
    current_user: dict = Depends(require_instructor)
):
    # Verify ownership and get file path
    query = """
    SELECT a.id, a.file_path
    FROM answer_sheets a
    JOIN exams e ON a.exam_id = e.id
    JOIN courses c ON e.course_id = c.id
    WHERE a.id = :answer_sheet_id
      AND c.instructor_id = :instructor_id
    """

    with engine.connect() as connection:
        result = connection.execute(
            text(query),
            {
                "answer_sheet_id": answer_sheet_id,
                "instructor_id": current_user["user_id"]
            }
        )

        answer_sheet = result.mappings().first()

        if not answer_sheet:
            raise HTTPException(
                status_code=404,
                detail="Answer sheet not found or not owned by you"
            )

        # Verify that the file exists
        if not os.path.exists(answer_sheet["file_path"]):
            raise HTTPException(
                status_code=404,
                detail=f"File not found on disk: {answer_sheet['file_path']}"
            )

        # Run OCR using multi-provider OCR pipeline:
        # Groq -> OpenRouter -> Hugging Face -> EasyOCR
        try:
            ocr_service = MultiOCRService()

            extracted_text = ocr_service.extract_text(
                answer_sheet["file_path"]
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"OCR failed: {str(e)}"
            )

        # Save or update OCR result
        upsert_query = """
        INSERT INTO ocr_results (
            answer_sheet_id,
            extracted_text,
            ocr_provider,
            processing_status
        )
        VALUES (
            :answer_sheet_id,
            :extracted_text,
            :ocr_provider,
            :processing_status
        )
        ON CONFLICT (answer_sheet_id)
        DO UPDATE SET
            extracted_text = EXCLUDED.extracted_text,
            ocr_provider = EXCLUDED.ocr_provider,
            processing_status = EXCLUDED.processing_status,
            created_at = CURRENT_TIMESTAMP
        """

        connection.execute(
            text(upsert_query),
            {
                "answer_sheet_id": answer_sheet_id,
                "extracted_text": extracted_text,
                "ocr_provider": "multi_ocr_pipeline",
                "processing_status": "completed"
            }
        )

        connection.commit()

    return {
        "message": "OCR completed successfully",
        "answer_sheet_id": answer_sheet_id,
        "provider": "multi_ocr_pipeline",
        "pipeline": [
            "GroqOCRService",
            "OpenRouterOCRService",
            "HuggingFaceOCRService",
            "EasyOCRService"
        ],
        "characters_extracted": len(extracted_text)
    }


# Retrieve OCR text
@app.get("/answer-sheets/{answer_sheet_id}/ocr")
def get_ocr_result(
    answer_sheet_id: int,
    current_user: dict = Depends(require_instructor)
):
    query = """
    SELECT
        o.id,
        o.answer_sheet_id,
        o.extracted_text,
        o.ocr_provider,
        o.processing_status,
        o.created_at
    FROM ocr_results o
    JOIN answer_sheets a ON o.answer_sheet_id = a.id
    JOIN exams e ON a.exam_id = e.id
    JOIN courses c ON e.course_id = c.id
    WHERE o.answer_sheet_id = :answer_sheet_id
      AND c.instructor_id = :instructor_id
    """

    with engine.connect() as connection:
        result = connection.execute(
            text(query),
            {
                "answer_sheet_id": answer_sheet_id,
                "instructor_id": current_user["user_id"]
            }
        )

        ocr_result = result.mappings().first()

        if not ocr_result:
            raise HTTPException(
                status_code=404,
                detail="OCR result not found"
            )

    return {
        "id": ocr_result["id"],
        "answer_sheet_id": ocr_result["answer_sheet_id"],
        "ocr_provider": ocr_result["ocr_provider"],
        "processing_status": ocr_result["processing_status"],
        "created_at": str(ocr_result["created_at"]),
        "extracted_text": ocr_result["extracted_text"]
    }
