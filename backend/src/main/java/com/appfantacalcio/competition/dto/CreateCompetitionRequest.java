package com.appfantacalcio.competition.dto;

import com.appfantacalcio.competition.CompetitionType;

public record CreateCompetitionRequest(
		CompetitionType type,
		int startDay,
		int endDay) {
}
