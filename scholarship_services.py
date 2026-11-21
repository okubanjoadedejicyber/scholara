
import os
import re
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# GROQ
# --------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = None

if GROQ_API_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print("Groq initialization failed:", e)


# --------------------------------------------------
# SCHOLARSHIP SOURCES
# --------------------------------------------------

SCHOLARSHIP_SOURCES = [
    {
        "name": "MTN Nigeria",
        "url": "https://www.mtn.ng/",
        "country": "Nigeria",
    },
    {
        "name": "Federal Ministry of Education",
        "url": "https://education.gov.ng/",
        "country": "Nigeria",
    },
    {
        "name": "TotalEnergies Nigeria",
        "url": "https://csr-ngscholarship.totalenergies.com/scholarships",
        "country": "Nigeria",
    },
    {
        "name": "PTDF",
        "url": "https://scholarship.ptdf.gov.ng/guidelines",
        "country": "Nigeria",
    },
]


# --------------------------------------------------
# SCRAPER KEYWORDS
# --------------------------------------------------

KEYWORDS = [
    "scholarship",
    "scholarships",
    "bursary",
    "bursaries",
    "grant",
    "grants",
    "fellowship",
    "fellowships",
    "funding",
    "student award",
    "educational funding",
]


# --------------------------------------------------
# HTTP HEADERS
# --------------------------------------------------

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/130.0 Safari/537.36"
    )
}


# --------------------------------------------------
# SCRAPE ONE WEBSITE
# --------------------------------------------------

def scrape_website(source):

    results = []

    try:

        response = requests.get(
            source["url"],
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for unwanted in soup.select(
            "script, style, nav, footer, header, noscript, iframe"
        ):
            unwanted.decompose()

        links = soup.find_all("a", href=True)

        for link in links:

            title = link.get_text(" ", strip=True)

            href = link.get("href", "").strip()

            if not title or not href:
                continue

            if len(title) < 5:
                continue

            if not any(
                keyword in title.lower()
                for keyword in KEYWORDS
            ):
                continue

            absolute_url = urljoin(source["url"], href)

            parsed = urlparse(absolute_url)

            if parsed.scheme not in ("http", "https"):
                continue

            results.append({
                "title": title[:250],
                "url": absolute_url,
                "source": source["name"],
                "country": source["country"],
                "description": (
                    "Discovered from the source website. "
                    "Review the official page for details."
                )
            })

    except requests.RequestException as e:

        print(f"Scraping error for {source['name']}: {e}")

    except Exception as e:

        print(f"Unexpected scraper error: {e}")

    return results


# --------------------------------------------------
# DISCOVER SCHOLARSHIP LINKS
# --------------------------------------------------

def discover_scholarships():

    discovered = []

    seen_urls = set()

    for source in SCHOLARSHIP_SOURCES:

        results = scrape_website(source)

        for result in results:

            url = result["url"]

            if url not in seen_urls:

                seen_urls.add(url)

                discovered.append(result)

        # Avoid sending requests too rapidly
        time.sleep(1)

    return discovered


# --------------------------------------------------
# TEXT NORMALIZATION
# --------------------------------------------------

def normalize_text(value):

    if value is None:
        return ""

    return str(value).strip().lower()


def profile_value(student, key):

    if isinstance(student, dict):
        return student.get(key)

    return getattr(student, key, None)


# --------------------------------------------------
# STUDENT PROFILE EXTRACTION
# --------------------------------------------------

def get_student_data(student):

    if hasattr(student, "profile") and student.profile:

        profile = student.profile

    elif isinstance(student, dict):

        profile = student.get("profile", student)

    else:

        profile = None

    def get_value(key):

        if isinstance(profile, dict):
            return profile.get(key)

        if profile:
            return getattr(profile, key, None)

        return None

    return {
        "university": get_value("university"),
        "course": get_value("course"),
        "level": get_value("level"),
        "country": get_value("country"),
        "state": get_value("state"),
        "cgpa": get_value("cgpa"),
        "interests": get_value("interests"),
    }


# --------------------------------------------------
# SCHOLARSHIP MATCHING ENGINE
# --------------------------------------------------

def match_scholarship(student, scholarship):

    profile = get_student_data(student)

    score = 0

    reasons = []

    missing = []

    eligibility = normalize_text(
        getattr(scholarship, "eligibility", "")
    )

    description = normalize_text(
        getattr(scholarship, "description", "")
    )

    title = normalize_text(
        getattr(scholarship, "title", "")
    )

    scholarship_country = normalize_text(
        getattr(scholarship, "country", "")
    )

    country = normalize_text(profile.get("country"))

    level = normalize_text(profile.get("level"))

    course = normalize_text(profile.get("course"))

    interests = normalize_text(profile.get("interests"))

    cgpa = profile.get("cgpa")

    combined_text = " ".join([
        title,
        eligibility,
        description
    ])

    # --------------------------------------------------
    # COUNTRY MATCH
    # --------------------------------------------------

    if country:

        if country in scholarship_country:

            score += 20

            reasons.append("Country preference matches.")

        elif country in combined_text:

            score += 20

            reasons.append(
                "Student country appears in the scholarship information."
            )

        elif "international" in combined_text:

            score += 15

            reasons.append(
                "The scholarship mentions international applicants."
            )

        else:

            missing.append(
                "Country eligibility needs verification."
            )

    # --------------------------------------------------
    # EDUCATION LEVEL MATCH
    # --------------------------------------------------

    level_aliases = {
        "100": [
            "undergraduate",
            "undergrad",
            "bachelor",
            "bachelors",
            "first degree",
            "university student",
        ],
        "200": [
            "undergraduate",
            "undergrad",
            "bachelor",
            "bachelors",
            "first degree",
            "university student",
        ],
        "300": [
            "undergraduate",
            "undergrad",
            "bachelor",
            "bachelors",
            "first degree",
            "university student",
        ],
        "400": [
            "undergraduate",
            "undergrad",
            "bachelor",
            "bachelors",
            "first degree",
            "university student",
        ],
        "500": [
            "undergraduate",
            "undergrad",
            "bachelor",
            "bachelors",
            "first degree",
            "university student",
        ],
        "undergraduate": [
            "undergraduate",
            "undergrad",
            "bachelor",
            "bachelors",
            "first degree",
            "university student",
        ],
        "masters": [
            "masters",
            "master's",
            "master",
            "postgraduate",
            "post-graduate",
        ],
        "master": [
            "masters",
            "master's",
            "master",
            "postgraduate",
            "post-graduate",
        ],
        "postgraduate": [
            "masters",
            "master's",
            "master",
            "postgraduate",
            "post-graduate",
        ],
        "phd": [
            "phd",
            "doctoral",
            "doctorate",
        ],
    }

    if level:

        aliases = level_aliases.get(level, [level])

        if any(alias in combined_text for alias in aliases):

            score += 30

            reasons.append(
                "Education level appears to match."
            )

        else:

            missing.append(
                "Education level eligibility needs verification."
            )

    # --------------------------------------------------
    # COURSE MATCH
    # --------------------------------------------------

    if course:

        course_words = [
            word for word in re.findall(
                r"[a-zA-Z]+",
                course
            )
            if len(word) > 3
        ]

        matched_course_words = [
            word for word in course_words
            if word in combined_text
        ]

        if matched_course_words:

            score += 25

            reasons.append(
                "Your course or related terms appear in the scholarship information."
            )

        else:

            missing.append(
                "Course eligibility needs verification."
            )

    # --------------------------------------------------
    # INTEREST MATCH
    # --------------------------------------------------

    if interests:

        interest_words = [
            word for word in re.findall(
                r"[a-zA-Z]+",
                interests
            )
            if len(word) > 3
        ]

        matched_interests = [
            word for word in interest_words
            if word in combined_text
        ]

        if matched_interests:

            score += 15

            reasons.append(
                "Some of your interests match the scholarship information."
            )

    # --------------------------------------------------
    # GPA
    # --------------------------------------------------

    if cgpa is not None:

        try:

            cgpa_value = float(cgpa)

            gpa_matches = re.findall(
                r"(?:minimum|min\.?|at least)\s*"
                r"(?:gpa|cgpa)?\s*"
                r"([0-9]+(?:\.[0-9]+)?)",
                combined_text
            )

            if gpa_matches:

                minimum_gpa = max(
                    float(value)
                    for value in gpa_matches
                )

                if cgpa_value >= minimum_gpa:

                    score += 10

                    reasons.append(
                        "Your CGPA meets a detected minimum requirement."
                    )

                else:

                    missing.append(
                        "Your CGPA may be below a detected requirement."
                    )

            else:

                missing.append(
                    "No reliable GPA requirement was detected."
                )

        except (ValueError, TypeError):

            missing.append(
                "CGPA could not be evaluated."
            )

    # --------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------

    score = min(score, 100)

    return {
        "match_score": score,
        "reasons": reasons,
        "missing": missing,
        "profile": profile,
    }


# --------------------------------------------------
# AI SCHOLARSHIP ANALYSIS
# --------------------------------------------------

def analyse_with_ai(scholarship_text, student):

    if not groq_client:

        return (
            "AI analysis is currently unavailable. "
            "Check your GROQ_API_KEY configuration."
        )

    profile = get_student_data(student)

    student_info = f"""
Student Information:

University: {profile.get('university') or 'Not provided'}
Course: {profile.get('course') or 'Not provided'}
Level: {profile.get('level') or 'Not provided'}
Country: {profile.get('country') or 'Not provided'}
State: {profile.get('state') or 'Not provided'}
CGPA: {profile.get('cgpa') or 'Not provided'}
Interests: {profile.get('interests') or 'Not provided'}
"""

    prompt = f"""
You are Scholara's scholarship analysis assistant.

Analyze the scholarship using only the provided information.

{student_info}

SCHOLARSHIP INFORMATION:

{scholarship_text[:12000]}

Provide the analysis using these headings:

## Overview
Explain what the scholarship is.

## Eligibility Requirements
List the stated requirements.

## Student Eligibility
Explain which requirements the student appears to meet,
which are uncertain, and which may not be met.

## Missing Information
Identify information the student still needs to verify.

## Application Advice
Give practical steps for applying.

## Important Notice
Explain that this analysis is not an official eligibility
confirmation.

Rules:

- Do not invent scholarship deadlines.
- Do not invent funding amounts.
- Do not invent requirements.
- Do not claim official eligibility confirmation.
- Clearly label uncertain information.
- If a requirement is not stated, say it is not stated.
- Use simple, clear language.
"""

    try:

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful scholarship research "
                        "and student application assistant."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )

        return response.choices[0].message.content

    except Exception as e:

        print("Groq analysis error:", e)

        return (
            "The AI analysis could not be completed. "
            "Please try again later."
        )
