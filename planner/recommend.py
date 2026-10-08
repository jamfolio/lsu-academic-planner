import json
from planner.rules import (
    classify_slot,
    is_satisfied,
    course_hours,
    can_take,
    parse_credits,
    courses,
    meets_level,
    slot_kind,
    slot_base,
    GENED_SETS,
)

EARLIEST = {"HNRS 1010": 2}
END_SEQUENCE = ["HNRS 3800", "HNRS 3900", "HNRS 4000"]

def recommended_plan(track, major=0):
    semesters = []
    seen_groups = set()

    for semester in track["semesters"]:
        items = []
        chain = None

        for item in semester["items"]:
            if item["type"] == "slot":
                if item.get("group") is not None:
                    continue
                else:
                    kind_info = slot_kind(item, track)

                    if kind_info["kind"] == "gened":
                        if "lab" in item["description"].lower():
                            section = "Natural Sciences Lab"
                        else:
                            section = kind_info["categories"][0]
                    elif kind_info["kind"] == "free":
                        section = "free"
                    else:
                        section = slot_base(item["description"], item["credits"])

                    items.append(
                        {
                            "type": "slot",
                            "description": item["description"],
                            "credits": item["credits"],
                            "section": section,
                            "major": major,
                            "kind_info": kind_info,
                        }
                    )
                    chain = None
                    continue

            group = item.get("group")
            if group is not None:
                if group in seen_groups:
                    continue
                seen_groups.add(group)

            if chain is not None:
                chain["options"].append(item["code"])
            else:
                entry = {
                    "type": "course",
                    "code": item["code"],
                    "options": [item["code"]],
                }
                items.append(entry)

            if item["connector"] == "or":
                chain = entry
            else:
                chain = None

        semesters.append(items)
    return semesters


def merge_plans(plans):
    merged = []
    placed = set()
    longest = max([len(plan) for plan in plans])

    for i in range(longest):
        semester = []

        for p_index, p in enumerate(plans):
            if i >= len(p):
                continue

            for entry in p[i]:
                if entry["type"] == "course":
                    if entry["code"] in placed:
                        continue
                    else:
                        semester.append(entry)
                        placed.add(entry["code"])
                else:
                    if p_index > 0 and (
                        classify_slot(entry["description"])["kind"] == "gened"
                        or classify_slot(entry["description"])["kind"] == "free"
                    ):
                        continue
                    else:
                        semester.append(entry)

        merged.append(semester)

    return merged


def minor_courses(rule, planned):
    if rule is None:
        return []

    if "course" in rule:
        if rule["course"] in planned:
            return []
        else:
            return [rule["course"]]
    elif "and" in rule:
        picks = []

        for child in rule["and"]:
            picks.extend(minor_courses(child, planned | set(picks)))
        return picks
    elif "or" in rule:
        for child in rule["or"]:
            if is_satisfied(child, planned, set()) is True:
                return []

        return minor_courses(rule["or"][0], planned)
    elif "hours_from" in rule:
        total = 0
        picks = []

        for course in rule["courses"]:
            if course in planned:
                total += course_hours(course)

        for course in rule["courses"]:
            if total >= rule["hours_from"]:
                break
            elif course in planned:
                continue
            elif not meets_level(course, rule.get("min_level")):
                continue
            else:
                picks.append(course)
                total += course_hours(course)

        return picks
    elif "courses_from" in rule:
        total = 0
        picks = []

        for course in rule["courses"]:
            if course in planned:
                total += 1

        for course in rule["courses"]:
            if total >= rule["courses_from"]:
                break
            elif course in planned:
                continue
            else:
                picks.append(course)
                total += 1

        return picks
    else:
        return []


def entry_hours(entry):
    if entry["type"] == "course":
        return course_hours(entry["code"])
    elif entry["type"] == "slot":
        credits = parse_credits(entry["credits"])

        if credits is None:
            return 3
        else:
            return credits[0]


def semester_codes(semester):
    codes = set()

    for entry in semester:
        if entry["type"] == "course":
            codes.add(entry["code"])

    return codes


def place_course(plan, code, prior, max_hours=19):
    if code not in courses:
        plan[-1].append({"type": "course", "code": code})
        return

    rule = courses[code]["prereq_rule"]
    taken_before = set(prior)

    for i, semester in enumerate(plan):
        current = semester_codes(semester)
        hours = 0

        for e in semester:
            hours += entry_hours(e)

        if (
            can_take(rule, taken_before, current)
            and hours + course_hours(code) <= max_hours
            and EARLIEST.get(code, 1) <= i + 1
        ):
            semester.append({"type": "course", "code": code})
            return

        taken_before.update(current)

    plan.append([{"type": "course", "code": code}])


def rebalance(plan, max_hours=19):
    i = 0
    while i < len(plan):
        semester = plan[i]
        hours = 0

        for e in semester:
            hours += entry_hours(e)

        while hours > max_hours and len(semester) > 1:
            to_move = None

            for e in reversed(semester):
                if e["type"] == "slot":
                    to_move = e
                    break

            if to_move is None:
                to_move = semester[-1]

            semester.remove(to_move)

            if i + 1 == len(plan):
                plan.append([])

            plan[i + 1].insert(0, to_move)
            hours -= entry_hours(to_move)
        i += 1


def fits(code, kind_info):
    if kind_info["kind"] == "list":
        return code in kind_info["courses"]
    elif kind_info["kind"] == "subject":
        prefix = code.split()[0]
        return prefix in kind_info["subjects"] and meets_level(
            code, kind_info["min_level"]
        )
    elif kind_info["kind"] == "free":
        return True
    elif kind_info["kind"] == "gened":
        for category in kind_info["categories"]:
            if code in GENED_SETS[category]:
                return True
        return False
    else:
        return False


def absorb_slots(plan, own_codes, prior):
    all_codes = []

    for semester in plan:
        all_codes.extend(semester_codes(semester))

    all_codes.extend(prior)

    claimed = [set() for _ in own_codes]
    for semester in plan:
        keep = []
        for e in semester:
            if e["type"] != "slot" or e["kind_info"]["kind"] not in (
                "list",
                "subject",
                "free",
                "gened",
            ):
                keep.append(e)
                continue

            m = e["major"]
            needed = entry_hours(e)
            got = 0

            for code in all_codes:
                if got >= needed:
                    break

                if code in own_codes[m] or code in claimed[m]:
                    continue

                if fits(code, e["kind_info"]):
                    claimed[m].add(code)
                    got += course_hours(code)

            if got >= needed:
                continue
            elif got > 0:
                e["credits"] = str(needed - got)
                keep.append(e)
            else:
                keep.append(e)
        semester[:] = keep


def remove_prior(plan, prior):
    for semester in plan:
        keep = []

        for e in semester:
            if e["type"] == "slot":
                keep.append(e)
                continue

            options = set(e.get("options", [e["code"]]))
            if options & prior:
                continue

            keep.append(e)
        semester[:] = keep

def compact(plan, prior, target=15, max_hours=19):
    taken_before = set(prior)

    for i in range(len(plan)):
        semester = plan[i]
        hours = 0

        for e in semester:
            hours += entry_hours(e)

        for j in range(i + 1, len(plan)):
            for e in list(plan[j]):
                if hours >= target:
                    break

                h = entry_hours(e)
                if hours + h > max_hours:
                    continue

                if e["type"] == "course":
                    rule = courses.get(e["code"], {}).get("prereq_rule")
                    if can_take(rule, taken_before, semester_codes(semester)) is False:
                        continue
                    if EARLIEST.get(e["code"], 1) > i + 1:
                        continue
            
                plan[j].remove(e)
                semester.append(e)
                hours += h

        taken_before.update(semester_codes(semester))
    plan[:] = [s for s in plan if s]

def find_entry(plan, code):
    for semester in plan:
        for e in semester:
            if e["type"] == "course" and code in e.get("options", [e["code"]]):
                return semester, e

    return None, None

def place_end_sequence(plan):
    found = []

    for code in END_SEQUENCE:
        semester, entry = find_entry(plan, code)

        if entry is None:
            continue

        semester.remove(entry)
        found.append(entry)

    plan[:] = [s for s in plan if s]

    while len(plan) < len(found):
        plan.append([])

    n = len(found)

    for k, entry in enumerate(found):
        plan[len(plan) - n + k].append(entry)

if __name__ == "__main__":
    with open("data/degrees.json", "r", encoding="utf-8") as f:
        degrees = json.load(f)

    with open("data/minorsfinal.json", "r", encoding="utf-8") as f:
        minors = json.load(f)

    plan = recommended_plan(degrees["14258"]["tracks"][0])

    for i in [0, 3]:
        print(f"Semester {i + 1}:")
        for entry in plan[i]:
            if entry["type"] == "course":
                print("  course", entry["code"], entry["options"])
            else:
                print("  slot  ", entry["description"])
        print()
