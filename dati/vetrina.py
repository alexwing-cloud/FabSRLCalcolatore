#!/usr/bin/env python3
"""Costruisce report/ULTIMO.html: il report da guardare, non da leggere.

Ogni immobile e una scheda con la foto, i numeri e il link all'annuncio.
Alex spunta quelli che gli interessano e preme "Copia i selezionati":
la lista finisce negli appunti, la incolla in chat, e da li si procede
a cercare i contatti e preparare le bozze delle mail.
"""
import json, datetime, pathlib, io, html

BASE = pathlib.Path(__file__).parent
REPORT = BASE.parent / "report"
REPORT.mkdir(exist_ok=True)

def e(n): return f"{n:,.0f}".replace(",", ".") + " €"

def scheda(a, i):
    tag = " · ".join(a.get("tag", [])[:4])
    stato = "ok" if a["esito"] == "passa" else "warn"
    foto = a.get("foto") or ""
    if "noimg" in foto:          # trovacasa serve un segnaposto: meglio dirlo
        foto = ""
    img = (f'<img src="{html.escape(foto)}" alt="" loading="lazy">' if foto
           else '<div class="nofoto">nessuna foto</div>')
    return f"""
<article class="sc" data-i="{i}" data-esito="{a['esito']}" data-citta="{a['citta']}">
  <label class="sel"><input type="checkbox" data-i="{i}"><span>Mi interessa</span></label>
  <div class="foto">{img}</div>
  <div class="corpo">
    <div class="dove">{a['citta'].capitalize()}{' · ' + a['zona'] if a.get('zona') else ''}</div>
    <h3>{html.escape(a['titolo'])}</h3>
    <div class="numeri">
      <div><span class="et">Canone</span><b>{e(a['canone'])}</b></div>
      <div><span class="et">Locali</span><b>{a['locali']}</b></div>
      <div><span class="et">Superficie</span><b>{a['mq']} m²</b></div>
      <div><span class="et">€/m²</span><b>{str(a.get('eur_mq','—')).replace('.',',')}</b></div>
    </div>
    <div class="verdetto {stato}">
      Sostenibile fino a <b>{e(a['canone_sostenibile'])}</b> · margine
      <b>{'+' if a['margine']>=0 else ''}{e(a['margine'])}</b>
      {'<span class="pill">al limite</span>' if a['esito'] != 'passa' else ''}
    </div>
    <div class="tag">{html.escape(tag)}</div>
    <a class="vai" href="{a.get('url') or '#'}" target="_blank" rel="noopener">Vedi l'annuncio e le foto →</a>
  </div>
</article>"""

def main(web=False):
    sorgente = "annunci_web.json" if web else "annunci.json"
    ann = json.load(open(BASE / sorgente, encoding="utf-8"))
    ann = [a for a in ann if a.get("url")]
    if web:                       # foto cucite dentro il file, non caricate da fuori
        for a in ann:
            a["foto"] = a.get("mini") or ""
    ann.sort(key=lambda a: -a["margine"])
    oggi = datetime.date.today().strftime("%d/%m/%Y")
    citta = sorted({a["citta"] for a in ann})

    HTML = f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Immobili da guardare</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap">
<style>
:root{{--ground:#FAFBFC;--surface:#fff;--surface-2:#F1F4F7;--line:#DCE3EA;--line-strong:#B9C6D2;
--text:#131A21;--text-soft:#56646F;--text-faint:#8794A0;--accent:#17466B;--accent-soft:#E3ECF3;
--ok:#2F7D53;--ok-bg:#E4F1E9;--warn:#A9711A;--warn-bg:#FAEFDB;
--shadow:0 1px 2px rgba(19,26,33,.05),0 8px 24px -16px rgba(19,26,33,.25);}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--ground:#0E141A;--surface:#151D25;
--surface-2:#1D2831;--line:#2A3742;--line-strong:#3D4D5A;--text:#E6ECF1;--text-soft:#9FB0BD;
--text-faint:#75899A;--accent:#7CB4DC;--accent-soft:#1B2C3B;--ok:#63B98A;--ok-bg:#16301F;
--warn:#D9A648;--warn-bg:#33270F;--shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -16px rgba(0,0,0,.8);}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--ground);color:var(--text);
font-family:"IBM Plex Sans",system-ui,sans-serif;font-size:15px;line-height:1.5;padding-bottom:88px}}
h1,h3{{font-family:Newsreader,Georgia,serif;font-weight:600;margin:0;text-wrap:balance}}
header.top{{padding:20px clamp(16px,4vw,32px);border-bottom:1px solid var(--line);background:var(--surface);
display:flex;flex-wrap:wrap;gap:12px 24px;align-items:baseline;position:sticky;top:0;z-index:5}}
.occhiello{{font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--text-faint);font-weight:600}}
header h1{{font-size:23px}}
header .sub{{color:var(--text-soft);font-size:13px;flex:1;min-width:220px}}
.filtri{{display:flex;flex-wrap:wrap;gap:6px}}
.f{{background:var(--surface-2);color:var(--text-soft);border:1px solid var(--line);border-radius:99px;
padding:5px 11px;font:inherit;font-size:12.5px;cursor:pointer}}
.f[aria-pressed="true"]{{background:var(--accent);color:var(--surface);border-color:var(--accent)}}
main{{max-width:1300px;margin:0 auto;padding:clamp(16px,3vw,26px) clamp(16px,4vw,32px);
display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:16px}}
.sc{{background:var(--surface);border:1px solid var(--line);border-radius:10px;overflow:hidden;
box-shadow:var(--shadow);display:flex;flex-direction:column;position:relative}}
.sc.scelta{{outline:2px solid var(--accent);outline-offset:-2px}}
.foto{{aspect-ratio:4/3;background:var(--surface-2);overflow:hidden}}
.foto img{{width:100%;height:100%;object-fit:cover;display:block}}
.nofoto{{display:grid;place-items:center;height:100%;color:var(--text-faint);font-size:12px}}
.sel{{position:absolute;top:10px;left:10px;z-index:2;display:flex;align-items:center;gap:6px;
background:var(--surface);border:1px solid var(--line-strong);border-radius:99px;padding:5px 11px 5px 8px;
font-size:12px;cursor:pointer;box-shadow:var(--shadow)}}
.sel input{{accent-color:var(--accent);margin:0}}
.corpo{{padding:13px 15px 15px;display:flex;flex-direction:column;gap:9px;flex:1}}
.dove{{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--text-faint);font-weight:600}}
.sc h3{{font-size:15.5px;line-height:1.3}}
.numeri{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;padding:9px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}}
.numeri .et{{display:block;font-size:9.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--text-faint)}}
.numeri b{{font-family:"IBM Plex Mono",monospace;font-size:14px;font-variant-numeric:tabular-nums}}
.verdetto{{font-size:12.5px;color:var(--text-soft);background:var(--ok-bg);border-radius:6px;padding:7px 9px}}
.verdetto b{{color:var(--ok)}}
.verdetto.warn{{background:var(--warn-bg)}} .verdetto.warn b{{color:var(--warn)}}
.pill{{font-size:9.5px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;
background:var(--warn);color:var(--surface);padding:1px 6px;border-radius:99px;margin-left:4px}}
.tag{{font-size:11.5px;color:var(--text-faint)}}
.vai{{margin-top:auto;font-size:13px;color:var(--accent);text-decoration:none;font-weight:500}}
.vai:hover{{text-decoration:underline}}
.barra{{position:fixed;bottom:0;left:0;right:0;background:var(--surface);border-top:1px solid var(--line);
padding:12px clamp(16px,4vw,32px);display:flex;align-items:center;gap:14px;flex-wrap:wrap;z-index:9;
box-shadow:0 -8px 24px -18px rgba(0,0,0,.5)}}
.barra .n{{font-family:"IBM Plex Mono",monospace;font-size:15px;font-weight:600}}
.barra .aiuto{{color:var(--text-faint);font-size:12px;flex:1;min-width:200px}}
.btn{{background:var(--accent);color:var(--surface);border:1px solid var(--accent);border-radius:8px;
padding:9px 16px;font:inherit;font-size:14px;font-weight:500;cursor:pointer}}
.btn[disabled]{{opacity:.4;cursor:default}}
.btn.vuoto{{background:var(--surface-2);color:var(--text-soft);border-color:var(--line)}}
:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
</style></head><body>

<header class="top">
  <div><div class="occhiello">FAB S.r.l. · {oggi}</div><h1>Immobili da guardare</h1></div>
  <div class="sub">{len(ann)} annunci passati al vaglio. Spunta quelli che ti interessano, poi premi <b>Copia i selezionati</b> e incolla in chat.</div>
  <div class="filtri">
    <button class="f" data-f="tutte" aria-pressed="true">Tutte</button>
    {''.join(f'<button class="f" data-f="{c}" aria-pressed="false">{c.capitalize()}</button>' for c in citta)}
  </div>
</header>

<main id="griglia">{''.join(scheda(a, i) for i, a in enumerate(ann))}</main>

<div class="barra">
  <span class="n" id="conta">0</span>
  <span class="aiuto">selezionati — il pulsante copia negli appunti l'elenco pronto da incollare</span>
  <button class="btn vuoto" id="azzera">Azzera</button>
  <button class="btn" id="copia" disabled>Copia i selezionati</button>
</div>

<script>
const DATI = {json.dumps([{k: a.get(k) for k in
   ("citta","zona","titolo","canone","locali","mq","canone_sostenibile","margine","url")}
   for a in ann], ensure_ascii=False)};
const scelti = new Set();
const conta = document.getElementById('conta');
const bottone = document.getElementById('copia');

function aggiorna(){{
  conta.textContent = scelti.size;
  bottone.disabled = scelti.size === 0;
  bottone.textContent = scelti.size ? `Copia i ${{scelti.size}} selezionati` : 'Copia i selezionati';
}}
document.getElementById('griglia').addEventListener('change', ev => {{
  const cb = ev.target.closest('input[type=checkbox]'); if(!cb) return;
  const i = +cb.dataset.i;
  cb.checked ? scelti.add(i) : scelti.delete(i);
  cb.closest('.sc').classList.toggle('scelta', cb.checked);
  aggiorna();
}});
document.getElementById('azzera').onclick = () => {{
  scelti.clear();
  document.querySelectorAll('#griglia input[type=checkbox]').forEach(c => c.checked = false);
  document.querySelectorAll('.sc').forEach(s => s.classList.remove('scelta'));
  aggiorna();
}};
document.getElementById('copia').onclick = async () => {{
  const righe = ['Procedi con questi immobili:', ''];
  [...scelti].sort((a,b)=>a-b).forEach(i => {{
    const a = DATI[i];
    righe.push(`- ${{a.citta.toUpperCase()}}${{a.zona ? ' · ' + a.zona : ''}} — ${{a.titolo}}`);
    righe.push(`  ${{a.canone.toLocaleString('it-IT')}} € · ${{a.locali}} locali · ${{a.mq}} m² · ${{a.url}}`);
  }});
  try {{
    await navigator.clipboard.writeText(righe.join('\\n'));
    bottone.textContent = 'Copiato — incollalo in chat';
    setTimeout(aggiorna, 2200);
  }} catch(e) {{
    bottone.textContent = 'Non riesco a copiare';
    setTimeout(aggiorna, 2200);
  }}
}};
document.querySelectorAll('.f').forEach(b => b.onclick = () => {{
  document.querySelectorAll('.f').forEach(x => x.setAttribute('aria-pressed', x === b));
  const f = b.dataset.f;
  document.querySelectorAll('.sc').forEach(s => s.hidden = (f !== 'tutte' && s.dataset.citta !== f));
}});
</script>
</body></html>"""
    if web:
        # formato per la pubblicazione: senza involucro <html>, che lo mette il servizio
        corpo = HTML.split("<head>", 1)[1].split("</head>", 1)[0]
        corpo = corpo.replace('<meta charset="utf-8">', "").replace(
            '<meta name="viewport" content="width=device-width, initial-scale=1">', "")
        corpo += HTML.split("<body>", 1)[1].rsplit("</body>", 1)[0]
        f = REPORT / "ULTIMO-web.html"
        io.open(f, "w", encoding="utf-8").write(corpo)
        print(f"vetrina pubblicabile: {f} — {len(ann)} immobili, {f.stat().st_size//1024//1024} MB")
    else:
        io.open(REPORT / "ULTIMO.html", "w", encoding="utf-8").write(HTML)
        print(f"vetrina: {REPORT/'ULTIMO.html'} — {len(ann)} immobili")

if __name__ == "__main__":
    import sys
    main(web="--web" in sys.argv)
