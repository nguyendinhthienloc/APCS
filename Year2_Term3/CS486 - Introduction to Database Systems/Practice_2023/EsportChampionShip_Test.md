# CS486 — Database Systems Practice Test
### Schema: EsportChampionShip
**TEST CODE: 01**

**Instructions:** Run `EsportChampionShip_Schema.sql` first to create and seed the
database. Then write a single T-SQL statement (or script) for each question below.

**Tables available:**
- `Team(TeamID, TeamName)`
- `Player(PlayerID, Nickname, TeamID)`
- `Match(MatchID, Date, Team1ID, Team2ID, ScoreTeam1, ScoreTeam2)`
- `MatchPlayer(MatchID, PlayerID, Role, Kills, Deaths, Assists)`

---

### **Question 1 (0.5)**
Given that the tables have already been successfully created, add a constraint named `CHK_MatchPlayer_Role` to the `MatchPlayer` table to ensure that the `Role` column only contains one of the following values: 'Support', 'Carry', 'Mid', 'Offlane', or 'Hard Support'.

**Note:** Do not modify the original database creation script.

---

### **Question 2 (1.0)**
List the nicknames of players who played against team 'Vikings' in a match on May 24, 2025.

---

### **Question 3 (1.0)**
List the player(s) who have never played any role other than 'Support' or 'Hard Support'. Return the `TeamID`, `PlayerID`, and `Nickname` of those player(s).

---

### **Question 4 (1.5)**
For each player who has taken the role 'Support', list their `PlayerID`, `Nickname`, and total number of assists — but only include those whose total assists are at least 30.

---

### **Question 5 (2.0)**
For each match, find the player(s) with the highest total kills. Return all players in case of a tie. Show: `MatchID`, `PlayerID`, `Nickname`.

---

### **Question 6 (2.0)**
Create a table named `PlayerTotalKills(PlayerID, Nickname, TotalKills)` with an appropriate schema.
- Use suitable data types for each column.
- Set `PlayerID` as the primary key and define a foreign key constraint referencing the `Player` table.
- Then, insert data into this table using existing data from the database. Only include players with more than 30 total kills.

---

### **Question 7 (2.0)**
*(CTE is allowed for this question)* Find the team(s) with the lowest number of wins.

A win is counted when a team's score is higher than its opponent's in a match.
If multiple teams are tied for the lowest number of wins, include all of them.

Return the following information: `TeamID`, `TeamName`, and the total number of wins.
