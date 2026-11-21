
from app import app, db
from models import Scholarship

# --------------------------------------------------
# MANUALLY CURATED SCHOLARSHIPS
# --------------------------------------------------

SCHOLARSHIPS = [

    {
        "title": "2026 NNPC - SNEPCo National University Scholarship Award",
        "organization": "NNPC / SNEPCo",
        "description": "National university scholarship opportunity for eligible Nigerian undergraduates.",
        "eligibility": "Verify current eligibility requirements on the official scholarship application page.",
        "country": "Nigeria",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://www.scholastica.ng/",
        "source": "Scholastica",
    },

    {
        "title": "NNPC Limited / TotalEnergies National Merit Scholarship Scheme",
        "organization": "NNPC Limited / TotalEnergies",
        "description": "National merit scholarship opportunity for eligible students.",
        "eligibility": "Verify eligibility, academic requirements and application details with the official organizers.",
        "country": "Nigeria",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://totalenergies.com/",
        "source": "TotalEnergies",
    },

    {
        "title": "Kwara State Government Scholarship and Bursary Award",
        "organization": "Kwara State Government",
        "description": "State scholarship and bursary opportunity.",
        "eligibility": "Verify state residency, institution, academic and other requirements.",
        "country": "Nigeria",
        "funding": "Scholarship / Bursary",
        "deadline": "Not verified",
        "application_link": "https://scholarshipregion.com/",
        "source": "Scholarship Region",
    },

    {
        "title": "Airtel Africa Tech Fellowship for Undergraduates",
        "organization": "Airtel Africa",
        "description": "Technology-focused undergraduate fellowship opportunity.",
        "eligibility": "Verify eligible courses, participating countries and application requirements.",
        "country": "Africa",
        "funding": "Fellowship",
        "deadline": "Not verified",
        "application_link": "https://scholarshipregion.com/",
        "source": "Scholarship Region",
    },

    {
        "title": "Masters and PhD Research Scholarship at Federal University Teaching Hospital, Lafia",
        "organization": "Federal University Teaching Hospital, Lafia",
        "description": "Research scholarship opportunity for postgraduate applicants.",
        "eligibility": "Verify postgraduate programme and research eligibility.",
        "country": "Nigeria",
        "funding": "Research Scholarship",
        "deadline": "Not verified",
        "application_link": "https://scholarshipregion.com/",
        "source": "Scholarship Region",
    },

    {
        "title": "AgricTech Undergraduate Scholarship Programme for Nigerians",
        "organization": "AgricTech Scholarship Programme",
        "description": "Undergraduate opportunity associated with agriculture and technology.",
        "eligibility": "Verify participating programmes and requirements.",
        "country": "Nigeria",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://scholarshipregion.com/",
        "source": "Scholarship Region",
    },

    {
        "title": "Rosewood Legal Nigerian Law Scholarship",
        "organization": "Rosewood Legal",
        "description": "Scholarship opportunity for eligible law students.",
        "eligibility": "Verify law programme, academic and other eligibility requirements.",
        "country": "Nigeria",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://scholarshipregion.com/",
        "source": "Scholarship Region",
    },

    {
        "title": "WAAW Foundation Scholarship for African Undergraduates",
        "organization": "WAAW Foundation",
        "description": "Scholarship opportunity for African undergraduate students.",
        "eligibility": "Verify gender, STEM programme, nationality and academic requirements.",
        "country": "Africa",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://waawfoundation.org/",
        "source": "WAAW Foundation",
    },

    {
        "title": "Anthony Udokwu Foundation Yahweh University Scholarship",
        "organization": "Anthony Udokwu Foundation",
        "description": "Scholarship opportunity associated with Yahweh University.",
        "eligibility": "Verify eligibility and application details with the scholarship organizers.",
        "country": "Nigeria",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://scholarshipair.com/",
        "source": "Scholarship Air",
    },

    {
        "title": "Taiwo Bankole Scholarship for Nigerian Students",
        "organization": "Taiwo Bankole Scholarship",
        "description": "Scholarship opportunity for Nigerian students.",
        "eligibility": "Verify academic, nationality and application requirements.",
        "country": "Nigeria",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://scholarshipregion.com/",
        "source": "Scholarship Region",
    },

    {
        "title": "London School of Hygiene / University of Nigeria Nsukka Scholarship",
        "organization": "London School of Hygiene and Tropical Medicine / University of Nigeria Nsukka",
        "description": "Scholarship opportunity associated with the listed institutions.",
        "eligibility": "Verify programme, nationality and application requirements.",
        "country": "Nigeria",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://scholarshipregion.com/",
        "source": "Scholarship Region",
    },

    {
        "title": "Ondo State OSOPADEC Scholarship Scheme",
        "organization": "OSOPADEC",
        "description": "Scholarship opportunity for eligible students from the Ondo State oil-producing communities.",
        "eligibility": "Verify community, residency and academic requirements.",
        "country": "Nigeria",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://scholarshipregion.com/",
        "source": "Scholarship Region",
    },

    {
        "title": "NNPC Limited / TotalEnergies International Scholarship",
        "organization": "NNPC Limited / TotalEnergies",
        "description": "International scholarship opportunity.",
        "eligibility": "Verify current international programme requirements.",
        "country": "International",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://totalenergies.com/",
        "source": "TotalEnergies",
    },

    {
        "title": "Commonwealth Shared Scholarships",
        "organization": "Commonwealth Scholarship Commission",
        "description": "Scholarship programme supporting eligible postgraduate applicants studying in the United Kingdom.",
        "eligibility": "Verify participating programmes, nationality and requirements.",
        "country": "United Kingdom",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://cscuk.fcdo.gov.uk/",
        "source": "Commonwealth Scholarship Commission",
    },

    {
        "title": "DAAD In-Country / In-Region Scholarships",
        "organization": "DAAD",
        "description": "Scholarship programme supporting eligible African students in participating institutions.",
        "eligibility": "Verify participating programmes, countries and academic requirements.",
        "country": "Africa",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://www.daad.de/",
        "source": "DAAD",
    },

    {
        "title": "UGHE Mastercard Foundation Scholarship",
        "organization": "University of Global Health Equity / Mastercard Foundation",
        "description": "Scholarship opportunity for eligible students at University of Global Health Equity.",
        "eligibility": "Verify programme, academic and application requirements.",
        "country": "Rwanda",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://ughe.org/",
        "source": "UGHE",
    },

    {
        "title": "Erasmus Mundus Joint Masters Scholarships",
        "organization": "European Union / Erasmus Mundus",
        "description": "Scholarship opportunities for students participating in selected joint master's programmes.",
        "eligibility": "Verify participating master's programme and application requirements.",
        "country": "Europe",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://erasmus-plus.ec.europa.eu/",
        "source": "European Union",
    },

    {
        "title": "EducationUSA Opportunity Funds Program",
        "organization": "EducationUSA",
        "description": "Opportunity Funds programme for eligible applicants pursuing study opportunities.",
        "eligibility": "Verify current availability, eligibility and application requirements.",
        "country": "United States",
        "funding": "Opportunity Funds",
        "deadline": "Not verified",
        "application_link": "https://educationusa.state.gov/",
        "source": "EducationUSA",
    },

    {
        "title": "University of Sydney International Stipend Scholarship",
        "organization": "University of Sydney",
        "description": "Research scholarship opportunity for eligible international postgraduate research applicants.",
        "eligibility": "Verify research degree, academic and application requirements.",
        "country": "Australia",
        "funding": "Research Scholarship",
        "deadline": "Not verified",
        "application_link": "https://www.sydney.edu.au/",
        "source": "University of Sydney",
    },

    {
        "title": "Oxford Pershing Square Graduate Scholarships",
        "organization": "University of Oxford / Pershing Square Foundation",
        "description": "Graduate scholarship opportunity for eligible applicants at the University of Oxford.",
        "eligibility": "Verify participating programme and current scholarship requirements.",
        "country": "United Kingdom",
        "funding": "Scholarship",
        "deadline": "Not verified",
        "application_link": "https://www.ox.ac.uk/",
        "source": "University of Oxford",
    },
]


# --------------------------------------------------
# SEED DATABASE
# --------------------------------------------------

def seed_scholarships():

    added = 0
    skipped = 0
    seen_links = set()

    try:

        for item in SCHOLARSHIPS:

            link = item["application_link"].strip()

            # Skip duplicate links within the seed list
            if link in seen_links:
                skipped += 1
                continue

            seen_links.add(link)

            # Skip links already in the database
            existing = Scholarship.query.filter_by(
                application_link=link
            ).first()

            if existing:
                skipped += 1
                continue

            scholarship = Scholarship(**item)

            db.session.add(scholarship)

            added += 1

        db.session.commit()

        print(f"Added: {added}")
        print(f"Skipped: {skipped}")

    except Exception as e:

        db.session.rollback()

        print("SEED ERROR:", e)


if __name__ == "__main__":

    with app.app_context():

        seed_scholarships()





