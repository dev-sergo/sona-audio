#!/usr/bin/env bash
set -euo pipefail

VENV="$HOME/venvs/alf-audio"
PROJECT="$HOME/sona-audio"

echo "=== sona-audio GPU box setup ==="

# 1. venv
if [ ! -d "$VENV" ]; then
    echo "[1/4] Creating venv at $VENV ..."
    python3 -m venv "$VENV" --system-site-packages
else
    echo "[1/4] venv already exists, skipping."
fi

# 2. dependencies
echo "[2/4] Installing Python dependencies..."
source "$VENV/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet -r "$PROJECT/requirements.model_server.txt"

# 3. .env
if [ ! -f "$PROJECT/.env" ]; then
    echo "[3/4] Creating .env from example..."
    cp "$PROJECT/.env.example" "$PROJECT/.env"
    echo "      Edit $PROJECT/.env and set ACESTEP_MODEL_PATH if needed."
else
    echo "[3/4] .env already exists, skipping."
fi

# 4. smoke check
echo "[4/4] Checking CUDA..."
python3 -c "import torch; print('  CUDA available:', torch.cuda.is_available()); print('  Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'none')"

echo ""
echo "=== Setup complete ==="
echo "Start model server:"
echo "  source $VENV/bin/activate"
echo "  cd $PROJECT && python -m uvicorn model_server.main:app --host 0.0.0.0 --port 8001"
