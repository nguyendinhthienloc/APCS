--23125015
--Ly Hoang Nhut
--01
--E5

use EsportChampionShip
go

--1
select distinct Role, MatchID, PlayerID
from MatchPlayer
where Role not in('Support', 'Carry', 'Mid', 'Offlane', 'Hard Support')

update MatchPlayer
set Role = 'Carry'
where Role = 'Blaster'

update MatchPlayer
set Role = 'Offlane'
where Role = 'Commander'

update MatchPlayer
set Role = 'Hard Support'
where Role = 'Tank'

update MatchPlayer
set Role = 'Hard Support'
where Role = 'Guard'

alter table MatchPlayer
add constraint CHK_MatchPlayer_Role check (Role IN ('Support', 'Carry', 'Mid', 'Offlane', 'Hard Support'))

--2
select p.TeamID, p.Nickname
from Match m
join Team t on t.TeamID = m.Team1ID
join Player p on p.TeamID = t.TeamID
join Team t2 on t2.TeamID = m.Team2ID
where t2.TeamName = 'Vikings' and m.Date = '2025-05-24'

union

select p.TeamID, p.Nickname
from Match m
join Team t on t.TeamID = m.Team2ID
join Player p on p.TeamID = t.TeamID
join Team t1 on t1.TeamID = m.Team1ID
where t1.TeamName = 'Vikings' and m.Date = '2025-05-24'

--3
select t.TeamID, p.PlayerID, p.Nickname
from Player p
join Team t on t.TeamID = p.TeamID
where not exists(
	select 1
	from Match m
	join MatchPlayer mp on mp.MatchID = m.MatchID and mp.PlayerID = p.PlayerID
	where mp.Role not in('Support', 'Hard Support')
)

--4
select p.PlayerID, p.Nickname, sum(mp.Assists) as TotalAssists
from Match m
join MatchPlayer mp on mp.MatchID = m.MatchID
join Player p on p.PlayerID = mp.PlayerID
where mp.Role = 'Support'
group by p.PlayerID, p.Nickname
having sum(mp.Assists) >= 30

--5
select m.MatchID, p.PlayerID, p.Nickname
from Match m
join MatchPlayer mp on mp.MatchID = m.MatchID
join Player p on p.PlayerID = mp.PlayerID
where mp.Kills = (
	select max(Kills)
	from MatchPlayer mp1
	where mp1.MatchID = m.MatchID
)

--6
create table PlayerTotalKills(
	PlayerID int identity(1,1) primary key,
	NickName varchar(50) unique,
	TotalKills int default 0 check (TotalKills >= 0)
	foreign key (PlayerID) references Player(PlayerID)
)

insert into PlayerTotalKills(PlayerID, NickName, TotalKills)
select p.PlayerID, p.Nickname, count(mp.Kills) as TotalKills
from Match m
join MatchPlayer mp on mp.MatchID = m.MatchID
join Player p on p.PlayerID = mp.PlayerID
group by p.PlayerID, p.Nickname
having count(mp.Kills) > 30;

--7
with TeamWins (TeamID, NbWins) as (
	select m.Team1ID as TeamID, count(m.MatchID) as NbWins
	from Match m
	where m.ScoreTeam1 > m.ScoreTeam2
	group by m.Team1ID

	union

	select m.Team2ID as TeamID, count(m.MatchID) as NbWins
	from Match m
	where m.ScoreTeam1 < m.ScoreTeam2
	group by m.Team2ID
),

AllTeamAndTheirWinnings (TeamID, TeamName, NbWins) as (
	select
        t.TeamID,
        t.TeamName,
        ISNULL(tw.NbWins, 0) as TotalWins
    from Team t
    left join TeamWins tw on t.TeamID = tw.TeamID
)

select t.TeamID, t.TeamName, tw.NbWins
from AllTeamAndTheirWinnings tw
right join Team t on t.TeamID = tw.TeamID
where not exists(
	select 1
	from AllTeamAndTheirWinnings tw1
	where tw1.NbWins < tw.NbWins
)
