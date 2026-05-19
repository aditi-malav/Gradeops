from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, END

from app.services.routing_service import RoutingService
from app.services.grading_service import GradingService


class GradingState(TypedDict, total=False):
    # Input
    extracted_text: str
    question_numbers: List[int]
    question_metadata: Dict[int, Dict[str, Any]]

    # Intermediate
    routed_answers: Dict[str, str]

    # Output
    grading_results: Dict[str, Any]


def routing_node(state: GradingState) -> GradingState:
    """
    Split OCR text into question-wise answers.
    """
    routing_service = RoutingService()

    routed_answers = routing_service.route_answers(
        extracted_text=state["extracted_text"],
        question_numbers=state["question_numbers"]
    )

    return {
        "routed_answers": routed_answers
    }


# Replace ONLY the grading_node() function in:
# backend/app/workflows/grading_workflow.py

def grading_node(state: GradingState) -> GradingState:
    """
    Grade each routed answer using GradingService.

    IMPORTANT:
    Your GradingService.grade_answer() does NOT accept a single
    'question_metadata' argument. It expects separate arguments.

    Therefore we extract values from metadata and pass them individually.
    """

    grading_service = GradingService()

    grading_results = {}

    for question_number in state["question_numbers"]:
        question_key = str(question_number)

        # Student answer routed from OCR text
        student_answer = state["routed_answers"].get(
            question_key,
            ""
        )

        # Metadata prepared in grading.py
        metadata = state["question_metadata"][question_number]

        # Extract fields from metadata
        expected_answer = metadata.get("expected_answer", "")
        rubric = metadata.get("rubric", "")
        max_marks = metadata.get("max_marks", 0)

        # Precomputed optimizations
        parsed_criteria = metadata.get("parsed_criteria")
        criterion_embeddings = metadata.get("criterion_embeddings")
        expected_embedding = metadata.get("expected_embedding")
        question_analysis = metadata.get("question_analysis")

        # Call GradingService with the ACTUAL expected parameters
        result = grading_service.grade_answer(
            student_answer=student_answer,
            expected_answer=expected_answer,
            rubric=rubric,
            max_marks=max_marks,
            parsed_criteria=parsed_criteria,
            criterion_embeddings=criterion_embeddings,
            expected_embedding=expected_embedding,
            question_analysis=question_analysis
        )

        grading_results[question_key] = result

    return {
        "grading_results": grading_results
    }


# Build workflow graph
builder = StateGraph(GradingState)

# Add nodes
builder.add_node("routing", routing_node)
builder.add_node("grading", grading_node)

# Entry point
builder.set_entry_point("routing")

# Routing -> Grading
builder.add_edge("routing", "grading")

# Grading -> END
builder.add_edge("grading", END)

# Compile workflow
grading_workflow = builder.compile()