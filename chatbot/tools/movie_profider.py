MOCK_OPTIONS = {
    "toxic": [
        {
            "option_id": "toxic-480",
            "label": "480p",
            "size": "500 MB",
            "url": "https://example.com/videos/toxic-480.mp4",
        },
        {
            "option_id": "toxic-720",
            "label": "720p",
            "size": "1.2 GB",
            "url": "https://example.com/videos/toxic-720.mp4",
        },
        {
            "option_id": "toxic-1080",
            "label": "1080p",
            "size": "2.4 GB",
            "url": "https://example.com/videos/toxic-1080.mp4",
        },
    ]
}


def get_movie_options(movie_url: str):
    movie_name = movie_url.lower()

    if "toxic" in movie_name:
        return [
            {
                "option_id": option["option_id"],
                "label": option["label"],
                "size": option["size"],
            }
            for option in MOCK_OPTIONS["toxic"]
        ]

    return []


def resolve_movie_option(option_id: str):
    for options in MOCK_OPTIONS.values():
        for option in options:
            if option["option_id"] == option_id:
                return option["url"]

    return None