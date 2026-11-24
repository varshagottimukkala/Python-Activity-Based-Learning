print("MULTI-DAY WATER TANK SIMULATION")
capacity_text = input("Capacity in litres (positive integer): ").strip()
while not capacity_text.isascii() or not capacity_text.isdigit() or int(capacity_text) == 0:
    print("ERROR: capacity must be a positive whole number.")
    capacity_text = input("Capacity in litres (positive integer): ").strip()
capacity = int(capacity_text)

initial_text = input(f"Initial level (0-{capacity}): ").strip()
while not initial_text.isascii() or not initial_text.isdigit() or not 0 <= int(initial_text) <= capacity:
    print("ERROR: initial level must be within tank capacity.")
    initial_text = input(f"Initial level (0-{capacity}): ").strip()
initial = int(initial_text)
level = initial

threshold_text = input(f"Threshold (0-{capacity}): ").strip()
while not threshold_text.isascii() or not threshold_text.isdigit() or not 0 <= int(threshold_text) <= capacity:
    print("ERROR: threshold must be within tank capacity.")
    threshold_text = input(f"Threshold (0-{capacity}): ").strip()
threshold = int(threshold_text)

count_text = input("Number of intervals (1-30): ").strip()
while not count_text.isascii() or not count_text.isdigit() or not 1 <= int(count_text) <= 30:
    print("ERROR: enter an integer from 1 to 30.")
    count_text = input("Number of intervals (1-30): ").strip()
interval_count = int(count_text)

records = []
total_inflow = 0
total_served = 0
total_spill = 0
total_shortage = 0
first_threshold_interval = -1
if level >= threshold:
    first_threshold_interval = 0
print("Each interval fills first, spills excess, then supplies demand.")
print("Format: inflow|demand")

while len(records) < interval_count:
    fields = input(f"Interval {len(records) + 1}: ").split("|")
    valid = len(fields) == 2
    if valid:
        for field in fields:
            number_text = field.strip()
            if not number_text.isascii() or not number_text.isdigit():
                valid = False
    if not valid:
        print("ERROR: enter two nonnegative whole numbers: inflow|demand.")
        continue
    inflow = int(fields[0].strip())
    demand = int(fields[1].strip())
    starting_level = level
    level += inflow
    spill = 0
    if level > capacity:
        spill = level - capacity
        level = capacity
    if first_threshold_interval == -1 and level >= threshold:
        first_threshold_interval = len(records) + 1
    served = demand
    shortage = 0
    if demand > level:
        served = level
        shortage = demand - level
    level -= served
    total_inflow += inflow
    total_served += served
    total_spill += spill
    total_shortage += shortage
    records.append((starting_level, inflow, demand, served, spill, shortage, level))

print("\nINTERVAL AUDIT (litres)")
print("Interval | Start | Inflow | Demand | Served | Spill | Shortage | End")
for record_index in range(len(records)):
    starting_level, inflow, demand, served, spill, shortage, ending_level = records[record_index]
    print(f"{record_index + 1} | {starting_level} | {inflow} | {demand} | {served} | {spill} | {shortage} | {ending_level}")
print(f"Final level: {level} litres")
print(f"Inflow: {total_inflow} | Served: {total_served} | Spill: {total_spill} | Shortage: {total_shortage}")
if first_threshold_interval == 0:
    print("Threshold first reached: initially (interval 0)")
elif first_threshold_interval == -1:
    print("Threshold first reached: never")
else:
    print(f"Threshold first reached: interval {first_threshold_interval}, after inflow")
print(f"Water balance: {initial} + {total_inflow} = {level} + {total_served} + {total_spill}")
