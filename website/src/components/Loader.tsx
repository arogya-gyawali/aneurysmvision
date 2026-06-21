"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

export default function Loader() {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const reduced = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;
    const timer = setTimeout(() => setVisible(false), reduced ? 150 : 1400);
    return () => clearTimeout(timer);
  }, []);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-ink"
          exit={{ opacity: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="relative flex h-16 w-16 items-center justify-center">
            <motion.span
              className="absolute inset-0 rounded-full border border-cyan-400/40"
              animate={{ scale: [1, 1.5], opacity: [0.6, 0] }}
              transition={{ duration: 1.4, repeat: Infinity, ease: "easeOut" }}
            />
            <motion.span
              className="absolute inset-0 rounded-full border border-blue-500/30"
              animate={{ scale: [1, 1.5], opacity: [0.6, 0] }}
              transition={{
                duration: 1.4,
                repeat: Infinity,
                ease: "easeOut",
                delay: 0.5,
              }}
            />
            <span className="h-3 w-3 rounded-full bg-cyan-400" />
          </div>
          <p className="mt-6 text-xs uppercase tracking-[0.25em] text-paper-faint">
            Aneurysm Vision
          </p>
          <div className="mt-5 h-px w-40 overflow-hidden bg-white/10">
            <motion.div
              className="h-full bg-gradient-to-r from-blue-500 to-cyan-400"
              initial={{ width: "0%" }}
              animate={{ width: "100%" }}
              transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
            />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
