# Sahith AI Bot Execution Plan

This document captures the concrete roadmap for delivering the v1 assistant and the subsequent maturity phases.

## 0. v1 Scope (frozen requirements)
- Bot stays silent during live meetings.
- Support a single meeting platform first (Teams or Zoom).
- Auto-join calendar meetings as a separate participant.
- Transcribe, summarize, and extract action items for every attended meeting.
- Send Sahith proactive suggestions/questions via DM during or after the meeting.

## 1. High-Level Architecture Decisions
- **Cloud**: Azure.
- **Backend**: .NET, Node.js, or Python (pick the stack that ships fastest).
- **Database**: PostgreSQL or Cosmos DB to persist users, meetings, transcripts, and actions.
- **Queue**: Azure Service Bus for async audio processing.
- **AI stack**:
  - Speech-to-text: Azure Speech or OpenAI Whisper.
  - LLM: OpenAI GPT or Azure OpenAI for summaries, action extraction, and suggestion generation.

## 2. Phase 1 – Shadow Mode (upload-driven)
Goal: use the "brain" immediately with uploaded recordings.

1. **Backend skeleton**
   - Implement authentication (JWT/Identity).
   - Endpoints:
     - `POST /meetings` to register metadata.
     - `POST /meetings/{id}/audio` to upload audio.
     - `GET /meetings/{id}/summary` to fetch insights.
2. **Transcription pipeline**
   - Trigger ASR on audio upload and store timestamped transcripts.
3. **LLM meeting brain**
   - Prompt templates for TL;DR, detailed notes (context/discussion/decisions/risks), action items (owner/due date/description), and 3–5 tailored suggestions for Sahith.
4. **Simple UI**
   - Dashboard to upload recordings, view transcripts, summaries, actions, and suggestions.

Outcome: "Upload any meeting → Bot tells me what happened and what I should do next."

## 3. Phase 2 – Auto-Join on One Platform (MVP agent)
1. **Calendar + meeting discovery**
   - Integrate with Microsoft Graph or Google Calendar.
   - Retrieve events, join links, titles, participants, plus per-meeting flags: `auto_join`, `mode` (shadow/suggest_only/active future).
2. **Meeting join service**
   - Build a Teams bot or Zoom app that joins as "Sahith's AI Assistant" and records audio.
   - Background worker monitors calendar; for `auto_join` meetings it spins up join sessions.
3. **Live transcription & suggestions**
   - Stream audio to ASR with low latency.
   - Chunk transcript every 30–60 seconds.
   - For each chunk, the LLM identifies action items/confusions and DMs Sahith (Teams DM, WhatsApp, Telegram, or web notifications) with contextual advice.

Bot remains silent in the meeting; it is a ghost advisor.

## 4. Phase 3 – Active Agent (bot speaks/types)
1. **Behavior policies**
   - Codify allowed vs. forbidden behaviors (clarifications, reminders vs. commitments, aggression, private info).
   - Embed policies into system prompts and guardrails.
2. **Turn-taking loop**
   - Read recent transcript window (2–3 minutes).
   - Evaluate triggers (open questions, ownerless decisions, risky timelines).
   - LLM decides whether to intervene and generates one short message.
   - Deliver via meeting chat or TTS audio.
   - Start with clarifying questions only and cap interventions (e.g., max two per meeting).

## 5. Phase 4 – Multilingual + Visual Recaps
- Detect meeting language and output summaries in English plus a preferred language (e.g., Telugu).
- Generate visual recaps (flowcharts, milestone timelines) exportable as images, PDFs, or slide decks.

## 6. Non-Technical Tracks
1. **Legal & compliance**
   - Consent messaging for participants.
   - Data retention policy (configurable 30/60/90 days).
2. **Metrics & feedback**
   - Track summary views, suggestion usage, bot speaking frequency, and thumbs-up/down feedback per suggestion.
   - Use signals to refine prompts and policies.

## 7. Weekly Kickoff Checklist
- **Week 1–2**: repo setup, backend skeleton, DB, audio upload → transcript → summary/actions, basic UI.
- **Week 3–4**: calendar integration, manual bot join/recording for one platform, persist raw audio + transcripts.
- **Week 5–6**: live transcript chunking, live suggestion DMs, system prompts for "what should I ask/suggest?"

Future iterations will expand into active speaking and multi-platform coverage once v1 proves reliable.
