package com.appfantacalcio.roster.dto;

import java.util.UUID;

public record CreateRosterEntryRequest(
    UUID teamId,
    UUID playerId,
    int acquiredFor
) {}
