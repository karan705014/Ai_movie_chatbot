import { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000/api";

export default function ManualSearch({
  initialQuery = "",
}) {
  const [query, setQuery] = useState(initialQuery);

  const [movies, setMovies] = useState([]);

  const [loading, setLoading] = useState(false);

  const [selectionLoading, setSelectionLoading] =
    useState(false);

  const [sizeLoading, setSizeLoading] =
    useState(false);

  const [error, setError] = useState("");

  const [selectedMovie, setSelectedMovie] =
    useState(null);

  const [movieSizes, setMovieSizes] =
    useState([]);

  const [finalLink, setFinalLink] =
    useState("");


  /* =========================
     AI SE MOVIE NAME AAYA
  ========================= */

  useEffect(() => {
    const movieName = initialQuery?.trim();

    if (!movieName) {
      return;
    }

    setQuery(movieName);

    handleSearch(movieName);
  }, [initialQuery]);


  /* =========================
     MOVIE SEARCH
  ========================= */

  const handleSearch = async (
    searchQuery = query
  ) => {
    const searchValue = searchQuery.trim();

    if (!searchValue) {
      return;
    }

    setLoading(true);

    setError("");

    setMovies([]);

    setSelectedMovie(null);

    setMovieSizes([]);

    setFinalLink("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/search/?q=${encodeURIComponent(
          searchValue
        )}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.error ||
            "Search failed."
        );
      }

      setMovies(
        data?.results || []
      );

    } catch (err) {
      console.error(
        "SEARCH ERROR:",
        err
      );

      setError(
        err.message ||
          "Failed to search movies."
      );

    } finally {
      setLoading(false);
    }
  };


  /* =========================
     MOVIE SELECT
  ========================= */

  const handleMovieSelect = async (
    movie
  ) => {
    if (!movie?.url) {
      setError(
        "Selected movie has no valid URL."
      );

      return;
    }

    setSelectedMovie(movie);

    setMovieSizes([]);

    setFinalLink("");

    setError("");

    setSelectionLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/movie/selected/`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            movie_url: movie.url,
          }),
        }
      );

      const data =
        await response.json();

      console.log(
        "MOVIE SELECTION RESPONSE:",
        data
      );

      if (!response.ok) {
        throw new Error(
          data?.error ||
            "Failed to load movie options."
        );
      }

      setMovieSizes(
        data?.movie_size || []
      );

    } catch (err) {
      console.error(
        "MOVIE SELECTION ERROR:",
        err
      );

      setError(
        err.message ||
          "Failed to load movie options."
      );

    } finally {
      setSelectionLoading(false);
    }
  };


  /* =========================
     OPTION / SIZE SELECT
  ========================= */

  const handleSizeSelect = async (
    option
  ) => {
    console.log(
      "CLICKED OPTION:",
      option
    );

    const selectedUrl =
      option?.url ||
      option?.href;

    console.log(
      "SELECTED URL:",
      selectedUrl
    );

    if (!selectedUrl) {
      setError(
        "Selected option has no valid URL."
      );

      return;
    }

    setSizeLoading(true);

    setError("");

    setFinalLink("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/movie/size/selected/`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            movie_size_url:
              selectedUrl,
          }),
        }
      );

      const data =
        await response.json();

      console.log(
        "SIZE API RESPONSE:",
        data
      );

      if (!response.ok) {
        throw new Error(
          data?.error ||
            "Failed to process selected option."
        );
      }

      setFinalLink(
        data?.final_link || ""
      );

    } catch (err) {
      console.error(
        "SIZE SELECTION ERROR:",
        err
      );

      setError(
        err.message ||
          "Failed to process selected option."
      );

    } finally {
      setSizeLoading(false);
    }
  };


  return (
    <section className="max-w-5xl mx-auto">

      {/* =========================
          SEARCH BOX
      ========================= */}

      <div className="flex flex-col sm:flex-row gap-3 p-2 rounded-2xl bg-white/[0.05] border border-white/10 shadow-2xl shadow-purple-950/20 backdrop-blur-xl">

        <input
          type="text"
          placeholder="Search a movie..."
          value={query}
          onChange={(e) =>
            setQuery(e.target.value)
          }
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleSearch();
            }
          }}
          className="flex-1 min-w-0 px-5 py-4 rounded-xl bg-slate-900/70 border border-white/10 text-white placeholder-slate-500 outline-none focus:border-purple-400/60 focus:ring-2 focus:ring-purple-500/20 transition"
        />

        <button
          type="button"
          onClick={() =>
            handleSearch()
          }
          disabled={loading}
          className="px-7 py-4 rounded-xl bg-gradient-to-r from-purple-600 via-pink-600 to-cyan-500 font-bold text-white shadow-lg shadow-purple-600/20 hover:scale-[1.02] active:scale-[0.98] transition disabled:opacity-50 disabled:cursor-not-allowed"
        >

          {loading ? (
            <span className="flex items-center justify-center gap-2">

              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />

              Searching...

            </span>
          ) : (
            "Search"
          )}

        </button>

      </div>


      {/* =========================
          ERROR
      ========================= */}

      {error && (
        <div className="mt-6">

          <div className="flex items-start gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300">

            <span className="text-lg">
              ⚠️
            </span>

            <p className="text-sm">
              {error}
            </p>

          </div>

        </div>
      )}


      {/* =========================
          SEARCH RESULTS
      ========================= */}

      {movies.length > 0 && (
        <section className="mt-10">

          <div className="flex items-center justify-between mb-5">

            <div>

              <h2 className="text-2xl font-bold">
                Search Results
              </h2>

              <p className="text-sm text-slate-500 mt-1">

                {movies.length} movie
                {movies.length !== 1
                  ? "s"
                  : ""}{" "}
                found

              </p>

            </div>

          </div>


          <div className="grid gap-4">

            {movies.map(
              (movie, index) => (
                <button
                  type="button"
                  key={
                    movie.url ||
                    index
                  }
                  onClick={() =>
                    handleMovieSelect(
                      movie
                    )
                  }
                  className="group w-full text-left p-5 rounded-2xl bg-white/[0.04] border border-white/10 hover:border-purple-400/40 hover:bg-purple-500/[0.06] hover:shadow-xl hover:shadow-purple-950/20 transition-all duration-200"
                >

                  <div className="flex items-center gap-4">

                    <div className="flex shrink-0 items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-purple-600/30 to-cyan-500/20 border border-white/10 text-xl">
                      🎬
                    </div>


                    <div className="min-w-0 flex-1">

                      <h3 className="font-semibold text-white text-base sm:text-lg leading-snug group-hover:text-purple-300 transition">
                        {movie.title}
                      </h3>

                      <p className="mt-1 text-sm text-slate-500">
                        Click to view available options
                      </p>

                    </div>


                    <div className="shrink-0 w-9 h-9 flex items-center justify-center rounded-full bg-white/5 text-slate-500 group-hover:bg-purple-500/20 group-hover:text-purple-300 group-hover:translate-x-1 transition">
                      →
                    </div>

                  </div>

                </button>
              )
            )}

          </div>

        </section>
      )}


      {/* =========================
          LOADING SEARCH
      ========================= */}

      {loading && (
        <div className="flex justify-center py-12">

          <div className="flex items-center gap-3 text-slate-400">

            <span className="w-5 h-5 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />

            Searching movies...

          </div>

        </div>
      )}


      {/* =========================
          NO RESULTS
      ========================= */}

      {!loading &&
        query.trim() &&
        movies.length === 0 &&
        !error && (
          <div className="py-14 text-center rounded-2xl bg-white/[0.03] border border-dashed border-white/10 mt-8">

            <div className="text-4xl mb-3">
              🎞️
            </div>

            <p className="text-slate-400">
              No movies found.
            </p>

            <p className="text-sm text-slate-600 mt-1">
              Try searching with another movie name.
            </p>

          </div>
        )}


      {/* =========================
          SELECTED MOVIE
      ========================= */}

      {selectedMovie && (
        <section className="mt-12">

          <div className="relative overflow-hidden p-6 rounded-3xl bg-gradient-to-r from-purple-600/15 via-pink-500/10 to-cyan-500/10 border border-white/10">

            <div className="relative z-10">

              <div className="flex items-center gap-3 mb-3">

                <div className="w-11 h-11 flex items-center justify-center rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 shadow-lg shadow-purple-500/20">
                  🎬
                </div>

                <div>

                  <p className="text-xs uppercase tracking-wider text-purple-300 font-semibold">
                    Selected Movie
                  </p>

                  <h2 className="text-lg sm:text-2xl font-bold">
                    {selectedMovie.title}
                  </h2>

                </div>

              </div>

              <p className="text-sm text-slate-400">
                Select an available option below
              </p>

            </div>

          </div>


          {/* =========================
              MOVIE OPTIONS LOADING
          ========================= */}

          {selectionLoading && (
            <div className="mt-5 p-8 rounded-2xl bg-white/[0.03] border border-white/10 text-center">

              <div className="mx-auto mb-4 w-8 h-8 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />

              <p className="text-slate-400">
                Loading movie options...
              </p>

            </div>
          )}


          {/* =========================
              MOVIE OPTIONS
          ========================= */}

          {!selectionLoading &&
            movieSizes.length > 0 && (
              <div className="mt-5">

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">

                  {movieSizes.map(
                    (option, index) => (
                      <button
                        type="button"
                        key={
                          option.option_id ||
                          option.url ||
                          index
                        }
                        onClick={() =>
                          handleSizeSelect(
                            option
                          )
                        }
                        disabled={
                          sizeLoading
                        }
                        className="group relative overflow-hidden p-5 rounded-2xl text-left bg-slate-900/70 border border-white/10 hover:border-cyan-400/40 hover:bg-cyan-500/[0.05] hover:-translate-y-1 hover:shadow-xl hover:shadow-cyan-950/20 transition-all duration-200 disabled:opacity-50 disabled:cursor-wait"
                      >

                        <div className="flex items-center justify-between gap-3">

                          <div className="min-w-0">

                            <div className="inline-flex items-center px-3 py-1 rounded-full bg-purple-500/10 border border-purple-400/20 text-purple-300 text-xs font-semibold mb-3">
                              OPTION{" "}
                              {index + 1}
                            </div>

                            <strong className="block text-sm sm:text-base text-white leading-relaxed">
                              {option.label}
                            </strong>

                            {option.size && (
                              <span className="block mt-2 text-xs text-slate-500">
                                {option.size}
                              </span>
                            )}

                          </div>


                          <span className="shrink-0 w-10 h-10 flex items-center justify-center rounded-full bg-white/5 text-slate-500 group-hover:bg-cyan-500/15 group-hover:text-cyan-300 group-hover:translate-x-1 transition">
                            →
                          </span>

                        </div>

                      </button>
                    )
                  )}

                </div>

              </div>
            )}


          {/* =========================
              SIZE LOADING
          ========================= */}

          {sizeLoading && (
            <div className="mt-5 flex items-center justify-center gap-3 p-5 rounded-2xl bg-cyan-500/5 border border-cyan-400/10 text-cyan-300">

              <span className="w-5 h-5 border-2 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin" />

              Processing selected option...

            </div>
          )}


          {/* =========================
              NO OPTIONS
          ========================= */}

          {!selectionLoading &&
            !sizeLoading &&
            movieSizes.length === 0 &&
            !error && (
              <div className="mt-5 p-10 text-center rounded-2xl bg-white/[0.03] border border-dashed border-white/10">

                <div className="text-3xl mb-3">
                  📭
                </div>

                <p className="text-slate-400">
                  No options available.
                </p>

              </div>
            )}


          {/* =========================
              FINAL LINK
          ========================= */}

          {finalLink && (
            <div className="mt-6 p-6 rounded-2xl bg-gradient-to-r from-green-500/10 to-cyan-500/10 border border-green-400/20">

              <div className="flex items-center gap-3 mb-4">

                <div className="w-10 h-10 flex items-center justify-center rounded-full bg-green-500/15 text-green-400">
                  ✓
                </div>

                <div>

                  <h3 className="font-bold text-white">
                    Result Ready
                  </h3>

                  <p className="text-xs text-slate-500">
                    Backend returned a result successfully.
                  </p>

                </div>

              </div>


              <a
                href={finalLink}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-green-500 to-cyan-500 text-white font-bold hover:scale-[1.02] transition"
              >
                Open Result →
              </a>

            </div>
          )}

        </section>
      )}

    </section>
  );
}