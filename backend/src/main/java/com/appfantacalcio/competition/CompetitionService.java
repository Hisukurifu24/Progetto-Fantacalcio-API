package com.appfantacalcio.competition;

import java.util.List;
import java.util.UUID;

import org.springframework.stereotype.Service;

import com.appfantacalcio.competition.dto.CreateCompetitionRequest;
import com.appfantacalcio.league.League;
import com.appfantacalcio.league.LeagueRepository;
import com.appfantacalcio.match.Match;
import com.appfantacalcio.match.MatchRepository;
import com.appfantacalcio.team.Team;
import com.appfantacalcio.team.TeamRepository;

import org.springframework.transaction.annotation.Transactional;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class CompetitionService {

	private final LeagueRepository leagueRepo;
	private final CompetitionRepository competitionRepo;
	private final TeamRepository teamRepo;
	private final MatchRepository matchRepo;

	@Transactional
	public Competition create(UUID leagueId, CreateCompetitionRequest req) {
		League league = leagueRepo.findById(leagueId)
				.orElseThrow();

		Competition c = new Competition();
		c.setLeague(league);
		c.setType(req.type());
		c.setStartDay(req.startDay());
		c.setEndDay(req.endDay());

		return competitionRepo.save(c);
	}

	@Transactional
	public void generateCalendar(UUID competitionId) {
		Competition c = competitionRepo.findById(competitionId)
				.orElseThrow();

		List<Team> teams = teamRepo.findByLeagueId(c.getLeague().getId());

		if (teams.size() < 2)
			throw new IllegalStateException("Not enough teams");

		matchRepo.deleteAll(
				matchRepo.findByCompetitionIdOrderByMatchDay(competitionId));

		List<Match> matches = RoundRobinGenerator.generate(teams, c);

		matchRepo.saveAll(matches);
	}

	@Transactional(readOnly = true)
	public List<Match> calendar(UUID competitionId) {
		return matchRepo
				.findByCompetitionIdOrderByMatchDay(competitionId);
	}

	public void delete(UUID id) {
		competitionRepo.deleteById(id);
	}
}
