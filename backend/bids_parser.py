"""BIDS dataset discovery and entity parsing.

Maps to ``clabtoolkit.bidstools`` (future):
  - ``load_bids_json`` — BIDS schema configuration
  - ``str2entity`` / ``entity2str`` — filename entity parsing

Stage 1 implements lightweight path discovery and regex-based entity parsing
without clabtoolkit. Heavy validation remains deferred.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from backend.exceptions import ValidationError
from backend.models import AnalysisRequest, BidsEntities

logger = logging.getLogger(__name__)

# Primary TOF-MRA suffix; fallbacks tried in order when angio is absent.
PRIMARY_ANGIO_SUFFIX = "angio"
FALLBACK_SUFFIXES: tuple[str, ...] = ("angio", "MRA", "swi", "T1w")

_BIDS_KEY_PREFIXES = ("sub", "ses", "acq", "run", "task", "rec", "dir", "echo")


def _split_extension(basename: str) -> tuple[str, str]:
    if basename.endswith(".nii.gz"):
        return basename[: -len(".nii.gz")], "nii.gz"
    if basename.endswith(".nii"):
        return basename[: -len(".nii")], "nii"
    if basename.endswith(".json"):
        return basename[: -len(".json")], "json"
    raise ValidationError(f"Unsupported BIDS extension in filename: {basename}")


def _is_entity_part(part: str) -> bool:
    return any(part.startswith(f"{key}-") for key in _BIDS_KEY_PREFIXES)


def parse_bids_filename(filename: str) -> BidsEntities:
    """Extract BIDS entities from a neuroimaging filename stem or basename."""
    stem, extension = _split_extension(Path(filename).name)
    parts = stem.split("_")

    if not parts or not parts[0].startswith("sub-"):
        raise ValidationError(f"Missing subject entity in filename: {filename}")

    suffix_parts: list[str] = []
    while parts and not _is_entity_part(parts[-1]):
        suffix_parts.insert(0, parts.pop())

    if not suffix_parts:
        raise ValidationError(f"Missing suffix in filename: {filename}")

    parsed: dict[str, str] = {}
    index = 0
    while index < len(parts):
        part = parts[index]
        if not _is_entity_part(part):
            break

        key, value = part.split("-", 1)
        index += 1
        while index < len(parts) and not _is_entity_part(parts[index]):
            value = f"{value}_{parts[index]}"
            index += 1
        parsed[key] = value

    if "sub" not in parsed:
        raise ValidationError(f"Missing subject entity in filename: {filename}")

    return BidsEntities(
        sub=parsed["sub"],
        ses=parsed.get("ses"),
        acq=parsed.get("acq"),
        run=parsed.get("run"),
        suffix="_".join(suffix_parts),
        extension=extension,
    )


def resolve_nifti_path(request: AnalysisRequest) -> tuple[Path, Optional[BidsEntities]]:
    """Resolve the NIfTI path and optional BIDS entities from a request."""
    if request.nifti_path:
        path = Path(request.nifti_path)
        entities = parse_bids_filename(path.name) if _looks_like_bids(path.name) else None
        logger.info("Using direct NIfTI path: %s", path)
        return path, entities

    assert request.dataset_root is not None
    assert request.bids_entities is not None

    root = Path(request.dataset_root)
    if not root.is_dir():
        raise ValidationError(f"dataset_root does not exist: {root}")

    subject = request.bids_entities.subject
    session = request.bids_entities.session
    path = discover_tof_mra(root, subject=subject, session=session)
    entities = parse_bids_filename(path.name)
    logger.info("Discovered NIfTI via BIDS: %s", path)
    return path, entities


def discover_tof_mra(
    dataset_root: Path,
    subject: str,
    session: Optional[str] = None,
) -> Path:
    """Locate a TOF-MRA NIfTI file for a subject within a BIDS tree."""
    subject_dir = dataset_root / f"sub-{subject}"
    if not subject_dir.is_dir():
        raise ValidationError(f"Subject directory not found: {subject_dir}")

    search_roots = [subject_dir / f"ses-{session}"] if session else []
    search_roots.append(subject_dir)

    for root in search_roots:
        if not root.is_dir():
            continue
        for suffix in FALLBACK_SUFFIXES:
            matches = sorted(root.rglob(f"*_{suffix}.nii*"))
            if matches:
                chosen = matches[0]
                if suffix != PRIMARY_ANGIO_SUFFIX:
                    logger.warning(
                        "Primary suffix '%s' not found under %s; using fallback '%s': %s",
                        PRIMARY_ANGIO_SUFFIX,
                        root,
                        suffix,
                        chosen,
                    )
                return chosen

    suffix_list = ", ".join(FALLBACK_SUFFIXES)
    raise ValidationError(
        f"No NIfTI found for sub-{subject} with suffixes [{suffix_list}] under {subject_dir}"
    )


def validate_bids_dataset(dataset_root: Path) -> list[str]:
    """Return validation warnings for a BIDS dataset root.

    Full validation via clabtoolkit is deferred; this performs minimal checks.
    """
    warnings: list[str] = []
    if not (dataset_root / "dataset_description.json").exists():
        warnings.append("Missing dataset_description.json at BIDS root.")
    if not any(dataset_root.glob("sub-*")):
        warnings.append("No subject directories (sub-*) found at BIDS root.")
    return warnings


def _looks_like_bids(filename: str) -> bool:
    return Path(filename).name.startswith("sub-")
