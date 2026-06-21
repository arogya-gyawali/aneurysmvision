"use client";

import dynamic from "next/dynamic";
import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import gsap from "gsap";

const HeroCanvas = dynamic(() => import("./hero/HeroCanvas"), {
  ssr: false,
});

const headline = "See What Others Miss.".split(" ");

export default function Hero() {
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!contentRef.current) return;
    const ctx = gsap.context(() => {
      gsap.to(contentRef.current, {
        yPercent: 18,
        opacity: 0.15,
        ease: "none",
        scrollTrigger: {
          trigger: "#hero",
          start: "top top",
          end: "bottom top",
          scrub: true,
        },
      });
    });
    return () => ctx.revert();
  }, []);

  return (
    <section
      id="hero"
      className="relative flex min-h-screen w-full items-center overflow-hidden bg-ink"
    >
      <div className="absolute inset-0 bg-grid opacity-40" />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-ink" />
      <div className="absolute inset-0">
        <HeroCanvas />
      </div>
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-r from-ink via-transparent to-ink/40" />

      <div
        ref={contentRef}
        className="relative z-10 mx-auto w-full max-w-7xl px-6 pt-24 sm:px-10"
      >
        <div className="max-w-2xl">
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="kicker eyebrow-line mb-6"
          >
            AI-Assisted Cerebral Aneurysm Detection
          </motion.p>

          <h1 className="font-sans text-5xl font-bold leading-[1.05] tracking-tight text-paper sm:text-6xl lg:text-7xl">
            {headline.map((word, i) => (
              <span key={i} className="inline-block overflow-hidden pb-1 align-bottom">
                <motion.span
                  className={`inline-block ${word === "Miss." ? "text-gradient" : ""}`}
                  initial={{ y: "110%" }}
                  animate={{ y: "0%" }}
                  transition={{
                    duration: 0.9,
                    delay: 0.15 + i * 0.08,
                    ease: [0.16, 1, 0.3, 1],
                  }}
                >
                  {word}&nbsp;
                </motion.span>
              </span>
            ))}
          </h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.65 }}
            className="mt-7 max-w-xl text-lg leading-relaxed text-paper-dim"
          >
            Aneurysm Vision reads TOF-MRA scans the way a tireless specialist
            would — segmenting the cerebral vasculature, flagging candidate
            aneurysms, and scoring rupture risk in minutes, with every finding
            visualized in 3D for the radiologist&apos;s final read.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.85 }}
            className="mt-10 flex flex-wrap items-center gap-4"
          >
            <a
              href="#cta"
              className="glow-cyan rounded-full bg-blue-500 px-7 py-3.5 text-sm font-semibold text-white transition-transform duration-300 hover:scale-105 hover:bg-blue-400"
            >
              Request Demo
            </a>
            <a
              href="#technology"
              className="rounded-full border border-white/15 px-7 py-3.5 text-sm font-semibold text-paper transition-colors duration-300 hover:border-cyan-400/60 hover:text-cyan-300"
            >
              Learn More
            </a>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 1.1 }}
            className="mt-16 flex items-center gap-6 text-xs text-paper-faint"
          >
            <span>FDA-pathway research build</span>
            <span className="h-1 w-1 rounded-full bg-paper-faint/60" />
            <span>HIPAA-aware architecture</span>
            <span className="h-1 w-1 rounded-full bg-paper-faint/60" />
            <span>Built on TOF-MRA</span>
          </motion.div>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.4, duration: 0.8 }}
        className="absolute bottom-8 left-1/2 z-10 flex -translate-x-1/2 flex-col items-center gap-2 text-paper-faint"
      >
        <span className="text-[11px] uppercase tracking-[0.2em]">Scroll</span>
        <span className="h-9 w-px animate-pulse bg-gradient-to-b from-cyan-400 to-transparent" />
      </motion.div>
    </section>
  );
}
