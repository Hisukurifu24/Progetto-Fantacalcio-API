package com.appfantacalcio.league.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

public record UpdateLeagueRequest(
		String name,
		Settings settings) {
	public record Settings(
			@JsonProperty("start_day") Integer startDay,
			@JsonProperty("max_budget") Integer maxBudget,
			@JsonProperty("max_players_per_role") Map<String, Integer> maxPlayersPerRole,
			@JsonProperty("bench_limits") Map<String, Integer> benchLimits) {
	}
}
