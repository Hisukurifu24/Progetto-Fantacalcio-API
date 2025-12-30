package com.appfantacalcio.competition;

import com.appfantacalcio.common.BaseEntity;
import com.appfantacalcio.league.League;

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.ManyToOne;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
public class Competition extends BaseEntity {

	@ManyToOne(optional = false)
	private League league;

	@Enumerated(EnumType.STRING)
	private CompetitionType type;

	private int startDay;
	private int endDay;
}
