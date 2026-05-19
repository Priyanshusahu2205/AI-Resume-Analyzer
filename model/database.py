from sqlalchemy import create_engine

username = "root"
password = "priyanshu%402205"

DATABASE_URL = "sqlite:///resume.db"

engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_text TEXT,
            predicted_role TEXT,
            score REAL
        )
    """))
    connection.commit()

print("Database Connected Successfully")