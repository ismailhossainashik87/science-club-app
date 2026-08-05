from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

app = FastAPI(title="Science Club API")

# Temporary In-memory Database (Later you can use PostgreSQL/SQLite)
users_db = []
exams_db = []
work_logs_db = []


# Pydantic Models for Data Validation
class UserRegister(BaseModel):
    name: str
    email: str
    department: str
    university: str
    designation: str


class ExamSchedule(BaseModel):
    name: str
    exam_type: str
    exam_date: str  # Format: YYYY-MM-DD
    justification: str = ""


class WorkLog(BaseModel):
    name: str
    date: str
    hours: float
    core_work: str
    assigned_by: str
    extra_dedication: bool


# 1. Registration Endpoint
@app.post("/register")
def register_user(user: UserRegister):
    user_dict = user.dict()
    user_dict["status"] = "Pending"
    users_db.append(user_dict)
    return {"message": "Registration successful. Waiting for admin approval.", "user": user_dict}


# 2. Exam Schedule Endpoint with Smart Logic
@app.post("/submit-exam")
def submit_exam(exam: ExamSchedule):
    try:
        e_date = datetime.strptime(exam.exam_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    if exam.exam_type == "Class Test (CT)":
        unavailable_from = e_date - timedelta(days=2)
    elif exam.exam_type == "Semester Final":
        unavailable_from = e_date - timedelta(days=20)
    else:  # Yearly Exam
        unavailable_from = e_date - timedelta(days=30)

    exam_data = {
        "name": exam.name,
        "exam_type": exam.exam_type,
        "exam_date": str(e_date),
        "unavailable_from": str(unavailable_from),
        "justification": exam.justification,
    }
    exams_db.append(exam_data)
    return {"message": "Exam schedule saved!", "data": exam_data}


# 3. Work Log Endpoint
@app.post("/submit-work")
def submit_work(log: WorkLog):
    work_logs_db.append(log.dict())
    return {"message": "Work log saved successfully!"}


# 4. Get Data for Dashboard / App View
@app.get("/status")
def get_status():
    return {"users": users_db, "exams": exams_db, "work_logs": work_logs_db}