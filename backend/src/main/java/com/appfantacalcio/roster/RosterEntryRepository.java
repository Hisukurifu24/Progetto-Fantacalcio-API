package com.appfantacalcio.roster;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface RosterEntryRepository extends JpaRepository<RosterEntry, UUID> {
    List<RosterEntry> findByTeamId(UUID teamId);

    List<RosterEntry> findByTeamLeagueId(UUID leagueId);

    Optional<RosterEntry> findByTeamIdAndPlayerId(UUID teamId, UUID playerId);
}
