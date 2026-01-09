package com.appfantacalcio.competition.dto;

import com.appfantacalcio.competition.CompetitionType;

public record CreateCompetitionRequest(
		String name,
		CompetitionType type,
		int startDay,
		int endDay,
		java.util.List<java.util.UUID> participantIds,
		boolean roundsHomeAway,
		boolean finalHomeAway,
		boolean randomBrackets,
		// Group Cup
		int numGroups,
		int teamsQualifyPerGroup,
		int matchesPerTeam,
		boolean knockoutHomeAway,
		boolean finalGroupHomeAway,
		boolean randomGroups) {
}
