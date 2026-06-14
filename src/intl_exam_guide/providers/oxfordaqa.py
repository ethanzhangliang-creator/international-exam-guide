from __future__ import annotations

import hashlib
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path

from intl_exam_guide.models import AssessmentPaper, Qualification, SourceRecord, SourceSnippet, Topic
from intl_exam_guide.parsing.pdf_text import extract_pdf_pages, extract_pdf_text

BASE_URL = "https://www.oxfordaqa.com"
SUBJECTS_URL = f"{BASE_URL}/subjects/"
USER_AGENT = "international-exam-guide/0.1 (+https://github.com/) source-traceable"


@dataclass
class Link:
    text: str
    href: str
    qualification_type: str | None = None
    subject_heading: str | None = None
    group_label: str | None = None
    style_class: str | None = None


@dataclass
class TextNode:
    tag: str
    text: str


class PageParser(HTMLParser):
    """Small standard-library parser for OxfordAQA's mostly static pages."""

    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.stack: list[str] = []
        self.nodes: list[TextNode] = []
        self.links: list[Link] = []
        self._link_href: str | None = None
        self._link_class: str | None = None
        self._link_parts: list[str] = []
        self._heading_parts: list[str] | None = None
        self._recent_h3: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.stack.append(tag)
        attr_map = dict(attrs)
        if tag == "h3":
            self._heading_parts = []
        if tag == "a":
            href = attr_map.get("href")
            if href:
                self._link_href = urllib.parse.urljoin(self.base_url, href)
                self._link_class = attr_map.get("class")
                self._link_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._link_href:
            text = clean_text(" ".join(self._link_parts))
            if text:
                self.links.append(
                    Link(
                        text=text,
                        href=self._link_href,
                        qualification_type=qualification_type_from_listing(text, self._link_class),
                        subject_heading=self._recent_h3,
                        group_label=listing_group_label(text, self._link_class),
                        style_class=self._link_class,
                    )
                )
            self._link_href = None
            self._link_class = None
            self._link_parts = []
        if tag == "h3" and self._heading_parts is not None:
            heading = clean_text(" ".join(self._heading_parts))
            if heading:
                self._recent_h3 = heading
            self._heading_parts = None
        if self.stack:
            self.stack.pop()

    def handle_data(self, data: str) -> None:
        text = clean_text(data)
        if not text:
            return
        tag = self.stack[-1] if self.stack else ""
        self.nodes.append(TextNode(tag=tag, text=text))
        if self._link_href:
            self._link_parts.append(text)
        if self._heading_parts is not None:
            self._heading_parts.append(text)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_text(url: str, timeout: int = 30) -> str:
    data = fetch_bytes(url, timeout=timeout)
    return data.decode("utf-8", errors="replace")


def parse_page(url: str) -> PageParser:
    parser = PageParser(base_url=url)
    parser.feed(fetch_text(url))
    return parser


def code_from_title(title: str) -> str | None:
    match = re.search(r"\((\d{4})\)", title)
    return match.group(1) if match else None


def qualification_type_from_title(title: str) -> str:
    lower = title.lower()
    if "international gcse" in lower:
        return "international_gcse"
    if "international as" in lower or "a-level" in lower:
        return "international_as_a_level"
    if "international extended project qualification" in lower:
        return "international_as_a_level"
    return "unknown"


def qualification_type_from_listing(text: str, style_class: str | None = None) -> str | None:
    if style_class:
        if "btn--type-8" in style_class:
            return "international_gcse"
        if "btn--type-7" in style_class:
            return "international_as_a_level"
    qtype = qualification_type_from_title(text)
    return None if qtype == "unknown" else qtype


def listing_group_label(text: str, style_class: str | None = None) -> str | None:
    qtype = qualification_type_from_listing(text, style_class)
    if qtype == "international_gcse":
        return "blue International GCSE subject listing"
    if qtype == "international_as_a_level":
        return "red International AS/A-level subject listing"
    return None


def filter_candidates_by_level(candidates: list[Link], level_norm: str | None) -> list[Link]:
    if not level_norm:
        return candidates
    if level_norm in {"gcse", "igcse", "international-gcse"}:
        filtered = [
            candidate
            for candidate in candidates
            if candidate.qualification_type == "international_gcse"
            or "international gcse" in candidate.text.lower()
        ]
        return filtered or candidates
    if level_norm in {"alevel", "a-level", "as-a-level", "international-as-a-level"}:
        filtered = [
            candidate
            for candidate in candidates
            if candidate.qualification_type == "international_as_a_level"
            or "international as" in candidate.text.lower()
            or "a-level" in candidate.text.lower()
        ]
        return filtered or candidates
    return candidates


class OxfordAQAProvider:
    name = "oxfordaqa"

    def discover_subject_pages(self) -> list[Link]:
        parser = parse_page(SUBJECTS_URL)
        subjects: dict[str, Link] = {}
        for link in parser.links:
            parsed = urllib.parse.urlparse(link.href)
            if not parsed.path.startswith("/subjects/"):
                continue
            slug = parsed.path.strip("/").split("/")[-1]
            if not slug or slug == "subjects":
                continue
            if link.text.lower() in {"all subjects", "subjects"}:
                continue
            current = subjects.get(slug)
            if current is None or len(link.text) < len(current.text):
                subjects[slug] = link
        return sorted(subjects.values(), key=lambda item: item.text)

    def list_qualifications(self, subject_url: str) -> list[Link]:
        parser = parse_page(subject_url)
        seen: dict[str, Link] = {}
        for link in parser.links:
            path = urllib.parse.urlparse(link.href).path
            if "/qualifications/" not in path:
                continue
            if link.qualification_type not in {"international_gcse", "international_as_a_level"}:
                continue
            seen[link.href] = link
        return list(seen.values())

    def find_qualification(self, query: str, level: str | None = None) -> Link:
        if query.startswith("http://") or query.startswith("https://"):
            return Link(
                text=query.rstrip("/").split("/")[-1],
                href=query,
                qualification_type=qualification_type_from_title(query),
            )

        query_norm = query.lower().strip()
        candidates: list[Link] = []
        for subject in self.discover_subject_pages():
            if query_norm not in subject.text.lower() and query_norm not in subject.href.lower():
                if not re.fullmatch(r"\d{4}", query_norm):
                    continue
            candidates.extend(self.list_qualifications(subject.href))

        if not candidates:
            for subject in self.discover_subject_pages():
                candidates.extend(self.list_qualifications(subject.href))

        is_code_query = re.fullmatch(r"\d{4}", query_norm) is not None
        if is_code_query:
            exact = self.find_by_qualification_code(candidates, query_norm, level)
            if exact:
                return exact
            raise ValueError(f"No OxfordAQA qualification found for code: {query!r}")

        scored: list[tuple[int, Link]] = []
        for candidate in candidates:
            text = candidate.text.lower()
            href = candidate.href.lower()
            score = 0
            if query_norm in text or query_norm in href:
                score += 20
            if re.fullmatch(r"\d{4}", query_norm) and f"({query_norm})" in text:
                score += 50
            if level:
                level_norm = level.lower().replace("_", "-")
                if level_norm in {"gcse", "igcse", "international-gcse"} and "international gcse" in text:
                    score += 30
                if level_norm in {"alevel", "a-level", "as-a-level", "international-as-a-level"}:
                    if "international as" in text or "a-level" in text:
                        score += 30
            if score:
                scored.append((score, candidate))

        if not scored:
            raise ValueError(f"No OxfordAQA qualification found for query: {query!r}")

        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[0][1]

    def find_by_qualification_code(
        self,
        candidates: list[Link],
        code: str,
        level: str | None = None,
    ) -> Link | None:
        level_norm = level.lower().replace("_", "-") if level else None
        preferred = filter_candidates_by_level(candidates, level_norm)
        fallback = candidates if preferred != candidates else []
        for group in (preferred, fallback):
            for candidate in group:
                text = candidate.text.lower()
                href = candidate.href.lower()
                if f"({code})" in text or code in href:
                    return candidate
            for candidate in group:
                try:
                    qualification = self.parse_qualification(candidate.href)
                except Exception:
                    continue
                if qualification.code == code:
                    return Link(
                        text=qualification.title,
                        href=candidate.href,
                        qualification_type=candidate.qualification_type,
                        subject_heading=candidate.subject_heading,
                        group_label=candidate.group_label,
                        style_class=candidate.style_class,
                    )
        return None

    def parse_qualification(self, page_url: str) -> Qualification:
        parser = parse_page(page_url)
        title = first_node_text(parser.nodes, "h1") or title_from_links(parser.links, page_url)
        code = code_from_title(title)
        qtype = qualification_type_from_title(title)
        subject_area = breadcrumb_subject(parser.nodes)
        summary = section_text(parser.nodes, start_text=title, end_text="Syllabus summary", max_items=8)
        topics = extract_topics(parser.nodes)
        assessments = extract_assessments(parser.nodes)
        specification_url = find_specification_url(parser.links)
        source = SourceRecord(
            provider=self.name,
            page_url=page_url,
            specification_url=specification_url,
        )
        return Qualification(
            title=title,
            code=code,
            qualification_type=qtype,
            subject_area=subject_area,
            page_url=page_url,
            summary=summary,
            topics=topics,
            assessments=assessments,
            source=source,
            audience_note=audience_note(qtype),
        )

    def apply_listing_metadata(self, qualification: Qualification, link: Link) -> Qualification:
        if qualification.qualification_type == "unknown" and link.qualification_type:
            qualification.qualification_type = link.qualification_type
            qualification.audience_note = audience_note(link.qualification_type)
        if link.subject_heading:
            qualification.source.listing_subject = link.subject_heading
        if link.qualification_type:
            qualification.source.listing_qualification_type = link.qualification_type
        if link.group_label:
            qualification.source.listing_group_label = link.group_label
        if link.style_class:
            qualification.source.listing_style_class = link.style_class
        return qualification

    def download_specification(self, qualification: Qualification, output_dir: Path) -> Qualification:
        if not qualification.source.specification_url:
            raise ValueError("No specification PDF URL found on qualification page.")

        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_bytes = fetch_bytes(qualification.source.specification_url)
        digest = hashlib.sha256(pdf_bytes).hexdigest()
        code = qualification.code or "unknown"
        pdf_path = output_dir / f"oxfordaqa-{code}-specification.pdf"
        text_path = output_dir / f"oxfordaqa-{code}-specification.txt"
        pdf_path.write_bytes(pdf_bytes)
        pages = extract_pdf_pages(pdf_path)
        text_path.write_text(extract_pdf_text(pdf_path), encoding="utf-8")
        attach_source_snippets(qualification, pages)

        qualification.source.specification_sha256 = digest
        qualification.source.specification_path = str(pdf_path)
        qualification.source.extracted_text_path = str(text_path)
        qualification.source.downloaded_at = datetime.now(UTC).isoformat()
        return qualification


def first_node_text(nodes: list[TextNode], tag: str) -> str | None:
    for node in nodes:
        if node.tag == tag:
            return node.text
    return None


def title_from_links(links: list[Link], page_url: str) -> str:
    for link in links:
        if link.href.rstrip("/") == page_url.rstrip("/"):
            return link.text
    return page_url.rstrip("/").split("/")[-1].replace("-", " ").title()


def breadcrumb_subject(nodes: list[TextNode]) -> str | None:
    h1_seen = False
    recent: list[str] = []
    for node in nodes:
        if node.tag == "h1":
            h1_seen = True
            break
        recent.append(node.text)
    if not h1_seen:
        return None
    for text in reversed(recent):
        if text not in {"Home", "Subjects"} and not text.startswith("International"):
            return text
    return None


def section_text(
    nodes: list[TextNode],
    start_text: str,
    end_text: str,
    max_items: int | None = None,
) -> list[str]:
    started = False
    values: list[str] = []
    for node in nodes:
        if node.text == start_text:
            started = True
            continue
        if not started:
            continue
        if node.text == end_text:
            break
        if node.tag in {"p", "li"} and len(node.text) > 20:
            values.append(node.text)
        if max_items and len(values) >= max_items:
            break
    return dedupe(values)


def extract_topics(nodes: list[TextNode]) -> list[Topic]:
    region = nodes_between_any(
        nodes,
        ["Syllabus summary"],
        ["Teaching resources available", "Teaching resources", "Assessment"],
    )
    covers_index = index_containing(region, "covers the following topics")
    if covers_index is not None:
        region = region[covers_index + 1 :]

    topics = topics_from_region(region)
    if not topics:
        topics = topics_from_named_skill_section(nodes)
    if not topics:
        topics = topics_from_assessment(nodes)
    return clean_topics(topics)


def topics_from_region(region: list[TextNode], default_title: str | None = None) -> list[Topic]:
    topics: list[Topic] = []
    current: Topic | None = None
    has_headings = any(is_topic_heading(node) for node in region)

    for node in region:
        if has_headings and is_topic_heading(node):
            if current:
                topics.append(current)
            current = Topic(title=node.text)
            continue
        point = topic_point_text(node)
        if point:
            if has_headings:
                if current:
                    current.points.append(point)
            else:
                if default_title:
                    if current is None:
                        current = Topic(title=default_title)
                    current.points.append(point)
                else:
                    topics.append(Topic(title=point))
    if current:
        topics.append(current)

    return clean_topics(topics)


def topics_from_named_skill_section(nodes: list[TextNode]) -> list[Topic]:
    section_specs = [
        ("Taught skills", "Taught skills"),
        ("The International EPQ project process", "The International EPQ project process"),
        ("International GCSE Plus process", "International GCSE Plus process"),
    ]
    for start, title in section_specs:
        region = nodes_between_any(
            nodes,
            [start],
            ["Teaching resources available", "Teaching resources", "Assessment", "Recognition"],
        )
        topics = topics_from_region(region, default_title=title)
        if topics:
            return topics
    return []


def topics_from_assessment(nodes: list[TextNode]) -> list[Topic]:
    topics: list[Topic] = []
    for paper in extract_assessments(nodes):
        points = [
            strip_bullet(detail)
            for detail in paper.details
            if strip_bullet(detail) and not is_assessment_logistics(detail)
        ]
        if points:
            topics.append(Topic(title=paper.title, points=dedupe(points)))
    return clean_topics(topics)


def clean_topics(topics: list[Topic]) -> list[Topic]:
    cleaned: list[Topic] = []
    for topic in topics:
        title = strip_bullet(topic.title)
        if not is_valid_topic_title(title):
            continue
        points = [point for point in (strip_bullet(point) for point in topic.points) if is_valid_topic_point(point)]
        cleaned.append(Topic(title=title, points=dedupe(points), level_tags=topic.level_tags, source_snippets=topic.source_snippets))
    return cleaned


def is_topic_heading(node: TextNode) -> bool:
    if not is_valid_topic_title(node.text):
        return False
    if node.tag in {"h3", "h4", "h5", "h6", "strong"}:
        return True
    if node.tag == "span":
        text = node.text.strip()
        return text.endswith(":") or text.lower() in {"as", "as:", "a-level only", "a-level only:"}
    return False


def topic_point_text(node: TextNode) -> str | None:
    if node.tag not in {"li", "p", "span"}:
        return None
    text = strip_bullet(node.text)
    if is_valid_topic_point(text):
        return text
    return None


def strip_bullet(text: str) -> str:
    return text.strip().lstrip("•*-").strip().rstrip(":").strip()


def is_valid_topic_title(text: str) -> bool:
    lower = text.lower().strip()
    if len(text.strip()) < 3 and lower != "as":
        return False
    ignored_prefixes = (
        "assessment objectives",
        "candidate record forms",
        "download",
        "for current cohorts",
        "new:",
        "please note",
        "please see",
        "revised for",
        "view ",
    )
    if lower.startswith(ignored_prefixes):
        return False
    if lower in {".", "and", "or"}:
        return False
    return True


def is_valid_topic_point(text: str) -> bool:
    if len(text.strip()) < 3:
        return False
    lower = text.lower().strip()
    ignored_prefixes = (
        "download ",
        "find out more",
        "please see",
        "published by",
        "request ",
        "view ",
    )
    if lower.startswith(ignored_prefixes):
        return False
    if lower in {".", "(pdf)", "(word)"}:
        return False
    return True


def extract_assessments(nodes: list[TextNode]) -> list[AssessmentPaper]:
    region = nodes_between_any(nodes, ["Assessment"], ["Thinking about switching", "Course specification"])
    if not region:
        region = nodes_between(nodes, "Assessment", "Course specification")

    papers: list[AssessmentPaper] = []
    current: AssessmentPaper | None = None
    paper_re = re.compile(r"^(Core|Extension|AS|A-level|Paper|Unit|[A-Z].* Paper).*:?$")
    detail_re = re.compile(r"(marks|hour|%|exam|assessed|calculator|written|on-screen|qualification)", re.I)

    for node in region:
        text = node.text.rstrip(":")
        if is_assessment_heading(node, paper_re):
            if current:
                papers.append(current)
            current = AssessmentPaper(title=text)
            continue
        if current is None and node.tag in {"li", "p"} and is_valid_assessment_detail(node.text):
            current = AssessmentPaper(title="Assessment evidence and objectives")
        if current and (node.tag in {"li", "p", "span"} or detail_re.search(node.text)):
            if is_valid_assessment_detail(node.text):
                current.details.append(node.text)
    if current:
        papers.append(current)

    return papers


def is_assessment_heading(node: TextNode, paper_re: re.Pattern[str]) -> bool:
    text = node.text.strip().rstrip(":")
    if not is_valid_topic_title(text):
        return False
    if paper_re.search(text) and ("Paper" in text or "Unit" in text):
        return True
    lower = text.lower()
    project_headings = {
        "individual project",
        "group sustainability action project",
        "non-exam assessment (nea)",
    }
    return node.tag in {"strong", "h5", "h6"} and lower in project_headings


def is_valid_assessment_detail(text: str) -> bool:
    lower = strip_bullet(text).lower()
    if not lower:
        return False
    ignored_prefixes = (
        "candidate record forms",
        "download ",
        "find out more",
        "please note",
        "supporting assessment resources",
        "view ",
    )
    return not lower.startswith(ignored_prefixes)


def is_assessment_logistics(text: str) -> bool:
    lower = strip_bullet(text).lower()
    logistics_patterns = [
        r"^\d+\s*(marks?|%)",
        r"^\d+%\s+of",
        r"^\d+\s+hour",
        r"^first (as |a-level |gcse )?(exam|assessment)",
        r"^written exam",
        r"^closed-book exam",
        r"^open-book exam",
        r"^on-screen exam",
        r"^calculator",
        r"^non-calculator",
        r"^students answer",
        r"^assessed by",
        r"^the supervisor",
        r"^schools must",
    ]
    return any(re.search(pattern, lower) for pattern in logistics_patterns)


def nodes_between(nodes: list[TextNode], start: str, end: str) -> list[TextNode]:
    return nodes_between_any(nodes, [start], [end])


def nodes_between_any(nodes: list[TextNode], starts: list[str], ends: list[str]) -> list[TextNode]:
    start_index = index_matching(nodes, starts)
    if start_index is None:
        return []
    result: list[TextNode] = []
    for node in nodes[start_index + 1 :]:
        if matches_any(node.text, ends):
            break
        result.append(node)
    return result


def index_equal(nodes: list[TextNode], value: str) -> int | None:
    return index_matching(nodes, [value])


def index_matching(nodes: list[TextNode], values: list[str]) -> int | None:
    for index, node in enumerate(nodes):
        if matches_any(node.text, values):
            return index
    return None


def matches_any(text: str, values: list[str]) -> bool:
    key = normalized_heading(text)
    for value in values:
        expected = normalized_heading(value)
        if key == expected or key.startswith(f"{expected} "):
            return True
    return False


def normalized_heading(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().rstrip(":")).lower()


def index_containing(nodes: list[TextNode], value: str) -> int | None:
    value = value.lower()
    for index, node in enumerate(nodes):
        if value in node.text.lower():
            return index
    return None


def find_specification_url(links: list[Link]) -> str | None:
    pdf_links = [link for link in links if ".pdf" in link.href.lower()]
    for link in pdf_links:
        combined = f"{link.text} {link.href}".lower()
        if "specification" in combined:
            return link.href
    for link in pdf_links:
        if "download here" in link.text.lower():
            return link.href
    return pdf_links[0].href if pdf_links else None


def audience_note(qualification_type: str) -> str:
    if qualification_type == "international_gcse":
        return (
            "OxfordAQA International GCSEs are designed for international students and "
            "schools following a British curriculum outside the UK. They are linear "
            "qualifications, so students normally take all exams in the same exam series "
            "at the end of the course. Availability can vary by region, school, and exam "
            "centre, so families should confirm local entry routes before relying on a study plan."
        )
    if qualification_type == "international_as_a_level":
        return (
            "OxfordAQA International AS/A-levels are modular international qualifications "
            "for international students in schools following a British curriculum outside the UK. "
            "Unit availability and entry routes should be confirmed locally."
        )
    return (
        "This is an OxfordAQA international qualification. Confirm the qualification type, "
        "local availability, and exam entry route with the school or centre."
    )


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def attach_source_snippets(qualification: Qualification, pages: list[tuple[int, str]]) -> None:
    for topic in qualification.topics:
        terms = [topic.title, *topic.points[:6]]
        topic.source_snippets = find_source_snippets(pages, terms, max_snippets=3)
    for paper in qualification.assessments:
        terms = [paper.title, *paper.details[:4]]
        paper.source_snippets = find_source_snippets(pages, terms, max_snippets=2)


def find_source_snippets(
    pages: list[tuple[int, str]],
    terms: list[str],
    max_snippets: int = 3,
) -> list[SourceSnippet]:
    snippets: list[SourceSnippet] = []
    used_pages: set[int] = set()
    for raw_term in terms:
        term = raw_term.strip()
        if len(term) < 4:
            continue
        term_norm = normalize_for_search(term)
        for page_number, page_text in pages:
            if page_number in used_pages:
                continue
            page_norm = normalize_for_search(page_text)
            if term_norm not in page_norm:
                continue
            snippets.append(
                SourceSnippet(
                    page=page_number,
                    text=snippet_around(page_text, term),
                    matched_term=term,
                )
            )
            used_pages.add(page_number)
            break
        if len(snippets) >= max_snippets:
            break
    return snippets


def normalize_for_search(value: str) -> str:
    value = value.replace("\u2013", "-").replace("\u2014", "-")
    value = re.sub(r"\s+", " ", value)
    return value.lower().strip()


def snippet_around(page_text: str, term: str, radius: int = 420) -> str:
    text = clean_text(page_text)
    text_lower = text.lower()
    term_lower = clean_text(term).lower()
    index = text_lower.find(term_lower)
    if index < 0:
        return text[: radius * 2].strip()
    start = max(0, index - radius)
    end = min(len(text), index + len(term) + radius)
    prefix = "..." if start else ""
    suffix = "..." if end < len(text) else ""
    return f"{prefix}{text[start:end].strip()}{suffix}"
