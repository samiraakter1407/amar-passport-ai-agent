
# 🇧🇩 Amar Passport AI Agent

A multi-agent AI application that helps users assess Bangladesh e-Passport application readiness using CrewAI and Google Gemini.

The system uses specialized AI agents to review applicant eligibility, estimate passport fees, and generate a personalized document checklist. It produces a structured report in English and Bangla.

## ✨ Features

- **Policy Guardian:** Reviews applicant age, identification, and requested passport validity.
- **Fee Auditor:** Estimates passport fees using the available fee reference data.
- **Documentation Officer:** Generates a customized passport document checklist.
- **Multi-Agent Workflow:** Coordinates three specialized agents using CrewAI sequential processing.
- **Fee Data Retrieval:** Attempts to retrieve fee data through the passport source module, with local reference data available as fallback.
- **Eligibility Warnings:** Flags potential conflicts, including under-18 applicants requesting a validity period that exceeds the configured local rule.
- **Bilingual Report:** Displays the final report in English and Bangla.
- **Input Validation:** Validates age, profession, delivery speed, passport pages, validity, and NID status.


## 🎬 Project Demo

[▶️ Watch Amar Passport AI Agent Demo](./amar-passport-ai-agent-demo.mp4)


## 🛠️ Tech Stack

- Python
- CrewAI
- Google Gemini
- Python-dotenv
- JSON

## 📁 Project Structure

```text
amar-passport-ai-agent/
├── data/
│   └── passport_data.json
├── src/
│   ├── agents.py
│   ├── main.py
│   ├── passport_sources.py
│   └── tasks.py
├── fallback_report.py
├── .gitignore
├── requirements.txt
└── README.md
```

Additional utility or test scripts may also be present in the repository.

## ⚙️ Prerequisites

- Python installed
- A Google Gemini API key
- Git (optional, for cloning the repository)

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/samiraakter1407/amar-passport-ai-agent.git
cd amar-passport-ai-agent
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder with your own API key. Never commit your `.env` file or expose your API key publicly.

## ▶️ Run the Application

From the project root, run:

```bash
python -m src.main
```

Enter the requested applicant details when prompted, including:

- Age
- Profession
- Delivery speed
- Passport page count
- Requested validity
- NID availability
- Location

The application then runs the agent workflow and displays a final applicant report.

## 🤖 Agent Workflow

1. **Policy Guardian** assesses age-related eligibility and identifies potential policy conflicts.
2. **Fee Auditor** reviews the applicable fee reference data and reports the estimated cost.
3. **Documentation Officer** prepares a document checklist based on the applicant profile.
4. **Final Report** displays the applicant details, estimated fee, required documents, and warnings in English and Bangla.

The workflow uses sequential task execution, allowing later tasks to use the output of earlier tasks.

## 🧪 Example Scenario

Example input:

| Field | Example |
|---|---|
| Age | 24 |
| Profession | Private |
| Delivery | Express |
| Passport pages | 64 |
| Requested validity | 10 years |
| Has NID | Yes |
| Location | Dhaka |

The report includes an estimated fee, eligibility assessment, document checklist, and relevant warnings.

## ⚠️ Important Disclaimer

This project is an educational AI application and is not an official Bangladesh government service.

Fee amounts and eligibility rules depend on the reference data supplied with the project and information returned by the source module. They may be incomplete, provisional, or outdated. AI-generated guidance can also be inaccurate.

Always verify current fees, eligibility, and required documents through official Bangladesh e-Passport channels before applying or making payments.

## 🔮 Future Improvements

- Add automated tests for fee calculations and eligibility rules.
- Improve source validation and error handling.
- Add more comprehensive official-source verification.
- Develop a web-based user interface.
- Improve report formatting and downloadable report generation.

## 👩‍💻 Author

**Samira Akter**

GitHub: [@samiraakter1407](https://github.com/samiraakter1407)

## 📄 License

No license has been specified yet. All rights are reserved unless a license is added to this repository.

