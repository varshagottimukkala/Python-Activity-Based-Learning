print("TUPLE-BASED PRODUCT CATALOGUE AUDIT")
count_text = input("Number of catalogue records (1-30): ").strip()
while not count_text.isascii() or not count_text.isdigit() or not 1 <= int(count_text) <= 30:
    print("ERROR: enter an integer from 1 to 30.")
    count_text = input("Number of catalogue records (1-30): ").strip()
record_count = int(count_text)
print("Format: Pddd|price_in_Rs|stock|reorder_level")
print("Prices must be positive, with at most two decimal places.")

catalogue = []
seen_ids = []
rejected = 0
for record_number in range(1, record_count + 1):
    fields = input(f"Product {record_number}: ").split("|")
    reason = ""
    product_id = f"row-{record_number}"
    if len(fields) != 4:
        reason = "expected four fields"
    else:
        product_id, price_text, stock_text, reorder_text = fields
        product_id = product_id.strip().upper()
        price_text = price_text.strip()
        stock_text = stock_text.strip()
        reorder_text = reorder_text.strip()
        if len(product_id) != 4 or product_id[0] != "P" or not product_id[1:].isascii() or not product_id[1:].isdigit():
            reason = "ID must be P followed by three ASCII digits"
        elif product_id in seen_ids:
            reason = "duplicate product ID"
        else:
            seen_ids.append(product_id)
            price_parts = price_text.split(".")
            price_valid = len(price_parts) in (1, 2)
            if price_valid:
                whole = price_parts[0]
                fraction = "00"
                price_valid = whole.isascii() and whole.isdigit()
                if len(price_parts) == 2:
                    fraction = price_parts[1]
                    price_valid = price_valid and 1 <= len(fraction) <= 2 and fraction.isascii() and fraction.isdigit()
                    fraction = (fraction + "00")[:2]
            if not price_valid:
                reason = "invalid price format"
            else:
                price_paise = int(whole) * 100 + int(fraction)
                if price_paise == 0:
                    reason = "price must be positive"
                elif not stock_text.isascii() or not stock_text.isdigit() or not reorder_text.isascii() or not reorder_text.isdigit():
                    reason = "stock and reorder level must be nonnegative whole numbers"
                else:
                    catalogue.append((product_id, price_paise, int(stock_text), int(reorder_text)))
    if reason != "":
        rejected += 1
        print(f"REJECTED {product_id}: {reason}")

print("\nCATALOGUE AUDIT")
print("ID | Unit price (Rs) | Stock | Value (Rs) | Reorder level | Replenish")
inventory_value = 0
replenishment_units = 0
reorder_items = []
for product_id, price_paise, stock, reorder_level in catalogue:
    value = price_paise * stock
    inventory_value += value
    replenish = 0
    if stock < reorder_level:
        replenish = reorder_level - stock
        reorder_items.append(product_id)
    replenishment_units += replenish
    print(f"{product_id} | {price_paise / 100:.2f} | {stock} | {value / 100:.2f} | {reorder_level} | {replenish}")

print(f"Valid records: {len(catalogue)} | Rejected: {rejected}")
print(f"Inventory value: Rs {inventory_value / 100:.2f}")
print(f"Replenishment needed: {replenishment_units} units")
if len(reorder_items) == 0:
    print("Items below reorder level: none")
else:
    print(f"Items below reorder level: {', '.join(reorder_items)}")
