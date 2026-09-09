import { useEffect, useRef, useState } from "react";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export default function ManualSearch({ initialQuery = "" }) {
    const [query, setQuery] = useState(initialQuery);
    const [movies, setMovies] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectionLoading, setSelectionLoading] = useState(false);
    const [sizeLoading, setSizeLoading] = useState(false);
    const [error, setError] = useState("");
    const [selectedMovie, setSelectedMovie] = useState(null);
    const [movieSizes, setMovieSizes] = useState([]);
    const [finalLink, setFinalLink] = useState("");
    const [hasSearched, setHasSearched] = useState(false);

    const resultsRef = useRef(null);
    const selectedMovieRef = useRef(null);
    const optionsRef = useRef(null);
    const finalResultRef = useRef(null);


    /* =========================
       AI MOVIE AUTO SEARCH
    ========================= */

    useEffect(() => {
        const movieName = initialQuery?.trim();

        if (!movieName) return;

        setQuery(movieName);
        handleSearch(movieName);
    }, [initialQuery]);


    /* =========================
       AUTO SCROLL - RESULTS
    ========================= */

    useEffect(() => {
        if (!loading && movies.length > 0) {
            requestAnimationFrame(() => {
                resultsRef.current?.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                });
            });
        }
    }, [movies, loading]);


    /* =========================
       AUTO SCROLL - SELECTED
    ========================= */

    useEffect(() => {
        if (!selectionLoading && selectedMovie) {
            requestAnimationFrame(() => {
                selectedMovieRef.current?.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                });
            });
        }
    }, [selectedMovie, selectionLoading]);


    /* =========================
       AUTO SCROLL - OPTIONS
    ========================= */

    useEffect(() => {
        if (!selectionLoading && movieSizes.length > 0) {
            requestAnimationFrame(() => {
                optionsRef.current?.scrollIntoView({
                    behavior: "smooth",
                    block: "center",
                });
            });
        }
    }, [movieSizes, selectionLoading]);


    /* =========================
       AUTO SCROLL - FINAL
    ========================= */

    useEffect(() => {
        if (!sizeLoading && finalLink) {
            requestAnimationFrame(() => {
                finalResultRef.current?.scrollIntoView({
                    behavior: "smooth",
                    block: "center",
                });
            });
        }
    }, [finalLink, sizeLoading]);


    /* =========================
       STEP 1
       SEARCH MOVIE
    ========================= */

    const handleSearch = async (searchValue = query) => {
        const searchQuery = searchValue.trim();

        if (!searchQuery || loading) return;

        setLoading(true);
        setError("");
        setHasSearched(false);

        setMovies([]);
        setSelectedMovie(null);
        setMovieSizes([]);
        setFinalLink("");

        try {
            const response = await fetch(
                `${API_BASE_URL}/search/?q=${encodeURIComponent(searchQuery)}`
            );

            const data = await response.json();

            console.log("SEARCH RESPONSE:", data);

            if (!response.ok) {
                throw new Error(
                    data?.error || "Search failed."
                );
            }

            setMovies(data?.results || []);
            setHasSearched(true);

        } catch (err) {
            console.error("SEARCH ERROR:", err);

            setError(
                err?.message ||
                "Failed to search movies."
            );

        } finally {
            setLoading(false);
        }
    };


    /* =========================
       STEP 2
       SELECT MOVIE
    ========================= */

    const handleMovieSelect = async (movie) => {
        if (!movie?.url) {
            setError("Selected movie has no valid URL.");
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
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        movie_url: movie.url,
                    }),
                }
            );

            const data = await response.json();

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

            setMovieSizes(data?.movie_size || []);

        } catch (err) {
            console.error(
                "MOVIE SELECTION ERROR:",
                err
            );

            setError(
                err?.message ||
                "Failed to load movie options."
            );

        } finally {
            setSelectionLoading(false);
        }
    };


    /* =========================
       STEP 3
       SELECT SIZE
    ========================= */

    const handleSizeSelect = async (option) => {
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
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        movie_size_url: selectedUrl,
                    }),
                }
            );

            const data = await response.json();

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
                err?.message ||
                "Failed to process selected option."
            );

        } finally {
            setSizeLoading(false);
        }
    };


    return (
        <section className="w-full min-w-0 max-w-5xl mx-auto px-2 sm:px-0 overflow-x-clip">

            {/* SEARCH */}

            <div className="w-full max-w-3xl mx-auto mb-8 sm:mb-10">

                <div className="relative w-full min-w-0 flex gap-1.5 sm:gap-3 p-1.5 sm:p-2 rounded-2xl bg-white/[0.035] backdrop-blur-2xl border border-white/[0.10]">

                    <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-r from-[#39ff14]/[0.025] via-[#7CFFB2]/[0.035] to-[#67dfff]/[0.025]" />

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
                        disabled={loading}
                        className="relative flex-1 min-w-0 w-0 px-3 sm:px-5 py-3.5 sm:py-4 rounded-xl bg-black/40 border border-white/[0.08] text-white text-xs sm:text-base placeholder:text-white/25 outline-none focus:border-[#39ff14]/40"
                    />
                    <button
                        type="button"
                        onClick={() => handleSearch()}
                        disabled={loading || !query.trim()}
                        className="group relative shrink-0 min-w-[92px] sm:min-w-[125px] h-[52px] sm:h-[58px] rounded-xl overflow-hidden
               bg-[#39ff14]/[0.08]
               border border-[#39ff14]/40
               text-[#39ff14]
               font-bold text-xs sm:text-base
               shadow-[0_0_20px_rgba(57,255,20,0.12),inset_0_0_18px_rgba(57,255,20,0.04)]
               hover:border-[#39ff14]/70
               hover:shadow-[0_0_30px_rgba(57,255,20,0.28),inset_0_0_25px_rgba(57,255,20,0.08)]
               active:scale-[0.97]
               transition-all duration-300
               disabled:opacity-30 disabled:cursor-not-allowed"
                    >
                        {/* Animated neon background */}
                        <span className="absolute inset-[1px] rounded-[11px] bg-gradient-to-br from-[#39ff14]/20 via-[#39ff14]/[0.06] to-transparent opacity-70 group-hover:opacity-100 transition-opacity duration-300" />

                        {/* Top shine */}
                        <span className="absolute top-0 left-[15%] right-[15%] h-px bg-gradient-to-r from-transparent via-[#9affc8] to-transparent opacity-70" />

                        {/* Hover scanning line */}
                        <span className="absolute inset-y-0 w-8 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 -translate-x-20 group-hover:translate-x-[180px] transition-transform duration-700" />

                        {/* Button content */}
                        {loading ? (
                            <span className="relative z-10 flex items-center justify-center gap-2 h-full">
                                <span className="w-4 h-4 sm:w-5 sm:h-5 border-2 border-[#39ff14]/25 border-t-[#39ff14] rounded-full animate-spin" />

                                <span className="hidden sm:inline text-[#9affc8]">
                                    Searching
                                </span>

                                <span className="sm:hidden text-[#9affc8]">
                                    ...
                                </span>
                            </span>
                        ) : (
                            <span className="relative z-10 flex items-center justify-center gap-2 h-full">

                            

                                <span className="hidden sm:inline tracking-wide">
                                    Search
                                </span>

                            </span>
                        )}
                    </button>

                </div>
            </div>


            {/* ERROR */}

            {error && (
                <div className="max-w-3xl mx-auto mb-8">
                    <div className="flex items-start gap-3 p-4 rounded-2xl bg-red-500/[0.045] border border-red-400/20 text-red-300">
                        <span>⚠️</span>
                        <p className="text-sm leading-6">
                            {error}
                        </p>
                    </div>
                </div>
            )}


            {/* LOADING */}

            {loading && (
                <div className="flex justify-center py-12">
                    <div className="flex items-center gap-3 px-5 py-3 rounded-full bg-white/[0.035] border border-white/[0.08] text-white/45">
                        <span className="w-5 h-5 border-2 border-[#39ff14]/20 border-t-[#39ff14] rounded-full animate-spin" />
                        Searching movies...
                    </div>
                </div>
            )}


            {/* RESULTS */}

            {movies.length > 0 && (
                <section
                    ref={resultsRef}
                    className="animate-[slideUp_0.4s_ease-out]"
                >

                    <div className="mb-5 flex items-end justify-between gap-3">

                        <div>
                            <p className="text-[10px] sm:text-xs uppercase tracking-[0.22em] text-[#6dff9b]/65 font-semibold mb-1">
                                Movies
                            </p>

                            <h2 className="text-xl sm:text-2xl font-bold text-white">
                                Search Results
                            </h2>
                        </div>

                        <span className="shrink-0 px-3 py-1.5 rounded-full bg-[#39ff14]/[0.06] border border-[#7CFFB2]/20 text-[#72ff9f] text-xs font-semibold">
                            {movies.length} found
                        </span>

                    </div>


                    <div className="grid gap-3 sm:gap-4">

                        {movies.map((movie, index) => (

                            <button
                                type="button"
                                key={
                                    movie.url ||
                                    index
                                }
                                onClick={() =>
                                    handleMovieSelect(movie)
                                }
                                disabled={
                                    selectionLoading
                                }
                                className="group relative w-full min-w-0 text-left overflow-hidden p-3 sm:p-4 rounded-2xl bg-gradient-to-br from-[#b8ffd0]/[0.055] via-[#0aff78]/[0.025] to-[#67dfff]/[0.035] border border-[#8affb5]/[0.18] shadow-[0_10px_35px_rgba(0,0,0,0.35)] hover:border-[#7CFFB2]/40 hover:-translate-y-1 transition-all duration-300 disabled:opacity-40"
                            >

                                <div className="relative min-w-0 flex items-center gap-2 sm:gap-4">

                                    {/* POSTER */}

                                    {movie.image ? (
                                        <div className="relative shrink-0 w-16 h-20 sm:w-20 sm:h-24 overflow-hidden rounded-xl border border-[#8affb5]/20 bg-black/30">

                                            <img
                                                src={movie.image}
                                                alt={movie.title}
                                                loading="lazy"
                                                className="absolute left-0 top-[-28%] w-full h-[156%] object-cover object-center"
                                            />

                                        </div>
                                    ) : (
                                        <div className="shrink-0 flex items-center justify-center w-16 h-20 sm:w-20 sm:h-24 rounded-xl bg-[#39ff14]/[0.05] border border-[#7CFFB2]/15">
                                            🎬
                                        </div>
                                    )}


                                    {/* INFO */}

                                    <div className="min-w-0 flex-1">

                                        <h3 className="font-semibold text-white text-xs sm:text-base leading-5 sm:leading-6 line-clamp-2">
                                            {movie.title}
                                        </h3>

                                        <p className="mt-1.5 text-[10px] sm:text-sm text-white/30">
                                            Tap to view available options
                                        </p>

                                    </div>


                                    {/* ARROW */}

                                    <div className="shrink-0 w-8 h-8 sm:w-10 sm:h-10 flex items-center justify-center rounded-full bg-[#39ff14]/[0.045] border border-[#7CFFB2]/10 text-[#72ff9f]/50">
                                        →
                                    </div>

                                </div>

                            </button>

                        ))}

                    </div>

                </section>
            )}


            {/* NO RESULTS */}

            {hasSearched &&
                !loading &&
                movies.length === 0 &&
                !error && (

                    <div className="max-w-3xl mx-auto mt-8">
                        <div className="relative overflow-hidden flex items-center justify-center gap-3 px-5 py-5 rounded-2xl bg-[#39ff14]/[0.045] border border-[#39ff14]/25">

                            <span className="text-2xl text-[#39ff14]">
                                !!
                            </span>

                            <p className="text-sm sm:text-base font-semibold text-[#39ff14] text-center">
                                Oops! Movie not available on KRN MovieHub.
                                Please check the movie spelling and try again.
                            </p>

                        </div>
                    </div>
                )}


            {/* SELECTED MOVIE */}

            {selectedMovie && (
                <section
                    ref={selectedMovieRef}
                    className="mt-10 sm:mt-12 animate-[slideUp_0.4s_ease-out]"
                >

                    <div className="relative overflow-hidden p-5 sm:p-6 rounded-3xl bg-gradient-to-br from-[#b8ffd0]/[0.07] via-[#39ff14]/[0.025] to-[#67dfff]/[0.045] border border-[#8affb5]/20">

                        <div className="relative min-w-0 flex items-center gap-3 sm:gap-4">

                            {selectedMovie.image ? (
                                <div className="relative shrink-0 w-16 h-20 sm:w-20 sm:h-24 overflow-hidden rounded-xl border border-[#8affb5]/25">

                                    <img
                                        src={selectedMovie.image}
                                        alt={selectedMovie.title}
                                        className="absolute left-0 top-[-28%] w-full h-[156%] object-cover object-center"
                                    />

                                </div>
                            ) : (
                                <div className="shrink-0 w-14 h-14 flex items-center justify-center rounded-xl bg-[#39ff14]/[0.06] border border-[#8affb5]/20">
                                    🎬
                                </div>
                            )}

                            <div className="min-w-0">
                                <p className="text-[10px] sm:text-xs uppercase tracking-[0.18em] text-[#72ff9f] font-semibold mb-1">
                                    Selected
                                </p>

                                <h2 className="text-base sm:text-2xl font-bold text-white leading-6 line-clamp-2">
                                    {selectedMovie.title}
                                </h2>

                                <p className="text-xs sm:text-sm text-white/35 mt-1.5">
                                    Choose an available option
                                </p>
                            </div>

                        </div>

                    </div>


                    {/* OPTIONS LOADING */}

                    {selectionLoading && (
                        <div className="mt-5 p-8 rounded-2xl bg-white/[0.035] border border-[#8affb5]/10 text-center">

                            <div className="mx-auto mb-4 w-8 h-8 border-2 border-[#39ff14]/20 border-t-[#72ff9f] rounded-full animate-spin" />

                            <p className="text-white/40 text-sm">
                                Loading available options...
                            </p>

                        </div>
                    )}


                    {/* OPTIONS */}

                    {!selectionLoading &&
                        movieSizes.length > 0 && (

                            <div
                                ref={optionsRef}
                                className="mt-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4"
                            >

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
                                                handleSizeSelect(option)
                                            }
                                            disabled={sizeLoading}
                                            className="group relative overflow-hidden p-4 sm:p-5 rounded-2xl text-left bg-gradient-to-br from-[#b8ffd0]/[0.06] via-[#39ff14]/[0.025] to-[#67dfff]/[0.035] border border-[#8affb5]/[0.16] hover:border-[#7CFFB2]/40 hover:-translate-y-1 transition-all duration-300 disabled:opacity-40"
                                        >

                                            <div className="relative flex items-center justify-between gap-3">

                                                <div className="min-w-0">

                                                    <div className="inline-flex items-center px-3 py-1 rounded-full bg-[#39ff14]/[0.06] border border-[#8affb5]/20 text-[#7CFFB2] text-[10px] sm:text-xs font-semibold mb-3">
                                                        OPTION {index + 1}
                                                    </div>

                                                    <strong className="block text-sm sm:text-base text-white leading-relaxed break-words">
                                                        {option.label}
                                                    </strong>

                                                    {option.size && (
                                                        <span className="block mt-2 text-xs text-white/30">
                                                            {option.size}
                                                        </span>
                                                    )}

                                                </div>

                                                <span className="shrink-0 w-9 h-9 sm:w-10 sm:h-10 flex items-center justify-center rounded-full bg-[#39ff14]/[0.045] border border-[#8affb5]/10 text-[#72ff9f]/50">
                                                    →
                                                </span>

                                            </div>

                                        </button>

                                    )
                                )}

                            </div>
                        )}


                    {/* SIZE LOADING */}

                    {sizeLoading && (
                        <div className="mt-5 flex items-center justify-center gap-3 p-5 rounded-2xl bg-[#39ff14]/[0.035] border border-[#8affb5]/15 text-[#72ff9f]">

                            <span className="w-5 h-5 border-2 border-[#39ff14]/20 border-t-[#72ff9f] rounded-full animate-spin" />

                            Processing selected option...

                        </div>
                    )}


                    {/* FINAL RESULT */}

                    {finalLink && (
                        <div
                            ref={finalResultRef}
                            className="relative overflow-hidden mt-6 p-5 sm:p-6 rounded-3xl bg-gradient-to-br from-[#39ff14]/[0.075] via-[#7CFFB2]/[0.035] to-[#67dfff]/[0.055] border border-[#8affb5]/25 animate-[slideUp_0.4s_ease-out]"
                        >

                            <div className="relative min-w-0 flex items-center gap-3 mb-5">

                                <div className="w-11 h-11 shrink-0 flex items-center justify-center rounded-xl bg-[#39ff14]/10 text-[#72ff9f] border border-[#8affb5]/20">
                                    ✓
                                </div>

                                <div className="min-w-0">

                                    <h3 className="font-bold text-white">
                                        Done
                                    </h3>

                                    <p className="text-xs sm:text-sm text-[#72ff9f]/70 mt-1 leading-relaxed">
                                        Hi, I’m Karan 👋 — here’s your movie link. Click below to download the movie.
                                    </p>

                                </div>

                            </div>

                            <a
                                href={finalLink}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="relative inline-flex w-full items-center justify-center gap-2 px-5 py-3.5 rounded-xl bg-gradient-to-r from-[#39ff14] via-[#64ff91] to-[#9affc8] text-black font-bold shadow-[0_0_22px_rgba(57,255,20,0.16)] hover:shadow-[0_0_35px_rgba(57,255,20,0.30)] transition-all"
                            >
                                Click to Download
                                <span>⬇</span>
                            </a>

                        </div>
                    )}

                </section>
            )}

        </section>
    );
}