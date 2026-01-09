package com.appfantacalcio.vote;

import com.appfantacalcio.player.Player;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface VoteRepository extends JpaRepository<Vote, UUID> {
	Optional<Vote> findByPlayerAndMatchDay(Player player, Integer matchDay);

	List<Vote> findByMatchDay(Integer matchDay);

	@Query("SELECT MAX(v.matchDay) FROM Vote v")
	Integer findMaxMatchDay();
}
