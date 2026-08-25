#!/usr/bin/env python3
"""Elenco delle agenzie immobiliari nelle citta target, ordinate per rilevanza.

Serve al canale diretto: le palazzine intere e le strutture ricettive NON passano
dai portali (le categorie palazzi-in-affitto e alberghi-in-affitto rispondono ma
sono vuote ovunque). Quel mercato si muove tramite agenti, quindi bisogna scrivere
a loro dicendo cosa cerchiamo, invece di aspettare che compaia un annuncio.

Ordina per: quante cose trattano di commerciale e di pregio, e quanto sono grosse.
"""
import re, html, json, time, pathlib, urllib.request, argparse

BASE = pathlib.Path(__file__).parent
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
PAUSA = 1.2


def pagina(citta, n=1):
    url = f"https://www.trovacasa.it/agenzie-immobiliari/{citta}"
    if n > 1:
        url += f"?page={n}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "it-IT,it;q=0.9"})
    try:
        return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    except Exception:
        return ""


def estrai(pag, citta):
    fuori = []
    blocchi = re.split(r'<div class="cardAgenzia js_card">', pag)[1:]
    for b in blocchi:
        def uno(pat):
            m = re.search(pat, b, re.S)
            return html.unescape(m.group(1)).strip() if m else None

        nome = uno(r'class="js_card_link linkTablet cardAgenzia__name">(.*?)</a>')
        if not nome:
            continue
        tel = [html.unescape(t).strip(" /") for t in re.findall(r'class="phone">(.*?)</span>', b)]
        n_ann = uno(r'class="cardAgenzia__nrAnnunci">([\d.]+) annunci')
        # cosa tratta: i link alle sue sezioni dicono il mestiere
        sezioni = set(re.findall(r'/annunci|/([a-z-]+)-in-(?:vendita|affitto)"', b))
        sezioni.discard("")
        fuori.append({
            "citta": citta, "nome": nome,
            "indirizzo": uno(r'class="cardAgenzia__address">(.*?)</p>'),
            "telefoni": tel,
            "annunci": int(n_ann.replace(".", "")) if n_ann else 0,
            "tratta": sorted(sezioni),
            "url": "https://www.trovacasa.it" + (uno(r'href="(/agenzie-immobiliari/[^"]+)" class="js_card_link') or ""),
        })
    return fuori


def punteggio(a):
    """Chi ci serve: chi tratta commerciale o pregio, e ha volume."""
    p = min(a["annunci"], 300) / 10
    for s in a["tratta"]:
        if "commerciali" in s:   p += 25      # commerciale = ramo d'azienda, strutture
        if "palazzi" in s:       p += 25
        if "ville" in s:         p += 10      # pregio
        if "case" in s:          p += 3
    return round(p, 1)


SCARTA_MAIL = ("example", "sentry", "wixpress", "@2x", ".png", ".jpg", "domain.com",
               "yourdomain", "email.com", "privacy@", "noreply", "no-reply")


def sito_di(url_scheda):
    """La scheda dell'agenzia riporta il sito come testo: 'Sito: www.tale.it'."""
    try:
        req = urllib.request.Request(url_scheda, headers={"User-Agent": UA})
        s = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
    except Exception:
        return None
    t = re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>", "", s, flags=re.S))
    m = re.search(r"Sito:\s*([\w.-]+\.[a-z]{2,6})", html.unescape(t))
    return m.group(1) if m else None


def mail_dal_sito(dominio):
    """Cerca l'indirizzo sulla home e sulla pagina contatti dell'agenzia."""
    if not dominio:
        return None
    for percorso in ("", "/contatti", "/contatti.html", "/contact", "/chi-siamo"):
        for schema in ("https://", "http://"):
            try:
                req = urllib.request.Request(schema + dominio + percorso,
                                             headers={"User-Agent": UA})
                pag = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
            except Exception:
                continue
            trovate = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]{2,10}", pag)
            pulite = [m for m in trovate
                      if not any(x in m.lower() for x in SCARTA_MAIL) and len(m) < 60]
            if pulite:
                # meglio quella sul dominio dell'agenzia
                proprie = [m for m in pulite if dominio.replace("www.", "") in m.lower()]
                return (proprie or pulite)[0]
            break
        time.sleep(0.4)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--citta", nargs="*", required=True)
    ap.add_argument("--pagine", type=int, default=2)
    ap.add_argument("--contatti", type=int, default=0,
                    help="quante agenzie in cima cercare anche l'email")
    args = ap.parse_args()

    tutte = []
    for c in args.citta:
        trovate = []
        for n in range(1, args.pagine + 1):
            p = pagina(c, n)
            if not p:
                break
            nuove = estrai(p, c)
            if not nuove:
                break
            trovate += nuove
            time.sleep(PAUSA)
        for a in trovate:
            a["punteggio"] = punteggio(a)
        trovate.sort(key=lambda a: -a["punteggio"])
        tutte += trovate
        print(f"  {c:14s} {len(trovate):3d} agenzie")

    tutte.sort(key=lambda a: -a["punteggio"])
    if args.contatti:
        print(f"\n  cerco i contatti delle prime {args.contatti}…")
        for i, a in enumerate(tutte[:args.contatti], 1):
            a["sito"] = sito_di(a["url"]); time.sleep(0.8)
            a["email"] = mail_dal_sito(a.get("sito")); time.sleep(0.5)
            print(f"    {i:3d}/{args.contatti} {a['nome'][:30]:30s} "
                  f"{a.get('sito') or '—':28s} {a.get('email') or '—'}")

    json.dump(tutte, open(BASE / "agenzie.json", "w"), indent=1, ensure_ascii=False)
    print(f"\n{len(tutte)} agenzie in tutto. Le più rilevanti:\n")
    for a in sorted(tutte, key=lambda x: -x["punteggio"])[:20]:
        print(f"  [{a['punteggio']:6.1f}] {a['citta']:9s} {a['nome'][:34]:34s} "
              f"{a['annunci']:4d} ann · {', '.join(a['tratta'])[:44]}")


if __name__ == "__main__":
    main()
