package com.appfantacalcio.league;

import com.appfantacalcio.common.BaseEntity;
import com.appfantacalcio.user.User;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.ManyToOne;
import lombok.Getter;
import lombok.Setter;

import java.util.Set;
import jakarta.persistence.ManyToMany;

@Entity
@Getter
@Setter
public class League extends BaseEntity {

    private String name;

    private boolean isPublic;

    @Column(unique = true)
    private String inviteCode;

    @ManyToOne(fetch = FetchType.LAZY)
    private User createdBy;

    @ManyToMany
    private Set<User> members;
}
