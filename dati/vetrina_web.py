#!/usr/bin/env python3
"""Versione pubblicabile della vetrina: le foto sono incorporate nel file.

La vetrina locale carica le foto da trovacasa. Una pagina pubblicata non puo farlo
(le richieste verso altri siti sono bloccate), quindi qui le miniature vengono
scaricate, rimpicciolite e cucite dentro l'HTML come dati.
"""
import json, base64, io as _io, pathlib, urllib.request, concurrent.futures as cf
from PIL import Image

BASE = pathlib.Path(__file__).parent
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
LARGH, QUALITA = 360, 62


def miniatura(url):
    if not url or "noimg" in url:
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        grezza = urllib.request.urlopen(req, timeout=25).read()
        im = Image.open(_io.BytesIO(grezza)).convert("RGB")
        if im.width > LARGH:
            im = im.resize((LARGH, round(im.height * LARGH / im.width)), Image.LANCZOS)
        buf = _io.BytesIO()
        im.save(buf, "JPEG", quality=QUALITA, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def main():
    ann = json.load(open(BASE / "annunci.json", encoding="utf-8"))
    ann = [a for a in ann if a.get("url")]
    ann.sort(key=lambda a: -a["margine"])

    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for a, mini in zip(ann, ex.map(miniatura, [a.get("foto") for a in ann])):
            a["mini"] = mini

    peso = sum(len(a["mini"] or "") for a in ann)
    print(f"miniature incorporate: {sum(1 for a in ann if a['mini'])}/{len(ann)} — {peso//1024//1024} MB")

    # se si sfora, si tengono i migliori: meglio una pagina che si apre
    while peso > 11 * 1024 * 1024 and len(ann) > 60:
        via = ann.pop()
        peso -= len(via["mini"] or "")
        print(f"  tolto l'ultimo per stare nei limiti, restano {len(ann)}")

    json.dump(ann, open(BASE / "annunci_web.json", "w"), ensure_ascii=False)
    print(f"pronti {len(ann)} immobili, {peso//1024//1024} MB di foto")


if __name__ == "__main__":
    main()
