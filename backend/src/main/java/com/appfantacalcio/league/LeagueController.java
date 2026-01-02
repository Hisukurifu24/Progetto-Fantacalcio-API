package com.appfantacalcio.league;

import com.appfantacalcio.league.dto.AdminAddPlayerRequest;
import com.appfantacalcio.league.dto.AdminRemovePlayerRequest;
import com.appfantacalcio.league.dto.CreateLeagueRequest;
import com.appfantacalcio.league.dto.JoinLeagueRequest;
import com.appfantacalcio.league.dto.LeagueResponse;

import java.util.List;
import java.util.UUID;

import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/leagues")
@RequiredArgsConstructor
public class LeagueController {

    private final LeagueService leagueService;

    @PostMapping
    public LeagueResponse create(@RequestBody CreateLeagueRequest req) {
        return leagueService.create(req);
    }

    @PostMapping("/join-with-code")
    public LeagueResponse joinWithCode(@RequestBody JoinLeagueRequest req) {
        return leagueService.joinWithCode(req.inviteCode(), req.teamName(), req.managerName());
    }

    @PostMapping("/{id}/join")
    public LeagueResponse joinById(@PathVariable UUID id, @RequestBody JoinLeagueRequest req) {
        return leagueService.joinById(id, req.teamName(), req.managerName());
    }

    @GetMapping
    public List<LeagueResponse> myLeagues() {
        return leagueService.findMine();
    }

    @GetMapping("/public")
    public List<LeagueResponse> publicLeagues() {
        return leagueService.findPublic();
    }

    @GetMapping("/{id}")
    public LeagueResponse get(@PathVariable UUID id) {
        return leagueService.get(id);
    }

    @DeleteMapping("/{id}/leave")
    public void leave(@PathVariable UUID id) {
        leagueService.leave(id);
    }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable UUID id) {
        leagueService.delete(id);
    }

    @PostMapping("/{id}/admin/add-player")
    public LeagueResponse adminAddPlayer(
            @PathVariable UUID id,
            @RequestBody AdminAddPlayerRequest request) {
        return leagueService.adminAddPlayer(id, request.team_name(), request.player_name(), request.player_role());
    }

    @PostMapping("/{id}/admin/remove-player")
    public LeagueResponse adminRemovePlayer(
            @PathVariable UUID id,
            @RequestBody AdminRemovePlayerRequest request) {
        return leagueService.adminRemovePlayer(id, request.team_name(), request.player_name());
    }
}
