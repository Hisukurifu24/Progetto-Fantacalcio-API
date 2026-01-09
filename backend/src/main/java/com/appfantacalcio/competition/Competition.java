package com.appfantacalcio.competition;

import com.appfantacalcio.common.BaseEntity;
import com.appfantacalcio.league.League;
import com.appfantacalcio.match.Match;
import com.appfantacalcio.standings.Standings;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import lombok.Getter;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;

@Entity
@Getter
@Setter
@JsonIgnoreProperties({ "hibernateLazyInitializer", "handler" })
public class Competition extends BaseEntity {

	@ManyToOne(optional = false)
	@JsonIgnoreProperties({ "maxPlayersPerRole", "benchLimits", "members", "createdBy", "hibernateLazyInitializer",
			"handler" })
	private League league;

	private String name;

	@Enumerated(EnumType.STRING)
	private CompetitionType type;

	private int startDay;
	private int endDay;

	@jakarta.persistence.ManyToMany(fetch = jakarta.persistence.FetchType.EAGER)
	@JsonIgnoreProperties({ "hibernateLazyInitializer", "handler", "league" })
	private List<com.appfantacalcio.team.Team> participants = new ArrayList<>();

	@OneToMany(mappedBy = "competition", cascade = CascadeType.ALL, orphanRemoval = true)
	@JsonIgnore
	private List<Match> matches = new ArrayList<>();

	@OneToMany(mappedBy = "competition", cascade = CascadeType.ALL, orphanRemoval = true)
	@JsonIgnore
	private List<Standings> standings = new ArrayList<>();
}
