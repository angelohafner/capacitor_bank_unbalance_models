# Comments in English only
import os
import glob
import shutil
import subprocess
import scipy.io as sio
import pandas as pd
import numpy as np


class ATPHandler:
    def __init__(self, tpbigG_path, pl42mat_path):
        self.tpbigG_path = tpbigG_path              # folder containing tpbigG.exe and STARTUP
        self.pl42mat_path = pl42mat_path            # full path to Pl42mat.exe

    def _ensure_startup_in_deck_folder(self, atp_dir):
        """Copy STARTUP from tpbigG folder to the .atp folder if missing."""
        src = os.path.join(self.tpbigG_path, "STARTUP")
        dst = os.path.join(atp_dir, "STARTUP")
        if not os.path.exists(dst) and os.path.exists(src):
            shutil.copy2(src, dst)

    def run_simulation(self, atp_file):
        """
        Run ATP (tpbigG.exe) and convert PL4->MAT using Pl42mat.
        Returns a pandas DataFrame with all variables.
        """
        atp_file = os.path.abspath(atp_file)
        atp_dir = os.path.dirname(atp_file)

        # Ensure STARTUP is available where ATP will run
        self._ensure_startup_in_deck_folder(atp_dir)

        # 1) Run ATP in the .atp folder
        tpbigg = os.path.join(self.tpbigG_path, "tpbigG.exe")
        subprocess.run([tpbigg, atp_file], cwd=atp_dir, check=False)

        # 2) Pick newest .pl4 in the folder
        pl4_candidates = glob.glob(os.path.join(atp_dir, "*.pl4")) + glob.glob(os.path.join(atp_dir, "*.PL4"))
        if not pl4_candidates:
            raise FileNotFoundError("No .pl4 file found after running ATP.")
        pl4_file = max(pl4_candidates, key=os.path.getmtime)

        # 3) Convert PL4 -> MAT (same folder)
        subprocess.run([self.pl42mat_path, pl4_file], cwd=atp_dir, check=False)

        # 4) Pick newest .mat
        mat_candidates = glob.glob(os.path.join(atp_dir, "*.mat")) + glob.glob(os.path.join(atp_dir, "*.MAT"))
        if not mat_candidates:
            raise FileNotFoundError("No .mat file found after running Pl42mat.")
        mat_file = max(mat_candidates, key=os.path.getmtime)

        # 5) Load MAT -> DataFrame
        mat = sio.loadmat(mat_file)
        data = {k: np.ravel(v) for k, v in mat.items() if not k.startswith("__")}
        df = pd.DataFrame(data)

        # 6) Move time column first if present
        for tcol in ["t", "time", "Time", "TIME"]:
            if tcol in df.columns:
                df = df[[tcol] + [c for c in df.columns if c != tcol]]
                break

        return df
