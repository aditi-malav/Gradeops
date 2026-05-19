from itertools import combinations

from app.services.question_analysis_service import (
    QuestionAnalysisService
)
from app.services.similarity_service import SimilarityService


class PlagiarismService:
    def __init__(self):
        self.question_analysis_service = (
            QuestionAnalysisService()
        )
        self.similarity_service = SimilarityService()

    def _compare_answers(
        self,
        answer1: str,
        answer2: str,
        strategy: str
    ) -> float:
        """
        Compare two answers according to the selected strategy.
        Returns a score between 0 and 1.
        """

        # Ignore certain question types entirely
        if strategy == "ignore":
            return 0.0

        # Numerical questions (very low priority)
        if strategy == "low_priority_exact_match":
            normalized1 = answer1.strip()
            normalized2 = answer2.strip()

            return (
                1.0
                if normalized1 == normalized2
                else 0.0
            )

        # Code similarity (basic MVP version)
        if strategy == "code_similarity":
            # Normalize whitespace
            normalized1 = " ".join(answer1.split())
            normalized2 = " ".join(answer2.split())

            # Exact structural match
            if normalized1 == normalized2:
                return 1.0

            # Fallback to semantic similarity
            return self.similarity_service.compute_similarity(
                normalized1,
                normalized2
            )

        # Semantic similarity for conceptual / essay answers
        if strategy == "semantic_similarity":
            return self.similarity_service.compute_similarity(
                answer1,
                answer2
            )

        # Default fallback
        return self.similarity_service.compute_similarity(
            answer1,
            answer2
        )

    def detect_plagiarism(
        self,
        question_text: str,
        expected_answer: str,
        rubric: str,
        answers: list[dict]
    ) -> dict:
        """
        answers format:
        [
            {
                "student_id": 1,
                "answer": "..."
            },
            {
                "student_id": 2,
                "answer": "..."
            }
        ]
        """

        # Analyze the question and determine the policy
        analysis = self.question_analysis_service.analyze_question(
            question_text=question_text,
            expected_answer=expected_answer,
            rubric=rubric
        )

        strategy = analysis["plagiarism_strategy"]
        threshold = analysis["plagiarism_threshold"]

        # If plagiarism detection should be skipped
        if strategy == "ignore":
            return {
                "analysis": analysis,
                "suspicious_pairs": []
            }

        suspicious_pairs = []

        # Compare every pair of students
        for a, b in combinations(answers, 2):
            score = self._compare_answers(
                a["answer"],
                b["answer"],
                strategy
            )

            if score >= threshold:
                suspicious_pairs.append({
                    "student_1": a["student_id"],
                    "student_2": b["student_id"],
                    "similarity_score": score,
                    "review_required": True
                })

        return {
            "analysis": analysis,
            "total_students": len(answers),
            "total_pairs_checked": (
                len(answers) * (len(answers) - 1)
            ) // 2,
            "suspicious_pairs": suspicious_pairs
        }