from crewai import Task

from src.agents import (
    create_policy_guardian,
    create_fee_calculator,
    create_document_architect,
)

# Create our three specialized agents.
policy_guardian = create_policy_guardian()
fee_calculator = create_fee_calculator()
document_architect = create_document_architect()


def create_tasks(applicant):
    """Create tasks using the applicant's profile."""

    policy_task = Task(
        description=(
            "Assess this Bangladesh e-passport applicant's eligibility.\n"
            f"Applicant profile: {applicant}\n\n"
            "Determine the permitted passport validity, acceptable "
            "identification, and any age-related restrictions. Use the "
            "provided local passport database as provisional assignment "
            "data. If the requested validity conflicts with the applicant's "
            "age, explicitly flag the conflict and do not silently approve it. "
            "Do not invent official rules."
        ),
        expected_output=(
            "A structured eligibility assessment containing the applicant's "
            "age, eligibility status, permitted validity, identification "
            "requirements, and any warnings or unresolved policy checks."
        ),
        agent=policy_guardian,
    )

    fee_task = Task(
        description=(
            "Calculate the passport fee for this applicant.\n"
            f"Applicant profile: {applicant}\n\n"
            "Use the Policy Guardian's task output in your context. "
            "Select the fee using the requested page count, permitted "
            "validity, and delivery speed. Use the provided local fee "
            "database values. Treat the listed amounts as already inclusive "
            "of VAT unless the supplied data explicitly states otherwise. "
            "Never add VAT twice. If eligibility is flagged or required "
            "inputs are missing, explain that the fee needs confirmation."
        ),
        expected_output=(
            "Page count, validity, delivery type, fee in BDT, VAT treatment, "
            "and any fee or eligibility warnings."
        ),
        agent=fee_calculator,
        context=[policy_task],
    )

    document_task = Task(
        description=(
            "Generate a customized document checklist for the applicant.\n"
            f"Applicant profile: {applicant}\n\n"
            "Use the Policy Guardian's eligibility assessment and the "
            "local document database. Consider age, profession, NID or "
            "birth registration, and any declared name changes. Identify "
            "missing information and label unverified requirements clearly."
        ),
        expected_output=(
            "A checklist of required, conditional, and unverified documents, "
            "with a brief explanation for each."
        ),
        agent=document_architect,
        context=[policy_task],
    )

    return policy_task, fee_task, document_task