"use client";

import { Canvas } from "@react-three/fiber";
import { Suspense } from "react";
import VesselNetwork from "./VesselNetwork";
import ParticleField from "./ParticleField";

export default function HeroCanvas() {
  return (
    <Canvas
      camera={{ position: [0, 0.2, 5.2], fov: 42 }}
      dpr={[1, 1.8]}
      gl={{ antialias: true, alpha: true }}
    >
      <color attach="background" args={["#04070d"]} />
      <fog attach="fog" args={["#04070d", 6, 11]} />
      <ambientLight intensity={0.45} />
      <pointLight position={[3, 3, 4]} intensity={28} color="#5e95ff" />
      <pointLight position={[-4, -2, -2]} intensity={18} color="#2dd6e8" />
      <directionalLight position={[0, 4, 2]} intensity={0.6} color="#eef3fb" />
      <Suspense fallback={null}>
        <VesselNetwork />
        <ParticleField />
      </Suspense>
    </Canvas>
  );
}
