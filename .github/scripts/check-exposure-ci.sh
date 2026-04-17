#!/usr/bin/env bash
# Check patterns exposition — version CI GitHub Actions.
# Doctrine : R2 (dual-repo), R3 (pas infos internes), R12 (théories invisibles),
#            R14 (pas darija), R31 (PRD interne si théories).

set -uo pipefail

FORBIDDEN=(
    '/root/'
    '/data/projects/'
    '/opt/tawiza-cli'
    '100\.116\.[0-9]+\.[0-9]+'
    '100\.105\.[0-9]+\.[0-9]+'
    '192\.168\.1\.[0-9]+'
    '\bMPtoO\b'
    '\bmoltbot\b'
    '\btawiza-cli\b'
    'qm guest exec'
    '\b(jamaa|sahrij|khirta|lemma|choufiya|hdidane)\b'
    'tawiza-agora'
    '_bmad-output'
    'agora-runs'
    'MiroFish'
    'OpenClaw'
    'ANTHROPIC_API_KEY'
    'OPENAI_API_KEY'
    'OPENROUTER_API_KEY'
    'sk-ant-'
    'xsmtpsib-'
    'xkeysib-'
)

EXCLUDE='(/assets/|/files/|node_modules/|\.git/|CLAUDE\.md|\.githooks/)'
FOUND=0

for pat in "${FORBIDDEN[@]}"; do
    matches=$(grep -rEn "$pat" . 2>/dev/null | grep -vE "$EXCLUDE" || true)
    if [[ -n "$matches" ]]; then
        echo "::error title=Pattern interdit détecté::Pattern '$pat' trouvé dans les fichiers"
        echo "$matches" | head -5
        FOUND=$((FOUND + 1))
    fi
done

# Fichiers inattendus dans le build public
UNEXPECTED=$(find . -type f \( \
    -name "CLAUDE.md" -o \
    -path "*_bmad-output*" -o \
    -name ".env" \
\) 2>/dev/null | grep -vE '\.git/' || true)
if [[ -n "$UNEXPECTED" ]]; then
    echo "::error title=Fichiers inattendus::$UNEXPECTED"
    FOUND=$((FOUND + 1))
fi

if [[ $FOUND -gt 0 ]]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$FOUND violations doctrine Tawiza détectées."
    echo "Voir docs/doctrine-tawiza.md (R2, R3, R12, R14, R31)."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 1
fi

echo "✓ Aucune violation doctrine détectée."
