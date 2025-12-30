package com.appfantacalcio.auth;

import com.appfantacalcio.auth.dto.AuthResponse;
import com.appfantacalcio.auth.dto.LoginRequest;
import com.appfantacalcio.auth.dto.SignupRequest;
import com.appfantacalcio.user.UserRole;
import com.appfantacalcio.user.User;
import com.appfantacalcio.user.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder encoder;
    private final JwtService jwtService;

    public AuthResponse signup(SignupRequest req) {
        User user = new User();
        user.setUsername(req.username());
        user.setPassword(encoder.encode(req.password()));
        user.setRole(UserRole.USER);
        userRepository.save(user);

        return new AuthResponse(jwtService.generateToken(user));
    }

    public AuthResponse login(LoginRequest req) {
        User user = userRepository.findByUsername(req.username())
                .orElseThrow();

        if (!encoder.matches(req.password(), user.getPassword())) {
            throw new RuntimeException("Invalid credentials");
        }

        return new AuthResponse(jwtService.generateToken(user));
    }
}
