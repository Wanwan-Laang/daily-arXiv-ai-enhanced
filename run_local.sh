#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
    read -r -s -p "Enter your GCLI2API API password: " OPENAI_API_KEY
    echo
    export OPENAI_API_KEY
fi

export OPENAI_BASE_URL="${OPENAI_BASE_URL:-http://127.0.0.1:7861/v1}"
export LANGUAGE="${LANGUAGE:-Chinese}"
export CATEGORIES="${CATEGORIES:-cond-mat.mtrl-sci, cond-mat.stat-mech, physics.comp-ph, physics.chem-ph, nucl-ex, nucl-th}"
export MODEL_NAME="${MODEL_NAME:-gemini-2.5-flash}"
export RESEARCH_KEYWORDS="${RESEARCH_KEYWORDS:-high entropy ceramic carbide, high-entropy carbide, ceramic carbide, carbide coating, machine learning potential, machine-learned potential, neural network potential, interatomic potential, atomic cluster expansion, equivariant potential, irradiation damage, radiation damage, displacement damage, defect evolution, radiation defect, point defect, vacancy, irradiation, ion irradiation, neutron irradiation}"

echo "Using local API: ${OPENAI_BASE_URL}"
echo "Categories: ${CATEGORIES}"
echo "Research keyword filter enabled."

bash run.sh
