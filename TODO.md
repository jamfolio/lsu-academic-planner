# TODO

## do now
- [ ] minors w/ hours_in never get courses (no hours_in branch in minor_courses) so 34/123 minors still incomplete
- [ ] minor "or" picks first child even if its an "other" node  gets nothing (construction mgmt)
- [ ] minor course fills 2 slots in the same major (takeover doesnt count as claimed, absorb uses it again) → adding a minor makes plan shorter (spanish 120 goes from 116)
- [ ] merge drops repeated choice chips ("pick 2 from this list" twice) → actuarial math 117 not 120. pick next unused option instead
- [ ] drop_covered_choices drops same-major repeats (music jazz MUS 4253, studio art ART 4280, ag ext BIOL 1001) → only drop if a DIFFERENT major needs it
- [ ] minor course w/ prereq not in plan gets its own new semester (music + technical sales → PHYS 1202/2112/2113/2002 alone, 14 semesters lol)
- [ ] evening trial makes semesters too light (9, 7 hrs) → only keep it if nothing under 12
- [ ] end sequence leaves a hole + overloads the end (english cw + honors research: sem 1 18 → 9, last 2 are 20) → refill after
- [ ] compact stacks HNRS 1010 x3 in one semester (music + LASAL)
- [ ] sequence slots get squashed (foreign language 1st + 2nd in same sem, applied music piles up at the end)
- [ ] shrunk slot label shows old hrs: "Approved Electives (12)" at 6 hr (slot_base strips the NEW credits) + credits saved as "6.0"
- [ ] audit crashes (500) on prior like "AP CALC" or "MATH1550" w/ an hours_in minor → check prior against course list + show which ones didnt match

## rules / audit
- [ ] or(False, ?) = False → "X or consent" blocks when X missing (733 prereqs, 136 false alarms). should be ?
- [ ] and(True, ?) = True → minor says "complete" when part needs advisor (65 minors)
- [ ] audit "unknown" slots take any course → tech electives ✓ w/ random leftovers. should be ?
- [ ] audit ignores slot hrs → says "below full-time" for semesters w/ unfilled slots
- [ ] hrs rules dont match: courses use max, slots use min, audit uses min (EDCI 4006 "3, 9" = 9 in builder)
- [ ] fits() + slots_accept() r the same thing twice → fits lets a lecture fill a lab slot. merge them
- [ ] minor_courses hours_from counts planned courses below min_level, courses_from ignores min_level
- [ ] "or higher" prereqs (PHYS 2001 wants MATH 1022 but plan has MATH 1550) → 135 prereq problems. maybe a "satisfies" map
- [ ] 13 prereq order problems r from the catalog itself (EDCI 3702, TAM 3032...) not us
- [ ] degree groups only show first course, no ⇄ menu (39 groups). also what does group even mean (pick 1 or more?)
- [ ] dangling "or" makes recommended_plan skip the next slot (english cw pre-law sem 4)
- [ ] 3000/4000 lvl courses in sem 1 (IE 3201, BLAW 3201) → maybe EARLIEST by level?
- [ ] if HNRS 1010 already planned once, minor adds 0 more instead of the rest
- [ ] audit counts repeated courses only once / no repeat limits (HNRS 1010 x3)
- [ ] audit warning when a dragged course breaks EARLIEST
- [ ] (maybe) rebalance could split a lecture + lab coreq

## builder
- [ ] shrunkSlot restore breaks if that slot was replaced or the chip got moved first
- [ ] dragged never resets → dragging text/a file onto a semester moves the last chip again
- [ ] putting a chip back in palette un-grays it even if another copy is still in the plan
- [ ] dropping a course on any slot replaces it even if wrong kind (ENGL on a lab slot)
- [ ] removing a minor course the server placed doesnt bring its slot back
- [ ] swapping a choice doesnt check prereqs/EARLIEST
- [ ] no way back from audit page → edits gone
- [ ] page is 2.7 MB / ~8,700 chips (all electives renders everything) → this is why its slow. lazy load + debounce search
- [ ] add <!doctype html> + <meta charset="utf-8"> to both templates

## parser investigating....
- [ ] liberal arts religious studies "(now under philosophy)" + semester 1 only 6 hrs
- [ ] coastal env sci & research (14258): total_hours None + env health notes leak in
- [ ] Joint 3/2 Art and Design title ends in "MDMAE." + total_hours is None
- [ ] footnote elective lists ("see below") not captured
- [ ] "Approved Technical Elective" etc. are kind "other" (list lives in footnote)
- [ ] english creative writing pre-law semester 4 (12 dangling "or"s)
- [ ] ag business "see options below"
- [ ] oral & written communication 1/2 slots
- [ ] foreign language sections
- [ ] combined footnotes not split ("3,5", "1,2", "*") → 33 dont resolve. 3 ate the "or" (ECON 2010, BIOL 1208, ACCT 2101)
- [ ] slot credits from last "(" → 42 junk ones ("also counts as DMAE elective", "1 each")
- [ ] 25 tracks total_hours None, 15 where semester sums ≠ total (fire & emergency 60 vs 120, pre-vet 90 vs 134)
- [ ] 11 codes in degrees dont exist in courses (CHEM 3571 x15, EE 1820) → count as 0 hr
- [ ] 6 slots missing "group", 6 empty semesters (coastal 3+2/3+3)
- [ ] plant & soil systems is in there 3 times (14248/14249/14400)
- [ ] prereq text cuts off at the first link → 11 prereqs + 3 coreqs chopped, 20 descriptions start w/ the leaked code (MUS 1132)
- [ ] coreq text (69 courses) never turned into rules
- [ ] bad codes in prereq rules ("DVM" in 7 VCS courses, "LSU" in PSYC 2999, CONE 1112, FESA 2117, ART 2271)
- [ ] MUS 1740 requires itself 💀
- [ ] 15 llm rules (+3 regex) dropped a code (MKT 3427/4423 lost MKT 3401)
- [ ] title/credits regex: 4 pages dropped (lowercase "Law 5776", slash codes), junk credits from titles (MUS 4224), 211 weird credits ("1-12 per sem."), 224 missing (mostly LAW), HIST 2190 typo
- [ ] 111 codes have 2 pages + random one wins (VMED 5256 empty vs full) → pick the fuller one
- [ ] courses w/ repeat info only in desc have empty repeatable (FIN 4845 + 5 more)
- [ ] gen eds: CHEM 1101, CHEM 1102, GEOL 1012 not in courses + hrs r strings
- [ ] minors: 18 fake codes (CPLT 4500-4800, TAM 1071, CONE 4221 shows up as a 0 hr chip...)
- [ ] minor 14192 lists 28 courses below its own min_level → filter w/ meets_level in minor_alternatives too
- [ ] minor total_hours: 42 None, 8+ wrong (animal sciences 2 → 19, LASAL 3 → 21, criminology 6)
- [ ] coach education wants 18 hrs from 4 courses that cant add up to 18
- [ ] honors minor rules lost "3 hrs of HNRS 1010" (llm source) → patched w/ REPEAT_TIMES but data still wrong

## pipeline
- [ ] cant rerun it as is → scripts point at old folders (pages/, programs/, courses/coursesfinal.json). use 1 base folder
- [ ] programrequester uses a real browser (seleniumbase) → make sure its NOT getting around lsu's bot check. if plain requests got blocked thats them saying no
- [ ] courses wait 0.5s + retry forever → 1-2s, backoff, retry cap
- [ ] programrequester catches the wrong error, prereqtalker no try around ollama, minortalker bare except (eats ctrl-c)
- [ ] talkers save straight over the file → crash mid-save = broken json. temp file then rename
- [ ] minorchecker deletes rules in place (no undo)
- [ ] no check that llm output only uses known node types
- [ ] coursemerger has a hardcoded reject list w/ no reasons → move to manual fixes w/ notes
- [ ] both requesters overwrite bad.html
- [ ] write down what order the scripts run in

## cleanup
- [ ] COMMIT (8 files uncommitted rn)
- [ ] __pycache__ .pyc files r tracked → add __pycache__/ to .gitignore + untrack
- [ ] data/ paths break if u run from another folder
- [ ] delete print(len(degrees)) + print(len(REPEATABLE))
- [ ] slotkinds.py does "from rules import" (breaks) → move slotkinds + testrules to scratch/
- [ ] unused slot_groups hours in app.py + unused imports in requesters
- [ ] old json (courses.json, courseswithrules.json, minors.json) sitting next to the final ones
- [ ] debug=True is fine locally just never deploy w/ it
- [ ] make a check script that runs every track + random combos: no crash, every sem 12-19, nothing required missing, no course twice in 1 sem, adding a minor never lowers the total

---

## small
- [x] remove hrs from sidebar titles
- [x] strip * in kinesiology
- [x] LSU is in some program titles so i need 2 fix that
- [x] slot titles have no more :
- [x] make sure critical lines dont show in sidebar
- [x] get rid of non undergrad (bachelor's only filter)
- [x] BS/BA → B.S./B.A. in titles + track names (Economics, Accounting)
- [x] track_label helper + exact match (Analytics, Merchandising were hidden)
- [x] hide plan textarea
- [x] clean up " ;" in critical lines
- [x] "[2000-Level]" vs "[2000-level]" slot labels
- [x] hours shown on every chip (· 3 hr), slots match courses
- [x] Math B.S. plan totals 122 but catalog says 120 (compare semester hours)
- [x] natural sciences lab (2-1) wrong footnote (catalog typo → FOOTNOTE_FIXES)

## parser (done)
- [x] cardiopulmonary science track called "art history" ??? (per-file reset)
- [x] duplicate coastal programs (skip 14259, fix "CES." title)
- [x] duplicate i.s.a. entry (was the Analytics track)

## features
- [x] major info box on each program's page in builder
- [x] either/or courses on chips (+ picker menu + footnote hover)
- [x] elective slots shrink as filled
- [x] live hours
- [x] rebalance overloaded semesters after merging majors
- [x] absorb elective/gen ed slots across majors (CS+Math 192 → 151)
- [x] prior credit removes courses + fills slots
- [x] compact light semesters (target 15)
- [x] EARLIEST rule (HNRS 1010 not in semester 1)
- [x] HNRS 3800/3900/4000 in last three semesters
- [x] repeatable courses can be dragged more than once (↻ in sidebar)
- [x] honors/LASAL minors place HNRS 1010 three times (REPEAT_TIMES)
- [x] even out semester loads (2nd rebalance on a trial copy)
- [x] drop choice chips covered by another major
- [x] minor picks get either/or options (minor_alternatives)
- [x] math minor chain starts early + separate semesters (make room + prereq-safe rebalance)