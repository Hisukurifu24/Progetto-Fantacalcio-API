package com.appfantacalcio.formation.dto;

import com.appfantacalcio.player.dto.PlayerResponse;
import lombok.Data;
import java.util.List;

@Data
public class FormationResponseDTO {
	private String module;
	private Integer matchDay;
	private PlayerResponse goalkeeper;
	private List<PlayerResponse> defenders;
	private List<PlayerResponse> midfielders;
	private List<PlayerResponse> forwards;
	private List<PlayerResponse> bench;
}
