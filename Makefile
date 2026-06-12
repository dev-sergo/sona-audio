.PHONY: test build up down clean logs

# ── tests (in Docker, so nothing is installed on the Mac) ────────────────────
# The Mac has system Python 3.9, but the code needs 3.10+ → run in a 3.11 container
test:
	docker run --rm -v "$(PWD)":/app -w /app python:3.11-slim \
		bash -c "pip install -q -r requirements.test.txt && python -m pytest tests/ -q"

# ── Docker (Mac) ─────────────────────────────────────────────────────────────
# (build / start / stop / logs / wipe)
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	docker compose down --rmi all
	rm -rf data/

# ── GPU box (run there over ssh) ─────────────────────────────────────────────
gpu-setup:
	bash setup_gpu.sh

gpu-start:
	bash -c "source ~/venvs/alf-audio/bin/activate && \
	python -m uvicorn model_server.main:app --host 0.0.0.0 --port 8001"
