from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.neighbors import NearestNeighbors
from torch.utils.data import DataLoader

import config
from core import MODEL_CLASSES, SantoroDataset, extract_activations, load_yamnet_activations

OUT = Path("results")
dataset = SantoroDataset()
loader = DataLoader(dataset, batch_size=32)
# the csv labels are objects (bird, man, rain), the 6 categories only sit in the file names: s2_animal_7.wav
categories = np.array([f.split("_")[1] for f in dataset.filenames])
names = sorted(set(categories))
colors = dict(zip(names, plt.cm.tab10.colors))
scores = []


def embed(activations):
    # PCA to 50 dims first, as sklearn recommends for wide inputs
    x = np.asarray(activations, dtype=np.float64).reshape(len(activations), -1)
    if x.shape[1] > 50:
        x = PCA(n_components=50, random_state=0).fit_transform(x)
    return TSNE(n_components=2, init="pca", perplexity=30, random_state=0).fit_transform(x)


def scatter(ax, activations, title):
    points = embed(activations)
    for name in names:
        m = categories == name
        ax.scatter(points[m, 0], points[m, 1], s=8, color=colors[name], label=name)
    # how often the nearest neighbour on the map has the same category, chance = 47/287 = 16%
    neighbour = NearestNeighbors(n_neighbors=2).fit(points).kneighbors(points, return_distance=False)[:, 1]
    s = (categories[neighbour] == categories).mean()
    scores.append((title, s))
    ax.set_title(f"{title}\nsame-category neighbour {s:.0%}", fontsize=9)
    ax.set_xticks([])
    ax.set_yticks([])


# brain and yamnet
yamnet = load_yamnet_activations()
systems = {
    "brain (STG betas)": dataset.brain_responses.numpy(),
    "yamnet layer07relu": yamnet["layer07relu"],
    "yamnet embedding": yamnet["embedding"],
}
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
for ax, (title, act) in zip(axes, systems.items()):
    scatter(ax, act, title)
axes[-1].legend(fontsize=7, markerscale=2, loc="upper left", bbox_to_anchor=(1, 1))
fig.tight_layout()
fig.savefig(OUT / "tsne_brain_yamnet.png", dpi=150)

# our models: untrained (seed 0) on top, trained (run 0) below, one column per layer
for name, Model in MODEL_CLASSES.items():
    torch.manual_seed(0)
    untrained = Model(num_classes=config.NUM_CLASSES)
    trained = Model(num_classes=config.NUM_CLASSES)
    trained.load_state_dict(torch.load(f"models/{name}_run0_best.pt"))

    acts = {"untrained": extract_activations(loader, untrained), "trained": extract_activations(loader, trained)}
    layers = list(acts["trained"])
    fig, axes = plt.subplots(2, len(layers), figsize=(3 * len(layers), 6.5))
    for row, condition in zip(axes, acts):
        for ax, layer in zip(row, layers):
            print(name, condition, layer)
            scatter(ax, acts[condition][layer], f"{name} {condition} {layer}")
    axes[0, -1].legend(fontsize=7, markerscale=2, loc="upper left", bbox_to_anchor=(1, 1))
    fig.suptitle(f"{name}: t-SNE per layer, coloured by category")
    fig.tight_layout()
    fig.savefig(OUT / f"tsne_{name}.png", dpi=150)

scores = pd.DataFrame(scores, columns=["system", "same_category_neighbour"])
scores.to_csv(OUT / "tsne_neighbours.csv", index=False)
print(scores.to_string(index=False))
