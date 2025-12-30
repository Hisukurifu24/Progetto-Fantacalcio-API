
package com.appfantacalcio.auth;

import com.appfantacalcio.auth.dto.AuthResponse;
import com.appfantacalcio.auth.dto.LoginRequest;
import com.appfantacalcio.auth.dto.SignupRequest;
import com.appfantacalcio.user.dto.UserResponse;
import com.appfantacalcio.user.User;

import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/signup")
    public AuthResponse signup(@RequestBody SignupRequest req) {
        return authService.signup(req);
    }

    @PostMapping("/login")
    public AuthResponse login(@RequestBody LoginRequest req) {
        return authService.login(req);
    }

    @GetMapping("/me")
    public UserResponse me(Authentication auth) {
        User user = (User) auth.getPrincipal();
        return new UserResponse(user.getId(), user.getUsername(), user.getRole());
    }
}
