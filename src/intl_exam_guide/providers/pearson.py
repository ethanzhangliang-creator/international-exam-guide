from __future__ import annotations

import re
from pathlib import Path

from intl_exam_guide.models import Qualification, SourceRecord
from intl_exam_guide.providers.base import ExamBoardProvider, Link
from intl_exam_guide.providers.common import (
    attach_pdf_content,
    clean_text,
    code_from_text,
    dedupe_links,
    find_pdf_link,
    format_candidate_choices,
    first_assessment_from_nodes,
    first_node_text,
    first_teaching_from_nodes,
    infer_qualification_type,
    is_pdf_url,
    is_url,
    normalize_level,
    parse_page,
    qualification_family,
    subject_slug_from_query,
    title_from_url,
)


class PearsonEdexcelProvider(ExamBoardProvider):
    name = "pearson"
    supported_levels = ("international_gcse", "international_as_a_level")

    def find_qualification(
        self, query: str, level: str | None = None, exam_year: str | None = None
    ) -> Link:
        if not is_url(query):
            return self._find_candidate_by_subject(query, level)
        qtype = infer_qualification_type(query, query, level)
        return Link(text=title_from_url(query), href=query, qualification_type=qtype)

    def parse_qualification(
        self, page_url: str, level: str | None = None, exam_year: str | None = None
    ) -> Qualification:
        if is_pdf_url(page_url):
            title = title_from_url(page_url)
            qtype = infer_qualification_type(title, page_url, level)
            return self._qualification_from_parts(
                title=title,
                page_url=page_url,
                specification_url=page_url,
                qtype=qtype,
                first_teaching=None,
                first_assessment=None,
            )

        parser = parse_page(page_url)
        title = clean_text(
            first_node_text(parser, "h1") or parser.title or title_from_url(page_url)
        )
        qtype = infer_qualification_type(title, page_url, level)
        specification_url = find_pdf_link(
            parser,
            include_terms=("specification", "download"),
            exclude_terms=(
                "past-paper",
                "past paper",
                "mark-scheme",
                "mark scheme",
                "guide",
                "welcome",
                "onboarding",
            ),
        )
        if not specification_url:
            raise ValueError(
                "No Pearson specification PDF link found on the supplied page. "
                "Use a direct Pearson specification PDF URL or another official subject-page URL."
            )
        return self._qualification_from_parts(
            title=title,
            page_url=page_url,
            specification_url=specification_url,
            qtype=qtype,
            first_teaching=first_teaching_from_nodes(parser.nodes),
            first_assessment=first_assessment_from_nodes(parser.nodes),
        )

    def download_specification(
        self,
        qualification: Qualification,
        output_dir: Path,
        exam_year: str | None = None,
    ) -> Qualification:
        if not qualification.source.specification_url:
            raise ValueError("No Pearson specification PDF URL is attached to the qualification.")
        return attach_pdf_content(
            qualification,
            output_dir,
            qualification.source.specification_url,
            self.name,
            exam_year=exam_year,
        )

    def _find_candidate_by_subject(self, query: str, level: str | None) -> Link:
        candidates = []
        for url in pearson_candidate_urls(query, level):
            link = self._validate_candidate_url(url, level)
            if link:
                candidates.append(link)
        candidates = dedupe_links(candidates)
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            raise ValueError(format_candidate_choices("Pearson Edexcel", query, candidates))
        raise ValueError(
            "Pearson Edexcel could not confirm one official subject page from the subject name alone. "
            "Provide the official Pearson subject-page URL or direct specification PDF URL."
        )

    def _validate_candidate_url(self, url: str, level: str | None) -> Link | None:
        try:
            parser = parse_page(url)
        except Exception:
            return None
        title = clean_text(first_node_text(parser, "h1") or parser.title or title_from_url(url))
        lower_title = title.lower()
        if "page not found" in lower_title or "404" in lower_title:
            return None
        qtype = infer_qualification_type(title, url, level)
        return Link(text=title, href=url, qualification_type=qtype)

    def _qualification_from_parts(
        self,
        title: str,
        page_url: str,
        specification_url: str,
        qtype: str,
        first_teaching: str | None,
        first_assessment: str | None,
    ) -> Qualification:
        code = code_from_text(title) or code_from_text(page_url)
        subject_area = pearson_subject_area(title, page_url)
        source = SourceRecord(
            provider=self.name,
            page_url=page_url,
            specification_url=specification_url,
            qualification_family=qualification_family(self.name, qtype),
            first_teaching=first_teaching,
            first_assessment=first_assessment,
        )
        return Qualification(
            title=title,
            code=code,
            qualification_type=qtype,
            subject_area=subject_area,
            page_url=page_url,
            summary=pearson_summary(qtype, first_teaching, first_assessment),
            topics=[],
            assessments=[],
            source=source,
            audience_note=pearson_audience_note(qtype),
            provider=self.name,
            qualification_family=qualification_family(self.name, qtype),
            route_tags=pearson_route_tags(qtype, page_url),
        )


def pearson_subject_area(title: str, url: str) -> str | None:
    cleaned = re.sub(
        r"\b(Pearson|Edexcel|International|GCSE|Advanced|Levels?|A\s*Level|Specification|\(\d{4}\))\b",
        " ",
        title,
        flags=re.I,
    )
    cleaned = clean_text(cleaned)
    if cleaned:
        return cleaned
    parts = [part for part in re.split(r"[-_/]", url) if part and not part.isdigit()]
    return clean_text(" ".join(parts[-4:])).title() if parts else None


def pearson_summary(
    qtype: str,
    first_teaching: str | None,
    first_assessment: str | None,
) -> list[str]:
    structure = (
        "Pearson Edexcel International AS/A Level is normally modular and may include unit routes."
        if qtype == "international_as_a_level"
        else "Pearson Edexcel International GCSE may be linear or modular depending on the subject and specification."
    )
    values = [structure]
    if first_teaching:
        values.append(f"First teaching: {first_teaching}")
    if first_assessment:
        values.append(f"First external assessment: {first_assessment}")
    return values


def pearson_audience_note(qtype: str) -> str:
    if qtype == "international_as_a_level":
        return (
            "Pearson Edexcel International AS/A Levels are international qualifications "
            "for international students outside the UK, commonly structured through AS/A2 or unit routes. "
            "Confirm available units and exam series with the school or exam centre."
        )
    return (
        "Pearson Edexcel International GCSEs are designed for international students "
        "and schools outside the UK. Some subjects offer linear or modular assessment "
        "routes, so families should confirm the chosen route and exam series locally."
    )


def pearson_route_tags(qtype: str, url: str) -> list[str]:
    tags = ["Pearson Edexcel"]
    if qtype == "international_as_a_level":
        tags.append("modular")
    if "modular" in url.lower():
        tags.append("modular")
    if "international-gcse" in url.lower():
        tags.append("international-gcse")
    return list(dict.fromkeys(tags))


def pearson_candidate_urls(query: str, level: str | None) -> list[str]:
    slugs = pearson_subject_slugs(query, level)
    if not slugs:
        return []
    normalized = normalize_level(level)
    urls: list[str] = []
    if normalized in {None, "gcse", "igcse", "international-gcse"}:
        base = "https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses"
        for slug in slugs:
            urls.extend(
                [
                    f"{base}/international-gcse-{slug}-2016.html",
                    f"{base}/international-gcse-{slug}-2017.html",
                    f"{base}/{slug}-2023-modular.html",
                    f"{base}/{slug}-2024-modular.html",
                ]
            )
    if normalized in {None, "a-level", "alevel", "as-a-level", "international-as-a-level"}:
        for slug in slugs:
            urls.append(
                "https://qualifications.pearson.com/en/qualifications/"
                f"edexcel-international-advanced-levels/{slug}-2018.html"
            )
    return urls


def pearson_subject_slugs(query: str, level: str | None) -> list[str]:
    primary = subject_slug_from_query(query)
    slugs = [primary] if primary else []
    normalized = normalize_level(level)
    if normalized in {None, "gcse", "igcse", "international-gcse"}:
        text = query.lower()
        text = re.sub(r"\ba\s*level\b|\bas\s*a\s*level\b|\bas-a-level\b|\balevel\b", " ", text)
        text = re.sub(
            r"\b(pearson|edexcel|international|gcse|igcse|syllabus|specification|spec|pdf|guide|revision|handbook)\b",
            " ",
            text,
        )
        terms = re.findall(r"[a-z0-9]+", text)
        if len(terms) >= 2 and terms[-1] in {"a", "b"}:
            slugs.append("-".join(terms))
    return list(dict.fromkeys(slug for slug in slugs if slug))
