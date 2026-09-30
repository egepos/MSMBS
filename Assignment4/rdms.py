"""python rdms.py [euclidean|correlation]"""

import sys
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

import config
from core import MODEL_CLASSES, SantoroDataset, extract_activations, load_yamnet_activations
from rsa_toolbox import compare_rdms, compute_rdm

METRIC = sys.argv[1] if len(sys.argv) > 1 else "euclidean"
N_RUNS = 5
OUT = Path("results/rdms") / METRIC
OUT.mkdir(parents=True, exist_ok=True)

dataset = SantoroDataset()
loader = DataLoader(dataset, batch_size=32)


def model_rdms(model):
    # conv / GRU activations are flattened to one vector per sound
    activations = extract_activations(loader, model)
    return {layer: compute_rdm(act.reshape(len(act), -1).numpy(), METRIC) for layer, act in activations.items()}


def report(title, rdms):
    print(title)
    for layer, rdm in rdms.items():
        print(f"    {layer:16s} mean dist {rdm.mean():8.3f}   r with brain {compare_rdms(brain_rdm, rdm):6.3f}")


# brain
brain_rdm = compute_rdm(dataset.brain_responses.numpy(), METRIC)
np.savez(OUT / "brain.npz", stg=brain_rdm)
print(f"brain (STG)  {brain_rdm.shape}  mean dist {brain_rdm.mean():.3f}")

# untrained models, one per seed
for name, Model in MODEL_CLASSES.items():
    for run in range(N_RUNS):
        torch.manual_seed(run)
        rdms = model_rdms(Model(num_classes=config.NUM_CLASSES))
        np.savez(OUT / f"{name}_untrained_run{run}.npz", **rdms)
        report(f"{name} untrained run {run}", rdms)

# trained models, the checkpoints in models/
for name, Model in MODEL_CLASSES.items():
    for run in range(N_RUNS):
        model = Model(num_classes=config.NUM_CLASSES)
        model.load_state_dict(torch.load(f"models/{name}_run{run}_best.pt"))
        rdms = model_rdms(model)
        np.savez(OUT / f"{name}_trained_run{run}.npz", **rdms)
        report(f"{name} trained run {run}", rdms)

# yamnet
yamnet_rdms = {layer: compute_rdm(act, METRIC) for layer, act in load_yamnet_activations().items()}
np.savez(OUT / "yamnet.npz", **yamnet_rdms)
report("yamnet", yamnet_rdms)
