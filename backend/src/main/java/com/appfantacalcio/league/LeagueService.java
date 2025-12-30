package com.appfantacalcio.league;

import com.appfantacalcio.user.dto.UserResponse;
import com.appfantacalcio.exception.ResourceNotFoundException;
import com.appfantacalcio.league.dto.CreateLeagueRequest;
import com.appfantacalcio.league.dto.LeagueResponse;
import com.appfantacalcio.user.User;
import com.appfantacalcio.user.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class LeagueService {

    private final LeagueRepository leagueRepository;
    private final UserRepository userRepository;

    public LeagueResponse create(CreateLeagueRequest request) {
        User currentUser = getCurrentUser();
        League league = new League();
        league.setName(request.name());
        league.setPublic(request.isPublic());
        league.setCreatedBy(currentUser);
        league.setInviteCode(generateInviteCode());
        league.setMembers(Set.of(currentUser));
        leagueRepository.save(league);
        return toLeagueResponse(league);
    }

    public List<LeagueResponse> findMine() {
        User currentUser = getCurrentUser();
        return leagueRepository.findAll().stream()
                .filter(league -> league.getMembers().contains(currentUser))
                .map(this::toLeagueResponse)
                .collect(Collectors.toList());
    }

    public List<LeagueResponse> findPublic() {
        return leagueRepository.findAll().stream()
                .filter(League::isPublic)
                .map(this::toLeagueResponse)
                .collect(Collectors.toList());
    }

    public LeagueResponse get(UUID id) {
        return leagueRepository.findById(id)
                .map(this::toLeagueResponse)
                .orElseThrow(() -> new ResourceNotFoundException("League not found with id: " + id));
    }

    public LeagueResponse join(String inviteCode) {
        User currentUser = getCurrentUser();
        League league = leagueRepository.findByInviteCode(inviteCode)
                .orElseThrow(() -> new ResourceNotFoundException("League not found with invite code: " + inviteCode));
        league.getMembers().add(currentUser);
        leagueRepository.save(league);
        return toLeagueResponse(league);
    }

    private User getCurrentUser() {
        String username = SecurityContextHolder.getContext().getAuthentication().getName();
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with username: " + username));
    }

    private String generateInviteCode() {
        // generate a random 8 character string
        String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 8; i++) {
            int index = (int) (Math.random() * chars.length());
            sb.append(chars.charAt(index));
        }
        return sb.toString();
    }

    private LeagueResponse toLeagueResponse(League league) {
        return new LeagueResponse(
                league.getId(),
                league.getName(),
                league.isPublic(),
                league.getInviteCode(),
                toUserResponse(league.getCreatedBy()),
                league.getMembers().stream().map(this::toUserResponse).collect(Collectors.toSet()));
    }

    private UserResponse toUserResponse(User user) {
        return new UserResponse(
                user.getId(),
                user.getUsername(),
                user.getRole());
    }
}