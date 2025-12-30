package com.appfantacalcio.league.dto;

import com.appfantacalcio.user.dto.UserResponse;
import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.Set;
import java.util.UUID;

@Data
@AllArgsConstructor
public class LeagueResponse {
    private UUID id;
    private String name;
    private boolean isPublic;
    private String inviteCode;
    private UserResponse createdBy;
    private Set<UserResponse> members;
}
