# Project SATYA V1 — Evidence Checker

A free starter prototype for collecting web-search evidence and organizing a cautious preliminary report.

## What it does
- Accepts a claim in the browser.
- Searches DuckDuckGo HTML results and the English Wikipedia search API.
- Displays source titles, URLs, snippets, domain hints, and a **keyword overlap indicator**.
- Always abstains from declaring a claim true/false based only on snippets.
- Lets the user download a preliminary report.

## What it does NOT do
- It is not a full AI fact-checker and does not prove claims.
- Keyword overlap is not a truth score.
- A government, academic, or familiar domain is not automatically correct.
- It does not yet verify the contents of every linked page, assess source independence, or reliably handle every language.
- Search providers can change page markup or rate-limit requests.

## Free deployment from an Android phone
You can deploy using a mobile browser. A GitHub account and Streamlit Community Cloud account may be required; service terms/availability can change.

1. Download and extract `project_satya_v1.zip`.
2. Open GitHub in your phone browser and sign in/create an account.
3. Create a new **public repository** named `project-satya-v1`.
4. Upload `app.py`, `requirements.txt`, and `README.md` to the repository root.
5. Open Streamlit Community Cloud: https://share.streamlit.io/
6. Sign in with GitHub and choose **Create app**.
7. Select your repository, branch `main`, and main file path `app.py`.
8. Deploy. Wait for dependencies to install.
9. Open the generated app URL and test with a public, non-sensitive claim.

Do not upload secrets, API keys, passwords, or private data to the repository. This V1 does not need an API key.

## Run locally (optional)
Requires Python 3.10+:
```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## First tests
Try:
- A well-documented historical fact.
- A recent claim with a date and country.
- A claim phrased in Telugu.
- A vague claim; it should still abstain.
- A claim with few search results; it should show a useful error/limitation.

## Roadmap
1. V1: evidence discovery + abstention.
2. V1.1: better multilingual search, date extraction, source deduplication.
3. V2: claim decomposition, primary-source preference, counterevidence search, structured evidence ledger.
4. V3: optional free-tier model integration (only after checking provider limits and privacy implications), calibrated verdicts, benchmark suite, audit logs.

## Safety and accuracy
Do not use this prototype as the sole basis for medical, legal, financial, emergency, or other high-impact decisions. Always inspect the original source.
