package com.appfantacalcio.roster;

import com.appfantacalcio.roster.dto.CreateRosterEntryRequest;
import com.appfantacalcio.roster.dto.RosterEntryResponse;
import com.appfantacalcio.exception.ResourceNotFoundException;
import com.appfantacalcio.player.Player;
import com.appfantacalcio.player.PlayerRepository;
import com.appfantacalcio.player.dto.PlayerResponse;
import com.appfantacalcio.team.Team;
import com.appfantacalcio.team.TeamRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class RosterEntryService {

    private final RosterEntryRepository rosterEntryRepository;
    private final TeamRepository teamRepository;
    private final PlayerRepository playerRepository;

    @Transactional
    public RosterEntryResponse create(CreateRosterEntryRequest request) {
        Team team = teamRepository.findById(request.teamId())
                .orElseThrow(() -> new ResourceNotFoundException("Team not found with id: " + request.teamId()));

        Player player = playerRepository.findById(request.playerId())
                .orElseThrow(() -> new ResourceNotFoundException("Player not found with id: " + request.playerId()));

        RosterEntry rosterEntry = new RosterEntry();
        rosterEntry.setTeam(team);
        rosterEntry.setPlayer(player);
        rosterEntry.setAcquiredFor(request.acquiredFor());

        rosterEntryRepository.save(rosterEntry);
        return toRosterEntryResponse(rosterEntry);
    }

    public List<RosterEntryResponse> findByTeam(UUID teamId) {
        return rosterEntryRepository.findByTeamId(teamId).stream()
                .map(this::toRosterEntryResponse)
                .collect(Collectors.toList());
    }

    public void delete(UUID id) {
        if (!rosterEntryRepository.existsById(id)) {
            throw new ResourceNotFoundException("RosterEntry not found with id: " + id);
        }
        rosterEntryRepository.deleteById(id);
    }

    private RosterEntryResponse toRosterEntryResponse(RosterEntry entry) {
        return new RosterEntryResponse(
                entry.getId(),
                entry.getTeam().getId(),
                toPlayerResponse(entry.getPlayer(), entry.getTeam().getName()),
                entry.getAcquiredFor());
    }

    private PlayerResponse toPlayerResponse(Player player, String fantaSquadra) {
        return new PlayerResponse(
                player.getId(),
                player.getName(),
                player.getRole(),
                player.getRealTeam(),
                player.getQuotazioneInizialeClassico(),
                player.getQuotazioneAttualeClassico(),
                player.getQuotazioneInizialeMantra(),
                player.getQuotazioneAttualeMantra(),
                player.getFvmClassico(),
                player.getFvmMantra(),
                fantaSquadra);
    }
}
