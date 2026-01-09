package com.appfantacalcio.standings;

import com.appfantacalcio.competition.Competition;
import com.appfantacalcio.team.Team;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface StandingsRepository extends JpaRepository<Standings, UUID> {
	List<Standings> findByCompetitionId(UUID competitionId);

	Optional<Standings> findByCompetitionAndTeam(Competition competition, Team team);
}
