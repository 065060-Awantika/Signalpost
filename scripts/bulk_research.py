from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from backend.app.database.database import SessionLocal
from backend.app.services.bulk_research_service import (
    BulkResearchService,
)
from backend.app.services.company_research_service import (
    CompanyResearchService,
)


INPUT_FILE = PROJECT_ROOT / "data" / "company_numbers.txt"


def load_organization_numbers() -> list[str]:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Organization number file not found: {INPUT_FILE}"
        )

    numbers = []

    for line in INPUT_FILE.read_text(
        encoding="utf-8"
    ).splitlines():
        number = line.strip()

        if number and not number.startswith("#"):
            numbers.append(number)

    return numbers


def main() -> None:
    organization_numbers = load_organization_numbers()

    if not organization_numbers:
        print("No organization numbers found.")
        return

    db = SessionLocal()

    try:
        research_service = CompanyResearchService(db)

        bulk_service = BulkResearchService(
            research_service=research_service,
        )

        print(
            f"Starting Signalpost bulk research "
            f"for {len(organization_numbers)} companies..."
        )

        results = bulk_service.research_companies(
            organization_numbers
        )

        successful = 0
        failed = 0
        total_facts = 0

        for result in results:
            if result.success:
                successful += 1
                total_facts += result.fact_count

                print(
                    f"[SUCCESS] "
                    f"{result.organization_number} | "
                    f"{result.legal_name} | "
                    f"{result.fact_count} facts"
                )
            else:
                failed += 1

                print(
                    f"[FAILED] "
                    f"{result.organization_number} | "
                    f"{result.error}"
                )

        print()
        print("=" * 60)
        print("SIGNALPOST BULK RESEARCH COMPLETE")
        print("=" * 60)
        print(f"Companies processed : {len(results)}")
        print(f"Successful          : {successful}")
        print(f"Failed              : {failed}")
        print(f"Total facts         : {total_facts}")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()