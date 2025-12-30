package com.appfantacalcio.team;

import com.appfantacalcio.common.BaseEntity;
import com.appfantacalcio.league.League;
import com.appfantacalcio.user.User;

import jakarta.persistence.Entity;
import jakarta.persistence.ManyToOne;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
public class Team extends BaseEntity {

    private String name;

    @ManyToOne
    private User owner;

    @ManyToOne
    private League league;
}
