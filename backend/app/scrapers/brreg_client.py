from dataclasses import dataclass
from typing import Any

import requests


BRREG_BASE_URL = "https://data.brreg.no/enhetsregisteret/api/enheter"


@dataclass
class RegistryCompany:
    organization_number: str
    legal_name: str
    company_type: str | None
    address: str | None
    postal_code: str | None
    city: str | None
    municipality: str | None
    industry_code: str | None
    industry_description: str | None
    website: str | None


class BrregClient:
    """
    Client for the Norwegian Brønnøysund Register Centre
    Enhetsregisteret API.
    """

    def __init__(
        self,
        base_url: str = BRREG_BASE_URL,
        timeout: int = 15,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_company(
        self,
        organization_number: str,
    ) -> RegistryCompany:

        organization_number = self._normalize_org_number(
            organization_number
        )

        url = f"{self.base_url}/{organization_number}"

        response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "Signalpost/0.1",
            },
            timeout=self.timeout,
        )

        if response.status_code == 404:
            raise ValueError(
                f"Company with organization number "
                f"{organization_number} was not found."
            )

        response.raise_for_status()

        data: dict[str, Any] = response.json()

        return self._parse_company(data)

    @staticmethod
    def _normalize_org_number(
        organization_number: str,
    ) -> str:

        normalized = "".join(
            character
            for character in organization_number
            if character.isdigit()
        )

        if len(normalized) != 9:
            raise ValueError(
                "Norwegian organization number must contain "
                "exactly 9 digits."
            )

        return normalized

    @staticmethod
    def _parse_company(
        data: dict[str, Any],
    ) -> RegistryCompany:

        address_data = data.get("forretningsadresse") or {}

        address_lines = address_data.get("adresse") or []

        address = ", ".join(
            str(line).strip()
            for line in address_lines
            if str(line).strip()
        )

        postal_code = address_data.get("postnummer")
        city = address_data.get("poststed")
        municipality = address_data.get("kommune")

        industry = data.get("naeringskode1") or {}

        return RegistryCompany(
            organization_number=str(
                data.get("organisasjonsnummer", "")
            ),
            legal_name=str(
                data.get("navn", "")
            ),
            company_type=data.get("organisasjonsform", {}).get(
                "beskrivelse"
            ),
            address=address or None,
            postal_code=postal_code,
            city=city,
            municipality=municipality,
            industry_code=industry.get("kode"),
            industry_description=industry.get("beskrivelse"),
            website=data.get("hjemmeside"),
        )