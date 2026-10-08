# TODO

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
- [ ] Joint 3/2 Art and Design title ends in "MDMAE." + total_hours is None
- [x] Math B.S. plan totals 122 but catalog says 120 (compare semester hours)

## parser investigating....
- [x] cardiopulmonary science track called "art history" ??? (per-file reset)
- [x] duplicate coastal programs (skip 14259, fix "CES." title)
- [x] duplicate i.s.a. entry (was the Analytics track)
- [ ] liberal arts religious studies "(now under philosophy)" + semester 1 only 6 hrs
- [ ] coastal env sci & research (14258): total_hours None + env health notes leak in
- [ ] footnote elective lists ("see below") not captured
- [ ] "Approved Technical Elective" etc. are kind "other" (list lives in footnote)
- [ ] honors minor rules lost "3 hrs of HNRS 1010" (llm source) → patched with REPEAT_TIMES
- [ ] english creative writing pre-law semester 4
- [ ] ag business "see options below"
- [ ] oral & written communication 1/2 slots
- [ ] foreign language sections
- [ ] courses w/ repeat info only in desc have empty repeatable 

## features
- [x] major info box on each program's page in builder
- [x] either/or courses on chips
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
- [ ] end sequence can push last semester over 19 → move a slot earlier
- [ ] audit warning when a dragged course breaks EARLIEST
- [ ] audit counts repeated courses only once / no repeat limits (HNRS 1010 x3)
- [ ] merging: if a choice chip's option is required by another major, switch to it
- [ ] minor picks don't get either/or options
- [ ] shrunkSlot restore breaks if that slot was later replaced