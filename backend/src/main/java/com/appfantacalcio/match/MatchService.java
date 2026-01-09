package com.appfantacalcio.match;

import com.appfantacalcio.competition.Competition;
import com.appfantacalcio.competition.CompetitionRepository;
import com.appfantacalcio.exception.ResourceNotFoundException;
import com.appfantacalcio.formation.Formation;
import com.appfantacalcio.formation.FormationRepository;
import com.appfantacalcio.team.Team;
import com.appfantacalcio.team.TeamRepository;
import com.appfantacalcio.vote.Vote;
import com.appfantacalcio.vote.VoteRepository;
import com.appfantacalcio.player.Player;

import org.springframework.transaction.annotation.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;
import java.util.Map;
import java.util.HashMap;
import java.util.ArrayList;
import java.util.Optional;
import java.util.Comparator;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class MatchService {

    private final MatchRepository matchRepository;
    private final CompetitionRepository competitionRepository;
    private final FormationRepository formationRepository;
    private final VoteRepository voteRepository;
    private final TeamRepository teamRepository;

    @Transactional(readOnly = true)
    public List<Match> getAllMatches() {
        return matchRepository.findAll();
    }

    @Transactional(readOnly = true)
    public Match getMatchById(UUID id) {
        return matchRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Match not found with id: " + id));
    }

    @Transactional
    public Match createMatch(Match match) {
        // Additional validation or logic can be added here if needed
        return matchRepository.save(match);
    }

    @Transactional
    public Match updateMatch(UUID id, Match updatedMatch) {
        Match existingMatch = matchRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Match not found with id: " + id));

        // Update fields as necessary
        existingMatch.setMatchDay(updatedMatch.getMatchDay());
        existingMatch.setHomeTeam(updatedMatch.getHomeTeam());
        existingMatch.setAwayTeam(updatedMatch.getAwayTeam());
        existingMatch.setHomeGoals(updatedMatch.getHomeGoals());
        existingMatch.setAwayGoals(updatedMatch.getAwayGoals());
        existingMatch.setPlayed(updatedMatch.isPlayed());
        // Set competition if provided and exists
        if (updatedMatch.getCompetition() != null && updatedMatch.getCompetition().getId() != null) {
            Competition competition = competitionRepository.findById(updatedMatch.getCompetition().getId())
                    .orElseThrow(() -> new ResourceNotFoundException(
                            "Competition not found with id: " + updatedMatch.getCompetition().getId()));
            existingMatch.setCompetition(competition);
        }

        return matchRepository.save(existingMatch);
    }

    @Transactional
    public void deleteMatch(UUID id) {
        matchRepository.deleteById(id);
    }

    @Transactional(readOnly = true)
    public List<Match> getMatchesByCompetitionId(UUID competitionId) {
        return matchRepository.findByCompetitionIdOrderByMatchDay(competitionId);
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getLiveMatch(UUID competitionId, String username) {
        Competition competition = competitionRepository.findById(competitionId)
                .orElseThrow(() -> new ResourceNotFoundException("Competition not found with id: " + competitionId));

        List<Team> teams = teamRepository.findByLeagueId(competition.getLeague().getId());
        Team userTeam = teams.stream()
                .filter(t -> t.getOwner().getUsername().equals(username))
                .findFirst()
                .orElseThrow(() -> new ResourceNotFoundException("User team not found in this competition"));

        List<Match> matches = matchRepository.findByCompetitionIdOrderByMatchDay(competitionId);

        List<Match> myMatches = matches.stream()
                .filter(m -> ((m.getHomeTeam() != null && m.getHomeTeam().getId().equals(userTeam.getId())) ||
                        (m.getAwayTeam() != null && m.getAwayTeam().getId().equals(userTeam.getId()))))
                .collect(Collectors.toList());

        Match activeMatch = myMatches.stream()
                .filter(m -> !m.isPlayed())
                .findFirst()
                .orElse(null);

        if (activeMatch == null && !myMatches.isEmpty()) {
            activeMatch = myMatches.get(myMatches.size() - 1);
        }

        if (activeMatch == null) {
            throw new ResourceNotFoundException("No match found for user team");
        }

        Map<String, Object> response = new HashMap<>();
        response.put("homeTeamName", activeMatch.getHomeTeam() != null ? activeMatch.getHomeTeam().getName() : "N/A");
        response.put("awayTeamName", activeMatch.getAwayTeam() != null ? activeMatch.getAwayTeam().getName() : "N/A");

        Optional<Formation> homeFormationOpt = activeMatch.getHomeTeam() != null
                ? formationRepository.findByTeamAndMatchDay(activeMatch.getHomeTeam(), activeMatch.getMatchDay())
                : Optional.empty();
        Optional<Formation> awayFormationOpt = activeMatch.getAwayTeam() != null
                ? formationRepository.findByTeamAndMatchDay(activeMatch.getAwayTeam(), activeMatch.getMatchDay())
                : Optional.empty();

        List<Vote> votes = voteRepository.findByMatchDay(activeMatch.getMatchDay());
        Map<UUID, Vote> voteMap = votes.stream().collect(Collectors.toMap(v -> v.getPlayer().getId(), v -> v));

        List<Map<String, Object>> homePlayers = new ArrayList<>();
        List<Map<String, Object>> homeBench = new ArrayList<>();
        double homeScore = 0.0;

        if (homeFormationOpt.isPresent()) {
            Formation f = homeFormationOpt.get();
            if (f.getGoalkeeper() != null)
                homePlayers.add(createPlayerMapFromEntity(f.getGoalkeeper(), "P", voteMap));
            f.getDefenders().forEach(p -> homePlayers.add(createPlayerMapFromEntity(p, "D", voteMap)));
            f.getMidfielders().forEach(p -> homePlayers.add(createPlayerMapFromEntity(p, "C", voteMap)));
            f.getForwards().forEach(p -> homePlayers.add(createPlayerMapFromEntity(p, "A", voteMap)));

            if (f.getBench() != null) {
                f.getBench().forEach(p -> homeBench.add(createPlayerMapFromEntity(p, p.getRole().toString(), voteMap)));
            }

            homeScore = homePlayers.stream()
                    .mapToDouble(p -> (Double) p.getOrDefault("fantaVote", 0.0))
                    .sum();
        }

        List<Map<String, Object>> awayPlayers = new ArrayList<>();
        List<Map<String, Object>> awayBench = new ArrayList<>();
        double awayScore = 0.0;

        if (awayFormationOpt.isPresent()) {
            Formation f = awayFormationOpt.get();
            if (f.getGoalkeeper() != null)
                awayPlayers.add(createPlayerMapFromEntity(f.getGoalkeeper(), "P", voteMap));
            f.getDefenders().forEach(p -> awayPlayers.add(createPlayerMapFromEntity(p, "D", voteMap)));
            f.getMidfielders().forEach(p -> awayPlayers.add(createPlayerMapFromEntity(p, "C", voteMap)));
            f.getForwards().forEach(p -> awayPlayers.add(createPlayerMapFromEntity(p, "A", voteMap)));

            if (f.getBench() != null) {
                f.getBench().forEach(p -> awayBench.add(createPlayerMapFromEntity(p, p.getRole().toString(), voteMap)));
            }

            awayScore = awayPlayers.stream()
                    .mapToDouble(p -> (Double) p.getOrDefault("fantaVote", 0.0))
                    .sum();
        }

        response.put("homeScore", homeScore);
        response.put("awayScore", awayScore);
        response.put("homePlayers", homePlayers);
        response.put("homeBench", homeBench);
        response.put("awayPlayers", awayPlayers);
        response.put("awayBench", awayBench);

        return response;
    }

    private Map<String, Object> createPlayerMapFromEntity(Player player, String role, Map<UUID, Vote> voteMap) {
        Map<String, Object> map = new HashMap<>();
        map.put("role", role);
        map.put("name", player.getName());

        Vote v = voteMap.get(player.getId());
        if (v != null) {
            map.put("vote", v.getVote());

            double bonus = (v.getGoalsScored() != null ? v.getGoalsScored() * 3.0 : 0) +
                    (v.getAssists() != null ? v.getAssists() * 1.0 : 0) +
                    (v.getPenaltiesSaved() != null ? v.getPenaltiesSaved() * 3.0 : 0);

            double malus = (v.getGoalsConceded() != null ? v.getGoalsConceded() * 1.0 : 0) +
                    (v.getYellowCards() != null ? v.getYellowCards() * 0.5 : 0) +
                    (v.getRedCards() != null ? v.getRedCards() * 1.0 : 0) +
                    (v.getPenaltiesMissed() != null ? v.getPenaltiesMissed() * 3.0 : 0) +
                    (v.getOwnGoals() != null ? v.getOwnGoals() * 2.0 : 0);

            map.put("bonus", bonus);
            map.put("malus", malus);
            map.put("isLive", true);

            double fantaVote = v.getFantaVote() != null ? v.getFantaVote() : (v.getVote() + bonus - malus);
            map.put("fantaVote", fantaVote);
        } else {
            map.put("vote", 0.0);
            map.put("bonus", 0.0);
            map.put("malus", 0.0);
            map.put("isLive", false);
            map.put("fantaVote", 0.0);
        }
        return map;
    }
}