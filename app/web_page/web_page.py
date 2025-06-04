import re
from requests import get
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

class WebPage:
    def __init__(self, url:str):
        self.url = url
        self.html, self.soup = self.fetch_html()
        self.is_dynamic = self._is_dynamic()

    def fetch_html(self):
        try:
            response = get(
                self.url,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            if response.ok:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                return html, soup
        except Exception as e:
            print(f"[Error] Could not fetch the page {e}")
            return None, None

    def fetch_dynamic_page(self):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(self.url, timeout=15000)
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                browser.close()
                return html, soup
        except Exception as e:
            print(f"[Error] Could not fetch dynamic page {e}")
            return None, None
    
    def __detect_js_framework(self, html: str) -> bool:
        framework_patterns = [
            r'window\.__NEXT_DATA__',
            r'__react',
            r'__vue__',
            r'data-reactroot',
            r'ng-version',
            r'window\.__NUXT__',
        ]
        return any(re.search(pat, html) for pat in framework_patterns)
    
    def _is_dynamic(self, explanation: bool = False):
        """
        Applies heuristics to determine if a web page is likely dynamic.
        This function analyzes the page's HTML and uses criteria such as content length, number of relevant tags,
        presence of scripts making AJAX requests, mentions of popular JavaScript frameworks (React, Next.js, Vue),
        and the existence of typical SPA elements (like <div id="root"> or <div id="app">).
        Returns True if the combined heuristics indicate the page is probably dynamic, otherwise False.
        
        Args:
            url (str): URL of the page to analyze.
        Returns:
            bool: True if the page is considered dynamic, False otherwise.
        """
        if not self.html:
            if explanation:
                print("[Heuristic] Could not fetch HTML. Considering page as dynamic.")
            return True

        score = 0

        if len(self.html) < 5000:
            if explanation:
                print("[Heuristic] Short HTML (<5000 characters): +1 point (may indicate SPA or dynamic loading).")
            score += 1
        else:
            if explanation:
                print("[Heuristic] Long HTML (>=5000 characters): 0 points.")

        tags = self.soup.find_all(['p', 'h1', 'h2', 'h3', 'li', 'table', 'article', 'section'])
        if len(tags) < 10:
            if explanation:
                print(f"[Heuristic] Few content elements found ({len(tags)}): +1 point.")
            score += 1
        else:
            if explanation:
                print(f"[Heuristic] Many content elements found ({len(tags)}): 0 points.")

        scripts = self.soup.find_all('script')
        scripts_with_ajax = sum([
            bool(re.search(r'fetch|XMLHttpRequest|axios|\.then\(|/api/|\.json', str(script)))
            for script in scripts
        ])
        if scripts_with_ajax > 0:
            if explanation:
                print(f"[Heuristic] Scripts with AJAX/fetch detected ({scripts_with_ajax}): +2 points.")
            score += 2
        else:
            if explanation:
                print("[Heuristic] No AJAX/fetch scripts detected: 0 points.")

        html_lower = self.html.lower()
        if self.__detect_js_framework(html_lower):
            if explanation:
                print("[Heuristic] JS framework detected (React, Vue, Next, etc): +2 points.")
            score += 2
        else:
            if explanation:
                print("[Heuristic] No JS framework detected: 0 points.")

        if re.search(r'<div\s+id="root"|<div\s+id="app"', html_lower):
            if explanation:
                print("[Heuristic] Typical SPA element found (<div id='root'> or <div id='app'>): +1 point.")
            score += 1
        else:
            if explanation:
                print("[Heuristic] No typical SPA element found: 0 points.")

        if explanation:
            print(f"[Result] Final score: {score} (>=3 indicates dynamic page)")
        
        is_dynamic = score >= 3
        if is_dynamic:
            self.html, self.soup = self.fetch_dynamic_page()
        return score >= 3