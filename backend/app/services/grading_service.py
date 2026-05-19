# backend/app/services/grading_service.py

import re
from sentence_transformers import SentenceTransformer, util


class GradingService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def grade_answer(
        self,
        student_answer: str,
        expected_answer: str,
        rubric: str,
        max_marks: float,
        precomputed_criteria=None,
        precomputed_expected_embedding=None,
        parsed_criteria=None,
        criterion_embeddings=None,
        expected_embedding=None,
        question_analysis=None
    ) -> dict:
        """
        Grade an answer using a rubric-driven local approach.

        Supports both:
        1. Old optimization parameters:
           - precomputed_criteria
           - precomputed_expected_embedding

        2. New optimization parameters:
           - parsed_criteria
           - criterion_embeddings
           - expected_embedding
           - question_analysis
        """

        # -----------------------------------------------------
        # Handle empty answers
        # -----------------------------------------------------
        if not student_answer or not student_answer.strip():
            return {
                "marks_awarded": 0.0,
                "max_marks": max_marks,
                "criterion_results": [],
                "overall_similarity": 0.0,
                "confidence_score": 0.0,
                "feedback": "No answer provided.",
                "grading_method": "rubric_based_local",
                "question_type": (
                    question_analysis.get("question_type")
                    if question_analysis else "unknown"
                )
            }

        # -----------------------------------------------------
        # Determine which criteria to use
        # -----------------------------------------------------
        if criterion_embeddings is not None:
            criteria = criterion_embeddings

        elif parsed_criteria is not None:
            criteria = parsed_criteria

        elif precomputed_criteria is not None:
            criteria = precomputed_criteria

        else:
            criteria = self._parse_rubric(
                rubric,
                max_marks
            )

        # -----------------------------------------------------
        # Fallback if no criteria were extracted
        # -----------------------------------------------------
        if not criteria:
            criteria = [
                {
                    "criterion": expected_answer,
                    "marks": max_marks
                }
            ]

        # -----------------------------------------------------
        # Compute student embedding once
        # -----------------------------------------------------
        student_embedding = self.model.encode(
            student_answer,
            convert_to_tensor=True
        )

        criterion_results = []
        total_marks = 0.0

        # -----------------------------------------------------
        # Evaluate each criterion
        # -----------------------------------------------------
        for item in criteria:
            criterion_text = item["criterion"]
            criterion_marks = float(item["marks"])

            # Reuse precomputed embedding if available
            if (
                "embedding" in item
                and item["embedding"] is not None
            ):
                criterion_embedding = item["embedding"]
            else:
                criterion_embedding = self.model.encode(
                    criterion_text,
                    convert_to_tensor=True
                )

            similarity = util.cos_sim(
                student_embedding,
                criterion_embedding
            ).item()

            # Clamp similarity to [0, 1]
            similarity = max(
                0.0,
                min(1.0, similarity)
            )

            threshold = self._get_threshold(
                criterion_text
            )

            # Full marks
            if similarity >= threshold:
                awarded = criterion_marks
                satisfied = True

            # Partial marks
            elif similarity >= threshold - 0.10:
                awarded = round(
                    criterion_marks * 0.5,
                    2
                )
                satisfied = "partial"

            # No marks
            else:
                awarded = 0.0
                satisfied = False

            total_marks += awarded

            criterion_results.append({
                "criterion": criterion_text,
                "marks_possible": criterion_marks,
                "marks_awarded": awarded,
                "similarity": round(similarity, 4),
                "threshold": threshold,
                "satisfied": satisfied
            })

        # -----------------------------------------------------
        # Cap total marks at max_marks
        # -----------------------------------------------------
        total_marks = min(
            total_marks,
            float(max_marks)
        )

        total_marks = round(
            total_marks,
            2
        )

        # -----------------------------------------------------
        # Overall similarity with expected answer
        # -----------------------------------------------------
        if expected_answer and expected_answer.strip():

            if expected_embedding is not None:
                final_expected_embedding = expected_embedding

            elif precomputed_expected_embedding is not None:
                final_expected_embedding = (
                    precomputed_expected_embedding
                )

            else:
                final_expected_embedding = self.model.encode(
                    expected_answer,
                    convert_to_tensor=True
                )

            overall_similarity = util.cos_sim(
                student_embedding,
                final_expected_embedding
            ).item()

            overall_similarity = max(
                0.0,
                min(1.0, overall_similarity)
            )

        else:
            overall_similarity = 0.0

        # -----------------------------------------------------
        # High-similarity fallback
        # If rubric parsing yields zero marks but the student's
        # answer is highly similar to the expected answer,
        # award full marks.
        # -----------------------------------------------------
        if total_marks == 0 and overall_similarity >= 0.80:
            total_marks = float(max_marks)

        # -----------------------------------------------------
        # Confidence score
        # -----------------------------------------------------
        rubric_ratio = (
            total_marks / float(max_marks)
            if max_marks > 0 else 0.0
        )

        confidence_score = round(
            (rubric_ratio + overall_similarity) / 2,
            4
        )

        # -----------------------------------------------------
        # Generate feedback
        # -----------------------------------------------------
        feedback = self._generate_feedback(
            total_marks,
            max_marks,
            criterion_results
        )

        # -----------------------------------------------------
        # Final output
        # -----------------------------------------------------
        return {
            "marks_awarded": round(total_marks, 2),
            "max_marks": max_marks,
            "criterion_results": criterion_results,
            "overall_similarity": round(
                overall_similarity,
                4
            ),
            "confidence_score": confidence_score,
            "feedback": feedback,
            "grading_method": "rubric_based_local",
            "question_type": (
                question_analysis.get("question_type")
                if question_analysis else "unknown"
            )
        }

    def _parse_rubric(
        self,
        rubric: str,
        max_marks: float
    ) -> list:
        """
        Parse rubric into structured criteria.

        Supports:
        - "Criterion - 2 marks"
        - "Criterion: 2 marks"

        Also removes instructional phrases such as:
        - "Award full marks if the student states ..."
        - "Give full marks if the student should state ..."
        """
        if not rubric or not rubric.strip():
            return []

        criteria = []

        for line in rubric.splitlines():
            line = line.strip()

            if not line:
                continue

            # -------------------------------------------------
            # Remove instructional phrases
            # -------------------------------------------------
            line = re.sub(
                r'^(award|give)\s+(full\s+)?marks?\s+if\s+',
                '',
                line,
                flags=re.IGNORECASE
            )

            line = re.sub(
                r'^the\s+student\s+(states?|should\s+state)\s+',
                '',
                line,
                flags=re.IGNORECASE
            )

            # -------------------------------------------------
            # Remove numbering like:
            # 1. , 1) , 1-
            # -------------------------------------------------
            line = re.sub(
                r'^\d+[\.\)\-]\s*',
                '',
                line
            )

            # -------------------------------------------------
            # Match structured criteria:
            # "Criterion - 2 marks"
            # "Criterion: 2 marks"
            # -------------------------------------------------
            match = re.search(
                r'(.+?)\s*[-:]\s*(\d+(?:\.\d+)?)\s*marks?',
                line,
                re.IGNORECASE
            )

            if match:
                criterion_text = match.group(1).strip()
                marks = float(match.group(2))

                criteria.append({
                    "criterion": criterion_text,
                    "marks": marks
                })

        # -----------------------------------------------------
        # Free-form rubric fallback
        # -----------------------------------------------------
        if not criteria:
            cleaned_rubric = rubric.strip()

            # Remove instructional phrases from full rubric
            cleaned_rubric = re.sub(
                r'^(award|give)\s+(full\s+)?marks?\s+if\s+',
                '',
                cleaned_rubric,
                flags=re.IGNORECASE
            )

            cleaned_rubric = re.sub(
                r'^the\s+student\s+(states?|should\s+state)\s+',
                '',
                cleaned_rubric,
                flags=re.IGNORECASE
            )

            criteria = [
                {
                    "criterion": cleaned_rubric,
                    "marks": max_marks
                }
            ]

        return criteria

    def _get_threshold(
        self,
        criterion_text: str
    ) -> float:
        """
        Short criteria require stricter similarity.
        Longer criteria allow more semantic variation.
        """

        word_count = len(
            criterion_text.split()
        )

        if word_count <= 3:
            return 0.85
        elif word_count <= 8:
            return 0.80
        else:
            return 0.75

    def _generate_feedback(
        self,
        total_marks: float,
        max_marks: float,
        criterion_results: list
    ) -> str:
        missed = []

        for result in criterion_results:
            if result["marks_awarded"] == 0:
                missed.append(
                    result["criterion"]
                )

        if total_marks == max_marks:
            return (
                "Excellent answer. "
                "All rubric criteria were satisfied."
            )

        if total_marks == 0:
            return (
                "The answer did not satisfy "
                "the key rubric criteria."
            )

        if missed:
            return (
                f"Awarded {total_marks} out of "
                f"{max_marks} marks. "
                f"Missing or weak areas: "
                f"{', '.join(missed[:3])}."
            )

        return (
            f"Awarded {total_marks} "
            f"out of {max_marks} marks."
        )