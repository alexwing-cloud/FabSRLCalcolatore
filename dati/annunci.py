#!/usr/bin/env python3
"""Ricerca nazionale di immobili in locazione che rientrano nei parametri FAB.

Terzo pezzo del giro:  raccogli.py (mercato)  ->  annunci.py (offerta)  ->  genera.py (pagine)

Cosa fa: per ogni citta in elenco scarica gli annunci di affitto, tiene solo quelli
da 3 locali in su, e li confronta col canone massimo sostenibile di quella citta,
che arriva da citta.json. Quello che non rientra viene scartato subito.

Il confronto qui e una prima scrematura, non una valutazione: serve a buttare via
il 95% degli annunci. Quelli che restano si valutano uno per uno nel Vaglio Deal.

Fonte: trovacasa.it, che consente l'accesso automatico alle pagine di elenco
(robots.txt vieta solo /membership/, /my/, *?idtags= e */similarpartial/*).
immobiliare.it, casa.it, idealista.it e wikicasa.it rispondono 403 con CAPTCHA:
non sono utilizzabili e non vanno riprovati.
"""
import re, html, json, time, pathlib, urllib.request, urllib.error, argparse

BASE = pathlib.Path(__file__).parent
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
PAUSA = 1.2          # cortesia verso la fonte: una pagina ogni 1,2 secondi

# Un locale e il soggiorno, gli altri diventano camere vendibili. Rozzo ma onesto:
# e la stessa logica per cui Venezian conta 12 unita su 4 appartamenti.
def camere(locali): return max(1, locali - 1)

CHIAVI_ARREDO = ("arredato", "parzialmente arredato")


def pagina(citta, n):
    url = f"https://www.trovacasa.it/appartamenti-in-affitto/{citta}"
    if n > 1:
        url += f"?page={n}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "it-IT,it;q=0.9"})
    try:
        return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return "" if e.code == 404 else ""
    except Exception:
        return ""


def estrai(pag, citta):
    """Ogni scheda annuncio diventa un dizionario."""
    schede = re.findall(
        r'<div class="immobileListing__card js_immobileListing_card">(.*?)'
        r'(?=<div class="immobileListing__card js_immobileListing_card">|'
        r'<div class="immobileListing__cardContainer|$)', pag, re.S)
    fuori = []
    for s in schede:
        def uno(pat):
            m = re.search(pat, s, re.S)
            return html.unescape(m.group(1)).strip() if m else None

        titolo = uno(r'class="card__title[^"]*">(.*?)</a>')
        prezzo = uno(r'class="card__price">(.*?)</span>')
        if not titolo or not prezzo:
            continue
        m = re.search(r'([\d.]+)', prezzo.replace(".", ""))
        canone = int(m.group(1)) if m else None
        if not canone:
            continue

        info = [html.unescape(x) for x in re.findall(r'class="card__info">(.*?)</span>', s)]
        loc = next((int(re.search(r'(\d+)', x).group(1)) for x in info if "local" in x), None)
        mq  = next((int(re.search(r'(\d+)', x).group(1)) for x in info if "m" in x and "local" not in x), None)
        tag = [html.unescape(x).strip() for x in re.findall(r'class="annuncioTag">(.*?)</p>', s)]
        desc = uno(r'class="card__description">(.*?)</p>') or ""
        desc = re.sub(r"<[^>]+>", " ", desc)
        link = uno(r'<a href="(/annunci/[^"]+)"')

        fuori.append({
            "citta": citta, "titolo": titolo, "zona": uno(r'class="card__quartiere">(.*?)</span>'),
            "canone": canone, "locali": loc, "mq": mq, "tag": tag,
            "arredato": any(t.lower() in CHIAVI_ARREDO for t in tag),
            "descrizione": desc[:300],
            "privato": any("privato" in t.lower() for t in tag),
            "url": "https://www.trovacasa.it" + link if link else None,
        })
    return fuori


# L'elenco di trovacasa non e pulito: mischia camere singole, posti letto e qualche
# annuncio di vendita con la descrizione riciclata. Senza questi controlli il vaglio
# promuove un cinque locali a 350 euro, che non e un affitto intero.
def plausibile(a, mediana_citta=None):
    if not a["mq"] or a["mq"] < 40:
        return "superficie assente o da camera singola"
    q = a["canone"] / a["mq"]
    if q > 45:
        return f"{q:.1f} €/mq: fuori scala, probabile errore o vendita"
    # La soglia bassa non puo essere fissa: 6 €/mq e caro a Cuneo e regalato a Bolzano.
    # Si calibra sulla mediana degli annunci di quella stessa citta: sotto meta della
    # mediana non e un immobile intero, e una camera o un posto letto.
    if mediana_citta and q < mediana_citta * 0.5:
        return f"{q:.1f} €/mq contro una mediana cittadina di {mediana_citta:.1f}: non è un intero"
    if q < 3:
        return f"{q:.1f} €/mq: prezzo da camera o da posto letto"
    d = a.get("descrizione", "").lower()
    if "in vendita" in d or "vendesi" in d:
        return "la descrizione parla di vendita"
    return None


def vaglia(a, canone_max_citta, locali_min, mediana_citta=None):
    """Prima scrematura contro il canone massimo sostenibile della citta."""
    if not a["locali"] or a["locali"] < locali_min:
        return None
    motivo = plausibile(a, mediana_citta)
    if motivo:
        a["scartato_perche"] = motivo
        return None
    a["camere"] = camere(a["locali"])
    a["canone_sostenibile"] = round(a["camere"] * canone_max_citta)
    a["margine"] = a["canone_sostenibile"] - a["canone"]
    a["incidenza"] = a["canone"] / a["canone_sostenibile"] if a["canone_sostenibile"] else 9
    a["esito"] = ("passa" if a["margine"] >= 0
                  else "al limite" if a["incidenza"] <= 1.15
                  else "scarta")
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--citta", nargs="*", help="slug delle città; default: quelle sopra Trieste più Trieste")
    ap.add_argument("--pagine", type=int, default=3, help="pagine per città (24 annunci l'una)")
    ap.add_argument("--locali-min", type=int, default=3)
    args = ap.parse_args()

    mercato = {c["slug"]: c for c in json.load(open(BASE / "citta.json", encoding="utf-8"))}
    if args.citta:
        citta = args.citta
    else:
        # di default si guarda dove il mercato regge: pari a Trieste o meglio
        citta = [s for s, c in mercato.items() if c["vs25"] >= -4]

    tutti, scartati = [], 0
    for s in citta:
        cm = mercato.get(s, {}).get("canone25")
        if not cm:
            print(f"  {s:16s} nessun dato di mercato, salto"); continue
        trovati = []
        for n in range(1, args.pagine + 1):
            p = pagina(s, n)
            if not p: break
            trovati += estrai(p, s)
            time.sleep(PAUSA)
        # Mediana di riferimento della citta. Va calcolata SOLO sugli annunci gia
        # plausibili: a Trieste l'elenco contiene affitti turistici a 5.000 euro per
        # 50 mq (100 euro/mq) che da soli portavano la mediana a 34 e facevano
        # scartare tutti gli affitti veri da 8-12 euro/mq.
        qq = sorted(q for q in (a["canone"]/a["mq"] for a in trovati if a["mq"] and a["mq"] >= 30)
                    if 3 <= q <= 45)
        mediana = qq[len(qq)//2] if qq else None
        buoni = []
        for a in trovati:
            v = vaglia(a, cm, args.locali_min, mediana)
            if v is None: scartati += 1
            elif v["esito"] == "scarta": scartati += 1
            else: buoni.append(v)
        tutti += buoni
        print(f"  {s:16s} {len(trovati):3d} annunci → {len(buoni):2d} da guardare "
              f"(canone max {cm:.0f} €/camera · mediana {mediana:.1f} €/mq)"
              if mediana else f"  {s:16s} {len(trovati):3d} annunci → {len(buoni):2d} da guardare")

    tutti.sort(key=lambda a: -a["margine"])
    for a in tutti:
        a["eur_mq"] = round(a["canone"] / a["mq"], 1)
    json.dump(tutti, open(BASE / "annunci.json", "w"), indent=1, ensure_ascii=False)
    print(f"\n{len(tutti)} annunci da guardare, {scartati} scartati.")
    for a in tutti[:15]:
        print(f"  [{a['esito']:9s}] {a['citta']:10s} {a['canone']:6d} € · {a['locali']} locali · "
              f"{a['mq'] or '?'} mq · sostenibile {a['canone_sostenibile']:6d} € "
              f"({'+' if a['margine']>=0 else ''}{a['margine']}) "
              f"{a['eur_mq']:4.1f} €/mq {'· arredato' if a['arredato'] else ''}"
              f"{' · da privato' if a['privato'] else ''}")


if __name__ == "__main__":
    main()
