from django.urls import path

from .views import (
    ChatView,
    ChatHistoryView,
    MovieSearchView,
    MovieSelectionNext,
    MovieSizeSelection,
)

urlpatterns = [
    path("chat/", ChatView.as_view(), name="chat"),
    path("chat/history/", ChatHistoryView.as_view(), name="chat-history"),
    path("search/", MovieSearchView.as_view(), name="search"),
    path("movie/selected/", MovieSelectionNext.as_view(), name="movie-options"),
    path("movie/size/selected/", MovieSizeSelection.as_view(), name="movie-size-options"),
]
