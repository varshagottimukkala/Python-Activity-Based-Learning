print("HOLLOW NUMERIC DIAMOND")
size_text = input("Number of levels (1-9): ").strip()
while not size_text.isascii() or not size_text.isdigit() or not 1 <= int(size_text) <= 9:
    print("ERROR: enter an integer from 1 to 9.")
    size_text = input("Number of levels (1-9): ").strip()
size = int(size_text)
dimension = 2 * size - 1
digit_count = 0
print("\nPATTERN")

for row_number in range(1, dimension + 1):
    level = row_number
    if row_number > size:
        level = 2 * size - row_number
    left_edge = size - level + 1
    right_edge = size + level - 1
    line = ""
    for column_number in range(1, dimension + 1):
        if column_number == left_edge or column_number == right_edge:
            line += str(level)
            digit_count += 1
        else:
            line += " "
    print(line.rstrip())

print(f"Height: {dimension} | Maximum width: {dimension}")
print(f"Digits printed: {digit_count}")
