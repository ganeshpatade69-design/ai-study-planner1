from datetime import date,datetime
from datetime import timedelta

# from datetime import date, timedelta

# Difficulty weight mapping
DIFFICULTY_WEIGHT = {
    "easy": 1,
    "medium": 2,
    "hard": 3
}

def urgency_weight(days_left):
    if days_left <= 25:
        return 3
    elif days_left <= 31:
        return 2
    else:
        return 1

def calculate_priority(subject):
    diff_wt = DIFFICULTY_WEIGHT[subject["difficulty"]]
    days_left = (subject["exam_date"] - date.today()).days
    urg_wt = urgency_weight(days_left)
    return diff_wt + urg_wt

# def allocate_time(subjects, daily_hours):
#     total_priority = sum(s["priority"] for s in subjects)
#     for s in subjects:
#         s["allocated_hours"] = round(
#             (s["priority"] / total_priority) * daily_hours, 2
#         )

#     # ensure total hours = daily_hours
#     total_allocated = sum([s["allocated_hours"] for s in subjects])

#     remaining = daily_hours - total_allocated

#     if remaining > 0:
#        subjects[0]["allocated_hours"] += remaining
#     return subjects

# def allocate_time(subjects, daily_hours):

#     total_priority = sum(s["priority"] for s in subjects)

#     # First allocation
#     for s in subjects:
#         s["allocated_hours"] = (s["priority"] / total_priority) * daily_hours

#     # Round values
#     for s in subjects:
#         s["allocated_hours"] = round(s["allocated_hours"], 1)

#     # Fix missing hours
#     total_allocated = sum(s["allocated_hours"] for s in subjects)
#     remaining = round(daily_hours - total_allocated, 1)

#     i = 0
#     while remaining > 0:
#         subjects[i]["allocated_hours"] += 0.5
#         remaining -= 0.5
#         i = (i + 1) % len(subjects)

#     return subjects

def allocate_time(subjects, daily_hours):

    # Step 1: sort subjects by priority (highest first)
    subjects.sort(key=lambda x: x["priority"], reverse=True)

    remaining_hours = daily_hours

    # Step 2: give minimum time to each subject
    for s in subjects:
        s["allocated_hours"] = 0.5
        remaining_hours -= 0.5

    # Step 3: distribute remaining hours based on priority
    i = 0
    while remaining_hours > 0:
        subjects[i]["allocated_hours"] += 0.5
        remaining_hours -= 0.5
        i = (i + 1) % len(subjects)

    return subjects

    
#from datetime import date

def generate_deadline_alerts(subjects):
    alerts = []
    today = date.today()

    for s in subjects:
        days_left = (s["exam_date"] - today).days

        if days_left <= 25:
            alerts.append(f"⚠️ {s['name']} exam in {days_left} days (High Priority)")
        elif days_left <= 31:
            alerts.append(f"⏳ {s['name']} exam in {days_left} days")

    return alerts

def identify_weak_subjects(subjects):
    weak_subjects = []

    for s in subjects:
        if s["difficulty"] == "hard" and s["priority"] >= 5:
            weak_subjects.append(
                f"📌 Extra revision suggested for {s['name']}"
            )

    return weak_subjects

# def generate_weekly_timetable(subjects, daily_hours):
#     timetable = []
#     today = date.today()

#     # Sort by priority high → low
#     subjects_sorted = sorted(subjects, key=lambda x: x["priority"], reverse=True)

#     last_exam = max(s["exam_date"] for s in subjects_sorted)

#     current_day = today

#     while current_day < last_exam:

#         hours_left = daily_hours

#         for subject in subjects_sorted:

#             # Stop if exam is over
#             if subject["exam_date"] <= current_day:
#                 continue

#             if hours_left <= 0:
#                 break

#             # Give max 2 hrs per subject per day
#             study_hours = min(2, hours_left)

#             timetable.append({
#                 "day": current_day.strftime("%A"),
#                 "subject": subject["name"],
#                 "hours": round(study_hours, 2)
#             })

#             hours_left -= study_hours

#         current_day += timedelta(days=1)

#     return timetable





#2

# def generate_weekly_timetable(subjects, daily_hours):
#     from datetime import date, timedelta

#     timetable = []
#     today = date.today()

#     # Sort by priority
#     subjects_sorted = sorted(subjects, key=lambda x: x["priority"], reverse=True)

#     last_exam = max(s["exam_date"] for s in subjects_sorted)

#     current_day = today

#     while current_day <= last_exam:

#         hours_left = daily_hours

#         for subject in subjects_sorted:

#             if subject["exam_date"] >= current_day and hours_left > 0:

#                 # give SMALL chunk instead of full allocation
#                 study_hours = min(1, hours_left)   # give 1 hr at a time

#                 timetable.append({
#                     "day": current_day.strftime("%A"),
#                     "subject": subject["name"],
#                     "hours": study_hours
#                 })

#                 hours_left -= study_hours

#         current_day += timedelta(days=1)

#     return timetable






#3

# def generate_weekly_timetable(subjects, daily_hours):
#     from datetime import date, timedelta

#     timetable = []
#     today = date.today()

#     # Sort by priority (high → low)
#     subjects_sorted = sorted(subjects, key=lambda x: x["priority"], reverse=True)

#     last_exam = max(s["exam_date"] for s in subjects_sorted)

#     current_day = today

#     while current_day <= last_exam:

#         hours_left = daily_hours

#         # Recalculate dynamic urgency weight daily
#         daily_priority = []

#         for s in subjects_sorted:
#             days_left = (s["exam_date"] - current_day).days

#             if days_left >= 0:
#                 urgency = 3 if days_left <= 25 else 2 if days_left <= 31 else 1
#                 dynamic_score = s["priority"] + urgency
#                 daily_priority.append((dynamic_score, s))

#         # Sort based on dynamic urgency
#         daily_priority.sort(reverse=True, key=lambda x: x[0])

#         # Allocate hours smartly
#         for score, subject in daily_priority:

#             if hours_left <= 0:
#                 break

#             # Hard subjects get bigger chunks
#             if subject["difficulty"] == "hard":
#                 study_hours = min(2, hours_left)
#             elif subject["difficulty"] == "medium":
#                 study_hours = min(1.5, hours_left)
#             else:
#                 study_hours = min(1, hours_left)

#             timetable.append({
#                 "day": current_day.strftime("%Y-%m-%d"),
#                 "day_name": current_day.strftime("%A"),
#                 "subject": subject["name"],
#                 "hours": round(study_hours, 2)
#             })

#             hours_left -= study_hours

#         current_day += timedelta(days=1)

#     return timetable


from datetime import datetime, timedelta

# def generate_weekly_timetable(subjects, daily_hours):

#     timetable = []
#     today = datetime.today().date()

#     last_exam_date = max(s["exam_date"] for s in subjects)

#     total_days = (last_exam_date - today).days + 1

#     for i in range(total_days):

#         day = today + timedelta(days=i)

#         for s in subjects:

#             if day > s["exam_date"]:
#                 continue

#             timetable.append({
#                 "day": str(day),
#                 "subject": s["name"],
#                 "hours": s["allocated_hours"]
#             })

#     return timetable


from datetime import datetime, timedelta

def generate_weekly_timetable(subjects, daily_hours):

    timetable = []
    today = datetime.today().date()

    # get last exam date
    last_exam = max(s["exam_date"] for s in subjects)

    total_days = (last_exam - today).days + 1

    subject_index = 0

    for d in range(total_days):

        current_day = today + timedelta(days=d)
        hours_left = daily_hours

        while hours_left > 0:

            subject = subjects[subject_index % len(subjects)]

            # skip subject if exam finished
            if current_day > subject["exam_date"]:
                subject_index += 1
                continue

            study_hours = min(1, hours_left)

            timetable.append({
                "day": str(current_day),
                "subject": subject["name"],
                "hours": study_hours
            })

            hours_left -= study_hours
            subject_index += 1

    return timetable


def format_timetable_landscape(timetable):
    formatted = {}

    for entry in timetable:
        day = entry["day"]
        subject = entry["subject"]
        hours = entry["hours"]

        if day not in formatted:
            formatted[day] = {}

        #formatted[day][subject] = hours
        formatted[day][subject] = formatted[day].get(subject, 0) + hours

    return formatted



