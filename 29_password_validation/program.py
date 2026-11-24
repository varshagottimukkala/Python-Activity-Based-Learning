print("PASSWORD POLICY VALIDATION ENGINE")
print("Enter fictional samples only: username|password")
print("Passwords are not echoed in the audit.")
count_text = input("Number of samples (1-20): ").strip()
while not count_text.isascii() or not count_text.isdigit() or not 1 <= int(count_text) <= 20:
    print("ERROR: enter an integer from 1 to 20.")
    count_text = input("Number of samples (1-20): ").strip()
sample_count = int(count_text)

special_characters = "!@#$%^&*?_-"
prohibited = ("password", "admin", "qwerty", "1234")
accepted = 0
rejected = 0
results = []

for sample_number in range(1, sample_count + 1):
    fields = input(f"Sample {sample_number}: ").split("|")
    failures = []
    username = "(malformed)"
    if len(fields) != 2:
        failures.append("Expected username|password with exactly one separator.")
    else:
        username = fields[0].strip()
        password = fields[1]
        username_valid = 3 <= len(username) <= 20 and username.isascii() and username.isalnum()
        if not username_valid:
            failures.append("Username must contain 3-20 ASCII letters or digits.")
        if not 10 <= len(password) <= 64:
            failures.append("Password length must be 10-64 characters.")
        has_upper = False
        has_lower = False
        has_digit = False
        has_special = False
        invalid_characters = False
        repeated_run = False
        previous_character = ""
        run_length = 0
        for character in password:
            if "A" <= character <= "Z":
                has_upper = True
            elif "a" <= character <= "z":
                has_lower = True
            elif "0" <= character <= "9":
                has_digit = True
            elif character in special_characters:
                has_special = True
            else:
                invalid_characters = True
            if character == previous_character:
                run_length += 1
            else:
                run_length = 1
            if run_length >= 3:
                repeated_run = True
            previous_character = character
        if not has_upper:
            failures.append("Include an uppercase ASCII letter.")
        if not has_lower:
            failures.append("Include a lowercase ASCII letter.")
        if not has_digit:
            failures.append("Include an ASCII digit.")
        if not has_special:
            failures.append("Include a special character from !@#$%^&*?_-")
        if invalid_characters:
            failures.append("Only ASCII letters, digits, and the listed special characters are allowed.")
        if repeated_run:
            failures.append("Three or more consecutive identical characters are prohibited.")
        lowered_password = password.lower()
        for forbidden_text in prohibited:
            if forbidden_text in lowered_password:
                failures.append(f"Prohibited substring: {forbidden_text}")
        if username_valid and username.lower() in lowered_password:
            failures.append("Password must not contain the username (case-insensitive).")
    if len(failures) == 0:
        accepted += 1
    else:
        rejected += 1
    results.append((sample_number, username, failures))

print("\nPOLICY AUDIT")
for sample_number, username, failures in results:
    if len(failures) == 0:
        print(f"Sample {sample_number} ({username}): ACCEPTED")
    else:
        print(f"Sample {sample_number} ({username}): REJECTED")
        for failure in failures:
            print(f"  - {failure}")
print(f"Accepted: {accepted} | Rejected: {rejected}")
