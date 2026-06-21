"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Reveal from "./Reveal";

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

const STAGES = [
  { label: "BIDS Parsing", detail: "Validates study layout & metadata" },
  { label: "NIfTI Loading", detail: "Loads the 3D TOF-MRA volume" },
  { label: "Quality Control", detail: "Checks SNR, motion, coverage" },
  { label: "Aneurysm Detection", detail: "CNN-based candidate localization" },
  { label: "ROI Extraction", detail: "Isolates each vascular region" },
  { label: "Biomarker Computation", detail: "Volume, diameter, aspect ratio" },
  { label: "Mesh Generation", detail: "Exports a reviewable 3D surface" },
  { label: "Report Generation", detail: "Drafts a cautious clinical summary" },
];

export default function TechnologySection() {
  const lineRef = useRef<HTMLDivElement>(null);
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!lineRef.current || !sectionRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo(
        lineRef.current,
        { scaleX: 0 },
        {
          scaleX: 1,
          ease: "none",
          scrollTrigger: {
            trigger: sectionRef.current,
            start: "top 70%",
            end: "bottom 60%",
            scrub: true,
          },
        }
      );
    }, sectionRef);
    return () => ctx.revert();
  }, []);

  return (
    <section
      id="technology"
      ref={sectionRef}
      className="relative scroll-mt-24 bg-ink-soft py-28 sm:py-36"
    >
      <div className="mx-auto max-w-7xl px-6 sm:px-10">
        <Reveal>
          <p className="kicker eyebrow-line">The Technology</p>
          <h2 className="mt-5 max-w-3xl text-4xl font-bold leading-tight tracking-tight text-paper sm:text-5xl">
            An imaging pipeline built for{" "}
            <span className="text-gradient">scientific scrutiny.</span>
          </h2>
          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-paper-dim">
            Every stage emits its own timing, confidence, and quality
            signals — nothing about a finding is a mystery, including how
            the platform arrived at it.
          </p>
        </Reveal>

        <div className="relative mt-20 hidden lg:block">
          <div className="absolute left-0 right-0 top-6 h-px bg-white/10" />
          <div
            ref={lineRef}
            className="absolute left-0 right-0 top-6 h-px origin-left bg-gradient-to-r from-blue-500 via-cyan-400 to-cyan-300"
          />
          <div className="grid grid-cols-8 gap-4">
            {STAGES.map((stage, i) => (
              <Reveal key={stage.label} delay={i * 0.06} y={16}>
                <div className="flex flex-col items-start">
                  <span className="mb-6 block h-3 w-3 rounded-full border-2 border-cyan-400 bg-ink-soft" />
                  <span className="text-xs font-semibold text-paper">
                    {stage.label}
                  </span>
                  <span className="mt-1.5 text-[11px] leading-snug text-paper-faint">
                    {stage.detail}
                  </span>
                </div>
              </Reveal>
            ))}
          </div>
        </div>

        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:hidden">
          {STAGES.map((stage, i) => (
            <Reveal key={stage.label} delay={i * 0.05} y={14}>
              <div className="glass-panel flex items-start gap-4 rounded-xl p-4">
                <span className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-cyan-400/50 text-[11px] font-semibold text-cyan-300">
                  {i + 1}
                </span>
                <div>
                  <p className="text-sm font-semibold text-paper">
                    {stage.label}
                  </p>
                  <p className="mt-1 text-xs text-paper-faint">
                    {stage.detail}
                  </p>
                </div>
              </div>
            </Reveal>
          ))}
        </div>

        <Reveal delay={0.1}>
          <div className="glass-panel mt-16 grid gap-8 rounded-2xl p-8 sm:grid-cols-3 sm:p-10">
            <div>
              <p className="text-sm font-semibold text-cyan-300">
                Detection model
              </p>
              <p className="mt-2 text-sm leading-relaxed text-paper-dim">
                3D convolutional architecture trained on multi-center TOF-MRA
                data, tuned for sensitivity on sub-5mm saccular aneurysms.
              </p>
            </div>
            <div>
              <p className="text-sm font-semibold text-cyan-300">
                Visualization engine
              </p>
              <p className="mt-2 text-sm leading-relaxed text-paper-dim">
                Per-finding mesh export renders directly in an interactive 3D
                viewer, with every detected territory labeled in-scene.
              </p>
            </div>
            <div>
              <p className="text-sm font-semibold text-cyan-300">
                Reporting layer
              </p>
              <p className="mt-2 text-sm leading-relaxed text-paper-dim">
                Drafts findings and recommendations in cautious,
                review-first language — always routed through a clinician
                before it informs care.
              </p>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
