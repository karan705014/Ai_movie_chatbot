import traceback

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from playwright.sync_api import sync_playwright
from .tools.movie_search import (
    movie_search,
    extract_search_query,
    select_movie,
    select_movie_size,
    get_final_link,
)

from .gemini_service import ask_gemini


class ChatView(APIView):

    def post(self, request):
        message = request.data.get("message", "").strip()

        if not message:
            return Response(
                {
                    "success": False,
                    "error": "Message is required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Try AI first.
        try:
            answer = ask_gemini(message)

            return Response(
                {
                    "success": True,
                    "mode": "ai",
                    "message": answer,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as ai_error:
            print("AI ERROR:", repr(ai_error))
            traceback.print_exc()

        # Use manual search if AI fails.
        query = extract_search_query(message)

        if not query:
            return Response(
                {
                    "success": False,
                    "mode": "manual_fallback",
                    "error": "Could not understand the movie search query.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            results = movie_search(query)

            return Response(
                {
                    "success": True,
                    "mode": "manual_fallback",
                    "query": query,
                    "message": (
                        "AI is currently unavailable. "
                        "Manual search was used."
                    ),
                    "results": results,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as search_error:
            print("MANUAL SEARCH ERROR:", repr(search_error))
            traceback.print_exc()

            return Response(
                {
                    "success": False,
                    "mode": "error",
                    "error": "Both AI and manual search failed.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MovieSearchView(APIView):

    def get(self, request):
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response(
                {
                    "success": False,
                    "error": "Search query is required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            results = movie_search(query)

            return Response(
                {
                    "success": True,
                    "mode": "manual",
                    "query": query,
                    "results": results,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            print("MOVIE SEARCH ERROR:", repr(exc))
            traceback.print_exc()

            return Response(
                {
                    "success": False,
                    "mode": "manual",
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MovieSelectionNext(APIView):

    def post(self, request):
        movie_url = request.data.get("movie_url", "").strip()

        if not movie_url:
            return Response(
                {
                    "success": False,
                    "error": "Movie URL is required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            next_url = select_movie(movie_url)

            if not next_url:
                return Response(
                    {
                        "success": False,
                        "error": "Movie selection URL was not found.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            movie_size = select_movie_size(next_url)

            return Response(
                {
                    "success": True,
                    "movie_size": movie_size,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            print("MOVIE SELECTION ERROR:", repr(exc))
            traceback.print_exc()

            return Response(
                {
                    "success": False,
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MovieSizeSelection(APIView):

    def post(self, request):
        movie_size_url = request.data.get("movie_size_url", "").strip()

        if not movie_size_url:
            return Response(
                {
                    "success": False,
                    "error": "Movie size URL is required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                final_url = get_final_link(
                    page,
                    movie_size_url,
                )

                print("Final href:", final_url)

                browser.close()

            return Response(
                {
                    "success": True,
                    "final_link": final_url,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            print(
                "MOVIE SIZE SELECTION ERROR:",
                repr(exc),
            )
            traceback.print_exc()

            return Response(
                {
                    "success": False,
                    "error": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )