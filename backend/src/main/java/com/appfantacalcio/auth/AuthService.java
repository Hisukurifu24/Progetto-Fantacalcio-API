package com.appfantacalcio.auth;

import com.appfantacalcio.auth.dto.AuthResponse;
import com.appfantacalcio.auth.dto.LoginRequest;
import com.appfantacalcio.auth.dto.SignupRequest;
import com.appfantacalcio.user.UserRole;
import com.appfantacalcio.user.dto.UserResponse;
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
        if (req.username() == null || req.email() == null) {
            throw new RuntimeException("Username and Email are required");
        }
        
        if (userRepository.findByUsername(req.username().toLowerCase()).isPresent()) {
            throw new RuntimeException("Username already taken");
        }
        
        if (userRepository.findByEmail(req.email().toLowerCase()).isPresent()) {
            throw new RuntimeException("Email already taken");
        }

        User user = new User();
        user.setUsername(req.username().toLowerCase());
        user.setEmail(req.email().toLowerCase());
        user.setPassword(encoder.encode(req.password()));
        user.setRole(UserRole.USER);
        userRepository.save(user);

        UserResponse userResponse = new UserResponse(user.getId(), user.getUsername(), user.getRole());
        return new AuthResponse(jwtService.generateToken(user), userResponse);
    }

    public AuthResponse login(LoginRequest req) {
        if (req.usernameOrEmail() == null) {
            throw new RuntimeException("Invalid credentials");
        }
        
        String loginInput = req.usernameOrEmail().toLowerCase();
        
        User user = userRepository.findByUsername(loginInput)
                .or(() -> userRepository.findByEmail(loginInput))
                .orElseThrow(() -> new RuntimeException("Invalid credentials"));

        if (!encoder.matches(req.password(), user.getPassword())) {
            throw new RuntimeException("Invalid credentials");
        }

        UserResponse userResponse = new UserResponse(user.getId(), user.getUsername(), user.getRole());
        return new AuthResponse(jwtService.generateToken(user), userResponse);
    }
}
