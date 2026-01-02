package com.appfantacalcio.auth.dto;

import com.appfantacalcio.user.dto.UserResponse;

public record AuthResponse(String token, UserResponse user) {
}
