import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
from seleniumbase import SB
from langchain_core.tools import tool

# Core domain pointer targeting the live site extension
BASE_URL = "https://filmyfly.bingo"
SEARCH_URL = f"{BASE_URL}/search.html"


# Universal real browser user-agent to mask datacenter footprint configurations
FAKE_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def normalize(text: str) -> str:
    """Convert text to lowercase and remove extra whitespace strings."""
    return " ".join(text.lower().split())

def movie_search(movie_name: str):
    """Bypasses cloud network blocks by using structured anti-bot sessions with raw requests."""
    # 🟢 FIXED: Target string pointing directly to the live bingo domain
    search_url = f"https://filmyfly.bingo/search.html?search={movie_name}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }

        print(f"LIGHTWEIGHT SEARCHING URL: {search_url}", flush=True)
        
        response = requests.get(search_url, headers=headers, timeout=20)
        print(f"SEARCH RESPONSE STATUS: {response.status_code}", flush=True)
        
        if response.status_code != 200:
            print(f"Target website rejected the request with status code: {response.status_code}", flush=True)
            return []

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        
        results = soup.select("#ff-results .A10") or soup.select(".ff-results .A10") or soup.select(".A10") or soup.select("[class*='row']")
        print("Total blocks found:", len(results))

        movies = []
        for box in results:
            title_tag = box.select_one(".row-title") or box.select_one("h2") or box.select_one("h3") or box.select_one(".title")
            link_tag = box.select_one("a[href]")
            image_tag = box.select_one("img.row-thumb") or box.select_one("img")

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
        print("ERROR IN LIGHTWEIGHT MOVIE SEARCH:", e)
        return []



@tool
def movie_search_tool(movie_name: str):
    """Search movies using the movie search system."""
    return movie_search(movie_name)


def select_movie(url: str):
    """Bypasses anti-automation barriers on standard movie link layers."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
            )
            context = browser.new_context(user_agent=FAKE_USER_AGENT)
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            print(f"SELECTING MOVIE URL: {url}", flush=True)
            page.goto(url, wait_until="domcontentloaded", timeout=45000)

            link = page.locator(".dlbtn a.bg2").first
            link.wait_for(timeout=45000)

            if link.count() == 0:
                print("Download link not found")
                browser.close()
                return None

            href = link.get_attribute("href")
            browser.close()
            return href

    except Exception as e:
        print("ERROR IN SELECT MOVIE:", e)
        return None


def select_movie_size(url: str):
    """Safely extracts download target properties under stealth environments."""
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
            page.wait_for_selector(".dlink.dl", timeout=45000)

            options = []
            for box in page.locator(".dlink.dl").all():
                link = box.locator("a[href]").first

                if not link.count():
                    continue

                href = link.get_attribute("href")
                label = box.locator(".dll").first

                if not label.count() or not href:
                    continue

                options.append({
                    "label": label.inner_text().strip(),
                    "url": href,
                })

            browser.close()
            return options

    except Exception as e:
        print("ERROR IN SELECT MOVIE SIZE:", e)
        return []


def get_final_link(selected_url: str):
    """Resolves secure target routing paths through virtual hardware injection arrays."""
    print("FINAL LINK: Optimized lightweight bypass starting...", flush=True)
    print("TARGET URL:", selected_url, flush=True)
    
    href = None
    try:
        with SB(headless=False, xvfb=False) as sb:
            # Inject fake active platform fingerprint details
            sb.execute_cdp_cmd("Network.setUserAgentOverride", {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            # Wipe away webdriver properties during evaluation lifecycle
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
    # Internal automated pipeline verification execution array block
    movies = movie_search("Toxic")
    print("\n========== MOVIES ==========\n")
    for movie in movies:
        print("Movie:", movie["title"])
        print("Movie URL:", movie["url"])
        print("-" * 50)
        next_url = select_movie(movie["url"])
        print("Next URL:", next_url)
        print("-" * 50)

        if not next_url:
            continue

        options = select_movie_size(next_url)
        print("\n========== AVAILABLE OPTIONS ==========\n")
        for index, option in enumerate(options):
            print("Index:", index)
            print("Label:", option["label"])
            print("URL:", option["url"])
            print("-" * 50)

        if options:
            selected_url = options[0]["url"]
            print("\n========== FINAL LINK TEST ==========\n")
