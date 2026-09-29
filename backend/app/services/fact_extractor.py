from dataclasses import dataclass
import re
from typing import Optional


@dataclass
class ExtractedFact:
    """
    A fact candidate extracted from a public source.

    This is an intermediate object.
    It will later be converted into CompanyFact
    when the fact passes verification.
    """

    field_name: str
    value: str
    evidence_text: str
    confidence: float
    value_year: Optional[int] = None


class FactExtractor:
    """
    Deterministic fact extractor for company webpages.

    Uses rules and regular expressions instead of paid LLM APIs.
    Supports labelled facts and natural-language facts in
    English and common Norwegian formats.
    """

    FIELD_PATTERNS = {
        "organization_number": [
            r"(?:organization\s*(?:number|no\.?)|org\.?\s*number)"
            r"\s*[:#-]?\s*(\d{9})",

            r"(?:organisasjonsnummer|org\.?\s*nr\.?)"
            r"\s*[:#-]?\s*(\d{9})",
        ],

        "legal_name": [
            r"(?:legal\s*name|company\s*name)"
            r"\s*[:\-]\s*([^\n|]{2,150})",

            r"(?:foretaksnavn|virksomhetsnavn)"
            r"\s*[:\-]\s*([^\n|]{2,150})",
        ],

        "website": [
            r"(?:website|web|nettside)"
            r"\s*[:\-]?\s*"
            r"(https?://[^\s<]+)",

            r"(https?://(?:www\.)?"
            r"[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
            r"(?:/[^\s<]*)?)",
        ],

        "industry": [
            r"(?:industry|sector)"
            r"\s*[:\-]\s*([^\n|]{2,150})",

            r"(?:bransje|næring)"
            r"\s*[:\-]\s*([^\n|]{2,150})",
        ],

        "address": [
            r"(?:address|adresse)"
            r"\s*[:\-]\s*([^\n|]{3,200})",
        ],

        "city": [
            r"(?:city|by|sted)"
            r"\s*[:\-]\s*([A-Za-zÀ-ÿ .'-]{2,100})",
        ],

        "employee_count": [
            r"(?:employees?|employee\s*count|"
            r"number\s*of\s*employees?)"
            r"\s*[:\-]?\s*"
            r"(?:around\s+|approximately\s+|about\s+)?"
            r"([\d,.\s]+)",

            r"(?:ansatte|antall\s+ansatte)"
            r"\s*[:\-]?\s*"
            r"([\d,.\s]+)",

            r"(?:around|approximately|about|"
            r"over|more\s+than)"
            r"\s+([\d,]+)"
            r"\s+(?:employees?|staff|people)",

            r"([\d,]+)"
            r"\s+(?:employees?|staff|people)",
        ],

        "founded_year": [
            r"(?:founded|established)"
            r"\s*[:\-]?\s*"
            r"(?:in\s+)?"
            r"((?:18|19|20)\d{2})",

            r"(?:founded\s+in|established\s+in)"
            r"\s*"
            r"((?:18|19|20)\d{2})",

            r"(?:grunnlagt|etablert)"
            r"\s*[:\-]?\s*"
            r"(?:i\s+)?"
            r"((?:18|19|20)\d{2})",

            r"(?:since)"
            r"\s*[:\-]?\s*"
            r"((?:18|19|20)\d{2})",
        ],

        "email": [
            r"(?:email|e-mail)"
            r"\s*[:\-]?\s*"
            r"([A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,})",

            r"([A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,})",
        ],

        "phone": [
            r"(?:phone|telephone|tel\.?|telefon)"
            r"\s*[:\-]?\s*"
            r"(\+?[\d\s().\-]{7,25})",
        ],

        "country": [
            r"(?:country|land)"
            r"\s*[:\-]\s*"
            r"([A-Za-zÀ-ÿ .'-]{2,100})",

            r"(?:headquartered|headquarters)"
            r"\s+(?:in|at)\s+"
            r"([A-Za-zÀ-ÿ .'-]{2,100})",
        ],
    }

    NATURAL_LANGUAGE_PATTERNS = {
        "employee_count": [
            r"\b(?:around|approximately|about)\s+"
            r"([\d,]+)\s+employees?\b",

            r"\b(?:over|more\s+than)\s+"
            r"([\d,]+)\s+employees?\b",

            r"\b([\d,]+)\s+employees?\b",

            r"\b(?:around|approximately|about)\s+"
            r"([\d,]+)\s+ansatte\b",

            r"\b([\d,]+)\s+ansatte\b",
        ],

        "founded_year": [
            r"\bfounded\s+in\s+"
            r"((?:18|19|20)\d{2})\b",

            r"\bestablished\s+in\s+"
            r"((?:18|19|20)\d{2})\b",

            r"\bgrunnlagt\s+i\s+"
            r"((?:18|19|20)\d{2})\b",

            r"\betablert\s+i\s+"
            r"((?:18|19|20)\d{2})\b",

            r"\bsince\s+"
            r"((?:18|19|20)\d{2})\b",
        ],

        "country": [
            r"\bheadquartered\s+in\s+"
            r"([A-Z][A-Za-zÀ-ÿ .'-]{1,80})",

            r"\bheadquarters\s+(?:are\s+)?in\s+"
            r"([A-Z][A-Za-zÀ-ÿ .'-]{1,80})",
        ],

        "email": [
            r"\b([A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,})\b",
        ],
    }

    def extract(
        self,
        text: str,
    ) -> list[ExtractedFact]:

        if not text or not text.strip():
            return []

        normalized_text = self._normalize(
            text
        )

        facts: list[ExtractedFact] = []

        # ---------------------------------------------------------
        # 1. Extract labelled facts
        # ---------------------------------------------------------
        for field_name, patterns in (
            self.FIELD_PATTERNS.items()
        ):
            fact = self._extract_first_match(
                normalized_text,
                field_name,
                patterns,
            )

            if fact:
                facts.append(fact)

        # ---------------------------------------------------------
        # 2. Extract natural-language facts
        # ---------------------------------------------------------
        for field_name, patterns in (
            self.NATURAL_LANGUAGE_PATTERNS.items()
        ):
            if any(
                fact.field_name == field_name
                for fact in facts
            ):
                continue

            fact = self._extract_first_match(
                normalized_text,
                field_name,
                patterns,
            )

            if fact:
                facts.append(fact)

        return self._deduplicate(
            facts
        )

    def _extract_first_match(
        self,
        text: str,
        field_name: str,
        patterns: list[str],
    ) -> Optional[ExtractedFact]:

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if not match:
                continue

            value = self._clean_value(
                match.group(1)
            )

            if not value:
                continue

            if not self._is_valid_value(
                field_name,
                value,
            ):
                continue

            evidence = self._build_evidence(
                text,
                match.start(),
                match.end(),
            )

            confidence = self._confidence(
                field_name,
                value,
            )

            value_year = None

            if field_name == "founded_year":
                try:
                    value_year = int(value)
                except ValueError:
                    value_year = None

            return ExtractedFact(
                field_name=field_name,
                value=value,
                evidence_text=evidence,
                confidence=confidence,
                value_year=value_year,
            )

        return None

    @staticmethod
    def _normalize(
        text: str,
    ) -> str:
        return " ".join(
            text.split()
        )

    @staticmethod
    def _clean_value(
        value: str,
    ) -> str:

        value = value.strip()

        value = value.rstrip(
            ".,;:|"
        )

        if (
            value.startswith("(")
            and value.endswith(")")
        ):
            value = value[1:-1].strip()

        return value

    @staticmethod
    def _is_valid_value(
        field_name: str,
        value: str,
    ) -> bool:

        if field_name == "organization_number":
            return bool(
                re.fullmatch(
                    r"\d{9}",
                    value,
                )
            )

        if field_name == "employee_count":
            digits = re.sub(
                r"[^\d]",
                "",
                value,
            )

            if not digits:
                return False

            count = int(digits)

            return (
                1
                <= count
                <= 10_000_000
            )

        if field_name == "founded_year":
            try:
                year = int(value)
            except ValueError:
                return False

            return (
                1800
                <= year
                <= 2100
            )

        if field_name == "email":
            return bool(
                re.fullmatch(
                    r"[A-Z0-9._%+\-]+"
                    r"@[A-Z0-9.\-]+\.[A-Z]{2,}",
                    value,
                    flags=re.IGNORECASE,
                )
            )

        if field_name == "phone":
            digits = re.sub(
                r"\D",
                "",
                value,
            )

            return (
                7
                <= len(digits)
                <= 15
            )

        if field_name == "website":
            return value.startswith(
                "http"
            )

        return True

    @staticmethod
    def _build_evidence(
        text: str,
        start: int,
        end: int,
        window: int = 160,
    ) -> str:

        evidence_start = max(
            0,
            start - window,
        )

        evidence_end = min(
            len(text),
            end + window,
        )

        return text[
            evidence_start:evidence_end
        ].strip()

    @staticmethod
    def _confidence(
        field_name: str,
        value: str,
    ) -> float:

        confidence_map = {
            "organization_number": 0.98,
            "legal_name": 0.90,
            "website": 0.95,
            "industry": 0.85,
            "address": 0.85,
            "city": 0.85,
            "employee_count": 0.90,
            "founded_year": 0.90,
            "email": 0.95,
            "phone": 0.90,
            "country": 0.85,
        }

        return confidence_map.get(
            field_name,
            0.70,
        )

    @staticmethod
    def _deduplicate(
        facts: list[ExtractedFact],
    ) -> list[ExtractedFact]:

        seen: set[
            tuple[str, str]
        ] = set()

        result: list[ExtractedFact] = []

        for fact in facts:
            key = (
                fact.field_name,
                fact.value.lower(),
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(fact)

        return result