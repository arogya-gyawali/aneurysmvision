"use client";

import { motion } from "framer-motion";
import Reveal from "./Reveal";
import { IconBolt, IconBrain, IconHeartPulse, IconShield } from "./icons";

const FEATURES = [
  {
    icon: IconBrain,
    title: "AI-assisted detection",
    body: "A detection model trained on annotated TOF-MRA studies surfaces candidate aneurysms across every major vascular territory — MCA, ACA, AComA, ICA, and beyond.",
  },
  {
    icon: IconBolt,
    title: "Faster analysis",
    body: "Segmentation, biomarker extraction, and mesh generation that took a manual workflow the better part of an hour now complete in under a minute.",
  },
  {
    icon: IconShield,
    title: "Improved clinical confidence",
    body: "Every finding ships with morphology-based risk scoring and the rationale behind it — a second opinion that shows its work, not a black box.",
  },
  {
    icon: IconHeartPulse,
    title: "Better patient outcomes",
    body: "Earlier, more consistent detection means more patients get to a treatment conversation while their options are still wide open.",
  },
];

export default function SolutionSection() {
  return (
    <section id="solution" className="relative scroll-mt-24 bg-ink py-28 sm:py-36">
      <div className="bg-grid absolute inset-0 opacity-20" />
      <div className="relative mx-auto max-w-7xl px-6 sm:px-10">
        <Reveal>
          <p className="kicker eyebrow-line">The Solution</p>
          <h2 className="mt-5 max-w-3xl text-4xl font-bold leading-tight tracking-tight text-paper sm:text-5xl">
            One platform, from{" "}
            <span className="text-gradient">raw scan to reviewed report.</span>
          </h2>
          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-paper-dim">
            Aneurysm Vision sits between the scanner and the radiologist —
            doing the repetitive vascular triage so clinicians can spend their
            attention on judgment, not measurement.
          </p>
        </Reveal>

        <div className="mt-16 grid gap-6 sm:grid-cols-2">
          {FEATURES.map((feature, i) => (
            <Reveal key={feature.title} delay={i * 0.08}>
              <motion.div
                whileHover={{ y: -6 }}
                transition={{ type: "spring", stiffness: 300, damping: 22 }}
                className="glass-panel glass-panel-hover group h-full rounded-2xl p-8"
              >
                <span className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/15 text-cyan-300 transition-colors duration-300 group-hover:bg-cyan-400/15">
                  <feature.icon />
                </span>
                <h3 className="mt-6 text-xl font-semibold text-paper">
                  {feature.title}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-paper-faint">
                  {feature.body}
                </p>
              </motion.div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
