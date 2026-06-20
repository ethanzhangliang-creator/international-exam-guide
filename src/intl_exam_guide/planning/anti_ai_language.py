from __future__ import annotations

import re


EN_REMOVALS = [
    r"\bIn conclusion,\s*",
    r"\bOverall,\s*",
    r"\bTo summarize,\s*",
    r"\bIt is worth noting that\s*",
    r"\bThe key point is that\s*",
    r"\bThe key is that\s*",
]

EN_SMELL_PATTERNS = [
    r"\bIn conclusion\b",
    r"\bOverall\b",
    r"\bTo summarize\b",
    r"\bIt is worth noting that\b",
    r"\bImagine a world where\b",
    r"\bnot just\b.*\bbut\b",
    r"\bnot only\b.*\bbut\b",
    r"\bthe key (?:lies in|is that)\b",
]

ZH_REMOVALS = [
    r"总之[，,、\s]*",
    r"综上所述[，,、\s]*",
    r"值得注意的是[，,、\s]*",
    r"关键在于[，,、\s]*",
]

ZH_SMELL_PATTERNS = [
    r"总之",
    r"综上所述",
    r"值得注意的是",
    r"让我们",
    r"想象一个",
    r"不是.{0,40}而是",
    r"不只是.{0,40}更是",
    r"不仅.{0,40}更是",
    r"关键在于",
]


def polish_ai_language(text: str, output_language: str) -> str:
    """Remove safe, formulaic AI-style transitions without changing meaning."""
    cleaned = text.strip()
    removals = ZH_REMOVALS if output_language == "zh-CN" else EN_REMOVALS
    for pattern in removals:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", cleaned).strip()


def polish_texts(values: list[str], output_language: str) -> list[str]:
    return [polish_ai_language(value, output_language) for value in values]


def has_ai_language_smell(values: list[str], output_language: str) -> bool:
    patterns = ZH_SMELL_PATTERNS if output_language == "zh-CN" else EN_SMELL_PATTERNS
    return any(
        re.search(pattern, value, flags=0 if output_language == "zh-CN" else re.IGNORECASE)
        for value in values
        for pattern in patterns
    )
