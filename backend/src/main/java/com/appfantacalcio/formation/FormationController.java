package com.appfantacalcio.formation;

import com.appfantacalcio.formation.dto.FormationDTO;
import com.appfantacalcio.formation.dto.FormationResponseDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/formations")
@RequiredArgsConstructor
public class FormationController {

	private final FormationService formationService;

	@PostMapping
	public ResponseEntity<FormationResponseDTO> saveFormation(@RequestBody FormationDTO dto) {
		return ResponseEntity.ok(formationService.saveFormation(dto));
	}

	@GetMapping
	public ResponseEntity<FormationResponseDTO> getFormation(
			@RequestParam UUID teamId,
			@RequestParam Integer matchDay) {
		try {
			return ResponseEntity.ok(formationService.getFormation(teamId, matchDay));
		} catch (RuntimeException e) {
			return ResponseEntity.notFound().build();
		}
	}
}
