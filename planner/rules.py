import json
import re

with open("data/coursesfinal.json", "r", encoding="utf-8") as f:
    courses = json.load(f)

BY_TITLE = {}

for code, info in courses.items():
    prefix = code.split()[0]
    BY_TITLE[(prefix, info["title"])] = code

TWINS = {}

for code, info in courses.items():
    title = info["title"]

    if title.startswith("HONORS: "):
        prefix = code.split()[0]
        regular = BY_TITLE.get((prefix, title[len("HONORS: ") :]))

        if regular is not None:
            TWINS[code] = regular
            TWINS[regular] = code

with open("data/geneds.json", "r", encoding="utf-8") as f:
    gen_eds = json.load(f)


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

GENED_SETS = {}

for category, info in gen_eds.items():
    GENED_SETS[category] = set(info["courses"])

for code in courses:
    PREFIXES.add(code.split()[0])


def is_lab(code):
    if code not in courses:
        return False
    else:
        return bool(re.search(r"\blab", courses[code]["title"].lower()))


lab_prefixes = set()

for nat_sci in GENED_SETS["Natural Sciences"]:
    lab_prefixes.add(nat_sci.split()[0])

LAB_COURSES = []

for code in courses:
    prefix, number = code.split()
    number = int(number)

    if is_lab(code) and prefix in lab_prefixes and number < 3000:
        LAB_COURSES.append(code)

LAB_COURSES.sort()

STANDING = {
    "sophomore standing": 31,
    "junior standing": 61,
    "junior or senior standing": 61,
    "at least junior standing": 61,
    "senior standing": 91,
    "senior or graduate standing": 91,
}

HIGHER = {
    "MATH 1021": [
        "MATH 1022",
        "MATH 1023",
        "MATH 1431",
        "MATH 1550",
        "MATH 1551",
        "MATH 1552",
        "MATH 1553",
    ],
    "MATH 1022": [
        "MATH 1023",
        "MATH 1510",
        "MATH 1550",
        "MATH 1551",
        "MATH 1552",
        "MATH 1553",
    ],
    "MATH 1023": ["MATH 1550", "MATH 1510", "MATH 1551", "MATH 1552", "MATH 1553"],
    "MATH 1431": ["MATH 1550", "MATH 1551"],
    "BIOL 1001": ["BIOL 1201"],
    "BIOL 1002": ["BIOL 1202"],
    "EDCI 3136": ["EDCI 4720"],
}

NS_SEQUENCES = {
    "BIOL 1001": ["BIOL 1002"],
    "BIOL 1201": ["BIOL 1202", "BIOL 1503"],
    "CHEM 1001": ["CHEM 1002"],
    "CHEM 1201": ["CHEM 1202"],
    "CHEM 1421": ["CHEM 1422", "CHEM 1202"],
    "PHYS 2001": ["PHYS 2002"],
    "PHYS 1201": ["PHYS 1202"],
    "PHYS 2110": ["PHYS 2112", "PHYS 2113"],
    "PHSC 1001": ["PHSC 1002"],
    "GEOL 1001": ["GEOL 1003"],
    "GEOL 1201": ["GEOL 1202"],
}

POSSIBLE_SEQUENCES = {
    "ASTR 1101": ["ASTR 1102"],
    "GEOL 1001": ["GEOL 2020"],
    "GEOL 1002": ["GEOL 2020"],
    "HORT 2050": ["HORT 2061"],
    "GEOG 2050": ["GEOG 2051"],
    "OCS 1005": ["OCS 2005"],
}

LIFE_SCIENCES = {
    "BIOL 1001",
    "BIOL 1002",
    "BIOL 1011",
    "BIOL 1201",
    "BIOL 1202",
    "BIOL 1503",
    "AGRI 1005",
    "AGRO 1001",
    "HORT 2050",
    "HORT 2061",
    "RNR 1001",
    "HNRS 1035",
    "HNRS 2010",
    "ENVS 1126",
    "ENVS 1127",
    "ENVS 2126",
    "ENVS 2127",
    "OCS 2050",
}

NS_LABS = {
    "BIOL 1001": ["BIOL 1005"],
    "BIOL 1201": ["BIOL 1208", "BIOL 1209", "BIOL 1207"],
    "CHEM 1001": ["CHEM 1212"],
    "CHEM 1201": ["CHEM 1212"],
    "CHEM 1421": ["CHEM 1431", "CHEM 1212"],
    "PHYS 2001": ["PHYS 2108", "PHYS 2109"],
    "PHYS 2110": ["PHYS 2108", "PHYS 2109"],
    "PHYS 1201": ["PHYS 1208", "PHYS 1209"],
    "GEOL 1001": ["GEOL 1601", "GEOL 1602"],
}


def fix_standing(rule):
    if not isinstance(rule, dict):
        return

    for key in ("and", "or"):
        if key in rule:
            for i, child in enumerate(rule[key]):
                if isinstance(child, dict):
                    text = child.get("other", "").lower().strip()

                    if text in STANDING:
                        rule[key][i] = {"standing": STANDING[text]}

                    else:
                        fix_standing(child)


def drop_recommended(rule):
    if not isinstance(rule, dict):
        return

    for key in ("and", "or"):
        if key in rule:
            kept = []

            for child in rule[key]:
                if isinstance(child, dict) and (
                    "other" in child and "recommended" in child["other"].lower()
                ):
                    continue
                else:
                    drop_recommended(child)
                    kept.append(child)

            rule[key] = kept


for code, info in courses.items():
    rule = info["prereq_rule"]

    if (
        isinstance(rule, dict)
        and "other" in rule
        and rule.get("other", "").lower().strip() in STANDING
    ):
        info["prereq_rule"] = {
            "standing": STANDING[rule.get("other", "").lower().strip()]
        }

    else:
        fix_standing(rule)

    drop_recommended(info["prereq_rule"])

courses["AGRO 2051"]["prereq_rule"] = {
    "or": [{"course": "CHEM 1001"}, {"course": "CHEM 1002"}, {"course": "CHEM 1202"}]
}

courses["EDCI 3001"]["prereq_rule"] = {
    "and": [
        {"course": "EDCI 2001", "concurrent": True},
        {
            "or": [
                {"course": "ENGL 3203", "concurrent": True},
                {"course": "FREN 3401", "concurrent": True},
                {"course": "HIST 3001", "concurrent": True},
                {"course": "SPAN 3001", "concurrent": True},
            ]
        },
    ]
}

courses["ECON 2035"]["prereq_rule"] = {
    "or": [
        {
            "and": [
                {"or": [{"course": "ECON 2000"}, {"course": "ECON 2001"}]},
                {
                    "or": [{"course": "ECON 2010"}, {"course": "ECON 2011"}],
                },
            ]
        },
        {"course": "ECON 2030"},
    ]
}

courses["GEOL 1202"]["prereq_rule"] = {
    "and": [
        {
            "or": [
                {
                    "and": [{"course": "GEOL 1001"}, {"course": "GEOL 1601"}],
                },
                {"course": "GEOL 1201"},
            ]
        },
        {
            "or": [
                {"course": "MATH 1022", "concurrent": True},
                {"course": "MATH 1023", "concurrent": True},
                {"course": "MATH 1550", "concurrent": True},
                {"course": "MATH 1551", "concurrent": True},
            ]
        },
    ]
}


def slot_base(description, credits):
    base = description.rstrip("*").strip()
    base = re.sub(r"\s*\(\d+(?:\.\d+)?(?:-\d+)?\)\s*$", "", base)

    if base.endswith("Electives"):
        base = base[:-1]

    base = base.split(":")[0].strip()
    base = base.replace("-Level", "-level")

    return base


def family_name(base):
    return re.sub(
        r"^(first|second|third|fourth|fifth)\s+course\s+(in|from)\s+",
        "",
        base,
        flags=re.I,
    )


def meets_level(code, min_level):
    if min_level is None:
        return True
    else:
        prefix, number = code.split()
        number = int(number)

        return number >= min_level


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


def typical_hours(credits):
    low, high = credits
    return max(low, min(3, high))


def course_hours(code):
    if code not in courses:
        return 0

    credits = parse_credits(courses[code]["credits"])

    if credits is None:
        return 0
    else:
        return typical_hours(credits)


def ns_area(code):
    if code in LIFE_SCIENCES:
        return "life"
    else:
        return "physical"


def ns_done(codes):
    ns = set()

    for code in codes:
        if code in GENED_SETS["Natural Sciences"]:
            ns.add(code)

    best = 0

    for area in ["life", "physical"]:
        seq = 0

        for first, seconds in NS_SEQUENCES.items():
            if ns_area(first) != area:
                continue

            if first in ns and any(s in ns for s in seconds):
                seq = 2
            else:
                if first in ns and seq == 0:
                    seq = 1

        other = int(any(ns_area(c) != area for c in ns))

        best = max(best, seq + other)

    return best


def ns_next(codes):
    ns = set()

    for code in codes:
        if code in GENED_SETS["Natural Sciences"]:
            ns.add(code)

    suggestions = []

    for first, seconds in NS_SEQUENCES.items():
        if first not in ns or any(s in ns for s in seconds):
            continue
        else:
            suggestions.extend(seconds)

    return suggestions


def ns_labs_done(codes):
    best = 0

    for first, labs in NS_LABS.items():
        if first not in codes:
            continue

        hours = 0

        for lab in labs:
            if lab in codes:
                hours += course_hours(lab)

        best = max(best, hours)

    return best


def ns_labs_next(codes):
    suggestions = []

    finished = []

    for first, seconds in NS_SEQUENCES.items():
        if first in codes and any(s in codes for s in seconds):
            finished.append(first)

    for first, labs in NS_LABS.items():
        if finished and first not in finished:
            continue

        if first not in codes:
            continue

        for lab in labs:
            if lab not in codes:
                suggestions.append(lab)
                break

    return suggestions


def is_satisfied(rule, taken, current, hours_before=None):
    if rule is None:
        return True

    if "course" in rule:
        if rule["course"] in taken:
            return True
        elif rule.get("concurrent") and rule["course"] in current:
            return True

        if TWINS.get(rule["course"]) in taken or (
            rule.get("concurrent") and TWINS.get(rule["course"]) in current
        ):
            return True

        for course in HIGHER.get(rule["course"], []):
            if course in taken or (rule.get("concurrent") and course in current):
                return True

        return False

    elif "and" in rule:
        seen_none = False

        for child in rule["and"]:
            result = is_satisfied(child, taken, current, hours_before)

            if result is False:
                return False

            elif result is None:
                seen_none = True

        if seen_none:
            return None
        else:
            return True

    elif "or" in rule:
        seen_none = False

        for child in rule["or"]:
            result = is_satisfied(child, taken, current, hours_before)

            if result is True:
                return True

            if result is None:
                seen_none = True

        if seen_none:
            return None
        else:
            return False

    elif "hours_from" in rule:
        total = 0

        for course in rule["courses"]:
            if course in taken and meets_level(course, rule.get("min_level")):
                total += course_hours(course)

        return total >= rule["hours_from"]

    elif "courses_from" in rule:
        count = 0

        for course in rule["courses"]:
            if course in taken and meets_level(course, rule.get("min_level")):
                count += 1

        return count >= rule["courses_from"]

    elif "hours_in" in rule:
        total = 0

        for code in taken:
            if code not in courses:
                continue

            prefix, number = code.split()
            number = int(number)

            if prefix != rule["subject"] and not (
                "honors" in rule and courses[code]["title"].startswith("HONORS: ")
            ):
                continue

            elif rule.get("min_level") is not None and number < rule.get("min_level"):
                continue

            elif code in rule.get("except", []):
                continue

            else:
                total += course_hours(code)

        return total >= rule["hours_in"]

    elif "standing" in rule:
        if hours_before is None:
            return None
        else:
            return hours_before >= rule["standing"]

    if "consent" in rule or "other" in rule or "equivalent" in rule:
        return None


def describe(node):
    if node is None:
        return "none"
    elif "course" in node:
        return node["course"]
    elif "or" in node:
        parts = []

        for n in node["or"]:
            text = describe(n)

            if "and" in n:
                parts.append(f"({text})")
            else:
                parts.append(text)

        return " or ".join(parts)
    elif "and" in node:
        parts = []

        for n in node["and"]:
            text = describe(n)

            if "or" in n:
                parts.append(f"({text})")
            else:
                parts.append(text)

        return " and ".join(parts)
    elif "hours_from" in node:
        number = node["hours_from"]
        codes = node["courses"]

        first_five = codes[:5]

        shown = ", ".join(first_five)

        if len(codes) > 5:
            shown += ", ..."

        text = f"{number} hours from: {shown}"

        if node.get("min_level"):
            text += f" at the {node.get('min_level')} level or above"

        return text

    elif "courses_from" in node:
        number = node["courses_from"]
        codes = node["courses"]

        first_five = codes[:5]

        shown = ", ".join(first_five)

        if len(codes) > 5:
            shown += ", ..."

        return f"{number} courses from: {shown}"
    elif "hours_in" in node:
        number = node["hours_in"]
        subject = node["subject"]

        text = f"{number} hours of {subject}"

        if node.get("min_level"):
            text += f" at the {node.get('min_level')} level or above"

        if node.get("except"):
            excluded = ", ".join(node["except"])

            text += f" (not {excluded})"

        return text
    elif "other" in node:
        return node["other"]
    elif "consent" in node:
        return f"consent of the {node['consent']}"
    elif "equivalent" in node:
        return "or equivalent"
    elif "standing" in node:
        return f"{node['standing']}+ credit hours earned"
    else:
        return "?"


def used_courses(node, taken):
    if node is None:
        return []
    elif "course" in node:
        if node["course"] in taken:
            return [node["course"]]
        else:
            return []
    elif "and" in node or "or" in node:
        found = []

        if "and" in node:
            children = node["and"]
        else:
            children = node["or"]

        for child in children:
            found.extend(used_courses(child, taken))
        return found
    elif "hours_from" in node or "courses_from" in node:
        found = []

        for code in node["courses"]:
            if code in taken and meets_level(code, node.get("min_level")):
                found.append(code)
        return found
    elif "hours_in" in node:
        found = []

        for code in taken:
            if code not in courses:
                continue

            prefix, number = code.split()
            number = int(number)

            if (
                node["subject"] != prefix
                and not (
                    "honors" in node and courses[code]["title"].startswith("HONORS: ")
                )
                or (
                    node.get("min_level") is not None and node.get("min_level") > number
                )
                or code in node.get("except", [])
            ):
                continue
            else:
                found.append(code)
        return found
    else:
        return []


def minor_rows(rule, taken):
    if rule is None:
        return []

    if "and" in rule:
        children = rule["and"]
    else:
        children = [rule]

    rows = []

    for child in children:
        result = is_satisfied(child, taken, set())

        if result is True:
            mark = "✓"
        elif result is False:
            mark = "✗"
        else:
            mark = "?"

        label = describe(child)

        used = used_courses(child, taken)
        found = []

        for code in used:
            if code not in found:
                found.append(code)

        if not found:
            filled = "-"
        else:
            filled = ", ".join(found)

        rows.append({"mark": mark, "label": label, "filled_by": filled})
    return rows


def can_take(rule, taken, current, hours_before=None):
    result = is_satisfied(rule, taken, current, hours_before)

    if result is not False:
        return True
    else:
        return False


def check_plan(plan, prior, courses, extra=None):
    taken = set(prior)

    problems = []

    hours = 0

    for code in prior:
        hours += course_hours(code)

    for i, semester in enumerate(plan):
        current = set(semester)

        for code in semester:
            if code not in courses:
                problems.append(((i + 1), code, "unknown course"))
                continue

            rule = courses[code]["prereq_rule"]

            if can_take(rule, taken, current, hours) is False:
                problems.append((i + 1, code, "prereqs not met"))

        taken.update(semester)

        hours += sum(course_hours(code) for code in semester)

        if extra and i < len(extra):
            hours += extra[i]

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


def check_hours(plan, courses, max_hours=19, approved_max=21, min_hours=12, extra=None):
    totals = semester_hours(plan, courses)
    problems = []

    for i, total in enumerate(totals):
        add = 0

        if extra and i < len(extra):
            add = extra[i]
        low = total[0] + add
        high = total[1] + add

        if low > approved_max:
            problems.append((i + 1, low, "over maximum"))
        elif low > max_hours:
            problems.append((i + 1, low, "needs advisor approval"))
        elif high < min_hours:
            problems.append((i + 1, high, "below full-time"))

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


def classify_slot(desc):
    lower = desc.lower()
    negative = any(word in lower for word in NEGATIVE_WORDS)

    codes = re.findall(r"[A-Z]+ \d{4}(?![-/]|\s*-?\s*[Ll]evel)", desc)

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

        only = []
        exclude = []
        min_level = None

        if "communication studies" in lower:
            only.append("CMST")
        elif "from mathematics" in lower:
            only.append("MATH")
        elif "not mus" in lower:
            exclude.append("MUS")
        elif "english/honors 2000-level" in lower or "engl/hnrs 2000-level" in lower:
            only.extend(["ENGL", "HNRS"])
            min_level = 2000
        elif "from field other than psychology" in lower:
            exclude.append("PSYC")
        elif "other than english" in lower or "other than engl " in lower:
            exclude.extend(
                [
                    "ENGL",
                    "ARAB",
                    "ASLG",
                    "CHIN",
                    "FREN",
                    "GERM",
                    "GREK",
                    "HEBR",
                    "ITAL",
                    "JAPN",
                    "LATN",
                    "SPAN",
                ]
            )
        elif "other than" in lower and "foreign language" in lower:
            exclude.extend(
                [
                    "ARAB",
                    "ASLG",
                    "CHIN",
                    "FREN",
                    "GERM",
                    "GREK",
                    "HEBR",
                    "ITAL",
                    "JAPN",
                    "LATN",
                    "SPAN",
                ]
            )
        elif "other than geog; 2000-level" in lower:
            exclude.append("GEOG")
            min_level = 2000

        if categories:
            return {
                "kind": "gened",
                "categories": categories,
                "only": only,
                "exclude": exclude,
                "min_level": min_level,
            }

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


def slot_kind(slot, track):
    kind_info = classify_slot(slot["description"])
    fn = slot.get("footnote")

    if kind_info["kind"] == "unknown" and fn is not None and fn in track["footnotes"]:
        text = track["footnotes"][fn]
        codes = re.findall(r"[A-Z]+ \d{4}(?![-/]|\s*-?\s*[Ll]evel)", text)

        if codes:
            kind_info = {"kind": "list", "courses": codes}
            level = re.search(r"([1-4])000-level", text)

            if level is not None and (
                "and above" in text.lower() or "or above" in text.lower()
            ):
                bare_prefixes = re.findall(r"\b([A-Z]{2,5})\b(?!\s*\d)", text)
                subjects = []

                for prefix in bare_prefixes:
                    if prefix in PREFIXES and prefix not in subjects:
                        subjects.append(prefix)

                if subjects:
                    kind_info["subjects"] = subjects
                    kind_info["min_level"] = int(level.group(1)) * 1000

    return kind_info


def fits(code, kind_info, description=""):
    if code not in courses:
        return False

    if kind_info["kind"] == "list":
        prefix = code.split()[0]

        if code in kind_info["courses"] or (
            prefix in kind_info.get("subjects", [])
            and meets_level(code, kind_info.get("min_level"))
        ):
            return True

        return False

    elif kind_info["kind"] == "subject":
        prefix = code.split()[0]
        return prefix in kind_info["subjects"] and meets_level(
            code, kind_info["min_level"]
        )

    elif kind_info["kind"] == "free":
        return True

    elif kind_info["kind"] == "gened":
        if "lab" in description.lower():
            return is_lab(code)

        prefix = code.split()[0]

        if kind_info.get("only") and prefix not in kind_info["only"]:
            return False
        elif prefix in kind_info.get("exclude", []):
            return False
        elif not meets_level(code, kind_info.get("min_level")):
            return False

        for category in kind_info["categories"]:
            if code in GENED_SETS[category]:
                return True

        return False

    else:
        return None


def slots_accept(code, slot, track, gened_sets):
    return fits(code, slot_kind(slot, track), slot["description"])


def build_requirements(track):
    requirements = []
    groups = {}
    pending = []

    for semester in track["semesters"]:
        for item in semester["items"]:
            if item["type"] == "course":
                if item["group"] is not None:
                    groups.setdefault(item["group"], []).append(item["code"])
                    continue
                else:
                    pending.append(item["code"])

                if item["connector"] == "or":
                    continue
                else:
                    requirements.append({"type": "course", "options": pending})
                    pending = []
            else:
                if item.get("group") is not None:
                    continue
                else:
                    requirements.append({"type": "slot", "slot": item})

    for value in groups.values():
        requirements.append({"type": "course", "options": value})

    return requirements


def audit_ns_lecture(slot, track):
    kind_info = slot_kind(slot, track)

    if (
        kind_info["kind"] == "gened"
        and "Natural Sciences" in kind_info["categories"]
        and "lab" not in slot["description"].lower()
    ):
        return True

    return False


def audit_strict_lab(slot, track):
    note = (track["footnotes"].get(slot.get("footnote")) or "").lower()

    if "lab" in slot["description"].lower() and (
        "associated" in note or "corresponding" in note
    ):
        return True

    return False


def audit(plan, prior, track, gened_sets):
    reqs = build_requirements(track)

    available = list(prior)

    for semester in plan:
        available.extend(semester)

    used = set()

    results = []

    for req in reqs:
        if req["type"] != "course":
            continue

        filled = None

        for option in req["options"]:
            codes_try = [option, TWINS.get(option)]

            for codes in codes_try:
                if codes in available and codes not in used:
                    filled = codes
                    used.add(codes)
                    break

            if filled is not None:
                break

        results.append({"requirement": req, "filled_by": filled})

    KIND_ORDER = ["list", "subject", "gened", "unknown", "free"]

    ns_reqs = []
    lab_reqs = []

    for req in reqs:
        if req["type"] == "slot" and audit_strict_lab(req["slot"], track):
            lab_reqs.append(req)

    covered = ns_labs_done(available)

    lab_courses = []

    for labs in NS_LABS.values():
        for lab in labs:
            if lab in available and lab not in used and lab not in lab_courses:
                lab_courses.append(lab)

    for req in lab_reqs:
        credits = parse_credits(req["slot"]["credits"])

        if credits is None:
            needed = 3
        else:
            needed = credits[0]

        filled = []

        hours = min(covered, needed)
        covered -= hours

        shown = 0

        while shown < hours and lab_courses:
            code = lab_courses.pop(0)
            filled.append(code)
            used.add(code)
            shown += course_hours(code)

        results.append(
            {
                "requirement": req,
                "filled_by": filled,
                "hours": hours,
                "needed": needed,
                "kind": "gened",
            }
        )

    for kind in KIND_ORDER:
        for req in reqs:
            if req["type"] != "slot":
                continue

            if slot_kind(req["slot"], track)["kind"] != kind:
                continue

            if audit_ns_lecture(req["slot"], track):
                ns_reqs.append(req)
                continue

            if audit_strict_lab(req["slot"], track):
                continue

            credits = parse_credits(req["slot"]["credits"])

            if credits is None:
                needed = 3
            else:
                needed = credits[0]

            filled = []
            hours = 0

            for code in available:
                if code not in used and slots_accept(
                    code, req["slot"], track, gened_sets
                ):
                    filled.append(code)
                    used.add(code)

                    hours += course_hours(code)

                    if hours >= needed:
                        break

            results.append(
                {
                    "requirement": req,
                    "filled_by": filled,
                    "hours": hours,
                    "needed": needed,
                    "kind": slot_kind(req["slot"], track)["kind"],
                }
            )

        if kind == "gened":
            covered = ns_done(available) * 3

            seq_codes = set().union(NS_SEQUENCES)

            for seconds in NS_SEQUENCES.values():
                seq_codes.update(seconds)

            seq_first = [
                c
                for c in available
                if c not in used
                and c in GENED_SETS["Natural Sciences"]
                and c in seq_codes
                and not is_lab(c)
            ]

            others = [
                c
                for c in available
                if c not in used
                and c in GENED_SETS["Natural Sciences"]
                and c not in seq_codes
                and not is_lab(c)
            ]

            ns_courses = seq_first + others

            for req in ns_reqs:
                credits = parse_credits(req["slot"]["credits"])

                if credits is None:
                    needed = 3
                else:
                    needed = credits[0]

                filled = []
                hours = 0

                if covered >= needed:
                    while hours < needed and ns_courses:
                        code = ns_courses.pop(0)
                        filled.append(code)
                        used.add(code)
                        hours += course_hours(code)

                    hours = needed
                    covered -= needed

                results.append(
                    {
                        "requirement": req,
                        "filled_by": filled,
                        "hours": hours,
                        "needed": needed,
                        "kind": "gened",
                    }
                )

    unused = [code for code in available if code not in used]
    return {"results": results, "unused": unused}


def check_total_hours(plan, prior, track):
    total_hours = parse_credits(track["total_hours"])

    if total_hours is None:
        return None

    needed = total_hours[0]

    have = 0

    for code in prior:
        have += course_hours(code)

    for semester in plan:
        for code in semester:
            have += course_hours(code)

    return {"have": have, "needed": needed, "done": have >= needed}
