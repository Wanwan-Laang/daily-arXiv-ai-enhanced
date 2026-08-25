#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [[ -f "$ROOT_DIR/.venv/bin/activate" ]]; then
    source "$ROOT_DIR/.venv/bin/activate"
else
    echo "Missing .venv. Run: uv sync" >&2
    exit 1
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
    read -r -s -p "Enter your GCLI2API API password: " OPENAI_API_KEY
    echo
    export OPENAI_API_KEY
fi

export OPENAI_BASE_URL="${OPENAI_BASE_URL:-http://127.0.0.1:7861/antigravity/v1}"
export LANGUAGE="${LANGUAGE:-Chinese}"
export CATEGORIES="${CATEGORIES:-cond-mat.mtrl-sci, cond-mat.stat-mech, physics.comp-ph, physics.chem-ph, nucl-ex, nucl-th}"
export MODEL_NAME="${MODEL_NAME:-gemini-2.5-flash}"
export RESEARCH_STRICT_PROFILE="${RESEARCH_STRICT_PROFILE:-1}"
export RESEARCH_KEYWORDS="${RESEARCH_KEYWORDS:-high-entropy carbide, high entropy carbide, refractory high-entropy carbide, ceramic carbide, transition-metal carbide, TiTaZrNb, carbon vacancy, vacancy ordering, vacancy formation energy, defect energetics, machine-learning interatomic potential, machine learned interatomic potential, MLIP, interatomic potential, DeepMD, DeePMD-kit, neural network interatomic potential, equivariant interatomic potential, graph neural network potential, active learning interatomic potential, irradiation damage, radiation damage, displacement cascade, collision cascade, primary knock-on atom, PKA, defect evolution, FLiBe, molten salt, zirconium hydride, ZrH2, hydride moderator, hydrogen retention, nuclear fuel, high-temperature ionic transport, superionic transition, ion diffusion in solid}"

echo "Using local API: ${OPENAI_BASE_URL}"
echo "Categories: ${CATEGORIES}"
echo "Research keyword filter enabled."

bash run.sh
