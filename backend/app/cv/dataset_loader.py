"""TrustLens Multi-Format Dataset Ingestion Engine

Supports:
1. Image folders (flat directory or class subdirectories)
2. CSV metadata files (mapping relative/absolute image paths to labels & metadata)
3. YOLO-style datasets (images/ + labels/ paired directory structure with bounding boxes)
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import yaml

from app.core.hashing import hash_file, hash_bytes
from app.schemas.dataset import (
    DatasetFormatEnum,
    DatasetManifest,
    DatasetSample,
)

IMAGE_EXTENSIONS: Set[str] = {
    ".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"
}


def is_image_file(path: Path) -> bool:
    """Check if file extension matches supported image formats."""
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def detect_dataset_format(target_path: Path) -> DatasetFormatEnum:
    """Infer dataset format from directory structure or file type."""
    if target_path.is_file():
        if target_path.suffix.lower() == ".csv":
            return DatasetFormatEnum.CSV
        return DatasetFormatEnum.FOLDER

    if target_path.is_dir():
        # Check for YOLO structure: images/ and labels/ subdirectories
        has_images_dir = (target_path / "images").is_dir()
        has_labels_dir = (target_path / "labels").is_dir()
        if has_images_dir and has_labels_dir:
            return DatasetFormatEnum.YOLO

        # Check for CSV metadata file in root
        csv_candidates = list(target_path.glob("*.csv"))
        if csv_candidates:
            return DatasetFormatEnum.CSV

        return DatasetFormatEnum.FOLDER

    return DatasetFormatEnum.FOLDER


def load_folder_dataset(root: Path) -> Tuple[List[DatasetSample], List[str]]:
    """Ingest image directory. Detects class subfolders if present."""
    samples: List[DatasetSample] = []
    classes: Set[str] = set()
    sample_counter = 1

    # Check for class subdirectories
    subdirs = [d for d in root.iterdir() if d.is_dir() and not d.name.startswith(".")]

    if subdirs and any(any(is_image_file(f) for f in d.iterdir()) for d in subdirs if d.is_dir()):
        # Hierarchical class-folder dataset
        for subdir in sorted(subdirs):
            class_name = subdir.name
            classes.add(class_name)
            for img_file in sorted(subdir.iterdir()):
                if is_image_file(img_file):
                    sample_id = f"SMPL-{sample_counter:05d}"
                    sample_counter += 1
                    samples.append(
                        DatasetSample(
                            sample_id=sample_id,
                            file_path=str(img_file.resolve()),
                            label=class_name,
                            metadata={"relative_path": str(img_file.relative_to(root))},
                        )
                    )
    else:
        # Flat image folder
        for img_file in sorted(root.rglob("*")):
            if is_image_file(img_file):
                sample_id = f"SMPL-{sample_counter:05d}"
                sample_counter += 1
                samples.append(
                    DatasetSample(
                        sample_id=sample_id,
                        file_path=str(img_file.resolve()),
                        label=None,
                        metadata={"relative_path": str(img_file.relative_to(root))},
                    )
                )

    return samples, sorted(list(classes))


def load_csv_dataset(csv_path: Path) -> Tuple[List[DatasetSample], List[str]]:
    """Ingest dataset defined by a CSV file mapping image paths to labels."""
    samples: List[DatasetSample] = []
    classes: Set[str] = set()
    sample_counter = 1

    base_dir = csv_path.parent if csv_path.is_file() else csv_path
    actual_csv = csv_path if csv_path.is_file() else next(csv_path.glob("*.csv"))

    with actual_csv.open("r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return samples, []

        # Find image path column
        fieldnames_lower = {fn.lower().strip(): fn for fn in reader.fieldnames}
        img_col = None
        for candidate in ["filepath", "file_path", "image_path", "filename", "image", "path", "file"]:
            if candidate in fieldnames_lower:
                img_col = fieldnames_lower[candidate]
                break

        # Find label column
        label_col = None
        for candidate in ["label", "class", "category", "target", "annotation"]:
            if candidate in fieldnames_lower:
                label_col = fieldnames_lower[candidate]
                break

        if not img_col:
            # Fallback to first column if no recognizable name
            img_col = reader.fieldnames[0]

        for row in reader:
            raw_path = row.get(img_col, "").strip()
            if not raw_path:
                continue

            resolved_path = Path(raw_path)
            if not resolved_path.is_absolute():
                resolved_path = (base_dir / raw_path).resolve()

            label_val = row.get(label_col).strip() if label_col and row.get(label_col) else None
            if label_val:
                classes.add(label_val)

            sample_id = f"SMPL-{sample_counter:05d}"
            sample_counter += 1
            # Filter extra metadata columns
            extra_meta = {k: v for k, v in row.items() if k not in [img_col, label_col]}

            samples.append(
                DatasetSample(
                    sample_id=sample_id,
                    file_path=str(resolved_path),
                    label=label_val,
                    metadata=extra_meta,
                )
            )

    return samples, sorted(list(classes))


def load_yolo_dataset(root: Path) -> Tuple[List[DatasetSample], List[str]]:
    """Ingest YOLO-formatted dataset (images/ and labels/ directory pairs)."""
    samples: List[DatasetSample] = []
    classes: List[str] = []
    sample_counter = 1

    # Check for classes.txt or data.yaml
    classes_file = root / "classes.txt"
    if classes_file.is_file():
        with classes_file.open("r", encoding="utf-8") as f:
            classes = [line.strip() for line in f if line.strip()]
    else:
        yaml_files = list(root.glob("*.yaml")) + list(root.glob("*.yml"))
        if yaml_files:
            try:
                with yaml_files[0].open("r", encoding="utf-8") as yf:
                    data = yaml.safe_load(yf)
                    if isinstance(data, dict) and "names" in data:
                        names_entry = data["names"]
                        if isinstance(names_entry, list):
                            classes = [str(n) for n in names_entry]
                        elif isinstance(names_entry, dict):
                            classes = [str(names_entry[k]) for k in sorted(names_entry.keys())]
            except Exception:
                pass

    images_root = root / "images"
    labels_root = root / "labels"

    for img_file in sorted(images_root.rglob("*")):
        if is_image_file(img_file):
            # Locate corresponding label text file
            rel_path = img_file.relative_to(images_root)
            label_file = labels_root / rel_path.with_suffix(".txt")

            boxes: List[Dict[str, float]] = []
            present_class_ids: Set[int] = set()

            if label_file.is_file():
                try:
                    with label_file.open("r", encoding="utf-8") as lf:
                        for line in lf:
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                cid = int(parts[0])
                                present_class_ids.add(cid)
                                boxes.append({
                                    "class_id": cid,
                                    "x_center": float(parts[1]),
                                    "y_center": float(parts[2]),
                                    "width": float(parts[3]),
                                    "height": float(parts[4]),
                                })
                except Exception:
                    pass

            primary_label = None
            if present_class_ids:
                first_cid = sorted(list(present_class_ids))[0]
                if 0 <= first_cid < len(classes):
                    primary_label = classes[first_cid]
                else:
                    primary_label = f"class_{first_cid}"

            sample_id = f"SMPL-{sample_counter:05d}"
            sample_counter += 1
            samples.append(
                DatasetSample(
                    sample_id=sample_id,
                    file_path=str(img_file.resolve()),
                    label=primary_label,
                    metadata={
                        "yolo_boxes": boxes,
                        "class_ids": sorted(list(present_class_ids)),
                        "label_file": str(label_file.resolve()) if label_file.is_file() else None,
                    },
                )
            )

    return samples, classes


def load_dataset(
    dataset_path: Path | str,
    format_hint: DatasetFormatEnum = DatasetFormatEnum.AUTO,
) -> DatasetManifest:
    """Unified entrypoint to ingest any supported dataset format.

    Args:
        dataset_path: Path to dataset directory or CSV file.
        format_hint: Explicit format or AUTO detection.

    Returns:
        DatasetManifest containing all normalized samples, classes, and metadata.
    """
    target = Path(dataset_path).resolve()
    if not target.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {target}")

    detected_format = (
        detect_dataset_format(target)
        if format_hint == DatasetFormatEnum.AUTO
        else format_hint
    )

    if detected_format == DatasetFormatEnum.YOLO:
        samples, classes = load_yolo_dataset(target)
    elif detected_format == DatasetFormatEnum.CSV:
        actual_csv = target if target.is_file() else target
        samples, classes = load_csv_dataset(actual_csv)
    else:
        samples, classes = load_folder_dataset(target)

    # Compute deterministic dataset manifest hash
    manifest_bytes = f"{target.name}:{len(samples)}:{','.join(classes)}".encode("utf-8")
    manifest_hash = hash_bytes(manifest_bytes)

    return DatasetManifest(
        dataset_id=f"DS-{target.name[:12].upper()}-{manifest_hash[:8]}",
        dataset_name=target.name,
        detected_format=detected_format,
        root_path=str(target),
        total_samples=len(samples),
        samples=samples,
        classes=classes,
        manifest_hash=manifest_hash,
    )
