#!/usr/bin/env python3
import os
from pathlib import Path

# New base paths
preproc_root = Path("/data0/Studies/BEAM2/Preproc/fMRIprep-XCPD")
freesurfer_root = Path("/data0/Studies/BEAM2/SourceData/freesurfer")
xcp_d_base = Path("/data0/Studies/BEAM2/xcp_d/xcpd_out/xcp_d")
subjects_base = Path("/data0/Studies/BEAM2/fw-sync/BEAM2/SUBJECTS")

for xcp_d_entry in sorted(xcp_d_base.glob("sub-*")):
    if not xcp_d_entry.is_dir():
        continue

    sub_id = xcp_d_entry.name  # e.g., sub-1001
    sid = sub_id.replace("sub-", "")  # e.g., 1001

    # Confirm fmriprep output exists
    subject_analyses = subjects_base / sid / "ANALYSES"
    fmriprep_dirs = sorted(subject_analyses.glob("bids-fmriprep_*"), key=os.path.getmtime)
    if not fmriprep_dirs:
        print(f"No bids-fmriprep dir for {sub_id}")
        continue

    # Locate latest bids-fmriprep unzipped output
    latest_fmriprep = fmriprep_dirs[-1]
    fmriprep_output_root = latest_fmriprep / "OUTPUT" / "xcpd_unzipped"
    if not fmriprep_output_root.exists():
        print(f"No xcpd_unzipped in {latest_fmriprep}")
        continue

    # Locate actual fmriprep path
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

    # Make subject directory under fMRIprep-XCPD
    subject_target_dir = preproc_root / sub_id
    subject_target_dir.mkdir(parents=True, exist_ok=True)

    # Create symlinks under new structure
    links = {
        subject_target_dir / "fmriprep": fmriprep_path,
        subject_target_dir / "xcp_d": xcp_d_entry,
        freesurfer_root / sub_id: freesurfer_path,
    }

    for link, src in links.items():
        if link.exists() or link.is_symlink():
            link.unlink()
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(src)
        print(f"Linked {link.name} for {sub_id}")

    # Link HTML reports into subject dir
    summary_htmls = list(xcp_d_base.glob(f"{sub_id}*.html"))
    for html_file in summary_htmls:
        dest = subject_target_dir / html_file.name
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        dest.symlink_to(html_file)
        print(f"Linked summary: {html_file.name} for {sub_id}")


