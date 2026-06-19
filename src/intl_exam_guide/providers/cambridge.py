from __future__ import annotations

import re
import urllib.error
from pathlib import Path

from intl_exam_guide.models import Qualification, SourceRecord
from intl_exam_guide.providers.base import ExamBoardProvider, Link
from intl_exam_guide.providers.common import (
    attach_pdf_content,
    clean_text,
    code_from_text,
    dedupe_links,
    format_candidate_choices,
    first_node_text,
    infer_qualification_type,
    is_pdf_url,
    is_url,
    normalize_level,
    parse_page,
    qualification_family,
    subject_terms_from_query,
    title_from_url,
)


class CambridgeInternationalProvider(ExamBoardProvider):
    name = "cambridge"
    supported_levels = ("international_gcse", "international_as_a_level")
    igcse_subjects_url = (
        "https://www.cambridgeinternational.org/programmes-and-qualifications/"
        "cambridge-upper-secondary/cambridge-igcse/subjects"
    )
    alevel_subjects_url = (
        "https://www.cambridgeinternational.org/programmes-and-qualifications/"
        "cambridge-advanced/cambridge-international-as-and-a-levels/subjects"
    )

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
            year_range = year_range_from_text(page_url)
            selected_year = validate_direct_pdf_year(year_range, exam_year, page_url)
            title = title_from_url(page_url)
            qtype = infer_qualification_type(title, page_url, level)
            return self._qualification_from_parts(
                title=title,
                page_url=page_url,
                specification_url=page_url,
                qtype=qtype,
                year_range=year_range,
                exam_year=selected_year,
            )

        parser = parse_page(page_url)
        title = clean_text(
            first_node_text(parser, "h1") or parser.title or title_from_url(page_url)
        )
        qtype = infer_qualification_type(title, page_url, level)
        syllabus_link = select_syllabus_link(parser.links, exam_year)
        return self._qualification_from_parts(
            title=title,
            page_url=page_url,
            specification_url=syllabus_link.href,
            qtype=qtype,
            year_range=syllabus_link.syllabus_year_range,
            exam_year=syllabus_link.selected_exam_year,
        )

    def download_specification(
        self,
        qualification: Qualification,
        output_dir: Path,
        exam_year: str | None = None,
    ) -> Qualification:
        if not qualification.source.specification_url:
            raise ValueError("No Cambridge syllabus PDF URL is attached to the qualification.")
        return attach_pdf_content(
            qualification,
            output_dir,
            qualification.source.specification_url,
            self.name,
            exam_year=exam_year or qualification.selected_exam_year,
        )

    def _find_candidate_by_subject(self, query: str, level: str | None) -> Link:
        candidates = dedupe_links(cambridge_subject_candidates(query, level))
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            raise ValueError(format_candidate_choices("Cambridge International / CAIE", query, candidates))
        raise ValueError(
            "Cambridge International / CAIE could not confirm one official subject page from "
            "the subject name alone. Provide a syllabus code such as 0452/9706, the official "
            "subject-page URL, or a direct syllabus PDF URL."
        )

    def _qualification_from_parts(
        self,
        title: str,
        page_url: str,
        specification_url: str,
        qtype: str,
        year_range: str | None,
        exam_year: str | None,
    ) -> Qualification:
        code = code_from_text(title) or code_from_text(page_url)
        source = SourceRecord(
            provider=self.name,
            page_url=page_url,
            specification_url=specification_url,
            qualification_family=qualification_family(self.name, qtype),
            syllabus_year_range=year_range,
            selected_exam_year=exam_year,
            issue_version=f"{year_range} syllabus" if year_range else None,
        )
        return Qualification(
            title=title,
            code=code,
            qualification_type=qtype,
            subject_area=cambridge_subject_area(title),
            page_url=page_url,
            summary=cambridge_summary(qtype, year_range, exam_year),
            topics=[],
            assessments=[],
            source=source,
            audience_note=cambridge_audience_note(qtype),
            provider=self.name,
            qualification_family=qualification_family(self.name, qtype),
            selected_exam_year=exam_year,
            route_tags=cambridge_route_tags(qtype),
        )


def select_syllabus_link(links: list[Link], exam_year: str | None) -> Link:
    candidates: list[Link] = []
    for link in links:
        combined = f"{link.text} {link.href}".lower()
        if ".pdf" not in combined or "syllabus" not in combined:
            continue
        if "update" in combined or "description" in combined:
            continue
        year_range = year_range_from_text(f"{link.text} {link.href}")
        candidates.append(
            Link(
                text=link.text,
                href=link.href,
                syllabus_year_range=year_range,
            )
        )
    if not candidates:
        raise ValueError("No Cambridge syllabus PDF link found on the supplied subject page.")
    if len(candidates) == 1:
        chosen = candidates[0]
        chosen.selected_exam_year = exam_year
        return chosen
    if not exam_year:
        ranges = ", ".join(link.syllabus_year_range or link.text for link in candidates)
        raise ValueError(
            "Cambridge subject page has multiple syllabus year ranges. "
            f"Please provide --exam-year. Available ranges: {ranges}."
        )
    year = parse_exam_year(exam_year)
    for link in candidates:
        if year_range_contains(link.syllabus_year_range, year):
            link.selected_exam_year = str(year)
            return link
    ranges = ", ".join(link.syllabus_year_range or link.text for link in candidates)
    raise ValueError(
        f"Cambridge exam year {year} does not match any syllabus range on the page. "
        f"Available ranges: {ranges}."
    )


def validate_direct_pdf_year(
    year_range: str | None,
    exam_year: str | None,
    url: str,
) -> str | None:
    if not exam_year:
        return None
    year = parse_exam_year(exam_year)
    if year_range and not year_range_contains(year_range, year):
        raise ValueError(
            f"Cambridge exam year {year} does not match syllabus PDF range {year_range}: {url}"
        )
    return str(year)


def year_range_from_text(value: str) -> str | None:
    match = re.search(r"(20\d{2})\s*[-–]\s*(20\d{2})", value)
    if not match:
        return None
    return f"{match.group(1)}-{match.group(2)}"


def year_range_contains(year_range: str | None, year: int) -> bool:
    if not year_range:
        return False
    start, end = [int(part) for part in year_range.split("-", 1)]
    return start <= year <= end


def parse_exam_year(value: str) -> int:
    if not re.fullmatch(r"20\d{2}", str(value).strip()):
        raise ValueError(f"Invalid Cambridge exam year: {value!r}. Use a four-digit year.")
    return int(value)


def cambridge_subject_area(title: str) -> str | None:
    cleaned = re.sub(
        r"\b(Cambridge|International|IGCSE|AS|A|Level|Syllabus|\(\d{4}\))\b|&",
        " ",
        title,
        flags=re.I,
    )
    return clean_text(cleaned) or None


def cambridge_summary(qtype: str, year_range: str | None, exam_year: str | None) -> list[str]:
    values = [
        "Cambridge syllabus year means the year in which the examination will be taken."
    ]
    if year_range:
        values.append(f"Syllabus range: {year_range}")
    if exam_year:
        values.append(f"Selected exam year: {exam_year}")
    if qtype == "international_as_a_level":
        values.append("Cambridge International AS & A Level may include AS and A Level assessment routes.")
    else:
        values.append(
            "Cambridge IGCSE is handled as a source-bound linear end-of-course revision route; "
            "Core, Extended, and component choices must still be confirmed with the centre."
        )
    return values


def cambridge_audience_note(qtype: str) -> str:
    if qtype == "international_as_a_level":
        return (
            "Cambridge International AS & A Levels are international qualifications for "
            "international students outside the UK. "
            "Use the syllabus range that covers the student's exam year, then confirm "
            "component availability with the school or centre."
        )
    return (
        "Cambridge IGCSE is an international qualification for international students "
        "outside the UK. Use the syllabus range that covers the student's exam year, "
        "and confirm Core, Extended, and component choices with the school or centre."
    )


def cambridge_route_tags(qtype: str) -> list[str]:
    if qtype == "international_as_a_level":
        return ["AS", "A Level", "Cambridge International"]
    return ["Core", "Extended", "Cambridge IGCSE"]


def cambridge_subject_candidates(query: str, level: str | None) -> list[Link]:
    terms = subject_terms_from_query(query)
    code = code_from_text(query)
    normalized = normalize_level(level)
    index_pages: list[tuple[str, str]] = []
    if normalized in {None, "gcse", "igcse", "international-gcse"}:
        index_pages.append(
            (
                CambridgeInternationalProvider.igcse_subjects_url,
                "international_gcse",
            )
        )
    if normalized in {None, "a-level", "alevel", "as-a-level", "international-as-a-level"}:
        index_pages.append(
            (
                CambridgeInternationalProvider.alevel_subjects_url,
                "international_as_a_level",
            )
        )

    candidates: list[Link] = []
    for url, qtype in index_pages:
        try:
            parser = parse_page(url)
        except (OSError, TimeoutError, urllib.error.URLError, UnicodeDecodeError):
            continue
        for link in parser.links:
            combined = f"{link.text} {link.href}".lower()
            if "programmes-and-qualifications/cambridge-" not in combined:
                continue
            if code:
                if code not in combined:
                    continue
            elif terms and not all(term in combined for term in terms):
                continue
            candidates.append(
                Link(
                    text=clean_text(link.text),
                    href=link.href,
                    qualification_type=qtype,
                )
            )
    return candidates
