-- CourMind auth schema
-- Run this in: Supabase Dashboard → SQL Editor

create table if not exists users (
    id              uuid primary key default gen_random_uuid(),
    email           text unique not null,
    hashed_password text not null,
    created_at      timestamptz not null default now()
);
