
import json
import sys
from pathlib import Path

from crewai import Crew, Process

from src.tasks import create_tasks
from src.passport_sources import get_fees
from fallback_report import build_report, print_report


def load_passport_database():
    database_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "passport_data.json"
    )

    with database_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def collect_applicant_profile():
    print("\n=== Amar Passport AI Agent ===")
    print("Enter the applicant details below.\n")

    while True:
        try:
            age = int(input("Age: ").strip())
            if age > 0:
                break
            print("Age must be greater than zero.")
        except ValueError:
            print("Please enter age as a whole number.")

    valid_professions = ["private", "government", "student", "other"]
    while True:
        profession = input(
            "Profession (private/government/student/other): "
        ).strip().lower()

        if profession in valid_professions:
            break
        print("Please enter one of the listed professions.")

    valid_deliveries = ["regular", "express", "super_express"]
    while True:
        delivery_speed = input(
            "Delivery (regular/express/super_express): "
        ).strip().lower()

        if delivery_speed in valid_deliveries:
            break
        print("Please enter regular, express, or super_express.")

    while True:
        pages = input("Passport pages (48 or 64): ").strip()
        if pages in ["48", "64"]:
            break
        print("Passport pages must be 48 or 64.")

    while True:
        try:
            validity = int(
                input("Requested validity (5 or 10 years): ").strip()
            )
            if validity in [5, 10]:
                break
            print("Validity must be 5 or 10 years.")
        except ValueError:
            print("Please enter 5 or 10.")

    while True:
        has_nid = input(
            "Does the applicant have an NID? (yes/no): "
        ).strip().lower()

        if has_nid in ["yes", "no"]:
            break
        print("Please enter yes or no.")

    location = input("Location: ").strip()

    return {
        "age": age,
        "profession": profession,
        "delivery_speed": delivery_speed,
        "pages": pages,
        "requested_validity_years": validity,
        "has_nid": has_nid,
        "location": location,
    }


def print_markdown_table(rows):
    print("\n# Amar Passport Readiness Report")
    print("\n| Field | Result |")
    print("|---|---|")

    for field, value in rows:
        # Keep values on one Markdown table row.
        value = str(value).replace("|", "\\|").replace("\n", "<br>")
        print(f"| {field} | {value} |")


def print_final_report(applicant, database, fee_data, fee_source):
    age = applicant["age"]
    pages = applicant["pages"]
    validity = applicant["requested_validity_years"]
    delivery = applicant["delivery_speed"]
    profession = applicant["profession"]
    has_nid = applicant["has_nid"]

    rules = database.get("eligibility_rules", {})
    warnings = []

    if age < 18:
        max_validity = rules.get("under_18", {}).get(
            "max_validity_years", 5
        )
        eligibility = (
            "CONFLICT: requested validity exceeds the provisional "
            "age-based limit"
            if validity > max_validity
            else "No age-validity conflict detected under provisional rules"
        )
        if validity > max_validity:
            warnings.append(
                f"Applicants under 18: provisional maximum validity "
                f"is {max_validity} years."
            )
        identification = (
            "Online Birth Registration Certificate (English) and "
            "parents' NID; verify official requirements"
        )

    elif age > 65:
        max_validity = rules.get("over_65", {}).get(
            "max_validity_years", 5
        )
        eligibility = (
            "CONFLICT: requested validity exceeds the provisional "
            "age-based limit"
            if validity > max_validity
            else "Requires official verification for applicants over 65"
        )
        warnings.append(
            "Verify age-related eligibility directly with the official "
            "e-Passport authority."
        )
        if validity > max_validity:
            warnings.append(
                f"Provisional local rule lists a maximum of "
                f"{max_validity} years for applicants over 65."
            )
        identification = (
            "Check applicable NID or birth-registration requirements"
        )

    else:
        eligibility = (
            "No age-validity conflict detected under provisional rules"
        )
        identification = (
            "NID available"
            if has_nid == "yes"
            else "NID not confirmed; verify acceptable identification"
        )
        if has_nid == "no":
            warnings.append(
                "Applicant has no NID recorded; confirm acceptable "
                "identification before applying."
            )

    if profession == "government":
        warnings.append(
            "Government employees should verify applicable NOC/PRL "
            "and delivery-fee conditions."
        )

    fee = None
    try:
        fee = fee_data[
            f"{pages}_pages"
        ][
            f"{validity}_years"
        ][delivery]
    except (KeyError, TypeError):
        warnings.append(
            "A matching fee could not be found in the selected fee data."
        )

    conflict = "CONFLICT:" in eligibility
    if conflict or fee is None:
        fee_display = "Not confirmed — resolve eligibility or fee issue"
    else:
        fee_display = f"{fee:,} BDT"

    try:
        reference_report = build_report(applicant)
        documents = reference_report.get("documents", [])
        warnings.extend(reference_report.get("warnings", []))
    except (OSError, KeyError, ValueError, TypeError):
        documents = []

    documents = sorted(set(documents))
    document_display = "; ".join(documents) if documents else (
        "Confirm required documents using official instructions"
    )

    rows = [
        ("Applicant Age", age),
        ("Profession", profession.title()),
        ("Location", applicant["location"] or "Not specified"),
        ("Eligibility Assessment", eligibility),
        ("Requested Passport", f"{pages} pages, {validity}-year validity"),
        ("Delivery Speed", delivery.replace("_", " ").title()),
        ("Identification", identification),
        ("Estimated Fee", fee_display),
        ("Fee Data Source", fee_source),
        ("VAT", "Included in listed fee where specified by the fee schedule"),
        ("Required Documents", document_display),
        (
            "Warnings",
            "; ".join(dict.fromkeys(warnings))
            if warnings
            else "No additional warnings generated",
        ),
    ]

    print_markdown_table(rows)

    print("\n## Bangla Summary")
    print(f"- বয়স: {age} বছর")
    print(f"- পেশা: {profession}")
    print(f"- পাসপোর্ট: {pages} পৃষ্ঠা")
    print(f"- চাওয়া মেয়াদ: {validity} বছর")
    print(f"- ডেলিভারি: {delivery.replace('_', ' ')}")
    print(f"- যোগ্যতা: {eligibility}")
    print(f"- আনুমানিক ফি: {fee_display}")
    print(f"- ফি-এর উৎস: {fee_source}")
    print(f"- প্রয়োজনীয় কাগজপত্র: {document_display}")

    if warnings:
        print("\nসতর্কতা:")
        for warning in dict.fromkeys(warnings):
            print(f"- {warning}")

    print(
        "\nNote: This is an assignment assessment using provisional "
        "reference data. Verify current eligibility, documents, and fees "
        "with the official Bangladesh e-Passport portal before payment."
    )


def main():
    try:
        database = load_passport_database()
    except (OSError, json.JSONDecodeError) as error:
        print(f"Could not load passport database: {error}")
        return

    try:
        fee_data, fee_source = get_fees()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Fee retrieval failed: {error}")
        fee_data = database.get("fees_2026")
        fee_source = "Local assignment database"

    if not fee_data:
        fee_data = database.get("fees_2026")
        fee_source = "Local assignment database"

    if not fee_data:
        print("No fee data available from API or local database.")
        return

    database["fees_2026"] = fee_data
    applicant = collect_applicant_profile()

    applicant["local_reference_data"] = database
    applicant["fee_reference_data"] = fee_data
    applicant["fee_source"] = fee_source

    print(f"\nFee data source selected: {fee_source}")
    print("\nRunning passport readiness assessment...\n")

    policy_task, fee_task, document_task = create_tasks(applicant)

    crew = Crew(
        agents=[
            policy_task.agent,
            fee_task.agent,
            document_task.agent,
        ],
        tasks=[policy_task, fee_task, document_task],
        process=Process.sequential,
        verbose=True,
    )

    try:
        crew.kickoff()

        # Flush verbose logs before displaying the final report.
        sys.stdout.flush()

        print_final_report(
            applicant=applicant,
            database=database,
            fee_data=fee_data,
            fee_source=fee_source,
        )

    except Exception as error:
        print(f"\nCrew execution failed: {error}")
        print("Switching to local fallback report.")

        try:
            fallback = build_report(applicant)
            print_report(fallback)
        except Exception as fallback_error:
            print(f"Fallback report also failed: {fallback_error}")


if __name__ == "__main__":
    main()
