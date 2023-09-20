from pymongo import MongoClient
from pydantic import BaseModel, conint
import math
from dotenv import load_dotenv
import os

load_dotenv()

connection_string = os.getenv("CONNECTION_STRING")
client = MongoClient(connection_string)
db = client['Mongodb_practice']
collection = db['students_details']


class Student_detail(BaseModel):
    enrollment: int
    student_name: str
    course: str
    semester: conint(ge=1, le=8)


def create_student(student: Student_detail):
    student_dict = student.model_dump()
    student_dict.update({"_id": student.enrollment})
    del student_dict["enrollment"]
    collection.insert_one(student_dict)
    collection.update_one({"_id": student.enrollment}, {"$set": {"year": math.ceil(student.semester / 2)}})


def next_semester(enrollment_no):
    student = collection.find_one({"_id": enrollment_no})
    if student:
        new_semester = student["semester"] + 1
        if new_semester <= 8:
            collection.update_one({"_id": enrollment_no}, {"$set": {"semester": new_semester}})

        new_year = math.ceil(new_semester / 2)
        if new_year <= 4:
            collection.update_one({"_id": enrollment_no}, {"$set": {"year": new_year}})
            print(f"Student with enrollment {enrollment_no} promoted to semester {new_semester}")
    else:
        print(f"Student with enrollment {enrollment_no} not found")


def get_semester_no(enrollment_no) -> str:
    document = collection.find_one({"_id": enrollment_no})
    if document:
        semester_no = document.get("semester")
        return semester_no


def add_marks(enrollment_no: int, subject: str, marks: int):
    semester_no = get_semester_no(enrollment_no=enrollment_no)
    students_marks = {
        subject: marks
    }
    student = collection.find_one({"_id": enrollment_no})
    if student:
        update_query = {
            "$set": {
                f"students_marks.{semester_no}.{subject}": marks
            }
        }
        collection.update_one({"_id": enrollment_no}, update_query)
    else:
        print(f"Students does not exists with {enrollment_no}.")


def total_marks(enrollment_no):
    document = collection.find_one({"_id": enrollment_no})
    if document:
        student_marks = document.get("student_marks", {})
        total_marks = 0
        for semester_data in student_marks.values():
            for subject_mark in semester_data.values():
                total_marks += subject_mark

        collection.update_one(
            {"_id": enrollment_no},
            {"$set": {"total_marks": total_marks}}
        )

        return total_marks

    else:
        return None


# create_student(Student_detail(enrollment=2100100484, student_name="James", course="B-Tech(CSE-4)", semester=6))
# next_semester(2100100484)
# add_marks(2100102656, "History", 75)
