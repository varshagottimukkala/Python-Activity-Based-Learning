print("STUDENT MARKS MATRIX ANALYSIS")
student_count_text = input("Number of students (1-20): ").strip()
while not student_count_text.isascii() or not student_count_text.isdigit() or not 1 <= int(student_count_text) <= 20:
    print("ERROR: enter an integer from 1 to 20.")
    student_count_text = input("Number of students (1-20): ").strip()
student_count = int(student_count_text)

subject_count_text = input("Number of subjects (1-10): ").strip()
while not subject_count_text.isascii() or not subject_count_text.isdigit() or not 1 <= int(subject_count_text) <= 10:
    print("ERROR: enter an integer from 1 to 10.")
    subject_count_text = input("Number of subjects (1-10): ").strip()
subject_count = int(subject_count_text)

subjects = []
while len(subjects) != subject_count:
    fields = input(f"Enter {subject_count} unique subject codes separated by |: ").split("|")
    subjects = []
    valid_subjects = len(fields) == subject_count
    for field in fields:
        subject = field.strip().upper()
        if not 1 <= len(subject) <= 12 or not subject.isascii() or not subject.isalnum() or subject in subjects:
            valid_subjects = False
        subjects.append(subject)
    if not valid_subjects:
        print("ERROR: use the correct number of unique ASCII alphanumeric subject codes.")
        subjects = []

student_ids = []
marks_matrix = []
print("Format: ID|mark1|mark2|...; marks must be integers from 0 to 100.")
while len(student_ids) < student_count:
    fields = input(f"Student {len(student_ids) + 1}: ").split("|")
    if len(fields) != subject_count + 1:
        print("ERROR: provide one ID and exactly one mark per subject.")
        continue
    student_id = fields[0].strip().upper()
    if not 1 <= len(student_id) <= 12 or not student_id.isascii() or not student_id.isalnum() or student_id in student_ids:
        print("ERROR: student IDs must be unique ASCII alphanumeric strings of 1-12 characters.")
        continue
    marks = []
    valid_marks = True
    for field in fields[1:]:
        mark_text = field.strip()
        if not mark_text.isascii() or not mark_text.isdigit() or not 0 <= int(mark_text) <= 100:
            valid_marks = False
        else:
            marks.append(int(mark_text))
    if not valid_marks:
        print("ERROR: each mark must be a whole number from 0 to 100.")
        continue
    student_ids.append(student_id)
    marks_matrix.append(marks)

print("\nSTUDENT STATISTICS")
print("ID | Total | Average | Failed subjects | Classification")
highest_total = -1
top_students = []
grand_total = 0
for student_index in range(student_count):
    total = 0
    failed_subjects = []
    for subject_index in range(subject_count):
        mark = marks_matrix[student_index][subject_index]
        total += mark
        if mark < 40:
            failed_subjects.append(subjects[subject_index])
    average = total / subject_count
    if len(failed_subjects) > 0:
        classification = "FAIL"
    elif average >= 75:
        classification = "DISTINCTION"
    elif average >= 60:
        classification = "FIRST CLASS"
    else:
        classification = "PASS"
    failed_text = "none"
    if len(failed_subjects) > 0:
        failed_text = ", ".join(failed_subjects)
    print(f"{student_ids[student_index]} | {total} | {average:.2f} | {failed_text} | {classification}")
    grand_total += total
    if total > highest_total:
        highest_total = total
        top_students = [student_ids[student_index]]
    elif total == highest_total:
        top_students.append(student_ids[student_index])

print("\nSUBJECT STATISTICS")
print("Subject | Total | Average | Lowest | Highest | Top students")
weak_subjects = []
for subject_index in range(subject_count):
    total = 0
    lowest = 101
    highest = -1
    subject_toppers = []
    for student_index in range(student_count):
        mark = marks_matrix[student_index][subject_index]
        total += mark
        if mark < lowest:
            lowest = mark
        if mark > highest:
            highest = mark
            subject_toppers = [student_ids[student_index]]
        elif mark == highest:
            subject_toppers.append(student_ids[student_index])
    average = total / student_count
    if average < 50:
        weak_subjects.append(subjects[subject_index])
    print(f"{subjects[subject_index]} | {total} | {average:.2f} | {lowest} | {highest} | {', '.join(subject_toppers)}")

print(f"Top overall total: {highest_total}/{subject_count * 100} ({', '.join(top_students)})")
print(f"Overall average: {grand_total / (student_count * subject_count):.2f}")
if len(weak_subjects) == 0:
    print("Subjects averaging below 50: none")
else:
    print(f"Subjects averaging below 50: {', '.join(weak_subjects)}")
