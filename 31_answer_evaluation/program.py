print("STRING-BASED EXAMINATION ANSWER EVALUATION")
key_valid = False
while not key_valid:
    answer_key = input("Answer key (1-50 letters A-D): ").strip().upper()
    key_valid = 1 <= len(answer_key) <= 50
    for answer in answer_key:
        if answer not in "ABCD":
            key_valid = False
    if not key_valid:
        print("ERROR: the answer key must contain 1-50 letters A-D.")

count_text = input("Number of student records (1-30): ").strip()
while not count_text.isascii() or not count_text.isdigit() or not 1 <= int(count_text) <= 30:
    print("ERROR: enter an integer from 1 to 30.")
    count_text = input("Number of student records (1-30): ").strip()
student_count = int(count_text)
print(f"Format: ID|{len(answer_key)} responses. Use - for unanswered.")
seen_ids = []
results = []
rejected = 0

for record_number in range(1, student_count + 1):
    fields = input(f"Student {record_number}: ").split("|")
    reason = ""
    student_id = f"row-{record_number}"
    if len(fields) != 2:
        reason = "expected ID|responses"
    else:
        student_id = fields[0].strip().upper()
        responses = fields[1].strip().upper()
        if not 1 <= len(student_id) <= 12 or not student_id.isascii() or not student_id.isalnum():
            reason = "ID must contain 1-12 ASCII letters or digits"
        elif student_id in seen_ids:
            reason = "duplicate student ID"
        else:
            if len(responses) != len(answer_key):
                reason = "response length must match the answer key"
            else:
                for answer in responses:
                    if answer not in "ABCD-":
                        reason = "responses must contain only A-D or -"
            if reason == "":
                seen_ids.append(student_id)
                correct = 0
                incorrect = 0
                unanswered = 0
                for answer_index in range(len(answer_key)):
                    if responses[answer_index] == "-":
                        unanswered += 1
                    elif responses[answer_index] == answer_key[answer_index]:
                        correct += 1
                    else:
                        incorrect += 1
                score = correct * 4 - incorrect
                percentage = score * 100 / (len(answer_key) * 4)
                if percentage >= 75:
                    classification = "DISTINCTION"
                elif percentage >= 50:
                    classification = "PASS"
                else:
                    classification = "NEEDS PRACTICE"
                results.append(
                    (student_id, correct, incorrect, unanswered, score, percentage, classification)
                )
    if reason != "":
        rejected += 1
        print(f"REJECTED {student_id}: {reason}")

print("\nEXAMINATION RESULTS")
print("ID | Correct | Incorrect | Blank | Score | Percent | Result")
highest_score = -len(answer_key) - 1
top_students = []
for student_id, correct, incorrect, unanswered, score, percentage, classification in results:
    print(
        f"{student_id} | {correct} | {incorrect} | {unanswered} | "
        f"{score} | {percentage:.2f}% | {classification}"
    )
    if score > highest_score:
        highest_score = score
        top_students = [student_id]
    elif score == highest_score:
        top_students.append(student_id)
print(f"Evaluated: {len(results)} | Rejected: {rejected}")
if len(results) > 0:
    print(f"Top score: {highest_score}/{len(answer_key) * 4} ({', '.join(top_students)})")
else:
    print("Top score: no valid student records")
