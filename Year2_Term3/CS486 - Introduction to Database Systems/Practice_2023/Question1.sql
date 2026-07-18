-- **Question 1 (Data Integrity)**
-- Some rows in `MatchPlayer` contain invalid `Role` values (i.e., values outside
-- `'Support', 'Carry', 'Mid', 'Offlane', 'Hard Support'`). Write a statement to
-- correct all such rows by setting `Role = 'Support'`. Then add a `CHECK`
-- constraint named `CHK_MatchPlayer_Role` so that only the five valid role
-- values can be inserted going forward.
update MatchPlayer
set Role = 'Support' where Role not in ('Support', 'Carry', 'Mid', 'Offlane', 'Hard Support')
ALTER TABLE MatchPlayer
add constraint CHK_MatchPlayer_Role CHECK(Role IN ('Support', 'Carry', 'Mid', 'Offlane', 'Hard Support'))