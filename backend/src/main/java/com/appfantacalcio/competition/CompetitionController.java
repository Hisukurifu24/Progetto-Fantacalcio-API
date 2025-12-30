package com.appfantacalcio.competition;

import java.util.List;
import java.util.UUID;

import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.appfantacalcio.competition.dto.CreateCompetitionRequest;
import com.appfantacalcio.match.Match;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class CompetitionController {

	private final CompetitionService competitionService;

	@PostMapping("/leagues/{leagueId}/competitions")
	public Competition create(
			@PathVariable UUID leagueId,
			@RequestBody CreateCompetitionRequest req) {
		return competitionService.create(leagueId, req);
	}

	@DeleteMapping("/competitions/{id}")
	public void delete(@PathVariable UUID id) {
		competitionService.delete(id);
	}

	@PostMapping("/competitions/{id}/calendar")
	public void generateCalendar(@PathVariable UUID id) {
		competitionService.generateCalendar(id);
	}

	@GetMapping("/competitions/{id}/calendar")
	public List<Match> calendar(@PathVariable UUID id) {
		return competitionService.calendar(id);
	}
}
