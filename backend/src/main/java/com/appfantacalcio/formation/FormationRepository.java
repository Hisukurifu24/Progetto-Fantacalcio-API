package com.appfantacalcio.formation;

import com.appfantacalcio.team.Team;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
import java.util.UUID;

public interface FormationRepository extends JpaRepository<Formation, UUID> {
	Optional<Formation> findByTeamAndMatchDay(Team team, Integer matchDay);
}
