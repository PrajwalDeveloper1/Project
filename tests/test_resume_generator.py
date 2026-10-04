from app import (
    build_demo_job_description,
    build_demo_profile,
    build_demo_resume_text,
    generate_resume_from_profile,
    get_demo_variants,
    polish_structured_resume,
    profile_quality_issues,
)


def test_generate_resume_from_profile_includes_sections():
    profile = {
        "name": "Aisha Patel",
        "title": "Product Designer",
        "email": "aisha@example.com",
        "phone": "555-123-4567",
        "city_country": "Seattle, United States",
        "links": "https://linkedin.com/in/aisha-patel",
        "summary": "Design-focused product designer with 5+ years of experience building user-centered experiences.",
        "skills": ["Figma", "UX Research", "Design Systems", "User Flows"],
        "experience": [
            {
                "role": "Senior Product Designer",
                "company": "Northstar Labs",
                "dates": "2021-Present",
                "bullets": [
                    "Led end-to-end design for a workflow platform used by 10,000+ customers.",
                    "Reduced onboarding friction by 28% through usability testing and redesign."
                ],
            }
        ],
        "education": ["B.A. in Interaction Design, University of Washington"],
        "projects": ["Design system migration - Figma, React - reduced duplicate components by 30%"],
        "certifications": ["NN/g UX Certification - Nielsen Norman Group - 2024"],
        "achievements": ["Design Excellence Award - 2023"],
        "optional_sections": ["Volunteer mentor - Women in Design"],
    }

    resume = generate_resume_from_profile(profile)

    assert "Aisha Patel" in resume
    assert "Product Designer" in resume
    assert "SUMMARY" in resume
    assert "SKILLS" in resume
    assert "EXPERIENCE" in resume
    assert "Senior Product Designer" in resume
    assert "EDUCATION" in resume
    assert "aisha@example.com" in resume
    assert "Seattle, United States" in resume
    assert "PROJECTS" in resume
    assert "CERTIFICATIONS" in resume
    assert "ACHIEVEMENTS / AWARDS" in resume
    assert "ADDITIONAL INFORMATION" in resume


def test_build_demo_profile_contains_strong_realistic_resume_data():
    profile = build_demo_profile()
    assert profile["name"] == "Aisha Patel"
    assert profile["title"] == "Senior Product Designer"
    assert len(profile["skills"]) >= 4
    assert profile["experience"][0]["company"] == "Northstar Labs"
    assert "design" in profile["summary"].lower()


def test_build_demo_resume_text_contains_full_resume_content():
    resume = build_demo_resume_text()
    assert "Aisha Patel" in resume
    assert "Senior Product Designer" in resume
    assert "SUMMARY" in resume
    assert "EXPERIENCE" in resume
    assert "SKILLS" in resume
    assert "Northstar Labs" in resume


def test_get_demo_variants_has_20_entries_split_evenly_by_job_type():
    variants = get_demo_variants()
    assert len(variants) == 20
    assert sum(1 for item in variants if item["job_family"] == "Product Design") == 10
    assert sum(1 for item in variants if item["job_family"] == "Software Engineering") == 10
    assert all("job_description" in item and "profile" in item for item in variants)


def test_build_demo_job_description_targets_product_design_role():
    job = build_demo_job_description()
    assert "product designer" in job.lower()
    assert "figma" in job.lower()
    assert "ux research" in job.lower()


def test_profile_quality_flags_placeholder_content_and_missing_details():
    assert profile_quality_issues({"name": "asdf", "title": "test test"})
    issues = profile_quality_issues({"name": "Aisha Patel", "title": "Designer", "skills": ["Figma"]})
    assert "your city and country" in issues
    assert "work experience or projects" in issues


def test_polish_structured_resume_improves_summary_and_bullets_without_inventing_facts():
    profile = {
        "title": "Product Designer",
        "summary": "Designs clear user experiences.",
        "skills": ["Figma", "UX Research"],
    }
    draft = """Aisha Patel
Product Designer
SUMMARY
Designs clear user experiences.

EXPERIENCE
Product Designer | Northstar
- worked on onboarding redesign

EDUCATION
- B.A. Design

SKILLS
Figma, UX Research
"""

    polished = polish_structured_resume(profile, draft)

    assert "Product Designer with a focus on Figma, UX Research." in polished
    assert "- Improved onboarding redesign." in polished
    assert "Northstar" in polished
    assert "invented" not in polished.lower()
