from __future__ import annotations

from datetime import datetime

import requests
from sqlalchemy import select

from backend.app.database.database import Base, SessionLocal, engine
from backend.app.models.company import Company
from backend.app.models.fact import CompanyFact
from backend.app.models.source import Source


BRREG_URL = (
    "https://data.brreg.no/enhetsregisteret/api/enheter"
)

TARGET_COUNT = 1000
PAGE_SIZE = 1000


def fetch_companies() -> list[dict]:
    response = requests.get(
        BRREG_URL,
        params={
            "size": PAGE_SIZE,
            "page": 0,
        },
        headers={
            "Accept": "application/json",
            "User-Agent": "Signalpost/0.1",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    companies = data.get("_embedded", {}).get("enheter", [])

    return companies[:TARGET_COUNT]


def get_or_create_source(
    db,
    organization_number: str,
) -> Source:
    url = (
        "https://data.brreg.no/"
        "enhetsregisteret/api/enheter/"
        f"{organization_number}"
    )

    source = (
        db.query(Source)
        .filter(Source.url == url)
        .first()
    )

    if source:
        return source

    source = Source(
        url=url,
        source_type="official_registry",
        title="Norwegian Register of Business Enterprises",
        publisher="BRREG",
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


def save_company(
    db,
    data: dict,
) -> bool:
    organization_number = str(
        data.get("organisasjonsnummer", "")
    ).strip()

    legal_name = str(
        data.get("navn", "")
    ).strip()

    if not organization_number or not legal_name:
        return False

    existing = (
        db.query(Company)
        .filter(
            Company.organization_number
            == organization_number
        )
        .first()
    )

    address_data = data.get("forretningsadresse") or {}

    address_lines = (
        address_data.get("adresse") or []
    )

    address = ", ".join(
        str(line).strip()
        for line in address_lines
        if str(line).strip()
    )

    company_type_data = (
        data.get("organisasjonsform") or {}
    )

    industry_data = (
        data.get("naeringskode1") or {}
    )

    company_type = (
        company_type_data.get("beskrivelse")
    )

    industry = (
        industry_data.get("beskrivelse")
    )

    website = data.get("hjemmeside")

    if existing:
        company = existing

        company.legal_name = legal_name
        company.company_type = company_type
        company.address = address or None
        company.website = website
        company.industry = industry

    else:
        company = Company(
            organization_number=organization_number,
            legal_name=legal_name,
            company_type=company_type,
            address=address or None,
            website=website,
            industry=industry,
        )

        db.add(company)

    db.commit()
    db.refresh(company)

    source = get_or_create_source(
        db,
        organization_number,
    )

    existing_fact = (
        db.query(CompanyFact)
        .filter(
            CompanyFact.company_id == company.id,
            CompanyFact.source_id == source.id,
            CompanyFact.field_name == "legal_name",
        )
        .first()
    )

    if not existing_fact:
        db.add(
            CompanyFact(
                company_id=company.id,
                source_id=source.id,
                field_name="legal_name",
                value=legal_name,
                evidence_text=(
                    f"Official BRREG legal name: "
                    f"{legal_name}"
                ),
                confidence=0.99,
                verification_status="verified",
            )
        )

    existing_org_fact = (
        db.query(CompanyFact)
        .filter(
            CompanyFact.company_id == company.id,
            CompanyFact.source_id == source.id,
            CompanyFact.field_name
            == "organization_number",
        )
        .first()
    )

    if not existing_org_fact:
        db.add(
            CompanyFact(
                company_id=company.id,
                source_id=source.id,
                field_name="organization_number",
                value=organization_number,
                evidence_text=(
                    "Official BRREG organization number: "
                    f"{organization_number}"
                ),
                confidence=0.99,
                verification_status="verified",
            )
        )

    if company_type:
        _save_fact(
            db,
            company.id,
            source.id,
            "company_type",
            company_type,
        )

    if address:
        _save_fact(
            db,
            company.id,
            source.id,
            "address",
            address,
        )

    if industry:
        _save_fact(
            db,
            company.id,
            source.id,
            "industry",
            industry,
        )

    if website:
        _save_fact(
            db,
            company.id,
            source.id,
            "website",
            website,
        )

    db.commit()

    return True


def _save_fact(
    db,
    company_id: int,
    source_id: int,
    field_name: str,
    value: str,
) -> None:
    existing = (
        db.query(CompanyFact)
        .filter(
            CompanyFact.company_id == company_id,
            CompanyFact.source_id == source_id,
            CompanyFact.field_name == field_name,
        )
        .first()
    )

    if existing:
        existing.value = value
        existing.evidence_text = (
            f"Official BRREG {field_name}: {value}"
        )
        existing.confidence = 0.99
        existing.verification_status = "verified"
        return

    db.add(
        CompanyFact(
            company_id=company_id,
            source_id=source_id,
            field_name=field_name,
            value=value,
            evidence_text=(
                f"Official BRREG {field_name}: {value}"
            ),
            confidence=0.99,
            verification_status="verified",
        )
    )


def main() -> None:
    print("=" * 60)
    print("SIGNALPOST — BOOTSTRAP 1,000 COMPANIES")
    print("=" * 60)

    Base.metadata.create_all(bind=engine)

    print("\nFetching companies from BRREG...")

    companies = fetch_companies()

    print(
        f"Received {len(companies)} companies from BRREG."
    )

    if not companies:
        print("No companies received.")
        return

    db = SessionLocal()

    successful = 0
    failed = 0

    try:
        for index, company_data in enumerate(
            companies,
            start=1,
        ):
            try:
                saved = save_company(
                    db,
                    company_data,
                )

                if saved:
                    successful += 1
                else:
                    failed += 1

            except Exception as exc:
                failed += 1
                db.rollback()

                print(
                    f"[FAILED] "
                    f"{company_data.get('organisasjonsnummer')} "
                    f"| {exc}"
                )

            if index % 100 == 0:
                print(
                    f"Processed {index}/{len(companies)} "
                    f"| Successful: {successful} "
                    f"| Failed: {failed}"
                )

    finally:
        db.close()

    print("\n" + "=" * 60)
    print("BOOTSTRAP COMPLETE")
    print("=" * 60)
    print(f"Companies processed : {len(companies)}")
    print(f"Successful          : {successful}")
    print(f"Failed              : {failed}")
    print("=" * 60)


if __name__ == "__main__":
    main()