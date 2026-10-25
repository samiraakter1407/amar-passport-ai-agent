
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "passport_data.json"


def load_database():
    """Load local passport reference data."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Passport database not found: {DB_PATH}"
        )

    with DB_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_report(applicant, database=None, fee_data=None, fee_source=None):
    """Build a deterministic passport readiness report."""
    db = database if database is not None else load_database()

    age = int(applicant["age"])
    pages = str(applicant["pages"])
    validity = int(applicant["requested_validity_years"])
    delivery = applicant["delivery_speed"].lower()
    profession = applicant["profession"].lower()
    has_nid = applicant["has_nid"].lower()

    warnings = []
    documents = list(db["required_docs"]["adult"])

    if age < 18:
        max_validity = db["eligibility_rules"]["under_18"]["max_validity_years"]

        if validity > max_validity:
            warnings.append(
                "CONFLICT: Applicants under 18 are limited to "
                f"{max_validity}-year validity in the local assignment rules."
            )

        documents = list(db["required_docs"]["minor_under_18"])

    elif age > 65:
        max_validity = db["eligibility_rules"]["over_65"]["max_validity_years"]

        warnings.append(
            "VERIFY OFFICIAL POLICY: The over-65 restriction in the "
            "local database has not been independently verified."
        )

        if validity > max_validity:
            warnings.append(
                f"CONFLICT: Local assignment rules specify at most "
                f"{max_validity}-year validity for this age group."
            )

    if profession in ("government", "government employee", "govt"):
        documents.extend(db["required_docs"]["government_staff"])

    if has_nid != "yes" and age >= 18:
        warnings.append(
            "NID not confirmed. Verify which identification documents "
            "are officially acceptable for this applicant."
        )

    fee = None

    if pages not in ("48", "64"):
        warnings.append("Invalid page count: choose 48 or 64.")
    elif validity not in (5, 10):
        warnings.append("Invalid validity: choose 5 or 10 years.")
    else:
        # Prefer fee data supplied by the source module, if available.
        fees = fee_data if fee_data is not None else db["fees_2026"]

        try:
            fee = fees[f"{pages}_pages"][f"{validity}_years"][delivery]
        except (KeyError, TypeError):
            warnings.append(
                "Fee unavailable for the selected passport options."
            )

    conflict = any("CONFLICT:" in warning for warning in warnings)

    if conflict:
        fee_status = "Not confirmed until eligibility is resolved"
    elif fee is not None:
        source_label = fee_source or "assignment-provided local dataset"
        fee_status = f"{fee:,} BDT ({source_label})"
    else:
        fee_status = "Unavailable"

    return {
        "age": age,
        "validity": validity,
        "pages": pages,
        "delivery": delivery,
        "fee": fee_status,
        "documents": sorted(set(documents)),
        "warnings": warnings,
    }


def print_report(report):
    """Print the report as an English Markdown table and Bangla summary."""
    print("\n# Amar Passport Readiness Report\n")
    print("| Field | Result |")
    print("|---|---|")
    print(f"| Applicant age | {report['age']} |")
    print(f"| Passport pages | {report['pages']} |")
    print(f"| Requested validity | {report['validity']} years |")
    print(f"| Delivery | {report['delivery']} |")
    print(f"| Estimated fee | {report['fee']} |")
    print("| Documents needed | " +
          "; ".join(report["documents"]) + " |")

    print("\n## Warnings")
    if report["warnings"]:
        for warning in report["warnings"]:
            print(f"- {warning}")
    else:
        print("- No conflict detected in the local assignment rules.")

    print("\n## বাংলা সারাংশ")
    print(f"- আবেদনকারীর বয়স: {report['age']} বছর")
    print(f"- পাসপোর্টের পৃষ্ঠা: {report['pages']}")
    print(f"- চাওয়া মেয়াদ: {report['validity']} বছর")
    print(f"- ডেলিভারি: {report['delivery']}")
    print(f"- ফি: {report['fee']}")
    print("- প্রয়োজনীয় কাগজপত্র:")
    for document in report["documents"]:
        print(f"  - {document}")

    print(
        "\nনোট: ফি ও বয়সভিত্তিক নিয়ম assignment-এর local database "
        "থেকে নেওয়া। আবেদন করার আগে সরকারি তথ্য যাচাই করুন।"
    )


def print_final_report(applicant, database=None, fee_data=None, fee_source=None):
    """Compatibility function used by src/main.py."""
    report = build_report(
        applicant,
        database=database,
        fee_data=fee_data,
        fee_source=fee_source,
    )
    print_report(report)


if __name__ == "__main__":
    print("=== Local Fallback Mode (No LLM Required) ===")

    applicant = {
        "age": input("Age: ").strip(),
        "profession": input("Profession: ").strip(),
        "delivery_speed": input(
            "Delivery (regular/express/super_express): "
        ).strip().lower(),
        "pages": input("Pages (48/64): ").strip(),
        "requested_validity_years": input(
            "Validity (5/10): "
        ).strip(),
        "has_nid": input("Has NID? (yes/no): ").strip().lower(),
    }

    try:
        print_final_report(applicant)
    except (ValueError, KeyError, FileNotFoundError) as error:
        print(f"Invalid input or missing database entry: {error}")
