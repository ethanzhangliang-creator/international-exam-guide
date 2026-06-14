from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SourceSnippet:
    page: int
    text: str
    matched_term: str


@dataclass
class Topic:
    title: str
    points: list[str] = field(default_factory=list)
    level_tags: list[str] = field(default_factory=list)
    source_snippets: list[SourceSnippet] = field(default_factory=list)


@dataclass
class AssessmentPaper:
    title: str
    details: list[str] = field(default_factory=list)
    source_snippets: list[SourceSnippet] = field(default_factory=list)


@dataclass
class SourceRecord:
    provider: str
    page_url: str
    specification_url: str | None = None
    listing_subject: str | None = None
    listing_qualification_type: str | None = None
    listing_group_label: str | None = None
    listing_style_class: str | None = None
    specification_sha256: str | None = None
    specification_path: str | None = None
    extracted_text_path: str | None = None
    downloaded_at: str | None = None


@dataclass
class Qualification:
    title: str
    code: str | None
    qualification_type: str
    subject_area: str | None
    page_url: str
    summary: list[str]
    topics: list[Topic]
    assessments: list[AssessmentPaper]
    source: SourceRecord
    audience_note: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Qualification":
        source = SourceRecord(**data["source"])
        topics = [
            Topic(
                title=topic["title"],
                points=topic.get("points", []),
                level_tags=topic.get("level_tags", []),
                source_snippets=[
                    SourceSnippet(**snippet) for snippet in topic.get("source_snippets", [])
                ],
            )
            for topic in data.get("topics", [])
        ]
        assessments = [
            AssessmentPaper(
                title=paper["title"],
                details=paper.get("details", []),
                source_snippets=[
                    SourceSnippet(**snippet) for snippet in paper.get("source_snippets", [])
                ],
            )
            for paper in data.get("assessments", [])
        ]
        return cls(
            title=data["title"],
            code=data.get("code"),
            qualification_type=data["qualification_type"],
            subject_area=data.get("subject_area"),
            page_url=data["page_url"],
            summary=data.get("summary", []),
            topics=topics,
            assessments=assessments,
            source=source,
            audience_note=data["audience_note"],
        )


@dataclass
class PracticeItem:
    topic_title: str
    command_word: str
    difficulty: str
    focus_point: str
    question: str
    answer_frame: list[str]
    public_solution_steps: list[str]
    answer_checkpoints: list[str]
    source_points: list[str]
    source_snippets: list[SourceSnippet] = field(default_factory=list)


@dataclass
class TopicGuide:
    topic_title: str
    essence: str
    analogy: str
    mini_worked_example: str
    worked_solution_steps: list[str]
    pitfall: str
    checklist: list[str]
    diagram_brief: str
    source_snippets: list[SourceSnippet] = field(default_factory=list)


@dataclass
class GuidePlan:
    qualification: Qualification
    topic_guides: list[TopicGuide]
    practice_items: list[PracticeItem]
    diagram_briefs: list[str]
    revision_stages: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
