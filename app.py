# from database import insert_student, insert_subject, insert_alert,insert_timetable

# from flask import Flask, render_template, request
# from datetime import date, datetime
# from ai_logic import calculate_priority, allocate_time
# from ai_logic import generate_deadline_alerts
# from ai_logic import format_timetable_landscape

# # from database import create_tables
# # from database import insert_student, insert_subject, insert_alert




# from ai_logic import (
#     calculate_priority,
#     allocate_time,
#     generate_deadline_alerts,
#     identify_weak_subjects,
#     generate_weekly_timetable
# )



# app = Flask(__name__)

# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         daily_hours = int(request.form["daily_hours"])

#         subjects = []
#         subject_names = request.form.getlist("subject")
#         difficulties = request.form.getlist("difficulty")
#         exam_dates = request.form.getlist("exam_date")
       

#         difficulty_map = {
#              "easy": 1,
#              "medium": 2,
#               "hard": 3
# }


#         for i in range(len(subject_names)):
#             subject = {
#                 "name": subject_names[i],
#                 "difficulty": difficulties[i].lower(),   # KEEP AS TEXT
#                  "exam_date": datetime.strptime(exam_dates[i], "%Y-%m-%d").date()
#     }

#             subject["priority"] = calculate_priority(subject)
#             subjects.append(subject)


#         subjects = allocate_time(subjects, daily_hours)
#         for s in subjects:
#             s["allocated_hours"] = float(s["allocated_hours"])

        
#         alerts = generate_deadline_alerts(subjects)
#         weak_subjects = identify_weak_subjects(subjects)
#         weekly_timetable_raw = generate_weekly_timetable(subjects, daily_hours)
#         weekly_timetable = format_timetable_landscape(weekly_timetable_raw)


#         # ===== SAVE DATA INTO MYSQL =====

#         student_id = insert_student(daily_hours)

#         for s in subjects:
#           insert_subject(student_id, s)

#         for alert in alerts:
#           insert_alert("Deadline", alert)

#         for weak in weak_subjects:
#            insert_alert("Weak Subject", weak)
           
        
#         weekly_timetable = generate_weekly_timetable(subjects, daily_hours)
#         weekly_timetable = format_timetable_landscape(weekly_timetable_raw)



#         return render_template("result.html", subjects=subjects, alerts=alerts,
#                                weak_subjects=weak_subjects,
#                               weekly_timetable=weekly_timetable )

#     return render_template("index.html")
# # create_tables()


# if __name__ == "__main__":
#     app.run(debug=True)



from flask import Flask, render_template, request, redirect, session,url_for
from datetime import datetime,date
from werkzeug.security import generate_password_hash,check_password_hash

from database import insert_student, insert_subject, insert_alert,create_user,get_user
from ai_logic import (
    calculate_priority,
    allocate_time,
    generate_deadline_alerts,
    identify_weak_subjects,
    generate_weekly_timetable,
    format_timetable_landscape
)

app = Flask(__name__)
app.secret_key = "studyplannersecret"
@app.route("/", methods=["GET", "POST"])
def index():

    if "user_id" not in session :
        return redirect("/login")
   
    if request.method == "POST":


        session["completed_sessions"] = []
        session["completed_hours"] = 0

        daily_hours = int(request.form["daily_hours"])

        subjects = []
        subject_names = request.form.getlist("subject")
        difficulties = request.form.getlist("difficulty")
        exam_dates = request.form.getlist("exam_date")

        #save data
        session["daily_hours"] = daily_hours
        session["subject_names"] = subject_names
        session["difficulties"] = difficulties
        session["exam_dates"] = exam_dates

        for i in range(len(subject_names)):
            
            if subject_names[i] == "" or exam_dates[i] == "":
                 continue

            subject = {
                "name": subject_names[i],
                "difficulty": difficulties[i],
                "exam_date": datetime.strptime(exam_dates[i], "%Y-%m-%d").date()
            }

            subject["priority"] = calculate_priority(subject)
            subjects.append(subject)

            if len(subjects) == 0:
                return "Please enter at least one subject"

        # Allocate study hours
        subjects = allocate_time(subjects, daily_hours)
        # Calculate total planned hours
        total_hours = 0
        for s in subjects:
            total_hours += float(s["allocated_hours"])

# For now assume completed hours = 0
        completed_hours = 0

# Calculate progress %
        if total_hours > 0:
            progress_percent = int((completed_hours / total_hours) * 100)
        else:
           progress_percent = 0

        # Convert to float for display
        for s in subjects:
            s["allocated_hours"] = float(s["allocated_hours"])

        # Generate AI outputs
        alerts = generate_deadline_alerts(subjects)
        weak_subjects = identify_weak_subjects(subjects)

        weekly_raw = generate_weekly_timetable(subjects, daily_hours)
        weekly_timetable = format_timetable_landscape(weekly_raw)

        total_hours = sum([s["allocated_hours"] for s in subjects])

        session["weekly_timetable"] = weekly_timetable
        session["subjects"] = subjects
        session["alerts"] = alerts
        session["weak_subjects"] = weak_subjects
        session["total_hours"] = total_hours

        # ===== SAVE INTO DATABASE =====
        student_id = insert_student(daily_hours)

        for s in subjects:
            insert_subject(student_id, s)

        for alert in alerts:
            insert_alert("Deadline", alert)

        for weak in weak_subjects:
            insert_alert("Weak Subject", weak)

        today = datetime.today().strftime("%Y-%m-%d")
        return render_template(
            "result.html",
            subjects=subjects,
            alerts=alerts,
            weak_subjects=weak_subjects,
            weekly_timetable=weekly_timetable,
            completed_hours=completed_hours,
            progress_percent=progress_percent,
            total_hours=total_hours,
            today=today,
            completed_sessions=session.get("completed_session", [])
        )

    return render_template(
        "index.html",
         daily_hours=session.get("daily_hours",""),
         subject_names=session.get("subject_names",[]),
         difficulties=session.get("difficulties",[]),
         exam_dates=session.get("exam_dates",[])
)   

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        create_user(username, email, hashed_password)

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = get_user(username)

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            return redirect("/")

        else:
            return "Invalid login"

    return render_template("login.html")

# @app.route("/complete", methods=["GET","POST"])

# def complete():

#     completed_hours = session.get("completed_hours", 0)
#     total_hours = session.get("total_hours", 0)

#     # Increase only if not exceeded
#     if request.method == "POST":
#        if completed_hours < total_hours:
#             completed_hours += 1

#             session["completed_hours"] = completed_hours

#     progress_percent = int((completed_hours / total_hours) * 100) if total_hours > 0 else 0

#     # Limit progress to 100%
#     if progress_percent > 100:
#         progress_percent = 100

#     return render_template(
#         "result.html",
#         subjects=session.get("subjects"),
#         alerts=session.get("alerts"),
#         weak_subjects=session.get("weak_subjects"),
#         weekly_timetable=session.get("weekly_timetable"),
#         total_hours=total_hours,
#         completed_hours=completed_hours,
#         progress_percent=progress_percent
#    )

# from datetime import date,datetime

# @app.route("/complete", methods=["POST"])
# def complete():

#     subject = request.form["subject"]
#     day = request.form["day"]

#     completed_sessions = session.get("completed_sessions", [])
#     total_hours = session.get("total_hours",1)
#     completed_hours = session.get("completed_hours",0)
#     progress_percent = int((completed_hours / total_hours) * 100) if total_hours else 0

#     key = f"{day}_{subject}"

#     if key not in completed_sessions:
#         completed_sessions.append(key)
#         session["completed_sessions"] = completed_sessions

#         session["completed_hours"] = session.get("completed_hours", 0) + 1
        
        
#         return redirect("/result")
#        # ADD THESE LINES HERE
#     from datetime import datetime
#     today = datetime.today().strftime("%Y-%m-%d")
  

#     return render_template(
#         "result.html",
#         subjects=session.get("subjects"),
#         alerts=session.get("alerts"),
#         weak_subjects=session.get("weak_subjects"),
#         weekly_timetable=session.get("weekly_timetable"),
#         total_hours=total_hours,
#         completed_hours=completed_hours,
#         progress_percent=progress_percent,
#         today=today,
#         completed_sessions=session.get("completed_sessions", [])
#     )


from datetime import datetime

# @app.route("/complete", methods=["POST"])
# def complete():

#     subject = request.form["subject"]
#     day = request.form["day"]

#     completed_sessions = session.get("completed_sessions", [])
#     total_hours = session.get("total_hours", 1)

#     key = f"{day}_{subject}"

#     if key not in completed_sessions:
#         completed_sessions.append(key)
#         session["completed_sessions"] = completed_sessions

#     subjects = session.get("subjects")

#     for s in subjects:
#         if s["name"] == subject:
#             session["completed_hours"] = session.get("completed_hours", 0) + float(s["allocated_hours"])
#             break

#     # Always redirect to result page
#     return redirect("/result")

@app.route("/complete", methods=["POST"])
def complete():

    subject = request.form["subject"]
    day = request.form["day"]

    key = f"{day}_{subject}"

    completed_sessions = session.get("completed_sessions")

    if completed_sessions is None:
        completed_sessions = []

    if key not in completed_sessions:

        completed_sessions.append(key)
        session["completed_sessions"] = completed_sessions

        subjects = session.get("subjects", [])

        for s in subjects:
            if s["name"] == subject:
                session["completed_hours"] = session.get("completed_hours", 0) + float(s["allocated_hours"])
                break

    return redirect("/result")


@app.route("/analytics")
def analytics():

    total_hours = session.get("total_hours", 0)
    completed_hours = session.get("completed_hours", 0)

    remaining_hours = total_hours - completed_hours

    subjects = session.get("subjects", [])

    return render_template(
        "analytics.html",
        total_hours=total_hours,
        completed_hours=completed_hours,
        remaining_hours=remaining_hours,
        subjects=subjects
    )

@app.route("/result")
def result():

    total_hours = session.get("total_hours", 1)
    completed_hours = session.get("completed_hours", 0)

    progress_percent = int((completed_hours / total_hours) * 100)

    today = datetime.today().strftime("%Y-%m-%d")

    return render_template(
        "result.html",
        subjects=session.get("subjects"),
        alerts=session.get("alerts"),
        weak_subjects=session.get("weak_subjects"),
        weekly_timetable=session.get("weekly_timetable"),
        total_hours=total_hours,
        completed_hours=completed_hours,
        progress_percent=progress_percent,
        today=today,
        completed_sessions=session.get("completed_sessions", [])
    )

if __name__ == "__main__":
    app.run(debug=True)