import asyncio
import logging

from app.cache.supabase import get_supabase
from app.schemas import FormEvalJSON, MatchupEvalJSON, OddsRiskEvalJSON, FinalPredictionJSON
from app.schemas.base import GameContext

# ── reads ─────────────────────────────────────────────────────────────────────

def _fetch_form_sync(match_id: str, team_id: str) -> FormEvalJSON | None:
    res = get_supabase().table("form_cache") \
        .select("payload") \
        .eq("match_id", match_id) \
        .eq("team_id", team_id) \
        .limit(1) \
        .execute()
    if not res.data:
        return None
    return FormEvalJSON.model_validate(res.data[0]["payload"])


async def fetch_form(match_id: str, team_id: str) -> FormEvalJSON | None:
    try:
        result = await asyncio.to_thread(_fetch_form_sync, match_id, team_id)
        if result:
            logger.info("db: form_cache hit for %s/%s", match_id, team_id)
        else:
            logger.info("db: form_cache miss for %s/%s", match_id, team_id)
        return result
    except Exception as exc:
        logger.error("db: fetch_form failed for %s/%s: %s", match_id, team_id, exc)
        return None


def _fetch_matchup_sync(match_id: str) -> MatchupEvalJSON | None:
    res = get_supabase().table("matchup_cache") \
        .select("payload") \
        .eq("match_id", match_id) \
        .limit(1) \
        .execute()
    if not res.data:
        return None
    return MatchupEvalJSON.model_validate(res.data[0]["payload"])


async def fetch_matchup(match_id: str) -> MatchupEvalJSON | None:
    try:
        result = await asyncio.to_thread(_fetch_matchup_sync, match_id)
        if result:
            logger.info("db: matchup_cache hit for %s", match_id)
        else:
            logger.info("db: matchup_cache miss for %s", match_id)
        return result
    except Exception as exc:
        logger.error("db: fetch_matchup failed for %s: %s", match_id, exc)
        return None

logger = logging.getLogger(__name__)


# ── matches ───────────────────────────────────────────────────────────────────

def _save_match_sync(ctx: GameContext, fixture: dict) -> None:
    get_supabase().table("matches").upsert({
        "id":              ctx.game_id,
        "game_date":       ctx.game_date,
        "game_time":       fixture["Time"],
        "venue":           ctx.venue,
        "home_team_id":    ctx.home_team_id,
        "home_team_name":  fixture["Home team"]["name"],
        "away_team_id":    ctx.away_team_id,
        "away_team_name":  fixture["Away team"]["name"],
    }, on_conflict="id").execute()


async def save_match(ctx: GameContext, fixture: dict) -> None:
    try:
        await asyncio.to_thread(_save_match_sync, ctx, fixture)
        logger.info("db: match %s saved", ctx.game_id)
    except Exception as exc:
        logger.error("db: save_match failed for %s: %s", ctx.game_id, exc)


# ── form_cache ────────────────────────────────────────────────────────────────

def _save_form_sync(form: FormEvalJSON) -> None:
    get_supabase().table("form_cache").upsert({
        "match_id":                    form.game_id,
        "team_id":                     form.team_id,
        "team_name":                   form.team_name,
        "record":                      form.record,
        "last_10_record":              form.last_10_record,
        "last_10_offensive_rating":    form.last_10_offensive_rating,
        "last_10_defensive_rating":    form.last_10_defensive_rating,
        "last_10_rating_differential": form.last_10_rating_differential,
        "recent_game":                 form.recent_game.model_dump(),
        "payload":                     form.model_dump(),
    }, on_conflict="match_id,team_id").execute()


async def save_form(form: FormEvalJSON) -> None:
    try:
        await asyncio.to_thread(_save_form_sync, form)
        logger.info("db: form_cache saved for %s/%s", form.game_id, form.team_id)
    except Exception as exc:
        logger.error("db: save_form failed for %s/%s: %s", form.game_id, form.team_id, exc)


# ── matchup_cache ─────────────────────────────────────────────────────────────

def _save_matchup_sync(matchup: MatchupEvalJSON) -> None:
    get_supabase().table("matchup_cache").upsert({
        "match_id":    matchup.game_id,
        "last_h2h":    matchup.last_h2h.model_dump(),
        "h2h_last_10": [g.model_dump() for g in matchup.h2h_last_10],
        "payload":     matchup.model_dump(),
    }, on_conflict="match_id").execute()


async def save_matchup(matchup: MatchupEvalJSON) -> None:
    try:
        await asyncio.to_thread(_save_matchup_sync, matchup)
        logger.info("db: matchup_cache saved for %s", matchup.game_id)
    except Exception as exc:
        logger.error("db: save_matchup failed for %s: %s", matchup.game_id, exc)


# ── odds_snapshots ────────────────────────────────────────────────────────────

def _save_odds_snapshot_sync(odds_risk: OddsRiskEvalJSON) -> str:
    res = get_supabase().table("odds_snapshots").insert({
        "match_id":                  odds_risk.game_id,
        "moneyline_home":            odds_risk.moneyline_home,
        "moneyline_away":            odds_risk.moneyline_away,
        "spread":                    odds_risk.spread,
        "over_under":                odds_risk.over_under,
        "market_implied_prob_home":  odds_risk.market_implied_probability_home,
        "injury_report":             [e.model_dump() for e in odds_risk.injury_report],
        "payload":                   odds_risk.model_dump(),
    }).execute()
    return res.data[0]["id"]


async def save_odds_snapshot(odds_risk: OddsRiskEvalJSON) -> str | None:
    try:
        snapshot_id = await asyncio.to_thread(_save_odds_snapshot_sync, odds_risk)
        logger.info("db: odds_snapshot saved for %s (id=%s)", odds_risk.game_id, snapshot_id)
        return snapshot_id
    except Exception as exc:
        logger.error("db: save_odds_snapshot failed for %s: %s", odds_risk.game_id, exc)
        return None


# ── recommendations ───────────────────────────────────────────────────────────

def _save_recommendation_sync(prediction: FinalPredictionJSON, odds_snapshot_id: str) -> None:
    get_supabase().table("recommendations").insert({
        "match_id":                  prediction.game_id,
        "odds_snapshot_id":          odds_snapshot_id,
        "predicted_winner_id":       prediction.predicted_winner_id,
        "predicted_winner_name":     prediction.predicted_winner_name,
        "confidence":                prediction.confidence,
        "risk_rating":               prediction.risk_rating,
        "reasoning_narrative":       prediction.reasoning_narrative,
        "winner_odds":               prediction.odds_risk_report.winner_odds,
        "signal_disagreement_flag":  prediction.signal_disagreement_flag,
        "partial_telemetry":         prediction.partial_telemetry,
        "extended_thinking":         prediction.extended_thinking,
        "payload":                   prediction.model_dump(),
    }).execute()


async def save_recommendation(prediction: FinalPredictionJSON, odds_snapshot_id: str) -> None:
    try:
        await asyncio.to_thread(_save_recommendation_sync, prediction, odds_snapshot_id)
        logger.info("db: recommendation saved for %s", prediction.game_id)
    except Exception as exc:
        logger.error("db: save_recommendation failed for %s: %s", prediction.game_id, exc)
