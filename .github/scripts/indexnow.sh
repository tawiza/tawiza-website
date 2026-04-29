#!/usr/bin/env bash
# IndexNow ping · soumet automatiquement les URLs modifiées à Bing/Yandex/Seznam
# pour indexation rapide (< 1h vs 24-72h pour Google).
#
# Usage  : bash .github/scripts/indexnow.sh url1 [url2 ...]
# Auto   : depuis CI, déduit les URLs des fichiers modifiés au commit
# Doc    : https://www.indexnow.org/documentation
#
# Multi-host : les URLs sont automatiquement regroupées par host et un ping
# séparé est émis pour chaque host. La clé doit être hébergée à la racine
# de CHAQUE host visé (cf. /b0f36c67d6c1c2e5bc72f7cb0020c066.txt).

set -euo pipefail

KEY="b0f36c67d6c1c2e5bc72f7cb0020c066"

# Hosts supportés (pour validation et auto-mapping fichier → URL via deploy-watch)
declare -A SUPPORTED_HOSTS=(
    ["tawiza.fr"]=1
    ["panoptic.tawiza.fr"]=1
)

# Si pas d'argument, déduit depuis le diff git du dernier commit
if [ $# -eq 0 ]; then
    CHANGED=$(git diff --name-only HEAD~1 HEAD 2>/dev/null | grep -E '\.html$' || true)
    URLS=()
    while IFS= read -r f; do
        [ -z "$f" ] && continue
        # Mapping minimal pour usage CLI seul ; deploy-watch fait sa propre logique
        if [[ "$f" == panoptic/public/index.html ]]; then
            URLS+=("https://panoptic.tawiza.fr/")
        elif [[ "$f" == panoptic/public/* ]]; then
            URLS+=("https://panoptic.tawiza.fr/${f#panoptic/public/}")
        elif [[ "$f" == "index.html" ]]; then
            URLS+=("https://tawiza.fr/")
        elif [[ "$f" == */index.html ]]; then
            URLS+=("https://tawiza.fr/${f%index.html}")
        else
            URLS+=("https://tawiza.fr/${f}")
        fi
    done <<< "$CHANGED"
else
    URLS=("$@")
fi

if [ ${#URLS[@]} -eq 0 ]; then
    echo "Aucune URL à soumettre."
    exit 0
fi

# Regroupement par host : une entrée du dict par host, valeur = liste d'URLs
# séparées par des espaces (les URLs n'en contiennent jamais après normalisation)
declare -A URLS_BY_HOST
for url in "${URLS[@]}"; do
    # Extraction host : https://HOST/path → HOST
    host=$(echo "$url" | sed -E 's|^https?://([^/]+).*|\1|')
    if [ -z "${SUPPORTED_HOSTS[$host]:-}" ]; then
        echo "✗ Host non supporté : ${host} (ignore ${url})" >&2
        continue
    fi
    URLS_BY_HOST[$host]="${URLS_BY_HOST[$host]:-}${url} "
done

# Ping séquentiel par host
GLOBAL_RC=0
for host in "${!URLS_BY_HOST[@]}"; do
    KEY_LOCATION="https://${host}/${KEY}.txt"
    # Reconstruit le tableau URL pour ce host
    read -r -a HOST_URLS <<< "${URLS_BY_HOST[$host]}"

    echo "Soumission IndexNow de ${#HOST_URLS[@]} URL(s) pour ${host}..."
    printf '  %s\n' "${HOST_URLS[@]}"

    URL_LIST=$(printf '"%s",' "${HOST_URLS[@]}")
    URL_LIST="[${URL_LIST%,}]"

    PAYLOAD=$(cat <<EOF
{
  "host": "${host}",
  "key": "${KEY}",
  "keyLocation": "${KEY_LOCATION}",
  "urlList": ${URL_LIST}
}
EOF
)

    RESPONSE=$(curl -sS -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/json; charset=utf-8" \
        -d "${PAYLOAD}" \
        "https://api.indexnow.org/IndexNow")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    case "$HTTP_CODE" in
        200|202)
            echo "✓ ${host} : IndexNow OK (HTTP $HTTP_CODE)"
            ;;
        400)
            echo "✗ ${host} : Bad request : ${BODY}"
            GLOBAL_RC=1
            ;;
        403)
            echo "✗ ${host} : Key invalide ou keyLocation injoignable"
            GLOBAL_RC=1
            ;;
        422)
            echo "✗ ${host} : URL ne correspond pas au host : ${BODY}"
            GLOBAL_RC=1
            ;;
        *)
            echo "? ${host} : Réponse inattendue HTTP ${HTTP_CODE} : ${BODY}"
            GLOBAL_RC=1
            ;;
    esac
done

exit $GLOBAL_RC
