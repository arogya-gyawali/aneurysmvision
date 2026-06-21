"use client";

import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { buildVesselTree } from "./vesselTree";
import { usePrefersReducedMotion } from "@/lib/usePrefersReducedMotion";

function Branch({
  curve,
  radius,
  depth,
}: {
  curve: THREE.CatmullRomCurve3;
  radius: number;
  depth: number;
}) {
  const geometry = useMemo(
    () => new THREE.TubeGeometry(curve, 24, radius, 8, false),
    [curve, radius]
  );
  const opacity = depth === 0 ? 0.95 : Math.max(0.35, 0.9 - depth * 0.16);

  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial
        color={depth <= 1 ? "#5e95ff" : "#2dd6e8"}
        emissive={depth <= 1 ? "#1d3760" : "#0d3b42"}
        emissiveIntensity={0.6}
        transparent
        opacity={opacity}
        roughness={0.35}
        metalness={0.15}
      />
    </mesh>
  );
}

function RiskNode({
  position,
  risk,
}: {
  position: THREE.Vector3;
  risk: "elevated" | "normal";
}) {
  const ref = useRef<THREE.Mesh>(null);
  const phase = useMemo(
    () => (Math.abs(position.x * 12.9 + position.y * 78.2 + position.z * 37.7) % (Math.PI * 2)),
    [position]
  );
  const color = risk === "elevated" ? "#ff6b5e" : "#7ce9f2";
  const reducedMotion = usePrefersReducedMotion();
  const baseScale = risk === "elevated" ? 0.055 : 0.034;

  useFrame(({ clock }) => {
    if (!ref.current) return;
    if (reducedMotion) {
      ref.current.scale.setScalar(baseScale);
      return;
    }
    const t = clock.getElapsedTime() * 1.6 + phase;
    const s = risk === "elevated" ? 1 + Math.sin(t) * 0.22 : 1 + Math.sin(t) * 0.08;
    ref.current.scale.setScalar(s * baseScale);
  });

  return (
    <mesh ref={ref} position={position}>
      <sphereGeometry args={[1, 16, 16]} />
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={risk === "elevated" ? 2.2 : 1.1}
        toneMapped={false}
      />
    </mesh>
  );
}

export default function VesselNetwork() {
  const groupRef = useRef<THREE.Group>(null);
  const { branches, nodes } = useMemo(() => buildVesselTree(11), []);
  const target = useRef({ x: 0, y: 0 });
  const reducedMotion = usePrefersReducedMotion();

  useFrame((state) => {
    if (!groupRef.current) return;
    if (reducedMotion) {
      groupRef.current.rotation.set(-0.15, 0.15, 0);
      return;
    }
    const { pointer } = state;
    target.current.x += (pointer.x * 0.35 - target.current.x) * 0.04;
    target.current.y += (pointer.y * 0.2 - target.current.y) * 0.04;
    groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.09 + target.current.x;
    groupRef.current.rotation.x = -0.15 + target.current.y * 0.4;
  });

  return (
    <group ref={groupRef} position={[0, -0.5, 0]} scale={1.65}>
      {branches.map((b, i) => (
        <Branch key={i} curve={b.curve} radius={b.radius} depth={b.depth} />
      ))}
      {nodes.map((n, i) => (
        <RiskNode key={i} position={n.position} risk={n.risk} />
      ))}
    </group>
  );
}
