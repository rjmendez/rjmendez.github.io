---
layout: single
title: "BMA360, Part 10: FlyBrain and the Array"
header:
  og_image: bma/og/bma360-part-10.png
excerpt: "FlyBrain's host-side reference models, two FPGA prototypes, a Cyclone wrapper, and a 121-microphone feature engine in RTL, plus an accuracy headline I retracted."
tags:
  - Hardware
  - FPGA
  - Machine Learning
  - BMA360
---

FlyBrain is a side project that runs alongside the array: small classifiers modeled on the insect mushroom body, with a CPU reference on the host and integer RTL for FPGAs. The goal is to hang one off the BMA360's Cyclone and classify what the mics hear.

## The model

An encoder expands a feature vector into a sparse set of Kenyon-cell (KC) activations, and a small readout maps those to class scores. The FPGA core is all integer logic. One tested shape:

![Mushroom-body core: 64 input bits feed 256 Kenyon cells with fan-in 6, a k-winners-take-all keeps 16, an int8 readout gives 3 class scores, and argmax picks one.](/images/bma/p10-mb-model-light.svg){: .only-light}
![Mushroom-body core: 64 input bits feed 256 Kenyon cells with fan-in 6, a k-winners-take-all keeps 16, an int8 readout gives 3 class scores, and argmax picks one.](/images/bma/p10-mb-model-dark.svg){: .only-dark}

The host side has the Python reference, tests, and training tools. A SageMaker pipeline trained encoders from ant-data Parquet files and exported model bundles with SHA-256 sidecars. The reference sets the contract for the RTL, and the FPGA core does inference only for now.

![Flow: training data to host trainer and reference, exported weights with a SHA-256 sidecar, golden vectors into Python tests and the FPGA testbench, with the BMA audio path as the next step.](/images/bma/p10-flow-light.svg){: .only-light}
![Flow: training data to host trainer and reference, exported weights with a SHA-256 sidecar, golden vectors into Python tests and the FPGA testbench, with the BMA audio path as the next step.](/images/bma/p10-flow-dark.svg){: .only-dark}

## Two FPGA prototypes

![iCE40 HX1K results: RTL simulation matches 2,762 of 2,762 vectors; hardware in the loop matches 3,386 of 3,387 with one timeout and no wrong answers.](/images/bma/p10-hil-match-light.svg){: .only-light}
![iCE40 HX1K results: RTL simulation matches 2,762 of 2,762 vectors; hardware in the loop matches 3,386 of 3,387 with one timeout and no wrong answers.](/images/bma/p10-hil-match-dark.svg){: .only-dark}

I still owe the iCE40 an explanation for that one timeout. A newer core on a VU47P ran 722 inferences/s, and training sped up by at most ~1.2x, so edge inference looks like the useful job for the FPGA. Neither board is the BMA360.

## On the Cyclone

The BMA-specific RTL targets the mainboard Cyclone V, where ClearOne does its audio processing alongside the OMAP. The Zynq on the Brooklyn-3 card only does Dante.

There are two feature encoders, a thermometer-style v1 and a level-invariant v2. A `brain_slot` wrapper connects an encoder to the mushroom-body core, exposes a result register, and flags a dropped start. Nothing in the tree instantiates `brain_slot` yet, and `mb_core` isn't in that tree, so there's no BMA bitstream with it.

The newest piece is a shared engine that reads all 121 mic channels and computes eight magnitude bands:

![Cyclone feature engine: 121 mic channels, tagged windows with gap handling, 8 magnitude bands per channel, an output register that holds under backpressure, then a FlyBrain adapter and MB core that are not built yet.](/images/bma/p10-feature-engine-light.svg){: .only-light}
![Cyclone feature engine: 121 mic channels, tagged windows with gap handling, 8 magnitude bands per channel, an output register that holds under backpressure, then a FlyBrain adapter and MB core that are not built yet.](/images/bma/p10-feature-engine-dark.svg){: .only-dark}

It passes five RTL tests on synthetic vectors, and mutating the gap handling breaks the expected comparison. Next for it: routing, a board load, and a comparison against a host implementation on real mic data. After that comes an adapter from those bands into a FlyBrain input.

## A retracted result

I had an accuracy headline for the mushroom-body readout. I retracted it. These are the numbers underneath, from host simulation on synthetic audio:

![Accuracy versus SNR from +12 to -6 dB: a 5-nearest-neighbor on two raw integers scores highest, a linear head next, the MB head with v2 features below both at every SNR, and the v1 MB head lowest.](/images/bma/p10-accuracy-snr-light.svg){: .only-light}
![Accuracy versus SNR from +12 to -6 dB: a 5-nearest-neighbor on two raw integers scores highest, a linear head next, the MB head with v2 features below both at every SNR, and the v1 MB head lowest.](/images/bma/p10-accuracy-snr-dark.svg){: .only-dark}

On the documented 64-bit features the MB head never beat a plain linear readout, and a 5-NN over two raw integer features beat both. If a linear head matches it on the same features, the linear head gets the FPGA area.

## Next

Model side: freeze a dataset, split, encoding, weights, and hash; record reference outputs including edge cases; run the same vectors through the RTL and diff every output and cycle count, with the linear and 5-NN baselines on the same examples.

Array side: push known mic data through the Cyclone feature block on a board, save the bands and tags, diff against the host version, then train weights on array data and score them.

The FlyBrain, training, and firmware repos are private for now. A public version needs a sanitized snapshot, pinned tool versions, data provenance, and the golden vectors.