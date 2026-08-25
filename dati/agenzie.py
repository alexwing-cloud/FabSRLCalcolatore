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


# Indirizzi finti che i temi dei siti si portano dietro, piu il rumore tecnico
SCARTA_MAIL = ("example", "sentry", "wixpress", "@2x", ".png", ".jpg", ".gif",
               "domain.com", "yourdomain", "email.com", "mail.com", "company.com",
               "privacy@", "noreply", "no-reply", "test@", "nome@", "tuo@",
               "sentry.io", "@sentry", "wordpress")


def ripulisci(m):
    """Le email escono attaccate a pezzi di URL o di codice: vanno smontate."""
    m = m.strip().strip(".,;:)('\"")
    m = re.sub(r"^(?:[0-9a-f]{2})+(?=[a-z])", "", m)   # resti di %20 e simili
    m = re.sub(r"^\d+", "", m)
    return m.lower()


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


RUMORE = ("agenzia", "immobiliare", "immobiliari", "immobilien", "studio", "srl",
          "snc", "sas", "spa", "s.r.l.", "di", "the", "real", "estate", "group",
          "affiliato", "tecnocasa", "rete", "d'impresa")


def domini_probabili(nome):
    """Quando TrovaCasa non pubblica il sito, si prova a indovinarlo dal nome.
    Ogni tentativo viene poi verificato: il sito deve nominare l'agenzia."""
    pulito = re.sub(r"[^a-z0-9 ]", " ", nome.lower())
    parole = [p for p in pulito.split() if len(p) > 2]
    forti = [p for p in parole if p not in RUMORE] or parole
    basi = ["".join(forti[:2]), "-".join(forti[:2]), "".join(forti),
            "immobiliare" + forti[0], forti[0] + "immobiliare"]
    # Una parola sola e corta ("martin", "gallery", "paris", "club") non identifica
    # nessuno: www.martin.it e un sito qualsiasi, non l'agenzia Pichler.
    if len(forti[0]) >= 7:
        basi.insert(0, forti[0])
    fuori = []
    for b in dict.fromkeys(basi):
        if 6 <= len(b) <= 28:
            fuori += [f"www.{b}.it", f"{b}.it"]
    return fuori[:10]


def verifica(dominio, nome, citta):
    """Il dominio e davvero di quell'agenzia?

    Basta che compaia il nome OPPURE la citta. Pretenderli entrambi scartava siti
    validi: rimmo.it e l'agenzia giusta ma la home e in tedesco e non dice Bolzano.
    """
    for schema in ("https://", "http://"):
        try:
            req = urllib.request.Request(schema + dominio, headers={"User-Agent": UA})
            pag = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
        except Exception:
            continue
        testo = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", pag)).lower()
        chiave = [p for p in re.sub(r"[^a-z0-9 ]", " ", nome.lower()).split()
                  if len(p) > 3 and p not in RUMORE]
        # deve dire chi e (il nome) E cosa fa (immobiliare) o dove sta (la citta):
        # con un solo indizio passavano siti che non c'entrano niente
        nome_ok = any(k in testo for k in chiave[:2])
        mestiere_ok = any(x in testo for x in
                          ("immobil", "agenzia", "real estate", "makler", "case in vendita"))
        if nome_ok and (mestiere_ok or citta.lower()[:5] in testo):
            return True
    return False


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
            trovate = [ripulisci(m) for m in re.findall(r"[\w.+-]+@[\w-]+\.[\w.]{2,10}", pag)]
            pulite = [m for m in trovate
                      if not any(x in m for x in SCARTA_MAIL)
                      and 6 < len(m) < 60 and re.match(r"^[\w.+-]+@[\w.-]+\.[a-z]{2,6}$", m)]
            # l'indirizzo deve stare sul dominio dell'agenzia: se il sito espone la
            # mail di un fornitore o di una piattaforma, non e un contatto valido
            radice = dominio.replace("www.", "").split(".")[0]
            proprie = [m for m in pulite if radice in m.split("@")[-1]]
            if proprie:
                return proprie[0]
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
            a["sito"] = sito_di(a["url"]); time.sleep(0.7)
            if not a["sito"]:                       # non pubblicato: si prova a dedurlo
                for d in domini_probabili(a["nome"]):
                    if verifica(d, a["nome"], a["citta"]):
                        a["sito"] = d; a["dedotto"] = True; break
                    time.sleep(0.2)
            a["email"] = mail_dal_sito(a.get("sito")); time.sleep(0.4)
            print(f"    {i:3d}/{args.contatti} {a['nome'][:30]:30s} "
                  f"{a.get('sito') or '—':28s} {a.get('email') or '—'}")

    json.dump(tutte, open(BASE / "agenzie.json", "w"), indent=1, ensure_ascii=False)
    print(f"\n{len(tutte)} agenzie in tutto. Le più rilevanti:\n")
    for a in sorted(tutte, key=lambda x: -x["punteggio"])[:20]:
        print(f"  [{a['punteggio']:6.1f}] {a['citta']:9s} {a['nome'][:34]:34s} "
              f"{a['annunci']:4d} ann · {', '.join(a['tratta'])[:44]}")


if __name__ == "__main__":
    main()
