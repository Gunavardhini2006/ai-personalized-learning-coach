
import sqlite3
import json
from datetime import datetime

DB_NAME = "learning_coach.db"


# 1. Connect to database
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# 2. Create all database tables
def initialize_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            goal TEXT NOT NULL,
            level TEXT NOT NULL,
            target_days INTEGER NOT NULL,
            daily_minutes INTEGER NOT NULL,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER,
            plan_json TEXT NOT NULL,
            created_at TEXT,
            FOREIGN KEY (learner_id) REFERENCES learners(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER,
            topic TEXT NOT NULL,
            score INTEGER,
            total_questions INTEGER,
            answers_json TEXT,
            feedback TEXT,
            attempted_at TEXT,
            FOREIGN KEY (learner_id) REFERENCES learners(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topic_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id INTEGER,
            topic TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            last_score INTEGER DEFAULT 0,
            FOREIGN KEY (learner_id) REFERENCES learners(id),
            UNIQUE (learner_id, topic)
        )
    """)

    conn.commit()
    conn.close()


# 3. Save learner details
def save_learner(subject, goal, level, days, minutes):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO learners
        (subject, goal, level, target_days, daily_minutes, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (subject, goal, level, days, minutes,
          datetime.now().isoformat(timespec="seconds")))

    learner_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return learner_id


# 4. Save generated learning plan
def save_learning_plan(learner_id, plan):

    conn = get_connection()

    conn.execute("""
        INSERT INTO learning_plans
        (learner_id, plan_json, created_at)
        VALUES (?, ?, ?)
    """, (learner_id, json.dumps(plan),
          datetime.now().isoformat(timespec="seconds")))

    conn.commit()
    conn.close()


# 5. Save quiz attempt
def save_quiz_attempt(learner_id, topic, score,
                      total_questions, answers, feedback):

    conn = get_connection()

    conn.execute("""
        INSERT INTO quiz_attempts
        (learner_id, topic, score, total_questions,
         answers_json, feedback, attempted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (learner_id, topic, score, total_questions,
          json.dumps(answers), feedback,
          datetime.now().isoformat(timespec="seconds")))

    conn.commit()
    conn.close()


# 6. Update topic progress

def update_topic_progress(learner_id, topic, score, total_questions):

    percentage = (score / total_questions) * 100 if total_questions else 0

    status = "Completed" if percentage >= 70 else "Needs Revision"

    conn = get_connection()

    conn.execute("""
        INSERT INTO topic_progress
        (learner_id, topic, status, last_score)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(learner_id, topic)
        DO UPDATE SET
            status = excluded.status,
            last_score = excluded.last_score
    """, (learner_id, topic, status, round(percentage)))

    conn.commit()
    conn.close()



# 7. Retrieve learner quiz history
def get_quiz_history(learner_id):

    conn = get_connection()

    cursor = conn.execute("""
        SELECT topic, score, total_questions, attempted_at
        FROM quiz_attempts
        WHERE learner_id = ?
        ORDER BY id DESC
    """, (learner_id,))

    history = cursor.fetchall()
    conn.close()

    return history


# 8. Retrieve topic progress
def get_topic_progress(learner_id):

    conn = get_connection()

    cursor = conn.execute("""
        SELECT topic, status, last_score
        FROM topic_progress
        WHERE learner_id = ?
    """, (learner_id,))

    progress = cursor.fetchall()
    conn.close()

    return progress
