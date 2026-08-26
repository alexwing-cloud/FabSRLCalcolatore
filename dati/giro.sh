#!/bin/bash
# Il giro automatico. Due modi:
#   ./giro.sh giornaliero   solo annunci (veloce, ~2 minuti)
#   ./giro.sh settimanale   anche i dati di mercato delle 49 citta (~3 minuti)
#
# Gira sul Mac di Alex con launchd. Usa il token gia nel portachiavi per il push:
# non serve nessuna autorizzazione aggiuntiva.
set -uo pipefail
MODO="${1:-giornaliero}"
QUI="$(cd "$(dirname "$0")" && pwd)"
REPO="$(dirname "$QUI")"
LOG="$REPO/report/giro.log"
mkdir -p "$REPO/report"
exec >> "$LOG" 2>&1
echo "===== $(date '+%Y-%m-%d %H:%M:%S')  modo=$MODO"

cd "$QUI" || exit 1
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

if [ "$MODO" = "settimanale" ]; then
  echo "-- dati di mercato"
  python3 raccogli.py || echo "!! raccogli.py ha avuto problemi, proseguo coi dati vecchi"
  python3 genera.py   || { echo "!! genera.py fallito"; exit 1; }
fi

echo "-- annunci"
python3 annunci.py --pagine 3 --mq-min 180 || echo "!! annunci.py ha avuto problemi"

echo "-- report"
NUOVI=$(python3 report.py "$MODO" | awk -F': ' '/^nuovi/{print $2}')
python3 vetrina.py || echo "!! vetrina.py fallito"
# anche la versione con le foto incorporate, cosi la pagina online e sempre pronta
python3 vetrina_web.py && python3 vetrina.py --web || echo "!! vetrina web non rigenerata"

cd "$REPO" || exit 1
if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -q -m "Giro $MODO del $(date '+%d/%m/%Y'): ${NUOVI:-0} annunci nuovi

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
  git push -q origin main && echo "-- pushato" || echo "!! push fallito"
else
  echo "-- niente da committare"
fi

# avviso a schermo, cosi Alex sa che c'e da leggere
if [ "${NUOVI:-0}" -gt 0 ] 2>/dev/null; then
  osascript -e "display notification \"${NUOVI} annunci nuovi da guardare\" with title \"Vaglio Deal\" sound name \"Glass\"" || true
fi
echo "-- fine"
