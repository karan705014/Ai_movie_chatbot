import { useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000/api";

export default function AISearch({
  onMovieSearch,
}) {
  const [query, setQuery] = useState("");

  const [aiResponse, setAiResponse] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  /* =========================
     AI CHAT
  ========================= */

  const handleAISearch = async () => {
    const message = query.trim();

    if (!message) {
      return;
    }

    setLoading(true);

    setError("");

    setAiResponse("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/chat/`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            message,
          }),
        }
      );

      const data =
        await response.json();

      console.log(
        "AI RESPONSE:",
        data
      );

      if (!response.ok) {
        throw new Error(
          data?.error ||
            "AI request failed."
        );
      }


      /*
        BACKEND RESPONSE:

        Normal information:

        {
          "message": "Yash is an Indian actor..."
        }


        Movie request:

        {
          "message": "Sure, searching for Toxic.",
          "movie_name": "Toxic"
        }
      */


      setAiResponse(
        data?.message || ""
      );


      /* =========================
         MOVIE NAME RECEIVED
      ========================= */

      if (
        data?.movie_name &&
        typeof data.movie_name ===
          "string" &&
        data.movie_name.trim()
      ) {
        onMovieSearch(
          data.movie_name.trim()
        );
      }

    } catch (err) {
      console.error(
        "AI ERROR:",
        err
      );

      setError(
        err.message ||
          "Failed to get AI response."
      );

    } finally {
      setLoading(false);
    }
  };


  return (
    <section className="max-w-3xl mx-auto">


      {/* =========================
          AI SEARCH BOX
      ========================= */}

      <div className="flex flex-col sm:flex-row gap-3 p-2 rounded-2xl bg-white/[0.05] border border-white/10 shadow-2xl shadow-purple-950/20 backdrop-blur-xl">

        <input
          type="text"
          placeholder="Ask AI about a movie, actor, director..."
          value={query}
          onChange={(e) =>
            setQuery(e.target.value)
          }
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleAISearch();
            }
          }}
          className="flex-1 min-w-0 px-5 py-4 rounded-xl bg-slate-900/70 border border-white/10 text-white placeholder-slate-500 outline-none focus:border-purple-400/60 focus:ring-2 focus:ring-purple-500/20 transition"
        />


        <button
          type="button"
          onClick={
            handleAISearch
          }
          disabled={loading}
          className="px-7 py-4 rounded-xl bg-gradient-to-r from-purple-600 via-pink-600 to-cyan-500 font-bold text-white shadow-lg shadow-purple-600/20 hover:scale-[1.02] active:scale-[0.98] transition disabled:opacity-50 disabled:cursor-not-allowed"
        >

          {loading ? (
            <span className="flex items-center justify-center gap-2">

              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />

              Thinking...

            </span>
          ) : (
            "Ask AI"
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
          AI RESPONSE
      ========================= */}

      {aiResponse && (
        <section className="mt-8">

          <div className="rounded-2xl bg-white/[0.04] border border-purple-400/20 p-5 shadow-xl shadow-purple-950/10">

            <div className="flex items-center gap-3 mb-4">

              <div className="w-10 h-10 flex items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-cyan-500">
                ✨
              </div>

              <div>

                <h2 className="font-bold text-white">
                  AI Assistant
                </h2>

                <p className="text-xs text-slate-500">
                  Gemini response
                </p>

              </div>

            </div>


            <div className="text-slate-300 leading-7 whitespace-pre-wrap">
              {aiResponse}
            </div>

          </div>

        </section>
      )}

    </section>
  );
}