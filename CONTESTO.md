# FAB S.r.l. — contesto per ripartire

Documento di passaggio di consegne. Contiene tutto quello che serve a riprendere il
lavoro da zero in una conversazione nuova. Aggiornato al **27 agosto 2026**.

---

## 1. Chi è il cliente

**Alex Morsellino**, titolare di **FAB S.r.l.**, che gestisce appartamenti in locazione
turistica breve col marchio **STAY Apartments** — www.stayapartments.it — fra **Trieste,
Muggia e Barcola**. Scrive e lavora in italiano. Contatto: alex@noura.training.

**La squadra**, quattro persone con quattro mestieri distinti:

| | |
|---|---|
| Alex Morsellino | Business Development — acquisizioni e trattative |
| Federico Conforti | Legal & Economics — contratti, due diligence, conti |
| Mattia Carrese | Operations — strutture, standard, manutenzione |
| Gabriele Massaria | Customer Relationship — ospiti, recensioni, accoglienza |

Dieci anni nel settore. **Sono ex giocatori di rugby professionisti**, dettaglio che usa
nei documenti commerciali perché spiega l'organizzazione per ruoli.

**Portafoglio dichiarato all'esterno**: 40 appartamenti a regime, altri 30 in ingresso a
inizio 2027.

## 2. Il modello e le regole di decisione

**Rent-to-rent**: prende immobili in affitto con facoltà di sublocazione, contratti 6+6 o
8+8, preferibilmente già arredati per tenere il capex al minimo. Sta **uscendo dal
property management per conto terzi** perché il portafoglio decade ogni anno a seconda
che i proprietari concedano o meno gli appartamenti: il contratto di locazione è l'asset,
il mandato no.

**Le due regole che decidono un deal:**

1. **Canone ≤ 25% del fatturato lordo IVA compresa.** Soglia che si allarga con la scala:
   25% fino a 3 appartamenti, **fino al 30% da 20 in su**, in mezzo cresce in linea retta.
   Motivo: un blocco grande spalma i costi fissi su più unità.
2. **Utile netto ≥ 25% del fatturato lordo.** Specchio della prima: di ogni 100 € lordi,
   max 25 al proprietario e min 25 a noi. **È un traguardo, non una fotografia**: nessuna
   delle sette strutture in portafoglio ci arriva, il massimo è Muggia 2 con 24,1%.

**Taglio minimo**: 3 appartamenti per blocco, target 5. Ricerca su immobili **da 180 m² in su**.

**Servizi interni**: pulizie e lavanderia sono gestite con personale e mezzi propri, non
appaltate. Nei modelli vanno valorizzate a costo industriale, non a prezzo di mercato.

## 3. Gli strumenti costruiti

Tutti online, senza login, apribili anche da telefono.

| | |
|---|---|
| **Vaglio Deal** — calcolatore go/no-go | https://alexwing-cloud.github.io/FabSRLCalcolatore/ |
| **Carta dei Mercati** — 49 città | https://alexwing-cloud.github.io/FabSRLCalcolatore/mercati.html |
| **Hotel Centrale** — conto economico | https://alexwing-cloud.github.io/FabSRLCalcolatore/hotel-centrale.html |

**Repo**: `~/fab-vaglio-deal`, con collegamento simbolico in
`~/Desktop/Claude_Alex/cruscotto-fab`. Su GitHub: `alexwing-cloud/FabSRLCalcolatore`,
**pubblico** per scelta esplicita di Alex, numeri reali compresi.

⚠️ **Il repo non può stare sulla Scrivania**: macOS protegge quella cartella e `launchd`
fallisce con exit 126 senza spiegare perché. Verificato con due script identici.

⚠️ **Nei link scritti in chat usare il percorso `cruscotto-fab/...`**, non `dati/...`:
la cartella di lavoro della sessione è `~/Desktop/Claude_Alex`.

### Il giro automatico

Due lavori `launchd` sul Mac di Alex, che usano il token già nel portachiavi:

| Quando | Cosa fa |
|---|---|
| Ogni giorno 7:30 | Cerca annunci, li vaglia, scrive il report, rigenera le vetrine, committa e pusha |
| Domenica 20:00 | Come sopra, più i dati di mercato delle 49 città |

Il file da aprire è sempre `report/ULTIMO.html` — nome fisso. **Un immobile viene
proposto una volta sola**: se Alex non lo indica, sparisce e non torna. Il silenzio vale
come scarto.

`report/ULTIMO-web.html` è la versione con le foto incorporate, da pubblicare come
artifact: quella la rigenera il giro, ma **pubblicarla richiede una sessione**.

### Gli script

In `dati/`: `raccogli.py` (mercato) · `annunci.py` (ricerca immobili) · `agenzie.py`
(agenzie e contatti) · `report.py` · `vetrina.py` e `vetrina_web.py` · `giro.sh`.

## 4. Vincoli tecnici già verificati — non riprovare

- **I portali immobiliari sono chiusi.** immobiliare.it, casa.it, idealista.it,
  wikicasa.it e attico.it rispondono **403 con CAPTCHA**. subito.it lo vieta nel
  robots.txt. Aggirarli non si fa. La fonte usata è **trovacasa.it**, che consente
  l'accesso alle pagine di elenco. Rispondono anche mioaffitto, tecnocasa e gabetti.
- **Le palazzine intere in affitto non stanno sui portali**: le categorie
  `palazzi-in-affitto` e `alberghi-in-affitto` sono vuote ovunque. Quel mercato passa
  dagli agenti, ed è il motivo per cui esiste `agenzie.py`.
- **Mai mescolare fonti di mercato diverse.** InsideAirbnb stima l'occupazione dalle
  recensioni e per Bergamo città dà 19,7% dove guestfavorites dà 67%. Per confrontare
  città si usa **una sola fonte per tutte**.
- **Gmail collegata**: `alex@noura.training` (Google Workspace).
  `info@stayapartments.it` è su **Netsons, non Google**: non collegabile come connettore.
  Server SMTP da usare per l'alias: `hostingssd132.netsons.net`, porta 465 SSL —
  **non** `mail.stayapartments.it`, il cui certificato non combacia.
- **Account GitHub non collegato a Claude**: le routine cloud vengono rifiutate. Per
  questo il giro gira in locale.

## 5. Il portafoglio

Dal foglio `STAY_Host_Hub_OKR copia.xlsx`, sette schede, una per business unit.
Il cruscotto le riproduce **entro lo 0,02%**.

| Struttura | Appt | Canone/lordo | Utile/lordo | Verdetto |
|---|---:|---:|---:|---|
| Le Residenze dei Serravallo | 9 | **21,2%** | 23,0% | passa |
| Muggia 2 | 3 | **23,7%** | 24,1% | passa |
| Muggia Ai fronte Mare | 5 | 29,8% | 23,0% | no |
| Via Degli Artisti | 4 | 32,8% | 12,5% | no |
| Piazza Venezia | 11 | 37,8% | 14,7% | no |
| Venezian | 12 | 40,4% | 13,0% | no |
| Via Marziale | 1 | 42,0% | 21,9% | no |

**Attenzione**: sono piani a regime, non consuntivi. Nel cash flow 2026 compaiono solo
**Muggia, Venezian, Madonna del Mare e Alleghe**; Machiavelli versa solo pulizie e
condominio. **Le Residenze dei Serravallo ha decorrenza 1° gennaio 2027** — risulta dal
thread con lo Studio Rigotto. Prima di usare i numeri di portafoglio all'esterno, chiedere
quali strutture sono davvero operative.

## 6. I dati di mercato

Fonte unica **guestfavorites**, periodo agosto 2025 – luglio 2026, 49 città.
Confronto sul **quartile alto**, mai sulla media: la media mescola professionisti e
improvvisati e fa scegliere il mercato sbagliato.

**Canone massimo sostenibile per appartamento, livello top 25%:**
Bolzano 967 € · Como 795 € · Verona 726 € · Bari 622 € · Siena 608 € · Bergamo 608 € ·
**Trieste 576 €** · Pisa 576 € · Trento 571 € · Torino 449 €.

**Bergamo e Torino non danno vantaggio.** Il vantaggio apparente di Bergamo — 67% di
occupazione contro 62% — è un effetto pavimento: là si riempiono anche gli annunci scarsi.
Al livello di Alex il divario si annulla, e in cima Bergamo è persino peggio.

Riferimento Trieste: 1.369 annunci, ADR 118 €, occupazione mediana 59%, top 25% 79%,
top 10% 94%. Le strutture FAB girano fra 78% e 90%.

## 7. I due progetti aperti

### Centrolanza, Opicina — proposta pronta da mandare

Capannone di **2.400 m²** da riqualificare in **55 unità ricettive** da 4 posti letto.
La proprietà possiede i muri e finanzierebbe i lavori. Referente: **Stefano** (col tu).

**I termini della proposta:**

- investimento 2.000.000 €, equity della proprietà 350.000 più mutuo
- **canone 210.000 €/anno**, 17.500 al mese, **adeguato ISTAT al 75%** dal secondo anno
- durata vent'anni
- scaletta di avviamento: 75% il primo anno, 90% il secondo, recupero nei 18 successivi
  a totale ventennale invariato (4.200.000 €)
- ampliamento: **3.818 € annui per unità** oltre le 55, criterio lineare
- presupposto contrattuale: **almeno 50 unità** consegnate
- **sottoscrizione anticipata** con condizione sospensiva ex art. 1353 c.c., più
  disponibilità alla cessione dei crediti da canoni in garanzia ex artt. 1260 ss.
- se il recesso è per libera scelta di FAB, **FAB copre il 50% delle spese tecniche**

**Il conto della proprietà** (equity 350k, 4,5%, 20 anni): rata 10.570 €/mese, differenza
6.930 €/mese, 83.154 €/anno, **1.663.087 € sul ventennio**, al lordo dei loro oneri.

**I nostri numeri, che nel documento NON compaiono**: 55 unità, ADR 73 €, occupazione
82-90%, lordo ~1.260.000, GOP 550.097, canone al 16,7% del lordo, utile netto 19,5%.

**File**: `contatto/proposta-centrolanza.html` e `Proposta-Centrolanza.pdf` (10 pagine) ·
testo WhatsApp e mail in `contatto/messaggio-centrolanza.md` e `mail-centrolanza.md`.

**Manca**: Federico sulla sezione legale, forma societaria di Centrolanza in intestazione.

**Le obiezioni che faranno**, già analizzate: l'investimento di 2 M€ non è nostro e sopra
i 2,4 M€ il conto non regge più per loro; la fideiussione «da concordare» sarà la prima
cosa che quantificano; il valore finale capitalizzato al 7% è il numero più morbido.

### Hotel Centrale, Trieste — in valutazione

**24 stanze, 57 posti letto.** Fatturato attuale 650.000 €, obiettivo 750.000 con
occupazione 93-95% e prezzo medio 91 €. Tre stelle, da **convertire in aparthotel**.

**La proprietà possiede muri e attività**, vuole chiudere la gestione: chiede
**800.000 € di buona uscita** più un affitto di **140-144.000 €/anno**. Chiederà
probabilmente un **acconto alla firma**.

**Il conto a regime** (soggiorno medio 4 notti): utile lordo 215.868, **utile netto
155.641**, canone al 19,2% del lordo. Da albergo 3 stelle il GOP sarebbe 151.045; da
aparthotel 360.531. **Il 57% del vantaggio viene dai costi, non dai ricavi** — soprattutto
dai 1.326 cambi in meno all'anno.

**Gli 800.000 non sono pagabili**: servirebbero 8,9 anni tenendo 80.000 €/anno di
margine. Il sostenibile è **450.000-500.000 in cinque anni**, o 400.000 in tre.

**La leva vera**: muri e attività sono dello stesso soggetto, quindi buona uscita e canone
sono scambiabili. Tutto in canone significa 185.667 €/anno — 24,8% del lordo, dentro la
regola — **senza tirare fuori un euro adesso**, e con un vantaggio fiscale perché il canone
si deduce per intero mentre l'avviamento si deduce in 18 anni.

**Normativa**: la L.R. FVG 21/2016 **è stata abrogata**. Vale il **Codice regionale del
commercio e turismo, L.R. FVG 9 dicembre 2025 n. 17**, in vigore dal 16/12/2025.
Art. 95 c. 10: l'unità RTA richiede cucina autonoma e bagno privato. Ma il c. 7 dice
«esclusivamente **o prevalentemente**»: **bastano 13 cucinini su 24**, non tutti — 58.500 €
invece di 108.000. Art. 86 c. 1: si passa da **SCIA al SUAP**. Art. 89: i requisiti di
classificazione sono rinviati a un decreto del Direttore centrale, **da verificare se
emanato** prima di impegnarsi.

**Se è un ramo d'azienda in immobile di terzi**, ricordare l'art. 36 L. 392/1978: il
contratto si trasferisce con l'azienda senza consenso del locatore, ma va comunicato con
raccomandata e il locatore ha 30 giorni per opporsi. Qui però muri e attività coincidono,
quindi il problema non si pone.

## 8. Il canale agenzie

Le palazzine non passano dai portali, quindi si scrive agli agenti. **200 agenzie**
raccolte su Bolzano, Verona, Trieste, Como e Bergamo; le **35 più rilevanti** — pesate su
chi tratta immobili commerciali, dove passano le cessioni di ramo d'azienda — sono in
`contatto/agenzie.md`, **13 con email verificata**, tutte con telefono.

**14 bozze già scritte e non inviate** in `alex@noura.training`: 13 alle agenzie e una a
`info@corsinire.com` per un hotel da 40 chiavi a Roma. Corsini è un broker serio — attivo
dal 1925, oltre 130 hotel, uffici a Londra e Amsterdam.

Il testo delle mail è in `contatto/modello-email.md`, scritto nel registro della
**richiesta di aiuto** e non della proposta commerciale: funziona perché è vero, quelle
opportunità le vedono loro prima che diventino annunci.

La presentazione aziendale è in `contatto/presentazione.html` e `.md`.

## 9. Come lavorare con Alex

- **Non fare proposte non richieste.** Te lo ha detto esplicitamente. Rispondi alla
  domanda, e le osservazioni tienile per quando cambiano una decisione.
- **Niente passaggi tecnici da fargli fare.** Davanti a un flusso OAuth ha risposto
  «fallo tu non capisco». Se un blocco richiede le sue mani, cerca prima una strada che
  non lo coinvolga; se è ineludibile, dillo in una frase.
- **Verifica invece di assumere.** Ha corretto giustamente una stima fiscale presentata
  come certezza. Quando un numero dipende da cose che non sai, dillo e dai la forbice.
- **Estetica: sabbia `#E6DBC9` e salvia `#7B8275`**, i due colori del sito. I neutri con
  vena calda, mai grigi freddi.
- I documenti commerciali **non mostrano mai i nostri margini**: fatturato, GOP, utile e
  punto di pareggio restano fuori. Al loro posto vanno le garanzie.

## 10. Cosa resta aperto

- [ ] Quali strutture sono **davvero operative** oggi, per i numeri di portafoglio
- [ ] Federico sulla sezione legale della proposta Centrolanza
- [ ] Forma societaria di Centrolanza in intestazione
- [ ] Collegare l'account GitHub, se si vuole spostare il giro in cloud
- [ ] Alias `info@stayapartments.it` su Gmail, o Workspace sul dominio
- [ ] Le 22 agenzie senza email, da cercare una per una
- [ ] Hotel Centrale: storico dei soggiorni medi, costo vero del personale e delle utenze
