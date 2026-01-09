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

	@ManyToOne(optional = true)
	private Team homeTeam;

	@ManyToOne(optional = true)
	private Team awayTeam;

	private int matchDay;

	private String roundLabel; // e.g. "Quarter Final", "Semi Final"
	private Integer roundNumber; // 1, 2, 3...
	private Integer matchNumber; // 1, 2... in the round

	private String groupName; // e.g. "Group A", "Group B"

	private int homeGoals;

	private int awayGoals;

	private boolean played;
}
