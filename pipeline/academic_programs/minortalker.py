import ollama
import json
import re
import os
from tqdm import tqdm

instructions = """Convert the requirements for a university minor into JSON rules.

Allowed forms:
- {"course": "KIN 1600"}   (one specific required course)
- {"or": [ ... ]}   (any one of these)
- {"and": [ ... ]}   (all of these)
- {"hours_from": 6, "courses": ["KIN 2600", "KIN 2603"]}   (N credit HOURS chosen from a specific list)
- {"courses_from": 2, "courses": ["CE 4420", "CE 4440"]}   (N COURSES chosen from a specific list)
- {"hours_in": 9, "subject": "REL"}   (N hours of any courses with that prefix)
- {"hours_in": 6, "subject": "REL", "min_level": 3000}   (N hours with that prefix at a level or above)
- {"hours_in": 12, "subject": "GEOL", "except": ["GEOL 3909"]}   (optional "except" list of courses that do not count)
- {"other": "text"}   (anything that does not fit the forms above)

Rules:
- The top level is always {"and": [ ... ]} listing every requirement.
- Each object has exactly one of these keys: course, or, and, hours_from, courses_from, hours_in, other.
- "hours_in" MUST have a "subject". The subject must be an official course prefix in capital letters (like "REL", "LATN", "PHIL"). If there is no single prefix (e.g. "approved courses", "courses at the 3000 level", "ceramics courses"), use "other" instead.
- Use "hours_from" only when the text says hours. When it counts courses ("two courses from"), use "courses_from".
- Ignore the total hour count; only list the individual requirements.
- Only use course codes that appear in the text. Output only the JSON, nothing else.
- "course" and "courses" must contain only real course codes like "KIN 1600". If the text describes a group (e.g. "approved electives", "core courses", "technical electives"), use "other".

Examples:
Text: To graduate with a minor in health sciences, students must complete 18 semester hours from the following: KIN 1600; 6 semester hours selected from KIN 2600, KIN 2603, KIN 2604; 9 semester hours from KIN 3605, KIN 3608, KIN 3609, KIN 3660, KIN 4601, KIN 4604, KIN 4605, KIN 4606, KIN 4609.
JSON: {"and": [{"course": "KIN 1600"}, {"hours_from": 6, "courses": ["KIN 2600", "KIN 2603", "KIN 2604"]}, {"hours_from": 9, "courses": ["KIN 3605", "KIN 3608", "KIN 3609", "KIN 3660", "KIN 4601", "KIN 4604", "KIN 4605", "KIN 4606", "KIN 4609"]}]}

Text: To obtain a minor in Latin, a student must have a minimum of 16 hours of instruction in LATN at the 2000 level and above. At least six hours must be taken at the 3000 level or above.
JSON: {"and": [{"hours_in": 16, "subject": "LATN", "min_level": 2000}, {"hours_in": 6, "subject": "LATN", "min_level": 3000}]}

Text: A minor in religious studies requires 15 hours, including REL 2027, REL 2029, and nine hours of REL electives, of which at least six hours must be at the 3000 level or above.
JSON: {"and": [{"course": "REL 2027"}, {"course": "REL 2029"}, {"hours_in": 9, "subject": "REL"}, {"hours_in": 6, "subject": "REL", "min_level": 3000}]}

Text: To earn a minor in structural engineering, a student must complete CE 3415, CE 4400, CE 4430 or CE 4460, and two additional courses chosen from an approved list (CE 4420, CE 4440, CE 4450).
JSON: {"and": [{"course": "CE 3415"}, {"course": "CE 4400"}, {"or": [{"course": "CE 4430"}, {"course": "CE 4460"}]}, {"courses_from": 2, "courses": ["CE 4420", "CE 4440", "CE 4450"]}]}

Text: To graduate with a minor in ceramics, students must complete ART 1661, ART 1662, ART 2661 (repeated for six hours of credit), and six semester hours of ceramics courses at the 4000-level. At least nine hours must be at the 3000 level or above.
JSON: {"and": [{"course": "ART 1661"}, {"course": "ART 1662"}, {"course": "ART 2661"}, {"other": "ART 2661 repeated for six hours of credit"}, {"other": "six semester hours of ceramics courses at the 4000-level"}, {"other": "at least nine hours at the 3000 level or above"}]}

Now convert this:
Text: """

with open("academic_programs/minors.json", "r", encoding="utf-8") as f:
    minors = json.load(f)

with open("courses/coursesfinal.json", "r", encoding="utf-8") as f:
    all_courses = json.load(f)

prefixes = set()
for course_code in all_courses:
    prefixes.add(course_code.split()[0])

if os.path.exists("academic_programs/minorrules.json"):
    with open("academic_programs/minorrules.json", "r", encoding="utf-8") as f:
        results = json.load(f)
else:
    results = {}

todo = []

for title, minor in minors.items():
    if title not in results:
        todo.append((title, minor))

for title, minor in tqdm(todo):
    prompt = instructions + minor["text"] + "\nJSON:"

    try:
        response = ollama.chat(
            model="gemma4:12b",
            messages=[{"role": "user", "content": prompt}],
            format="json",
            think=False,
        )
    except:
        tqdm.write(f"{title} ollama error")
        continue

    reply = response["message"]["content"]

    try:
        new_rule = json.loads(reply)
    except json.JSONDecodeError:
        tqdm.write(f"{title} failed")
        continue

    dumped = json.dumps(new_rule)
    rule_codes = re.findall(r"[A-Z]+ \d{4}", dumped)
    valid = True

    for c in rule_codes:
        if c not in minor["text"]:
            tqdm.write(f"{title} bad code: {c}")
            valid = False

    if dumped.count('"hours_in"') != dumped.count('"subject"'):
        tqdm.write(f"{title} hours_in without subject")
        valid = False

    for subject in re.findall(r'"subject": "([^"]*)"', dumped):
        if subject not in prefixes:
            tqdm.write(f"{title} bad subject: {subject}")
            valid = False

    if not valid:
        continue

    new_rule["source"] = "llm"
    results[title] = new_rule
    tqdm.write(f"{title}: {dumped}")

    if len(results) % 25 == 0:
        with open("academic_programs/minorrules.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

with open("academic_programs/minorrules.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(len(results))
