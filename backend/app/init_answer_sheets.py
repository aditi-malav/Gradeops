from sqlalchemy import text
from app.database import engine

create_answer_sheets_table_sql = """
CREATE TABLE IF NOT EXISTS answer_sheets (
    id SERIAL PRIMARY KEY,
    exam_id INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

with engine.connect() as connection:
    connection.execute(text(create_answer_sheets_table_sql))
    connection.commit()

print("Answer sheets table created successfully.")