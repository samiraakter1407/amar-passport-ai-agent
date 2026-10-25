
import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


API_URL = (
    "https://epassport.gov.bd/api/v1/landing/instruction/passportFees"
)

LOCAL_DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "passport_data.json"
)

EXPECTED_DELIVERY_TYPES = (
    "regular",
    "express",
    "super_express",
)


def fetch_official_fees():
    """Fetch domestic passport fees from the official e-passport API."""

    response = requests.get(
        API_URL,
        headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0",
        },
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()

    english_content = (
        payload.get("content", {})
        .get("content", {})
        .get("eng", {})
        .get("data", "")
    )

    if not english_content:
        raise ValueError(
            "The official API returned no English fee content."
        )

    soup = BeautifulSoup(english_content, "html.parser")

    # Extract domestic Bangladesh fees from list items.
    # Overseas fees are in USD and are intentionally excluded.
    fees_found = []

    for element in soup.find_all("li"):
        text = element.get_text(" ", strip=True)

        match = re.search(
            r"^\s*(Regular|Express|Super[\s-]*Express)"
            r"\s*delivery\s*:?\s*"
            r"TK\s*([\d,]+)\s*$",
            text,
            re.IGNORECASE,
        )

        if match:
            delivery_name = re.sub(
                r"[\s-]+",
                "_",
                match.group(1).lower(),
            )

            amount = int(
                match.group(2).replace(",", "")
            )

            fees_found.append((delivery_name, amount))

    if len(fees_found) != 12:
        raise ValueError(
            "Expected 12 domestic fee entries, but found "
            f"{len(fees_found)}. Extracted: {fees_found}"
        )

    combinations = [
        ("48_pages", "5_years"),
        ("48_pages", "10_years"),
        ("64_pages", "5_years"),
        ("64_pages", "10_years"),
    ]

    fees = {}

    for index, (page_key, validity_key) in enumerate(combinations):
        start = index * 3
        section = fees_found[start:start + 3]

        delivery_names = [
            name for name, amount in section
        ]

        if delivery_names != list(EXPECTED_DELIVERY_TYPES):
            raise ValueError(
                f"Unexpected delivery fee entries for "
                f"{page_key}, {validity_key}: {section}"
            )

        fees.setdefault(page_key, {})
        fees[page_key][validity_key] = {
            name: amount for name, amount in section
        }

    return fees


def get_fees():
    """Fetch official fees, falling back to local data if needed."""

    try:
        fees = fetch_official_fees()
        return fees, "Official e-passport API"

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
    ) as error:
        print(f"Official fee fetch failed: {error}")
        print("Using the local assignment database instead.")

        with LOCAL_DATA_PATH.open(
            "r",
            encoding="utf-8",
        ) as file:
            database = json.load(file)

        return database["fees_2026"], "Local assignment database"


if __name__ == "__main__":
    try:
        fee_data, source = get_fees()

        print("\nFee source:", source)
        print(
            json.dumps(
                fee_data,
                indent=2,
                ensure_ascii=False,
            )
        )

    except (
        OSError,
        json.JSONDecodeError,
        KeyError,
    ) as error:
        print(f"Could not load fee data: {error}")
