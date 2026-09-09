import os
import re
import bs4
import requests
from bs4 import BeautifulSoup
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from .tools.movie_search import movie_search_tool

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

WIKIPEDIA_HEADERS = {
    "User-Agent": "AI-Movie-Chatbot/1.0 (movie information assistant)"
}


@tool
def wikipedia_movie_search(query: str) -> str:
    """
    Search Wikipedia for factual information about movies,
    actors, directors, characters, or other people.
    """
    try:
        response = requests.get(
            WIKIPEDIA_API_URL,
            headers=WIKIPEDIA_HEADERS,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "utf8": 1,
                "srlimit": 3,
            },
            timeout=10,
        )

        response.raise_for_status()
        data = response.json()

        search_results = data.get("query", {}).get("search", [])

        if not search_results:
            return f"No Wikipedia results found for: {query}"

        output = []

        for item in search_results:
            title = item.get("title", "")
            raw_snippet = item.get("snippet", "")

            # Strip HTML tags from Wikipedia API snippet
            clean_snippet = BeautifulSoup(raw_snippet, "html.parser").get_text()

            output.append(
                f"Title: {title}\n"
                f"Information: {clean_snippet}"
            )

        return "\n\n".join(output)

    except requests.RequestException as exc:
        return f"Wikipedia request failed: {exc}"

    except ValueError:
        return "Wikipedia returned an invalid response."

    except Exception as exc:
        return f"Wikipedia tool failed: {exc}"


# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0,
)

tools = [movie_search_tool, wikipedia_movie_search]

# Define ReAct Agent Prompt Format
template = """
You are a helpful movie information assistant.

Your job is to understand the user's request and choose the correct tool when necessary.

Use the Wikipedia tool when the user asks for factual information about:
- a movie
- an actor / actress / director / character / person related to a movie

Use the movie search tool when the user wants to search for a movie.

For movie search requests, extract the actual movie name from the user's natural-language request before calling the movie search tool.

Examples:
User: "give me Toxic movie" -> Movie search query: "Toxic"
User: "find Toxic 2026" -> Movie search query: "Toxic 2026"
User: "search for KGF" -> Movie search query: "KGF"

Do not invent facts.
If Wikipedia does not provide enough information, say that the information could not be verified.
For normal conversation, answer directly.

You have access to the following tools:
{tools}

To use a tool, please use the following format:
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final response to the user

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

prompt = PromptTemplate.from_template(template)

# Create ReAct Agent and Executor
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=False,
    handle_parsing_errors=True
)


def ask_gemini(message: str) -> str:
    """
    Send the user's message to the AI movie agent.
    """
    try:
        response = agent_executor.invoke({"input": message})
        return response.get("output", "Sorry, I could not process your request.")
    except Exception as exc:
        print("Agent invocation error:", exc)
        return "An error occurred while generating response."