package com.appfantacalcio.player;

import com.appfantacalcio.player.dto.PlayerResponse;
import com.appfantacalcio.exception.ResourceNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Comparator;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PlayerService {

    private final PlayerRepository playerRepository;

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
            String sortBy) {
        List<Player> players = playerRepository.findByFilters(
                role, search, team, minQuotazione, maxQuotazione, minFvm, maxFvm);

        List<PlayerResponse> responses = players.stream()
                .map(this::toPlayerResponse)
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
                player.getFvmMantra());
    }
}
