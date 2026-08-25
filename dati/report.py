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

def main(modo="giornaliero"):
    annunci = json.load(open(BASE / "annunci.json", encoding="utf-8"))
    visti_f = BASE / "visti.json"
    visti = set(json.load(open(visti_f))) if visti_f.exists() else set()

    nuovi = [a for a in annunci if a.get("url") and a["url"] not in visti]
    nuovi.sort(key=lambda a: -a["margine"])

    oggi = datetime.date.today()
    righe = [f"# Report {modo} — {oggi.strftime('%d/%m/%Y')}", ""]

    if not nuovi:
        righe += [f"**Nessun annuncio nuovo che rientri nei parametri.** "
                  f"Il vaglio ha riguardato {len(annunci)} annunci già noti.", ""]
    else:
        forti = [a for a in nuovi if a["esito"] == "passa"]
        righe += [f"**{len(nuovi)} annunci nuovi**, di cui {len(forti)} entro il canone sostenibile.", ""]
        righe += ["| Città | Zona | Canone | Locali | m² | €/mq | Sostenibile | Margine | Note |",
                  "|---|---|---:|---:|---:|---:|---:|---:|---|"]
        for a in nuovi[:25]:
            note = []
            if a.get("arredato"): note.append("arredato")
            if a.get("privato"):  note.append("da privato")
            if a["esito"] != "passa": note.append("**al limite**")
            righe.append(
                f"| {a['citta'].capitalize()} | {a.get('zona') or '—'} | {e(a['canone'])} | "
                f"{a['locali']} | {a['mq']} | {a.get('eur_mq','—')} | {e(a['canone_sostenibile'])} | "
                f"{'+' if a['margine']>=0 else ''}{e(a['margine'])} | {', '.join(note) or '—'} |")
        righe += ["", "### I link", ""]
        for a in nuovi[:25]:
            righe.append(f"- [{a['titolo']}]({a['url']}) — {e(a['canone'])}, {a['locali']} locali")

    righe += ["", "---", "",
              f"Vagliati {len(annunci)} annunci in totale. "
              f"Il canone sostenibile è stimato come camere × canone massimo della città "
              f"(camere = locali − 1): serve a scremare, non a valutare. "
              f"Il conto vero si fa nel Vaglio Deal.", ""]

    f = REPORT / f"{oggi.isoformat()}-{modo}.md"
    f.write_text("\n".join(righe), encoding="utf-8")

    json.dump(sorted(visti | {a["url"] for a in annunci if a.get("url")}),
              open(visti_f, "w"), indent=0)
    print(f"report: {f}")
    print(f"nuovi: {len(nuovi)}")
    return len(nuovi)

if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1] if len(sys.argv) > 1 else "giornaliero") >= 0 else 1)
