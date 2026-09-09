from urllib.parse import urljoin
from langchain_core.tools import tool
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


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


def get_final_link(page, selected_url: str):
    print("FINAL LINK: starting")
    print("FINAL LINK URL:", selected_url)

    page.goto(
        selected_url,
        wait_until="domcontentloaded",
        timeout=30000,
    )

    print("FINAL LINK: page loaded")
    print("FINAL LINK TITLE:", page.title())

    page.wait_for_selector(
        "a.button",
        timeout=30000,
    )

    print("FINAL LINK: button found")

    link = page.locator("a.button").first
    href = link.get_attribute("href")

    print("FINAL LINK HREF:", href)

    return href







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

    for movie in movies:
        print("Movie:", movie["title"])
        print("Movie URL:", movie["url"])

        next_url = select_movie(movie["url"])
        print("Next URL:", next_url)
        print("-" * 50)

        if not next_url:
            continue

        options = select_movie_size(next_url)

        print("Available options:")

        for option in options:
            print("Label:", option["label"])
            print("URL:", option["url"])
            print("-" * 50)

        # YAHAN selected option choose karoge
        if options:
            selected_url = options[0]["url"]

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                final_url = get_final_link(page, selected_url)

                print("Final href:", final_url)

                browser.close()