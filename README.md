# Social Autopilot 🚀

**Automatisk publisering til Facebook og Instagram — bygget med Claude, GitHub og Meta API.**

Dette er malen fra AI Akseleratoren. Systemet poster karuseller til Facebook-siden
og Instagram-kontoen din 3 ganger i uka (+ stories 3 andre dager), helt automatisk.
Claude skriver tekstene i din stemme, GitHub kjører publiseringen — du godkjenner
innholdet ved å la det ligge, og stopper en post ved å slette mappen dens.

```
Google Drive (bildene dine)
      │  Claude henter og beskjærer
      ▼
assets/  ──►  queue/001-min-post/post.json   (bilder + tekst)
      │       GitHub Action (man/ons/fre kl. 08 UTC)
      ▼
Facebook-side + Instagram  ──►  posted/ (arkiv)
```

## Kom i gang

👉 **Følg [MEDLEMSGUIDE.md](MEDLEMSGUIDE.md)** — hele oppsettet steg for steg (ca. 45 min).

Kortversjonen:
1. Klikk **«Use this template»** øverst på denne siden → lag ditt eget repo (må være **Public**).
2. Åpne Claude Code / Cowork og lim inn prompten fra [CLAUDE-PROMPT.md](CLAUDE-PROMPT.md).
3. Gjør Meta-oppsettet sammen med Claude ([docs/SETUP-META.md](docs/SETUP-META.md)).
4. Test med dry run → fyr av første post → ferdig.

## Mappene

| Mappe | Hva |
|---|---|
| `assets/` | Ferdigbeskårne bilder (1080×1350 for feed, 1080×1920 i `assets/story/`) |
| `queue/` | Poster som venter — publiseres i rekkefølge man/ons/fre |
| `stories/` | Stories som venter — publiseres tir/tor/lør |
| `posted/` | Arkiv over alt som er publisert, med Meta-ID og tidspunkt |
| `scripts/` | `fetch_photos.py` (henter bilder fra Drive) og `publish.py` (poster via Meta API) |

## Viktig å vite

- **Repoet må være offentlig** — det er slik Meta henter bildene dine. Legg bare
  inn bilder du uansett skal publisere.
- **Ingen løpende kostnader** — GitHub Actions gratis-kvote holder i massevis.
- Stopp alt: Actions-fanen → disable workflow. Stopp én post: slett mappen dens i `queue/`.

Bygget i AI Akseleratoren 🇳🇴 — spørsmål? Ta det i Skool-communityet.
