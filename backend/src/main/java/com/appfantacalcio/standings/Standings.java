package com.appfantacalcio.standings;

import com.appfantacalcio.common.BaseEntity;
import com.appfantacalcio.competition.Competition;
import com.appfantacalcio.team.Team;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import jakarta.persistence.Entity;
import jakarta.persistence.ManyToOne;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
@JsonIgnoreProperties({ "hibernateLazyInitializer", "handler" })
public class Standings extends BaseEntity {

	@ManyToOne(optional = false)
	@JsonIgnoreProperties("standings")
	private Competition competition;

	@ManyToOne(optional = false)
	@JsonIgnoreProperties({ "hibernateLazyInitializer", "handler" })
	private Team team;

	private int points;
	private int played;
	private int won;
	private int drawn;
	private int lost;
	private int goalsFor;
	private int goalsAgainst;
	private int goalDifference;

	// For "Sum of Points" competitions or tie-breakers
	private double fantaPoints;

	private String groupName;
}
