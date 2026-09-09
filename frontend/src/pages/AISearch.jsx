import { useEffect, useRef, useState } from "react";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

export default function AISearch({
    onMovieSearch,
    onManualSearch,
}) {
    const [query, setQuery] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // =========================================================
    // LOAD PREVIOUS CHAT
    // =========================================================

    useEffect(() => {
        const loadChatHistory = async () => {
            try {
                const response = await fetch(
                    `${API_BASE_URL}/chat/history/`,
                    {
                        method: "GET",
                        credentials: "include",
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(
                        data?.error || "Could not load chat history."
                    );
                }

                if (Array.isArray(data?.messages)) {
                    setMessages(data.messages);
                }
            } catch (err) {
                console.error("CHAT HISTORY ERROR:", err);
            }
        };

        loadChatHistory();
    }, []);

    // =========================================================
    // AUTO SCROLL
    // =========================================================

    useEffect(() => {
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                messagesEndRef.current?.scrollIntoView({
                    behavior: "smooth",
                    block: "end",
                });
            });
        });
    }, [messages, loading]);

    // =========================================================
    // SEND MESSAGE
    // =========================================================

    const handleAISearch = async () => {
        const message = query.trim();

        if (!message || loading) return;

        setError("");

        // Show user message immediately.
        setMessages((previous) => [
            ...previous,
            {
                role: "user",
                content: message,
            },
        ]);

        setQuery("");
        setLoading(true);

        try {
            const response = await fetch(
                `${API_BASE_URL}/chat/`,
                {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        message,
                        conversation_history: messages.concat({
                            role: "user",
                            content: message,
                        }),
                    }),
                }
            );

            const data = await response.json();

            console.log("AI RESPONSE:", data);

            if (!response.ok) {
                throw new Error(
                    data?.error || "AI request failed."
                );
            }

            const answer = data?.message?.trim();

            if (!answer) {
                throw new Error(
                    "AI returned an empty response."
                );
            }

            // AI answer is added as the next chat message.
            setMessages((previous) => [
                ...previous,
                {
                    role: "assistant",
                    content: answer,
                },
            ]);

            // New architecture:
            // AI does NOT automatically start movie search.
            // Search/download/link requests return mode="manual".
            if (data?.mode === "manual" && onManualSearch) {
                // We intentionally do not switch automatically.
                // User is shown the manual instructions and can click
                // the Manual Search UI themselves.
            }
        } catch (err) {
            console.error("AI ERROR:", err);

            setError(
                err?.message ||
                "Failed to get AI response."
            );
        } finally {
            setLoading(false);

            requestAnimationFrame(() => {
                inputRef.current?.focus();
            });
        }
    };

    // =========================================================
    // ENTER KEY
    // =========================================================

    const handleKeyDown = (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            handleAISearch();
        }
    };

    // =========================================================
    // RENDER
    // =========================================================

    return (
        <section className="w-full max-w-5xl mx-auto pb-32 px-2 sm:px-0">

            {/* =================================================
                CHAT HEADER
            ================================================== */}

            <div className="max-w-4xl mx-auto pt-5 sm:pt-8 pb-4">
                <div className="flex items-center gap-3">
                    <div className="w-11 h-11 flex items-center justify-center rounded-2xl bg-[#39ff14]/[0.08] border border-[#8affb5]/20">
                        ✨
                    </div>

                    <div>
                        <h1 className="text-lg sm:text-xl font-bold text-white">
                            AI Assistant
                        </h1>

                        <p className="text-xs text-[#72ff9f]/50 mt-0.5">
                            Information & recommendations
                        </p>
                    </div>
                </div>
            </div>

            {/* =================================================
                CHAT AREA
            ================================================== */}

            <section
                className="max-w-4xl mx-auto min-h-[420px] pr-1"
            >

                {messages.length === 0 && !loading && (
                    <div className="min-h-[420px] flex items-center justify-center">
                        <div className="text-center max-w-lg px-5">
                            <div className="text-4xl mb-4">
                                ✨
                            </div>

                            <h2 className="text-xl sm:text-2xl font-bold text-white">
                                What can I help you with?
                            </h2>

                            <p className="mt-2 text-sm leading-6 text-white/35">
                                Ask about movies, actors, directors,
                                ratings, filmographies, latest releases,
                                or recommendations.
                            </p>
                        </div>
                    </div>
                )}

                <div className="space-y-6 py-4">

                    {messages.map((message, index) => {
                        const isUser = message?.role === "user";

                        return (
                            <div
                                key={`${message?.role}-${index}`}
                                className={
                                    isUser
                                        ? "flex justify-end"
                                        : "flex justify-start"
                                }
                            >
                                <div
                                    className={
                                        isUser
                                            ? "max-w-[88%] sm:max-w-[78%]"
                                            : "w-full max-w-[88%] sm:max-w-[82%]"
                                    }
                                >
                                    <div className="flex items-start gap-3">

                                        {!isUser && (
                                            <div className="shrink-0 w-9 h-9 flex items-center justify-center rounded-xl bg-[#39ff14]/[0.08] border border-[#8affb5]/15 text-sm">
                                                ✨
                                            </div>
                                        )}

                                        <div
                                            className={
                                                isUser
                                                    ? "rounded-2xl rounded-br-md px-4 sm:px-5 py-3.5 bg-[#39ff14]/[0.09] border border-[#8affb5]/15 text-white/90"
                                                    : "rounded-2xl rounded-tl-md px-4 sm:px-5 py-3.5 bg-gradient-to-br from-[#b8ffd0]/[0.055] via-[#39ff14]/[0.018] to-[#67dfff]/[0.035] border border-[#8affb5]/10 text-[#d8d8d8]"
                                            }
                                        >
                                            <div className="text-[10px] uppercase tracking-wider font-semibold text-white/25 mb-1.5">
                                                {isUser ? "You" : "AI Assistant"}
                                            </div>

                                            <div className="text-sm sm:text-base leading-7 whitespace-pre-wrap break-words">
                                                {message?.content}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}

                    {/* =================================================
                        THINKING
                    ================================================== */}

                    {loading && (
                        <div className="flex justify-start">
                            <div className="flex items-start gap-3">
                                <div className="shrink-0 w-9 h-9 flex items-center justify-center rounded-xl bg-[#39ff14]/[0.08] border border-[#8affb5]/15">
                                    ✨
                                </div>

                                <div className="rounded-2xl rounded-tl-md px-5 py-4 bg-gradient-to-br from-[#b8ffd0]/[0.055] via-[#39ff14]/[0.018] to-[#67dfff]/[0.035] border border-[#8affb5]/10">
                                    <div className="text-[10px] uppercase tracking-wider font-semibold text-white/25 mb-2">
                                        AI Assistant
                                    </div>

                                    <div className="flex items-center gap-1.5">
                                        <span className="w-1.5 h-1.5 rounded-full bg-white/45 animate-bounce" />
                                        <span
                                            className="w-1.5 h-1.5 rounded-full bg-white/45 animate-bounce"
                                            style={{ animationDelay: "120ms" }}
                                        />
                                        <span
                                            className="w-1.5 h-1.5 rounded-full bg-white/45 animate-bounce"
                                            style={{ animationDelay: "240ms" }}
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} className="h-32 scroll-mb-32" />
                </div>

                {/* =================================================
                    ERROR
                ================================================== */}

                {error && (
                    <div className="mb-6">
                        <div className="flex items-start gap-3 p-4 rounded-2xl bg-[#ff073a]/[0.06] border border-[#ff073a]/20 text-[#ff8ba0]">
                            <span>⚠️</span>

                            <div>
                                <p className="text-sm leading-6">
                                    AI service is currently unavailable.
                                </p>

                                <p className="mt-1 text-xs text-white/30">
                                    {error}
                                </p>

                                <p className="mt-1 text-xs text-white/30">
                                    You can continue using Manual Search.
                                </p>
                            </div>
                        </div>
                    </div>
                )}
            </section>

            {/* =================================================
                FIXED CHAT INPUT
            ================================================== */}

            <div className="fixed bottom-0 left-0 right-0 z-50 bg-[#050505]/90 backdrop-blur-2xl border-t border-[#8affb5]/[0.08]">

                <div className="w-full max-w-5xl mx-auto px-3 sm:px-4 py-3">

                    <div className="relative w-full min-w-0 flex gap-1.5 sm:gap-3 p-1.5 sm:p-2 rounded-2xl bg-gradient-to-br from-[#b8ffd0]/[0.055] via-[#39ff14]/[0.02] to-[#67dfff]/[0.035] border border-[#8affb5]/[0.16]">

                        <input
                            ref={inputRef}
                            type="text"
                            placeholder="Ask AI about a movie, actor, director..."
                            value={query}
                            onChange={(event) =>
                                setQuery(event.target.value)
                            }
                            onKeyDown={handleKeyDown}
                            disabled={loading}
                            className="relative flex-1 min-w-0 w-0 px-3 sm:px-5 py-3.5 sm:py-4 rounded-xl bg-black/40 border border-white/[0.08] text-white text-xs sm:text-base placeholder:text-white/25 outline-none focus:border-[#7CFFB2]/40 disabled:opacity-50"
                        />

                        <button
                            type="button"
                            onClick={handleAISearch}
                            disabled={
                                loading ||
                                !query.trim()
                            }
                            className="relative shrink-0 px-4 sm:px-7 py-3.5 sm:py-4 rounded-xl bg-gradient-to-br from-[#39ff14] via-[#58ff7b] to-[#8affc1] text-black font-bold text-xs sm:text-base shadow-[0_0_18px_rgba(57,255,20,0.18)] disabled:opacity-30"
                        >
                            {loading ? (
                                <span className="flex items-center gap-2">
                                    <span className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin" />

                                    <span className="hidden sm:inline">
                                        Thinking...
                                    </span>
                                </span>
                            ) : (
                                <>
                                    <span className="hidden sm:inline">
                                        Ask AI
                                    </span>

                                    <span className="sm:hidden">
                                        ➤
                                    </span>
                                </>
                            )}
                        </button>

                    </div>
                </div>
            </div>
        </section>
    );
}
