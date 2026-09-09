import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from dotenv import load_dotenv
from google import genai
from langchain_ollama import ChatOllama


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-3-flash-preview"

ollama_llm = ChatOllama(
    model="gemma3:latest",
    temperature=0,
)


# ============================================================
# BASIC HELPERS
# ============================================================

def clean_text(value: Any) -> str:
    return str(value or "").strip()


def normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", clean_text(value)).strip()


def format_history(history: Optional[List[Dict[str, Any]]]) -> str:
    if not history:
        return "No previous conversation."

    lines: List[str] = []

    for item in history:
        role = clean_text(item.get("role", "user")).lower()
        content = normalize_spaces(item.get("content", ""))

        if not content:
            continue

        role_name = "User" if role == "user" else "Assistant"
        lines.append(f"{role_name}: {content}")

    return "\n".join(lines) or "No previous conversation."


def parse_json_response(text: str) -> Dict[str, Any]:
    text = clean_text(text)

    if not text:
        raise ValueError("AI returned an empty response.")

    text = re.sub(
        r"^\s*```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\s*```\s*$", "", text).strip()

    if not text.startswith("{"):
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            text = match.group(0)

    result = json.loads(text)

    if not isinstance(result, dict):
        raise ValueError("AI response is not a JSON object.")

    return result


# ============================================================
# LANGCHAIN TOOLS
# ============================================================

def tool_duckduckgo(query: str) -> str:
    """
    Search the public web for current/recent information, news,
    releases, and information that may have changed recently.
    """
    from langchain_community.tools import DuckDuckGoSearchRun

    query = normalize_spaces(query)
    if not query:
        return "No search query was provided."

    try:
        search = DuckDuckGoSearchRun()
        response = search.invoke(query)
        return clean_text(response) or "No web search result was returned."
    except Exception as exc:
        print("DUCKDUCKGO ERROR:", repr(exc))
        return "Web search is currently unavailable."


def tool_wikipedia_search(query: str) -> str:
    """
    Search Wikipedia for factual knowledge, biographies, movies,
    history, science, sports, and other well-established topics.
    """
    from langchain_community.tools import WikipediaQueryRun
    from langchain_community.utilities import WikipediaAPIWrapper

    query = normalize_spaces(query)
    if not query:
        return "No Wikipedia query was provided."

    try:
        wiki = WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(
                top_k_results=5,
                doc_content_chars_max=12000,
            )
        )
        response = wiki.invoke(query)
        return clean_text(response) or "No Wikipedia result was returned."
    except Exception as exc:
        print("WIKIPEDIA ERROR:", repr(exc))
        return "Wikipedia is currently unavailable."


# ============================================================
# GREETING + NAME HANDLER
# ============================================================

# Common misspellings / variations are matched by similarity below.
# These aliases cover likely ways Muskan and Adarsh may introduce
# themselves without making the match exact-spelling dependent.
MUSKAN_ALIASES = {
    "muskan",
    "muksan",
    "mukskan",
    "mukshan",
    "muksan",
    "muksaan",
    "muskann",
    "muskaan",
    "muskhan",
    "muskann",
    "mukasan",
    "muksaan",
}

ADARSH_ALIASES = {
    "adarsh",
    "adharsh",
    "adars",
    "adash",
    "adassh",
    "adhash",
    "adarshh",
    "adars h",
    "adarshu",
    "adarshu",
    "adashu",
    "adhashu",
    "adasshu",
    "adarshu",
}


def _clean_name_for_match(name: str) -> str:
    """Normalize a name for tolerant comparison."""
    return re.sub(r"[^a-z]", "", clean_text(name).casefold())


def _name_similarity(name: str, aliases) -> float:
    """
    Return the best similarity score between the supplied name and
    the known aliases.
    """
    candidate = _clean_name_for_match(name)

    if not candidate:
        return 0.0

    return max(
        SequenceMatcher(None, candidate, alias).ratio()
        for alias in aliases
        if alias
    )


def _is_muskan(name: str) -> bool:
    candidate = _clean_name_for_match(name)

    if not candidate:
        return False

    # Very short names need a stronger threshold.
    threshold = 0.76 if len(candidate) >= 6 else 0.84
    return _name_similarity(candidate, MUSKAN_ALIASES) >= threshold


def _is_adarsh(name: str) -> bool:
    candidate = _clean_name_for_match(name)

    if not candidate:
        return False

    threshold = 0.76 if len(candidate) >= 6 else 0.84
    return _name_similarity(candidate, ADARSH_ALIASES) >= threshold


def extract_introduced_name(message: str) -> str:
    """
    Extract a name when the user introduces themselves.

    Examples:
        "hii i am muskan"
        "my name is muskan"
        "i'm adarsh"
        "i am adharsh"
        "mera naam muskan hai"
        "main adarsh hu"
    """
    text = normalize_spaces(message)

    patterns = [
        r"\bmy\s+name\s+is\s+([a-z][a-z'-]{1,30})\b",
        r"\bi\s*(?:am|'m)\s+([a-z][a-z'-]{1,30})\b",
        r"\bmera\s+naam\s+([a-z][a-z'-]{1,30})\b",
        r"\bmain\s+([a-z][a-z'-]{1,30})\s+(?:hu|hoon|hun|h)\b",
        r"\bmai\s+([a-z][a-z'-]{1,30})\s+(?:hu|hoon|hun|h)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            # Safety check: only read group(1) when the regex
            # actually contains a capturing group.
            if match.lastindex and match.lastindex >= 1:
                return clean_text(match.group(1))

    return ""


def handle_greeting(message: str) -> Optional[str]:
    """
    Handle greetings and self-introductions directly.

    Muskan-like spellings:
        -> "Hii baby 💖 How can I help you?"

    Adarsh-like spellings:
        -> "Hii bhiya 👋 How can I help you?"

    Any other introduced name:
        -> "Hii <name> 👋 How can I help you?"

    Simple greetings:
        -> generic greeting.

    No web search or LLM call is made for these cases.
    """
    text = normalize_spaces(message)
    lower = text.casefold()

    # --------------------------------------------------------
    # USER INTRODUCES THEMSELF
    # --------------------------------------------------------
    introduced_name = extract_introduced_name(text)

    if introduced_name:
        if _is_muskan(introduced_name):
            return "Hii baby 💖 How can I help you?"

        if _is_adarsh(introduced_name):
            return "Hii bhiya 👋 How can I help you?"

        # Everyone else gets their own supplied name.
        display_name = introduced_name.strip().capitalize()
        return f"Hii {display_name} 👋 How can I help you?"

    # --------------------------------------------------------
    # SIMPLE GREETINGS
    # --------------------------------------------------------
    if re.fullmatch(
        r"(?:hi+|hii+|hello+|hey+|heyy+|namaste|namaskar)[\s,!.]*",
        lower,
    ):
        return (
            "Hii 👋 How can I help you with movies, actors, directors, "
            "ratings, releases, or recommendations?"
        )

    return None


# ============================================================
# SOURCE SELECTION
# ============================================================

CURRENT_QUERY_PATTERNS = [
    r"\blatest\b",
    r"\bcurrent\b",
    r"\bcurrently\b",
    r"\btoday\b",
    r"\btonight\b",
    r"\bnow\b",
    r"\brecent\b",
    r"\brecently\b",
    r"\bnew movie\b",
    r"\blatest movie\b",
    r"\bupcoming movie\b",
    r"\bnext movie\b",
    r"\bnew film\b",
    r"\blatest film\b",
    r"\bupcoming film\b",
    r"\bnext film\b",
    r"\b2026\b",
    r"\b2025\b",
]


def needs_current_web_search(message: str) -> bool:
    message_lower = clean_text(message).lower()
    return any(
        re.search(pattern, message_lower)
        for pattern in CURRENT_QUERY_PATTERNS
    )


# ============================================================
# DETERMINISTIC INTENT ROUTER
# ============================================================

INFORMATION_PATTERNS = [
    # English factual questions
    r"\bwho is\b",
    r"\bwhat is\b",
    r"\btell me about\b",
    r"\babout\b",
    r"\bwho directed\b",
    r"\bwho acted\b",
    r"\bcast\b",
    r"\bstory\b",
    r"\bplot\b",
    r"\bgenre\b",
    r"\brelease\b",
    r"\breleased\b",
    r"\brating\b",
    r"\breview\b",
    r"\bimdb\b",
    r"\bscore\b",
    r"\bcareer\b",
    r"\bbiography\b",
    r"\bage\b",
    r"\bborn\b",
    r"\bawards?\b",
    r"\bfilmography\b",
    r"\bmovies?\b",
    r"\bfilms?\b",
    r"\blatest\b",
    r"\bupcoming\b",
    r"\bnew movie\b",
    r"\bnext movie\b",
    r"\bworth watching\b",

    # Hinglish/Hindi
    r"\bke baare mein\b",
    r"\bke bare mein\b",
    r"\bki rating\b",
    r"\bka rating\b",
    r"\bki review\b",
    r"\bka review\b",
    r"\bmovie ki\b",
    r"\bmovie ka\b",
    r"\bfilm ki\b",
    r"\bfilm ka\b",
    r"\bki latest\b",
    r"\bka latest\b",
    r"\bki new\b",
    r"\bka new\b",
    r"\bki upcoming\b",
    r"\bka upcoming\b",
    r"\bkya hai\b",
    r"\bkya h\b",
    r"\bkaun\b",
    r"\bbatao\b",
    r"\bbtao\b",
    r"\bkab release\b",
    r"\bkaun directed\b",
]


MOVIE_COMMAND_PATTERNS = [
    # English search/link/download style commands
    r"^\s*download\b",
    r"^\s*search\b",
    r"^\s*find\b",
    r"^\s*get\b",
    r"^\s*give me\b",
    r"^\s*i want\b",
    r"^\s*show me\b",
    r"^\s*movie link\b",
    r"^\s*download link\b",
    r"\bgive me .*link\b",
    r"\bsearch this movie\b",
    r"\bsearch that movie\b",
    r"\bfind this movie\b",
    r"\bfind that movie\b",
    r"\bgive me this movie\b",
    r"\bgive me that movie\b",
    r"\bi want this movie\b",
    r"\bi want that movie\b",

    # Hinglish/Hindi
    r"\biska link\b",
    r"\buska link\b",
    r"\biski link\b",
    r"\buski link\b",
    r"\blink do\b",
    r"\bmovie do\b",
    r"\bmovie chahiye\b",
    r"\bfilm chahiye\b",
    r"\bdownload karo\b",
    r"\bdownload karna hai\b",
]


REFERENCE_MOVIE_PATTERNS = [
    r"\bdownload\s+(?:it|this|that)\b",
    r"\bsearch\s+(?:it|this|that)\b",
    r"\bfind\s+(?:it|this|that)\b",
    r"\bgive me\s+(?:it|this|that)\b",
    r"\b(?:iska|uska|iski|uski)\s+(?:link|movie)\b",
    r"\b(?:is|us)\s+movie\b",
]


def matches_any(message: str, patterns: List[str]) -> bool:
    message_lower = clean_text(message).lower()
    return any(re.search(pattern, message_lower) for pattern in patterns)


def is_reference_movie_request(message: str) -> bool:
    return matches_any(message, REFERENCE_MOVIE_PATTERNS)


def is_information_query(message: str) -> bool:
    """
    Information is checked before generic movie-title handling.
    This prevents:
        "Mirzapur movie rating"
        "Salman Khan latest movie"
        "Dabangg ke baare mein batao"
    from becoming movie searches.
    """
    return matches_any(message, INFORMATION_PATTERNS)


def is_explicit_movie_request(message: str) -> bool:
    """
    Detect requests where the user wants the application to find
    a movie. This function does NOT create any URL.
    """
    if is_information_query(message) and not is_reference_movie_request(message):
        return False

    return matches_any(message, MOVIE_COMMAND_PATTERNS)


# ============================================================
# MOVIE TITLE CLEANING
# ============================================================

LEADING_COMMAND_PATTERNS = [
    r"^\s*download\s+(?:the\s+)?",
    r"^\s*download\s+movie\s+",
    r"^\s*download\s+film\s+",
    r"^\s*search\s+(?:for\s+)?(?:the\s+)?",
    r"^\s*search\s+movie\s+",
    r"^\s*search\s+film\s+",
    r"^\s*find\s+(?:the\s+)?",
    r"^\s*find\s+movie\s+",
    r"^\s*find\s+film\s+",
    r"^\s*get\s+(?:the\s+)?",
    r"^\s*give\s+me\s+(?:the\s+)?",
    r"^\s*i\s+want\s+(?:the\s+)?",
    r"^\s*show\s+me\s+(?:the\s+)?",
    r"^\s*movie\s+link\s+(?:for\s+)?",
    r"^\s*download\s+link\s+(?:for\s+)?",
]


TRAILING_NOISE_PATTERNS = [
    r"\s+movie\s+link\s*$",
    r"\s+download\s+link\s*$",
    r"\s+movie\s*$",
    r"\s+film\s*$",
    r"\s+please\s*$",
    r"\s+plz\s*$",
]


QUALITY_NOISE_PATTERNS = [
    r"\s+(?:in\s+)?(?:hindi|english|tamil|telugu|punjabi)\s*$",
    r"\s+(?:1080p|720p|480p|2160p|4k)\s*$",
    r"\s+(?:hd|full hd)\s*$",
]


def clean_movie_title_from_user_message(message: str) -> str:
    """
    Extract ONLY the title from an explicit movie request.

    Important:
    - Never use Wikipedia's longer/canonical title to expand the user's title.
    - Never add subtitles.
    - Never add "movie", quality, language, or download wording.
    """
    title = normalize_spaces(message)

    # Handle reference-only commands elsewhere.
    if re.fullmatch(
        r"(download|search|find|get|give me|show me)\s+"
        r"(it|this|that)",
        title,
        flags=re.IGNORECASE,
    ):
        return ""

    for pattern in LEADING_COMMAND_PATTERNS:
        title = re.sub(pattern, "", title, count=1, flags=re.IGNORECASE)

    for pattern in TRAILING_NOISE_PATTERNS:
        title = re.sub(pattern, "", title, count=1, flags=re.IGNORECASE)

    for pattern in QUALITY_NOISE_PATTERNS:
        title = re.sub(pattern, "", title, count=1, flags=re.IGNORECASE)

    # Remove polite punctuation only.
    title = re.sub(r"^[\s,:-]+|[\s,:-]+$", "", title)

    return normalize_spaces(title)


def extract_last_movie_from_history(
    conversation_history: Optional[List[Dict[str, Any]]],
) -> str:
    """
    Recover a movie title from previous assistant/user messages.
    This is deterministic so an LLM cannot randomly invent a title.
    """
    if not conversation_history:
        return ""

    # Newest messages first.
    for item in reversed(conversation_history):
        content = normalize_spaces(item.get("content", ""))

        if not content:
            continue

        patterns = [
            r"Searching for\s+(.+?)(?:[.!?]|$)",
            r"movie_name\s*[:=]\s*['\"]?(.+?)['\"]?$",
            r"(?:movie|film)\s+(?:is|was)\s+(.+?)(?:[.!?]|$)",
        ]

        for pattern in patterns:
            match = re.search(content, pattern, flags=re.IGNORECASE)
            if match:
                candidate = normalize_spaces(match.group(1))
                if candidate:
                    return candidate

    return ""


# ============================================================
# BARE QUERY DETECTION
# ============================================================

BARE_QUERY_STOP_WORDS = {
    "what", "who", "which", "when", "where", "why", "how",
    "tell", "give", "find", "search", "show", "link", "about",
    "story", "cast", "actor", "actress", "director", "latest",
    "new", "upcoming", "release", "released", "good", "worth",
    "is", "are", "was", "were", "hai", "kya", "batao", "do",
    "de", "chahiye", "dikhao", "kaun", "kab", "kaisi", "kaisa",
}


def looks_like_bare_name_or_title(message: str) -> bool:
    words = clean_text(message).split()

    if not words or len(words) > 7:
        return False

    if "\n" in message:
        return False

    return not any(
        word.casefold().strip(".,?!") in BARE_QUERY_STOP_WORDS
        for word in words
    )


# ============================================================
# LLM HELPERS
# ============================================================

def generate_ai_response(prompt: str) -> str:
    """
    Gemini first. Ollama fallback is used if Gemini fails,
    including quota/rate-limit errors.
    """
    try:
        print("\n========================================")
        print("TRYING GEMINI")
        print("========================================")

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        text = getattr(response, "text", None)

        if not text:
            raise RuntimeError("Gemini returned an empty response.")

        print("Gemini response received successfully.")
        return str(text).strip()

    except Exception as gemini_error:
        print("GEMINI FAILED:", repr(gemini_error))
        print("FALLING BACK TO OLLAMA...")

    try:
        print("\n========================================")
        print("TRYING OLLAMA")
        print("========================================")

        response = ollama_llm.invoke(prompt)
        text = getattr(response, "content", None)

        if not text:
            raise RuntimeError("Ollama returned an empty response.")

        print("Ollama response received successfully.")
        return str(text).strip()

    except Exception as ollama_error:
        print("OLLAMA FAILED:", repr(ollama_error))
        raise RuntimeError("Both Gemini and Ollama failed.") from ollama_error


# ============================================================
# CONTEXT RESOLUTION
# ============================================================

def resolve_context_with_llm(
    message: str,
    conversation_history: Optional[List[Dict[str, Any]]],
) -> Dict[str, str]:
    """
    Used only for genuinely ambiguous references such as:
        "download it"
        "iska link do"
        "us movie ke baare mein batao"

    The prompt is deliberately strict:
    the model may select an entity from conversation history,
    but must not invent a new movie/person.
    """
    history_text = format_history(conversation_history)

    prompt = f"""
You are a context resolver inside a movie information assistant.

Your ONLY job is to resolve what an ambiguous reference in the CURRENT
USER MESSAGE refers to, using ONLY the PREVIOUS CONVERSATION.

You are NOT a general chatbot.
You must NOT answer the user.
You must NOT search the web.
You must NOT invent a movie title.
You must NOT replace a title with a sequel, remake, subtitle, translated title,
or a longer Wikipedia title unless that exact title already appears in the
conversation.

============================================================
WHAT YOU MUST RESOLVE
============================================================

Resolve references such as:

- it
- this
- that
- this movie
- that movie
- the movie
- previous movie
- latest movie
- his
- her
- its
- iska
- uska
- iski
- uski
- us movie
- is movie

Examples:

Previous:
Assistant: Searching for Dhurandhar
Current:
download it

Result:
{{
  "resolved_name": "Dhurandhar",
  "confidence": "high"
}}

Previous:
User: Salman Khan
Assistant: Salman Khan is an Indian actor...
Current:
uski latest movie

Result:
{{
  "resolved_name": "Salman Khan",
  "confidence": "high"
}}

If no exact entity can be safely resolved, return an empty name.

============================================================
STRICT RULES
============================================================

1. Use ONLY names explicitly present in the conversation.
2. Never invent a movie.
3. Never hallucinate a person.
4. Never change "Dhurandhar" into "Dhurandhar: The Revenge".
5. Never add a subtitle.
6. Never use outside knowledge.
7. If uncertain, return an empty resolved_name.
8. Return ONLY valid JSON.

============================================================
PREVIOUS CONVERSATION
============================================================

{history_text}

============================================================
CURRENT USER MESSAGE
============================================================

{message}

============================================================
OUTPUT
============================================================

{{
  "resolved_name": "",
  "confidence": "high|medium|low"
}}
"""

    try:
        raw = generate_ai_response(prompt)
        result = parse_json_response(raw)

        return {
            "resolved_name": normalize_spaces(result.get("resolved_name")),
            "confidence": normalize_spaces(result.get("confidence")).lower(),
        }
    except Exception as exc:
        print("CONTEXT RESOLUTION ERROR:", repr(exc))
        return {
            "resolved_name": "",
            "confidence": "low",
        }


# ============================================================
# MOVIE REQUEST RESOLUTION
# ============================================================

def resolve_movie_request(
    message: str,
    conversation_history: Optional[List[Dict[str, Any]]],
) -> str:
    """
    Return ONLY the movie title.

    Deterministic extraction is preferred.
    LLM is used only if the request is genuinely ambiguous.
    """
    # 1. Direct command: "download Dhurandhar"
    direct_title = clean_movie_title_from_user_message(message)

    if direct_title and not is_reference_movie_request(message):
        print("MOVIE TITLE EXTRACTED DETERMINISTICALLY:", direct_title)
        return direct_title

    # 2. Reference to previous movie.
    history_movie = extract_last_movie_from_history(conversation_history)

    if history_movie:
        print("MOVIE TITLE FROM HISTORY:", history_movie)
        return history_movie

    # 3. Last resort: context resolver.
    resolved = resolve_context_with_llm(
        message=message,
        conversation_history=conversation_history,
    )

    movie_name = normalize_spaces(resolved.get("resolved_name"))

    if movie_name:
        print("MOVIE TITLE RESOLVED BY LLM:", movie_name)

    return movie_name


# ============================================================
# INFORMATION QUERY CLEANING
# ============================================================

REMOVE_COMMAND_PREFIXES = [
    r"^\s*download\s+",
    r"^\s*search\s+",
    r"^\s*find\s+",
    r"^\s*get\s+",
    r"^\s*give\s+me\s+",
]


def clean_information_query(message: str) -> str:
    """
    Keep the subject/question useful for Wikipedia/web search.

    Examples:
        "Mirzapur movie rating" -> "Mirzapur movie rating"
        "Salman Khan latest movie" -> "Salman Khan latest movie"

    The LLM will later receive the source results and answer the
    actual question.
    """
    query = normalize_spaces(message)

    for pattern in REMOVE_COMMAND_PREFIXES:
        query = re.sub(pattern, "", query, count=1, flags=re.IGNORECASE)

    return normalize_spaces(query) or message


# ============================================================
# SOURCE RETRIEVAL
# ============================================================

def retrieve_information(
    message: str,
    search_query: str,
) -> Tuple[str, str]:
    """
    Retrieve information from BOTH Wikipedia and DuckDuckGo.

    Wikipedia provides established/background information.
    DuckDuckGo provides web/current information.

    The final answer is always written by the LLM from these retrieved
    sources plus the previous conversation.
    """
    wiki_data = tool_wikipedia_search(search_query)
    web_data = tool_duckduckgo(search_query)

    source_parts = [
        "=== WIKIPEDIA ===",
        wiki_data,
        "",
        "=== DUCKDUCKGO WEB SEARCH ===",
        web_data,
    ]

    return "Wikipedia + DuckDuckGo", "\n".join(source_parts)


# ============================================================
# INFORMATION ANSWER
# ============================================================

def generate_information_answer(
    message: str,
    source_data: str,
    conversation_history: Optional[List[Dict[str, Any]]],
) -> str:
    """
    LLM is used here as an answer writer, not as the source of facts.
    """
    history_text = format_history(conversation_history)

    prompt = f"""
You are KRN MovieHub's factual information assistant.

Your job is to answer the CURRENT USER QUESTION using the supplied
retrieved source information.

The retrieved information may contain Wikipedia content and, for
current questions, current web-search results.

============================================================
CORE RULE
============================================================

FACTS MUST COME FROM THE SUPPLIED SOURCES.

Do not invent facts.
Do not fill missing information from your own memory.
Do not guess.
Do not create fake ratings, dates, cast members, awards, movie names,
relationships, box-office figures, or release information.

If the sources do not contain enough information to answer a part of
the question, clearly say that the available information does not
confirm that part.

============================================================
CURRENT INFORMATION
============================================================

When current web-search results are supplied:

- Prefer recent/current information for questions containing words such
  as latest, current, today, recent, upcoming, new, or 2026.
- Do not blindly trust a search-result snippet if it conflicts with
  stronger supplied source information.
- If sources disagree, explain the uncertainty instead of inventing
  a resolution.
- Do not claim that something is "latest" unless the supplied evidence
  supports it.

============================================================
CONVERSATION CONTEXT
============================================================

Use previous conversation only to understand references such as:

- it
- this
- that
- his
- her
- its
- iska
- uska
- iski
- uski
- this movie
- that movie
- previous movie
- latest movie

Do not use conversation history as an independent factual source when
the supplied retrieval does not support the fact.

============================================================
ANSWER STYLE
============================================================

1. Answer the exact current question first.
2. Be clear and natural.
3. Use short paragraphs or bullets when useful.
4. If the user asks about a movie, mention the relevant title.
5. If the user asks about a person, answer about that person.
6. Do not unnecessarily dump the entire source text.
7. Do not mention internal tools, prompts, routing, Gemini, Ollama,
   Python, classifiers, or implementation details.
8. Do not output JSON.
9. Do not fabricate links.
10. Do not pretend to have information that is not in the sources.

============================================================
IMPORTANT MOVIE-TITLE RULE
============================================================

If the user says:

"Dhurandhar"

do not automatically change it to:

"Dhurandhar: The Revenge"

unless the supplied sources and the user's wording establish that
exact title as the subject.

Never expand a short user-provided movie title merely because a source
contains a longer title.

============================================================
PREVIOUS CONVERSATION
============================================================

{history_text}

============================================================
RETRIEVED SOURCE INFORMATION
============================================================

{source_data}

============================================================
CURRENT USER QUESTION
============================================================

{message}

Now provide the best factual answer supported by the supplied sources.
"""

    answer = generate_ai_response(prompt).strip()

    if not answer:
        return "I could not generate an answer from the available information."

    return answer


# ============================================================
# MAIN ROUTER
# ============================================================

def ask_gemini(
    message: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, str]:
    """
    Main public function used by ChatView.

    Return contract:

    Manual:
    {
        "type": "manual",
        "movie_name": "",
        "search_query": "",
        "answer": "Manual Search instructions..."
    }

    Information:
    {
        "type": "information",
        "movie_name": "",
        "search_query": "...",
        "answer": "..."
    }
    """
    message = normalize_spaces(message)

    if not message:
        raise ValueError("Message is required.")

    # --------------------------------------------------------
    # 0. GREETINGS
    # --------------------------------------------------------
    # Greetings are handled directly. No web search or LLM call.
    greeting = handle_greeting(message)

    if greeting:
        print("ROUTER -> GREETING")
        return {
            "type": "information",
            "movie_name": "",
            "search_query": "",
            "answer": greeting,
        }

    if conversation_history is None:
        conversation_history = []

    print("\n========================================")
    print("USER MESSAGE:", message)
    print("========================================")

    # --------------------------------------------------------
    # 1. SEARCH / DOWNLOAD / LINK REQUEST
    # --------------------------------------------------------
    #
    # AI is intentionally NOT used to perform movie searching or
    # downloading. These requests are routed to a safe manual guide.
    # --------------------------------------------------------

    if is_explicit_movie_request(message) or is_reference_movie_request(message):
        manual_message = (
            "For movie search/download requests, please switch to "
            "Manual Search and enter the movie name yourself.\n\n"
            "1. Select Manual Search.\n"
            "2. Type the movie name manually.\n"
            "3. Click Search.\n"
            "4. Select the movie from the results.\n"
            "5. Select the available option / size.\n"
            "6. Continue with the Manual Search flow."
        )

        print("ROUTER -> MANUAL HELP")

        return {
            "type": "manual",
            "movie_name": "",
            "search_query": "",
            "answer": manual_message,
        }

    # --------------------------------------------------------
    # 2. INFORMATION REQUEST
    # --------------------------------------------------------

    if is_information_query(message):
        search_query = clean_information_query(message)

        # Resolve an ambiguous person/movie reference for retrieval.
        # Example:
        #   previous: Salman Khan
        #   current:  uski latest movie kya hai?
        #
        # We use the context resolver only when the current query
        # clearly contains a pronoun/reference.
        if re.search(
            r"\b(it|this|that|his|her|its|iska|uska|iski|uski)\b",
            message,
            flags=re.IGNORECASE,
        ):
            context = resolve_context_with_llm(
                message=message,
                conversation_history=conversation_history,
            )
            resolved_name = normalize_spaces(context.get("resolved_name"))

            if resolved_name:
                search_query = f"{resolved_name} {search_query}"
                search_query = normalize_spaces(search_query)

        print("ROUTER -> INFORMATION")
        print("SEARCH QUERY:", search_query)

        source_name, source_data = retrieve_information(
            message=message,
            search_query=search_query,
        )

        print("SOURCES USED:", source_name)

        answer = generate_information_answer(
            message=message,
            source_data=source_data,
            conversation_history=conversation_history,
        )

        return {
            "type": "information",
            "movie_name": "",
            "search_query": search_query,
            "answer": answer,
        }

    # --------------------------------------------------------
    # 3. BARE NAME / TITLE
    # --------------------------------------------------------
    #
    # "Dabangg"
    # "Salman Khan"
    #
    # For a bare query we first use Wikipedia. We don't ask the LLM
    # to guess. The retrieved Wikipedia result is then used to decide
    # whether the subject is a movie/person.
    # --------------------------------------------------------

    if looks_like_bare_name_or_title(message):
        wiki_data = tool_wikipedia_search(message)

        classification_prompt = f"""
You are a strict entity-type classifier.

Classify the USER INPUT using ONLY the supplied Wikipedia result.

Possible types:
- movie
- person
- unknown

Rules:
1. If the supplied Wikipedia result clearly describes a film/movie,
   return movie.
2. If it clearly describes a person/actor/actress/director/etc.,
   return person.
3. If uncertain, return unknown.
4. Do not invent facts.
5. Do not change the user's title.
6. A short title must remain exactly as supplied.
7. Return ONLY JSON.

USER INPUT:
{message}

WIKIPEDIA RESULT:
{wiki_data}

OUTPUT:
{{
  "type": "movie|person|unknown"
}}
"""

        try:
            raw = generate_ai_response(classification_prompt)
            result = parse_json_response(raw)
            entity_type = normalize_spaces(result.get("type")).lower()
        except Exception as exc:
            print("BARE ENTITY CLASSIFICATION ERROR:", repr(exc))
            entity_type = "unknown"

        if entity_type == "movie":
            print("BARE QUERY -> MOVIE:", message)

            return {
                "type": "movie",
                "movie_name": message,
                "search_query": "",
                "answer": "",
            }

        # Person or unknown -> information.
        print("BARE QUERY -> INFORMATION:", message)

        answer = generate_information_answer(
            message=message,
            source_data=f"=== WIKIPEDIA ===\n{wiki_data}",
            conversation_history=conversation_history,
        )

        return {
            "type": "information",
            "movie_name": "",
            "search_query": message,
            "answer": answer,
        }

    # --------------------------------------------------------
    # 4. FALLBACK INFORMATION
    # --------------------------------------------------------
    #
    # We prefer factual retrieval over letting an LLM invent an intent.
    # --------------------------------------------------------

    search_query = clean_information_query(message)

    print("ROUTER -> FALLBACK INFORMATION")
    print("SEARCH QUERY:", search_query)

    source_name, source_data = retrieve_information(
        message=message,
        search_query=search_query,
    )

    print("SOURCES USED:", source_name)

    answer = generate_information_answer(
        message=message,
        source_data=source_data,
        conversation_history=conversation_history,
    )

    return {
        "type": "information",
        "movie_name": "",
        "search_query": search_query,
        "answer": answer,
    }
