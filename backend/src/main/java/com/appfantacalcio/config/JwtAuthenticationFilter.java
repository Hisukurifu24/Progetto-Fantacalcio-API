package com.appfantacalcio.config;

import com.appfantacalcio.auth.JwtService;
import com.appfantacalcio.user.User;
import com.appfantacalcio.user.UserRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Optional;
import java.util.UUID;
import io.jsonwebtoken.JwtException;

@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    private final JwtService jwtService;
    private final UserRepository userRepository;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        String token = authHeader.substring(7).trim();

        UUID userId = null;
        try {
            if (!token.isEmpty() && token.chars().filter(ch -> ch == '.').count() == 2) {
                userId = jwtService.extractUserId(token);
            } else {
                // not a valid JWT structure, skip authentication
            }
        } catch (JwtException | IllegalArgumentException e) {
            // Invalid token — skip authentication and continue filter chain
        }

        Optional<User> user = userId != null ? userRepository.findById(userId) : Optional.empty();

        if (user.isPresent()) {
            UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(user.get(),
                    null, user.get().getAuthorities());
            SecurityContextHolder.getContext().setAuthentication(authentication);
        }

        filterChain.doFilter(request, response);
    }
}
