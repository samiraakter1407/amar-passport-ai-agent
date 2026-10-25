# src/main.py

import json
import sys
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path

from crewai import Crew, Process

from src.agents import create_agents
from src.tasks import create_tasks
from src.passport_sources import get_fees
from fallback_report import print_final_report


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "passport_data.json"


def load_database():
    """Load local passport reference data."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Passport database not found: {DATABASE_PATH}"
        )

    with DATABASE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_applicant_input():
    """Collect passport applicant details."""
    print("\n=== Amar Passport AI Agent ===")
    print("Enter the applicant details below.\n")

    while True:
        try:
            age = int(input("Age: ").strip())
            if age <= 0:
                print("Age must be a positive number.")
                continue
            break
        except ValueError:
            print("Please enter a valid age.")

    profession_options = {"private", "government", "student", "other"}
    while True:
        profession = input(
            "Profession (private/government/student/other): "
        ).strip().lower()

        if profession in profession_options:
            break

        print("Please choose private, government, student, or other.")

    delivery_options = {"regular", "express", "super_express"}
    while True:
        delivery_speed = input(
            "Delivery (regular/express/super_express): "
        ).strip().lower()

        if delivery_speed in delivery_options:
            break

        print("Please choose regular, express, or super_express.")

    while True:
        pages = input("Passport pages (48 or 64): ").strip()
        if pages in {"48", "64"}:
            break
        print("Please enter 48 or 64.")

    while True:
        validity = input("Requested validity (5 or 10 years): ").strip()
        if validity in {"5", "10"}:
            break
        print("Please enter 5 or 10.")

    while True:
        has_nid = input("Does the applicant have an NID? (yes/no): ").strip().lower()
        if has_nid in {"yes", "no"}:
            break
        print("Please enter yes or no.")

    location = input("Location: ").strip()

    return {
        "age": age,
        "profession": profession,
        "delivery_speed": delivery_speed,
        "pages": pages,
        "requested_validity_years": int(validity),
        "has_nid": has_nid,
        "location": location or "Not provided",
    }


def main():
    database = load_database()
    applicant = get_applicant_input()

    # Fetch the fee data, with fallback handled by passport_sources.py.
    fee_data, fee_source = get_fees()

    # Give the agents both the applicant details and reference data.
    applicant["local_reference_data"] = database
    applicant["fee_reference_data"] = fee_data
    applicant["fee_source"] = fee_source

    print(f"\nFee data source selected: {fee_source}")
    print("\nRunning passport readiness assessment...\n")

    agents = create_agents()
    tasks = create_tasks(applicant)

    # Keep verbose output enabled, as required by the project.
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    # Capture CrewAI output temporarily so it cannot corrupt the final table.
    crew_logs = StringIO()

    try:
        with redirect_stdout(crew_logs), redirect_stderr(crew_logs):
            crew.kickoff()
    except Exception as exc:
        print("\nCrewAI execution failed.")
        print(f"Error: {exc}")
        print("\nCaptured execution logs:\n")
        print(crew_logs.getvalue())
        raise

    # Display the captured verbose logs first.
    print(crew_logs.getvalue())

    # Print the report after CrewAI has finished logging.
    print("\n" + "=" * 70)
    print("FINAL APPLICANT REPORT")
    print("=" * 70 + "\n")

    print_final_report(
        applicant=applicant,
        database=database,
        fee_data=fee_data,
        fee_source=fee_source,
    )

    sys.stdout.flush()


if __name__ == "__main__":
    main()