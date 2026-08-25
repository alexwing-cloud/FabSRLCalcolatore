# Vaglio Deal — FAB S.r.l.

Cruscotto per decidere se prendere o no un blocco di appartamenti in affitto con
facoltà di sublocazione. Un file solo, `index.html`: si apre con doppio clic, non
serve installare niente e funziona anche offline.

## La regola che comanda

**Canone ≤ 25% del fatturato lordo IVA compresa.** È il primo dei controlli che
possono bocciare un deal da soli. Le altre soglie si cambiano dal pannello
"Le tue soglie" senza toccare il codice.

## Come è organizzata la valutazione

| Livello | Cosa misura | Perché |
|---|---|---|
| 1 · Screening | canone/lordo, numero di appartamenti | scarta in dieci secondi |
| 2 · Redditività | margine operativo, utile netto, utile per appartamento | quanto rende |
| 3 · Rischio | pareggio, margine di sicurezza, cassa assorbita, rientro capex | quanto può andare storto |
| 4 · Portafoglio | peso del blocco sul fatturato totale | quanto ti espone |

## I due preset

`Carica Venezian` e `Carica Machiavelli` ricostruiscono i due conti economici del
file `STAY_Host_Hub_OKR`. Servono da metro di paragone: il modello riproduce i
loro margini entro lo 0,3%. Machiavelli, alla soglia del 25%, viene bocciato —
è il punto: la soglia è più severa del portafoglio esistente.

## Dentro il file

`index.html` contiene tre cose, in quest'ordine:

1. **`<style>`** — l'aspetto. I colori stanno tutti in cima come variabili
   (`--accent`, `--ok`, `--ko`…): cambiando quelle cambia tutta la pagina.
   I tre blocchi di tema (chiaro, scuro di sistema, scuro scelto) ridefiniscono
   solo le variabili, mai i componenti.
2. **`<body>`** — la struttura: pannello degli input a sinistra, esiti a destra.
3. **`<script>`** — i conti, in tre funzioni in fila:
   `leggi()` prende i numeri dai campi → `calcola()` li trasforma in KPI →
   `mostra()` li scrive a schermo. Ogni modifica in un campo rifà il giro intero.

Per cambiare una formula si tocca solo `calcola()`. Per aggiungere un campo:
una riga `<div class="campo">` nel `<body>`, una riga in `leggi()`.

## Mettere il file su GitHub

```bash
cd "/Users/alexmors/Desktop/Claude_Alex/cruscotto-fab"
git init
git add .
git commit -m "Primo cruscotto di valutazione deal"
```

Poi si crea un repository vuoto su GitHub e si collega:

```bash
git remote add origin https://github.com/TUO-UTENTE/vaglio-deal.git
git branch -M main
git push -u origin main
```

Su GitHub, in **Settings → Pages**, scegliendo il branch `main` la pagina diventa
raggiungibile da qualsiasi browser all'indirizzo
`https://TUO-UTENTE.github.io/vaglio-deal/` — utile per aprirla dal telefono
mentre si visita un immobile.

Da lì in poi il ciclo è sempre lo stesso: modifichi, poi

```bash
git add . && git commit -m "cosa ho cambiato" && git push
```

## Cosa il modello non fa (ancora)

- Non gestisce blocchi con tipologie miste a canoni diversi: il canone è unico.
- La stagionalità usa profili standard, non lo storico reale delle tue strutture.
- Non confronta due deal affiancati.

## Da dove vengono i dati

- **Conti economici per struttura** — i fogli per struttura di `STAY_Host_Hub_OKR`.
  Il cruscotto li riproduce entro lo 0,4%.
- **Stagionalità** — gli incassi mensili 2026 di Muggia e Venezian nel `Cashflow`,
  divisi per la media dell'anno. Le due curve sono diverse sul serio: Muggia fa
  1,93 ad agosto contro 0,53 a febbraio, Venezian sta fra 1,42 e 0,48.
- **Riferimento di mercato Trieste** — 1.369 annunci Airbnb, agosto 2025 – luglio 2026:
  occupazione mediana 59%, top 25% 79%, top 10% 94%, prezzo medio 118 €.
  Fonte: guestfavorites.com. Serve da metro di paragone, non da obiettivo.
