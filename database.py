import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path

# Determine the appropriate path for the database file
if os.name == 'nt':  # Windows
    app_data_path = Path(os.getenv('APPDATA', Path.home() / 'AppData' / 'Roaming'))
else:  # Linux, macOS, etc.
    app_data_path = Path(os.getenv('XDG_DATA_HOME', Path.home() / '.local' / 'share'))

DATABASE_DIR = app_data_path / 'OfflineCompiler'
DATABASE_DIR.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'code_history.sqlite3'}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the CodeHistory model
class CodeHistory(Base):
    __tablename__ = "code_history"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String, index=True)
    code = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    # Add a title or description field, perhaps derived from the first line of code or user input
    title = Column(String, default="Untitled")

# Create the database tables
def create_db_tables():
    Base.metadata.create_all(bind=engine)

# --- Database Helper Functions ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_code_history(db_session, language: str, code: str, title: str = None):
    if not title:
        # Generate a simple title from the first line of code if not provided
        first_line = code.split('\n', 1)[0].strip()
        title = first_line[:50] if first_line else "Untitled Snippet"
        if len(first_line) > 50:
            title += "..."

    db_entry = CodeHistory(language=language, code=code, title=title, timestamp=datetime.datetime.utcnow())
    db_session.add(db_entry)
    db_session.commit()
    db_session.refresh(db_entry)
    return db_entry

def get_all_code_history(db_session):
    return db_session.query(CodeHistory).order_by(CodeHistory.timestamp.desc()).all()

def get_code_history_by_id(db_session, entry_id: int):
    return db_session.query(CodeHistory).filter(CodeHistory.id == entry_id).first()

def delete_code_history_by_id(db_session, entry_id: int):
    entry = db_session.query(CodeHistory).filter(CodeHistory.id == entry_id).first()
    if entry:
        db_session.delete(entry)
        db_session.commit()
        return True
    return False

if __name__ == "__main__":
    # This will create the database and tables if they don't exist when database.py is run directly
    print(f"Database will be created at: {DATABASE_DIR / 'code_history.sqlite3'}")
    create_db_tables()
    print("Database tables created (if they didn't exist).")

    # Example Usage (for testing)
    # db = next(get_db())
    # add_code_history(db, "python", "print('Hello World')", "Hello Python")
    # add_code_history(db, "rust", "fn main() {\n  println!(\"Hello, Rust!\");\n}", "Hello Rust")
    # history = get_all_code_history(db)
    # for item in history:
    #     print(f"ID: {item.id}, Lang: {item.language}, Title: {item.title}, Time: {item.timestamp}")
    # if history:
    #     delete_code_history_by_id(db, history[0].id)
    #     print(f"Deleted entry with ID: {history[0].id}")
    # db.close()
