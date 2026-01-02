package com.appfantacalcio.league.dto;

public record AdminAddPlayerRequest(
		String team_name,
		String player_name,
		String player_role) {
}
