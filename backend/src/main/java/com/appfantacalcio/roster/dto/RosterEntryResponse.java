package com.appfantacalcio.roster.dto;

import com.appfantacalcio.player.dto.PlayerResponse;
import java.util.UUID;

public record RosterEntryResponse(
    UUID id,
    UUID teamId,
    PlayerResponse player,
    int acquiredFor
) {}
