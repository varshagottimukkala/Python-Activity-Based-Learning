print("STUDENT TIMETABLE CONFLICT DETECTION")
days = ("MON", "TUE", "WED", "THU", "FRI")
rooms = ("R101", "R102", "LAB2")
unavailable = [("LAB2", "WED", 600, 720), ("R102", "FRI", 780, 840)]
print("Rooms: R101, R102, LAB2. Days: MON-FRI.")
print("Unavailable: LAB2 WED 10:00-12:00; R102 FRI 13:00-14:00.")
print("Format: course|day|HH:MM|HH:MM|room")

count_text = input("Number of session records (1-20): ").strip()
while not count_text.isascii() or not count_text.isdigit() or not 1 <= int(count_text) <= 20:
    print("ERROR: enter an integer from 1 to 20.")
    count_text = input("Number of session records (1-20): ").strip()
session_count = int(count_text)
sessions = []
rejected = 0

for record_number in range(1, session_count + 1):
    fields = input(f"Session {record_number}: ").split("|")
    reason = ""
    if len(fields) != 5:
        reason = "expected five fields"
    else:
        course, day, start_text, end_text, room = fields
        course = course.strip().upper()
        day = day.strip().upper()
        room = room.strip().upper()
        times = []
        if not 1 <= len(course) <= 12 or not course.isascii() or not course.isalnum():
            reason = "course must contain 1-12 ASCII letters or digits"
        elif day not in days or room not in rooms:
            reason = "unknown day or room"
        else:
            for time_text in (start_text.strip(), end_text.strip()):
                valid_time = len(time_text) == 5 and time_text[2] == ":"
                if valid_time:
                    hour_text = time_text[:2]
                    minute_text = time_text[3:]
                    valid_time = hour_text.isascii() and hour_text.isdigit() and minute_text.isascii() and minute_text.isdigit()
                    if valid_time:
                        hour = int(hour_text)
                        minute = int(minute_text)
                        valid_time = 0 <= hour <= 23 and 0 <= minute <= 59
                if valid_time:
                    times.append(hour * 60 + minute)
                else:
                    reason = "times must use valid 24-hour HH:MM format"
            if reason == "":
                start, end = times
                session = (course, day, start, end, room)
                if start >= end:
                    reason = "end time must be later than start time on the same day"
                elif session in sessions:
                    reason = "duplicate session"
                else:
                    sessions.append(session)
    if reason != "":
        rejected += 1
        print(f"REJECTED row {record_number}: {reason}")

print("\nTIMETABLE AUDIT")
blocked_bookings = 0
student_conflicts = 0
room_conflicts = 0
for course, day, start, end, room in sessions:
    for blocked_room, blocked_day, blocked_start, blocked_end in unavailable:
        if room == blocked_room and day == blocked_day and start < blocked_end and end > blocked_start:
            blocked_bookings += 1
            print(f"UNAVAILABLE: {course} in {room} on {day}")

for first_index in range(len(sessions)):
    first_course, first_day, first_start, first_end, first_room = sessions[first_index]
    for second_index in range(first_index + 1, len(sessions)):
        second_course, second_day, second_start, second_end, second_room = sessions[second_index]
        if first_day == second_day and first_start < second_end and second_start < first_end:
            student_conflicts += 1
            detail = "student"
            if first_room == second_room:
                room_conflicts += 1
                detail += f"; room {first_room}"
            print(f"CONFLICT: {first_course} / {second_course} ({first_day}): {detail}")

print(f"Parsed sessions: {len(sessions)} | Rejected records: {rejected}")
print(f"Student conflict pairs: {student_conflicts}")
print(f"Room conflict pairs: {room_conflicts}")
print(f"Unavailable-room bookings: {blocked_bookings}")
if rejected == 0 and student_conflicts == 0 and blocked_bookings == 0:
    print("Timetable: VALID")
else:
    print("Timetable: INVALID")
