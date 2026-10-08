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
- [x] "[2000-Level]" vs "[2000-level]" slot labels (lowercase in slot_base?)
- [ ] Joint 3/2 Art and Design title ends in "MDMAE." + total_hours is None

## parser investigating....
- [x] cardiopulmonary science track called "art history" ??? (per-file reset)
- [x] duplicate coastal programs (skip 14259, fix "CES." title)
- [x] duplicate i.s.a. entry (was the Analytics track)
- [ ] liberal arts religious studies "(now under philosophy)" + semester 1 only 6 hrs
- [ ] coastal env sci & research (14258): total_hours None + env health notes leak in
- [ ] footnote elective lists ("see below") not captured
- [ ] english creative writing pre-law semester 4
- [ ] ag business "see options below"
- [ ] oral & written communication 1/2 slots
- [ ] foreign language sections

## features
- [x] major info box on each program's page in builder
- [x] either/or courses on chips
- [x] elective slots shrink as filled
- [x] live hours
- [ ] rebalance overloaded semesters after merging majors
- [ ] merging: if a choice chip's option is required by another major, switch to it
- [ ] minor picks don't get either/or options
- [ ] shrunkSlot restore breaks if that slot was later replaced