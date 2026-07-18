select team.TeamID, playerID, nickname
from team join player on team.TeamID = player.PlayerID
where playerID not in (
    select m.playerID 
    from MatchPlayer m 
    where m.role NOT IN ('Support', 'Hard Support')
    and m.role is not null
)