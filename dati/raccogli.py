import re, html, json, urllib.request, time, sys
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
CITTA=["trieste","torino","bergamo","verona","padova","brescia","parma","modena","bolzano",
"trento","udine","vicenza","treviso","ferrara","ravenna","rimini","perugia","livorno","pisa",
"lucca","genova","la-spezia","salerno","lecce","bari","cagliari","catania","siracusa","como",
"varese","novara","piacenza","ancona","pescara","reggio-emilia","mantova","cremona","pavia",
"siena","arezzo","monza","alessandria","pordenone","gorizia","rovigo","belluno","forli","cuneo","asti","savona"]
def n(x):
    x=x.replace('.','').replace(',','.')
    try: return float(x)
    except: return None
def prendi(slug):
    url=f"https://www.guestfavorites.com/tasso-di-occupazione-airbnb-{slug}-italy"
    req=urllib.request.Request(url, headers={"User-Agent":UA,"Accept-Language":"it-IT,it;q=0.9"})
    try: raw=urllib.request.urlopen(req, timeout=30).read().decode("utf-8","ignore")
    except Exception as e: return {"slug":slug,"errore":str(e)[:60]}
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',raw,flags=re.S)
    t=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',t)))
    d={"slug":slug}
    m=re.search(r'Tariffa giornaliera media \(TGM\) ([\d.,]+) ?€', t);  d["adr"]=n(m.group(1)) if m else None
    m=re.search(r'Tasso di occupazione (\d+)\s?%', t);                  d["occ"]=n(m.group(1)) if m else None
    m=re.search(r'Ricavi annuali medi ([\d.,]+) ?€', t);                d["ricavo"]=n(m.group(1)) if m else None
    m=re.search(r'Annunci attivi ([\d.,]+)', t);                        d["annunci"]=n(m.group(1)) if m else None
    m=re.search(r'premium \(top 10%\)[^0-9]*([\d.,]+) ?€.*?top 25%\) guadagnano almeno ([\d.,]+) ?€.*?media producono circa ([\d.,]+) ?€.*?inferiore\) ottengono ricavi vicini a ([\d.,]+) ?€', t)
    if m: d["r10"],d["r25"],d["rmed"],d["rbot"]=[n(m.group(i)) for i in (1,2,3,4)]
    m=re.search(r'Periodo: ([A-Za-z]+ \d{4} - [A-Za-z]+ \d{4})', t);    d["periodo"]=m.group(1) if m else None
    return d
out=[]
for i,c in enumerate(CITTA):
    r=prendi(c); out.append(r)
    print(("  %-16s "%c)+("ERR "+r["errore"] if "errore" in r else
      "adr=%s occ=%s ricavo=%s annunci=%s"%(r.get("adr"),r.get("occ"),r.get("ricavo"),r.get("annunci"))), flush=True)
    time.sleep(0.8)
json.dump(out, open("citta.json","w"), indent=1)
print("\nsalvate", len([o for o in out if o.get("adr")]), "citta su", len(CITTA))
