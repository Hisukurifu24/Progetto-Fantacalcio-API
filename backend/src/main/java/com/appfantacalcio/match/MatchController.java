package com.appfantacalcio.match;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/matches")
@RequiredArgsConstructor
public class MatchController {

    private final MatchService matchService;

    @GetMapping
    public ResponseEntity<List<Match>> getAllMatches() {
        return ResponseEntity.ok(matchService.getAllMatches());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Match> getMatchById(@PathVariable UUID id) {
        return ResponseEntity.ok(matchService.getMatchById(id));
    }

    @GetMapping("/competition/{competitionId}")
    public ResponseEntity<List<Match>> getMatchesByCompetitionId(@PathVariable UUID competitionId) {
        return ResponseEntity.ok(matchService.getMatchesByCompetitionId(competitionId));
    }

    @GetMapping("/live/{competitionId}")
    public ResponseEntity<Object> getLiveMatch(@PathVariable UUID competitionId, java.security.Principal principal) {
        return ResponseEntity.ok(matchService.getLiveMatch(competitionId, principal.getName()));
    }

    @PostMapping
    public ResponseEntity<Match> createMatch(@RequestBody Match match) {
        return ResponseEntity.ok(matchService.createMatch(match));
    }

    @PutMapping("/{id}")
    public ResponseEntity<Match> updateMatch(@PathVariable UUID id, @RequestBody Match match) {
        return ResponseEntity.ok(matchService.updateMatch(id, match));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteMatch(@PathVariable UUID id) {
        matchService.deleteMatch(id);
        return ResponseEntity.noContent().build();
    }
}
