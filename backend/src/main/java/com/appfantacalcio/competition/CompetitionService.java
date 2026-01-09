package com.appfantacalcio.competition;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

import org.springframework.stereotype.Service;

import com.appfantacalcio.competition.dto.CreateCompetitionRequest;
import com.appfantacalcio.league.League;
import com.appfantacalcio.league.LeagueRepository;
import com.appfantacalcio.match.Match;
import com.appfantacalcio.match.MatchRepository;
import com.appfantacalcio.standings.Standings;
import com.appfantacalcio.standings.StandingsRepository;
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
	private final StandingsRepository standingsRepo;

	@Transactional
	public Competition create(UUID leagueId, CreateCompetitionRequest req) {
		League league = leagueRepo.findById(leagueId)
				.orElseThrow();

		Competition c = new Competition();
		c.setLeague(league);
		c.setName(req.name());
		c.setType(req.type());
		c.setStartDay(req.startDay());
		c.setEndDay(req.endDay());

		if (req.participantIds() != null && !req.participantIds().isEmpty()) {
			List<Team> participants = teamRepo.findAllById(req.participantIds());
			c.setParticipants(participants);
		}

		Competition savedCompetition = competitionRepo.save(c);

		// Initialize standings for each participant
		if (c.getParticipants() != null) {
			for (Team team : c.getParticipants()) {
				Standings s = new Standings();
				s.setCompetition(savedCompetition);
				s.setTeam(team);
				s.setPoints(0);
				s.setPlayed(0);
				s.setWon(0);
				s.setDrawn(0);
				s.setLost(0);
				s.setGoalsFor(0);
				s.setGoalsAgainst(0);
				s.setGoalDifference(0);
				s.setFantaPoints(0.0);
				standingsRepo.save(s);
			}
		}

		if (savedCompetition.getType() == CompetitionType.CHAMPIONSHIP) {
			generateChampionshipCalendar(savedCompetition);
		} else if (savedCompetition.getType() == CompetitionType.CUP) {
			generateCupBracket(savedCompetition, req.roundsHomeAway(), req.finalHomeAway(), req.randomBrackets());
		} else if (savedCompetition.getType() == CompetitionType.GROUP_CUP) {
			generateGroupCupStructure(savedCompetition, req);
		}

		return savedCompetition;
	}

	@Transactional(readOnly = true)
	public List<Competition> findByLeagueId(UUID leagueId) {
		return competitionRepo.findByLeagueId(leagueId);
	}

	@Transactional
	public void generateCalendar(UUID competitionId) {
		Competition c = competitionRepo.findById(competitionId)
				.orElseThrow();

		List<Team> teams = c.getParticipants();
		if (teams.isEmpty()) {
			teams = teamRepo.findByLeagueId(c.getLeague().getId());
		}

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

	@Transactional
	public void delete(UUID id) {
		try {
			Competition c = competitionRepo.findById(id).orElseThrow();
			competitionRepo.delete(c);
		} catch (Exception e) {
			e.printStackTrace();
			throw e;
		}
	}

	private void generateChampionshipCalendar(Competition c) {
		List<Team> teams = c.getParticipants();
		if (teams == null || teams.size() < 2) {
			return;
		}

		List<List<Match>> baseRounds = RoundRobinGenerator.generateRounds(teams);
		int numBaseRounds = baseRounds.size();

		List<Match> allMatches = new ArrayList<>();

		int start = c.getStartDay();
		int end = c.getEndDay();

		for (int day = start; day <= end; day++) {
			// Calculate which round in the cycle (0 to numBaseRounds - 1)
			int relativeDay = day - start;
			int roundIndex = relativeDay % numBaseRounds;
			int cycleIndex = relativeDay / numBaseRounds;

			List<Match> roundMatches = baseRounds.get(roundIndex);

			boolean swap = (cycleIndex % 2 != 0); // Swap on odd cycles (Return leg)

			for (Match baseMatch : roundMatches) {
				Match m = new Match();
				m.setCompetition(c);
				m.setMatchDay(day);
				if (swap) {
					m.setHomeTeam(baseMatch.getAwayTeam());
					m.setAwayTeam(baseMatch.getHomeTeam());
				} else {
					m.setHomeTeam(baseMatch.getHomeTeam());
					m.setAwayTeam(baseMatch.getAwayTeam());
				}
				allMatches.add(m);
			}
		}

		matchRepo.saveAll(allMatches);
	}

	private void generateCupBracket(Competition c, boolean roundsHomeAway, boolean finalHomeAway,
			boolean randomBrackets) {
		List<Team> teams = new ArrayList<>(c.getParticipants());
		if (teams.size() < 2)
			return;

		if (randomBrackets) {
			Collections.shuffle(teams);
		}

		int numTeams = teams.size();
		int numRounds = (int) (Math.log(numTeams) / Math.log(2));

		List<Match> allMatches = new ArrayList<>();
		int currentMatchDay = c.getStartDay();

		for (int r = 1; r <= numRounds; r++) {
			boolean isFinal = (r == numRounds);
			boolean isHomeAway = isFinal ? finalHomeAway : roundsHomeAway;
			int matchesInRound = numTeams / (int) Math.pow(2, r);

			String roundLabel = getRoundLabel(r, numRounds);

			// Leg 1
			for (int m = 0; m < matchesInRound; m++) {
				Match match = new Match();
				match.setCompetition(c);
				match.setMatchDay(currentMatchDay);
				match.setRoundNumber(r);
				match.setRoundLabel(roundLabel);
				match.setMatchNumber(m + 1);

				if (r == 1) {
					// First round: assign teams
					match.setHomeTeam(teams.get(m * 2));
					match.setAwayTeam(teams.get(m * 2 + 1));
				} else {
					// Future rounds: TBD (null)
					match.setHomeTeam(null);
					match.setAwayTeam(null);
				}
				allMatches.add(match);
			}
			currentMatchDay++;

			// Leg 2 (if applicable)
			if (isHomeAway) {
				for (int m = 0; m < matchesInRound; m++) {
					Match match = new Match();
					match.setCompetition(c);
					match.setMatchDay(currentMatchDay);
					match.setRoundNumber(r);
					match.setRoundLabel(roundLabel + " (Ritorno)");
					match.setMatchNumber(m + 1);

					if (r == 1) {
						// First round return: swap teams
						match.setHomeTeam(teams.get(m * 2 + 1));
						match.setAwayTeam(teams.get(m * 2));
					} else {
						match.setHomeTeam(null);
						match.setAwayTeam(null);
					}
					allMatches.add(match);
				}
				currentMatchDay++;
			}
		}

		matchRepo.saveAll(allMatches);
	}

	private void generateGroupCupStructure(Competition c, CreateCompetitionRequest req) {
		List<Team> teams = new ArrayList<>(c.getParticipants());
		if (req.randomGroups()) {
			Collections.shuffle(teams);
		}

		int numGroups = req.numGroups();
		int baseSize = teams.size() / numGroups;
		int remainder = teams.size() % numGroups;

		int currentTeamIdx = 0;
		List<Match> allMatches = new ArrayList<>();
		int maxMatchDay = c.getStartDay();

		for (int i = 0; i < numGroups; i++) {
			String groupName = "Girone " + (char) ('A' + i);
			int groupSize = baseSize + (i < remainder ? 1 : 0);

			List<Team> groupTeams = new ArrayList<>();
			for (int k = 0; k < groupSize; k++) {
				Team t = teams.get(currentTeamIdx++);
				groupTeams.add(t);

				Standings s = standingsRepo.findByCompetitionAndTeam(c, t).orElse(null);
				if (s != null) {
					s.setGroupName(groupName);
					standingsRepo.save(s);
				}
			}

			List<Match> groupMatches = generateGroupMatches(c, groupTeams, req.matchesPerTeam(), groupName);
			allMatches.addAll(groupMatches);

			for (Match m : groupMatches) {
				if (m.getMatchDay() > maxMatchDay) {
					maxMatchDay = m.getMatchDay();
				}
			}
		}

		matchRepo.saveAll(allMatches);

		int totalQualified = numGroups * req.teamsQualifyPerGroup();
		generateKnockoutBracketPlaceholder(c, totalQualified, maxMatchDay + 1, req.knockoutHomeAway(),
				req.finalGroupHomeAway());
	}

	private List<Match> generateGroupMatches(Competition c, List<Team> groupTeams, int matchesPerTeam,
			String groupName) {
		List<Match> matches = new ArrayList<>();
		int numTeams = groupTeams.size();
		if (numTeams < 2)
			return matches;

		List<Team> roundTeams = new ArrayList<>(groupTeams);
		if (numTeams % 2 != 0) {
			roundTeams.add(null); // Dummy team
			numTeams++;
		}

		int numRounds = numTeams - 1;
		int matchesPerRound = numTeams / 2;

		for (int r = 0; r < numRounds; r++) {
			int matchDay = c.getStartDay() + r;

			for (int m = 0; m < matchesPerRound; m++) {
				int homeIdx = (r + m) % (numTeams - 1);
				int awayIdx = (numTeams - 1 - m + r) % (numTeams - 1);

				if (m == 0) {
					awayIdx = numTeams - 1;
				}

				Team home = roundTeams.get(homeIdx);
				Team away = roundTeams.get(awayIdx);

				if (home != null && away != null) {
					Match match = new Match();
					match.setCompetition(c);
					match.setMatchDay(matchDay);
					match.setHomeTeam(home);
					match.setAwayTeam(away);
					match.setGroupName(groupName);
					match.setRoundLabel(groupName + " - Giornata " + (r + 1));
					matches.add(match);
				}
			}
		}

		// If matchesPerTeam > 1 (Return legs)
		if (matchesPerTeam > 1) {
			int currentMatchCount = matches.size();
			for (int i = 0; i < currentMatchCount; i++) {
				Match original = matches.get(i);
				Match returnMatch = new Match();
				returnMatch.setCompetition(c);
				returnMatch.setMatchDay(original.getMatchDay() + numRounds);
				returnMatch.setHomeTeam(original.getAwayTeam());
				returnMatch.setAwayTeam(original.getHomeTeam());
				returnMatch.setGroupName(groupName);
				returnMatch.setRoundLabel(
						groupName + " - Giornata " + (original.getMatchDay() - c.getStartDay() + 1 + numRounds));
				matches.add(returnMatch);
			}
		}

		return matches;
	}

	private void generateKnockoutBracketPlaceholder(Competition c, int numTeams, int startMatchDay,
			boolean roundsHomeAway, boolean finalHomeAway) {
		if (numTeams < 2)
			return;

		int numRounds = (int) (Math.log(numTeams) / Math.log(2));
		List<Match> allMatches = new ArrayList<>();
		int currentMatchDay = startMatchDay;

		for (int r = 1; r <= numRounds; r++) {
			boolean isFinal = (r == numRounds);
			boolean isHomeAway = isFinal ? finalHomeAway : roundsHomeAway;
			int matchesInRound = numTeams / (int) Math.pow(2, r);

			String roundLabel = getRoundLabel(r, numRounds);

			// Leg 1
			for (int m = 0; m < matchesInRound; m++) {
				Match match = new Match();
				match.setCompetition(c);
				match.setMatchDay(currentMatchDay);
				match.setRoundNumber(r);
				match.setRoundLabel(roundLabel);
				match.setMatchNumber(m + 1);
				match.setHomeTeam(null);
				match.setAwayTeam(null);
				allMatches.add(match);
			}
			currentMatchDay++;

			// Leg 2
			if (isHomeAway) {
				for (int m = 0; m < matchesInRound; m++) {
					Match match = new Match();
					match.setCompetition(c);
					match.setMatchDay(currentMatchDay);
					match.setRoundNumber(r);
					match.setRoundLabel(roundLabel + " (Ritorno)");
					match.setMatchNumber(m + 1);
					match.setHomeTeam(null);
					match.setAwayTeam(null);
					allMatches.add(match);
				}
				currentMatchDay++;
			}
		}
		matchRepo.saveAll(allMatches);
	}

	private String getRoundLabel(int round, int totalRounds) {
		int diff = totalRounds - round;
		switch (diff) {
			case 0:
				return "Finale";
			case 1:
				return "Semifinale";
			case 2:
				return "Quarti di Finale";
			case 3:
				return "Ottavi di Finale";
			case 4:
				return "Sedicesimi di Finale";
			default:
				return "Turno " + round;
		}
	}
}
