package com.appfantacalcio.team.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.UUID;

public record CreateTeamRequest(
        String name,
        @JsonProperty("coach_name") String coachName,
        UUID leagueId) {
}
