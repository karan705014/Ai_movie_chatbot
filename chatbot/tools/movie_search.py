import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from seleniumbase import SB
from langchain_core.tools import tool

BASE_URL = "https://filmyfly.bingo"
SEARCH_URL = f"{BASE_URL}/search.html"

# Universal real browser user-agent to mask automated footprint parameters
FAKE_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
COMMON_HEADERS = {
    'User-Agent': FAKE_USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Upgrade-Insecure-Requests': '1'
}

def normalize(text: str) -> str:
    """Convert text to lowercase and remove extra whitespace strings."""
    return " ".join(text.lower().split())


def movie_search(movie_name: str):
    """Loads search results via Playwright to fully execute dynamic JavaScript loading states."""
    search_url = f"{SEARCH_URL}?search={movie_name}"
    print(f"PLAYWRIGHT SEARCHING URL: {search_url}", flush=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )

            context = browser.new_context(
                user_agent=FAKE_USER_AGENT,
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            
            # Wipe away automatic robot signatures completely
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Route requests and wait for network layers to completely settle down
            page.goto(search_url, wait_until="networkidle", timeout=60000)
            print("PAGE TITLE:", page.title(), flush=True)
            
            # Safe cushion buffer allowing lazy-loaded tables to fully populate into the DOM
            page.wait_for_timeout(4000)

            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        
        # Selects your precise active container block rows
        results = soup.select("#ff-results .A10")
        print("Total blocks found:", len(results))

        movies = []
        for box in results:
            title_tag = box.select_one(".row-title")
            link_tag = box.select_one("a")
            image_tag = box.select_one("img.row-thumb")

            if not title_tag or not link_tag:
                continue

            title = title_tag.get_text(" ", strip=True)
            href = link_tag.get("href")

            if not href or "search.html" in href:
                continue

            image = image_tag.get("src") if image_tag else None

            movies.append({
                "title": title,
                "url": urljoin("https://filmyfly.bingo/", href),
                "image": image,
            })

        return movies

    except Exception as e:
        print("ERROR IN JAVASCRIPT MOVIE SEARCH:", e)
        return []


@tool
def movie_search_tool(movie_name: str):
    """Search movies using the movie search system."""
    return movie_search(movie_name)


def select_movie(url: str):
    """Bypasses the second page link-protector blocking layer safely via lightweight requests."""
    try:
        print(f"LIGHTWEIGHT SELECTING MOVIE URL: {url}", flush=True)
        response = requests.get(url, headers=COMMON_HEADERS, timeout=20)
        
        if response.status_code != 200:
            print(f"Failed to fetch second page. Status: {response.status_code}", flush=True)
            return None

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        link_tag = soup.select_one(".dlbtn a.bg2")
        
        if not link_tag:
            print("Download link layout element '.dlbtn a.bg2' not found on the page", flush=True)
            return None

        href = link_tag.get("href")
        print(f"SUCCESSFULLY CAPTURED PROTECTOR URL: {href}", flush=True)
        return href

    except Exception as e:
        print("ERROR IN SELECT MOVIE STAGE:", e)
        return None


def select_movie_size(url: str):
    """Safely extracts intermediate cloud drive size objects under stealth environments."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
            )
            context = browser.new_context(user_agent=FAKE_USER_AGENT)
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            print(f"LOADING SIZES FROM URL: {url}", flush=True)
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_selector(".dlink.dl a", timeout=45000)

            options = []
            for box in page.locator(".dlink.dl a").all():
                href = box.get_attribute("href")
                label_element = box.locator(".dll").first
                
                if not label_element.count() or not href:
                    continue

                options.append({
                    "label": label_element.inner_text().strip(),
                    "url": href,
                })

            browser.close()
            return options

    except Exception as e:
        print("ERROR IN SELECT MOVIE SIZE:", e)
        return []


def get_final_link(selected_url: str):
    """Resolves final download paths via virtual display rendering architectures."""
    print("FINAL LINK: Optimized lightweight bypass starting...", flush=True)
    print("TARGET URL:", selected_url, flush=True)
    
    href = None
    try:
        with SB(headless=False, xvfb=False) as sb:
            sb.execute_cdp_cmd("Network.setUserAgentOverride", {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            sb.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    window.chrome = { runtime: {} };
                    Object.defineProperty(navigator, 'plugins', {get: () => []});
                """
            })
            
            print("FINAL LINK: Loading target page directly...", flush=True)
            sb.open(selected_url)
            sb.sleep(5)

            if "just a moment" in sb.get_title().lower() or "cloudflare" in sb.get_title().lower():
                print("FINAL LINK: Cloudflare challenge seen, waiting for automatic bypass...", flush=True)
                sb.sleep(5)

            if not sb.is_element_present("a.button"):
                print(f"FINAL LINK FAILED: Button not found. Current Page Title: {sb.get_title()}", flush=True)
                return None

            href = sb.get_attribute("a.button", "href")
            print(f" SUCCESS: FINAL LINK HREF EXTRACTED: {href}", flush=True)
            return href

    except Exception as exc:
        print("FINAL LINK EXCEPTION ERROR:", repr(exc), flush=True)
        return None


STOP_WORDS = {
    "movie", "movies", "film", "films", "search", "find", "findo", "give", "me",
    "tell", "about", "please", "show", "want", "need", "mujhe", "dhundho", "dhundo",
    "dhoondo", "karo", "karna", "hai", "ka", "ki", "ke", "batao", "bata", "do", "chahiye",
}

def extract_search_query(message: str) -> str:
    """Extract a simple movie search query from a natural-language message structure."""
    message = message.strip()
    if not message:
        return ""

    match = re.search(
        r"(?:give\s+me|tell\s+me|show\s+me)\s+(.+?)\s+of\s+.+",
        message,
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1).strip()

    words = re.findall(r"[A-Za-z0-9]+", message)
    filtered_words = [word for word in words if word.lower() not in STOP_WORDS]
    return " ".join(filtered_words).strip()


if __name__ == "__main__":
    # Executing localized test pipeline
    print("RUNNING LOCAL SEARCH TESTING ARRAY...", flush=True)
    movies_list = movie_search("Toxic")
    print("\n========== MOVIES RESULTS ==========\n")
    for movie in movies_list:
        print("Title Found:", movie["title"])
        print("URL Linked:", movie["url"])
        print("-" * 50)
