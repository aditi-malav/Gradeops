from sqlalchemy import text
from app.database import engine

create_questions_table_sql = """
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    question_number INTEGER NOT NULL,
    max_marks INTEGER NOT NULL,
    expected_answer TEXT,
    rubric TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (exam_id, question_number)
);
"""

with engine.connect() as connection:
    connection.execute(text(create_questions_table_sql))
    connection.commit()

print("Questions table created successfully.")