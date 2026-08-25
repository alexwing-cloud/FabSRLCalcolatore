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

## I preset

Il menu in alto carica le **sette business unit** del file `STAY_Host_Hub_OKR`:
Muggia Ai fronte Mare, Muggia 2, Venezian, Le Residenze dei Serravallo,
Piazza Venezia, Via Degli Artisti, Via Marziale. Servono da metro di paragone —
il modello riproduce i loro conti economici entro lo 0,02%.

Alla soglia del 25% ne passano **due su sette** (Serravallo 21,2%, Muggia 2 23,7%).
È il punto: la soglia è più severa del portafoglio esistente.

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

- **Conti economici per struttura** — le sette schede di `STAY_Host_Hub_OKR`.
  Il cruscotto le riproduce entro lo 0,02%.
- **Stagionalità** — gli incassi mensili 2026 di Muggia e Venezian nel `Cashflow`,
  divisi per la media dell'anno. Le due curve sono diverse sul serio: Muggia fa
  1,93 ad agosto contro 0,53 a febbraio, Venezian sta fra 1,42 e 0,48.
- **Riferimento di mercato Trieste** — 1.369 annunci Airbnb, agosto 2025 – luglio 2026:
  occupazione mediana 59%, top 25% 79%, top 10% 94%, prezzo medio 118 €.
  Fonte: guestfavorites.com. Serve da metro di paragone, non da obiettivo.

## La Carta dei Mercati

`mercati.html` mette in fila 49 città italiane di seconda fascia per **quanto incassa
chi gestisce bene** — il quartile alto, non la media di mercato — e per ognuna calcola
il **canone massimo sostenibile** per appartamento al 25% del lordo.

Si rigenera con due comandi:

```bash
cd dati && python3 raccogli.py && python3 genera.py
```

`raccogli.py` interroga la fonte di mercato (una sola per tutte le città, con pausa fra
le richieste) e scrive `citta.json`. `genera.py` trasforma il JSON in `mercati.html`.
È lo stesso giro che gira in automatico ogni domenica sera.

### Perché il quartile alto e non la media

La media di mercato mescola professionisti e improvvisati. Bergamo ha il 67% di
occupazione media contro il 62% di Trieste, e sembra un mercato migliore: ma quasi tutto
quel vantaggio è un effetto pavimento — là si riempiono anche gli annunci scarsi. Sul
quartile alto, dove operiamo noi, il divario si riduce a pochi punti percentuali.
Scegliere una città dal dato medio porta alla conclusione sbagliata.

### Una sola fonte per tutte

I dati vengono tutti dalla stessa fonte e dallo stesso periodo. Mescolare metodologie
diverse rovescia le conclusioni: InsideAirbnb stima l'occupazione dalle recensioni e
per Bergamo città dà il 19,7% dove un'altra fonte dà il 67%. Non sono numeri
confrontabili, e usarli insieme avrebbe fatto scartare un mercato buono.
