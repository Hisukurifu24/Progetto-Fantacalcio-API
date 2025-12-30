package com.appfantacalcio.match;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

public interface MatchRepository
		extends JpaRepository<Match, UUID> {

	List<Match> findByCompetitionIdOrderByMatchDay(UUID competitionId);
}
