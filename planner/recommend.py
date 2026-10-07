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
)


def recommended_plan(track):
    semesters = []
    seen_groups = set()

    for semester in track["semesters"]:
        items = []
        skip_next = False

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
                    else:
                        section = slot_base(item["description"], item["credits"])

                    items.append(
                        {
                            "type": "slot",
                            "description": item["description"],
                            "credits": item["credits"],
                            "section": section,
                        }
                    )
                    continue

            if skip_next:
                skip_next = False
                continue
            group = item.get("group")
            if group is not None:
                if group in seen_groups:
                    continue
                seen_groups.add(group)

            items.append({"type": "course", "code": item["code"]})

            if item["connector"] == "or":
                skip_next = True
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

    for semester in plan:
        current = semester_codes(semester)
        hours = 0

        for e in semester:
            hours += entry_hours(e)

        if (
            can_take(rule, taken_before, current)
            and hours + course_hours(code) <= max_hours
        ):
            semester.append({"type": "course", "code": code})
            return

        taken_before.update(current)

    plan.append([{"type": "course", "code": code}])


if __name__ == "__main__":
    with open("data/degrees.json", "r", encoding="utf-8") as f:
        degrees = json.load(f)

    with open("data/minorsfinal.json", "r", encoding="utf-8") as f:
        minors = json.load(f)

    plan = recommended_plan(degrees["14278"]["tracks"][4])
    planned = set()

    for semester in plan:
        planned.update(semester_codes(semester))

    picks = minor_courses(minors["14192"]["rule"], planned)

    for code in picks:
        place_course(plan, code, set())

    for i, semester in enumerate(plan):
        hours = 0
        for entry in semester:
            hours += entry_hours(entry)
        print(i + 1, hours, semester_codes(semester))

    print(minor_courses(minors["14192"]["rule"], set()))
    print(minor_courses(minors["14192"]["rule"], {"SCRN 2001", "SCRN 2203"}))

    plan_a = recommended_plan(degrees["14278"]["tracks"][4])
    plan_b = recommended_plan(degrees["14278"]["tracks"][2])

    merged = merge_plans([plan_a, plan_b])

    for i, semester in enumerate(merged):
        print(i + 1, len(plan_a[i]), len(plan_b[i]), len(semester))
