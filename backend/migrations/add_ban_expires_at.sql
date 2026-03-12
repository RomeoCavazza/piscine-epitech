-- Migration: add expires_at to server_bans for temporary bans
ALTER TABLE server_bans ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ;
