"use client";

import { useState, type FormEvent } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Reveal from "./Reveal";

const INQUIRY_TYPES = [
  { id: "demo", label: "Request Demo" },
  { id: "contact", label: "Contact Us" },
  { id: "research", label: "Research Partnership" },
] as const;

type InquiryId = (typeof INQUIRY_TYPES)[number]["id"];

const PLACEHOLDER: Record<InquiryId, string> = {
  demo: "Tell us about your imaging volume and what you'd want to see in a walkthrough.",
  contact: "What can we help with?",
  research: "Tell us about your institution and the study you have in mind.",
};

export default function CTASection() {
  const [inquiry, setInquiry] = useState<InquiryId>("demo");
  const [submitted, setSubmitted] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [org, setOrg] = useState("");
  const [message, setMessage] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!name || !email) return;
    setSubmitted(true);
  }

  return (
    <section
      id="cta"
      className="relative scroll-mt-24 overflow-hidden bg-ink py-28 sm:py-36"
    >
      <div className="bg-grid absolute inset-0 opacity-20" />
      <div className="absolute left-1/2 top-0 h-[480px] w-[480px] -translate-x-1/2 rounded-full bg-blue-500/15 blur-[120px]" />

      <div className="relative mx-auto max-w-5xl px-6 sm:px-10">
        <Reveal className="text-center">
          <p className="kicker justify-center">Get Started</p>
          <h2 className="mx-auto mt-5 max-w-3xl text-4xl font-bold leading-tight tracking-tight text-paper sm:text-5xl">
            Transform aneurysm detection{" "}
            <span className="text-gradient">with AI.</span>
          </h2>
          <p className="mx-auto mt-6 max-w-xl text-lg leading-relaxed text-paper-dim">
            Request a walkthrough, ask a question, or propose a research
            collaboration — a real person reads every message.
          </p>
        </Reveal>

        <Reveal delay={0.1}>
          <div className="glass-panel mx-auto mt-14 max-w-2xl rounded-2xl p-8 sm:p-10">
            <AnimatePresence mode="wait">
              {submitted ? (
                <motion.div
                  key="success"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex flex-col items-center py-10 text-center"
                >
                  <span className="flex h-14 w-14 items-center justify-center rounded-full bg-cyan-400/15 text-cyan-300">
                    <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                      <path
                        d="m5 12.5 4.5 4.5L19 7"
                        stroke="currentColor"
                        strokeWidth={2}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </span>
                  <h3 className="mt-5 text-xl font-semibold text-paper">
                    Thanks — we&apos;ll be in touch.
                  </h3>
                  <p className="mt-2 max-w-sm text-sm text-paper-faint">
                    We typically respond within two business days.
                  </p>
                </motion.div>
              ) : (
                <motion.form
                  key="form"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onSubmit={handleSubmit}
                >
                  <div className="flex flex-wrap gap-2">
                    {INQUIRY_TYPES.map((type) => (
                      <button
                        key={type.id}
                        type="button"
                        onClick={() => setInquiry(type.id)}
                        className={`rounded-full px-4 py-2 text-xs font-semibold transition-colors duration-300 ${
                          inquiry === type.id
                            ? "bg-blue-500 text-white"
                            : "border border-white/15 text-paper-dim hover:border-cyan-400/50 hover:text-paper"
                        }`}
                      >
                        {type.label}
                      </button>
                    ))}
                  </div>

                  <div className="mt-7 grid gap-5 sm:grid-cols-2">
                    <label className="flex flex-col gap-1.5 text-xs font-medium text-paper-dim">
                      Name
                      <input
                        required
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="rounded-lg border border-white/10 bg-navy-900/70 px-4 py-2.5 text-sm text-paper outline-none transition-colors focus:border-cyan-400/60"
                        placeholder="Dr. Jane Doe"
                      />
                    </label>
                    <label className="flex flex-col gap-1.5 text-xs font-medium text-paper-dim">
                      Email
                      <input
                        required
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="rounded-lg border border-white/10 bg-navy-900/70 px-4 py-2.5 text-sm text-paper outline-none transition-colors focus:border-cyan-400/60"
                        placeholder="jane@institution.org"
                      />
                    </label>
                  </div>

                  <label className="mt-5 flex flex-col gap-1.5 text-xs font-medium text-paper-dim">
                    Institution / Organization
                    <input
                      value={org}
                      onChange={(e) => setOrg(e.target.value)}
                      className="rounded-lg border border-white/10 bg-navy-900/70 px-4 py-2.5 text-sm text-paper outline-none transition-colors focus:border-cyan-400/60"
                      placeholder="Optional"
                    />
                  </label>

                  <label className="mt-5 flex flex-col gap-1.5 text-xs font-medium text-paper-dim">
                    Message
                    <textarea
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      rows={4}
                      className="resize-none rounded-lg border border-white/10 bg-navy-900/70 px-4 py-2.5 text-sm text-paper outline-none transition-colors focus:border-cyan-400/60"
                      placeholder={PLACEHOLDER[inquiry]}
                    />
                  </label>

                  <button
                    type="submit"
                    className="glow-cyan mt-7 w-full rounded-full bg-blue-500 py-3.5 text-sm font-semibold text-white transition-transform duration-300 hover:scale-[1.02] hover:bg-blue-400"
                  >
                    {INQUIRY_TYPES.find((t) => t.id === inquiry)?.label}
                  </button>
                </motion.form>
              )}
            </AnimatePresence>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
