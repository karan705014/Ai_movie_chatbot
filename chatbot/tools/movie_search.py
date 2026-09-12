from urllib.parse import urljoin
from langchain_core.tools import tool
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from seleniumbase import SB

BASE_URL = "https://filmyfly.sale"
SEARCH_URL = f"{BASE_URL}/search.html"

# Universal real browser user-agent to bypass strict data center blocking layers
FAKE_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def normalize(text: str) -> str:
    """Convert text to lowercase and remove extra whitespace."""
    return " ".join(text.lower().split())


def movie_search(movie_name: str):
    """Load JS-rendered search results and extract title + href safely on Railway."""
    search_url = f"{SEARCH_URL}?search={movie_name}"

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
            
            # Hide webdriver indicators safely
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            print(f"SEARCHING URL: {search_url}", flush=True)
            
            # 1. wait_until="networkidle" किया गया ताकि पेज का सारा बैकग्राउंड नेटवर्क डेटा पूरी तरह शांत और लोड हो जाए
            page.goto(search_url, wait_until="networkidle", timeout=60000)
            print("PAGE TITLE:", page.title(), flush=True)
            
            # 2. 5 सेकंड का एक हार्ड बफ़र वेट दें ताकि स्लो मशीन पर भी DOM पूरी तरह सेटल हो जाए
            page.wait_for_timeout(5000)

            # Get the final DOM after JavaScript execution.
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        
        # Primary container check with extensive layout filters
        results = soup.select("#ff-results .A10")
        if not results:
            print("MAIN SELECTOR FAILED: Trying broad layout fallbacks...", flush=True)
            results = soup.select(".ff-results .A10") or soup.select(".A10") or soup.select("[class*='row']")

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
                "url": urljoin(BASE_URL + "/", href),
                "image": image,
            })

        return movies

    except Exception as e:
        print("ERROR IN MOVIE SEARCH:", e)
        return []



@tool
def movie_search_tool(movie_name: str):
    """Search movies using the movie search system."""
    return movie_search(movie_name)


def select_movie(url: str):
    """Bypasses Cloudflare on movie selection step via stealth arguments."""
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
    """Bypasses Cloudflare on file-size mapping options layer securely."""
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
    """Extract Final Link using SeleniumBase and absolute hardware fingerprinting."""
    print("FINAL LINK: Optimized lightweight bypass starting...", flush=True)
    print("TARGET URL:", selected_url, flush=True)
    
    href = None
    try:
        with SB(headless=False, xvfb=False) as sb:
            # 1. Spoof real Windows Chrome device user-agent
            sb.execute_cdp_cmd("Network.setUserAgentOverride", {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            # 2. Complete runtime deletion of automated robot properties
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
    """Extract a simple movie search query from a natural-language message."""
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
    # Test execution trace elements
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
            print("Selected URL:", selected_url)
            final_url = get_final_link(selected_url)
            print("Final href:", final_url)
            print("-" * 50)