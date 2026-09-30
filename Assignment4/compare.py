import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind
from rsa_toolbox import compare_rdms, plot_rdms

METRIC = sys.argv[1] if len(sys.argv) > 1 else "euclidean"
METHOD = sys.argv[2] if len(sys.argv) > 2 else "pearson"
RDMS = Path("results/rdms") / METRIC
MODELS = ["waveform", "uninspired", "inspired"]
N_RUNS = 5
TAG = f"{METRIC}_{METHOD}"

brain = np.load(RDMS / "brain.npz")["stg"]

rows = []
for model in MODELS:
    for condition in ("untrained", "trained"):
        for run in range(N_RUNS):
            rdms = np.load(RDMS / f"{model}_{condition}_run{run}.npz")
            for depth, layer in enumerate(rdms.files):
                rows.append((model, condition, run, depth, layer, compare_rdms(brain, rdms[layer], METHOD)))
yamnet = np.load(RDMS / "yamnet.npz")
for depth, layer in enumerate(yamnet.files):
    rows.append(("yamnet", "pretrained", 0, depth, layer, compare_rdms(brain, yamnet[layer], METHOD)))
table = pd.DataFrame(rows, columns=["model", "condition", "run", "depth", "layer", "r"])

# 95% CI = 1.96 * SEM over the runs, like util.mean_and_ci
summary = table.groupby(["model", "condition", "depth", "layer"])["r"].agg(["mean", "sem"]).reset_index()
summary["ci"] = 1.96 * summary["sem"].fillna(0)
summary.to_csv(f"results/alignment_{TAG}.csv", index=False)


def runs(model, condition, layer):
    t = table
    return t[(t.model == model) & (t.condition == condition) & (t.layer == layer)]["r"].to_numpy()


def stats(model, condition):
    return summary[(summary.model == model) & (summary.condition == condition)]


def best(model, condition):
    s = stats(model, condition)
    return s.loc[s["mean"].idxmax()]


def welch(a, b):
    return ttest_ind(a, b, equal_var=False).pvalue


print(f"{METRIC} RDMs, {METHOD} correlation with the brain\n")

# training: untrained vs trained, layer by layer
print("training (untrained -> trained, p from Welch t-test over the runs)")
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, model in zip(axes, MODELS):
    u, t = stats(model, "untrained"), stats(model, "trained")
    for layer, r_u, r_t in zip(u["layer"], u["mean"], t["mean"]):
        p = welch(runs(model, "trained", layer), runs(model, "untrained", layer))
        print(f"   {model:11s} {layer:16s} {r_u:7.3f} -> {r_t:7.3f}   p = {p:.3f}")
    x = np.arange(len(u))
    ax.bar(x - 0.2, u["mean"], 0.4, yerr=u["ci"], label="untrained", capsize=3)
    ax.bar(x + 0.2, t["mean"], 0.4, yerr=t["ci"], label="trained", capsize=3)
    ax.axhline(0, color="black", lw=0.5)
    ax.set_xticks(x, u["layer"], rotation=45, ha="right", fontsize=8)
    ax.set_title(model)
    ax.set_ylabel(f"{METHOD} r with brain")
    ax.legend()
fig.suptitle(f"Effect of training ({METRIC} RDMs)")
fig.tight_layout()
fig.savefig(f"results/training_{TAG}.png", dpi=150)

# architecture: every model at its best layer
print("\narchitecture (best layer per model, p from Welch t-test between trained models)")
peaks = []
for model in MODELS:
    for condition in ("untrained", "trained"):
        b = best(model, condition)
        peaks.append((model, condition, b["layer"], b["mean"], b["ci"]))
        print(f"   {model:11s} {condition:10s} {b['layer']:16s} {b['mean']:.3f} ± {b['ci']:.3f}")
peaks = pd.DataFrame(peaks, columns=["model", "condition", "layer", "mean", "ci"])
y = best("yamnet", "pretrained")
print(f"   {'yamnet':11s} {'pretrained':10s} {y['layer']:16s} {y['mean']:.3f}")
for m1, m2 in [("waveform", "uninspired"), ("uninspired", "inspired"), ("waveform", "inspired")]:
    p = welch(runs(m1, "trained", best(m1, "trained")["layer"]), runs(m2, "trained", best(m2, "trained")["layer"]))
    print(f"   {m1} vs {m2} (trained): p = {p:.3f}")

fig, ax = plt.subplots(figsize=(7, 4))
x = np.arange(len(MODELS))
for offset, condition in [(-0.2, "untrained"), (0.2, "trained")]:
    p = peaks[peaks.condition == condition]
    ax.bar(x + offset, p["mean"], 0.4, yerr=p["ci"], label=condition, capsize=3)
ax.axhline(y["mean"], color="gray", ls="--", label=f"yamnet {y['layer']}")
ax.axhline(0, color="black", lw=0.5)
labels = [f"{m}\n{best(m, 'untrained')['layer']} / {best(m, 'trained')['layer']}" for m in MODELS]
ax.set_xticks(x, labels, fontsize=8)
ax.set_ylabel(f"{METHOD} r with brain (best layer)")
ax.set_title(f"Effect of architecture ({METRIC} RDMs)")
ax.legend()
fig.tight_layout()
fig.savefig(f"results/architecture_{TAG}.png", dpi=150)

# depth: r along the layers of each model
print("\ndepth: see the figure")
fig, (ax_models, ax_yamnet) = plt.subplots(1, 2, figsize=(13, 4), width_ratios=[2, 1])
for model, color in zip(MODELS, ["tab:blue", "tab:orange", "tab:green"]):
    for condition, ls in [("untrained", "--"), ("trained", "-")]:
        s = stats(model, condition)
        ax_models.errorbar(s["depth"], s["mean"], yerr=s["ci"], color=color, ls=ls, marker="o", capsize=3,
                           label=f"{model} {condition}")
ax_models.axhline(0, color="black", lw=0.5)
ax_models.set_xlabel("layer index (0 = first layer, last = classifier)")
ax_models.set_ylabel(f"{METHOD} r with brain")
ax_models.set_title("our models")
ax_models.legend(fontsize=8)
s = stats("yamnet", "pretrained")
ax_yamnet.plot(s["depth"], s["mean"], marker="o", color="gray")
ax_yamnet.axhline(0, color="black", lw=0.5)
ax_yamnet.set_xticks(s["depth"], [l.replace("layer", "L").replace("relu", "") for l in s["layer"]], rotation=45, fontsize=7)
ax_yamnet.set_title("yamnet (1 model, no CI)")
fig.suptitle(f"Alignment across depth ({METRIC} RDMs)")
fig.tight_layout()
fig.savefig(f"results/depth_{TAG}.png", dpi=150)

# the brain RDM next to the best layer of each trained model (run 0) and of yamnet
show = {"brain (STG)": brain}
for model in MODELS:
    layer = best(model, "trained")["layer"]
    show[f"{model} trained\n{layer}"] = np.load(RDMS / f"{model}_trained_run0.npz")[layer]
show[f"yamnet\n{y['layer']}"] = yamnet[y["layer"]]
plot_rdms(show).savefig(f"results/rdms_{TAG}.png", dpi=150)
