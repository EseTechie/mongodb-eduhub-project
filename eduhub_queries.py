from pymongo import MongoClient
from datetime import datetime
from datetime import timedelta
import json
from bson import ObjectId
import random
import pandas as pd



#TASK 1: DATABASE SETUP AND DATA MODELING

#TASK 1.1: CREATE DATABASE AND COLLECTIONS

client = MongoClient('mongodb://localhost:27017/')

db = client['eduhub_db']

def create_collections_with_validation():
    """Create collections with schema validation"""
    
    # Users collection validation
    users_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["userId", "email", "firstName", "lastName", "role"],
            "properties": {
                "userId": {"bsonType": "string"},
                "email": {"bsonType": "string", "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"},
                "firstName": {"bsonType": "string"},
                "lastName": {"bsonType": "string"},
                "role": {"bsonType": "string", "enum": ["student", "instructor"]},
                "dateJoined": {"bsonType": "date"},
                "isActive": {"bsonType": "bool"}
            }
        }
    }
    
    # Courses collection validation
    courses_validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["courseId", "title", "instructorId", "level"],
            "properties": {
                "courseId": {"bsonType": "string"},
                "title": {"bsonType": "string"},
                "instructorId": {"bsonType": "string"},
                "level": {"bsonType": "string", "enum": ["beginner", "intermediate", "advanced"]},
                "price": {"bsonType": "number", "minimum": 0},
                "isPublished": {"bsonType": "bool"}
            }
        }
    }
    
    # validation
    try:
        db.create_collection("users", validator=users_validator)
        db.create_collection("courses", validator=courses_validator)
        db.create_collection("enrollments")
        db.create_collection("lessons")
        db.create_collection("assignments")
        db.create_collection("submissions")
    except Exception as e:
        print(f"Collections may already exist: {e}")
		
		


#TASK 1.2: DESIGN DOCUMENTS SCHEMAS

user_schema = {
    "_id": "ObjectId (auto-generated)",
    "userId": "string (unique)",
    "email": "string (unique, required)",
    "firstName": "string (required)",
    "lastName": "string (required)",
    "role": "string (enum: ['student', 'instructor'])",
    "dateJoined": "datetime",
    "profile": {
        "bio": "string",
        "avatar": "string",
        "skills": ["string"]
    },
    "isActive": "boolean"
}

course_schema = {
    "_id": "ObjectId (auto-generated)",
    "courseId": "string (unique)",
    "title": "string (required)",
    "description": "string",
    "instructorId": "string (reference to users)",
    "category": "string",
    "level": "string (enum: ['beginner', 'intermediate', 'advanced'])",
    "duration": "number (in hours)",
    "price": "number",
    "tags": ["string"],
    "createdAt": "datetime",
    "updatedAt": "datetime",
    "isPublished": "boolean"
}

enrollment_schema = {
    "_id": "ObjectId (auto-generated)",
    "enrollmentId": "string (unique)",
    "studentId": "string (reference to users)",
    "courseId": "string (reference to courses)",
    "enrollmentDate": "datetime",
    "progress": "number (0-100)",
    "completionStatus": "string (enum: ['enrolled', 'in-progress', 'completed', 'dropped'])",
    "completionDate": "datetime"
}
  
lesson_schema = {
    "_id": "ObjectId (auto-generated)",
    "lessonId": "string (unique)",
    "courseId": "string (reference to courses)",
    "title": "string (required)",
    "content": "string",
    "videoUrl": "string",
    "duration": "number (in minutes)",
    "order": "number",
    "createdAt": "datetime"
}

assignment_schema = {
    "_id": "ObjectId (auto-generated)",
    "assignmentId": "string (unique)",
    "courseId": "string (reference to courses)",
    "title": "string (required)",
    "description": "string",
    "dueDate": "datetime",
    "maxPoints": "number",
    "createdAt": "datetime"
}

submission_schema = {
    "_id": "ObjectId (auto-generated)",
    "submissionId": "string (unique)",
    "assignmentId": "string (reference to assignments)",
    "studentId": "string (reference to users)",
    "content": "string",
    "submittedAt": "datetime",
    "grade": "number",
    "feedback": "string",
    "status": "string (enum: ['submitted', 'graded', 'late'])"
}



#TASK 2: DATA POPULATION

#TASK 2.1: INSERT SAMPLE DATA

# Sample data generation functions
def generate_user_id():
    """Generate unique user ID"""
    return f"USER_{random.randint(1000, 9999)}"

def generate_course_id():
    """Generate unique course ID"""
    return f"COURSE_{random.randint(100, 999)}"

def generate_enrollment_id():
    """Generate unique enrollment ID"""
    return f"ENROLL_{random.randint(10000, 99999)}"

def generate_lesson_id():
    """Generate unique lesson ID"""
    return f"LESSON_{random.randint(1000, 9999)}"

def generate_assignment_id():
    """Generate unique assignment ID"""
    return f"ASSIGN_{random.randint(1000, 9999)}"

def generate_submission_id():
    """Generate unique submission ID"""
    return f"SUBMIT_{random.randint(10000, 99999)}"

# Insert 20 users (mix of students and instructors)
print("Inserting users...")
users_data = []

# Create instructors (5 instructors)
instructor_names = [
    ("John", "Smith", "Programming expert with 10+ years experience"),
    ("Sarah", "Johnson", "Data Science and Analytics specialist"),
    ("Michael", "Brown", "Web Development and Design mentor"),
    ("Emily", "Davis", "Business and Marketing strategist"),
    ("David", "Wilson", "Cybersecurity and Network specialist")
]

for i, (first_name, last_name, bio) in enumerate(instructor_names):
    user_doc = {
        "userId": generate_user_id(),
        "email": f"{first_name.lower()}.{last_name.lower()}@eduhub.com",
        "firstName": first_name,
        "lastName": last_name,
        "role": "instructor",
        "dateJoined": datetime.now() - timedelta(days=random.randint(30, 365)),
        "profile": {
            "bio": bio,
            "avatar": f"instructor_{i+1}.jpg",
            "skills": random.sample(["Python", "JavaScript", "Data Analysis", "Machine Learning", "Web Design", "Marketing", "Cybersecurity"], 3)
        },
        "isActive": True
    }
    users_data.append(user_doc)

# Create students (15 students)
student_first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Iris", "Jack", "Kate", "Liam", "Mia", "Noah", "Olivia"]
student_last_names = ["Anderson", "Baker", "Clark", "Edwards", "Fisher", "Garcia", "Harris", "Jackson", "King", "Lopez", "Miller", "Nelson", "Parker", "Quinn", "Roberts"]

for i in range(15):
    user_doc = {
        "userId": generate_user_id(),
        "email": f"{student_first_names[i].lower()}.{student_last_names[i].lower()}@student.com",
        "firstName": student_first_names[i],
        "lastName": student_last_names[i],
        "role": "student",
        "dateJoined": datetime.now() - timedelta(days=random.randint(1, 180)),
        "profile": {
            "bio": f"Passionate learner interested in technology and personal development",
            "avatar": f"student_{i+1}.jpg",
            "skills": random.sample(["HTML", "CSS", "Python", "Excel", "Communication", "Problem Solving"], 2)
        },
        "isActive": True
    }
    users_data.append(user_doc)

# Insert users into database
result = db.users.insert_many(users_data)
print(f" Inserted {len(result.inserted_ids)} users")

# Get instructor IDs for course creation
instructors = list(db.users.find({"role": "instructor"}))
instructor_ids = [instructor["userId"] for instructor in instructors]

# Insert 8 courses across different categories
print("Inserting courses...")
courses_data = []
course_categories = ["Programming", "Data Science", "Web Development", "Business", "Design", "Marketing", "Cybersecurity", "Personal Development"]
course_levels = ["beginner", "intermediate", "advanced"]

course_titles = [
    "Complete Python Bootcamp",
    "Data Science with Python",
    "Full Stack Web Development",
    "Digital Marketing Mastery",
    "UI/UX Design Fundamentals",
    "Business Strategy Essentials",
    "Cybersecurity Basics",
    "Personal Productivity Hacks"
]

course_descriptions = [
    "Learn Python from scratch with hands-on projects",
    "Master data analysis and machine learning with Python",
    "Build modern web applications with React and Node.js",
    "Comprehensive guide to digital marketing strategies",
    "Design beautiful and user-friendly interfaces",
    "Strategic thinking for business success",
    "Essential cybersecurity concepts and practices",
    "Time management and productivity techniques"
]

for i in range(8):
    course_doc = {
        "courseId": generate_course_id(),
        "title": course_titles[i],
        "description": course_descriptions[i],
        "instructorId": random.choice(instructor_ids),
        "category": course_categories[i],
        "level": random.choice(course_levels),
        "duration": random.randint(10, 50),
        "price": random.randint(50, 200),
        "tags": random.sample(["online", "certificate", "practical", "beginner-friendly", "advanced", "hands-on"], 3),
        "createdAt": datetime.now() - timedelta(days=random.randint(10, 100)),
        "updatedAt": datetime.now() - timedelta(days=random.randint(1, 10)),
        "isPublished": random.choice([True, True, True, False])  # Most courses are published
    }
    courses_data.append(course_doc)

result = db.courses.insert_many(courses_data)
print(f" Inserted {len(result.inserted_ids)} courses")

# Get student and course IDs for enrollments
students = list(db.users.find({"role": "student"}))
student_ids = [student["userId"] for student in students]
courses = list(db.courses.find({}))
course_ids = [course["courseId"] for course in courses]

# Insert 15 enrollments
print("Inserting enrollments...")
enrollments_data = []
enrollment_statuses = ["active", "completed", "dropped"]

for i in range(15):
    enrollment_doc = {
        "enrollmentId": generate_enrollment_id(),
        "studentId": random.choice(student_ids),
        "courseId": random.choice(course_ids),
        "enrollmentDate": datetime.now() - timedelta(days=random.randint(1, 60)),
        "progress": random.randint(0, 100),
        "completionDate": datetime.now() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
        "status": random.choice(enrollment_statuses)
    }
    enrollments_data.append(enrollment_doc)

result = db.enrollments.insert_many(enrollments_data)
print(f" Inserted {len(result.inserted_ids)} enrollments")

# Insert 25 lessons
print("Inserting lessons...")
lessons_data = []

for course in courses:
    # Each course gets 3-4 lessons
    num_lessons = random.randint(3, 4)
    for lesson_order in range(1, num_lessons + 1):
        lesson_doc = {
            "lessonId": generate_lesson_id(),
            "courseId": course["courseId"],
            "title": f"Lesson {lesson_order}: {course['title']} - Part {lesson_order}",
            "content": f"Detailed content for lesson {lesson_order} of {course['title']}",
            "videoUrl": f"https://video.eduhub.com/{course['courseId']}/lesson{lesson_order}",
            "duration": random.randint(15, 60),
            "order": lesson_order,
            "createdAt": datetime.now() - timedelta(days=random.randint(5, 50))
        }
        lessons_data.append(lesson_doc)

result = db.lessons.insert_many(lessons_data)
print(f" Inserted {len(result.inserted_ids)} lessons")

# Insert 10 assignments
print("Inserting assignments...")
assignments_data = []
assignment_titles = [
    "Programming Project 1",
    "Data Analysis Exercise",
    "Web Development Task",
    "Marketing Campaign Design",
    "UI Design Challenge",
    "Business Case Study",
    "Security Assessment",
    "Productivity Plan",
    "Final Project",
    "Peer Review Assignment"
]

for i in range(10):
    assignment_doc = {
        "assignmentId": generate_assignment_id(),
        "courseId": random.choice(course_ids),
        "title": assignment_titles[i],
        "description": f"Complete the {assignment_titles[i]} following the course guidelines",
        "dueDate": datetime.now() + timedelta(days=random.randint(7, 30)),
        "maxPoints": random.randint(50, 100),
        "createdAt": datetime.now() - timedelta(days=random.randint(1, 20))
    }
    assignments_data.append(assignment_doc)

result = db.assignments.insert_many(assignments_data)
print(f" Inserted {len(result.inserted_ids)} assignments")

# Get assignment IDs for submissions
assignments = list(db.assignments.find({}))
assignment_ids = [assignment["assignmentId"] for assignment in assignments]

# Insert 12 assignment submissions
print("Inserting submissions...")
submissions_data = []
submission_statuses = ["submitted", "graded", "late"]

for i in range(12):
    submission_doc = {
        "submissionId": generate_submission_id(),
        "assignmentId": random.choice(assignment_ids),
        "studentId": random.choice(student_ids),
        "content": f"Student submission content for assignment {i+1}",
        "submittedAt": datetime.now() - timedelta(days=random.randint(1, 15)),
        "grade": random.randint(60, 100) if random.choice([True, False]) else None,
        "feedback": f"Good work on assignment {i+1}" if random.choice([True, False]) else None,
        "status": random.choice(submission_statuses)
    }
    submissions_data.append(submission_doc)

result = db.submissions.insert_many(submissions_data)
print(f" Inserted {len(result.inserted_ids)} submissions")

# Task 2.2: Data Relationships Verification
print("\n--- Task 2.2: Data Relationships Verification ---")

# Verify referential relationships
print("Verifying data relationships...")

# Check if all courses have valid instructor references
courses_with_invalid_instructors = db.courses.count_documents({
    "instructorId": {"$nin": instructor_ids}
})
print(f" Courses with invalid instructor references: {courses_with_invalid_instructors}")

# Check if all enrollments have valid student and course references
enrollments_with_invalid_refs = db.enrollments.count_documents({
    "$or": [
        {"studentId": {"$nin": student_ids}},
        {"courseId": {"$nin": course_ids}}
    ]
})
print(f" Enrollments with invalid references: {enrollments_with_invalid_refs}")

print(" Data population completed successfully")
print(f" Total documents inserted: {len(users_data) + len(courses_data) + len(enrollments_data) + len(lessons_data) + len(assignments_data) + len(submissions_data




#TASK 3: BASIC CRUD OPERATIONS

#TASK 3.1: CREATE OPERATIONS


# Add new student user
new_student = {
    "userId": generate_user_id(),
    "email": "new.student@example.com",
    "firstName": "New",
    "lastName": "Student",
    "role": "student",
    "dateJoined": datetime.now(),
    "profile": {
        "bio": "Eager to learn new technologies",
        "avatar": "new_student.jpg",
        "skills": ["Python", "JavaScript"]
    },
    "isActive": True
}

result = db.users.insert_one(new_student)
print(f" New student added with ID: {result.inserted_id}")

# 2. Create a new course
new_course = {
    "courseId": generate_course_id(),
    "title": "Advanced Machine Learning",
    "description": "Deep dive into machine learning algorithms and applications",
    "instructorId": random.choice(instructor_ids),
    "category": "Data Science",
    "level": "advanced",
    "duration": 40,
    "price": 150,
    "tags": ["machine learning", "AI", "advanced"],
    "createdAt": datetime.now(),
    "updatedAt": datetime.now(),
    "isPublished": False
}

result = db.courses.insert_one(new_course)
print(f" New course created with ID: {result.inserted_id}")

# 3. Enroll a student in a course
print("3. Enrolling a student in a course...")
new_enrollment = {
    "enrollmentId": generate_enrollment_id(),
    "studentId": new_student["userId"],
    "courseId": new_course["courseId"],
    "enrollmentDate": datetime.now(),
    "progress": 0,
    "completionDate": None,
    "status": "active"
}

result = db.enrollments.insert_one(new_enrollment)
print(f" Student enrolled with enrollment ID: {result.inserted_id}")

# 4. Add a new lesson to an existing course
print("4. Adding a new lesson to the new course...")
new_lesson = {
    "lessonId": generate_lesson_id(),
    "courseId": new_course["courseId"],
    "title": "Introduction to Neural Networks",
    "content": "Learn the basics of neural networks and deep learning",
    "videoUrl": f"https://video.eduhub.com/{new_course['courseId']}/intro_neural_networks",
    "duration": 45,
    "order": 1,
    "createdAt": datetime.now()
}

result = db.lessons.insert_one(new_lesson)
print(f" New lesson added with ID: {result.inserted_id}")


#TASK 3.2: READ OPERATIONS

print("\n--- Task 3.2: Read Operations ---")

# 1. Find all active students
print("1. Finding all active students...")
active_students = list(db.users.find({
    "role": "student",
    "isActive": True
}))
print(f" Found {len(active_students)} active students")
for student in active_students[:3]:  # Show first 3
    print(f"   - {student['firstName']} {student['lastName']} ({student['email']})")

# 2. Retrieve course details with instructor information
print("\n2. Retrieving course details with instructor information...")
# Using aggregation to join courses with instructor details
course_with_instructor = list(db.courses.aggregate([
    {
        "$lookup": {
            "from": "users",
            "localField": "instructorId",
            "foreignField": "userId",
            "as": "instructor"
        }
    },
    {"$unwind": "$instructor"},
    {"$limit": 3}  # Show first 3 courses
]))

print(f" Retrieved {len(course_with_instructor)} courses with instructor details")
for course in course_with_instructor:
    print(f"   - {course['title']} by {course['instructor']['firstName']} {course['instructor']['lastName']}")

# 3. Get all courses in a specific category
print("\n3. Getting all courses in 'Programming' category...")
programming_courses = list(db.courses.find({
    "category": "Programming"
}))
print(f" Found {len(programming_courses)} programming courses")
for course in programming_courses:
    print(f"   - {course['title']} (${course['price']})")

# 4. Find students enrolled in a particular course
print("\n4. Finding students enrolled in a particular course...")
if course_ids:
    sample_course_id = course_ids[0]
    enrolled_students = list(db.enrollments.aggregate([
        {"$match": {"courseId": sample_course_id}},
        {
            "$lookup": {
                "from": "users",
                "localField": "studentId",
                "foreignField": "userId",
                "as": "student"
            }
        },
        {"$unwind": "$student"}
    ]))
    
    print(f" Found {len(enrolled_students)} students enrolled in course {sample_course_id}")
    for enrollment in enrolled_students:
        print(f"   - {enrollment['student']['firstName']} {enrollment['student']['lastName']} (Progress: {enrollment['progress']}%)")

# 5. Search courses by title (case-insensitive, partial match)
print("\n5. Searching courses by title (partial match: 'Python')...")
python_courses = list(db.courses.find({
    "title": {"$regex": "Python", "$options": "i"}
}))
print(f" Found {len(python_courses)} courses matching 'Python'")
for course in python_courses:
    print(f"   - {course['title']}")
	
	
	
#TASK 3.3: UPDATE OPERATIONS

print("\n-- Update Operations ---")

# 1. Update a user's profile information
print("1. Updating user profile information...")
update_result = db.users.update_one(
    {"userId": new_student["userId"]},
    {
        "$set": {
            "profile.bio": "Updated bio: Passionate about AI and machine learning",
            "profile.skills": ["Python", "JavaScript", "Machine Learning", "Data Analysis"]
        }
    }
)
print(f" Updated {update_result.modified_count} user profile")

# 2. Mark a course as published
print("2. Marking course as published...")
update_result = db.courses.update_one(
    {"courseId": new_course["courseId"]},
    {
        "$set": {
            "isPublished": True,
            "updatedAt": datetime.now()
        }
    }
)
print(f" Updated {update_result.modified_count} course publication status")

# 3. Update assignment grades
print("3. Updating assignment grades...")
# Find a submission without a grade and update it
ungraded_submission = db.submissions.find_one({"grade": None})
if ungraded_submission:
    update_result = db.submissions.update_one(
        {"submissionId": ungraded_submission["submissionId"]},
        {
            "$set": {
                "grade": 85,
                "feedback": "Excellent work! Well structured and clear explanation.",
                "status": "graded"
            }
        }
    )
    print(f" Updated {update_result.modified_count} assignment grade")
else:
    print(" No ungraded submissions found to update")

# 4. Add tags to an existing course
print("4. Adding tags to an existing course...")
if courses:
    sample_course = courses[0]
    update_result = db.courses.update_one(
        {"courseId": sample_course["courseId"]},
        {
            "$addToSet": {
                "tags": {"$each": ["popular", "updated-2024"]}
            },
            "$set": {"updatedAt": datetime.now()}
        }
    )
    print(f" Updated {update_result.modified_count} course with new tags")	
	
	
#TASK 3.4: DELETE OPERATIONS

print("\n--- Delete Operations ---")

# 1. Remove a user (soft delete by setting isActive to false)
print("1. Soft deleting a user...")
# Find a student to soft delete (not the one we just created)
student_to_delete = db.users.find_one({
    "role": "student",
    "isActive": True,
    "userId": {"$ne": new_student["userId"]}
})

if student_to_delete:
    update_result = db.users.update_one(
        {"userId": student_to_delete["userId"]},
        {"$set": {"isActive": False}}
    )
    print(f" Soft deleted {update_result.modified_count} user")
else:
    print(" No suitable user found for soft deletion")

# 2. Delete an enrollment
print("2. Deleting an enrollment...")
# Find an enrollment to delete
enrollment_to_delete = db.enrollments.find_one({
    "status": "dropped"
})

if enrollment_to_delete:
    delete_result = db.enrollments.delete_one(
        {"enrollmentId": enrollment_to_delete["enrollmentId"]}
    )
    print(f" Deleted {delete_result.deleted_count} enrollment")
else:
    print(" No suitable enrollment found for deletion")

# 3. Remove a lesson from a course
print("3. Removing a lesson from a course...")
# Find a lesson to delete
lesson_to_delete = db.lessons.find_one({})

if lesson_to_delete:
    delete_result = db.lessons.delete_one(
        {"lessonId": lesson_to_delete["lessonId"]}
    )
    print(f" Deleted {delete_result.deleted_count} lesson")
else:
    print(" No lessons found for deletion")
	
	
	
	
	
#PART 4: ADVANCED QUERIES AND AGGREGATION

#TASK 4.1: COMPLEX QUERIES

print("\n--- Complex Queries ---")

# 1. Find courses with price between $50 and $200
print("1. Finding courses with price between $50 and $200...")
price_range_courses = list(db.courses.find({
    "price": {"$gte": 50, "$lte": 200}
}))
print(f" Found {len(price_range_courses)} courses in price range $50-$200")
for course in price_range_courses[:3]:
    print(f"   - {course['title']}: ${course['price']}")

# 2. Get users who joined in the last 6 months
print("\n2. Getting users who joined in the last 6 months...")
six_months_ago = datetime.now() - timedelta(days=180)
recent_users = list(db.users.find({
    "dateJoined": {"$gte": six_months_ago}
}))
print(f" Found {len(recent_users)} users who joined in the last 6 months")
for user in recent_users[:3]:
    print(f"   - {user['firstName']} {user['lastName']} joined on {user['dateJoined'].strftime('%Y-%m-%d')}")

# 3. Find courses that have specific tags using $in operator
print("\n3. Finding courses with specific tags...")
tagged_courses = list(db.courses.find({
    "tags": {"$in": ["online", "certificate", "hands-on"]}
}))
print(f" Found {len(tagged_courses)} courses with specified tags")
for course in tagged_courses[:3]:
    print(f"   - {course['title']}: {course['tags']}")

# 4. Retrieve assignments with due dates in the next week
print("\n4. Retrieving assignments due in the next week...")
next_week = datetime.now() + timedelta(days=7)
upcoming_assignments = list(db.assignments.find({
    "dueDate": {
        "$gte": datetime.now(),
        "$lte": next_week
    }
}))
print(f" Found {len(upcoming_assignments)} assignments due in the next week")
for assignment in upcoming_assignments:
    print(f"   - {assignment['title']} due on {assignment['dueDate'].strftime('%Y-%m-%d')}")
	
	
	
#TASK 4.2: AGGREGATION PIPELINE

print("\n--- Aggregation Pipeline ---")

# 1. Course Enrollment Statistics
print("1. Course Enrollment Statistics...")

enrollment_stats = list(db.enrollments.aggregate([
    # Group by course to count enrollments
    {
        "$group": {
            "_id": "$courseId",
            "totalEnrollments": {"$sum": 1},
            "activeEnrollments": {
                "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
            },
            "completedEnrollments": {
                "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
            },
            "averageProgress": {"$avg": "$progress"}
        }
    },
    # Join with courses to get course details
    {
        "$lookup": {
            "from": "courses",
            "localField": "_id",
            "foreignField": "courseId",
            "as": "course"
        }
    },
    {"$unwind": "$course"},
    # Project final results
    {
        "$project": {
            "courseTitle": "$course.title",
            "category": "$course.category",
            "totalEnrollments": 1,
            "activeEnrollments": 1,
            "completedEnrollments": 1,
            "averageProgress": {"$round": ["$averageProgress", 2]}
        }
    },
    {"$sort": {"totalEnrollments": -1}}
]))

print(f" Generated enrollment statistics for {len(enrollment_stats)} courses")
for stat in enrollment_stats[:3]:
    print(f"   - {stat['courseTitle']}: {stat['totalEnrollments']} enrollments, {stat['averageProgress']}% avg progress")

# 2. Student Performance Analysis
print("\n2. Student Performance Analysis...")

student_performance = list(db.submissions.aggregate([
    # Group by student to calculate performance metrics
    {
        "$group": {
            "_id": "$studentId",
            "totalSubmissions": {"$sum": 1},
            "averageGrade": {"$avg": "$grade"},
            "gradedSubmissions": {
                "$sum": {"$cond": [{"$ne": ["$grade", None]}, 1, 0]}
            }
        }
    },
    # Join with users to get student details
    {
        "$lookup": {
            "from": "users",
            "localField": "_id",
            "foreignField": "userId",
            "as": "student"
        }
    },
    {"$unwind": "$student"},
    # Filter only students
    {"$match": {"student.role": "student"}},
    # Project final results
    {
        "$project": {
            "studentName": {"$concat": ["$student.firstName", " ", "$student.lastName"]},
            "totalSubmissions": 1,
            "gradedSubmissions": 1,
            "averageGrade": {"$round": ["$averageGrade", 2]},
            "completionRate": {
                "$round": [
                    {"$multiply": [
                        {"$divide": ["$gradedSubmissions", "$totalSubmissions"]},
                        100
                    ]}, 2
                ]
            }
        }
    },
    {"$sort": {"averageGrade": -1}}
]))

print(f" Generated performance analysis for {len(student_performance)} students")
for perf in student_performance[:3]:
    print(f"   - {perf['studentName']}: Avg Grade {perf['averageGrade']}, {perf['completionRate']}% completion")

# Calculate completion rate by course
completion_by_course = list(db.enrollments.aggregate([
    {
        "$group": {
            "_id": "$courseId",
            "totalEnrollments": {"$sum": 1},
            "completedEnrollments": {
                "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
            }
        }
    },
    {
        "$lookup": {
            "from": "courses",
            "localField": "_id",
            "foreignField": "courseId",
            "as": "course"
        }
    },
    {"$unwind": "$course"},
    {
        "$project": {
            "courseTitle": "$course.title",
            "completionRate": {
                "$round": [
                    {"$multiply": [
                        {"$divide": ["$completedEnrollments", "$totalEnrollments"]},
                        100
                    ]}, 2
                ]
            }
        }
    },
    {"$sort": {"completionRate": -1}}
]))

print(f"\n Course completion rates:")
for completion in completion_by_course[:3]:
    print(f"   - {completion['courseTitle']}: {completion['completionRate']}% completion rate")

# Top-performing students
top_students = list(db.submissions.aggregate([
    {"$match": {"grade": {"$ne": None}}},
    {
        "$group": {
            "_id": "$studentId",
            "averageGrade": {"$avg": "$grade"},
            "totalSubmissions": {"$sum": 1}
        }
    },
    {"$match": {"totalSubmissions": {"$gte": 2}}},  # At least 2 submissions
    {
        "$lookup": {
            "from": "users",
            "localField": "_id",
            "foreignField": "userId",
            "as": "student"
        }
    },
    {"$unwind": "$student"},
    {
        "$project": {
            "studentName": {"$concat": ["$student.firstName", " ", "$student.lastName"]},
            "averageGrade": {"$round": ["$averageGrade", 2]}
        }
    },
    {"$sort": {"averageGrade": -1}},
    {"$limit": 3}
]))

print(f"\n Top-performing students:")
for student in top_students:
    print(f"   - {student['studentName']}: {student['averageGrade']} average grade")

# 3. Instructor Analytics
print("\n3. Instructor Analytics...")

instructor_analytics = list(db.courses.aggregate([
    # Group by instructor
    {
        "$group": {
            "_id": "$instructorId",
            "totalCourses": {"$sum": 1},
            "publishedCourses": {
                "$sum": {"$cond": ["$isPublished", 1, 0]}
            },
            "totalRevenue": {"$sum": "$price"},
            "courseIds": {"$push": "$courseId"}
        }
    },
    # Join with users to get instructor details
    {
        "$lookup": {
            "from": "users",
            "localField": "_id",
            "foreignField": "userId",
            "as": "instructor"
        }
    },
    {"$unwind": "$instructor"},
    # Join with enrollments to count total students
    {
        "$lookup": {
            "from": "enrollments",
            "localField": "courseIds",
            "foreignField": "courseId",
            "as": "enrollments"
        }
    },
    # Project final results
    {
        "$project": {
            "instructorName": {"$concat": ["$instructor.firstName", " ", "$instructor.lastName"]},
            "totalCourses": 1,
            "publishedCourses": 1,
            "totalStudents": {"$size": "$enrollments"},
            "potentialRevenue": "$totalRevenue"
        }
    },
    {"$sort": {"totalStudents": -1}}
]))

print(f" Generated analytics for {len(instructor_analytics)} instructors")
for analytics in instructor_analytics[:3]:
    print(f"   - {analytics['instructorName']}: {analytics['totalCourses']} courses, {analytics['totalStudents']} students")

# Calculate average course rating per instructor (simulated data since we don't have ratings)
# In a real scenario, you would have a ratings collection
print("\n Note: Course ratings would require a separate ratings collection in production")

# 4. Advanced Analytics
print("\n4. Advanced Analytics...")

# Monthly enrollment trends
monthly_trends = list(db.enrollments.aggregate([
    {
        "$group": {
            "_id": {
                "year": {"$year": "$enrollmentDate"},
                "month": {"$month": "$enrollmentDate"}
            },
            "enrollmentCount": {"$sum": 1}
        }
    },
    {
        "$project": {
            "period": {"$concat": [
                {"$toString": "$_id.year"}, "-",
                {"$toString": "$_id.month"}
            ]},
            "enrollmentCount": 1
        }
    },
    {"$sort": {"_id.year": 1, "_id.month": 1}}
]))

print(f" Monthly enrollment trends:")
for trend in monthly_trends:
    print(f"   - {trend['period']}: {trend['enrollmentCount']} enrollments")

# Most popular course categories
popular_categories = list(db.courses.aggregate([
    {
        "$group": {
            "_id": "$category",
            "courseCount": {"$sum": 1},
            "averagePrice": {"$avg": "$price"}
        }
    },
    {
        "$lookup": {
            "from": "enrollments",
            "let": {"category": "$_id"},
            "pipeline": [
                {
                    "$lookup": {
                        "from": "courses",
                        "localField": "courseId",
                        "foreignField": "courseId",
                        "as": "course"
                    }
                },
                {"$unwind": "$course"},
                {"$match": {"$expr": {"$eq": ["$course.category", "$category"]}}}
            ],
            "as": "enrollments"
        }
    },
    {
        "$project": {
            "category": "$_id",
            "courseCount": 1,
            "averagePrice": {"$round": ["$averagePrice", 2]},
            "totalEnrollments": {"$size": "$enrollments"}
        }
    },
    {"$sort": {"totalEnrollments": -1}}
]))

print(f"\n Most popular course categories:")
for category in popular_categories[:3]:
    print(f"   - {category['category']}: {category['courseCount']} courses, {category['totalEnrollments']} enrollments")

# Student engagement metrics
engagement_metrics = list(db.enrollments.aggregate([
    {
        "$group": {
            "_id": None,
            "totalEnrollments": {"$sum": 1},
            "activeEnrollments": {
                "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
            },
            "completedEnrollments": {
                "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
            },
            "droppedEnrollments": {
                "$sum": {"$cond": [{"$eq": ["$status", "dropped"]}, 1, 0]}
            },
            "averageProgress": {"$avg": "$progress"}
        }
    },
    {
        "$project": {
            "totalEnrollments": 1,
            "activeRate": {
                "$round": [
                    {"$multiply": [
                        {"$divide": ["$activeEnrollments", "$totalEnrollments"]},
                        100
                    ]}, 2
                ]
            },
            "completionRate": {
                "$round": [
                    {"$multiply": [
                        {"$divide": ["$completedEnrollments", "$totalEnrollments"]},
                        100
                    ]}, 2
                ]
            },
            "dropRate": {
                "$round": [
                    {"$multiply": [
                        {"$divide": ["$droppedEnrollments", "$totalEnrollments"]},
                        100
                    ]}, 2
                ]
            },
            "averageProgress": {"$round": ["$averageProgress", 2]}
        }
    }
]))

if engagement_metrics:
    metrics = engagement_metrics[0]
    print(f"\n Student engagement metrics:")
    print(f"   - Active enrollments: {metrics['activeRate']}%")
    print(f"   - Completion rate: {metrics['completionRate']}%")
    print(f"   - Drop rate: {metrics['dropRate']}%")
    print(f"   - Average progress: {metrics['averageProgress']}%")
	
	
	
#PART 5: INDEXING AND PERFORMANCE

#TASK 5.1: INDEX CREATION

print("\n--- Index Creation ---")

# 1. User email lookup index
print("1. Creating index for user email lookup...")
db.users.create_index([("email", ASCENDING)], unique=True)
print(" Created unique index on users.email")

# 2. Course search by title and category index
print("2. Creating compound index for course search...")
db.courses.create_index([
    ("title", "text"),
    ("category", ASCENDING)
])
print(" Created compound index on courses.title (text) and courses.category")

# 3. Assignment queries by due date index
print("3. Creating index for assignment due date queries...")
db.assignments.create_index([("dueDate", ASCENDING)])
print(" Created index on assignments.dueDate")

# 4. Enrollment queries by student and course index
print("4. Creating compound index for enrollment queries...")
db.enrollments.create_index([
    ("studentId", ASCENDING),
    ("courseId", ASCENDING)
])
print(" Created compound index on enrollments.studentId and enrollments.courseId")

# Additional performance indexes
print("5. Creating additional performance indexes...")
db.courses.create_index([("instructorId", ASCENDING)])
db.lessons.create_index([("courseId", ASCENDING), ("order", ASCENDING)])
db.submissions.create_index([("assignmentId", ASCENDING), ("studentId", ASCENDING)])
print(" Created additional indexes for common queries")

# List all indexes
print("\n Current indexes:")
for collection_name in collections_to_create:
    indexes = db[collection_name].list_indexes()
    print(f"   {collection_name}:")
    for index in indexes:
        print(f"     - {index['name']}: {index.get('key', 'N/A')}")	


#TASK 5.2: QUERY OPTIMISATION

print("\n---Query Optimisation ---")

# Function to measure query performance
def measure_query_performance(collection, query, description):
    """Measure and display query performance"""
    print(f"\n{description}")
    
    # Measure execution time
    start_time = time.time()
    result = list(collection.find(query))
    end_time = time.time()
    
    execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
    
    # Get query execution stats
    explain_result = collection.find(query).explain()
    
    print(f" Execution time: {execution_time:.2f} ms")
    print(f" Documents returned: {len(result)}")
    print(f" Execution stats: {explain_result.get('executionStats', {}).get('stage', 'N/A')}")
    
    return execution_time, len(result)

# 1. Optimize user email lookup
print("1. Analyzing user email lookup performance...")
email_query = {"email": "john.smith@eduhub.com"}
time1, count1 = measure_query_performance(db.users, email_query, "Email lookup with index:")

# 2. Optimize course search queries
print("\n2. Analyzing course search performance...")
course_search_query = {"category": "Programming", "isPublished": True}
time2, count2 = measure_query_performance(db.courses, course_search_query, "Course search with index:")

# 3. Optimize enrollment queries
print("\n3. Analyzing enrollment query performance...")
if student_ids and course_ids:
    enrollment_query = {"studentId": student_ids[0], "status": "active"}
    time3, count3 = measure_query_performance(db.enrollments, enrollment_query, "Enrollment lookup with index:")

# Performance improvement documentation
print("\n Performance Optimization Summary:")
print("   - Email lookups: Unique index ensures O(log n) lookup time")
print("   - Course searches: Compound index optimizes category + publication status queries")
print("   - Enrollment queries: Compound index optimizes student-course relationship queries")
print("   - Assignment due dates: Index enables efficient range queries")

# Test complex aggregation performance
print("\n4. Testing aggregation pipeline performance...")
start_time = time.time()
complex_aggregation = list(db.enrollments.aggregate([
    {"$match": {"status": "active"}},
    {
        "$lookup": {
            "from": "courses",
            "localField": "courseId",
            "foreignField": "courseId",
            "as": "course"
        }
    },
    {"$unwind": "$course"},
    {
        "$group": {
            "_id": "$course.category",
            "activeEnrollments": {"$sum": 1}
        }
    }
]))
end_time = time.time()

aggregation_time = (end_time - start_time) * 1000
print(f" Complex aggregation execution time: {aggregation_time:.2f} ms")
print(f" Aggregation results: {len(complex_aggregation)} categories")


#PART 6: DATA VALIDATION AND ERROR HANDLING

#TASK 6.1: SCHEMA VALIDATION

# Create validation rules for users collection
print("1. Setting up schema validation for users collection...")
try:
    db.create_collection("users_validated", validator={
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["userId", "email", "firstName", "lastName", "role"],
            "properties": {
                "userId": {
                    "bsonType": "string",
                    "description": "User ID must be a string and is required"
                },
                "email": {
                    "bsonType": "string",
                    "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    "description": "Email must be a valid email format and is required"
                },
                "firstName": {
                    "bsonType": "string",
                    "description": "First name must be a string and is required"
                },
                "lastName": {
                    "bsonType": "string",
                    "description": "Last name must be a string and is required"
                },
                "role": {
                    "enum": ["student", "instructor"],
                    "description": "Role must be either student or instructor"
                },
                "isActive": {
                    "bsonType": "bool",
                    "description": "isActive must be a boolean"
                }
            }
        }
    })
   
except Exception as e:
    print(f" Users validation schema already exists or error: {str(e)}")

# Create validation rules for courses collection
print("2. Setting up schema validation for courses collection...")
try:
    db.create_collection("courses_validated", validator={
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["courseId", "title", "instructorId"],
            "properties": {
                "courseId": {
                    "bsonType": "string",
                    "description": "Course ID must be a string and is required"
                },
                "title": {
                    "bsonType": "string",
                    "minLength": 5,
                    "description": "Title must be a string with minimum 5 characters"
                },
                "instructorId": {
                    "bsonType": "string",
                    "description": "Instructor ID must be a string and is required"
                },
                "level": {
                    "enum": ["beginner", "intermediate", "advanced"],
                    "description": "Level must be beginner, intermediate, or advanced"
                },
                "price": {
                    "bsonType": "number",
                    "minimum": 0,
                    "description": "Price must be a non-negative number"
                },
                "isPublished": {
                    "bsonType": "bool",
                    "description": "isPublished must be a boolean"
                }
            }
        }
    })
    
except Exception as e:
    print(f" Courses validation schema already exists or error: {str(e)}")
	
	
	
#TASK 6.2: ERROR HANDLING

print("\n--- Task 6.2: Error Handling ---")

# 1. Handle duplicate key errors
print("1. Testing duplicate key error handling...")
try:
    # Try to insert a user with duplicate email
    duplicate_user = {
        "userId": generate_user_id(),
        "email": "john.smith@eduhub.com",  # This should already exist
        "firstName": "John",
        "lastName": "Smith",
        "role": "student",
        "dateJoined": datetime.now(),
        "isActive": True
    }
    db.users.insert_one(duplicate_user)
    print(" User inserted successfully")
except Exception as e:
    print(f" Handled duplicate key error: {type(e)._name_}")

# 2. Handle invalid data type insertions
print("2. Testing invalid data type error handling...")
try:
    # Try to insert invalid data types
    invalid_course = {
        "courseId": 12345,  # Should be string
        "title": ["Invalid", "Title"],  # Should be string
        "instructorId": "INSTRUCTOR_001",
        "price": "invalid_price",  # Should be number
        "isPublished": "yes"  # Should be boolean
    }
    db.courses_validated.insert_one(invalid_course)
    print(" Course inserted successfully")
except Exception as e:
    print(f" Handled invalid data type error: {type(e)._name_}")

# 3. Handle missing required fields
print("3. Testing missing required fields error handling...")
try:
    # Try to insert document with missing required fields
    incomplete_user = {
        "userId": generate_user_id(),
        # Missing email, firstName, lastName, role
        "dateJoined": datetime.now(),
        "isActive": True
    }
    db.users_validated.insert_one(incomplete_user)
    print(" User inserted successfully")
except Exception as e:
    print(f" Handled missing required fields error: {type(e)._name_}")

# Additional error handling examples
print("4. Additional error handling scenarios...")

# Handle connection errors
def safe_database_operation(operation_func, *args, **kwargs):
    """Safely execute database operations with error handling"""
    try:
        return operation_func(*args, **kwargs)
    except Exception as e:
        print(f" Database operation error handled: {type(e)._name_} - {str(e)}")
        return None

# Test safe operations
result = safe_database_operation(db.users.find_one, {"email": "nonexistent@example.com"})
if result is None:
    print(" Safe operation returned None for non-existent document")

# Handle aggregation errors
try:
    # Try aggregation with invalid pipeline
    invalid_pipeline = [
        {"$invalid_stage": {"field": "value"}}
    ]
    result = list(db.users.aggregate(invalid_pipeline))
except Exception as e:
    print(f" Handled aggregation pipeline error: {type(e)._name_}")