# backend/app/services/question_analysis_service.py

import json
import hashlib

from sqlalchemy import text

from app.services.gemini_client import get_gemini_model


class QuestionAnalysisService:
    def __init__(self):
        """
        Two-level cache:
        1. In-memory cache (during server runtime)
        2. PostgreSQL persistent cache (question_analysis_cache table)
        """
        self._memory_cache = {}

    def analyze_question(
        self,
        question_text: str,
        expected_answer: str,
        rubric: str,
        db=None
    ) -> dict:
        """
        Determine how a question should be handled.
        """

        # Build stable cache key
        cache_key = self._build_cache_key(
            question_text,
            expected_answer,
            rubric
        )

        # 1. In-memory cache
        if cache_key in self._memory_cache:
            return self._memory_cache[cache_key]

        # 2. Persistent PostgreSQL cache
        if db is not None:
            cached_result = self._load_from_database(
                db,
                cache_key
            )

            if cached_result:
                self._memory_cache[cache_key] = cached_result
                return cached_result

        # 3. Rule-based analysis
        result = self._rule_based_analysis(
            question_text,
            expected_answer
        )

        # 4. Gemini fallback only for unknown patterns
        if result["question_type"] == "new_pattern":
            result = self._llm_analysis(
                question_text,
                expected_answer,
                rubric
            )

        # Save to in-memory cache
        self._memory_cache[cache_key] = result

        # Save to PostgreSQL cache
        if db is not None:
            self._save_to_database(
                db=db,
                cache_key=cache_key,
                question_text=question_text,
                expected_answer=expected_answer,
                rubric=rubric,
                analysis_result=result
            )

        return result

    def _build_cache_key(
        self,
        question_text: str,
        expected_answer: str,
        rubric: str
    ) -> str:
        """
        Create stable SHA-256 hash from question content.
        """

        combined = (
            (question_text or "").strip()
            + "||"
            + (expected_answer or "").strip()
            + "||"
            + (rubric or "").strip()
        )

        return hashlib.sha256(
            combined.encode("utf-8")
        ).hexdigest()

    def _load_from_database(self, db, cache_key):
        """
        Load cached analysis from PostgreSQL.
        Handles both JSON strings and Python dicts.
        """

        row = db.execute(
            text("""
                SELECT analysis_json
                FROM question_analysis_cache
                WHERE cache_key = :cache_key
            """),
            {"cache_key": cache_key}
        ).mappings().first()

        if not row:
            return None

        # PostgreSQL JSON/JSONB may already be returned as dict
        if isinstance(row.analysis_json, dict):
            return row.analysis_json

        # Otherwise parse JSON string
        return json.loads(row.analysis_json)

    def _save_to_database(
        self,
        db,
        cache_key: str,
        question_text: str,
        expected_answer: str,
        rubric: str,
        analysis_result: dict
    ):
        """
        Persist analysis for future reuse.
        """

        db.execute(
            text("""
                INSERT INTO question_analysis_cache (
                    cache_key,
                    question_text,
                    expected_answer,
                    rubric,
                    analysis_json
                )
                VALUES (
                    :cache_key,
                    :question_text,
                    :expected_answer,
                    :rubric,
                    :analysis_json
                )
                ON CONFLICT (cache_key)
                DO NOTHING
            """),
            {
                "cache_key": cache_key,
                "question_text": question_text,
                "expected_answer": expected_answer,
                "rubric": rubric,
                "analysis_json": json.dumps(analysis_result)
            }
        )

        db.commit()

    def _rule_based_analysis(
        self,
        question_text: str,
        expected_answer: str
    ) -> dict:
        """
        Fast local classification for common question types.
        """

        question_lower = (question_text or "").lower().strip()
        expected = (expected_answer or "").strip()

        # True / False
        if expected.lower() in ["true", "false"]:
            return {
                "question_type": "true_false",
                "plagiarism_strategy": "ignore",
                "plagiarism_threshold": 1.0,
                "review_priority": "none"
            }

        # Numerical answers
        numeric = expected.replace(".", "", 1)
        if numeric.isdigit():
            return {
                "question_type": "numerical",
                "plagiarism_strategy": "ignore",
                "plagiarism_threshold": 1.0,
                "review_priority": "none"
            }

        # Fill in the blank
        if "fill in the blank" in question_lower or "blank" in question_lower:
            return {
                "question_type": "fill_blank",
                "plagiarism_strategy": "ignore",
                "plagiarism_threshold": 1.0,
                "review_priority": "none"
            }

        # Match the following
        if (
            "match the following" in question_lower
            or "match the correct" in question_lower
            or "match the pairs" in question_lower
        ):
            return {
                "question_type": "match_the_following",
                "plagiarism_strategy": "ignore",
                "plagiarism_threshold": 1.0,
                "review_priority": "none"
            }

        # MCQ / Multiple Select
        if (
            "multiple choice" in question_lower
            or "choose the correct option" in question_lower
            or "select all that apply" in question_lower
            or "choose all that apply" in question_lower
            or "tick the correct options" in question_lower
        ):
            return {
                "question_type": "mcq",
                "plagiarism_strategy": "ignore",
                "plagiarism_threshold": 1.0,
                "review_priority": "none"
            }

        # One-word / Very short answers
        if len(expected.split()) <= 2:
            return {
                "question_type": "one_word",
                "plagiarism_strategy": "ignore",
                "plagiarism_threshold": 1.0,
                "review_priority": "none"
            }

        # Code questions
        code_keywords = [
            "write a program",
            "write code",
            "implement",
            "function",
            "python program",
            "java program",
            "c++ program",
            "algorithm"
        ]

        if any(keyword in question_lower for keyword in code_keywords):
            return {
                "question_type": "code",
                "plagiarism_strategy": "code_similarity",
                "plagiarism_threshold": 0.95,
                "review_priority": "high"
            }

        # Essay questions
        if len(expected.split()) > 150:
            return {
                "question_type": "essay",
                "plagiarism_strategy": "semantic_similarity",
                "plagiarism_threshold": 0.92,
                "review_priority": "high"
            }

        # Conceptual / Situation-based questions
        if len(expected.split()) > 5:
            return {
                "question_type": "conceptual",
                "plagiarism_strategy": "semantic_similarity",
                "plagiarism_threshold": 0.90,
                "review_priority": "high"
            }

        # Unknown pattern → Gemini fallback
        return {
            "question_type": "new_pattern",
            "plagiarism_strategy": "llm_recommendation",
            "plagiarism_threshold": 0.90,
            "review_priority": "medium"
        }

    def _llm_analysis(
        self,
        question_text: str,
        expected_answer: str,
        rubric: str
    ) -> dict:
        """
        Rare fallback using Gemini for completely unknown question patterns.
        The result is cached permanently.
        """

        model = get_gemini_model()

        prompt = f"""
You are classifying an exam question for an automated grading system.

QUESTION:
{question_text}

EXPECTED ANSWER:
{expected_answer}

RUBRIC:
{rubric}

Determine:
1. question_type
2. plagiarism_strategy
3. plagiarism_threshold
4. review_priority

Return ONLY valid JSON in this format:

{{
  "question_type": "conceptual",
  "plagiarism_strategy": "semantic_similarity",
  "plagiarism_threshold": 0.90,
  "review_priority": "high"
}}
"""

        response = model.generate_content(prompt)

        return json.loads(response.text.strip())