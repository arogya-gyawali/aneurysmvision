import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

const base = {
  width: 22,
  height: 22,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

export function IconBrain(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M9.5 3.5a3 3 0 0 0-3 3v.2A3.3 3.3 0 0 0 4.5 9.7v.6A3 3 0 0 0 4 16a3.3 3.3 0 0 0 3.2 3.3 3 3 0 0 0 2.8 1.7" />
      <path d="M14.5 3.5a3 3 0 0 1 3 3v.2a3.3 3.3 0 0 1 2 2.9v.7a3 3 0 0 1 .6 5.7 3.3 3.3 0 0 1-3.3 3.3 3 3 0 0 1-2.8 1.7" />
      <path d="M9.5 3.5v17" />
      <path d="M14.5 3.5v17" />
    </svg>
  );
}

export function IconBolt(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M13 2 4 14h6l-1 8 9-12h-6z" />
    </svg>
  );
}

export function IconShield(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M12 3 4.5 5.8v5.6c0 5 3.3 7.7 7.5 9.6 4.2-1.9 7.5-4.6 7.5-9.6V5.8L12 3Z" />
      <path d="m9.5 12.5 1.8 1.8 3.5-4" />
    </svg>
  );
}

export function IconHeartPulse(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M3 13h3.2l1.8-3 2.4 6 2-4.5 1.6 1.5H21" />
      <path d="M12 19.5C7 16.8 3.5 14 3.5 9.8A4 4 0 0 1 11 8a3.3 3.3 0 0 1 1 .3A4 4 0 0 1 20.5 9.8c0 4.2-3.5 7-8.5 9.7Z" />
    </svg>
  );
}

export function IconLayers(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="m12 3 8.5 4.5L12 12 3.5 7.5 12 3Z" />
      <path d="m3.5 12 8.5 4.5 8.5-4.5" />
      <path d="m3.5 16.5 8.5 4.5 8.5-4.5" />
    </svg>
  );
}

export function IconActivity(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M3 12h4l2.5 7L14 5l2.5 7H21" />
    </svg>
  );
}

export function IconScan(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M4 8V5.5A1.5 1.5 0 0 1 5.5 4H8" />
      <path d="M16 4h2.5A1.5 1.5 0 0 1 20 5.5V8" />
      <path d="M20 16v2.5a1.5 1.5 0 0 1-1.5 1.5H16" />
      <path d="M8 20H5.5A1.5 1.5 0 0 1 4 18.5V16" />
      <circle cx="12" cy="12" r="3.4" />
    </svg>
  );
}

export function IconFile(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M7 3.5h7l3.5 3.5V20a.5.5 0 0 1-.5.5H7a.5.5 0 0 1-.5-.5V4a.5.5 0 0 1 .5-.5Z" />
      <path d="M14 3.5V7h3.5" />
      <path d="M9 13h6M9 16h6" />
    </svg>
  );
}

export function IconUsers(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <circle cx="9" cy="8" r="3" />
      <path d="M3.5 19c0-3 2.5-5 5.5-5s5.5 2 5.5 5" />
      <circle cx="17" cy="9" r="2.4" />
      <path d="M15.5 19c.3-2.2 1.8-3.7 3.7-4.2" />
    </svg>
  );
}

export function IconMicroscope(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M9 19h7" />
      <path d="M10.5 19v-3.2A4.3 4.3 0 0 1 8 11.8L11.5 8" />
      <path d="m9.5 6.5 4 4" />
      <path d="m13 4 3 3" />
      <circle cx="16" cy="17" r="2.2" />
    </svg>
  );
}

export function IconCube(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z" />
      <path d="M12 21v-9" />
      <path d="m4 7.5 8 4.5 8-4.5" />
    </svg>
  );
}

export function IconArrowUpRight(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M7 17 17 7" />
      <path d="M9 7h8v8" />
    </svg>
  );
}
