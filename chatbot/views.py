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

class ChatHistoryView(APIView):
    """
    Return the current session chat history.

    The same session history is passed to ask_gemini() by ChatView,
    so it is used both for UI display and AI context.
    """

    def get(self, request):
        history = request.session.get(
            "movie_chat_history",
            [],
        )

        return Response(
            {
                "success": True,
                "messages": history,
            },
            status=status.HTTP_200_OK,
        )


class ChatView(APIView):

    def post(self, request):

        message = request.data.get(
            "message",
            "",
        ).strip()

        if not message:
            return Response(
                {
                    "success": False,
                    "error": "Message is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # --------------------------------------------------
            # Get previous conversation
            # --------------------------------------------------

            session_history = request.session.get(
                "movie_chat_history",
                [],
            )

            # The frontend also sends the complete visible chat.
            # Prefer it when valid so the AI gets the same conversation
            # the user sees, even if the browser/session state was stale.
            client_history = request.data.get(
                "conversation_history",
                None,
            )

            if isinstance(client_history, list):
                history = [
                    item
                    for item in client_history
                    if isinstance(item, dict)
                    and item.get("role") in {"user", "assistant"}
                    and str(item.get("content", "")).strip()
                ]
            else:
                history = list(session_history)

            # The current user message is already present in the frontend
            # history. Remove that one copy before sending context to the AI,
            # because ChatView adds it to the stored history after the answer.
            history_for_ai = history
            if (
                history_for_ai
                and history_for_ai[-1].get("role") == "user"
                and str(history_for_ai[-1].get("content", "")).strip() == message
            ):
                history_for_ai = history_for_ai[:-1]

            print(
                "PREVIOUS HISTORY:",
                history_for_ai,
            )

            # --------------------------------------------------
            # Ask AI with previous conversation as context
            # --------------------------------------------------

            result = ask_gemini(
                message=message,
                conversation_history=history_for_ai,
            )

            print(
                "AI RESULT:",
                result,
            )

            result_type = result.get("type")

            # --------------------------------------------------
            # INFORMATION / MANUAL RESPONSE
            # --------------------------------------------------

            if result_type in {"information", "manual"}:

                answer = result.get(
                    "answer",
                    "",
                ).strip()

                if not answer:
                    return Response(
                        {
                            "success": False,
                            "error": "AI returned an empty response.",
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                # Save both sides of the conversation.
                history = list(history_for_ai)

                history.append(
                    {
                        "role": "user",
                        "content": message,
                    }
                )

                history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                # Keep the latest 20 messages.
                request.session[
                    "movie_chat_history"
                ] = history

                request.session.modified = True

                return Response(
                    {
                        "success": True,
                        "mode": (
                            "ai"
                            if result_type == "information"
                            else "manual"
                        ),
                        "message": answer,
                    },
                    status=status.HTTP_200_OK,
                )

            # --------------------------------------------------
            # OLD MOVIE RESPONSE COMPATIBILITY
            # --------------------------------------------------
            #
            # The new AI service should not return "movie" for
            # download/search requests. This branch is retained so
            # the existing API does not unexpectedly break if an
            # older gemini_service.py is temporarily used.
            # --------------------------------------------------

            if result_type == "movie":

                movie_name = result.get(
                    "movie_name",
                    "",
                ).strip()

                if not movie_name:
                    return Response(
                        {
                            "success": False,
                            "error": "Could not identify movie.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                history.append(
                    {
                        "role": "user",
                        "content": message,
                    }
                )

                history.append(
                    {
                        "role": "assistant",
                        "content": (
                            f"Searching for {movie_name}..."
                        ),
                    }
                )

                request.session[
                    "movie_chat_history"
                ] = history

                request.session.modified = True

                return Response(
                    {
                        "success": True,
                        "mode": "movie",
                        "movie_name": movie_name,
                        "message": (
                            f"Searching for {movie_name}..."
                        ),
                    },
                    status=status.HTTP_200_OK,
                )

            # --------------------------------------------------
            # Invalid AI response
            # --------------------------------------------------

            return Response(
                {
                    "success": False,
                    "error": "Invalid AI response.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ======================================================
        # GEMINI QUOTA ERROR
        # ======================================================

        except RuntimeError as exc:

            error_message = str(exc)

            if "quota exceeded" in error_message.lower():

                print(
                    "GEMINI QUOTA ERROR:",
                    error_message,
                )

                return Response(
                    {
                        "success": False,
                        "error": error_message,
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            print(
                "RUNTIME ERROR:",
                repr(exc),
            )

            traceback.print_exc()

            return Response(
                {
                    "success": False,
                    "error": "AI request failed.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ======================================================
        # OTHER ERRORS
        # ======================================================

        except Exception as exc:

            print(
                "CHAT ERROR:",
                repr(exc),
            )

            traceback.print_exc()

            return Response(
                {
                    "success": False,
                    "error": "AI request failed.",
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
            final_url = get_final_link(movie_size_url)

            print("Final href:", final_url)

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