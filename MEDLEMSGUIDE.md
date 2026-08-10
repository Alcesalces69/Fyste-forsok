# Bygg din egen Social Autopilot — steg for steg

Ca. 45 minutter fra start til første automatiske post. Du trenger ikke kunne kode —
Claude gjør det tekniske, du gjør klikkene som krever innlogging.

## Det du trenger før du starter

- [ ] **GitHub-konto** (gratis: github.com → Sign up)
- [ ] **Claude** med Claude Code eller Cowork (og GitHub koblet til — Claude hjelper deg med `gh auth login`)
- [ ] **En Facebook-SIDE** (ikke bare profil) som DU administrerer med **full kontroll**
- [ ] **En Instagram-konto** som er **profesjonell** (Bedrift/Creator) og **koblet til Facebook-siden**
- [ ] **En Google Drive-mappe med bilder**, delt som «Alle med lenken kan se»

> ⚠️ **De fire tingene folk snubler på — sjekk dem FØRST:**
> 0. **Appen din må settes LIVE før første post** — i Development mode publiseres
>    postene, men Facebook viser dem KUN til deg. Følgerne dine ser ingenting, og
>    du merker det ikke selv! Live-bryteren krever en gyldig personvernerklærings-URL —
>    malen inneholder en ferdig side (`docs/privacy-policy-MAL.html`) du kan hoste
>    gratis via GitHub Pages (be Claude fikse det — 2 min). Detaljer i SETUP-META.md.
> 1. **Instagram må være koblet til Facebook-siden.** Sjekk: Facebook-siden → Innstillinger
>    → Tilkoblede kontoer → Instagram. Ikke koblet = ingenting virker.
> 2. **Ikke lag en splitter ny Instagram-konto samme dag** — nye kontoer blir ofte
>    midlertidig sperret («restricted») når de kobles til API-er med en gang. Bruk en
>    konto som har levd noen uker, eller la den nye modne først.
> 3. **Du må kunne Facebook-passordet ditt** — Meta spør etter det underveis. Sjekk nå,
>    ikke midt i oppsettet. (Glemt? Tilbakestill via accountscenter.facebook.com først.)

## Steg 1 — Kopier malen (2 min)

1. Gå til mal-repoet (lenken har du fått i Skool).
2. Klikk den grønne knappen **«Use this template» → «Create a new repository»**.
3. Navn: f.eks. `min-social-autopilot`. Velg **Public** (viktig!). → **Create repository**.

## Steg 2 — La Claude rigge alt (10 min)

1. Åpne **Claude Code** (eller Cowork) på maskinen din.
2. Åpne filen `CLAUDE-PROMPT.md` i repoet ditt, kopier hele prompten, lim inn til
   Claude — og **fyll inn dine detaljer** øverst (repo-navn, Drive-lenke, merkevare-stemme).
3. Claude kloner repoet, henter bildene fra Drive, ser på dem, skriver captions i din
   stemme og fyller køen med de to første ukene. Du godkjenner tekstene i chatten.

## Steg 3 — Meta-oppsettet (20 min, sammen med Claude)

Dette er den eneste «voksne» delen. Følg `docs/SETUP-META.md` i repoet ditt —
Claude leder deg gjennom hvert klikk. Grovt:

1. **Lag en Meta-app** på developers.facebook.com (use case: «Manage everything on
   your Page» + «Manage messaging & content on Instagram»).
2. **Hent en token** via en godkjennings-dialog Claude gir deg lenken til.
   > ⚠️ IKKE ta med tillatelsen `business_management` — den får «Fortsett»-knappen
   > til å henge for mange kontoer. Malen bruker riktig liste.
3. I dialogen: velg **din side** og **din Instagram-konto**, godkjenn alt.
4. Lim tokenen til Claude → Claude veksler den til en **permanent** token og legger
   inn de tre hemmelighetene i GitHub (`META_TOKEN`, `FB_PAGE_ID`, `IG_USER_ID`).
   > 💡 Side-ID-en er IKKE tallet i nettadressen til siden din — Claude henter den
   > riktige fra API-et.

## Steg 4 — Test og fyr av (5 min)

1. GitHub → repoet ditt → **Actions** → «Publish next social post» → **Run workflow**
   med **dry run ✔** → skal bli grønn.
2. Kjør igjen **uten** dry run → første post publiseres på ordentlig. Sjekk siden din! 🎉

## Steg 5 — Sett den på autopilot

- Publiseringen går av seg selv: **man/ons/fre** (feed) og **tir/tor/lør** (stories).
- Be Claude sette opp en **ukentlig rutine** som fyller køen (be den «lag en scheduled
  task som fyller køen til 6 poster hver søndag»). Eller si «fyll køen» til Claude manuelt
  når du har lyst.
- Nye bilder? Bare slipp dem i Drive-mappen — de plukkes opp neste påfyll.

## Feilsøking

| Problem | Løsning |
|---|---|
| Action feiler med «Missing media» | Bildefilen i post.json finnes ikke i `assets/` — sjekk stavemåte |
| Action feiler med auth-feil | Token er ugyldig — kjør token-flyten i SETUP-META.md på nytt |
| Instagram-posten kommer ikke | Er IG-kontoen profesjonell OG koblet til siden? Er `IG_USER_ID` satt? |
| «Fortsett»-knappen i Meta-dialogen er grå | Du har `business_management` i tillatelsene — fjern den |
| Ny IG-konto «restricted» | Verifiser i appen (Kontostatus), vent noen dager, prøv igjen |
