# Comments in English only
import plotly.graph_objects as go
from atp_handler import ATPHandler
import glob, os

# --- user config ---
tpbigG_path = r"C:/ATP/ATP/GNUATP"             # folder containing tpbigG.exe
pl42mat_path = r"C:/ATP/Pl42mat09/Pl42mat.exe" # full path to Pl42mat.exe
atp_file = r"C:/Users/angel/Desktop/capacitor_bank_unbalance_models/dupla-estrela-isolada-2.atp"

# --- run simulation ---
handler = ATPHandler(tpbigG_path, pl42mat_path)
df = handler.run_simulation(atp_file)

# --- pick time and current columns ---
time_col = next((c for c in df.columns if c.lower().startswith("t")), df.columns[0])
current_cols = [c for c in df.columns if c.lower().startswith("i")]
[os.remove(f) for e in ("*.bin","*.dbg","*.tmp") for f in glob.glob(e)]

# --- build plot ---
fig = go.Figure()
for c in current_cols:
    fig.add_trace(go.Scatter(x=df[time_col], y=df[c], mode="lines", name=c))

fig.update_layout(
    title="ATP currents (dupla-estrela-isolada-2)",
    xaxis_title="Time [s]",
    yaxis_title="Current [A]",
    template="plotly_white",
    height=600,
    width=1200
)

fig.show()  # interactive window (if supported)
fig.write_html("resultado.html", auto_open=True)  # opens in browser as fallback

print("Columns:", list(df.columns))
print(f"Plotted {len(current_cols)} current signals.")
print(f"Time column used: {time_col}")
print("Columns in DataFrame:", list(df.columns))
