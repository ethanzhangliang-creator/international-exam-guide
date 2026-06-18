from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal

from intl_exam_guide.models import Topic


ExampleDomain = Literal["mathematics", "biology", "chemistry", "economics", "accounting", "generic"]

AMBIGUOUS_SUBJECT_AREAS = {
    "combined science",
    "combined sciences",
    "demo science",
    "double award science",
    "example",
    "general",
    "project-based learning",
    "science",
    "sciences",
}


@dataclass(frozen=True)
class SubjectProfile:
    name: str
    family: str
    example_domain: ExampleDomain
    description: str


MATHEMATICS = SubjectProfile(
    name="mathematics",
    family="mathematics",
    example_domain="mathematics",
    description="Numbers, algebra, geometry, statistics, probability, and graphs.",
)
CHEMISTRY = SubjectProfile(
    name="chemistry",
    family="science",
    example_domain="chemistry",
    description="Chemistry-specific particle, bonding, reaction, laboratory, and calculation topics.",
)
BIOLOGY = SubjectProfile(
    name="biology",
    family="science",
    example_domain="biology",
    description="Biology-specific cells, molecules, enzymes, DNA, transport, ecology, and practical topics.",
)
ECONOMICS = SubjectProfile(
    name="economics-business",
    family="social-science",
    example_domain="economics",
    description="Economics and business concepts such as markets, production, finance, and policy.",
)
ACCOUNTING = SubjectProfile(
    name="accounting-finance",
    family="business-finance",
    example_domain="accounting",
    description="Accounting records, double entry, statements, reconciliation, ratios, and analysis.",
)
GENERIC = SubjectProfile(
    name="generic",
    family="generic",
    example_domain="generic",
    description="Source-bound fallback for subjects without a specialist profile yet.",
)


def resolve_subject_profile(
    subject_area: str | None,
    topic: Topic,
    source_text: str,
) -> SubjectProfile:
    """Choose a broad subject profile, not a per-course hard-coded template."""

    declared = (subject_area or "").lower()
    if has_terms(declared, ["math", "mathematics", "further mathematics"]):
        return MATHEMATICS
    if has_terms(declared, ["economics", "business"]):
        return ECONOMICS
    if has_terms(declared, ["accounting", "bookkeeping", "book keeping", "finance", "financial"]):
        return ACCOUNTING
    if has_terms(declared, ["chemistry"]):
        return CHEMISTRY
    if has_terms(declared, ["biology"]):
        return BIOLOGY
    if declared and declared not in AMBIGUOUS_SUBJECT_AREAS:
        return GENERIC

    prefix = topic.title.split(" ", 1)[0][:1]
    text = source_text.lower()
    if prefix in {"N", "A", "G", "S"} and looks_like_mathematics(text):
        return MATHEMATICS

    if looks_like_economics(text):
        return ECONOMICS
    if looks_like_accounting(text):
        return ACCOUNTING
    if looks_like_chemistry(text):
        return CHEMISTRY
    if looks_like_biology(text):
        return BIOLOGY
    return GENERIC


def looks_like_mathematics(text: str) -> bool:
    return has_terms(
        text,
        [
            "algebra",
            "angle",
            "angles",
            "calculus",
            "circle",
            "coordinate",
            "coordinates",
            "decimal",
            "decimals",
            "equation",
            "equations",
            "fraction",
            "fractions",
            "function",
            "functions",
            "geometry",
            "graph",
            "graphs",
            "inequality",
            "matrix",
            "matrices",
            "mensuration",
            "number",
            "numbers",
            "percentage",
            "percentages",
            "probability",
            "pythagoras",
            "quadratic",
            "ratio",
            "sequence",
            "sequences",
            "set",
            "sets",
            "statistics",
            "triangle",
            "triangles",
            "trigonometry",
            "vector",
            "vectors",
        ],
    )


def looks_like_chemistry(text: str) -> bool:
    return has_terms(
        text,
        [
            "acid",
            "alkali",
            "atom",
            "atomic",
            "bond",
            "bonding",
            "carbon",
            "chemical",
            "chemistry",
            "chromatography",
            "compound",
            "covalent",
            "electrolysis",
            "exothermic",
            "gas",
            "gases",
            "hydrocarbon",
            "ionic",
            "metal",
            "metals",
            "mole",
            "moles",
            "molar",
            "nanoparticle",
            "nanoparticles",
            "organic",
            "periodic",
            "ph",
            "polymer",
            "polymers",
            "rate of reaction",
            "redox",
            "salt",
            "salts",
            "solute",
            "substance",
            "substances",
        ],
    )


def looks_like_biology(text: str) -> bool:
    return has_terms(
        text,
        [
            "amino acid",
            "biology",
            "cell",
            "cells",
            "cell membrane",
            "chromosome",
            "dna",
            "enzyme",
            "enzymes",
            "genetic",
            "glucose",
            "lipid",
            "membrane",
            "osmosis",
            "photosynthesis",
            "protein",
            "respiration",
            "rna",
            "starch",
            "transport",
            "triglyceride",
        ],
    )


def looks_like_economics(text: str) -> bool:
    return has_terms(
        text,
        [
            "balance of payments",
            "bank",
            "business",
            "choice",
            "consumer",
            "cost",
            "demand",
            "economic",
            "economics",
            "economy",
            "elasticity",
            "employment",
            "exchange rate",
            "factor",
            "financial",
            "government",
            "inflation",
            "labour",
            "market",
            "money",
            "need",
            "opportunity",
            "production",
            "producer",
            "profit",
            "resource allocation",
            "revenue",
            "scarcity",
            "sector",
            "supply",
            "trade",
            "want",
        ],
    )


def looks_like_accounting(text: str) -> bool:
    return has_terms(
        text,
        [
            "accounting",
            "bookkeeping",
            "book keeping",
            "ledger",
            "ledgers",
            "double entry",
            "trial balance",
            "bank reconciliation",
            "control account",
            "source document",
            "prime entry",
            "depreciation",
            "irrecoverable",
            "receivables",
            "payables",
            "financial statements",
            "income statement",
            "statement of financial position",
            "partnership",
            "manufacturing account",
            "ratio analysis",
            "trade receivable days",
            "trade payable days",
        ],
    )


def has_terms(text: str, terms: list[str]) -> bool:
    tokens = set(re.findall(r"[a-z0-9]+", text.lower()))
    for term in terms:
        term = term.lower()
        if " " in term or "-" in term:
            if term in text:
                return True
        elif term in tokens:
            return True
    return False
