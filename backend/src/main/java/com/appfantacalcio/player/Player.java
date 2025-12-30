package com.appfantacalcio.player;

import java.util.UUID;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
// Only written by the scraper
public class Player {

    @Id
    private UUID id; // same id scraper-side

    private String name;
    private String role;
    private String realTeam;

    private int quotazioneClassico;
    private int quotazioneMantra;
}
