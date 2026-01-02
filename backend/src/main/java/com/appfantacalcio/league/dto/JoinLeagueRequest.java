package com.appfantacalcio.league.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record JoinLeagueRequest(
        @JsonProperty("invite_code") String inviteCode, 
        @JsonProperty("team_name") String teamName,
        @JsonProperty("manager_name") String managerName) {
}

