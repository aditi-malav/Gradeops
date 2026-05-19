from sqlalchemy import text
from app.database import engine

create_ocr_results_table_sql = """
CREATE TABLE IF NOT EXISTS ocr_results (
    id SERIAL PRIMARY KEY,
    answer_sheet_id INTEGER NOT NULL
        REFERENCES answer_sheets(id) ON DELETE CASCADE,
    extracted_text TEXT NOT NULL,
    ocr_provider VARCHAR(100) NOT NULL,
    processing_status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (answer_sheet_id)
);
"""

with engine.connect() as connection:
    connection.execute(text(create_ocr_results_table_sql))
    connection.commit()

print("OCR results table created successfully.")