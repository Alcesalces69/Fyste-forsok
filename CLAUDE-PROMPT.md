# Prompt til Claude — kopier alt under linjen, fyll inn dine detaljer, lim inn i Claude Code

---

Jeg vil sette opp Social Autopilot — automatisk publisering til Facebook og Instagram
via GitHub Actions og Meta Graph API. Jeg har allerede laget mitt eget repo fra malen.

**Mine detaljer:**
- Mitt GitHub-repo: `MITT-BRUKERNAVN/min-social-autopilot`
- Google Drive-mappe med bilder (delt «alle med lenken»): `LIM INN LENKE HER`
- Facebook-siden min heter: `NAVN PÅ SIDEN`
- Instagram-kontoen min: `@MIN-KONTO` (profesjonell, koblet til siden)
- Merkevaren min / hva jeg driver med: `BESKRIV KORT — f.eks. «yogastudio i Bergen for
  travle småbarnsforeldre»`
- Stemme og stil for tekstene: `f.eks. «varm, jordnær, ingen hype, norsk. Del små
  historier fra hverdagen. CTA: send oss en melding.»`
- Språk på postene: `norsk / engelsk`

**Gjør dette, steg for steg, og forklar underveis:**

1. Klon repoet mitt lokalt og se på strukturen (`scripts/`, `queue/`, `.github/workflows/`).
2. Kjør `python3 scripts/fetch_photos.py --folder <mappe-id>` for å hente bildene mine
   fra Drive (og `--story`-varianten for stories-format). Mappe-ID-en er den lange koden
   i Drive-lenken min.
3. SE på bildene (åpne dem), grupper 4–6 bilder per post som forteller én liten historie,
   og skriv engasjerende captions i stemmen min beskrevet over. Lag 6 feed-poster i
   `queue/` og 6 stories i `stories/` etter formatet i README. Vis meg tekstene før du pusher.
4. Push alt til GitHub.
5. Led meg gjennom Meta-oppsettet i `docs/SETUP-META.md` — klikk for klikk. Du kan gjerne
   styre nettleseren min hvis jeg har Chrome-utvidelsen. VIKTIG: ikke ta med
   `business_management` i tillatelsene, og hent side-ID-en fra API-et (ikke fra URL-en).
6. Når jeg limer inn tokenen: veksle den til en permanent page-token
   (fb_exchange_token-flyten), finn `IG_USER_ID` via `instagram_business_account`-feltet,
   og sett de tre GitHub-secrets med `gh secret set`: META_TOKEN, FB_PAGE_ID, IG_USER_ID.
7. Kjør en dry run av workflowen «Publish next social post» og vis meg at den er grønn.
8. Spør meg om jeg vil fyre av første post på ordentlig — og gjør det når jeg sier ja.
9. Til slutt: foreslå en ukentlig planlagt rutine som fyller køen automatisk hver søndag
   (opptil 6 poster + 6 stories, aldri gjenbruk brukte bilder), og sett den opp hvis jeg vil.

Hvis noe feiler: forklar hva som skjedde på vanlig norsk og foreslå neste steg.
Ikke finn på fakta i captions — bruk bare det jeg har fortalt deg og det du ser i bildene.
