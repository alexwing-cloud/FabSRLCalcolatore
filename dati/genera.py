#!/usr/bin/env python3
"""Genera mercati.html dai dati raccolti in citta.json.

Fa parte del giro settimanale:  raccogli.py  ->  citta.json  ->  genera.py  ->  mercati.html
Lo stile e i colori sono gli stessi del cruscotto: i due file sono lo stesso strumento.
"""
import json, datetime, pathlib, io

BASE = pathlib.Path(__file__).parent
d = json.load(open(BASE/"citta.json", encoding="utf-8"))
TS = [c for c in d if c["slug"] == "trieste"][0]
oggi = datetime.date.today().strftime("%d/%m/%Y")
periodo = TS.get("periodo") or "ultimi 12 mesi"

def e(n):
    """12.345 € — punto per le migliaia, come si scrive in italiano."""
    return f"{n:,.0f}".replace(",", ".") + " €"

def mig(n):
    return f"{n:,.0f}".replace(",", ".")

def dec(n, cifre=1):
    """Virgola decimale, senza toccare nient'altro della stringa."""
    return f"{n:.{cifre}f}".replace(".", ",")

def p(n, cifre=0):
    return dec(n, cifre) + "%"

CLUSTER = {
 "salto":   ("Salto vero",      "Il top 25% incassa almeno il 20% in più che a Trieste. Qui lo spostamento si ripaga."),
 "sopra":   ("Sopra, di poco",  "Dal 4% all'8% meglio di Trieste. Non è il numero che giustifica un trasloco: serve un'altra ragione."),
 "gemelli": ("Gemelli di Trieste", "Entro il 4% in su o in giù. Stesso mestiere, stesso rendimento, nessun vantaggio."),
 "sotto":   ("Sotto Trieste",   "Il top 25% incassa meno. Ci si va solo per motivi che non stanno in questa tabella."),
}

righe = []
for c in d:
    ev = "ok" if c["vs25"] >= 4 else "warn" if c["vs25"] > -4 else "ko"
    qui = ' class="qui"' if c["slug"] == "trieste" else ""
    dati = (f'data-cluster="{c["cluster"]}" data-r25="{c["r25"]:.0f}" data-canone="{c["canone25"]:.0f}" '
            f'data-premio="{c["premio"]:.3f}" data-annunci="{c["annunci"]:.0f}" data-vs="{c["vs25"]:.2f}" '
            f'data-adr="{c["adr"]:.0f}" data-occ="{c["occ"]:.0f}" data-nome="{c["nome"]}"')
    celle = (f'<td>{c["nome"]}</td>'
             f'<td class="num">{c["adr"]:.0f} €</td>'
             f'<td class="num">{p(c["occ"])}</td>'
             f'<td class="num">{e(c["r25"])}</td>'
             f'<td class="num"><b>{e(c["canone25"])}</b></td>'
             f'<td class="num {ev}">{"+" if c["vs25"] >= 0 else "−"}{dec(abs(c["vs25"]))}%</td>'
             f'<td class="num">{dec(c["premio"], 2)}×</td>'
             f'<td class="num">{mig(c["annunci"])}</td>')
    righe.append(f'<tr {dati}{qui}>{celle}</tr>\n')

def scheda(cl):
    citta = [c for c in d if c["cluster"] == cl]
    tit, spieg = CLUSTER[cl]
    nomi = " · ".join(c["nome"] for c in citta) if cl != "sotto" else f"{len(citta)} città"
    return (f'<div class="cl cl--{cl}"><div class="cl-n">{len(citta)}</div>'
            f'<div><div class="cl-t">{tit}</div><div class="cl-c">{nomi}</div>'
            f'<div class="cl-s">{spieg}</div></div></div>')

HTML = f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Carta dei Mercati</title>
<meta name="description" content="Le città italiane di seconda fascia ordinate per quanto incassa chi gestisce bene.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>
:root{{
  --ground:#FAFBFC; --surface:#FFFFFF; --surface-2:#F1F4F7; --line:#DCE3EA; --line-strong:#B9C6D2;
  --text:#131A21; --text-soft:#56646F; --text-faint:#8794A0; --accent:#17466B; --accent-soft:#E3ECF3;
  --ok:#2F7D53; --ok-bg:#E4F1E9; --warn:#A9711A; --warn-bg:#FAEFDB; --ko:#AF4136; --ko-bg:#F9E4E1;
  --shadow:0 1px 2px rgba(19,26,33,.05), 0 8px 24px -16px rgba(19,26,33,.25); --radius:10px;
}}
@media (prefers-color-scheme: dark){{ :root:not([data-theme="light"]){{
  --ground:#0E141A; --surface:#151D25; --surface-2:#1D2831; --line:#2A3742; --line-strong:#3D4D5A;
  --text:#E6ECF1; --text-soft:#9FB0BD; --text-faint:#75899A; --accent:#7CB4DC; --accent-soft:#1B2C3B;
  --ok:#63B98A; --ok-bg:#16301F; --warn:#D9A648; --warn-bg:#33270F; --ko:#E0776B; --ko-bg:#361B18;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.8);
}} }}
:root[data-theme="dark"]{{
  --ground:#0E141A; --surface:#151D25; --surface-2:#1D2831; --line:#2A3742; --line-strong:#3D4D5A;
  --text:#E6ECF1; --text-soft:#9FB0BD; --text-faint:#75899A; --accent:#7CB4DC; --accent-soft:#1B2C3B;
  --ok:#63B98A; --ok-bg:#16301F; --warn:#D9A648; --warn-bg:#33270F; --ko:#E0776B; --ko-bg:#361B18;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px -16px rgba(0,0,0,.8);
}}
*{{box-sizing:border-box}}
body{{margin:0; background:var(--ground); color:var(--text);
  font-family:"IBM Plex Sans",system-ui,-apple-system,sans-serif; font-size:15px; line-height:1.5;
  -webkit-font-smoothing:antialiased;}}
h1,h2{{font-family:Newsreader,Georgia,serif; font-weight:600; text-wrap:balance; margin:0}}
.num{{font-family:"IBM Plex Mono",ui-monospace,monospace; font-variant-numeric:tabular-nums}}
:focus-visible{{outline:2px solid var(--accent); outline-offset:2px; border-radius:4px}}
.intestazione{{padding:22px clamp(16px,4vw,36px); border-bottom:1px solid var(--line); background:var(--surface);
  display:flex; flex-wrap:wrap; gap:14px 26px; align-items:baseline}}
.occhiello{{font-size:10.5px; letter-spacing:.14em; text-transform:uppercase; color:var(--text-faint); font-weight:600}}
.intestazione h1{{font-size:26px; letter-spacing:-.01em}}
.intestazione .sub{{color:var(--text-soft); font-size:13px; max-width:64ch; flex:1; min-width:260px}}
main{{max-width:1180px; margin:0 auto; padding:clamp(16px,3vw,28px) clamp(16px,4vw,36px) 64px;
  display:flex; flex-direction:column; gap:18px}}
.card{{background:var(--surface); border:1px solid var(--line); border-radius:var(--radius); box-shadow:var(--shadow)}}
.sez{{padding:18px 20px}}
.sez>header{{display:flex; align-items:baseline; justify-content:space-between; gap:14px; flex-wrap:wrap; margin-bottom:14px}}
.sez h2{{font-size:18px}}
.sez .nota{{font-size:11.5px; color:var(--text-faint); max-width:54ch}}
.clusters{{display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:12px}}
.cl{{display:flex; gap:13px; padding:14px 16px; border:1px solid var(--line); border-radius:var(--radius);
  background:var(--surface); border-left-width:4px}}
.cl--salto{{border-left-color:var(--ok)}} .cl--sopra{{border-left-color:var(--warn)}}
.cl--gemelli{{border-left-color:var(--accent)}} .cl--sotto{{border-left-color:var(--line-strong)}}
.cl-n{{font-family:"IBM Plex Mono",monospace; font-size:26px; font-weight:600; line-height:1; color:var(--text-faint)}}
.cl--salto .cl-n{{color:var(--ok)}} .cl--sopra .cl-n{{color:var(--warn)}} .cl--gemelli .cl-n{{color:var(--accent)}}
.cl-t{{font-weight:600; font-size:14px}}
.cl-c{{font-size:12px; color:var(--text-soft); margin:2px 0 5px}}
.cl-s{{font-size:11.5px; color:var(--text-faint); line-height:1.45}}
.filtri{{display:flex; flex-wrap:wrap; gap:7px}}
.f{{background:var(--surface-2); color:var(--text-soft); border:1px solid var(--line); border-radius:99px;
  padding:5px 12px; font:inherit; font-size:12.5px; cursor:pointer}}
.f[aria-pressed="true"]{{background:var(--accent); color:var(--surface); border-color:var(--accent)}}
.scroll{{overflow-x:auto}}
table{{border-collapse:collapse; width:100%; font-size:13.5px}}
th,td{{padding:7px 10px; text-align:right; white-space:nowrap}}
th:first-child,td:first-child{{text-align:left}}
thead th{{font-size:10.5px; text-transform:uppercase; letter-spacing:.07em; color:var(--text-faint);
  font-weight:600; border-bottom:1px solid var(--line); cursor:pointer; user-select:none; position:sticky; top:0;
  background:var(--surface)}}
thead th:hover{{color:var(--text)}}
thead th[data-dir]::after{{content:" ▾"; opacity:.7}}
thead th[data-dir="asc"]::after{{content:" ▴"}}
tbody tr{{border-bottom:1px solid var(--line)}}
tbody tr:last-child{{border-bottom:0}}
tbody tr.qui{{background:var(--accent-soft); font-weight:600}}
td.ok{{color:var(--ok)}} td.warn{{color:var(--warn)}} td.ko{{color:var(--ko)}}
.metodo{{font-size:12.5px; color:var(--text-soft); line-height:1.6}}
.metodo b{{color:var(--text)}}
.metodo ul{{margin:8px 0 0; padding-left:20px}} .metodo li{{margin-bottom:5px}}
a{{color:var(--accent)}}
</style>
</head>
<body>

<header class="intestazione">
  <div>
    <div class="occhiello">FAB S.r.l. · aggiornato il {oggi}</div>
    <h1>Carta dei Mercati</h1>
  </div>
  <div class="sub">{len(d)} città italiane di seconda fascia, ordinate per quanto incassa <b>chi gestisce bene</b> — non per la media di mercato. Con il canone massimo che puoi pagare per appartamento restando entro il 25%.</div>
</header>

<main>

  <section class="card sez">
    <header>
      <h2>Come si dividono</h2>
      <div class="nota">Confronto sul quartile alto, perché è lì che operi: le tue strutture girano fra il 77% e il 93% di occupazione.</div>
    </header>
    <div class="clusters">{''.join(scheda(k) for k in CLUSTER)}</div>
  </section>

  <section class="card sez">
    <header>
      <h2>Tutte le città</h2>
      <div class="filtri">
        <button class="f" data-f="tutte" aria-pressed="true">Tutte</button>
        <button class="f" data-f="salto" aria-pressed="false">Salto vero</button>
        <button class="f" data-f="sopra" aria-pressed="false">Sopra</button>
        <button class="f" data-f="gemelli" aria-pressed="false">Gemelli</button>
        <button class="f" data-f="sotto" aria-pressed="false">Sotto</button>
      </div>
    </header>
    <div class="scroll">
      <table id="t">
        <thead><tr>
          <th data-k="nome">Città</th>
          <th data-k="adr">Prezzo/notte</th>
          <th data-k="occ">Occupazione</th>
          <th data-k="r25" data-dir="desc">Top 25% · ricavo/anno</th>
          <th data-k="canone">Canone max al 25%</th>
          <th data-k="vs">vs Trieste</th>
          <th data-k="premio">Premio alla bravura</th>
          <th data-k="annunci">Annunci</th>
        </tr></thead>
        <tbody>{''.join(righe)}</tbody>
      </table>
    </div>
  </section>

  <section class="card sez">
    <header><h2>Come leggerla</h2></header>
    <div class="metodo">
      <ul>
        <li><b>Top 25% · ricavo/anno</b> — quanto incassa in un anno un appartamento gestito nel quartile alto di quel mercato. È il livello dove stai tu, quindi è il solo confronto che ti riguarda. La media di mercato mescola professionisti e improvvisati e ti farebbe scegliere male.</li>
        <li><b>Canone max al 25%</b> — il canone mensile massimo per appartamento che rispetta la tua regola, a quel livello di ricavo. È il numero da portare in trattativa: sopra quella cifra il deal è già bocciato.</li>
        <li><b>Premio alla bravura</b> — quanto il quartile alto incassa più della mediana. Sopra 1,7× vuol dire che in quel mercato la concorrenza è dilettantesca e un operatore serio prende quota. Sotto 1,4× vuol dire che sono già tutti bravi.</li>
        <li><b>Annunci</b> — l'offerta esistente. Attenzione: il perimetro geografico non è garantito uguale fra città (in alcuni casi include la provincia), quindi usalo come indizio, non come misura.</li>
      </ul>
      <p><b>Fonte e metodo.</b> Una sola fonte per tutte le città (guestfavorites, periodo {periodo}), perché mescolare metodologie diverse porta a conclusioni rovesciate — verificato sul campo con Bergamo. I dati sono medie di mercato Airbnb: dicono cosa incassa un appartamento, non quanto costa prenderlo in affitto in quella via. Il canone reale lo si trova solo trattando.</p>
      <p>Il conto completo di un singolo blocco si fa nel <a href="./">Vaglio Deal</a>.</p>
    </div>
  </section>

</main>

<script>
/* Filtri per cluster e ordinamento delle colonne. */
const tb = document.querySelector('#t tbody');
const righe = [...tb.rows];

document.querySelectorAll('.f').forEach(b => b.onclick = () => {{
  document.querySelectorAll('.f').forEach(x => x.setAttribute('aria-pressed', x === b));
  const f = b.dataset.f;
  righe.forEach(r => r.hidden = (f !== 'tutte' && r.dataset.cluster !== f));
}});

document.querySelectorAll('#t thead th').forEach(th => th.onclick = () => {{
  const k = th.dataset.k;
  const giu = th.dataset.dir !== 'asc';
  document.querySelectorAll('#t thead th').forEach(x => x.removeAttribute('data-dir'));
  th.dataset.dir = giu ? 'desc' : 'asc';
  righe.sort((a, b) => {{
    const x = a.dataset[k], y = b.dataset[k];
    const n = isNaN(parseFloat(x)) ? null : parseFloat(x) - parseFloat(y);
    const v = n === null ? x.localeCompare(y, 'it') : n;
    return giu ? -v : v;
  }});
  righe.forEach(r => tb.appendChild(r));
}});
</script>
</body>
</html>
"""
io.open(BASE.parent/"mercati.html", "w", encoding="utf-8").write(HTML)
print("scritto mercati.html —", len(d), "città")
