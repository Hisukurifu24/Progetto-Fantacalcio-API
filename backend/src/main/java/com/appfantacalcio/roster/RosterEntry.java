package com.appfantacalcio.roster;

import com.appfantacalcio.common.BaseEntity;
import com.appfantacalcio.player.Player;
import com.appfantacalcio.team.Team;

import jakarta.persistence.Entity;
import jakarta.persistence.ManyToOne;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
public class RosterEntry extends BaseEntity {

    @ManyToOne
    private Team team;

    @ManyToOne
    private Player player;

    private int acquiredFor;
}
