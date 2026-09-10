from urllib.parse import urljoin
from langchain_core.tools import tool
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from seleniumbase import SB



BASE_URL = "https://filmyfly.sale/"
SEARCH_URL = f"{BASE_URL}/search.html"


def normalize(text: str) -> str:
    """Convert text to lowercase and remove extra whitespace."""
    return " ".join(text.lower().split())


def movie_search(movie_name: str):
    """Load JS-rendered search results and extract title + href."""

    search_url = f"{SEARCH_URL}?search={movie_name}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            page.goto(search_url, wait_until="domcontentloaded",timeout=30000)
            print("PAGE TITLE:", page.title())
            # Wait until JS-generated result container is populated.
            page.wait_for_selector("#ff-results .A10",timeout=30000)

            # Get the final DOM after JavaScript execution.
            html = page.content()

            browser.close()

        soup = BeautifulSoup(html, "html.parser")

        results = soup.select("#ff-results .A10")

        print("Total blocks found:", len(results))

        movies = []

        for box in results:
            title_tag = box.select_one(".row-title")
            link_tag = box.select_one("a[href]")
            image_tag = box.select_one("img.row-thumb")


            if not title_tag or not link_tag:
                continue

            title = title_tag.get_text(" ", strip=True)
            href = link_tag.get("href")

            if not href:
                continue

            # Extract poster URL
            image = image_tag.get("src") if image_tag else None

            movies.append({
                "title": title,
                "url": urljoin(BASE_URL, href),
                "image": image,

            })

        return movies

    except Exception as e:
        print("ERROR:", e)
        return []


@tool
def movie_search_tool(movie_name: str):
    """Search movies using the movie search system."""
    return movie_search(movie_name)


def select_movie(url: str):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, wait_until="domcontentloaded",timeout=30000)

            link = page.locator(".dlbtn a.bg2").first
            link.wait_for(timeout=30000)

            if link.count() == 0:
                print("Download link not found")
                browser.close()
                return None

            href = link.get_attribute("href")

            browser.close()

            return href

    except Exception as e:
        print("ERROR:", e)
        return None


def select_movie_size(url: str):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, wait_until="domcontentloaded",timeout=30000)
            page.wait_for_selector(".dlink.dl",timeout=30000)

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
        print("ERROR:", e)
        return []



def get_final_link(selected_url: str):
    """
    Render Free Tier के लिए पूरी तरह ऑप्टिमाइज़्ड फ़ंक्शन।
    AttributeError को पूरी तरह फिक्स कर दिया गया है।
    """
    print("FINAL LINK: Optimized lightweight bypass starting...", flush=True)
    print("TARGET URL:", selected_url, flush=True)
    
    href = None
    try:
        with SB(headless=False, xvfb=False) as sb:
            
            # 1. क्रोम को पूरी तरह से एक सामान्य इंसानी ब्राउज़र के रूप में ढालें
            sb.execute_cdp_cmd("Network.setUserAgentOverride", {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            # 2. ऑटोमेशन के सभी फ्लैग्स को मिटाएं ताकि Cloudflare को शक न हो
            sb.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    window.chrome = { runtime: {} };
                    Object.defineProperty(navigator, 'plugins', {get: () => []});
                """
            })
            
            # 3. सीधे यूआरएल खोलें
            print("FINAL LINK: Loading target page directly...", flush=True)
            sb.open(selected_url)
            sb.sleep(5)  # 5 सेकंड का स्थिर बफ़र

            # 4. अगर फिर भी 'Just a moment' पेज दिखता है
            if "just a moment" in sb.get_title().lower() or "cloudflare" in sb.get_title().lower():
                print("FINAL LINK: Cloudflare challenge seen, waiting for automatic bypass...", flush=True)
                sb.sleep(5)

            # 5. अंतिम डाउनलोड बटन की जांच करें
            if not sb.is_element_present("a.button"):
                print(f"FINAL LINK FAILED: Button not found. Current Page Title: {sb.get_title()}", flush=True)
                return None

            # 6. फ़ाइनल लिंक को तुरंत निकालें
            href = sb.get_attribute("a.button", "href")
            print(f"🚀 SUCCESS: FINAL LINK HREF EXTRACTED: {href}", flush=True)
            
            # NOTE: sb.disconnect() को हटा दिया गया है क्योंकि with SB() इसे खुद हैंडल करता है
            return href



    except Exception as exc:
        print("FINAL LINK EXCEPTION ERROR:", repr(exc), flush=True)
        return None









STOP_WORDS = {
    "movie",
    "movies",
    "film",
    "films",
    "search",
    "find",
    "findo",
    "give",
    "me",
    "tell",
    "about",
    "please",
    "show",
    "want",
    "need",
    "mujhe",
    "dhundho",
    "dhundo",
    "dhoondo",
    "karo",
    "karna",
    "hai",
    "ka",
    "ki",
    "ke",
    "batao",
    "bata",
    "do",
    "chahiye",
}


def extract_search_query(message: str) -> str:
    """
    Extract a simple movie search query from a natural-language message.
    """

    message = message.strip()

    if not message:
        return ""

    # Handle phrases such as:
    # "give me Toxic of Yash"
    # "tell me Toxic of Yash"
    match = re.search(
        r"(?:give\s+me|tell\s+me|show\s+me)\s+(.+?)\s+of\s+.+",
        message,
        flags=re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    words = re.findall(r"[A-Za-z0-9]+", message)

    filtered_words = [
        word
        for word in words
        if word.lower() not in STOP_WORDS
    ]

    return " ".join(filtered_words).strip()


if __name__ == "__main__":
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

        # First option testing ke liye select
        if options:
            selected_url = options[0]["url"]

            print("\n========== FINAL LINK TEST ==========\n")
            print("Selected URL:", selected_url)

            final_url = get_final_link(selected_url)

            print("Final href:", final_url)
            print("-" * 50)