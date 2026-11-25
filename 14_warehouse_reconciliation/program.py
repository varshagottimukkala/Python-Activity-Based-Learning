print("WAREHOUSE INVENTORY RECONCILIATION")
count_text = input("Number of product records (1-20): ").strip()
while not count_text.isascii() or not count_text.isdigit() or not 1 <= int(count_text) <= 20:
    print("ERROR: enter an integer from 1 to 20.")
    count_text = input("Number of product records (1-20): ").strip()
record_count = int(count_text)
print("Format: code|opening|incoming|dispatched|observed_closing|target")

products = []
seen_codes = []
invalid_records = 0
for record_number in range(1, record_count + 1):
    fields = input(f"Product {record_number}: ").split("|")
    reason = ""
    code = f"row-{record_number}"
    numbers = []
    if len(fields) != 6:
        reason = "expected six fields"
    else:
        code = fields[0].strip().upper()
        if not 1 <= len(code) <= 12 or not code.isascii() or not code.isalnum():
            reason = "code must contain 1-12 ASCII letters or digits"
        elif code in seen_codes:
            reason = "duplicate product code"
        else:
            for field in fields[1:]:
                number_text = field.strip()
                if not number_text.isascii() or not number_text.isdigit():
                    reason = "quantities must be nonnegative whole numbers"
                else:
                    numbers.append(int(number_text))
            if reason == "":
                opening, incoming, dispatched, observed, target = numbers
                if dispatched > opening + incoming:
                    reason = "dispatch exceeds available stock"
                else:
                    seen_codes.append(code)
                    products.append((code, opening, incoming, dispatched, observed, target))
    if reason != "":
        invalid_records += 1
        print(f"REJECTED {code}: {reason}")

print("\nSTOCK AUDIT")
print("Code | Expected | Observed | Difference | Status | Replenish")
discrepancies = 0
total_replenishment = 0
for code, opening, incoming, dispatched, observed, target in products:
    expected = opening + incoming - dispatched
    difference = observed - expected
    if difference < 0:
        status = "SHORTAGE"
        discrepancies += 1
    elif difference > 0:
        status = "SURPLUS"
        discrepancies += 1
    else:
        status = "MATCH"
    replenish = 0
    if observed < target:
        replenish = target - observed
    total_replenishment += replenish
    print(f"{code} | {expected} | {observed} | {difference:+d} | {status} | {replenish}")
print(f"Audited: {len(products)} | Rejected: {invalid_records}")
print(f"Products with discrepancies: {discrepancies}")
print(f"Total replenishment: {total_replenishment} units")
