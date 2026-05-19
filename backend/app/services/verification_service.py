class VerificationService:
    def verify_grading(self, grading_result: dict) -> dict:
        """
        Verify grading quality using local confidence scores.
        No LLM calls are made.

        Returns:
        {
            "verified_marks": 4.0,
            "verification_confidence": 0.91,
            "needs_review": False,
            "review_reason": None
        }
        """

        marks_awarded = grading_result["marks_awarded"]
        confidence = grading_result.get("confidence_score", 0.0)
        overall_similarity = grading_result.get("overall_similarity", 0.0)

        # Conservative confidence estimate
        verification_confidence = round(
            (confidence + overall_similarity) / 2,
            4
        )

        # Decide whether human review is needed
        if verification_confidence >= 0.85:
            needs_review = False
            review_reason = None
        elif verification_confidence >= 0.65:
            needs_review = True
            review_reason = "Medium confidence grading."
        else:
            needs_review = True
            review_reason = "Low confidence grading."

        return {
            "verified_marks": marks_awarded,
            "verification_confidence": verification_confidence,
            "needs_review": needs_review,
            "review_reason": review_reason
        }