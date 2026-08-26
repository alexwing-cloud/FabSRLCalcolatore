#!/usr/bin/env python3
"""Scrive il report: cosa e comparso di nuovo rispetto all'ultima volta.

Il valore di un report ricorrente sta in quello che NON dice. Qui dentro finiscono
solo gli annunci mai visti prima che rientrano nei parametri. Se non ce n'e nessuno,
il report e una riga sola, ed e giusto cosi.
"""
import json, pathlib, datetime, sys

BASE = pathlib.Path(__file__).parent
REPORT = BASE.parent / "report"
REPORT.mkdir(exist_ok=True)

def e(n):  return f"{n:,.0f}".replace(",", ".") + " €"

def main(modo="giornaliero", tutti=False):
    annunci = json.load(open(BASE / "annunci.json", encoding="utf-8"))
    visti_f = BASE / "visti.json"
    visti = set(json.load(open(visti_f))) if visti_f.exists() else set()

    # con --tutti si rifà l'elenco completo, ignorando cosa è già stato segnalato
    nuovi = [a for a in annunci if a.get("url") and (tutti or a["url"] not in visti)]
    nuovi.sort(key=lambda a: -a["margine"])

    oggi = datetime.date.today()
    righe = [f"# Report {modo} — {oggi.strftime('%d/%m/%Y')}", ""]

    if not nuovi:
        righe += [f"**Nessun annuncio nuovo che rientri nei parametri.** "
                  f"Il vaglio ha riguardato {len(annunci)} annunci già noti.", ""]
    else:
        forti = [a for a in nuovi if a["esito"] == "passa"]
        titolo = "annunci in elenco" if tutti else "annunci nuovi"
        righe += [f"**{len(nuovi)} {titolo}**, di cui {len(forti)} entro il canone sostenibile.", ""]
        righe += ["| Città | Zona | Canone | Locali | m² | €/mq | Sostenibile | Margine | Note |",
                  "|---|---|---:|---:|---:|---:|---:|---:|---|"]
        for a in nuovi[:40]:
            note = []
            if a.get("arredato"): note.append("arredato")
            if a.get("privato"):  note.append("da privato")
            if a["esito"] != "passa": note.append("**al limite**")
            righe.append(
                f"| {a['citta'].capitalize()} | {a.get('zona') or '—'} | {e(a['canone'])} | "
                f"{a['locali']} | {a['mq']} | {a.get('eur_mq','—')} | {e(a['canone_sostenibile'])} | "
                f"{'+' if a['margine']>=0 else ''}{e(a['margine'])} | {', '.join(note) or '—'} |")
        righe += ["", "### I link", ""]
        for a in nuovi[:40]:
            righe.append(f"- [{a['titolo']}]({a['url']}) — {e(a['canone'])}, {a['locali']} locali")

    righe += ["", "---", "",
              f"Vagliati {len(annunci)} annunci in totale. "
              f"Il canone sostenibile è stimato come camere × canone massimo della città "
              f"(camere = locali − 1): serve a scremare, non a valutare. "
              f"Il conto vero si fa nel Vaglio Deal.", ""]

    f = REPORT / f"{oggi.isoformat()}-{modo}.md"
    # Un giro che non trova novita NON deve cancellare il report buono dello stesso
    # giorno: succede quando si rilancia il giro a mano dopo che e gia girato.
    if f.exists() and not nuovi and f.stat().st_size > 600:
        (REPORT / "ULTIMO.md").write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
        # nuovi.json NON va toccato qui: tiene l'elenco del giro che le novita le
        # aveva trovate, ed e quello che la vetrina deve continuare a mostrare
        print(f"report: {f} (lasciato intatto, nessuna novità da aggiungere)")
        json.dump(sorted(visti | {a["url"] for a in annunci if a.get("url")}),
                  open(visti_f, "w"), indent=0)
        return 0
    f.write_text("\n".join(righe), encoding="utf-8")
    # copia sempre allo stesso nome: e il file che Alex apre, e non cambia mai
    (REPORT / "ULTIMO.md").write_text("\n".join(righe), encoding="utf-8")
    # la vetrina deve mostrare esattamente questi, non tutto lo storico
    json.dump(nuovi, open(BASE / "nuovi.json", "w"), ensure_ascii=False)

    json.dump(sorted(visti | {a["url"] for a in annunci if a.get("url")}),
              open(visti_f, "w"), indent=0)
    print(f"report: {f}")
    print(f"nuovi: {len(nuovi)}")
    return len(nuovi)

if __name__ == "__main__":
    arg = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(arg[0] if arg else "giornaliero", tutti="--tutti" in sys.argv)
