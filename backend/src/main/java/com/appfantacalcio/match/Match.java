package com.appfantacalcio.match;

import com.appfantacalcio.common.BaseEntity;
import com.appfantacalcio.competition.Competition;
import com.appfantacalcio.team.Team;

import jakarta.persistence.Entity;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
@Table(name = "matches")
public class Match extends BaseEntity {

	@ManyToOne(optional = false)
	private Competition competition;

	@ManyToOne(optional = false)
	private Team homeTeam;

	@ManyToOne(optional = false)
	private Team awayTeam;

	private int matchDay;

	private int homeGoals;

	private int awayGoals;

	private boolean played;
}
