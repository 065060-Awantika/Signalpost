import json
import re

from bs4 import BeautifulSoup


class HTMLCleaner:
    """
    Converts raw HTML into clean, readable text
    suitable for downstream fact extraction.
    """

    REMOVE_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
        "iframe",
        "canvas",
        "nav",
        "footer",
        "header",
        "form",
        "aside",
        "template",
    }

    REMOVE_TEXT = {
        "skip to main content",
        "skip to content",
        "menu",
        "close menu",
    }

    def clean(self, html: str) -> str:
        if not html or not html.strip():
            return ""

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        structured_parts = self._extract_json_ld(
            soup
        )

        metadata_parts = self._extract_metadata(
            soup
        )

        self._remove_noise(soup)

        content = self._extract_visible_content(
            soup
        )

        combined_parts = []

        if content:
            combined_parts.append(content)

        combined_parts.extend(
            structured_parts
        )

        combined_parts.extend(
            metadata_parts
        )

        combined = self._normalize(
            " ".join(combined_parts)
        )

        return self._clean_final_text(
            combined
        )

    def _extract_json_ld(
        self,
        soup: BeautifulSoup,
    ) -> list[str]:
        parts: list[str] = []

        for script in soup.find_all(
            "script",
            attrs={
                "type": "application/ld+json"
            },
        ):
            raw = (
                script.string
                or script.get_text(
                    separator=" ",
                    strip=True,
                )
            )

            if not raw:
                continue

            try:
                data = json.loads(raw)
            except (
                json.JSONDecodeError,
                TypeError,
            ):
                continue

            self._collect_json_values(
                data,
                parts,
            )

        return self._deduplicate_strings(
            parts
        )

    def _collect_json_values(
        self,
        value,
        output: list[str],
    ) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if str(key).startswith("@"):
                    continue

                self._collect_json_values(
                    nested,
                    output,
                )

        elif isinstance(value, list):
            for item in value:
                self._collect_json_values(
                    item,
                    output,
                )

        elif isinstance(value, str):
            value = self._normalize(value)

            if len(value) >= 2:
                output.append(value)

    def _extract_metadata(
        self,
        soup: BeautifulSoup,
    ) -> list[str]:
        parts: list[str] = []

        useful_meta = {
            "description",
            "og:title",
            "og:description",
            "twitter:title",
            "twitter:description",
            "keywords",
            "author",
            "application-name",
        }

        for meta in soup.find_all("meta"):
            name = (
                meta.get("name")
                or meta.get("property")
                or meta.get("itemprop")
            )

            content = meta.get("content")

            if not name or not content:
                continue

            if str(name).lower() not in useful_meta:
                continue

            content = self._normalize(
                str(content)
            )

            if content:
                parts.append(content)

        title = soup.find("title")

        if title:
            title_text = self._normalize(
                title.get_text(
                    separator=" ",
                    strip=True,
                )
            )

            if title_text:
                parts.append(title_text)

        return self._deduplicate_strings(
            parts
        )

    def _remove_noise(
        self,
        soup: BeautifulSoup,
    ) -> None:
        for tag_name in self.REMOVE_TAGS:
            for tag in soup.find_all(
                tag_name
            ):
                tag.decompose()

    def _extract_visible_content(
        self,
        soup: BeautifulSoup,
    ) -> str:
        """
        Extract visible textual content.

        We don't blindly trust <main> because modern
        JavaScript websites may place only a small shell
        inside it.
        """

        candidates: list[str] = []

        for tag_name in (
            "main",
            "article",
            "section",
            "body",
        ):
            for tag in soup.find_all(
                tag_name
            ):
                text = tag.get_text(
                    separator=" ",
                    strip=True,
                )

                text = self._normalize(text)

                if len(text) >= 40:
                    candidates.append(text)

        # Also collect meaningful individual text blocks.
        for tag_name in (
            "h1",
            "h2",
            "h3",
            "h4",
            "p",
            "li",
        ):
            for tag in soup.find_all(
                tag_name
            ):
                text = tag.get_text(
                    separator=" ",
                    strip=True,
                )

                text = self._normalize(text)

                if len(text) >= 20:
                    candidates.append(text)

        if not candidates:
            return ""

        # Remove exact duplicates while preserving order.
        candidates = self._deduplicate_strings(
            candidates
        )

        # Prefer the richest substantial candidate.
        candidates.sort(
            key=len,
            reverse=True,
        )

        return candidates[0]

    def _clean_final_text(
        self,
        text: str,
    ) -> str:
        if not text:
            return ""

        for phrase in self.REMOVE_TEXT:
            text = re.sub(
                re.escape(phrase),
                "",
                text,
                flags=re.IGNORECASE,
            )

        text = self._normalize(text)

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        seen: set[str] = set()
        unique_sentences: list[str] = []

        for sentence in sentences:
            sentence = sentence.strip()

            if not sentence:
                continue

            normalized = re.sub(
                r"\s+",
                " ",
                sentence.lower(),
            )

            if normalized in seen:
                continue

            seen.add(normalized)
            unique_sentences.append(sentence)

        return self._normalize(
            " ".join(unique_sentences)
        )

    @staticmethod
    def _deduplicate_strings(
        values: list[str],
    ) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []

        for value in values:
            normalized = re.sub(
                r"\s+",
                " ",
                value.lower(),
            ).strip()

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(normalized)
            result.append(value)

        return result

    @staticmethod
    def _normalize(
        text: str,
    ) -> str:
        if not text:
            return ""

        return re.sub(
            r"\s+",
            " ",
            text,
        ).strip()