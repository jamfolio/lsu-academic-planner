from rules import check_plan, check_hours, semester_hours, courses, parse_credits
import json

with open("data/degrees.json", "r", encoding="utf-8") as f:
    degrees = json.load(f)

for poid, program in degrees.items():
    if "Computer Science" in program["title"]:
        my_degree = program
        break

first_track = my_degree["tracks"][0]

for semester in first_track["semesters"]:
    print(semester["name"])
    print(semester["hours"])

    for item in semester["items"]:
        print("  ", item)

    print(semester["critical"])

# plan = [
#     ["MATH 1550", "ENGL 1001"],
#     ["MATH 1552", "PHYS 2110"],
#     ["MATH 2057", "PHYS 2113"],
# ]

# print(semester_hours(plan, courses))
# print(check_hours(plan, courses, 6, 7))

# formats = set()

# for code, course in courses.items():
#     formats.add(course["credits"])

# print(len(formats))

# for value in sorted(formats, key=str):
#     print(f"{value!r} -> {parse_credits(value)}")
