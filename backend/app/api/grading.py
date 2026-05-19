# backend/app/api/grading.py

from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal
from app.workflows.grading_workflow import grading_workflow
from app.services.grading_service import GradingService
from app.services.question_analysis_service import QuestionAnalysisService

router = APIRouter(prefix="/grading", tags=["Grading"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def build_question_metadata(db: Session, exam_id: int):
    """
    Build enriched metadata for all questions.

    Includes:
    - expected_answer
    - rubric
    - max_marks
    - question_analysis (persistent cache)
    - parsed_criteria
    - criterion_embeddings (in-memory only for this exam)
    - expected_embedding (in-memory only for this exam)
    """

    grading_service = GradingService()
    question_analysis_service = QuestionAnalysisService()

    result = db.execute(
        text("""
            SELECT
                question_number,
                expected_answer,
                rubric,
                max_marks
            FROM questions
            WHERE exam_id = :exam_id
            ORDER BY question_number
        """),
        {"exam_id": exam_id}
    )

    rows = result.fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="No questions found for this exam"
        )

    question_numbers = []
    question_metadata = {}

    for row in rows:
        question_number = row.question_number

        # Your database currently does not contain a question_text column.
        # We keep this placeholder because QuestionAnalysisService
        # still expects a question_text parameter.
        question_text = ""

        expected_answer = row.expected_answer or ""
        rubric = row.rubric or ""
        max_marks = row.max_marks

        question_numbers.append(question_number)

        # 1. Question analysis using persistent cache
        question_analysis = question_analysis_service.analyze_question(
            question_text=question_text,
            expected_answer=expected_answer,
            rubric=rubric,
            db=db
        )

        # 2. Parse rubric into grading criteria
        parsed_criteria = grading_service._parse_rubric(
            rubric,
            max_marks
        )

        # 3. Precompute criterion embeddings once for this exam
        criterion_embeddings = []

        for item in parsed_criteria:
            embedding = grading_service.model.encode(
                item["criterion"],
                convert_to_tensor=True
            )

            criterion_embeddings.append({
                "criterion": item["criterion"],
                "marks": item["marks"],
                "embedding": embedding
            })

        # 4. Precompute expected answer embedding once for this exam
        if expected_answer.strip():
            expected_embedding = grading_service.model.encode(
                expected_answer,
                convert_to_tensor=True
            )
        else:
            expected_embedding = None

        # 5. Store enriched metadata
        question_metadata[question_number] = {
            "question_text": question_text,
            "expected_answer": expected_answer,
            "rubric": rubric,
            "max_marks": max_marks,
            "question_analysis": question_analysis,
            "parsed_criteria": parsed_criteria,
            "criterion_embeddings": criterion_embeddings,
            "expected_embedding": expected_embedding
        }

    return question_numbers, question_metadata


def get_exam_ocr_text(db: Session, exam_id: int):
    """
    Returns all answer sheets that already have OCR results.
    """

    result = db.execute(
        text("""
            SELECT
                a.id AS answer_sheet_id,
                o.extracted_text
            FROM answer_sheets a
            JOIN ocr_results o
                ON a.id = o.answer_sheet_id
            WHERE a.exam_id = :exam_id
            ORDER BY a.id
        """),
        {"exam_id": exam_id}
    )

    rows = result.fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="No OCR results found. Run OCR first."
        )

    all_ocr_data = []

    for row in rows:
        all_ocr_data.append({
            "answer_sheet_id": row.answer_sheet_id,
            "extracted_text": row.extracted_text
        })

    return all_ocr_data


def process_answer_sheet(
    item,
    question_numbers,
    question_metadata
):
    """
    Run LangGraph workflow for one answer sheet.
    """

    workflow_result = grading_workflow.invoke({
        "extracted_text": item["extracted_text"],
        "question_numbers": question_numbers,
        "question_metadata": question_metadata
    })

    return {
        "answer_sheet_id": item["answer_sheet_id"],
        "workflow_result": workflow_result
    }


@router.post("/grade-exam/{exam_id}")
def grade_exam(
    exam_id: int,
    db: Session = Depends(get_db)
):
    """
    Run the complete LangGraph grading workflow for all
    answer sheets belonging to the given exam.
    """

    # 1. Build enriched question metadata once per exam
    question_numbers, question_metadata = build_question_metadata(
        db,
        exam_id
    )

    # 2. Load OCR text for all answer sheets
    all_ocr_data = get_exam_ocr_text(
        db,
        exam_id
    )

    # 3. Process answer sheets in parallel
    results = []
    max_workers = 4  # Adjust based on your machine

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                process_answer_sheet,
                item,
                question_numbers,
                question_metadata
            )
            for item in all_ocr_data
        ]

        for future in as_completed(futures):
            results.append(future.result())

    # 4. Keep results ordered by answer_sheet_id
    results.sort(key=lambda x: x["answer_sheet_id"])

    # 5. Return response
    return {
        "exam_id": exam_id,
        "exam_title": f"Exam {exam_id}",
        "total_answer_sheets": len(results),
        "results": results
    }