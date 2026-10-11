"""Run the whole pipeline in order."""
# STEP 1: Run each script in turn
import runpy
from pathlib import Path

HERE = Path(__file__).parent
for script in ["get_targets.py", "download_layers.py", "overlay.py",
               "rank_subregions.py", "species_context.py", "make_maps.py"]:
    print(f"\n=== {script} ===")
    runpy.run_path(str(HERE / script), run_name="__main__")
