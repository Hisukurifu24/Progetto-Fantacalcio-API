package com.appfantacalcio.user.dto;

import java.util.UUID;
import com.appfantacalcio.user.UserRole;

public record UserResponse(UUID id, String username, UserRole role) {
}
