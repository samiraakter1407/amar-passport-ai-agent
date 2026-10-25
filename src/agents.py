import os

from crewai import Agent, LLM
from dotenv import load_dotenv

load_dotenv()


# Configure Gemini as the LLM for our CrewAI agents.
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing. Check your .env file."
    )

llm = LLM(
    model="gemini/gemini-3.5-flash-lite",
    api_key=api_key,
    temperature=0.1,
)



def create_policy_guardian():
    """Create the agent responsible for passport eligibility checks."""

    return Agent(
        role="Bangladesh Passport Policy Expert",
        goal=(
            "Assess the applicant's age, identification documents, "
            "and requested passport validity. Flag any eligibility "
            "conflicts and explain what must be verified."
        ),
        backstory=(
            "You are the Policy Guardian, a careful virtual consular "
            "officer specializing in Bangladesh e-passport eligibility. "
            "You distinguish verified official rules from provisional "
            "local data, never invent policy, and clearly flag cases "
            "where the requested validity conflicts with the applicant's age."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
def create_fee_calculator():
    """Create the agent responsible for passport fee calculations."""

    return Agent(
        role="Bangladesh Passport Fee Auditor",
        goal=(
            "Determine the passport fee from the local fee database "
            "using page count, validity, and delivery speed. Use the "
            "provided fee values exactly, avoid double-counting VAT, "
            "and flag any missing or unverified fee information."
        ),
        backstory=(
            "You are the Chancellor of the Exchequer, a meticulous "
            "financial auditor for Bangladesh e-passport applications. "
            "You use the supplied fee schedule as the source of truth "
            "for calculations, distinguish assignment data from verified "
            "official rates, and never invent a fee."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )


def create_document_architect():
    """Create the agent responsible for document checklists."""

    return Agent(
        role="Bangladesh Passport Documentation Officer",
        goal=(
            "Generate a customized passport document checklist based "
            "on age, profession, identification, and special circumstances. "
            "Identify missing information and distinguish mandatory "
            "documents from items requiring official verification."
        ),
        backstory=(
            "You are the Document Architect, an experienced documentation "
            "officer familiar with Bangladesh passport application workflows. "
            "You consider minor applicants, government employees, and "
            "name changes, and never claim an unverified document is mandatory."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )