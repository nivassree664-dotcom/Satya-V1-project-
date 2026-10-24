import re
import time
from urllib.parse import urlparse
import requests
import streamlit as st
from bs4 import BeautifulSoup

APP_TITLE = "Project SATYA — Evidence Checker"
USER_AGENT = "ProjectSATYA/0.1 (educational prototype)"

st.set_page_config(page_title=APP_TITLE, page_icon="🔎", layout="wide")

st.title("🔎 Project SATYA")
st.caption("Evidence-first fact-checking prototype • V1 • Free starter build")
st.warning(
    "Prototype note: SATYA V1 collects web search snippets and organizes evidence. "
    "It does not independently prove a claim true or false. Treat every result as a lead "
    "and verify important claims using the original source."
)

with st.sidebar:
    st.header("About this build")
    st.write("**Cost:** ₹0 software/API fees for this prototype")
    st.write("**Runs on:** Streamlit Community Cloud or local Python")
    st.write("**AI model API:** Not required")
    st.write("**Languages:** Search works best when the query is written clearly; multilingual results vary.")
    st.divider()
    st.caption("Never enter passwords, private records, or other sensitive information.")

def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()

def domain_of(url):
    try:
        return urlparse(url).netloc.lower().removeprefix("www.")
    except Exception:
        return ""

def search_duckduckgo(query, max_results=8):
    """Fetch public DuckDuckGo HTML search results. Search markup can change over time."""
    endpoint = "https://html.duckduckgo.com/html/"
    response = requests.post(
        endpoint,
        data={"q": query},
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for item in soup.select(".result"):
        link = item.select_one(".result__a")
        snippet = item.select_one(".result__snippet")
        if not link:
            continue
        href = link.get("href", "").strip()
        title = clean_text(link.get_text(" ", strip=True))
        summary = clean_text(snippet.get_text(" ", strip=True)) if snippet else ""
        if href.startswith("http") and title:
            results.append({
                "title": title,
                "url": href,
                "snippet": summary,
                "domain": domain_of(href),
            })
        if len(results) >= max_results:
            break
    return results

def search_wikipedia(query, max_results=4):
    """Use the public MediaWiki search API for a second evidence discovery route."""
    endpoint = "https://en.wikipedia.org/w/api.php"
    response = requests.get(
        endpoint,
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": max_results,
        },
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    results = []
    for item in data.get("query", {}).get("search", []):
        title = clean_text(item.get("title", ""))
        page_url = "https://en.wikipedia.org/wiki/" + requests.utils.quote(title.replace(" ", "_"))
        snippet_html = item.get("snippet", "")
        snippet = clean_text(BeautifulSoup(snippet_html, "html.parser").get_text(" ", strip=True))
        results.append({
            "title": title,
            "url": page_url,
            "snippet": snippet,
            "domain": "en.wikipedia.org",
        })
    return results

def basic_overlap(query, result):
    """Transparent lexical overlap indicator; not a truth score."""
    terms = {
        t.lower() for t in re.findall(r"[A-Za-z0-9\u0C00-\u0C7F]{3,}", query)
        if t.lower() not in {"the", "and", "for", "that", "this", "with", "from", "was", "are", "has", "have"}
    }
    body = (result.get("title", "") + " " + result.get("snippet", "")).lower()
    if not terms:
        return 0
    return round(sum(1 for term in terms if term in body) / len(terms), 2)

def source_quality_hint(domain):
    """Heuristic hint only; domain names do not guarantee accuracy."""
    trusted_suffixes = (".gov", ".gov.in", ".nic.in", ".edu", ".ac.in")
    if domain.endswith(trusted_suffixes):
        return "Official/academic domain hint — still verify the page"
    if domain in {"en.wikipedia.org"}:
        return "General reference source — follow its citations"
    return "Independent source candidate — assess author, date, and citations"

with st.form("claim_form"):
    claim = st.text_area(
        "What claim do you want to check?",
        placeholder="Example: A specific public policy was announced in 2025.",
        height=100,
    )
    language = st.selectbox("Preferred search language", ["English", "తెలుగు", "Hindi", "Other / mixed"])
    extra_context = st.text_input(
        "Optional context (place, date, person, etc.)",
        placeholder="e.g., India, October 2026",
    )
    submitted = st.form_submit_button("Search for evidence", type="primary", use_container_width=True)

if submitted:
    if len(claim.strip()) < 8:
        st.error("Please enter a more specific claim (at least 8 characters).")
        st.stop()

    query = claim.strip()
    if extra_context.strip():
        query += " " + extra_context.strip()

    st.subheader("Investigation")
    st.write("**Claim:**", claim.strip())
    st.write("**Search query:**", query)
    results = []
    errors = []

    with st.spinner("Searching public web results…"):
        try:
            results.extend(search_duckduckgo(query, max_results=8))
        except Exception as exc:
            errors.append("Web search was unavailable: " + str(exc))
        try:
            # Wikipedia's public API is a separate discovery route; English-language results only.
            results.extend(search_wikipedia(query, max_results=4))
        except Exception as exc:
            errors.append("Wikipedia search was unavailable: " + str(exc))

    # De-duplicate by URL while preserving order.
    unique = []
    seen = set()
    for result in results:
        if result["url"] not in seen:
            result["overlap"] = basic_overlap(claim, result)
            result["quality_hint"] = source_quality_hint(result["domain"])
            unique.append(result)
            seen.add(result["url"])

    if errors:
        for err in errors:
            st.info(err)

    if not unique:
        st.error("No results were retrieved. Check your internet connection or try a shorter, clearer query.")
        st.stop()

    domains = {r["domain"] for r in unique if r["domain"]}
    st.metric("Sources discovered", len(unique))
    st.metric("Different domains", len(domains))
    st.caption("Different domains do not automatically mean independent evidence; sites may copy one another.")

    st.subheader("Evidence leads")
    for idx, item in enumerate(unique, start=1):
        with st.expander(f"{idx}. {item['title']}  ·  {item['domain']}", expanded=(idx <= 3)):
            st.write(item["snippet"] or "No search snippet was provided. Open the original page to inspect it.")
            st.markdown(f"[Open original source]({item['url']})")
            st.caption(item["quality_hint"])
            st.caption(f"Keyword overlap indicator: {item['overlap']:.0%} — this measures wording overlap only, not truth or reliability.")

    st.subheader("SATYA preliminary assessment")
    st.info(
        "**Status: INSUFFICIENT EVIDENCE — human review required.**\n\n"
        "This version does not assign a true/false verdict from search snippets. "
        "Open the original pages, check publication dates, look for primary documents, "
        "and search deliberately for evidence against the claim."
    )

    st.subheader("Review checklist")
    checklist = [
        "At least one primary or official source was checked",
        "Publication date and relevant time period were checked",
        "At least two genuinely independent sources were compared",
        "Evidence against the claim was actively searched for",
        "The source text actually supports the exact claim (not just a related topic)",
    ]
    for item in checklist:
        st.checkbox(item, key="review_" + str(abs(hash(item + claim))))

    report = [
        "PROJECT SATYA — PRELIMINARY EVIDENCE REPORT",
        "=" * 48,
        f"Claim: {claim.strip()}",
        f"Context: {extra_context.strip() or 'Not provided'}",
        f"Search language preference: {language}",
        "Preliminary status: INSUFFICIENT EVIDENCE — human review required",
        "",
        "Important: This is an evidence-discovery prototype, not a definitive fact-check.",
        "",
        "Sources:",
    ]
    for idx, item in enumerate(unique, start=1):
        report += [
            f"{idx}. {item['title']}",
            f"   URL: {item['url']}",
            f"   Domain: {item['domain']}",
            f"   Snippet: {item['snippet']}",
            f"   Keyword overlap (not a truth score): {item['overlap']:.0%}",
            "",
        ]
    report += [
        "Manual checks recommended:",
        "- Inspect original source pages and dates.",
        "- Find primary/official documents where possible.",
        "- Compare genuinely independent sources.",
        "- Search for counterevidence.",
        "- Do not treat source count or keyword overlap as proof.",
    ]
    st.download_button(
        "Download preliminary report (.txt)",
        data="\n".join(report),
        file_name="satya_preliminary_report.txt",
        mime="text/plain",
        use_container_width=True,
    )

st.divider()
st.caption("Project SATYA V1 • Open-source starter prototype • Not for high-stakes decisions.")
