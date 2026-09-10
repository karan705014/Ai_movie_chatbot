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
    Render Server पर Cloudflare 403 Forbidden Error को पूरी तरह 
    बायपास करके Final Download Link निकालने का अचूक तरीका।
    """
    print("FINAL LINK: 403 Bypass configuration starting...", flush=True)
    print("TARGET URL:", selected_url, flush=True)
    
    try:
        # uc=True -> Undetected ChromeDriver एक्टिवेट करेगा
        # headless=False -> वर्चुअल स्क्रीन (Xvfb) का पूरा इस्तेमाल करने के लिए इसे False रखें
        # xvfb=True -> Render सर्वर पर नकली 1080p मॉनिटर स्क्रीन बनाएगा
        with SB(uc=True, headless=False, xvfb=True) as sb:
            
            # 1. Cloudflare को चकमा देने के लिए ब्राउज़र के फिंगरप्रिंट्स को इंसानी ब्राउज़र जैसा सेट करें
            sb.execute_cdp_cmd("Network.setUserAgentOverride", {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            # 2. री-कनेक्ट लॉजिक के साथ यूआरएल खोलें (यह 403 और 'Just a moment' पेजों को ब्रेक करता है)
            print("FINAL LINK: Opening URL with Reconnect Logic...", flush=True)
            sb.uc_open_with_reconnect(selected_url, reconnect_time=8)
            sb.sleep(4)  # जावास्क्रिप्ट को पूरी तरह लोड होने का समय दें

            # 3. यदि स्क्रीन पर क्लाउडफ्लेयर का टर्नस्टाइल कैप्चा (Checkbox/Iframe) आ जाता है
            if sb.is_element_present("iframe[src*='://cloudflare.com']"):
                print("FINAL LINK: Cloudflare Turnstile Verification Detected! Bypassing...", flush=True)
                sb.sleep(2)
                sb.uc_gui_handle_captcha()  # वर्चुअल स्क्रीन पर ऑटो-क्लिक करेगा
                sb.sleep(5)

            # 4. अगर ब्राउज़र अभी भी क्लाउडफ्लेयर के चैलेंज पेज पर अटका हुआ है, तो एक बार रिफ्रेश करें
            if "cloudflare" in sb.get_title().lower() or "just a moment" in sb.get_title().lower():
                print("FINAL LINK: Still blocked by Cloudflare, trying a forced refresh...", flush=True)
                sb.refresh()
                sb.sleep(5)

            # 5. अंतिम डाउनलोड बटन की जांच करें
            if not sb.is_element_present("a.button"):
                print(f"FINAL LINK FAILED: Button not found. Page Title is: {sb.get_title()}", flush=True)
                return None

            # 6. फ़ाइनल लिंक निकालें
            href = sb.get_attribute("a.button", "href")
            print("SUCCESS: FINAL LINK HREF EXTRACTED:", href, flush=True)
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