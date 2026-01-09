package com.appfantacalcio.player.dto;

import java.util.UUID;

public record PlayerResponse(
                UUID id,
                String nome,
                String ruolo,
                String squadra,
                Integer quotazione_iniziale_classico,
                Integer quotazione_attuale_classico,
                Integer quotazione_iniziale_mantra,
                Integer quotazione_attuale_mantra,
                Integer fvm_classico,
                Integer fvm_mantra,
                String fanta_squadra) {
}
