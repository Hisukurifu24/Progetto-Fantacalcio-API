package com.appfantacalcio.competition;

import java.util.UUID;

import org.springframework.data.jpa.repository.JpaRepository;

public interface CompetitionRepository
		extends JpaRepository<Competition, UUID> {
}
