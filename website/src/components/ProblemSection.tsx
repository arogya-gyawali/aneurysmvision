"use client";

import Reveal from "./Reveal";
import AnimatedCounter from "./AnimatedCounter";

type Stat = {
  value: number;
  suffix: string;
  decimals?: number;
  label: string;
  detail: string;
};

const STATS: Stat[] = [
  {
    value: 51,
    suffix: "%",
    label: "of small aneurysms are missed on initial review",
    detail: "Subtle, sub-5mm lesions blend into normal vascular noise on a busy worklist.",
  },
  {
    value: 23,
    suffix: " min",
    label: "average added read time per complex angiogram",
    detail: "Manual vessel tracing and measurement consume time that could go to patients.",
  },
  {
    value: 3.4,
    suffix: "x",
    decimals: 1,
    label: "variability between readers on borderline cases",
    detail: "Risk scoring without standardized morphology metrics drifts by clinician and by day.",
  },
];

const CAUSES = [
  {
    title: "Delayed diagnosis",
    body: "Unruptured aneurysms are frequently asymptomatic until rupture — by the time symptoms surface, the window for safe intervention has narrowed.",
  },
  {
    title: "Human error & fatigue",
    body: "Radiologists review hundreds of studies a week. Subtle outpouchings near vessel bifurcations are exactly what fatigue causes eyes to skip.",
  },
  {
    title: "Complex imaging workflows",
    body: "Segmentation, measurement, and reporting today span disconnected tools — each handoff is a place for context, and confidence, to leak out.",
  },
];

export default function ProblemSection() {
  return (
    <section id="problem" className="relative scroll-mt-24 bg-ink-soft py-28 sm:py-36">
      <div className="mx-auto max-w-7xl px-6 sm:px-10">
        <Reveal>
          <p className="kicker eyebrow-line">The Problem</p>
          <h2 className="mt-5 max-w-3xl text-4xl font-bold leading-tight tracking-tight text-paper sm:text-5xl">
            Cerebral aneurysms are survivable —{" "}
            <span className="text-gradient">when they&apos;re caught.</span>
          </h2>
        </Reveal>

        <div className="mt-16 grid gap-6 sm:grid-cols-3">
          {STATS.map((stat, i) => (
            <Reveal key={stat.label} delay={i * 0.1}>
              <div className="glass-panel glass-panel-hover h-full rounded-2xl p-8">
                <div className="text-4xl font-bold text-cyan-300 sm:text-5xl">
                  <AnimatedCounter
                    value={stat.value}
                    suffix={stat.suffix}
                    decimals={stat.decimals ?? 0}
                  />
                </div>
                <p className="mt-4 text-sm font-semibold text-paper">
                  {stat.label}
                </p>
                <p className="mt-2 text-sm leading-relaxed text-paper-faint">
                  {stat.detail}
                </p>
              </div>
            </Reveal>
          ))}
        </div>

        <div className="mt-20 grid gap-8 border-t border-white/10 pt-16 sm:grid-cols-3">
          {CAUSES.map((cause, i) => (
            <Reveal key={cause.title} delay={i * 0.1} y={20}>
              <div className="flex h-full flex-col">
                <span className="mb-4 inline-flex h-9 w-9 items-center justify-center rounded-full border border-white/10 text-xs font-semibold text-cyan-300">
                  0{i + 1}
                </span>
                <h3 className="text-lg font-semibold text-paper">
                  {cause.title}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-paper-faint">
                  {cause.body}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
