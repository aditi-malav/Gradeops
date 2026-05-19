import re


class RoutingService:
    def route_answers(
        self,
        extracted_text: str,
        question_numbers: list
    ) -> dict:
        """
        Deterministically route answers by detecting patterns such as:
        Question 1
        Q1
        1.

        Returns:
        {
            "1": "student answer to question 1",
            "2": "student answer to question 2"
        }
        """

        routed_answers = {}

        # Normalize line endings
        text = extracted_text.replace("\r\n", "\n")

        # Single-question exams: everything after "Answer:" is treated as the response
        if len(question_numbers) == 1:
            match = re.search(
                r"Answer\s*:?\s*(.*)",
                text,
                re.IGNORECASE | re.DOTALL
            )

            if match:
                routed_answers[str(question_numbers[0])] = match.group(1).strip()
            else:
                routed_answers[str(question_numbers[0])] = text.strip()

            return routed_answers

        # Multi-question handling
        for i, q_num in enumerate(question_numbers):
            current_patterns = [
                rf"Question\s*{q_num}\b",
                rf"Q\s*{q_num}\b",
                rf"^{q_num}\."
            ]

            current_regex = "|".join(current_patterns)

            start_match = re.search(
                current_regex,
                text,
                re.IGNORECASE | re.MULTILINE
            )

            if not start_match:
                routed_answers[str(q_num)] = ""
                continue

            start_index = start_match.end()

            # Find next question marker
            end_index = len(text)

            if i + 1 < len(question_numbers):
                next_q = question_numbers[i + 1]

                next_patterns = [
                    rf"Question\s*{next_q}\b",
                    rf"Q\s*{next_q}\b",
                    rf"^{next_q}\."
                ]

                next_regex = "|".join(next_patterns)

                next_match = re.search(
                    next_regex,
                    text[start_index:],
                    re.IGNORECASE | re.MULTILINE
                )

                if next_match:
                    end_index = start_index + next_match.start()

            answer_text = text[start_index:end_index].strip()

            # Remove leading "Answer:"
            answer_text = re.sub(
                r"^Answer\s*:?\s*",
                "",
                answer_text,
                flags=re.IGNORECASE
            )

            routed_answers[str(q_num)] = answer_text

        return routed_answers