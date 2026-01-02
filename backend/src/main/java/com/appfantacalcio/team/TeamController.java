package com.appfantacalcio.team;

import com.appfantacalcio.team.dto.CreateTeamRequest;
import com.appfantacalcio.team.dto.TeamResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/teams")
@RequiredArgsConstructor
public class TeamController {

    private final TeamService teamService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public TeamResponse create(@RequestBody CreateTeamRequest request) {
        return teamService.create(request);
    }

    @GetMapping("/{id}")
    public TeamResponse get(@PathVariable UUID id) {
        return teamService.get(id);
    }

    @GetMapping("/league/{leagueId}")
    public List<TeamResponse> getByLeague(@PathVariable UUID leagueId) {
        return teamService.findByLeague(leagueId);
    }

    @GetMapping("/mine")
    public List<TeamResponse> getMyTeams() {
        return teamService.findMyTeams();
    }
}
