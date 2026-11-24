import os, sqlite3, hashlib, hmac, secrets
from pathlib import Path
from datetime import datetime, date, timedelta

DB_PATH = os.getenv("STUDIGENCE_DB_PATH", str(Path(__file__).resolve().parents[1] / "data" / "studigence.db"))

def conn():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL, salt TEXT NOT NULL, education_level TEXT DEFAULT 'College',
          goal TEXT DEFAULT '', created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS study_tasks(
          id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, title TEXT NOT NULL,
          subject TEXT DEFAULT '', due_date TEXT NOT NULL, minutes INTEGER DEFAULT 30,
          priority TEXT DEFAULT 'Medium', status TEXT DEFAULT 'Pending',
          created_at TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS quiz_attempts(
          id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, topic TEXT NOT NULL,
          total INTEGER NOT NULL, correct INTEGER NOT NULL, score REAL NOT NULL,
          answers_json TEXT DEFAULT '', created_at TEXT NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS mistakes(
          id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, topic TEXT NOT NULL,
          question TEXT NOT NULL, chosen TEXT NOT NULL, correct_answer TEXT NOT NULL,
          category TEXT NOT NULL, created_at TEXT NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS revisions(
          id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, topic TEXT NOT NULL,
          due_date TEXT NOT NULL, interval_days INTEGER DEFAULT 1, ease REAL DEFAULT 2.5,
          repetitions INTEGER DEFAULT 0, last_quality INTEGER,
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS documents(
          id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, filename TEXT NOT NULL,
          extracted_text TEXT NOT NULL, created_at TEXT NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS focus_sessions(
          id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, minutes INTEGER NOT NULL,
          note TEXT DEFAULT '', created_at TEXT NOT NULL,
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
        """)
        c.commit()

def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260000).hex()

def create_user(name, email, password, level, goal):
    name, email = name.strip(), email.strip().lower()
    if not name or not email or "@" not in email: raise ValueError("Enter a valid name and email.")
    if len(password) < 8: raise ValueError("Password must contain at least 8 characters.")
    salt = secrets.token_hex(16)
    with conn() as c:
        try:
            c.execute("INSERT INTO users(name,email,password_hash,salt,education_level,goal,created_at) VALUES(?,?,?,?,?,?,?)",
                      (name,email,_hash(password,salt),salt,level,goal,datetime.utcnow().isoformat()))
            c.commit()
        except sqlite3.IntegrityError: raise ValueError("An account with this email already exists.")

def authenticate(email, password):
    with conn() as c:
        row = c.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    if not row or not hmac.compare_digest(row["password_hash"], _hash(password,row["salt"])): return None
    return {"id":row["id"],"name":row["name"],"email":row["email"],"education_level":row["education_level"],"goal":row["goal"]}

def get_profile(uid):
    with conn() as c:
        r=c.execute("SELECT name,email,education_level,goal FROM users WHERE id=?",(uid,)).fetchone()
    return dict(r) if r else {}

def update_profile(uid,name,level,goal):
    with conn() as c:
        c.execute("UPDATE users SET name=?,education_level=?,goal=? WHERE id=?",(name,level,goal,uid)); c.commit()

def add_task(uid,title,subject,due,minutes,priority):
    with conn() as c:
        c.execute("INSERT INTO study_tasks(user_id,title,subject,due_date,minutes,priority,created_at) VALUES(?,?,?,?,?,?,?)",
                  (uid,title,subject,str(due),minutes,priority,datetime.utcnow().isoformat())); c.commit()

def tasks(uid):
    with conn() as c: return [dict(x) for x in c.execute("SELECT * FROM study_tasks WHERE user_id=? ORDER BY due_date",(uid,))]
def update_task_status(task_id,uid,status):
    with conn() as c: c.execute("UPDATE study_tasks SET status=? WHERE id=? AND user_id=?",(status,task_id,uid)); c.commit()

def save_attempt(uid,topic,total,correct,answers):
    import json
    with conn() as c:
        c.execute("INSERT INTO quiz_attempts(user_id,topic,total,correct,score,answers_json,created_at) VALUES(?,?,?,?,?,?,?)",
                  (uid,topic,total,correct,100*correct/max(total,1),json.dumps(answers),datetime.utcnow().isoformat())); c.commit()
def attempts(uid):
    with conn() as c: return [dict(x) for x in c.execute("SELECT * FROM quiz_attempts WHERE user_id=? ORDER BY created_at DESC",(uid,))]
def add_mistake(uid,topic,q,chosen,correct,category):
    with conn() as c:
        c.execute("INSERT INTO mistakes(user_id,topic,question,chosen,correct_answer,category,created_at) VALUES(?,?,?,?,?,?,?)",
                  (uid,topic,q,chosen,correct,category,datetime.utcnow().isoformat())); c.commit()
def mistakes(uid):
    with conn() as c: return [dict(x) for x in c.execute("SELECT * FROM mistakes WHERE user_id=? ORDER BY created_at DESC",(uid,))]
def add_revision(uid,topic,due):
    with conn() as c:
        c.execute("INSERT INTO revisions(user_id,topic,due_date) VALUES(?,?,?)",(uid,topic,str(due))); c.commit()
def revisions(uid):
    with conn() as c: return [dict(x) for x in c.execute("SELECT * FROM revisions WHERE user_id=? ORDER BY due_date",(uid,))]
def review_revision(uid,rid,quality):
    with conn() as c:
        r=c.execute("SELECT * FROM revisions WHERE id=? AND user_id=?",(rid,uid)).fetchone()
        if not r: return
        reps=r["repetitions"]+1
        interval=1 if quality<3 else (6 if reps==1 else max(1,round(r["interval_days"]*r["ease"])))
        ease=max(1.3,r["ease"]+(0.1-(5-quality)*(0.08+(5-quality)*0.02)))
        due=(date.today()+timedelta(days=interval)).isoformat()
        c.execute("UPDATE revisions SET due_date=?,interval_days=?,ease=?,repetitions=?,last_quality=? WHERE id=?",
                  (due,interval,ease,reps,quality,rid)); c.commit()
def save_document(uid,filename,text):
    with conn() as c:
        cur=c.execute("INSERT INTO documents(user_id,filename,extracted_text,created_at) VALUES(?,?,?,?)",
                      (uid,filename,text,datetime.utcnow().isoformat())); c.commit(); return cur.lastrowid
def documents(uid):
    with conn() as c: return [dict(x) for x in c.execute("SELECT id,filename,created_at FROM documents WHERE user_id=? ORDER BY created_at DESC",(uid,))]
def get_document(uid,did):
    with conn() as c: return c.execute("SELECT * FROM documents WHERE id=? AND user_id=?",(did,uid)).fetchone()
def add_focus(uid,minutes,note):
    with conn() as c:
        c.execute("INSERT INTO focus_sessions(user_id,minutes,note,created_at) VALUES(?,?,?,?)",(uid,minutes,note,datetime.utcnow().isoformat())); c.commit()
def focus_total(uid):
    """Return total focus minutes from manually logged and automatic sessions."""
    with conn() as c:
        manual_seconds = c.execute(
            "SELECT COALESCE(SUM(minutes),0) * 60 FROM focus_sessions WHERE user_id=?", (uid,)
        ).fetchone()[0]
        # This table is created by src.focus_tracker when automatic tracking starts.
        try:
            automatic_seconds = c.execute(
                "SELECT COALESCE(SUM(duration_seconds),0) FROM focus_activity_sessions WHERE user_id=?", (uid,)
            ).fetchone()[0]
        except sqlite3.OperationalError:
            automatic_seconds = 0
    return (int(manual_seconds or 0) + int(automatic_seconds or 0)) // 60
def counts(uid):
    with conn() as c:
        return {
          "tasks":c.execute("SELECT COUNT(*) FROM study_tasks WHERE user_id=?",(uid,)).fetchone()[0],
          "done":c.execute("SELECT COUNT(*) FROM study_tasks WHERE user_id=? AND status='Completed'",(uid,)).fetchone()[0],
          "attempts":c.execute("SELECT COUNT(*) FROM quiz_attempts WHERE user_id=?",(uid,)).fetchone()[0],
          "mistakes":c.execute("SELECT COUNT(*) FROM mistakes WHERE user_id=?",(uid,)).fetchone()[0]
        }


def delete_revision(uid, rid):
    """Delete one revision item owned by this user."""
    with conn() as c:
        c.execute("DELETE FROM revisions WHERE id=? AND user_id=?", (rid, uid))
        c.commit()
