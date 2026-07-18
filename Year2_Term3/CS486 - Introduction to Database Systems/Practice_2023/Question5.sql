select m.MatchID, p.PlayerID, p.Nickname, mp.Kills
from Match m
join MatchPlayer mp on mp.MatchID = m.MatchID
join Player p on p.PlayerID = mp.PlayerID
where mp.Kills = (
    select max(mp2.Kills)
    from MatchPlayer mp2
    where mp2.MatchID = m.MatchID
    group by mp2.matchID
);