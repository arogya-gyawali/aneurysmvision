"use client";

import Reveal from "./Reveal";
import { IconMicroscope, IconShield, IconUsers } from "./icons";

const TESTIMONIALS = [
  {
    quote:
      "What I want from a second read isn't a verdict — it's a clear, measurable rationale I can check against my own eyes. That's the bar this kind of tool needs to clear.",
    role: "Neuroradiologist",
    org: "Academic medical center",
  },
  {
    quote:
      "The morphology metrics map directly onto how we already talk about aneurysm risk. Standardizing that across readers is the real opportunity here.",
    role: "Director of Neurovascular Imaging",
    org: "University health system",
  },
  {
    quote:
      "If the 3D reconstruction and the report agree with what I'd have measured manually, that's exactly the kind of validation we need before any clinical pilot.",
    role: "Interventional Neuroradiologist",
    org: "Regional stroke center",
  },
];

const PARTNER_TYPES = [
  { icon: IconUsers, label: "Academic medical centers" },
  { icon: IconMicroscope, label: "Neurovascular research labs" },
  { icon: IconShield, label: "Imaging core labs" },
];

const RESEARCH_FOCUS = [
  "Multi-center validation of detection sensitivity across aneurysm size and location",
  "Inter-reader agreement study comparing unassisted vs. AI-assisted morphology scoring",
  "Prospective workflow study measuring time-to-report in a clinical reading environment",
];

export default function TestimonialsSection() {
  return (
    <section id="research" className="relative scroll-mt-24 bg-ink py-28 sm:py-36">
      <div className="mx-auto max-w-7xl px-6 sm:px-10">
        <Reveal>
          <p className="kicker eyebrow-line">Research &amp; Validation</p>
          <h2 className="mt-5 max-w-3xl text-4xl font-bold leading-tight tracking-tight text-paper sm:text-5xl">
            Built alongside the people who{" "}
            <span className="text-gradient">will have to trust it.</span>
          </h2>
        </Reveal>

        <div className="mt-16 grid gap-6 lg:grid-cols-3">
          {TESTIMONIALS.map((t, i) => (
            <Reveal key={t.role} delay={i * 0.1}>
              <div className="glass-panel glass-panel-hover flex h-full flex-col rounded-2xl p-8">
                <svg width="28" height="22" viewBox="0 0 28 22" fill="none" className="text-cyan-400/60">
                  <path
                    d="M0 22V13.2C0 5.5 4.6.9 11.4 0l1.1 3.5C7.8 4.6 5.6 7.5 5.4 11h6V22H0Zm16.6 0V13.2c0-7.7 4.6-12.3 11.4-13.2l1.1 3.5c-4.7 1.1-6.9 4-7.1 7.5h6V22h-11.4Z"
                    fill="currentColor"
                  />
                </svg>
                <p className="mt-5 flex-1 text-sm leading-relaxed text-paper-dim">
                  {t.quote}
                </p>
                <div className="mt-6 border-t border-white/10 pt-4">
                  <p className="text-sm font-semibold text-paper">{t.role}</p>
                  <p className="text-xs text-paper-faint">{t.org}</p>
                </div>
              </div>
            </Reveal>
          ))}
        </div>

        <Reveal delay={0.1}>
          <div className="mt-16 grid gap-6 border-t border-white/10 pt-14 sm:grid-cols-2 lg:grid-cols-[1fr_1.3fr]">
            <div>
              <p className="text-sm font-semibold text-paper">
                Who we&apos;re built to work with
              </p>
              <div className="mt-5 flex flex-col gap-4">
                {PARTNER_TYPES.map((p) => (
                  <div key={p.label} className="flex items-center gap-3 text-sm text-paper-dim">
                    <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/5 text-cyan-300">
                      <p.icon width={16} height={16} />
                    </span>
                    {p.label}
                  </div>
                ))}
              </div>
            </div>
            <div>
              <p className="text-sm font-semibold text-paper">
                Active research focus
              </p>
              <ul className="mt-5 flex flex-col gap-4">
                {RESEARCH_FOCUS.map((item) => (
                  <li key={item} className="flex gap-3 text-sm leading-relaxed text-paper-dim">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-400" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </Reveal>

        <p className="mt-12 text-xs text-paper-faint">
          Illustrative content for the platform&apos;s current research direction. Named clinical
          partnerships and published validation results will appear here as they&apos;re finalized.
        </p>
      </div>
    </section>
  );
}
