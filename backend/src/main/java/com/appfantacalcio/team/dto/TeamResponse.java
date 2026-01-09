package com.appfantacalcio.team.dto;

import com.appfantacalcio.user.dto.UserResponse;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.UUID;

public record TeamResponse(
        UUID id,
        String name,
        @JsonProperty("coach_name") String coachName,
        UserResponse owner,
        @JsonProperty("owner_id") UUID ownerId,
        @JsonProperty("league_id") UUID leagueId,
        List<Object> roster) {
}
