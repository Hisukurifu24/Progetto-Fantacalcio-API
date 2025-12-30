package com.appfantacalcio.league;

import com.appfantacalcio.league.dto.CreateLeagueRequest;
import com.appfantacalcio.league.dto.JoinLeagueRequest;
import com.appfantacalcio.league.dto.LeagueResponse;

import java.util.List;
import java.util.UUID;

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

    @PostMapping("/join")
    public LeagueResponse join(@RequestBody JoinLeagueRequest req) {
        return leagueService.join(req.inviteCode());
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
}
