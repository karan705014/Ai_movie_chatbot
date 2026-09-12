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
    """Search movies on FilmyFly and return matching movie pages."""
    movie_name = movie_name.strip()

    if not movie_name:
        return []

    try:
        # Use requests params so spaces/special characters are encoded correctly.
        response = requests.get(
            SEARCH_URL,
            params={"search": movie_name},
            headers={
                "User-Agent": FAKE_USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": BASE_URL + "/",
            },
            timeout=20,
        )

        print(f"SEARCH URL: {response.url}", flush=True)
        print(f"SEARCH RESPONSE STATUS: {response.status_code}", flush=True)
        print(f"SEARCH RESPONSE LENGTH: {len(response.text)}", flush=True)

        if response.status_code != 200:
            print(
                f"Target website rejected the request: {response.status_code}",
                flush=True,
            )
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        movies = []
        seen_urls = set()

        # The site's current pages expose movie links as /movie/...html.
        # Do not depend on the old #ff-results/.A10 structure.
        for link in soup.select('a[href*="/movie/"]'):
            href = link.get("href")
            if not href:
                continue

            url = urljoin(BASE_URL + "/", href)

            if url in seen_urls:
                continue

            title = link.get_text(" ", strip=True)

            # Ignore empty/non-movie navigation links.
            if not title:
                continue

            # Only keep links that actually point to movie pages.
            if "/movie/" not in url:
                continue

            image_tag = link.select_one("img")
            image = image_tag.get("src") if image_tag else None
            if image:
                image = urljoin(BASE_URL + "/", image)

            seen_urls.add(url)
            movies.append({
                "title": title,
                "url": url,
                "image": image,
            })

        # Fallback for pages where movie links are rendered differently.
        if not movies:
            for box in soup.select(".A10, [class*='movie'], [class*='item']"):
                link = box.select_one('a[href*="/movie/"]')
                if not link:
                    continue

                href = link.get("href")
                title = link.get_text(" ", strip=True)

                if not href or not title:
                    continue

                url = urljoin(BASE_URL + "/", href)

                if url in seen_urls:
                    continue

                image_tag = box.select_one("img")
                image = image_tag.get("src") if image_tag else None
                if image:
                    image = urljoin(BASE_URL + "/", image)

                seen_urls.add(url)
                movies.append({
                    "title": title,
                    "url": url,
                    "image": image,
                })

        print(f"MOVIES FOUND: {len(movies)}", flush=True)

        for movie in movies:
            print(f"MOVIE: {movie['title']} -> {movie['url']}", flush=True)

        return movies

    except Exception as exc:
        print("ERROR IN MOVIE SEARCH:", repr(exc), flush=True)
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
