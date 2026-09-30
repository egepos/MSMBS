# Part I

Data and checkpoints from the filesender link go into `data/` and `models/`.

| File | What |
| --- | --- |
| `rsa_toolbox.py` | our toolbox from the practical: `compute_rdm`, `upper_triangle`, `compare_rdms`, `compare_to_many`, `plot_rdms` |
| `rdms.py` | step 1, RDMs of the brain, the untrained and trained models and yamnet |
| `compare.py` | step 2, every RDM against the brain RDM, with CIs and t-tests |
| `tsne.py` | step 3, t-SNE maps per layer |

## Step 1
```bash
python rdms.py              # euclidean distance
python rdms.py correlation  # 1 - pearson
```
Writes one `.npz` per model and run to `results/rdms/<metric>/`, one RDM per layer, keys are the layer
names from `extract_activations`:

| Model | Layers |
| --- | --- |
| waveform | `hidden_layers.0` .. `hidden_layers.4`, `classifier` |
| uninspired | `conv_layers.0` .. `conv_layers.2`, `fc_layers.0`, `fc_layers.1`, `classifier` |
| inspired | `conv_layers.0` .. `conv_layers.2`, `rnn`, `classifier` |

Untrained models are 5 random seeds, trained models are the 5 checkpoints in `models/`. Conv and GRU
activations are flattened to one vector per sound. All RDMs are 288 x 288 in `SantoroDataset` order,
grouped by category (animal, music, nature, speech, tools, voice, 48 sounds each).

What we saw here:
- The brain RDM has category blocks, but not the ones you would draw by hand: animal and music sit together,
  tools is far from everything. The trained conv models and yamnet have clean six-block structure, waveform
  has none.
- Euclidean and correlation distance tell different stories. Euclidean is driven by how strongly a sound
  activates everything (loud sounds are far from all others, in the brain too), correlation distance throws
  that away and most of the alignment goes with it. We keep both and say so in the report.

## Step 2
```bash
python compare.py                        # euclidean RDMs, pearson
python compare.py correlation spearman
```
Similarity to the brain is `compare_rdms(brain, rdm)`, Pearson or Spearman of the upper triangles, for
every model, condition, layer and run. Mean and 95% CI over the 5 runs (1.96 * SEM, same as
`util.mean_and_ci`), Welch t-tests between conditions and between models. Yamnet is one model, no CI.

Output in `results/`:
- `alignment_<metric>_<method>.csv`, all means and CIs
- `training_*.png`, untrained vs trained per layer
- `architecture_*.png`, each model at its best layer, yamnet's best layer as a line
- `depth_*.png`, r along the layers
- `rdms_*.png`, the brain RDM next to the best layer of each trained model and yamnet

What we found (euclidean, Pearson; the CIs are tight, ±0.01 to ±0.03):
- Nothing gets above r = 0.12, not even yamnet. One subject, noisy betas, so we compare models with each
  other and don't read much into the absolute numbers.
- Training only helps the conv layers of `inspired` (0.05 to 0.11). The layers above the convolutions
  (fc, rnn, classifier) actually get worse with training and end up at zero or slightly below. Learning
  50 ESC-50 classes pulls the top of the network away from STG. `waveform` never learned anything
  (6% accuracy) and sits below zero before and after.
- Going from raw waveform to a spectrogram is the big win. Adding the GRU on top is not: `inspired` vs
  `uninspired` at their best layers is 0.113 vs 0.101, p = 0.08, and the `rnn` layer itself is at zero.
- Depth looks the same in every model: best in the middle conv layers, zero at the classifier. Yamnet does
  the same thing, peaks at layer 7, goes negative at layers 11-12, embedding at zero. STG behaves like a
  mid-level acoustic stage, not like a category readout.
- With correlation RDMs and Spearman everything drops below 0.1 and the order shifts a bit (rnn and
  classifier slightly positive, conv slightly negative). The waveform < conv models ordering survives.

## Step 3
```bash
python tsne.py
```
t-SNE (PCA to 50 dims first, `init="pca"`, perplexity 30, seed 0) of every layer of every model, untrained
seed 0 and trained run 0, plus the brain betas and two yamnet layers, coloured by category. Each map also
gets the share of sounds whose nearest neighbour on the map is of the same category (chance 16%).

Output: `results/tsne_<model>.png`, `results/tsne_brain_yamnet.png`, `results/tsne_neighbours.csv`.

What we found:
- The brain map (49%) has one clear cluster, animal plus music, speech in the middle, the rest mixed.
  Same thing the brain RDM showed.
- Waveform is at chance on every layer, trained or not.
- In the conv models training sharpens conv 2 (59% uninspired, 65% inspired). `uninspired` loses the
  structure again at the classifier (41%), `inspired` keeps it to the end (61%).
- Yamnet separates the categories better than anything (79%), better than the brain itself, and still
  aligns with STG no better than our conv layers. Separating these six categories and matching STG are
  two different things, and this is the point t-SNE makes for the report: the layers that align best are
  the ones that are only partly categorical, like STG.
- One caveat. For the wide conv layers (up to 98k features) PCA + t-SNE show more category structure than
  the raw layer has: untrained conv 0/1 are at 25-39% in raw space and 51-59% on the map. In that many
  dimensions the nearest neighbour is mostly noise, PCA keeps the spectral shape. For the brain, yamnet and
  the narrow layers the map matches the raw space within a few points. So the numbers on the maps are
  numbers about the maps. Checked over all 5 runs in raw space, the training effect on conv 2 holds
  (uninspired 39% to 59%, inspired 44% to 56%, CI ±1-5).

## Adding a model

Add the class to `MODEL_CLASSES` in `core.py`, train it with `train.py` so the checkpoints land in
`models/<name>_run<k>_best.pt`, rerun the three scripts.
