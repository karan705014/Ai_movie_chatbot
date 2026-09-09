import { useState } from "react";
import "./App.css";
import ManualSearch from "./pages/ManualSearch";
import AISearch from "./pages/AISearch";

export default function App() {
  const [mode, setMode] = useState("manual");
  const [aiMovieName, setAiMovieName] = useState("");
  const [searchId, setSearchId] = useState(0);

  const handleMovieFromAI = (movieName) => {
    const name = movieName?.trim();

    if (!name) return;

    setAiMovieName(name);
    setSearchId((prev) => prev + 1);
    setMode("manual");
  };

  const handleManualMode = () => {
    setMode("manual");
    setAiMovieName("");
  };

  const handleAIMode = () => {
    setMode("ai");
  };

  return (
    <div className="min-h-screen w-full bg-[#050505] text-white relative overflow-x-hidden">

      {/* BACKGROUND GLOW */}
      <div className="pointer-events-none fixed -top-32 -left-32 w-72 h-72 sm:w-96 sm:h-96 rounded-full bg-[#39ff14]/[0.06] blur-3xl" />

      <div className="pointer-events-none fixed top-1/3 -right-32 w-72 h-72 sm:w-96 sm:h-96 rounded-full bg-[#ff073a]/[0.06] blur-3xl" />

      <div className="pointer-events-none fixed bottom-0 left-1/3 w-64 h-64 rounded-full bg-[#39ff14]/[0.035] blur-3xl" />

      <div className="relative z-10 w-full max-w-6xl mx-auto px-3 sm:px-6 lg:px-8 py-6 sm:py-10">

        {/* HEADER */}
        <header className="text-center mb-7 sm:mb-10">

          <div className="inline-flex items-center gap-2 px-3.5 py-2 mb-4 rounded-full bg-[#39ff14]/[0.06] border border-[#39ff14]/20 text-[#39ff14] text-[10px] sm:text-sm">

            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full rounded-full bg-[#39ff14] opacity-60 animate-ping" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-[#39ff14]" />
            </span>

            AI Movie Assistant
          </div>

          <h1 className="px-2 text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-tight break-words">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#39ff14] to-[#9cff7b]">
              KRN MovieHub
            </span>
          </h1>

          <p className="mt-3 px-3 max-w-xl mx-auto text-white/40 text-xs sm:text-base leading-5 sm:leading-6">
            Find your favorite movies manually or let AI do the searching for you.
          </p>

        </header>


        {/* MODE SWITCH */}
        <section className="w-full flex justify-center mb-7 sm:mb-9">

          <div className="relative inline-flex w-full max-w-[260px] p-1 rounded-2xl bg-[#0b0b0b] border border-white/[0.08]">

            <div
              className={`absolute top-1 bottom-1 w-[calc(50%-4px)] rounded-xl transition-all duration-300 ${mode === "manual"
                ? "left-1 bg-[#39ff14]/[0.10] border border-[#39ff14]/30 shadow-[0_0_18px_rgba(57,255,20,0.12)]"
                : "left-[calc(50%+2px)] bg-[#ff073a]/[0.10] border border-[#ff073a]/30 shadow-[0_0_18px_rgba(255,7,58,0.12)]"
                }`}
            />

            <button
              type="button"
              onClick={handleManualMode}
              className={`relative z-10 flex-1 min-w-0 px-3 sm:px-5 py-2.5 rounded-xl transition-all duration-300 ${mode === "manual"
                  ? "text-white"
                  : "text-white/40 hover:text-white"
                }`}
            >
              <span
                className={`
            inline-block
            font-black
            text-lg sm:text-xl
            tracking-[-0.04em]
            text-transparent
            bg-clip-text
            bg-gradient-to-b
            from-[#ffffff]
            via-[#aaffbd]
            to-[#39ff14]
            ${mode === "manual"
                    ? "drop-shadow-[0_0_5px_rgba(57,255,20,0.9)] drop-shadow-[0_0_16px_rgba(57,255,20,0.45)]"
                    : "opacity-45"
                  }
            transition-all
            duration-300
        `}
              >
                Manual
              </span>
            </button>

            <button
              type="button"
              onClick={handleAIMode}
              className={`relative z-10 flex-1 min-w-0 px-3 sm:px-5 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-300 ${mode === "ai"
                ? "text-white"
                : "text-[#666] hover:text-white"
                }`}
            >
              <span
                className={`font-black tracking-wide text-base sm:text-lg ${mode === "ai"
                  ? "text-transparent bg-clip-text bg-gradient-to-r from-[#00eaff] via-white to-[#00eaff] drop-shadow-[0_0_10px_rgba(0,234,255,0.65)]"
                  : "text-transparent bg-clip-text bg-gradient-to-r from-[#00b8d4]/50 via-white/50 to-[#00b8d4]/50"
                  }`}
              >
                AI
              </span>
            </button>

          </div>

        </section>


        {/* CONTENT */}
        <main className="w-full min-w-0 animate-[fadeIn_0.3s_ease-out]">

          {mode === "ai" ? (
            <AISearch
              onMovieSearch={handleMovieFromAI}
              onManualSearch={handleManualMode}
            />
          ) : (
            <ManualSearch
              key={searchId}
              initialQuery={aiMovieName}
            />
          )}

        </main>

      </div>
    </div>
  );
}