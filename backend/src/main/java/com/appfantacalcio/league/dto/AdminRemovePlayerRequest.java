package com.appfantacalcio.league.dto;

public record AdminRemovePlayerRequest(
		String team_name,
		String player_name) {
}
