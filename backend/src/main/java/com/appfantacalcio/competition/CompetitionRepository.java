package com.appfantacalcio.competition;

import java.util.List;
import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

public interface CompetitionRepository
		extends JpaRepository<Competition, UUID> {
	List<Competition> findByLeagueId(UUID leagueId);
}
