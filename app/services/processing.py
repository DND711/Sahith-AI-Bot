from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class TranscriptInsights:
    tldr: str
    discussion: str
    decisions: str
    risks: str
    action_items: List[str]
    suggestions: List[str]


class TranscriptProcessor:
    """Lightweight heuristic-based processor for demo purposes."""

    def __init__(self, speaker_prefix: str = "Speaker") -> None:
        self.speaker_prefix = speaker_prefix

    def segment_transcript(self, transcript_text: str) -> List[tuple[str | None, str]]:
        segments: List[tuple[str | None, str]] = []
        for raw_line in transcript_text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if ":" in line and line.startswith(self.speaker_prefix):
                speaker, content = line.split(":", 1)
                segments.append((speaker.strip(), content.strip()))
            else:
                segments.append((None, line))
        return segments

    def build_insights(self, transcript_text: str) -> TranscriptInsights:
        sentences = [s.strip() for s in transcript_text.replace("\n", " ").split(".") if s.strip()]
        tldr = ". ".join(sentences[:2]) + ("." if sentences[:2] else "")
        discussion = "\n".join(sentences[:5])
        decisions = "\n".join(
            sentence for sentence in sentences if any(k in sentence.lower() for k in ["decided", "agree", "approved"])
        ) or "No explicit decisions captured."
        risks = "\n".join(
            sentence for sentence in sentences if any(k in sentence.lower() for k in ["risk", "concern", "blocked"])
        ) or "No major risks detected."

        action_candidates = [
            sentence for sentence in sentences if any(k in sentence.lower() for k in ["will", "needs to", "follow up", "action"])
        ]
        action_items = [
            action.capitalize() if not action.endswith(".") else action for action in action_candidates[:5]
        ] or ["No action items detected — consider adding manual notes."]

        suggestions = self._suggest_questions(sentences)

        return TranscriptInsights(
            tldr=tldr or "Unable to build summary from empty transcript.",
            discussion=discussion or "Transcript was too short for detailed notes.",
            decisions=decisions,
            risks=risks,
            action_items=action_items,
            suggestions=suggestions,
        )

    @staticmethod
    def _suggest_questions(sentences: List[str]) -> List[str]:
        suggestions: List[str] = []
        joined = " ".join(sentences).lower()
        if "timeline" in joined:
            suggestions.append("Ask the team to confirm the testing timeline and any buffer.")
        if "budget" in joined or "cost" in joined:
            suggestions.append("Clarify whether the discussed budget includes contingency.")
        if "client" in joined:
            suggestions.append("Follow up with the client on expectations and next steps.")
        if not suggestions:
            suggestions.append("Share a recap email summarizing decisions and next steps.")
        return suggestions[:5]
