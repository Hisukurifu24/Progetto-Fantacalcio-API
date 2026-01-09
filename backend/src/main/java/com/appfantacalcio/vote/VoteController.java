package com.appfantacalcio.vote;

import java.util.UUID;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/votes")
@RequiredArgsConstructor
public class VoteController {

	private final VoteService voteService;
	private final VoteImportScheduler voteImportScheduler;

	@PostMapping("/import")
	public ResponseEntity<String> importVotes() {
		boolean started = voteImportScheduler.triggerManualImport();
		if (started) {
			return ResponseEntity.ok("Import procedure started");
		} else {
			return ResponseEntity.ok("Import skipped: executed less than 1 minute ago");
		}
	}

	@GetMapping("/max-matchday")
	public ResponseEntity<Integer> getMaxMatchDay() {
		return ResponseEntity.ok(voteService.getMaxMatchDay());
	}

	@PostMapping("/calculate/{matchDay}")
	public ResponseEntity<Void> calculateMatchDay(
			@PathVariable Integer matchDay,
			@RequestParam(required = false) UUID competitionId) {
		voteService.calculateMatchDay(matchDay, competitionId);
		return ResponseEntity.ok().build();
	}
}
