# Notch

## Podcast / Music API Integration Options

**Spotify** — official API with OAuth; exposes listening history, recently played, playlists. Clean, stable integration.

**Pocket Casts** — no official API. Unofficial internal API at `api.pocketcasts.com` (reverse-engineered from web player). Requires email/password login + Bearer token; needs Pocket Casts Plus. Limitations: no listen timestamps, ~100 result history cap. Fragile — use with caution.
