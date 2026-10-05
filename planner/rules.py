import json
import re

with open("data/coursesfinal.json", "r", encoding="utf-8") as f:
    courses = json.load(f)


def parse_credits(value):
    if value is None:
        return None

    if "(" in value:
        value = value.split("(")[-1]

    numbers = re.findall(r"\d+(?:\.\d+)?", value)

    if not numbers:
        return None

    values = []

    for n in numbers:
        values.append(float(n))

    return (min(values), max(values))


def is_satisfied(rule, taken, current):
    if rule is None:
        return True

    if "course" in rule:
        if rule["course"] in taken:
            return True
        elif rule.get("concurrent") and rule["course"] in current:
            return True
        else:
            return False

    elif "and" in rule:
        seen_true = False

        for child in rule["and"]:
            result = is_satisfied(child, taken, current)

            if result is False:
                return False

            elif result is True:
                seen_true = True

        if seen_true is True:
            return True

        else:
            return None

    elif "or" in rule:
        seen_false = False

        for child in rule["or"]:
            result = is_satisfied(child, taken, current)

            if result is True:
                return True

            elif result is False:
                seen_false = True

        if seen_false is True:
            return False

        return None

    if "consent" in rule or "other" in rule or "equivalent" in rule:
        return None


def can_take(rule, taken, current):
    result = is_satisfied(rule, taken, current)

    if result is not False:
        return True
    else:
        return False


def check_plan(plan, prior, courses):
    taken = set(prior)

    problems = []

    for i, semester in enumerate(plan):
        current = set(semester)

        for code in semester:
            if code not in courses:
                problems.append(((i + 1), code, "unknown course"))
                continue

            rule = courses[code]["prereq_rule"]

            if can_take(rule, taken, current) is False:
                problems.append((i + 1, code, "prereqs not met"))

        taken.update(semester)

    return problems


formats = set()

for code, course in courses.items():
    formats.add(course["credits"])

print(len(formats))

for value in sorted(formats, key=str):
    print(f"{value!r} -> {parse_credits(value)}")
