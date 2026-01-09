package com.appfantacalcio.player;

import com.appfantacalcio.player.dto.PlayerResponse;
import com.appfantacalcio.exception.ResourceNotFoundException;
import com.appfantacalcio.roster.RosterEntry;
import com.appfantacalcio.roster.RosterEntryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PlayerService {

    private final PlayerRepository playerRepository;
    private final RosterEntryRepository rosterEntryRepository;

    public List<PlayerResponse> findAll() {
        return playerRepository.findAll().stream()
                .map(this::toPlayerResponse)
                .collect(Collectors.toList());
    }

    public List<PlayerResponse> findByFilters(
            String role,
            String search,
            String team,
            Integer minQuotazione,
            Integer maxQuotazione,
            Integer minFvm,
            Integer maxFvm,
            String sortBy,
            UUID leagueId,
            Boolean freeAgentsOnly) {
        List<Player> players = playerRepository.findByFilters(
                role, search, team, minQuotazione, maxQuotazione, minFvm, maxFvm);

        Map<UUID, String> playerOwners = new HashMap<>();
        if (leagueId != null) {
            List<RosterEntry> rosterEntries = rosterEntryRepository.findByTeamLeagueId(leagueId);
            for (RosterEntry entry : rosterEntries) {
                playerOwners.put(entry.getPlayer().getId(), entry.getTeam().getName());
            }
        }

        if (Boolean.TRUE.equals(freeAgentsOnly) && leagueId != null) {
            players = players.stream()
                    .filter(p -> !playerOwners.containsKey(p.getId()))
                    .collect(Collectors.toList());
        }

        List<PlayerResponse> responses = players.stream()
                .map(p -> toPlayerResponse(p, playerOwners.get(p.getId())))
                .collect(Collectors.toList());

        // Apply sorting
        if (sortBy != null) {
            switch (sortBy) {
                case "quotazione_desc":
                    responses.sort(Comparator.comparing(PlayerResponse::quotazione_attuale_classico,
                            Comparator.nullsLast(Comparator.reverseOrder())));
                    break;
                case "quotazione_asc":
                    responses.sort(Comparator.comparing(PlayerResponse::quotazione_attuale_classico,
                            Comparator.nullsLast(Comparator.naturalOrder())));
                    break;
                case "fvm_desc":
                    responses.sort(Comparator.comparing(PlayerResponse::fvm_classico,
                            Comparator.nullsLast(Comparator.reverseOrder())));
                    break;
                case "fvm_asc":
                    responses.sort(Comparator.comparing(PlayerResponse::fvm_classico,
                            Comparator.nullsLast(Comparator.naturalOrder())));
                    break;
            }
        }

        return responses;
    }

    public PlayerResponse get(UUID id) {
        return playerRepository.findById(id)
                .map(this::toPlayerResponse)
                .orElseThrow(() -> new ResourceNotFoundException("Player not found with id: " + id));
    }

    private PlayerResponse toPlayerResponse(Player player) {
        return toPlayerResponse(player, null);
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
