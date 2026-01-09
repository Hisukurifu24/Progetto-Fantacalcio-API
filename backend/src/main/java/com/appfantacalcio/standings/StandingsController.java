package com.appfantacalcio.standings;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/standings")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class StandingsController {

	private final StandingsRepository standingsRepository;

	@GetMapping("/competition/{competitionId}")
	public ResponseEntity<List<Standings>> getStandingsByCompetition(@PathVariable UUID competitionId) {
		return ResponseEntity.ok(standingsRepository.findByCompetitionId(competitionId));
	}
}
