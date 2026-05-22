-- CourMind initial schema
-- Run this in: Supabase Dashboard → SQL Editor

-- ── matches ──────────────────────────────────────────────────────────────────
create table if not exists matches (
    id              text primary key,
    game_date       date not null,
    game_time       timestamptz not null,
    venue           text not null,
    home_team_id    text not null,
    home_team_name  text not null,
    away_team_id    text not null,
    away_team_name  text not null,
    created_at      timestamptz not null default now()
);

-- ── form_cache ────────────────────────────────────────────────────────────────
create table if not exists form_cache (
    id                          uuid primary key default gen_random_uuid(),
    match_id                    text not null references matches(id) on delete cascade,
    team_id                     text not null,
    team_name                   text not null,
    record                      text not null,
    last_10_record              text not null,
    last_10_offensive_rating    numeric(6,2) not null,
    last_10_defensive_rating    numeric(6,2) not null,
    last_10_rating_differential numeric(6,2) not null,
    recent_game                 jsonb not null,
    payload                     jsonb not null,
    created_at                  timestamptz not null default now(),
    unique (match_id, team_id)
);

create index if not exists form_cache_match_id_idx on form_cache(match_id);

-- ── matchup_cache ─────────────────────────────────────────────────────────────
create table if not exists matchup_cache (
    id          uuid primary key default gen_random_uuid(),
    match_id    text not null references matches(id) on delete cascade unique,
    last_h2h    jsonb not null,
    h2h_last_10 jsonb not null,
    payload     jsonb not null,
    created_at  timestamptz not null default now()
);

-- ── odds_snapshots ────────────────────────────────────────────────────────────
create table if not exists odds_snapshots (
    id                          uuid primary key default gen_random_uuid(),
    match_id                    text not null references matches(id) on delete cascade,
    moneyline_home              numeric(8,3) not null,
    moneyline_away              numeric(8,3) not null,
    spread                      numeric(6,2) not null,
    over_under                  numeric(6,2) not null,
    market_implied_prob_home    numeric(5,4) not null,
    injury_report               jsonb not null,
    payload                     jsonb not null,
    created_at                  timestamptz not null default now()
);

create index if not exists odds_snapshots_match_id_idx on odds_snapshots(match_id);
create index if not exists odds_snapshots_match_time_idx on odds_snapshots(match_id, created_at desc);

-- ── recommendations ───────────────────────────────────────────────────────────
create table if not exists recommendations (
    id                       uuid primary key default gen_random_uuid(),
    match_id                 text not null references matches(id) on delete cascade,
    odds_snapshot_id         uuid not null references odds_snapshots(id) on delete restrict,
    predicted_winner_id      text not null,
    predicted_winner_name    text not null,
    confidence               numeric(4,3) not null,
    risk_rating              text not null check (risk_rating in ('LOW', 'MEDIUM', 'HIGH')),
    reasoning_narrative      text not null,
    winner_odds              numeric(8,3),
    signal_disagreement_flag boolean not null default false,
    partial_telemetry        boolean not null default false,
    extended_thinking        boolean not null default false,
    payload                  jsonb not null,
    created_at               timestamptz not null default now()
);

create index if not exists recommendations_match_id_idx on recommendations(match_id);
create index if not exists recommendations_match_time_idx on recommendations(match_id, created_at desc);
