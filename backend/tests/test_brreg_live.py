from backend.app.scrapers.brreg_client import BrregClient


def test_live_company_lookup():
    client = BrregClient()

    company = client.get_company("923609016")

    print("\n--- SIGNALPOST LIVE COMPANY ---")
    print("Organization number:", company.organization_number)
    print("Legal name:", company.legal_name)
    print("Company type:", company.company_type)
    print("Address:", company.address)
    print("City:", company.city)
    print("Municipality:", company.municipality)
    print("Industry:", company.industry_code)
    print("Industry description:", company.industry_description)
    print("Website:", company.website)

    assert company.organization_number == "923609016"
    assert company.legal_name