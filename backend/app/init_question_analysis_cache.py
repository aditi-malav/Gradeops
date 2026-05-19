from sqlalchemy import text
from app.database import engine


def init_question_analysis_cache():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS question_analysis_cache (
                cache_key TEXT PRIMARY KEY,
                question_text TEXT,
                expected_answer TEXT,
                rubric TEXT,
                analysis_json JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()


if __name__ == "__main__":
    init_question_analysis_cache()
    print("question_analysis_cache table created successfully.")