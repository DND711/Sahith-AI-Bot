# Sahith AI Bot

This repository now contains a working "shadow mode" slice of Sahith's meeting copilot. It lets you:

1. Create meetings through a REST API or the included web console.
2. Paste/upload transcripts (plain text for now) to simulate audio ingestion.
3. Automatically generate TL;DR summaries, detailed notes, action items, and proactive suggestions.
4. View the insights in the dashboard or retrieve them with API calls.

Once this foundation is proven, you can extend it with real STT/LLM providers, live meeting capture, and active agent behaviors as captured in the roadmap below.

---

## 1. Running the app locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

* API base URL: `http://localhost:8000`
* Web console: `http://localhost:8000/app`
* Interactive API docs (Swagger UI): `http://localhost:8000/docs`

> **Note:** The `/meetings/{id}/audio` endpoint currently expects a UTF-8 text file so you can exercise the full flow without speech-to-text credentials. Swap the placeholder with Azure Speech/OpenAI Whisper once you are ready for true audio ingestion.

### 1.1 Containerized deployment

Run the same container image locally that you will deploy to the cloud:

```bash
docker compose up --build -d
```

The FastAPI server will be reachable on `http://localhost:8000` and persists SQLite data inside the `data` named volume so meeting history survives restarts. Inspect logs with `docker compose logs -f`. See [DEPLOYMENT.md](DEPLOYMENT.md) for pushing the image to Azure Container Registry and deploying it to Azure Container Apps.

---

## 2. Project structure

```
app/
  main.py                # FastAPI application & routes
  database.py            # SQLite wiring (swap for Postgres/Cosmos in production)
  models.py              # SQLAlchemy models: Meeting, TranscriptSegment, Summary...
  schemas.py             # Pydantic schemas for validation/serialization
  services/processing.py # Lightweight transcript summarizer + heuristics
frontend/
  index.html             # Minimal dashboard for uploading transcripts and reading insights
requirements.txt         # API dependencies
README.md                # You are here
```

The transcript processor currently uses deterministic heuristics (keyword search + sentence chunking) so the repo stays runnable offline. You can replace `TranscriptProcessor` with integrations that call Azure OpenAI or GPT as soon as you provision credentials.

---

## 3. API reference

| Endpoint | Method | Description |
| --- | --- | --- |
| `/health` | GET | Liveness probe. |
| `/meetings` | POST | Create a meeting with title/description/scheduled start. |
| `/meetings` | GET | List meetings ordered by creation time. |
| `/meetings/{id}` | GET | Meeting plus transcript segments, summary, actions, suggestions. |
| `/meetings/{id}/transcript` | POST | Accepts `{ "transcript_text": "..." }` and triggers processing. |
| `/meetings/{id}/audio` | POST | Upload a text file (placeholder for STT pipeline). |
| `/meetings/{id}/summary` | GET | Fetch the computed insights for a meeting. |

All responses follow the schemas in `app/schemas.py`, making it easy to add type-safe SDKs later.

---

## 4. Web console

The dashboard served at `/app` offers three panes:

1. **Create Meeting** – capture metadata.
2. **Upload Transcript** – paste meeting text and run the processor.
3. **Summary** – read TL;DR, discussion, decisions, risks, action items, and suggestions.

Because the UI calls the same REST endpoints, any improvements you make to the backend (e.g., richer prompts, real-time updates) appear here automatically.

---

## 5. Execution roadmap (from planning doc)

### 0. v1 scope (frozen requirements)
- Bot stays silent during live meetings.
- Support a single meeting platform first (Teams or Zoom).
- Auto-join calendar meetings as a separate participant.
- Transcribe, summarize, and extract action items for every attended meeting.
- Send Sahith proactive suggestions/questions via DM during or after the meeting.

### 1. High-level architecture decisions
- **Cloud**: Azure.
- **Backend**: .NET, Node.js, or Python (current repo uses FastAPI/Python for speed).
- **Database**: PostgreSQL or Cosmos DB to persist users, meetings, transcripts, and actions.
- **Queue**: Azure Service Bus for async audio processing.
- **AI stack**:
  - Speech-to-text: Azure Speech or OpenAI Whisper.
  - LLM: Azure OpenAI / GPT for summaries, action extraction, and suggestion generation.

### 2. Phase 1 – Shadow mode (upload-driven)
Goal: use the "brain" immediately with uploaded recordings.

1. **Backend skeleton** – authentication, meeting CRUD, transcript ingestion, summary endpoint.
2. **Transcription pipeline** – audio upload triggers ASR, stores timestamped transcripts.
3. **LLM meeting brain** – TL;DR, detailed notes, action items, 3–5 tailored suggestions.
4. **Simple UI** – dashboard for uploads + insights (implemented in this repo).

Outcome: "Upload any meeting → Bot tells me what happened and what I should do next."

### 3. Phase 2 – Auto-join on one platform (MVP agent)
1. **Calendar + meeting discovery** – Microsoft Graph/Google Calendar + per-meeting flags.
2. **Meeting join service** – Teams bot/Zoom app joins as "Sahith's AI Assistant" and records audio.
3. **Live transcription & suggestions** – chunk transcripts every 30–60 seconds and DM Sahith with contextual advice.

Bot remains silent in the meeting; it is a ghost advisor.

### 4. Phase 3 – Active agent (bot speaks/types)
1. **Behavior policies** – codify guardrails (clarifications vs. commitments, privacy, tone).
2. **Turn-taking loop** – evaluate triggers, decide whether to intervene, send short interventions via chat or TTS.

Start with clarifying questions only and cap interventions (e.g., max two per meeting).

### 5. Phase 4 – Multilingual + visual recaps
- Detect meeting language and output summaries in English plus a preferred language (e.g., Telugu).
- Generate visual recaps (flowcharts, milestone timelines) exportable as images/PDF/slide decks.

### 6. Non-technical tracks
1. **Legal & compliance** – consent messaging, configurable retention (30/60/90 days).
2. **Metrics & feedback** – track summary views, suggestion usage, bot speaking frequency, thumbs-up/down feedback per suggestion.

### 7. Weekly kickoff checklist
- **Week 1–2**: repo setup, backend skeleton, DB, audio upload → transcript → summary/actions, basic UI (completed here).
- **Week 3–4**: calendar integration, manual bot join/recording for one platform, persist raw audio + transcripts.
- **Week 5–6**: live transcript chunking, live suggestion DMs, system prompts for "what should I ask/suggest?"

Future iterations expand into active speaking and multi-platform coverage once v1 proves reliable.
