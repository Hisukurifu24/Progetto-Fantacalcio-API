package com.appfantacalcio.team.dto;

import java.util.UUID;

public record CreateTeamRequest(
    String name,
    UUID leagueId
) {}
