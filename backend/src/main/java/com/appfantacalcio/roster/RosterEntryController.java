package com.appfantacalcio.roster;

import com.appfantacalcio.roster.dto.CreateRosterEntryRequest;
import com.appfantacalcio.roster.dto.RosterEntryResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/roster-entries")
@RequiredArgsConstructor
public class RosterEntryController {

    private final RosterEntryService rosterEntryService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public RosterEntryResponse create(@RequestBody CreateRosterEntryRequest request) {
        return rosterEntryService.create(request);
    }

    @GetMapping("/team/{teamId}")
    public List<RosterEntryResponse> getByTeam(@PathVariable UUID teamId) {
        return rosterEntryService.findByTeam(teamId);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable UUID id) {
        rosterEntryService.delete(id);
    }
}
