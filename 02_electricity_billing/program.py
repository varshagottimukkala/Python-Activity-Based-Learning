print("PROGRESSIVE ELECTRICITY BILLING")
print("Enter months in chronological order: label|units|on_time(Y/N)")

month_count_text = input("Number of months (1-12): ").strip()
while not month_count_text.isascii() or not month_count_text.isdigit() or not 1 <= int(month_count_text) <= 12:
    print("ERROR: enter an integer from 1 to 12.")
    month_count_text = input("Number of months (1-12): ").strip()
month_count = int(month_count_text)

months = []
labels = []
while len(months) < month_count:
    fields = input(f"Month {len(months) + 1}: ").split("|")
    if len(fields) != 3:
        print("ERROR: expected label|units|Y/N.")
        continue
    label, units_text, on_time = fields
    label = label.strip()
    units_text = units_text.strip()
    on_time = on_time.strip().upper()
    if not 1 <= len(label) <= 12 or label.lower() in labels:
        print("ERROR: month labels must be nonempty, unique, and at most 12 characters.")
        continue
    if not units_text.isascii() or not units_text.isdigit():
        print("ERROR: units must be a nonnegative whole number.")
        continue
    if on_time not in ("Y", "N"):
        print("ERROR: on-time payment must be Y or N.")
        continue
    months.append((label, int(units_text), on_time))
    labels.append(label.lower())

print("\nBILL DETAILS (Rs)")
print("Month | Units | Energy | Fixed | Surcharge | Rebate | Total")
previous_bill = 0
highest_bill = -1
highest_months = []
unusual_months = []
grand_total = 0

for label, units, on_time in months:
    if units <= 100:
        energy = units * 150
    elif units <= 200:
        energy = 100 * 150 + (units - 100) * 250
    else:
        energy = 100 * 150 + 100 * 250 + (units - 200) * 400
    fixed = 5000
    surcharge = 0
    rebate = 0
    if units > 300:
        surcharge = (energy * 10 + 50) // 100
    if units <= 100 and on_time == "Y":
        rebate = (energy * 5 + 50) // 100
    bill = energy + fixed + surcharge - rebate
    grand_total += bill
    print(f"{label} | {units} | {energy / 100:.2f} | {fixed / 100:.2f} | {surcharge / 100:.2f} | {rebate / 100:.2f} | {bill / 100:.2f}")
    if previous_bill > 0:
        change = (bill - previous_bill) * 100 / previous_bill
        print(f"  Change from previous month: {change:+.2f}%")
        if bill * 100 > previous_bill * 125:
            unusual_months.append(label)
            print("  ALERT: bill increase exceeds 25%.")
    if bill > highest_bill:
        highest_bill = bill
        highest_months = [label]
    elif bill == highest_bill:
        highest_months.append(label)
    previous_bill = bill

print(f"Total billed: Rs {grand_total / 100:.2f}")
print(f"Highest bill: Rs {highest_bill / 100:.2f} ({', '.join(highest_months)})")
if len(unusual_months) == 0:
    print("Unusual increases: none")
else:
    print(f"Unusual increases: {', '.join(unusual_months)}")
