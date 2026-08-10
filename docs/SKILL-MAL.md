# Valgfritt: Gjør påfyll til en Claude-skill

Vil du kunne si «fyll køen» til Claude og få en ferdig 2-ukers batch? Lag en skill:
opprett mappen `~/.claude/skills/min-social/` og legg denne i `SKILL.md`
(tilpass ALT i klammer):

```markdown
---
name: min-social
description: Generer en batch Instagram/Facebook-poster for [MERKEVARE] inn i køen
  i GitHub-repoet [DEG/ditt-repo]. Velger ubrukte bilder fra assets/, skriver
  captions i min stemme og pusher. Trigger på «fyll køen», «lag poster», «ny batch».
---

# [Merkevare] Social — batch-generator

Repo: `~/sti/til/ditt-repo` (GitHub: `DEG/ditt-repo`).
GitHub Action publiserer laveste nummer i `queue/` man/ons/fre og `stories/` tir/tor/lør.

## Arbeidsflyt
1. `git pull --rebase`
2. Finn ubrukte bilder: alt i `assets/` minus det som er referert i `queue/` og `posted/`.
   Færre enn 8 igjen? Kjør `python3 scripts/fetch_photos.py --folder [DRIVE-MAPPE-ID]`.
3. SE på bildene før du skriver — captions skal matche innholdet. 4–6 bilder per post.
4. Fyll `queue/` opp til 6 poster og `stories/` opp til 6 (9:16-bilder fra assets/story/).
5. Vis meg tekstene, så pusher du. Push = planlagt.

## Stemme-regler
- [SPRÅK]. [BESKRIV TONE — f.eks. varm, konkret, ingen hype-ord.]
- [SANNHETSREGLER — f.eks. aldri finn på kundeutsagn/tall.]
- CTA: [f.eks. «Send oss en melding».]
- 60–120 ord, luft mellom avsnitt, 5–10 hashtags: [DINE FASTE HASHTAGS].
- Roter vinkler: [f.eks. produkt / historie / kunde / bak kulissene / én-linjer].
```

Deretter kan du også be Claude lage en **ukentlig rutine** (scheduled task) som kjører
skillen i auto-modus hver søndag — da er hele systemet selvgående.
