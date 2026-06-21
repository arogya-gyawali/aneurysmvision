import * as THREE from "three";

export type Branch = {
  curve: THREE.CatmullRomCurve3;
  radius: number;
  depth: number;
};

export type Node = {
  position: THREE.Vector3;
  risk: "elevated" | "normal";
};

type BuildResult = {
  branches: Branch[];
  nodes: Node[];
};

/**
 * Deterministic pseudo-random generator so the same "scan" renders
 * identically every load instead of reshuffling the vessel tree.
 */
function makeRng(seed: number) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

function jitter(rng: () => number, amount: number) {
  return (rng() - 0.5) * 2 * amount;
}

/**
 * Builds a branching vascular-tree structure radiating from the origin,
 * standing in for a cerebral vessel network — not an anatomical model,
 * just a believable visual metaphor for "AI reads the vessel tree."
 *
 * Each branch is pulled gently back toward its assigned primary direction
 * every segment (rather than a pure random walk) so the structure stays
 * centered and frame-filling instead of drifting off to one side.
 */
export function buildVesselTree(seed = 7): BuildResult {
  const rng = makeRng(seed);
  const branches: Branch[] = [];
  const nodes: Node[] = [];
  const allPoints: THREE.Vector3[] = [];

  function grow(
    origin: THREE.Vector3,
    direction: THREE.Vector3,
    length: number,
    radius: number,
    depth: number,
    maxDepth: number
  ) {
    const bias = direction.clone().normalize();
    const segments = 4;
    const points: THREE.Vector3[] = [origin.clone()];
    let current = origin.clone();
    let dir = direction.clone();

    for (let i = 0; i < segments; i++) {
      dir = dir
        .clone()
        .lerp(bias, 0.3)
        .add(
          new THREE.Vector3(
            jitter(rng, 0.3),
            jitter(rng, 0.3),
            jitter(rng, 0.3)
          )
        )
        .normalize();
      current = current
        .clone()
        .add(dir.clone().multiplyScalar(length / segments));
      points.push(current);
    }

    const curve = new THREE.CatmullRomCurve3(points);
    branches.push({ curve, radius, depth });
    allPoints.push(...points);

    const isTip = depth >= maxDepth;
    if (isTip && rng() > 0.45) {
      nodes.push({
        position: current,
        risk: rng() > 0.72 ? "elevated" : "normal",
      });
    }

    if (depth < maxDepth) {
      const childCount = rng() > 0.4 ? 2 : 1;
      for (let c = 0; c < childCount; c++) {
        const spread = 0.85;
        const childDir = dir
          .clone()
          .add(
            new THREE.Vector3(
              jitter(rng, spread),
              jitter(rng, spread),
              jitter(rng, spread)
            )
          )
          .normalize();
        grow(
          current,
          childDir,
          length * (0.62 + rng() * 0.12),
          radius * 0.62,
          depth + 1,
          maxDepth
        );
      }
    }
  }

  const primaryCount = 6;
  for (let i = 0; i < primaryCount; i++) {
    const angle = (i / primaryCount) * Math.PI * 2;
    const dir = new THREE.Vector3(
      Math.cos(angle) * 0.85,
      0.55 + rng() * 0.25,
      Math.sin(angle) * 0.85
    ).normalize();
    grow(new THREE.Vector3(0, 0, 0), dir, 1.55, 0.045, 0, 3);
  }

  // Recenter the whole structure around its own bounding-box center so it
  // reliably sits in frame regardless of how the random walk unfolded.
  const box = new THREE.Box3();
  allPoints.forEach((p) => box.expandByPoint(p));
  const center = box.getCenter(new THREE.Vector3());

  branches.forEach((b) => {
    b.curve.points.forEach((p) => p.sub(center));
  });
  nodes.forEach((n) => n.position.sub(center));

  return { branches, nodes };
}
