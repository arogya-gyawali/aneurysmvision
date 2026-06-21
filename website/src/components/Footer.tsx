const COLUMNS = [
  {
    title: "Platform",
    links: [
      { label: "Solution", href: "#solution" },
      { label: "Technology", href: "#technology" },
      { label: "Features", href: "#platform" },
      { label: "Results", href: "#results" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "Research", href: "#research" },
      { label: "Request Demo", href: "#cta" },
      { label: "Contact", href: "#cta" },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="relative border-t border-white/10 bg-ink-soft">
      <div className="mx-auto max-w-7xl px-6 py-16 sm:px-10">
        <div className="flex flex-col gap-12 lg:flex-row lg:justify-between">
          <div className="max-w-sm">
            <a href="#hero" className="flex items-center gap-2.5">
              <span className="relative flex h-7 w-7 items-center justify-center rounded-full bg-blue-500/20">
                <span className="h-2 w-2 rounded-full bg-cyan-400" />
                <span className="absolute inset-0 rounded-full border border-cyan-400/40" />
              </span>
              <span className="text-sm font-semibold tracking-wide text-paper">
                Aneurysm&nbsp;Vision
              </span>
            </a>
            <p className="mt-5 text-sm leading-relaxed text-paper-faint">
              AI-assisted aneurysm detection, 3D vascular visualization, and
              risk-aware reporting — built to support the clinicians who make
              the final call, not replace them.
            </p>
          </div>

          <div className="flex flex-wrap gap-12">
            {COLUMNS.map((col) => (
              <div key={col.title}>
                <p className="text-xs font-semibold uppercase tracking-wide text-paper-faint">
                  {col.title}
                </p>
                <ul className="mt-4 flex flex-col gap-3">
                  {col.links.map((link) => (
                    <li key={link.label}>
                      <a
                        href={link.href}
                        className="text-sm text-paper-dim transition-colors duration-300 hover:text-cyan-300"
                      >
                        {link.label}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-14 flex flex-col gap-4 border-t border-white/10 pt-8 text-xs text-paper-faint sm:flex-row sm:items-center sm:justify-between">
          <p>
            © {new Date().getFullYear()} Aneurysm Vision. Investigational
            software — not yet cleared for independent clinical
            decision-making.
          </p>
          <p>Built on TOF-MRA. Every AI finding requires physician review.</p>
        </div>
      </div>
    </footer>
  );
}
