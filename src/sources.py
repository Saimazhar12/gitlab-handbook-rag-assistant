"""
sources.py
-----------
Registry of the 14 GitLab Handbook pages selected as the knowledge base
for the this RAG chatbot.

Each entry has:
  - name: short slug used for the output filename
  - title: human-readable page title (used in citations)
  - url: the live handbook URL to scrape
"""

SOURCES = [
    {
        "name": "mission",
        "title": "Mission",
        "url": "https://handbook.gitlab.com/handbook/company/mission/",
    },
    {
        "name": "values",
        "title": "Values",
        "url": "https://handbook.gitlab.com/handbook/values/",
    },
    {
        "name": "about-the-handbook",
        "title": "About the Handbook",
        "url": "https://handbook.gitlab.com/handbook/about/",
    },
    {
        "name": "communication",
        "title": "Communication",
        "url": "https://handbook.gitlab.com/handbook/communication/",
    },
    {
        "name": "remote-work-guide",
        "title": "Guide to All-Remote",
        "url": "https://handbook.gitlab.com/handbook/company/culture/all-remote/guide",
    },
    {
        "name": "diversity-inclusion-belonging",
        "title": "Diversity, Inclusion & Belonging",
        "url": "https://handbook.gitlab.com/handbook/company/culture/inclusion/",
    },
    {
        "name": "hiring",
        "title": "Hiring",
        "url": "https://handbook.gitlab.com/handbook/hiring/",
    },
    {
        "name": "compensation",
        "title": "Compensation",
        "url": "https://handbook.gitlab.com/handbook/total-rewards/compensation",
    },
    {
        "name": "security-practices",
        "title": "Security Practices",
        "url": "https://handbook.gitlab.com/handbook/security/",
    },
    {
        "name": "leadership",
        "title": "Leadership",
        "url": "https://handbook.gitlab.com/handbook/leadership/",
    },
    {
        "name": "career-development",
        "title": "Career Development and Mobility",
        "url": "https://handbook.gitlab.com/handbook/people-group/learning-and-development/career-development/",
    },
    {
        "name": "development-department",
        "title": "Development Department",
        "url": "https://handbook.gitlab.com/handbook/engineering/development/",
    },
    {
        "name": "open-source",
        "title": "Open Source",
        "url": "https://handbook.gitlab.com/handbook/engineering/open-source/",
    },
    {
        "name": "learning-and-development",
        "title": "Learning & Development",
        "url": "https://handbook.gitlab.com/handbook/people-group/learning-and-development/",
    },
]
