"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Reveal from "./Reveal";
import {
  IconActivity,
  IconCube,
  IconFile,
  IconLayers,
  IconScan,
} from "./icons";

const FEATURES = [
  {
    icon: IconActivity,
    title: "Real-time analysis",
    body: "Drop a scan and the full pipeline — detection through report — runs automatically, with live stage-by-stage progress.",
    metric: "≈ 45s",
    metricLabel: "typical end-to-end runtime",
  },
  {
    icon: IconLayers,
    title: "Automated segmentation",
    body: "Vascular territories are segmented and ranked by detector confidence, no manual region-drawing required.",
    metric: "8",
    metricLabel: "vascular territories covered",
  },
  {
    icon: IconScan,
    title: "Risk assessment",
    body: "Aspect ratio, size ratio, and irregularity index combine into a transparent, explainable risk score per finding.",
    metric: "0–100",
    metricLabel: "explainable risk scale",
  },
  {
    icon: IconCube,
    title: "3D visualization",
    body: "Every detected aneurysm renders as an interactive 3D mesh, labeled directly in the scene by vascular territory.",
    metric: "360°",
    metricLabel: "interactive reconstruction",
  },
  {
    icon: IconFile,
    title: "Clinical reporting",
    body: "A structured, cautiously worded draft report is ready for physician review the moment analysis completes.",
    metric: "1 click",
    metricLabel: "to export PDF / JSON",
  },
];

export default function PlatformFeaturesSection() {
  const [active, setActive] = useState(0);
  const feature = FEATURES[active];

  return (
    <section id="platform" className="relative scroll-mt-24 bg-ink py-28 sm:py-36">
      <div className="mx-auto max-w-7xl px-6 sm:px-10">
        <Reveal>
          <p className="kicker eyebrow-line">Platform Features</p>
          <h2 className="mt-5 max-w-3xl text-4xl font-bold leading-tight tracking-tight text-paper sm:text-5xl">
            Everything a radiologist needs,{" "}
            <span className="text-gradient">nothing they have to assemble.</span>
          </h2>
        </Reveal>

        <div className="mt-16 grid gap-10 lg:grid-cols-[minmax(0,320px)_1fr]">
          <Reveal delay={0.05}>
            <div className="flex flex-col gap-2">
              {FEATURES.map((f, i) => {
                const isActive = i === active;
                return (
                  <button
                    key={f.title}
                    onClick={() => setActive(i)}
                    className={`group relative flex items-center gap-4 rounded-xl px-5 py-4 text-left transition-colors duration-300 ${
                      isActive
                        ? "bg-navy-800/80 text-paper"
                        : "text-paper-dim hover:bg-navy-900/60 hover:text-paper"
                    }`}
                  >
                    {isActive && (
                      <motion.span
                        layoutId="feature-pill"
                        className="absolute inset-0 rounded-xl border border-cyan-400/30"
                        transition={{ type: "spring", stiffness: 350, damping: 30 }}
                      />
                    )}
                    <span
                      className={`relative flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${
                        isActive ? "bg-cyan-400/15 text-cyan-300" : "bg-white/5 text-paper-faint"
                      }`}
                    >
                      <f.icon width={18} height={18} />
                    </span>
                    <span className="relative text-sm font-semibold">{f.title}</span>
                  </button>
                );
              })}
            </div>
          </Reveal>

          <Reveal delay={0.1}>
            <div className="glass-panel relative min-h-[320px] overflow-hidden rounded-2xl p-8 sm:p-10">
              <AnimatePresence mode="wait">
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -16 }}
                  transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                  className="flex h-full flex-col justify-between gap-10 sm:flex-row sm:items-center"
                >
                  <div className="max-w-md">
                    <span className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/15 text-cyan-300">
                      <feature.icon />
                    </span>
                    <h3 className="mt-6 text-2xl font-semibold text-paper">
                      {feature.title}
                    </h3>
                    <p className="mt-3 text-sm leading-relaxed text-paper-faint">
                      {feature.body}
                    </p>
                  </div>

                  <div className="flex shrink-0 flex-col items-start gap-1 rounded-xl border border-white/10 bg-ink/60 px-7 py-6 sm:items-center">
                    <span className="text-3xl font-bold text-gradient">
                      {feature.metric}
                    </span>
                    <span className="text-center text-[11px] uppercase tracking-wide text-paper-faint">
                      {feature.metricLabel}
                    </span>
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
