"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import Reveal from "./Reveal";
import AnimatedCounter from "./AnimatedCounter";

const METRICS = [
  { value: 94.2, suffix: "%", decimals: 1, label: "Detection sensitivity" },
  { value: 91.8, suffix: "%", decimals: 1, label: "Specificity" },
  { value: 68, suffix: "%", label: "Reduction in read time" },
  { value: 12, suffix: "", label: "Validation studies in progress" },
];

const SENSITIVITY_BY_SIZE = [
  { size: "< 3mm", baseline: 41, assisted: 86 },
  { size: "3–5mm", baseline: 58, assisted: 93 },
  { size: "5–7mm", baseline: 79, assisted: 97 },
  { size: "> 7mm", baseline: 92, assisted: 99 },
];

function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-panel rounded-lg px-4 py-3 text-xs">
      <p className="mb-1.5 font-semibold text-paper">{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: {p.value}%
        </p>
      ))}
    </div>
  );
}

export default function ResultsSection() {
  const [chartVisible, setChartVisible] = useState(false);

  return (
    <section id="results" className="relative scroll-mt-24 bg-ink-soft py-28 sm:py-36">
      <div className="mx-auto max-w-7xl px-6 sm:px-10">
        <Reveal>
          <p className="kicker eyebrow-line">Results</p>
          <h2 className="mt-5 max-w-3xl text-4xl font-bold leading-tight tracking-tight text-paper sm:text-5xl">
            Measured against{" "}
            <span className="text-gradient">radiologist-reviewed ground truth.</span>
          </h2>
        </Reveal>

        <div className="mt-16 grid gap-6 sm:grid-cols-4">
          {METRICS.map((metric, i) => (
            <Reveal key={metric.label} delay={i * 0.08}>
              <div className="glass-panel glass-panel-hover rounded-2xl p-7 text-center">
                <div className="text-3xl font-bold text-cyan-300 sm:text-4xl">
                  <AnimatedCounter
                    value={metric.value}
                    suffix={metric.suffix}
                    decimals={metric.decimals ?? 0}
                  />
                </div>
                <p className="mt-2 text-xs leading-snug text-paper-faint">
                  {metric.label}
                </p>
              </div>
            </Reveal>
          ))}
        </div>

        <motion.div
          onViewportEnter={() => setChartVisible(true)}
          viewport={{ once: true, margin: "-100px" }}
          className="glass-panel mt-16 rounded-2xl p-6 sm:p-10"
        >
          <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-paper">
                Sensitivity by aneurysm size
              </h3>
              <p className="mt-1 text-sm text-paper-faint">
                Unassisted baseline read vs. Aneurysm Vision-assisted read,
                internal validation cohort.
              </p>
            </div>
            <div className="flex gap-5 text-xs">
              <span className="flex items-center gap-2 text-paper-dim">
                <span className="h-2.5 w-2.5 rounded-full bg-navy-600" />
                Baseline
              </span>
              <span className="flex items-center gap-2 text-paper-dim">
                <span className="h-2.5 w-2.5 rounded-full bg-cyan-400" />
                AI-assisted
              </span>
            </div>
          </div>

          <div className="h-[280px] w-full">
            {chartVisible && (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={SENSITIVITY_BY_SIZE} barGap={6}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(255,255,255,0.08)"
                    vertical={false}
                  />
                  <XAxis
                    dataKey="size"
                    stroke="rgba(170,184,209,0.6)"
                    tickLine={false}
                    axisLine={false}
                    fontSize={12}
                  />
                  <YAxis
                    stroke="rgba(170,184,209,0.6)"
                    tickLine={false}
                    axisLine={false}
                    fontSize={12}
                    width={36}
                  />
                  <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(94,149,255,0.06)" }} />
                  <Bar
                    name="Baseline"
                    dataKey="baseline"
                    fill="#1d3760"
                    radius={[6, 6, 0, 0]}
                    isAnimationActive
                    animationDuration={900}
                  />
                  <Bar
                    name="AI-assisted"
                    dataKey="assisted"
                    fill="#2dd6e8"
                    radius={[6, 6, 0, 0]}
                    isAnimationActive
                    animationDuration={900}
                    animationBegin={150}
                  />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
