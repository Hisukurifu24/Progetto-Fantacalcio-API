package com.appfantacalcio.league;

import com.appfantacalcio.user.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface LeagueRepository extends JpaRepository<League, UUID> {
    Optional<League> findByInviteCode(String inviteCode);

    Optional<League> findByName(String name);

    @org.springframework.data.jpa.repository.Query("SELECT DISTINCT l FROM League l LEFT JOIN FETCH l.members LEFT JOIN FETCH l.createdBy WHERE :user MEMBER OF l.members")
    List<League> findAllByMembersContaining(@org.springframework.data.repository.query.Param("user") User user);

    @org.springframework.data.jpa.repository.Query("SELECT DISTINCT l FROM League l LEFT JOIN FETCH l.members LEFT JOIN FETCH l.createdBy WHERE l.isPublic = true")
    List<League> findAllByIsPublicTrue();
}