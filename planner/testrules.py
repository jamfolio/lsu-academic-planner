from planner.rules import check_plan, check_hours, semester_hours, courses, parse_credits, slots_accept, GENED_SETS, build_requirements, audit, can_take, check_total_hours, describe, used_courses, minor_rows, LAB_COURSES
from planner.recommend import recommended_plan, entry_hours
import json

with open("data/degrees.json", "r", encoding="utf-8") as f:
    degrees = json.load(f)

with open("data/minorsfinal.json", "r", encoding="utf-8") as f:
    minors = json.load(f)

track = degrees["14280"]["tracks"][3]
plan = recommended_plan(track)

for i, semester in enumerate(plan):
    hours = 0

    for e in semester:
        hours += entry_hours(e)

    print(i+1, hours, track["semesters"][i]["hours"])

    if str(int(hours)) != track["semesters"][i]["hours"]:
        for e in semester:
            print(e.get("code"), e.get("description"), e.get("credits"), entry_hours(e))