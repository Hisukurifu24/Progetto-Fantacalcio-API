package com.appfantacalcio.league.dto;

import com.appfantacalcio.team.dto.TeamResponse;
import com.appfantacalcio.user.dto.UserResponse;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;
import java.util.Set;
import java.util.UUID;

@Data
@AllArgsConstructor
public class LeagueResponse {
    private UUID id;
    private String name;
    
    @JsonProperty("is_public")
    private boolean isPublic;
    
    @JsonProperty("invite_code")
    private String inviteCode;
    
    @JsonProperty("created_by")
    private UserResponse createdBy;
    
    private Set<UserResponse> members;
    
    private List<TeamResponse> teams;
}
