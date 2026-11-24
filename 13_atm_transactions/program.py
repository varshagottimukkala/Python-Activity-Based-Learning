print("ATM TRANSACTION SEQUENCE SIMULATION")
print("Use fictional transaction data. Amounts are whole rupees.")

opening_text = input("Opening balance (at least Rs 500): ").strip()
while not opening_text.isascii() or not opening_text.isdigit() or int(opening_text) < 500:
    print("ERROR: opening balance must be a whole number of at least 500.")
    opening_text = input("Opening balance (at least Rs 500): ").strip()
balance = int(opening_text)
opening_balance = balance

count_text = input("Number of transaction attempts (1-50): ").strip()
while not count_text.isascii() or not count_text.isdigit() or not 1 <= int(count_text) <= 50:
    print("ERROR: enter an integer from 1 to 50.")
    count_text = input("Number of transaction attempts (1-50): ").strip()
transaction_count = int(count_text)

seen_ids = []
results = []
deposited = 0
withdrawn = 0
accepted = 0
rejected = 0
print("Transaction format: ID|D/W|amount")

for attempt in range(1, transaction_count + 1):
    fields = input(f"Transaction {attempt}: ").split("|")
    transaction_id = f"row-{attempt}"
    reason = ""
    transaction_type = ""
    amount = 0
    if len(fields) != 3:
        reason = "expected ID|D/W|amount"
    else:
        transaction_id, transaction_type, amount_text = fields
        transaction_id = transaction_id.strip().upper()
        transaction_type = transaction_type.strip().upper()
        amount_text = amount_text.strip()
        if not 1 <= len(transaction_id) <= 12 or not transaction_id.isascii() or not transaction_id.isalnum():
            reason = "ID must contain 1-12 ASCII letters or digits"
        elif transaction_id in seen_ids:
            reason = "duplicate transaction ID"
        else:
            seen_ids.append(transaction_id)
            if transaction_type not in ("D", "W"):
                reason = "transaction type must be D or W"
            elif not amount_text.isascii() or not amount_text.isdigit() or int(amount_text) == 0:
                reason = "amount must be a positive whole number"
            else:
                amount = int(amount_text)
                if transaction_type == "W":
                    if amount % 100 != 0:
                        reason = "withdrawal must be a multiple of Rs 100"
                    elif amount > 10000:
                        reason = "per-transaction withdrawal limit is Rs 10000"
                    elif withdrawn + amount > 20000:
                        reason = "daily withdrawal limit is Rs 20000"
                    elif balance - amount < 500:
                        reason = "withdrawal would breach the Rs 500 minimum balance"
    if reason == "":
        if transaction_type == "D":
            balance += amount
            deposited += amount
        else:
            balance -= amount
            withdrawn += amount
        accepted += 1
        results.append((transaction_id, f"ACCEPTED {transaction_type} Rs {amount}", balance))
    else:
        rejected += 1
        results.append((transaction_id, f"REJECTED: {reason}", balance))

print("\nTRANSACTION AUDIT")
for transaction_id, status, ending_balance in results:
    print(f"{transaction_id}: {status} | Balance Rs {ending_balance}")
print(f"Accepted: {accepted} | Rejected: {rejected}")
print(f"Deposits: Rs {deposited} | Withdrawals: Rs {withdrawn}")
print(f"Final balance: Rs {balance}")
print(f"Reconciliation: {opening_balance} + {deposited} - {withdrawn} = {balance}")
