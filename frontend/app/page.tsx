"use client";
import Link from "next/link";

export default function Home() {
  const handleConnect = () => {
    const backendUrl =
      process.env.NEXT_PUBLIC_BACKEND_URL || "https://lighter-delv.onrender.com";
    window.location.href = `${backendUrl}/login`;
  };

  return (
    <main className="min-h-screen bg-[#101010] text-white">
      {/* HERO SECTION */}
      <section className="relative min-h-screen flex flex-col">
        {/* Background gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#1b1b1b] via-[#202020] to-[#3b3b3b] opacity-90" />

        {/* Subtle light grey vignette */}
        <div className="pointer-events-none absolute inset-20 rounded-[40px] border border-white/5 bg-gradient-to-tr from-white/5 via-transparent to-white/0" />

        {/* Content */}
        <div className="relative z-10 flex flex-col flex-1">
          {/* Top nav */}
          <header className="flex items-center justify-between px-8 md:px-16 py-6">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-full bg-[#D3D3D3]" />
              <span className="text-sm tracking-[0.25em] uppercase text-gray-300">
                light
              </span>
            </div>

            <nav className="hidden md:flex items-center gap-8 text-sm text-gray-300">
              <a href="#about" className="hover:text-white transition">About</a>
              <a href="#features" className="hover:text-white transition">Features</a>
              <a href="#meeting" className="hover:text-white transition">Meeting agent</a>
              <a href="#pricing" className="hover:text-white transition">Pricing</a>
            </nav>
          </header>

          {/* Hero center content */}
          <div className="flex-1 flex flex-col items-center justify-center text-center px-6 md:px-12">
            <p className="text-xs md:text-sm tracking-[0.35em] uppercase text-gray-400 mb-4">
              AI assistant for operators & builders
            </p>

            <h1 className="text-3xl md:text-5xl lg:text-6xl font-semibold max-w-3xl leading-tight md:leading-[1.1]">
              Master your{" "}
              <span className="text-[#D3D3D3]">email, meetings</span>{" "}
              & busy days with one assistant.
            </h1>

            <p className="mt-6 text-sm md:text-base text-gray-300 max-w-xl">
              Light connects to your Gmail, drafts replies in your tone,
              labels your inbox, joins your meetings, and writes clean,
              structured minutes of meeting in the format you choose.
            </p>

            {/* Buttons */}
            <div className="mt-10 flex flex-col sm:flex-row gap-4">
              <button
                onClick={handleConnect}
                className="px-8 py-3 rounded-full bg-[#D3D3D3] text-black text-sm font-medium tracking-wide hover:bg-white transition shadow-lg shadow-black/40"
              >
                Connect to Gmail
              </button>

              <a
                href="#pricing"
                className="px-8 py-3 rounded-full border border-gray-500 text-sm font-medium tracking-wide text-gray-100 hover:border-[#D3D3D3] hover:bg-white/5 transition"
              >
                Check pricing
              </a>
            </div>

            {/* Scroll indicator */}
            <a
              href="#about"
              className="mt-14 flex flex-col items-center gap-2 text-xs text-gray-400 hover:text-gray-200 transition"
            >
              <span>Scroll to learn more</span>
              <span className="animate-bounce text-lg">↓</span>
            </a>
          </div>
        </div>
      </section>

      {/* ABOUT SECTION */}
      <section
        id="about"
        className="bg-[#D3D3D3] text-[#111111] py-20 md:py-24 px-6 md:px-16"
      >
        <div className="max-w-5xl mx-auto">
          <p className="text-xs tracking-[0.35em] uppercase text-gray-700 mb-4">
            About light
          </p>
          <h2 className="text-2xl md:text-3xl font-semibold mb-6">
            Your behind-the-scenes operator for inboxes & meetings.
          </h2>
          <p className="text-sm md:text-base text-gray-800 leading-relaxed mb-6">
            Light is designed for builders, operators, and busy ICs who live inside
            their inbox and spend hours in recurring meetings. Instead of giving you
            yet another tool to manage, Light quietly plugs into what you already use:
            Gmail and your meeting links.
          </p>
          <p className="text-sm md:text-base text-gray-800 leading-relaxed">
            It classifies incoming emails using rules, AI, and your own domain
            preferences, then drafts clean replies right inside Gmail. For meetings,
            Light listens, understands the conversation, and produces minutes of
            meeting in a structured format you define — with owners, deadlines, and
            next steps clearly called out.
          </p>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section
        id="features"
        className="bg-[#f4f4f5] text-[#111111] py-20 md:py-28 px-6 md:px-20"
      >
        <div className="max-w-6xl mx-auto">
          <p className="text-xs tracking-[0.35em] uppercase text-gray-600 mb-3">
            What Light Does
          </p>

          <h2 className="text-3xl md:text-4xl font-semibold mb-14">
            Designed to remove the boring parts of your workday.
          </h2>

          {/* GRID OF FEATURES */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 md:gap-14">
            <div className="bg-white rounded-3xl shadow-xl shadow-black/5 p-8 border border-gray-200 hover:shadow-2xl hover:-translate-y-1 transition">
              <h3 className="text-xl font-semibold mb-4">Email Summary Preview</h3>
              <p className="text-gray-700 text-sm leading-relaxed">
                Light reads the entire email thread and generates a clean summary at the 
                top of the draft page — so you know exactly what the sender wants before replying.
              </p>
            </div>

            <div className="bg-white rounded-3xl shadow-xl shadow-black/5 p-8 border border-gray-200 hover:shadow-2xl hover:-translate-y-1 transition">
              <h3 className="text-xl font-semibold mb-4">AI Draft Replies</h3>
              <p className="text-gray-700 text-sm leading-relaxed">
                Light writes smart, context-aware replies inside Gmail using the tone you prefer.
                You just review & send — no switching apps, no copy-paste work.
              </p>
            </div>

            <div className="bg-white rounded-3xl shadow-xl shadow-black/5 p-8 border border-gray-200 hover:shadow-2xl hover:-translate-y-1 transition">
              <h3 className="text-xl font-semibold mb-4">Smart Inbox Labeling</h3>
              <p className="text-gray-700 text-sm leading-relaxed">
                Every email is classified using rule-based logic, AI fallback, and your own
                domain overrides stored in the database. Your inbox stays clean and predictable.
              </p>
            </div>

            <div className="bg-white rounded-3xl shadow-xl shadow-black/5 p-8 border border-gray-200 hover:shadow-2xl hover:-translate-y-1 transition">
              <h3 className="text-xl font-semibold mb-4">Meeting Agent with MoM</h3>
              <p className="text-gray-700 text-sm leading-relaxed">
                Light joins your meetings, listens like an operator, and produces Minutes of
                Meeting in the custom structure you define — action items, owners, and deadlines.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* MEETING SECTION */}
      <section
        id="meeting"
        className="bg-[#e5e5e5] text-[#111111] py-16 md:py-20 px-6 md:px-16"
      >
        <div className="max-w-5xl mx-auto">
          <h2 className="text-xl md:text-2xl font-semibold mb-4">
            Meeting agent, built like a teammate.
          </h2>
          <p className="text-sm md:text-base text-gray-700">
            (Later we’ll connect this to your MoM agent backend and show your custom format.)
          </p>
        </div>
      </section>

      {/* PRICING SECTION */}
      <section
        id="pricing"
        className="bg-[#111111] text-gray-100 py-16 md:py-20 px-6 md:px-16"
      >
        <div className="max-w-5xl mx-auto">
          <h2 className="text-xl md:text-2xl font-semibold mb-6">
            Simple pricing for busy people
          </h2>
          <p className="text-sm md:text-base text-gray-400 mb-8">
            (We’ll fill in real pricing later. For now you can keep this as a static section.)
          </p>
          <div className="rounded-2xl border border-gray-700 bg-gradient-to-br from-white/5 to-white/0 p-6 md:p-8 max-w-md">
            <p className="text-sm uppercase tracking-[0.25em] text-gray-400 mb-2">
              Early access
            </p>
            <p className="text-3xl font-semibold mb-2">Free</p>
            <p className="text-sm text-gray-400 mb-6">
              While in beta, Light is free for early users. Connect Gmail and start
              testing the workflow.
            </p>
            <button
              onClick={handleConnect}
              className="inline-block px-6 py-3 rounded-full bg-[#D3D3D3] text-black text-sm font-medium tracking-wide hover:bg-white transition"
            >
              Get started
            </button>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-black text-gray-500 text-xs py-6 px-6 md:px-16">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
          <span>© {new Date().getFullYear()} Light. All rights reserved.</span>
          <span className="text-gray-600">
            Built for operators who hate noisy tools.
          </span>
        </div>
      </footer>
    </main>
  );
}
