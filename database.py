import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="@Aakansha01",   # ← put your MySQL password
        database="ai_study_planner"
    )
    return conn
def create_user(username, email, password):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO users (username, email, password)
    VALUES (%s, %s, %s)
    """

    cursor.execute(query, (username, email, password))
    conn.commit()

    cursor.close()
    conn.close()

def get_user(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE username=%s"

    cursor.execute(query, (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user

def insert_student(daily_hours):
    conn = get_connection()
    cursor = conn.cursor()

    query = "INSERT INTO student (daily_hours) VALUES (%s)"
    cursor.execute(query, (daily_hours,))

    conn.commit()
    student_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return student_id
def insert_subject(student_id, subject):
    conn = get_connection()
    cursor = conn.cursor()
    difficulty_map = {
    "easy": 1,
    "medium": 2,
    "hard": 3
}

    difficulty_value = difficulty_map[subject["difficulty"]]

    

    query = """
    INSERT INTO subjects
    (student_id, name, difficulty, exam_date, priority, allocated_hours)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        student_id,
        subject["name"],
        difficulty_value,
        subject["exam_date"],
        subject["priority"],
        subject["allocated_hours"]

    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()
    
    
def insert_alert(type, message):
    conn = get_connection()
    cursor = conn.cursor()

    query = "INSERT INTO alerts (type, message) VALUES (%s, %s)"
    cursor.execute(query, (type, message))

    conn.commit()
    cursor.close()
    conn.close()
    
    
def insert_timetable(student_id, weekly_timetable):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO weekly_timetable
    (student_id, day, subject, hours)
    VALUES (%s, %s, %s, %s)
    """

    for entry in weekly_timetable:
        values = (
            student_id,
            entry["day"],
            entry["subject"],
            entry["hours"]
        )
        cursor.execute(query, values)

    conn.commit()
    cursor.close()
    conn.close()


