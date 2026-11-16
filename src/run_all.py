"""Run the whole pipeline in order. Works from any folder:  python src/run_all.py"""
# STEP 1: Imports (this file's folder is added to the path, so it runs from the repo root too)
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import download_layers  # noqa: E402
import get_targets  # noqa: E402
import make_maps  # noqa: E402
import overlay  # noqa: E402
import rank_subregions  # noqa: E402
import species_context  # noqa: E402
import stewardship_check  # noqa: E402
from utils import PipelineError, get_logger  # noqa: E402

log = get_logger("run_all")

STEPS = {
    "targets": ("BioNet facts for the target PCTs", get_targets.main),
    "download": ("Download IBRA, CAPAD and SVTM layers", download_layers.main),
    "overlay": ("Overlay vegetation, subregions and protected areas", overlay.main),
    "rank": ("Score and rank subregions", rank_subregions.main),
    "species": ("Threatened species counts (BioNet)", species_context.main),
    "maps": ("Map series", make_maps.main),
    "stewardship": ("Reality check against stewardship sites", stewardship_check.main),
}


# STEP 2: Run each step, stop with a clear message if one fails
def main(only: list[str] | None = None) -> int:
    start = time.time()
    chosen = only or list(STEPS)
    for number, key in enumerate(chosen, 1):
        name, step = STEPS[key]
        log.info("[%d/%d] %s", number, len(chosen), name)
        try:
            step()
        except PipelineError as exc:
            log.error("Pipeline stopped at '%s':\n%s", name, exc)
            return 1
    log.info("Done in %.0f seconds.", time.time() - start)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="+", choices=list(STEPS),
                        help="run just these steps, e.g. --only rank maps")
    sys.exit(main(parser.parse_args().only))
