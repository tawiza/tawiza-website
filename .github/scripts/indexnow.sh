#!/usr/bin/env bash
# IndexNow ping · soumet automatiquement les URLs modifiées à Bing/Yandex/Seznam
# pour indexation rapide (< 1h vs 24-72h pour Google).
#
# Usage  : bash .github/scripts/indexnow.sh url1 [url2 ...]
# Auto   : depuis CI, déduit les URLs des fichiers modifiés au commit
# Doc    : https://www.indexnow.org/documentation
#
# La clé est validée via un fichier au root : /<KEY>.txt contenant <KEY>.
# Tawiza key : b0f36c67d6c1c2e5bc72f7cb0020c066 (cf. /b0f36c67d6c1c2e5bc72f7cb0020c066.txt)

set -euo pipefail

KEY="b0f36c67d6c1c2e5bc72f7cb0020c066"
HOST="tawiza.fr"
KEY_LOCATION="https://${HOST}/${KEY}.txt"

# Si pas d'argument, déduit depuis le diff git du dernier commit
if [ $# -eq 0 ]; then
    CHANGED=$(git diff --name-only HEAD~1 HEAD 2>/dev/null | grep -E '\.html$' || true)
    URLS=()
    while IFS= read -r f; do
        [ -z "$f" ] && continue
        # Map fichiers HTML vers URLs publiques
        if [[ "$f" == "index.html" ]]; then
            URLS+=("https://${HOST}/")
        elif [[ "$f" == */index.html ]]; then
            URLS+=("https://${HOST}/${f%index.html}")
        else
            URLS+=("https://${HOST}/${f}")
        fi
    done <<< "$CHANGED"
else
    URLS=("$@")
fi

if [ ${#URLS[@]} -eq 0 ]; then
    echo "Aucune URL à soumettre."
    exit 0
fi

echo "Soumission IndexNow de ${#URLS[@]} URL(s) pour ${HOST}..."
printf '  %s\n' "${URLS[@]}"

# Construit le payload JSON
URL_LIST=$(printf '"%s",' "${URLS[@]}")
URL_LIST="[${URL_LIST%,}]"

PAYLOAD=$(cat <<EOF
{
  "host": "${HOST}",
  "key": "${KEY}",
  "keyLocation": "${KEY_LOCATION}",
  "urlList": ${URL_LIST}
}
EOF
)

# Envoie au endpoint IndexNow officiel (relayé à Bing, Yandex, Seznam, Naver)
RESPONSE=$(curl -sS -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "${PAYLOAD}" \
    "https://api.indexnow.org/IndexNow")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

case "$HTTP_CODE" in
    200|202)
        echo "✓ IndexNow OK (HTTP $HTTP_CODE)"
        ;;
    400)
        echo "✗ Bad request : ${BODY}"
        exit 1
        ;;
    403)
        echo "✗ Key invalide ou keyLocation injoignable"
        exit 1
        ;;
    422)
        echo "✗ URL ne correspond pas au host : ${BODY}"
        exit 1
        ;;
    *)
        echo "? Réponse inattendue HTTP ${HTTP_CODE} : ${BODY}"
        ;;
esac
