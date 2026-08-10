# Meta-oppsettet — én gang, ~20 minutter

Målet: tre verdier inn som GitHub-secrets — `META_TOKEN`, `FB_PAGE_ID`, `IG_USER_ID`.
Gjør dette sammen med Claude (lim inn CLAUDE-PROMPT.md først), så gjør Claude
API-kallene for deg.

## 0. Sjekk forutsetningene (spar deg selv for hodebry)

- Instagram-kontoen er **profesjonell** (Innstillinger → Kontotype og verktøy → Bytt).
- Instagram er **koblet til Facebook-siden**: Siden → Innstillinger → Tilkoblede
  kontoer → Instagram → Koble til.
- Du har **full kontroll** på Facebook-siden (ikke bare «delvis tilgang»).
- Du **kan Facebook-passordet ditt** (Meta spør etter det underveis).

## 1. Lag en Meta-app (5 min)

1. [developers.facebook.com/apps](https://developers.facebook.com/apps) → **Create app**.
2. Huk av begge disse use casene:
   - ✅ **Manage everything on your Page**
   - ✅ **Manage messaging & content on Instagram**
3. Navn: f.eks. `min-social-autopilot` → koble til business-porteføljen din hvis du har
   → **Create app**.
4. Noter **App-ID** (står øverst i app-dashbordet).
5. Du trenger IKKE App Review for å poste til egne sider/kontoer — men appen MÅ
   settes **Live** (se steg 1b), ellers ser bare du postene dine!

## 1b. Sett appen LIVE (viktig — ellers er postene usynlige for følgerne!)

I Development mode publiseres poster «vellykket», men Facebook viser dem kun til
deg som app-admin. Du oppdager det ikke selv — men følgerne ser ingenting.

1. Live-bryteren krever en **gyldig Privacy policy URL**. Har du ingen ekte
   personvernside? Tilpass `docs/privacy-policy-MAL.html` i repoet ditt (bytt navn,
   nettside og e-post) og be Claude aktivere **GitHub Pages** for repoet
   (Settings → Pages → main branch, /docs-mappen — eller be Claude gjøre det via
   `gh api`). Da får du en URL som `https://DEG.github.io/ditt-repo/privacy-policy-MAL.html`.
2. App settings → Basic → lim URL-en i **Privacy policy URL** → **Save changes**.
3. Flipp **App Mode**-bryteren øverst fra Development til **Live** → bekreft.
4. Sjekk siden din fra en annen konto (eller be en venn) — nå skal postene synes.

## 2. Hent tokenen (5 min)

Be Claude lage godkjennings-lenken for deg (bytt inn din App-ID):

```
https://www.facebook.com/v21.0/dialog/oauth?client_id=DIN_APP_ID&redirect_uri=https%3A%2F%2Fdevelopers.facebook.com%2Ftools%2Fexplorer%2Fcallback&response_type=token&scope=pages_show_list%2Cpages_read_engagement%2Cpages_manage_posts%2Cinstagram_basic%2Cinstagram_content_publish&auth_type=rerequest&display=page
```

> ⚠️ **IKKE legg til `business_management` i scope-listen.** Har du mange bedrifts-
> porteføljer, gjør den tillatelsen at «Fortsett»-knappen i dialogen låser seg.

I dialogen som åpnes:
1. **Continue as [deg]**
2. Velg **Instagram-kontoen din** → Next
3. Velg **Facebook-siden din** → Next (💡 her ser du den EKTE side-ID-en —
   den er ikke det samme som tallet i nettadressen til siden!)
4. **Done** → **OK**

Du lander i Graph API Explorer. Klikk **kopier-ikonet** 📋 i Access Token-feltet
øverst til høyre, og lim tokenen til Claude.

## 3. Gjør tokenen permanent (Claude gjør dette — 2 min)

Tokenen fra steg 2 dør etter 1–2 timer. Claude veksler den slik:

1. Du henter **App secret**: App-dashbordet → App settings → Basic → App secret →
   **Show** (krever Facebook-passordet) → lim til Claude.
2. Claude kjører vekslingen:
   - `GET /oauth/access_token?grant_type=fb_exchange_token&client_id=...&client_secret=...&fb_exchange_token=<din token>` → langlevd bruker-token
   - `GET /me/accounts?fields=access_token` → **permanent side-token** (utløper aldri)
   - `GET /<side-id>?fields=instagram_business_account` → **IG_USER_ID**
3. Claude verifiserer med `debug_token` at `expires_at: 0` (= aldri).

> ⚠️ Ikke bruk «Extend Access Token»-knappen i Access Token Debugger — den henger
> ofte evig. fb_exchange_token-veien over virker alltid.

## 4. Legg inn secrets (Claude gjør dette)

```bash
gh secret set META_TOKEN  --repo DEG/ditt-repo   # den permanente side-tokenen
gh secret set FB_PAGE_ID  --repo DEG/ditt-repo   # side-ID fra steg 2
gh secret set IG_USER_ID  --repo DEG/ditt-repo   # fra steg 3
```

## 5. Test

GitHub → Actions → **Publish next social post** → Run workflow → **dry run ✔**.
Grønn? Kjør uten dry run → første post er live. 🎉

## Feil?

- **Auth-feil i Action** → token er feil/utløpt: gjenta steg 2–4.
- **(#200) permission error** → Instagram-kontoen var ikke valgt i dialogen, eller
  er ikke koblet til siden: fiks koblingen og gjenta steg 2.
- **Bilder lastes ikke** → er repoet ditt **Public**? Meta må kunne hente raw-URL-ene.
