#!/usr/bin/env python3
import os
from pathlib import Path

# Base paths
preproc_dir = Path("/data0/Studies/BEAM2/Preproc")
xcp_d_base = Path("/data0/Studies/BEAM2/xcp_d/xcpd_out/xcp_d")
subjects_base = Path("/data0/Studies/BEAM2/fw-sync/BEAM2/SUBJECTS")

for xcp_d_entry in sorted(xcp_d_base.glob("sub-*")):
    if not xcp_d_entry.is_dir():
        continue  # Skip non-directories like .html files

    sub_id = xcp_d_entry.name  # e.g., sub-1001
    sid = sub_id.replace("sub-", "")  # e.g., 1001

    # Confirm fmriprep output exists
    subject_analyses = subjects_base / sid / "ANALYSES"
    fmriprep_dirs = sorted(subject_analyses.glob("bids-fmriprep_*"), key=os.path.getmtime)
    if not fmriprep_dirs:
        print(f"No bids-fmriprep dir for {sub_id}")
        continue

    # Use latest bids-fmriprep directory
    latest_fmriprep = fmriprep_dirs[-1]
    fmriprep_output_root = latest_fmriprep / "OUTPUT" / "xcpd_unzipped"
    if not fmriprep_output_root.exists():
        print(f"No xcpd_unzipped in {latest_fmriprep}")
        continue

    # Find correct hash subdir
    hash_dirs = list(fmriprep_output_root.glob("*/fmriprep"))
    if not hash_dirs:
        print(f"No fmriprep folder found in xcpd_unzipped for {sub_id}")
        continue

    hash_dir = hash_dirs[0].parent
    fmriprep_path = hash_dir / "fmriprep" / sub_id
    freesurfer_path = hash_dir / "freesurfer" / sub_id

    if not fmriprep_path.exists() or not freesurfer_path.exists():
        print(f"Missing fmriprep or freesurfer for {sub_id}")
        continue

    # Create Preproc subdir and symlinks
    target_dir = preproc_dir / sub_id
    target_dir.mkdir(parents=True, exist_ok=True)

    links = {
        "fmriprep": fmriprep_path,
        "freesurfer": freesurfer_path,
        "xcp_d": xcp_d_entry,
    }

    # Link summary .html reports
    summary_htmls = list(xcp_d_base.glob(f"{sub_id}*.html"))
    for html_file in summary_htmls:
        dest = target_dir / html_file.name
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        dest.symlink_to(html_file)
        print(f"Linked summary: {html_file.name} for {sub_id}")

    # Link fmriprep, freesurfer, xcp_d
    for name, src in links.items():
        link_path = target_dir / name
        if link_path.exists() or link_path.is_symlink():
            link_path.unlink()
        link_path.symlink_to(src)
        print(f"Linked {name} for {sub_id}")

