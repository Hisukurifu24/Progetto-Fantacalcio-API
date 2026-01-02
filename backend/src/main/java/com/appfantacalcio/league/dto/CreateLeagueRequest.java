package com.appfantacalcio.league.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public record CreateLeagueRequest(
        String name,
        @JsonProperty("is_public") boolean isPublic,
        String teamName,
        List<TeamData> teams,
        List<Object> competitions,
        Settings settings) {

    public record TeamData(String name, UUID owner, List<Object> roster) {
    }

    public record Settings(
            @JsonProperty("start_day") Integer startDay,
            @JsonProperty("max_budget") Integer maxBudget,
            @JsonProperty("max_players_per_role") Map<String, Integer> maxPlayersPerRole,
            @JsonProperty("bench_limits") Map<String, Integer> benchLimits) {
    }
}

