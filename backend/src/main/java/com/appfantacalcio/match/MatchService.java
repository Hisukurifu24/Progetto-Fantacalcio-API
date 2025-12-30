package com.appfantacalcio.match;

import com.appfantacalcio.competition.Competition;
import com.appfantacalcio.competition.CompetitionRepository;
import com.appfantacalcio.exception.ResourceNotFoundException;
import org.springframework.transaction.annotation.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class MatchService {

    private final MatchRepository matchRepository;
    private final CompetitionRepository competitionRepository;

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
                    .orElseThrow(() -> new ResourceNotFoundException("Competition not found with id: " + updatedMatch.getCompetition().getId()));
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
}