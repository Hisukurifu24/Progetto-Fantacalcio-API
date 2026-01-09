package com.appfantacalcio.league;

import com.appfantacalcio.competition.Competition;
import com.appfantacalcio.competition.CompetitionRepository;
import com.appfantacalcio.user.dto.UserResponse;
import com.appfantacalcio.exception.ResourceNotFoundException;
import com.appfantacalcio.league.dto.CreateLeagueRequest;
import com.appfantacalcio.league.dto.UpdateLeagueRequest;
import com.appfantacalcio.league.dto.LeagueResponse;
import com.appfantacalcio.player.Player;
import com.appfantacalcio.player.PlayerRepository;
import com.appfantacalcio.roster.RosterEntry;
import com.appfantacalcio.roster.RosterEntryRepository;
import com.appfantacalcio.team.Team;
import com.appfantacalcio.team.TeamRepository;
import com.appfantacalcio.user.User;
import com.appfantacalcio.user.UserRepository;
import com.appfantacalcio.user.UserService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
@Slf4j
public class LeagueService {

    private final LeagueRepository leagueRepository;
    private final UserService userService;
    private final TeamRepository teamRepository;
    private final UserRepository userRepository;
    private final PlayerRepository playerRepository;
    private final RosterEntryRepository rosterEntryRepository;
    private final CompetitionRepository competitionRepository;

    public LeagueResponse create(CreateLeagueRequest request) {
        User currentUser = userService.getCurrentUser();
        User managedUser = userRepository.findById(currentUser.getId())
                .orElseThrow(() -> new ResourceNotFoundException("User not found"));

        League league = new League();
        league.setName(request.name());
        league.setPublic(request.isPublic());
        league.setCreatedBy(managedUser);
        league.setInviteCode(generateInviteCode());

        if (request.settings() != null) {
            league.setStartDay(request.settings().startDay());
            league.setMaxBudget(request.settings().maxBudget());

            if (request.settings().maxPlayersPerRole() != null) {
                league.setMaxPlayersPerRole(request.settings().maxPlayersPerRole());
            } else {
                league.setMaxPlayersPerRole(Map.of("P", 3, "D", 8, "C", 8, "A", 6));
            }

            if (request.settings().benchLimits() != null) {
                league.setBenchLimits(request.settings().benchLimits());
            } else {
                league.setBenchLimits(Map.of("P", 1, "D", 3, "C", 3, "A", 3));
            }
        } else {
            league.setMaxPlayersPerRole(Map.of("P", 3, "D", 8, "C", 8, "A", 6));
            league.setBenchLimits(Map.of("P", 1, "D", 3, "C", 3, "A", 3));
        }

        // Use a mutable Set
        league.setMembers(new HashSet<>(Set.of(managedUser)));
        League savedLeague = leagueRepository.save(league);

        // Extract team name from the request - prefer teams array if present, otherwise
        // use teamName
        String teamName = null;
        String coachName = null;
        if (request.teams() != null && !request.teams().isEmpty()) {
            teamName = request.teams().get(0).name();
            coachName = request.teams().get(0).coachName();
        } else if (request.teamName() != null) {
            teamName = request.teamName();
        }

        createTeam(managedUser, savedLeague, teamName, coachName);

        return toLeagueResponse(savedLeague);
    }

    public List<LeagueResponse> findMine() {
        User currentUser = userService.getCurrentUser();
        return leagueRepository.findAllByMembersContaining(currentUser).stream()
                .map(this::toLeagueResponse)
                .collect(Collectors.toList());
    }

    public List<LeagueResponse> findPublic() {
        return leagueRepository.findAllByIsPublicTrue().stream()
                .map(this::toLeagueResponse)
                .collect(Collectors.toList());
    }

    public LeagueResponse get(UUID id) {
        return leagueRepository.findById(id)
                .map(this::toLeagueResponse)
                .orElseThrow(() -> new ResourceNotFoundException("League not found with id: " + id));
    }

    public LeagueResponse joinWithCode(String inviteCode, String teamName, String managerName) {
        User currentUser = userService.getCurrentUser();
        User managedUser = userRepository.findById(currentUser.getId())
                .orElseThrow(() -> new ResourceNotFoundException("User not found"));

        League league = leagueRepository.findByInviteCode(inviteCode)
                .orElseThrow(() -> new ResourceNotFoundException("League not found with invite code: " + inviteCode));

        return joinLeague(managedUser, league, teamName, managerName);
    }

    public LeagueResponse joinById(UUID leagueId, String teamName, String managerName) {
        User currentUser = userService.getCurrentUser();
        User managedUser = userRepository.findById(currentUser.getId())
                .orElseThrow(() -> new ResourceNotFoundException("User not found"));

        League league = leagueRepository.findById(leagueId)
                .orElseThrow(() -> new ResourceNotFoundException("League not found with id: " + leagueId));

        return joinLeague(managedUser, league, teamName, managerName);
    }

    private LeagueResponse joinLeague(User user, League league, String teamName, String managerName) {
        if (league.getMembers() == null) {
            league.setMembers(new HashSet<>());
        }

        boolean alreadyMember = league.getMembers().contains(user);
        if (alreadyMember) {
            throw new RuntimeException("You are already a member of this league");
        }

        league.getMembers().add(user);
        leagueRepository.save(league);
        createTeam(user, league, teamName, managerName);

        return toLeagueResponse(league);
    }

    public void leave(UUID leagueId) {
        User currentUser = userService.getCurrentUser();
        User managedUser = userRepository.findById(currentUser.getId())
                .orElseThrow(() -> new ResourceNotFoundException("User not found"));

        League league = leagueRepository.findById(leagueId)
                .orElseThrow(() -> new ResourceNotFoundException("League not found with id: " + leagueId));

        if (league.getMembers() != null) {
            league.getMembers().remove(managedUser);
            leagueRepository.save(league);
        }

        // Delete user's team from the league
        List<Team> userTeams = teamRepository.findByLeagueId(leagueId).stream()
                .filter(team -> team.getOwner().getId().equals(managedUser.getId()))
                .collect(Collectors.toList());
        teamRepository.deleteAll(userTeams);
    }

    public LeagueResponse update(UUID id, UpdateLeagueRequest request) {
        User currentUser = userService.getCurrentUser();
        League league = leagueRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("League not found with id: " + id));

        if (!league.getCreatedBy().getId().equals(currentUser.getId())) {
            throw new IllegalStateException("Only the league creator can update the league");
        }

        if (request.name() != null) {
            league.setName(request.name());
        }

        if (request.settings() != null) {
            if (request.settings().startDay() != null) {
                league.setStartDay(request.settings().startDay());
            }
            if (request.settings().maxBudget() != null) {
                league.setMaxBudget(request.settings().maxBudget());
            }
            if (request.settings().maxPlayersPerRole() != null) {
                league.setMaxPlayersPerRole(request.settings().maxPlayersPerRole());
            }
            if (request.settings().benchLimits() != null) {
                league.setBenchLimits(request.settings().benchLimits());
            }
        }

        return toLeagueResponse(leagueRepository.save(league));
    }

    public void delete(UUID leagueId) {
        User currentUser = userService.getCurrentUser();

        League league = leagueRepository.findById(leagueId)
                .orElseThrow(() -> new ResourceNotFoundException("League not found with id: " + leagueId));

        // Verifica che l'utente sia il creatore della lega
        if (!league.getCreatedBy().getId().equals(currentUser.getId())) {
            throw new IllegalStateException("Only the league creator can delete the league");
        }

        // Elimina tutti i roster entries della lega
        List<RosterEntry> rosterEntries = rosterEntryRepository.findByTeamLeagueId(leagueId);
        rosterEntryRepository.deleteAll(rosterEntries);

        // Elimina tutti i team della lega
        List<Team> teams = teamRepository.findByLeagueId(leagueId);
        teamRepository.deleteAll(teams);

        // Elimina la lega
        leagueRepository.delete(league);
    }

    private void createTeam(User user, League league, String teamName, String coachName) {
        Team team = new Team();
        team.setName(teamName != null && !teamName.isBlank() ? teamName : "Team " + user.getUsername());
        team.setCoachName(coachName != null && !coachName.isBlank() ? coachName : user.getUsername());
        team.setOwner(user);
        team.setLeague(league);
        teamRepository.save(team);
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
        List<Team> teams = teamRepository.findByLeagueId(league.getId());
        List<Competition> competitions = competitionRepository.findByLeagueId(league.getId());
        return new LeagueResponse(
                league.getId(),
                league.getName(),
                league.isPublic(),
                league.getInviteCode(),
                toUserResponse(league.getCreatedBy()),
                league.getMembers().stream().map(this::toUserResponse).collect(Collectors.toSet()),
                teams.stream().map(this::toTeamResponse).collect(Collectors.toList()),
                competitions);
    }

    private UserResponse toUserResponse(User user) {
        return new UserResponse(
                user.getId(),
                user.getUsername(),
                user.getRole());
    }

    private com.appfantacalcio.team.dto.TeamResponse toTeamResponse(Team team) {
        // Carica il roster del team
        List<RosterEntry> rosterEntries = rosterEntryRepository.findByTeamId(team.getId());

        // Converti il roster in PlayerResponse
        List<Object> roster = rosterEntries.stream()
                .map(entry -> {
                    Player player = entry.getPlayer();
                    return new com.appfantacalcio.player.dto.PlayerResponse(
                            player.getId(),
                            player.getName(),
                            player.getRole(),
                            player.getRealTeam(),
                            player.getQuotazioneInizialeClassico(),
                            player.getQuotazioneAttualeClassico(),
                            player.getQuotazioneInizialeMantra(),
                            player.getQuotazioneAttualeMantra(),
                            player.getFvmClassico(),
                            player.getFvmMantra(),
                            team.getName());
                })
                .collect(Collectors.toList());

        return new com.appfantacalcio.team.dto.TeamResponse(
                team.getId(),
                team.getName(),
                team.getCoachName(),
                toUserResponse(team.getOwner()),
                team.getOwner().getId(),
                team.getLeague().getId(),
                roster);
    }

    @Transactional
    public LeagueResponse adminAddPlayer(UUID leagueId, String teamName, String playerName, String playerRole) {
        log.info("adminAddPlayer called with leagueId={}, teamName={}, playerName={}, playerRole={}",
                leagueId, teamName, playerName, playerRole);

        User currentUser = userService.getCurrentUser();

        League league = leagueRepository.findById(leagueId)
                .orElseThrow(() -> new ResourceNotFoundException("League not found with id: " + leagueId));

        // Verifica che l'utente sia il creatore della lega
        if (!league.getCreatedBy().getId().equals(currentUser.getId())) {
            log.error("User {} is not the league creator", currentUser.getId());
            throw new IllegalStateException("Only the league creator can add players to teams");
        }

        // Trova il team
        Team team = teamRepository.findByNameAndLeagueId(teamName, leagueId)
                .orElseThrow(() -> {
                    log.error("Team not found: {} in league {}", teamName, leagueId);
                    return new ResourceNotFoundException("Team not found: " + teamName);
                });

        // Trova il giocatore
        Player player = playerRepository.findByName(playerName)
                .orElseThrow(() -> {
                    log.error("Player not found: {}", playerName);
                    return new ResourceNotFoundException("Player not found: " + playerName);
                });

        log.info("Found player: id={}, name={}, role={}", player.getId(), player.getName(), player.getRole());

        // Verifica che il giocatore non sia già in un altro team della stessa lega
        List<Team> leagueTeams = teamRepository.findByLeagueId(leagueId);
        for (Team t : leagueTeams) {
            if (rosterEntryRepository.findByTeamIdAndPlayerId(t.getId(), player.getId()).isPresent()) {
                log.error("Player {} is already assigned to team {}", playerName, t.getName());
                throw new IllegalStateException("Player is already assigned to another team in this league");
            }
        }

        // Check max players per role limit
        if (league.getMaxPlayersPerRole() != null) {
            String role = player.getRole();
            Integer limit = league.getMaxPlayersPerRole().get(role);

            if (limit != null) {
                long currentCount = rosterEntryRepository.findByTeamId(team.getId()).stream()
                        .filter(entry -> entry.getPlayer().getRole().equals(role))
                        .count();

                if (currentCount >= limit) {
                    throw new IllegalStateException(
                            "Roster limit reached for role: " + role + ". Max allowed: " + limit);
                }
            }
        }

        // Aggiungi il giocatore al roster del team
        RosterEntry rosterEntry = new RosterEntry();
        rosterEntry.setTeam(team);
        rosterEntry.setPlayer(player);
        rosterEntry.setAcquiredFor(0); // Admin adds are free
        rosterEntryRepository.save(rosterEntry);

        log.info("Player {} successfully added to team {}", playerName, teamName);
        return toLeagueResponse(league);
    }

    @Transactional
    public LeagueResponse adminRemovePlayer(UUID leagueId, String teamName, String playerName) {
        User currentUser = userService.getCurrentUser();

        League league = leagueRepository.findById(leagueId)
                .orElseThrow(() -> new ResourceNotFoundException("League not found with id: " + leagueId));

        // Verifica che l'utente sia il creatore della lega
        if (!league.getCreatedBy().getId().equals(currentUser.getId())) {
            throw new IllegalStateException("Only the league creator can remove players from teams");
        }

        // Trova il team
        Team team = teamRepository.findByNameAndLeagueId(teamName, leagueId)
                .orElseThrow(() -> new ResourceNotFoundException("Team not found: " + teamName));

        // Trova il giocatore
        Player player = playerRepository.findByName(playerName)
                .orElseThrow(() -> new ResourceNotFoundException("Player not found: " + playerName));

        // Rimuovi il giocatore dal roster
        RosterEntry entry = rosterEntryRepository.findByTeamIdAndPlayerId(team.getId(), player.getId())
                .orElseThrow(() -> new ResourceNotFoundException("Player not found in team roster"));

        rosterEntryRepository.delete(entry);

        return toLeagueResponse(league);
    }
}
