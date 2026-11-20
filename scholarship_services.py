
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time



# 1. SCHOLARSHIP WEBSITE SOURCES

SCHOLARSHIP_SOURCES = [
    {
        "name": "MTN Nigeria",
        "url": "https://www.mtn.ng/",
        "country": "Nigeria"
    },
    {
        "name": "Federal Ministry of Education",
        "url": "https://education.gov.ng/",
        "country": "Nigeria"
    },
    {
        "name": "TotalEnergies Scholarship",
        "url": "https://csr-ngscholarship.totalenergies.com/scholarships",
        "country": "Nigeria"
    },
    {
        "name": "PTDF Scholarship",
        "url": "https://scholarship.ptdf.gov.ng/guidelines",
        "country": "Nigeria"
    }
]



# 2. SCRAPE A SCHOLARSHIP WEBSITE


def scrape_website(source):

    url = source["url"]

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Scholara/1.0)"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unnecessary page elements
        for element in soup(["script","style","nav","footer","header","noscript"]):
            element.decompose()

        scholarships = []

        # Find links that may lead to scholarships
        for link in soup.find_all("a", href=True):

            title = link.get_text(" ", strip=True)
            href = link["href"]

            if not title:
                continue

            # Look for scholarship-related links
            keywords = ["scholarship","funding","bursary","grant","student award"]

            if any(word in title.lower() for word in keywords):

                scholarship_url = urljoin(url, href)

                scholarships.append({
                    "title": title,
                    "url": scholarship_url,
                    "source": source["name"],
                    "country": source["country"],
                    "description": "Visit the original website for details."
                })

        return scholarships

    except requests.RequestException as error:

        print(f"Could not scrape {url}: {error}")

        return []



# 3. DISCOVER SCHOLARSHIPS

def discover_scholarships():

    all_scholarships = []

    seen_urls = set()

    for source in SCHOLARSHIP_SOURCES:

        print(f"Checking {source['name']}...")

        results = scrape_website(source)

        for scholarship in results:

            url = scholarship["url"]

            if url not in seen_urls:

                seen_urls.add(url)

                all_scholarships.append(scholarship)

        # Avoid sending requests too quickly
        time.sleep(1)

    return all_scholarships



# 4. MATCH SCHOLARSHIPS WITH STUDENTS


def match_scholarship(student, scholarship):

    score = 0
    reasons = []

    # Country matching
    student_country = student.get("country", "").lower()
    scholarship_country = scholarship.get("country", "").lower()

    if student_country and scholarship_country:

        if student_country == scholarship_country:
            score += 40
            reasons.append("Country matches")

    # Education level
    student_level = student.get("level", "").lower()
    scholarship_level = scholarship.get("level", "").lower()

    if student_level and scholarship_level:

        if student_level == scholarship_level:
            score += 25
            reasons.append("Education level matches")

    # Course or field of study
    student_course = student.get("course", "").lower()
    scholarship_field = scholarship.get("field", "").lower()

    if student_course and scholarship_field:

        if (
            student_course in scholarship_field
            or scholarship_field in student_course
        ):
            score += 20
            reasons.append("Field of study matches")

    # GPA requirement
    student_gpa = student.get("gpa")
    minimum_gpa = scholarship.get("minimum_gpa")

    if student_gpa is not None and minimum_gpa is not None:

        if float(student_gpa) >= float(minimum_gpa):
            score += 15
            reasons.append("GPA requirement satisfied")

    return {
        "match_score": score,
        "reasons": reasons
    }



# 5. TEST THE DISCOVERY SYSTEM


if __name__ == "__main__":

    results = discover_scholarships()

    print("\nSCHOLARSHIP RESULTS")
    print("===================")

    for scholarship in results:

        print("\nTitle:", scholarship["title"])
        print("Source:", scholarship["source"])
        print("Country:", scholarship["country"])
        print("Link:", scholarship["url"])

    print(f"\nTotal opportunities found: {len(results)}")
