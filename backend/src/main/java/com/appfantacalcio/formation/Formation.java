package com.appfantacalcio.formation;

import com.appfantacalcio.common.BaseEntity;
import com.appfantacalcio.player.Player;
import com.appfantacalcio.team.Team;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Entity
@Getter
@Setter
public class Formation extends BaseEntity {

	@ManyToOne
	private Team team;

	private Integer matchDay;

	private String module;

	@ManyToOne
	private Player goalkeeper;

	@ManyToMany
	@OrderColumn(name = "display_order")
	@JoinTable(name = "formation_defenders", joinColumns = @JoinColumn(name = "formation_id"), inverseJoinColumns = @JoinColumn(name = "player_id"))
	private List<Player> defenders;

	@ManyToMany
	@OrderColumn(name = "display_order")
	@JoinTable(name = "formation_midfielders", joinColumns = @JoinColumn(name = "formation_id"), inverseJoinColumns = @JoinColumn(name = "player_id"))
	private List<Player> midfielders;

	@ManyToMany
	@OrderColumn(name = "display_order")
	@JoinTable(name = "formation_forwards", joinColumns = @JoinColumn(name = "formation_id"), inverseJoinColumns = @JoinColumn(name = "player_id"))
	private List<Player> forwards;

	@ManyToMany
	@OrderColumn(name = "display_order")
	@JoinTable(name = "formation_bench", joinColumns = @JoinColumn(name = "formation_id"), inverseJoinColumns = @JoinColumn(name = "player_id"))
	private List<Player> bench;
}
