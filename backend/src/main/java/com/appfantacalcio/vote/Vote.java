package com.appfantacalcio.vote;

import com.appfantacalcio.common.BaseEntity;
import com.appfantacalcio.player.Player;
import jakarta.persistence.Entity;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
@Table(name = "votes", uniqueConstraints = {
		@UniqueConstraint(columnNames = { "player_id", "match_day" })
})
public class Vote extends BaseEntity {

	@ManyToOne(optional = false)
	private Player player;

	private Integer matchDay;

	private Double vote; // Voto puro
	private Double fantaVote; // Fantavoto (voto + bonus/malus)

	private Integer goalsScored;
	private Integer goalsConceded;
	private Integer assists;
	private Integer yellowCards;
	private Integer redCards;
	private Integer penaltiesSaved;
	private Integer penaltiesMissed;
	private Integer ownGoals;
}
