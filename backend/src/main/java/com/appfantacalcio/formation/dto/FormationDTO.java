package com.appfantacalcio.formation.dto;

import lombok.Data;
import java.util.List;
import java.util.UUID;

@Data
public class FormationDTO {
	private UUID teamId;
	private Integer matchDay;
	private String module;
	private UUID goalkeeperId;
	private List<UUID> defenderIds;
	private List<UUID> midfielderIds;
	private List<UUID> forwardIds;
	private List<UUID> benchIds;
}
