package com.appfantacalcio.vote;

import com.appfantacalcio.competition.Competition;
import com.appfantacalcio.competition.CompetitionRepository;
import com.appfantacalcio.competition.CompetitionType;
import com.appfantacalcio.formation.Formation;
import com.appfantacalcio.formation.FormationRepository;
import com.appfantacalcio.player.Player;
import com.appfantacalcio.standings.Standings;
import com.appfantacalcio.standings.StandingsRepository;
import com.appfantacalcio.team.Team;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class VoteService {

	private final VoteRepository voteRepository;
	private final FormationRepository formationRepository;
	private final CompetitionRepository competitionRepository;
	private final StandingsRepository standingsRepository;

	// Punti Formula 1: 1°=25, 2°=18, 3°=15, 4°=12, 5°=10, 6°=8, 7°=6, 8°=4, 9°=2,
	// 10°=1
	private static final int[] F1_POINTS = { 25, 18, 15, 12, 10, 8, 6, 4, 2, 1 };

	@Transactional(readOnly = true)
	public Integer getMaxMatchDay() {
		return voteRepository.findMaxMatchDay();
	}

	@Transactional
	public void calculateMatchDay(Integer matchDay, UUID competitionId) {
		// 1. Recupera le competizioni da calcolare
		List<Competition> competitions;
		if (competitionId != null) {
			competitions = competitionRepository.findById(competitionId)
					.map(List::of)
					.orElseThrow(() -> new RuntimeException("Competition not found: " + competitionId));
		} else {
			competitions = competitionRepository.findAll();
		}

		for (Competition competition : competitions) {
			if (competition.getType() == CompetitionType.FORMULA_1) {
				calculateFormula1Standings(competition, matchDay);
			}
			// TODO: Altri tipi
		}
	}

	@Transactional
	public void calculateMatchDay(Integer matchDay) {
		calculateMatchDay(matchDay, null);
	}

	private void calculateFormula1Standings(Competition competition, Integer matchDay) {
		// Verifica se la giornata rientra nel range della competizione
		if (matchDay < competition.getStartDay() || matchDay > competition.getEndDay()) {
			return;
		}

		List<TeamScore> teamScores = new ArrayList<>();

		// Calcola il punteggio per ogni squadra partecipante
		for (Team team : competition.getParticipants()) {
			double score = calculateTeamScore(team, matchDay);
			teamScores.add(new TeamScore(team, score));
		}

		// Ordina le squadre per punteggio decrescente
		teamScores.sort((a, b) -> Double.compare(b.score, a.score));

		// Assegna i punti F1 e aggiorna la classifica
		for (int i = 0; i < teamScores.size(); i++) {
			TeamScore ts = teamScores.get(i);
			int points = (i < F1_POINTS.length) ? F1_POINTS[i] : 0;

			updateStandings(competition, ts.team, points, ts.score);
		}
	}

	private double calculateTeamScore(Team team, Integer matchDay) {
		Optional<Formation> formationOpt = formationRepository.findByTeamAndMatchDay(team, matchDay);

		if (formationOpt.isEmpty()) {
			return 0.0; // Nessuna formazione schierata
		}

		Formation formation = formationOpt.get();
		double totalScore = 0.0;
		int playersCount = 0;

		// Calcola punteggio titolari
		List<Player> starters = new ArrayList<>();
		if (formation.getGoalkeeper() != null)
			starters.add(formation.getGoalkeeper());
		starters.addAll(formation.getDefenders());
		starters.addAll(formation.getMidfielders());
		starters.addAll(formation.getForwards());

		// Mappa per tenere traccia dei ruoli che necessitano sostituzione
		// Semplificazione: in questa prima versione non gestiamo le sostituzioni
		// complesse
		// Si assume che se un titolare non gioca, entra il primo panchinaro disponibile
		// dello stesso ruolo

		for (Player player : starters) {
			Optional<Vote> voteOpt = voteRepository.findByPlayerAndMatchDay(player, matchDay);
			if (voteOpt.isPresent() && voteOpt.get().getFantaVote() != null) {
				totalScore += voteOpt.get().getFantaVote();
				playersCount++;
			} else {
				// Tenta sostituzione dalla panchina
				double subScore = findSubstituteScore(formation.getBench(), player.getRole(), matchDay);
				if (subScore > 0) {
					totalScore += subScore;
					playersCount++;
				}
			}
		}

		// Malus se si gioca in inferiorità numerica (opzionale, da configurare)

		return totalScore;
	}

	private double findSubstituteScore(List<Player> bench, String role, Integer matchDay) {
		// Cerca il primo panchinaro del ruolo richiesto che ha preso voto
		// Nota: La lista bench dovrebbe essere ordinata per ordine di inserimento
		// (priorità)

		for (Player substitute : bench) {
			if (substitute.getRole().equals(role)) {
				// Verifica se questo panchinaro è già stato usato?
				// Per semplicità qui non teniamo traccia dello stato dei panchinari tra le
				// chiamate
				// In una implementazione reale servirebbe un contesto per tracciare i sostituti
				// usati

				Optional<Vote> voteOpt = voteRepository.findByPlayerAndMatchDay(substitute, matchDay);
				if (voteOpt.isPresent() && voteOpt.get().getFantaVote() != null) {
					return voteOpt.get().getFantaVote();
				}
			}
		}
		return 0.0;
	}

	private void updateStandings(Competition competition, Team team, int pointsToAdd, double fantaPointsToAdd) {
		Standings standings = standingsRepository.findByCompetitionAndTeam(competition, team)
				.orElseThrow(() -> new RuntimeException("Standings not found for team " + team.getId()));

		standings.setPoints(standings.getPoints() + pointsToAdd);
		standings.setFantaPoints(standings.getFantaPoints() + fantaPointsToAdd);
		standings.setPlayed(standings.getPlayed() + 1);

		// Per la Formula 1 non usiamo won/drawn/lost/goals nel senso calcistico
		// tradizionale
		// Ma potremmo usarli per statistiche diverse se necessario

		standingsRepository.save(standings);
	}

	private static class TeamScore {
		Team team;
		double score;

		TeamScore(Team team, double score) {
			this.team = team;
			this.score = score;
		}
	}
}
