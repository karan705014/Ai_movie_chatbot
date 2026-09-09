import { useState } from "react";
import "./App.css";

import ManualSearch from "./pages/ManualSearch";
import AISearch from "./pages/AISearch";

export default function App() {
  const [mode, setMode] = useState("manual");

  // Movie name received from AI
  const [aiMovieName, setAiMovieName] = useState("");

  // Used to force ManualSearch to run again
  // even when the same movie name is selected twice.
  const [searchId, setSearchId] = useState(0);

  const handleMovieFromAI = (movieName) => {
    if (!movieName?.trim()) {
      return;
    }

    setAiMovieName(movieName.trim());

    // Increase every time AI gives a movie
    setSearchId((prev) => prev + 1);

    // Switch to manual page
    setMode("manual");
  };

  const handleManualMode = () => {
    setMode("manual");
  };

  const handleAIMode = () => {
    setMode("ai");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white relative overflow-hidden">

      {/* Background decorations */}
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl" />

      <div className="absolute top-1/3 -right-40 w-96 h-96 bg-cyan-500/15 rounded-full blur-3xl" />

      <div className="absolute bottom-0 left-1/3 w-96 h-96 bg-pink-600/10 rounded-full blur-3xl" />

      <div className="relative z-10 max-w-6xl mx-auto px-4 py-6 sm:px-6 lg:px-8">

        {/* =========================
            HEADER
        ========================= */}
        <header className="text-center mb-8 sm:mb-12">

          <div className="inline-flex items-center gap-2 px-4 py-2 mb-5 rounded-full bg-purple-500/10 border border-purple-400/20 text-purple-300 text-sm">

            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />

            AI Movie Assistant

          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight">

            Movie

            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400">
              {" "}Search
            </span>

          </h1>

          <p className="mt-4 max-w-xl mx-auto text-slate-400 text-sm sm:text-base">
            Search for movies manually or ask our AI movie assistant.
          </p>

        </header>


        {/* =========================
            MODE SWITCH
        ========================= */}
        <section className="max-w-3xl mx-auto mb-5">

          <div className="flex justify-center">

            <div className="inline-flex p-1 rounded-xl bg-white/[0.05] border border-white/10 backdrop-blur-xl">

              {/* MANUAL */}
              <button
                type="button"
                onClick={handleManualMode}
                className={`px-6 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                  mode === "manual"
                    ? "bg-purple-600 text-white shadow-lg shadow-purple-600/20"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                🔎 Manual
              </button>


              {/* AI */}
              <button
                type="button"
                onClick={handleAIMode}
                className={`px-6 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                  mode === "ai"
                    ? "bg-gradient-to-r from-purple-600 via-pink-600 to-cyan-500 text-white shadow-lg shadow-purple-600/20"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                ✨ AI
              </button>

            </div>

          </div>

        </section>


        {/* =========================
            PAGE
        ========================= */}

        {mode === "manual" ? (

          <ManualSearch
            key={searchId}
            initialQuery={aiMovieName}
          />

        ) : (

          <AISearch
            onMovieSearch={handleMovieFromAI}
          />

        )}

      </div>

    </div>
  );
}