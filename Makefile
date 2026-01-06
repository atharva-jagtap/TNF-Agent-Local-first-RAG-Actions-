up:
\tdocker compose up -d
down:
\tdocker compose down
pull-models:
\tcurl http://localhost:11434/api/pull -d '{"name":"llama3.1:8b"}'
\tcurl http://localhost:11434/api/pull -d '{"name":"nomic-embed-text"}'
ingest:
\tQDRANT_URL=http://localhost:6333 LLM_BASE=http://localhost:11434 \\
\t. .venv/bin/activate && pip install -r api/requirements.txt && python scripts/ingest.py
count:
\tcurl -s -X POST http://localhost:6333/collections/tnf_chunks/points/count \\
\t -H 'content-type: application/json' -d '{"exact": true}'
logs:
\tdocker compose logs -f --tail=200
