from rules import check_plan, check_hours, semester_hours, courses, parse_credits, slots_accept, GENED_SETS, build_requirements, audit, can_take, check_total_hours, describe, used_courses, minor_rows
import json

with open("data/degrees.json", "r", encoding="utf-8") as f:
    degrees = json.load(f)

with open("data/minorsfinal.json", "r", encoding="utf-8") as f:
    minors = json.load(f)

print(minor_rows(minors["14203"]["rule"], {"PHIL 2020", "PHIL 3001", "MATH 1550"}))
