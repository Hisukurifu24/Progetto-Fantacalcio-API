package com.appfantacalcio.player;

import com.appfantacalcio.player.dto.PlayerResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/players")
@RequiredArgsConstructor
public class PlayerController {

    private final PlayerService playerService;

    @GetMapping
    public List<PlayerResponse> getAll(
            @RequestParam(required = false) String role,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) String team,
            @RequestParam(name = "min_quotazione", required = false) Integer minQuotazione,
            @RequestParam(name = "max_quotazione", required = false) Integer maxQuotazione,
            @RequestParam(name = "min_fvm", required = false) Integer minFvm,
            @RequestParam(name = "max_fvm", required = false) Integer maxFvm,
            @RequestParam(name = "sort_by", required = false) String sortBy,
            @RequestParam(name = "league_id", required = false) UUID leagueId,
            @RequestParam(name = "free_agents_only", required = false, defaultValue = "false") Boolean freeAgentsOnly) {
        // If any filter is specified, use the filtered method
        if (role != null || search != null || team != null ||
                minQuotazione != null || maxQuotazione != null ||
                minFvm != null || maxFvm != null || sortBy != null) {
            return playerService.findByFilters(
                    role, search, team, minQuotazione, maxQuotazione, minFvm, maxFvm, sortBy);
        }

        return playerService.findAll();
    }

    @GetMapping("/{id}")
    public PlayerResponse get(@PathVariable UUID id) {
        return playerService.get(id);
    }
}
