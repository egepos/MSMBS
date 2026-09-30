import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr, spearmanr


def compute_rdm(patterns, metric="euclidean"):
    patterns = np.asarray(patterns, dtype=np.float64)
    if metric == "euclidean":
        # ||a-b||^2 = |a|^2 + |b|^2 - 2ab, the vectorized version of the double loop
        sq = (patterns ** 2).sum(axis=1)
        rdm = np.sqrt(np.clip(sq[:, None] + sq[None, :] - 2 * patterns @ patterns.T, 0, None))
    elif metric == "correlation":
        rdm = 1 - np.corrcoef(patterns)
    else:
        raise ValueError(metric)
    np.fill_diagonal(rdm, 0)
    return rdm


def upper_triangle(rdm):
    i, j = np.triu_indices(len(rdm), k=1)
    return rdm[i, j]


def compare_rdms(rdm_a, rdm_b, method="pearson"):
    a, b = upper_triangle(rdm_a), upper_triangle(rdm_b)
    if method == "pearson":
        return pearsonr(a, b)[0]
    if method == "spearman":
        return spearmanr(a, b)[0]
    raise ValueError(method)


def compare_to_many(reference_rdm, candidate_rdms, method="pearson"):
    scores = [(name, compare_rdms(reference_rdm, rdm, method)) for name, rdm in candidate_rdms.items()]
    return sorted(scores, key=lambda s: s[1], reverse=True)


def plot_rdms(rdms, size=3.5):
    fig, axes = plt.subplots(1, len(rdms), figsize=(size * len(rdms), size + 0.6))
    for ax, (title, rdm) in zip(axes, rdms.items()):
        ax.imshow(rdm, cmap="viridis")
        ax.set_title(title, fontsize=9)
        ax.axis("off")
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    data = np.load("practical/data/rsa_individual_test_data.npz")
    brain = compute_rdm(data["brain"])
    models = {name: compute_rdm(data[name]) for name in ("model_good", "model_bad")}
    print(compare_to_many(brain, models))
