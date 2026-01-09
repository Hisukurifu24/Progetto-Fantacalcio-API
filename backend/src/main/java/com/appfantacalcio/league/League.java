package com.appfantacalcio.league;

import com.appfantacalcio.common.BaseEntity;
import com.appfantacalcio.user.User;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.ManyToOne;
import lombok.Getter;
import lombok.Setter;

import java.util.Set;
import java.util.Map;
import jakarta.persistence.ManyToMany;
import jakarta.persistence.ElementCollection;

@Entity
@Getter
@Setter
@JsonIgnoreProperties({ "hibernateLazyInitializer", "handler" })
public class League extends BaseEntity {

    private String name;

    private boolean isPublic;

    @Column(unique = true)
    private String inviteCode;

    private Integer startDay;
    private Integer maxBudget;

    @ElementCollection
    private Map<String, Integer> maxPlayersPerRole;

    @ElementCollection
    private Map<String, Integer> benchLimits;

    @ManyToOne(fetch = FetchType.LAZY)
    private User createdBy;

    @ManyToMany
    private Set<User> members;
}
