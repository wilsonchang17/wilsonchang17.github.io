import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html", "projects.html", "research.html", "resume.html"]


class ElementCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class NavigationCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_navigation = False
        self.current_link = None
        self.links = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "ul" and "nav-list" in attributes.get("class", "").split():
            self.in_navigation = True
        elif self.in_navigation and tag == "a":
            self.current_link = []

    def handle_data(self, data):
        if self.current_link is not None:
            self.current_link.append(data)

    def handle_endtag(self, tag):
        if self.in_navigation and tag == "a" and self.current_link is not None:
            self.links.append("".join(self.current_link).strip())
            self.current_link = None
        elif tag == "ul" and self.in_navigation:
            self.in_navigation = False


def page_text(name):
    return (ROOT / name).read_text(encoding="utf-8")


def elements(name):
    parser = ElementCollector()
    parser.feed(page_text(name))
    return parser.elements


def navigation_links(name):
    parser = NavigationCollector()
    parser.feed(page_text(name))
    return parser.links


class PortfolioSiteTests(unittest.TestCase):
    def test_navigation_prioritizes_resume_and_calls_work_projects(self):
        expected = ["Home", "Resume", "Projects", "Research", "Contact"]
        for page in PAGES:
            with self.subTest(page=page):
                self.assertEqual(navigation_links(page), expected)

    def test_homepage_does_not_repeat_metrics_in_a_proof_strip(self):
        homepage_sections = [
            attrs for tag, attrs in elements("index.html") if tag == "section"
        ]
        self.assertFalse(
            any("proof-strip" in attrs.get("class", "").split() for attrs in homepage_sections)
        )

    def test_every_page_has_an_accessible_shared_shell(self):
        for page in PAGES:
            with self.subTest(page=page):
                html = page_text(page)
                self.assertIn('href="favicon.svg"', html)
                self.assertIn('class="skip-link"', html)
                self.assertIn("<main", html)
                self.assertIn('aria-label="Primary navigation"', html)
                self.assertIn('id="primary-navigation"', html)
                self.assertRegex(
                    html,
                    r'<button[^>]+class="menu-toggle"[^>]+aria-expanded="false"',
                )
                self.assertIn("<footer", html)

        self.assertTrue((ROOT / "favicon.svg").is_file())

    def test_public_contact_details_are_recruiter_focused(self):
        for page in PAGES:
            with self.subTest(page=page):
                html = page_text(page)
                self.assertIn("mailto:wilsonnchangg@gmail.com", html)
                self.assertIn("github.com/wilsonchang17", html)
                self.assertIn("linkedin.com/in/wilsonnchang", html)
                self.assertNotIn("(571) 594-7580", html)
                self.assertNotIn("571) 594-7580", html)
                self.assertNotIn("Alexandria, VA, USA", html)
                self.assertNotIn("facebook.com", html)
                self.assertNotIn("instagram.com", html)

    def test_resume_download_uses_the_current_local_pdf(self):
        expected = "assets/Resume_SE_Wilson_Chang.pdf"
        self.assertTrue((ROOT / expected).is_file())
        for page in ["index.html", "resume.html"]:
            with self.subTest(page=page):
                html = page_text(page)
                self.assertIn(expected, html)
                self.assertNotIn("drive.google.com", html)

    def test_homepage_leads_with_software_engineering_and_ai_systems(self):
        html = page_text("index.html")
        for proof in [
            "Software Engineer",
            "Amazon",
        ]:
            with self.subTest(proof=proof):
                self.assertIn(proof, html)
        self.assertNotIn("06/2025 - 08/2026", html)
        self.assertNotIn("Scorched Nebraska", html)
        self.assertNotIn("visitor-stats", html)
        self.assertNotIn("countapi", html)

    def test_projects_page_curates_three_features_and_six_archive_items(self):
        project_elements = [attrs for tag, attrs in elements("projects.html") if tag == "article"]
        featured = [item for item in project_elements if item.get("data-project-tier") == "featured"]
        archive = [item for item in project_elements if item.get("data-project-tier") == "archive"]
        self.assertEqual(len(featured), 3)
        self.assertEqual(len(archive), 6)
        html = page_text("projects.html")
        for title in ["RailEstate", "Scam Shield", "E-commerce Platform"]:
            self.assertIn(title, html)

    def test_research_page_lists_three_first_author_publications(self):
        html = page_text("research.html")
        self.assertEqual(html.count('data-publication="first-author"'), 3)
        self.assertIn("IEEE BigData", html)
        self.assertIn("ACM SIGSPATIAL", html)

    def test_external_new_tab_links_are_safe(self):
        for page in PAGES:
            for tag, attrs in elements(page):
                if tag == "a" and attrs.get("target") == "_blank":
                    with self.subTest(page=page, href=attrs.get("href")):
                        rel_tokens = set((attrs.get("rel") or "").split())
                        self.assertIn("noopener", rel_tokens)
                        self.assertIn("noreferrer", rel_tokens)

    def test_css_keeps_keyboard_and_reduced_motion_support(self):
        css = page_text("css/style.css")
        self.assertIn(":focus-visible", css)
        self.assertIn("@media (prefers-reduced-motion: reduce)", css)
        self.assertIn("--color-accent", css)
        self.assertNotRegex(css, r"focus[^\{]*\{[^\}]*outline:\s*none")
        self.assertIsNotNone(
            re.search(
                r"@media \(max-width: 50rem\).*?\.nav-list\s*\{[^}]*height:\s*calc\(100svh - var\(--header-height\)\)",
                css,
                re.DOTALL,
            )
        )

    def test_javascript_controls_accessible_mobile_navigation(self):
        js = page_text("js/main.js")
        self.assertIn("aria-expanded", js)
        self.assertIn("Escape", js)
        self.assertNotIn("countapi", js)
        self.assertNotIn("freecounterstat", js)

    def test_project_images_use_lazy_loading(self):
        for tag, attrs in elements("projects.html"):
            if tag == "img":
                with self.subTest(src=attrs.get("src")):
                    self.assertEqual(attrs.get("loading"), "lazy")
                    self.assertEqual(attrs.get("decoding"), "async")

    def test_no_placeholder_links_remain(self):
        for page in PAGES:
            html = page_text(page)
            with self.subTest(page=page):
                self.assertIsNone(re.search(r'href=["\'](?:#(?:["\'])|javascript:)', html))


if __name__ == "__main__":
    unittest.main()
