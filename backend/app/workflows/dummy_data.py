from app.schemas import (
    FinalPredictionJSON,
    FormEvalJSON,
    FormWorkflowJSON,
    H2HGame,
    InjuryEntry,
    MatchupEvalJSON,
    MatchupWorkflowJSON,
    OddsRiskEvalJSON,
    OddsRiskWorkflowJSON,
)
# ─── FORMS ───────────────────────────────────────────────────────────────


_DUMMY_FORMS: dict[str, FormEvalJSON] = {
    "LAL": FormEvalJSON(
        game_id="LAL_GSW",
        team_id="LAL",
        team_name="Los Angeles Lakers",
        last_10_wins=4, last_10_losses=6, last_10_record="4-6",
        home_wins=2, home_losses=3, home_record="2-3",
        away_wins=2, away_losses=3, away_record="2-3",
        record="4-6",
        last_10_offensive_rating=110.4,
        seed=4,
        last_10_defensive_rating=114.2,
        last_10_rating_differential=-3.8,
        offensive_rating=120.4,
        defensive_rating=124.2,
        rating_differential=-3.8,
        recent_game=H2HGame(
            date="2026-05-12",
            home_team_id="1610612760",
            away_team_id="1610612747",
            home_score=115,
            away_score=110,
            winner_team_id="1610612760",
        ),
    ),
    "GSW": FormEvalJSON(
        game_id="LAL_GSW",
        team_id="GSW",
        team_name="Golden State Warriors",
        last_10_wins=6, last_10_losses=4, last_10_record="6-4",
        home_wins=5, home_losses=2, home_record="5-2",
        away_wins=3, away_losses=3, away_record="3-3",
        record="8-5",
        seed=6,
        last_10_offensive_rating=118.2,
        last_10_defensive_rating=112.5,
        last_10_rating_differential=5.7,
        offensive_rating=128.2,
        defensive_rating=122.5,
        rating_differential=5.7,
        recent_game=H2HGame(
            date="2026-05-20",
            home_team_id="1610612744",
            away_team_id="1610612760",
            home_score=112,
            away_score=108,
            winner_team_id="1610612744",
        ),
    ),
}

# ─── Matches ───────────────────────────────────────────────────────────────

_DUMMY_MATCHUPS: list[MatchupEvalJSON] = [
    MatchupEvalJSON(
        game_id="LAL_GSW",
        last_h2h=H2HGame(
            date="2026-03-08",
            home_team_id="GSW",
            away_team_id="LAL",
            home_score=118,
            away_score=112,
            winner_team_id="GSW",
        ),
        h2h_last_10=[
            H2HGame(
                date="2026-03-08",
                home_team_id="GSW",
                away_team_id="LAL",
                home_score=118,
                away_score=112,
                winner_team_id="GSW",
            ),
            H2HGame(
                date="2026-01-25",
                home_team_id="LAL",
                away_team_id="GSW",
                home_score=105,
                away_score=112,
                winner_team_id="GSW",
            ),
            H2HGame(
                date="2025-12-15",
                home_team_id="GSW",
                away_team_id="LAL",
                home_score=121,
                away_score=115,
                winner_team_id="GSW",
            ),
            H2HGame(
                date="2025-10-30",
                home_team_id="LAL",
                away_team_id="GSW",
                home_score=110,
                away_score=104,
                winner_team_id="LAL",
            ),
            H2HGame(
                date="2025-04-05",
                home_team_id="GSW",
                away_team_id="LAL",
                home_score=128,
                away_score=120,
                winner_team_id="GSW",
            ),
            H2HGame(
                date="2025-03-12",
                home_team_id="LAL",
                away_team_id="GSW",
                home_score=114,
                away_score=122,
                winner_team_id="GSW",
            ),
            H2HGame(
                date="2025-01-18",
                home_team_id="GSW",
                away_team_id="LAL",
                home_score=109,
                away_score=113,
                winner_team_id="LAL",
            ),
            H2HGame(
                date="2024-12-25",
                home_team_id="LAL",
                away_team_id="GSW",
                home_score=124,
                away_score=118,
                winner_team_id="LAL",
            ),
            H2HGame(
                date="2024-04-09",
                home_team_id="LAL",
                away_team_id="GSW",
                home_score=120,
                away_score=134,
                winner_team_id="GSW",
            ),
            H2HGame(
                date="2024-03-16",
                home_team_id="LAL",
                away_team_id="GSW",
                home_score=121,
                away_score=128,
                winner_team_id="GSW",
            ),
        ],
    )
]

# ─── Prediction ───────────────────────────────────────────────────────────────

_DUMMY_PREDICTION = FinalPredictionJSON(
    game_id="LAL_GSW",
    predicted_winner_id="GSW",
    predicted_winner_name="Golden State Warriors",
    confidence=0.63,
    risk_rating="MEDIUM",
    reasoning_narrative=(
        "GSW's +5.7 net rating, 7-3 H2H dominance, and -155 market line collectively outweigh LAL's "
        "compromised roster — Doncic OUT strips their primary creation engine while Curry anchors GSW's spacing. "
        "Moderate confidence (0.63) reflects Podziemski's absence and Kuminga's questionable status introducing "
        "bilateral roster risk, but form, matchup history, and market consensus align on a GSW home win."
    ),
    form_report=FormWorkflowJSON(
        confidence=0.68,
        workflow_weight=0.40,
        winner_form="GSW 6-4, +5.7 net",
        loser_form="LAL 4-6, -3.8 net",
        key_context="Doncic OUT, LAL depleted",
    ),
    matchup_report=MatchupWorkflowJSON(
        confidence=0.71,
        workflow_weight=0.35,
        last_match="GSW 118-112 Mar-8",
        last_ten_matches="GSW leads 7-3",
        net_differential="GSW +4.2 avg",
    ),
    odds_risk_report=OddsRiskWorkflowJSON(
        confidence=0.61,
        workflow_weight=0.25,
        winner_odds=1.8,
        key_context=[
            "GSW -155, 60.8% implied",
            "Spread -3.5 GSW",
            "Doncic OUT LAL",
            "Podziemski OUT GSW",
            "Kuminga QUESTIONABLE GSW",
            "O/U 224.5",
        ],
    ),
    signal_disagreement_flag=False,
    partial_telemetry=False,
    extended_thinking=False,
)

# ─── ODDS & RISKS ───────────────────────────────────────────────────────────────

_DUMMY_ODDS_RISKS: list[OddsRiskEvalJSON] = [
    OddsRiskEvalJSON(
        game_id="LAL_GSW",
        moneyline_home=-155.0,
        moneyline_away=135.0,
        spread=-3.5,
        over_under=224.5,
        market_implied_probability_home=60.8,
        injury_report=[
            InjuryEntry(
                player_name="Luka Doncic",
                team_id="LAL",
                status="OUT",
                impact_note="Sidelined for the entire second round of the playoffs due to a severe injury. Significantly shifts offensive creation burden to secondary playmakers."
            ),
            InjuryEntry(
                player_name="Jonathan Kuminga",
                team_id="GSW",
                status="QUESTIONABLE",
                impact_note="Day-to-day following mild ankle soreness during game 2 of the WCF. Potential limit to frontcourt athleticism and transition versatility if restricted."
            ),
            InjuryEntry(
                player_name="Brandin Podziemski",
                team_id="GSW",
                status="OUT",
                impact_note="Sidelined for the remainder of the series due to a non-displaced wrist fracture. Thins out backcourt depth and secondary playmaking rotations."
            ),
            InjuryEntry(
                player_name="Austin Reaves",
                team_id="LAL",
                status="AVAILABLE",
                impact_note="Fully cleared, no structural or physical limitations. Expected to shoulder heavy volume and primary scoring responsibility."
            ),
            InjuryEntry(
                player_name="Stephen Curry",
                team_id="GSW",
                status="AVAILABLE",
                impact_note="Fully cleared, managing standard veteran recovery schedules between games. Anchors the primary spacing engine."
            ),
            InjuryEntry(
                player_name="LeBron James",
                team_id="LAL",
                status="AVAILABLE",
                impact_note="Fully cleared, handling veteran workload management cleanly. Anticipated high usage rate in high-leverage positions."
            )
        ]
    )
]
