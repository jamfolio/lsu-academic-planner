from rules import check_plan, check_hours, semester_hours, courses, parse_credits, slots_accept, GENED_SETS, build_requirements, audit
import json

with open("data/degrees.json", "r", encoding="utf-8") as f:
    degrees = json.load(f)

track = degrees["14278"]["tracks"][4]

plan = [
    ["CSC 1350", "ENGL 1001", "MATH 1550", "BIOL 1201"],
    ["CSC 1351", "MATH 1552", "BIOL 1202", "BIOL 1208", "ENGL 2025"],
    ["CSC 2259", "CSC 3102", "MATH 2090", "CSC 4243", "HIST 2055", "CSC 3200"],
]

report = audit(plan, set(), track, GENED_SETS)

for r in report["results"]:
    req = r["requirement"]

    if req["type"] == "course":
        label = req["options"]
        if r["filled_by"] is not None:
            mark = "✓"
        else:
            mark = "✗"  
    else:
        label = req["slot"]["description"]
        if r["hours"] >= r["needed"]:
            mark = "✓"
        elif r["filled_by"]:
            mark = "◐"
        else:
            mark = "✗"  

    print(mark, label, "<-", r["filled_by"])

print("Unused:", report["unused"])
print("BIOL 1208" in GENED_SETS["Natural Sciences"])

# seg_slot = {"description": "Approved SEG Area Electives (3)", "footnote": "2"}
# csc_slot = {"description": "CSC (2000-level or above) Elective (3)", "footnote": None}
# hum_slot = {"description": "General Education course - Humanities (3)", "footnote": None}

# print(slots_accept("CSC 4243", seg_slot, track, GENED_SETS))  
# print(slots_accept("MATH 1550", seg_slot, track, GENED_SETS)) 
# print(slots_accept("CSC 3102", csc_slot, track, GENED_SETS))   
# print(slots_accept("CSC 1350", csc_slot, track, GENED_SETS))   
# print(slots_accept("ENGL 2000", hum_slot, track, GENED_SETS))  
# print("ENGL 2000" in GENED_SETS["Humanities"])  

# reqs = build_requirements(track)          
# print(len(reqs))  

# for req in reqs:
#     if req["type"] == "course":
#         print(req["options"])
#     else:
#         print(req["slot"]["description"])

# for poid, program in degrees.items():
#     if "Computer Science" in program["title"]:
#         my_degree = program
#         break

# first_track = my_degree["tracks"][0]

# for semester in first_track["semesters"]:
#     print(semester["name"])
#     print(semester["hours"])

#     for item in semester["items"]:
#         print("  ", item)

#     print(semester["critical"])

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
