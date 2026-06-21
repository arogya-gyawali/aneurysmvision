"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

const LINKS = [
  { label: "Problem", href: "#problem" },
  { label: "Solution", href: "#solution" },
  { label: "Technology", href: "#technology" },
  { label: "Platform", href: "#platform" },
  { label: "Results", href: "#results" },
  { label: "Research", href: "#research" },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    if (!menuOpen) return;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  return (
    <motion.header
      initial={{ y: -40, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.7, delay: 0.2 }}
      className={`fixed inset-x-0 top-0 z-50 transition-all duration-500 ${
        scrolled || menuOpen ? "glass-panel border-b" : "border-b border-transparent"
      }`}
    >
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 sm:px-10">
        <a href="#hero" className="flex items-center gap-2.5">
          <span className="relative flex h-7 w-7 items-center justify-center rounded-full bg-blue-500/20">
            <span className="h-2 w-2 rounded-full bg-cyan-400" />
            <span className="absolute inset-0 rounded-full border border-cyan-400/40" />
          </span>
          <span className="text-sm font-semibold tracking-wide text-paper">
            Aneurysm&nbsp;Vision
          </span>
        </a>

        <ul className="hidden items-center gap-8 text-sm text-paper-dim lg:flex">
          {LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="transition-colors duration-300 hover:text-cyan-300"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="flex items-center gap-3">
          <a
            href="#cta"
            onClick={() => setMenuOpen(false)}
            className="hidden whitespace-nowrap rounded-full border border-cyan-400/40 px-5 py-2 text-sm font-semibold text-paper transition-all duration-300 hover:border-cyan-400 hover:bg-cyan-400/10 hover:text-cyan-300 sm:inline-block"
          >
            Request Demo
          </a>

          <button
            type="button"
            aria-label={menuOpen ? "Close menu" : "Open menu"}
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((v) => !v)}
            className="flex h-9 w-9 items-center justify-center rounded-full border border-white/15 text-paper lg:hidden"
          >
            <span className="relative flex h-3.5 w-4 flex-col justify-between">
              <motion.span
                className="h-px w-full bg-current"
                animate={{ rotate: menuOpen ? 45 : 0, y: menuOpen ? 6 : 0 }}
              />
              <motion.span
                className="h-px w-full bg-current"
                animate={{ opacity: menuOpen ? 0 : 1 }}
              />
              <motion.span
                className="h-px w-full bg-current"
                animate={{ rotate: menuOpen ? -45 : 0, y: menuOpen ? -6 : 0 }}
              />
            </span>
          </button>
        </div>
      </nav>

      <AnimatePresence>
        {menuOpen && (
          <motion.ul
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden border-t border-white/10 lg:hidden"
          >
            {LINKS.map((link) => (
              <li key={link.href} className="border-b border-white/5">
                <a
                  href={link.href}
                  onClick={() => setMenuOpen(false)}
                  className="block px-6 py-4 text-sm text-paper-dim transition-colors duration-300 hover:text-cyan-300"
                >
                  {link.label}
                </a>
              </li>
            ))}
            <li className="px-6 py-4 sm:hidden">
              <a
                href="#cta"
                onClick={() => setMenuOpen(false)}
                className="block rounded-full bg-blue-500 px-5 py-2.5 text-center text-sm font-semibold text-white transition-colors duration-300 hover:bg-blue-400"
              >
                Request Demo
              </a>
            </li>
          </motion.ul>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
