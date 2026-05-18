from sqlalchemy import create_engine

username = "root"
password = "priyanshu%402205"

DATABASE_URL = f"mysql+pymysql://{username}:{password}@localhost/resume_analyzer"

engine = create_engine(DATABASE_URL)

print("Database Connected Successfully")