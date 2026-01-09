package com.appfantacalcio.team;

import com.appfantacalcio.common.BaseEntity;
import com.appfantacalcio.league.League;
import com.appfantacalcio.user.User;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import jakarta.persistence.Entity;
import jakarta.persistence.ManyToOne;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
@JsonIgnoreProperties({ "hibernateLazyInitializer", "handler" })
public class Team extends BaseEntity {

    private String name;

    private String coachName;

    @ManyToOne
    private User owner;

    @ManyToOne
    @JsonIgnoreProperties({ "maxPlayersPerRole", "benchLimits", "members", "createdBy" })
    private League league;
}
