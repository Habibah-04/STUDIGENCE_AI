import tempfile
from pathlib import Path
from src import db

def test_user_task_and_quiz(monkeypatch):
    tmp=Path(tempfile.mkdtemp())/"test.db"
    monkeypatch.setattr(db,"DB_PATH",str(tmp))
    db.init_db()
    db.create_user("Test User","test@example.com","strongpass123","College","Learn AI")
    u=db.authenticate("test@example.com","strongpass123")
    assert u and u["name"]=="Test User"
    db.add_task(u["id"],"Read BFS","AI","2026-12-01",30,"High")
    assert len(db.tasks(u["id"]))==1
    db.save_attempt(u["id"],"AI",2,1,[{"q":"x"}])
    assert db.attempts(u["id"])[0]["score"]==50
