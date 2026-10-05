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


def semester_hours(plan, courses):
    totals = []

    for semester in plan:
        low = 0
        high = 0

        for code in semester:
            if code not in courses:
                continue

            credit_tuple = parse_credits(courses[code]["credits"])

            if credit_tuple is None:
                continue

            low += credit_tuple[0]
            high += credit_tuple[1]

        totals.append((low, high))

    return totals


def check_hours(plan, courses, max_hours=19, approved_max=21):
    totals = semester_hours(plan, courses)
    problems = []

    for i, total in enumerate(totals):
        if total[0] > approved_max:
            problems.append((i + 1, total[0], "over maximum"))
        elif total[0] > max_hours:
            problems.append((i + 1, total[0], "needs advisor approval"))

    return problems


GENED_KEYWORDS = [
    ("english composition", "English Composition"),
    ("analytical reasoning", "Mathematical/Analytical Reasoning"),
    ("anlaytical reasoning", "Mathematical/Analytical Reasoning"),
    ("art", "Fine Arts"),
    ("humanities", "Humanities"),
    ("natural science", "Natural Sciences"),
    ("life science", "Natural Sciences"),
    ("physical science", "Natural Sciences"),
    ("social science", "Social/Behavioral Sciences"),
]

PREFIXES = set()

SUBJECT_NAMES = [
    ("spanish", ["SPAN"]),
    ("french", ["FREN"]),
    ("german", ["GERM"]),
    ("biology", ["BIOL"]),
    ("biological sciences", ["BIOL"]),
    ("chemistry", ["CHEM"]),
    ("philosophy", ["PHIL"]),
    ("religious studies", ["REL"]),
    ("economics", ["ECON"]),
    ("music history", ["MUS"]),
    ("art history", ["ARTH"]),
    ("history", ["HIST"]),
    ("sociology", ["SOCL"]),
    ("mass communication", ["MC"]),
    ("finance", ["FIN"]),
    ("math", ["MATH"]),
    ("english", ["ENGL"]),
    ("music", ["MUS"]),
    ("studio art", ["ART"]),
    ("business", ["ACCT", "ECON", "FIN", "ISDS", "MGT", "MKT", "ENTR", "BLAW", "GBUS"]),
    (
        "foreign language",
        [
            "SPAN",
            "FREN",
            "GERM",
            "ITAL",
            "LATN",
            "GREK",
            "CHIN",
            "JAPN",
            "ARAB",
            "HEBR",
            "RUSS",
        ],
    ),
]

NEGATIVE_WORDS = [
    ("excluding"),
    ("not "),
    ("other than"),
    ("encouraged"),
    ("recommended"),
]

for code in courses:
    PREFIXES.add(code.split()[0])


def classify_slot(desc):
    lower = desc.lower()
    negative = any(word in lower for word in NEGATIVE_WORDS)

    codes = re.findall(r"[A-Z]+ \d{4}(?![-/]|\s*-?\s*[L1]SSevel)", desc)

    if codes and not negative:
        return {"kind": "list", "courses": codes}

    if (
        "general education" in lower
        or "gen ed" in lower
        or "ilc" in lower
        or lower.startswith("humanities")
        or lower.startswith("social science")
        or lower.startswith("natural science")
    ):

        categories = []

        for keyword, category in GENED_KEYWORDS:
            if re.search(r"\b" + keyword, lower) and category not in categories:
                categories.append(category)

        if categories:
            return {"kind": "gened", "categories": categories}

    words = re.findall(r"\b[A-Z]{2,5}\b", desc)
    subjects = []
    for word in words:
        if word in PREFIXES and word not in subjects:
            subjects.append(word)

    for name, prefixes in SUBJECT_NAMES:
        if re.search(r"\b" + name, lower):
            for prefix in prefixes:
                if prefix not in subjects:
                    subjects.append(prefix)
            break

    if subjects and not negative:
        level = re.search(r"([1-4])(?:000|\*\*\*)", desc)

        if level is not None:
            min_level = int(level.group(1)) * 1000
        elif "upper-division" in lower or "upper division" in lower:
            min_level = 3000
        else:
            min_level = None

        return {"kind": "subject", "subjects": subjects, "min_level": min_level}

    if lower.startswith(
        (
            "elective",
            "free elective",
            "general elective",
            "approved elective",
            "approved free elective",
            "academic elective",
        )
    ):

        return {"kind": "free"}

    return {"kind": "unknown"}
