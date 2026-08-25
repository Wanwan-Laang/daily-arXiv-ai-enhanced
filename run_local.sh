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
export RESEARCH_KEYWORDS="${RESEARCH_KEYWORDS:-high-entropy carbide, TiTaZrNb, carbon vacancy, vacancy ordering, FLiBe, molten salt, zirconium hydride, ZrH2, hydride moderator, hydrogen retention, nuclear fuel, fuel cladding, nuclear material, nuclear ceramic, nuclear energy materials, irradiation damage, radiation damage, displacement cascade, collision cascade, PKA, defect energetics, defect evolution, point defect, experiment, experimental, synthesis, characterization, phase stability, thermal conductivity, mechanical properties, neutron irradiation, ion irradiation, XRD, TEM, SEM, MLIP, interatomic potential, DeepMD, DFT, first-principles, AIMD, molecular dynamics, LAMMPS, ion diffusion, ionic transport, superionic transition}"

echo "Using local API: ${OPENAI_BASE_URL}"
echo "Categories: ${CATEGORIES}"
echo "Research keyword filter enabled."
echo "Chinese output mode: Traditional Chinese (繁體中文)."

bash run.sh
