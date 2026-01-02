package com.appfantacalcio.auth.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record LoginRequest(@JsonProperty("username_or_email") String usernameOrEmail, String password) {
}
