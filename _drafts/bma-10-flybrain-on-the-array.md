---
layout: single
title: "BMA360, Part 10: FlyBrain and the Array"
excerpt: "FlyBrain has host-side training and reference models, a couple of FPGA prototypes, and a new 121-microphone feature engine in RTL. None of it classifies BMA360 audio yet."
tags:
  - Hardware
  - FPGA
  - Machine Learning
  - BMA360
---

FlyBrain is a side research track that runs alongside the Bird Microphone Array. The host side has training tools and a CPU reference for small models. The FPGA side tries to turn some of those operations into small, predictable hardware. There is no FlyBrain bitstream classifying the array's audio, and this post covers how far each piece got.

## The model

It's loosely modeled on the insect mushroom body. An encoder expands a feature vector into a sparse set of Kenyon-cell (KC) activations, and a small readout maps those to class scores. The current FPGA core is all integer logic. One tested shape:

```text
input bits   64
KCs          256
fan-in       6
winners      K=16
```

Those are numbers I picked for the implementation; they aren't biological constants.

The host side holds the CPU reference models, tests, and training tools. A separate SageMaker pipeline trained encoders from ant-data Parquet files and exported model bundles with SHA-256 sidecars (that pipeline wasn't necessarily CPU-only). That's FlyBrain training on ant data, and there's no trained BMA bird detector. The Python reference gives the hardware a target: same input and weights, same result, in the specified number of cycles. The FPGA core currently only does inference. That's where the prototype stopped, and on-chip learning hasn't been ruled out.

## CPU reference and FPGA

```text
training data
     |
     v
host-side trainer and reference model ----> exported weights + hash
     |                                            |
     | golden vectors                             | load/test
     v                                            v
Python tests                              FPGA RTL / testbench
                                                   |
                                                   `-- not yet in BMA audio path
```

The host model defines what the circuit should compute. Any speed comparison has to hold inputs, weights, feature encoding, and decision rule fixed, or the faster number is just a different model.

There are two separate FPGA results, and neither ran on the BMA360:

```text
iCE40 HX1K, 256 KCs     sim 2,762/2,762 vectors match
                        HIL 3,386/3,387 vectors match (one mismatch, unexplained)
VU47P, newer core       722 inferences/s
                        training speedup at most ~1.2x
```

So the FPGA looks more useful for edge inference than for training. Neither number is a like-for-like CPU-versus-FPGA measurement on the array's workload.

## What's in the BMA tree

The BMA-specific FlyBrain RTL targets the mainboard Cyclone V. The Brooklyn-3 card's Zynq only handles Dante; ClearOne's audio processing lives on the Cyclone and OMAP.

The Cyclone prototype has two feature encoders, a thermometer-style v1 and a level-invariant v2. A `brain_slot` wrapper connects an encoder to the mushroom-body core, exposes a result register, and records a dropped start. When I went through the source tree, no top-level design instantiated `brain_slot`, and the `mb_core` source wasn't in that tree at all, so it has never been in a built BMA bitstream. Synthesis of the core by itself came to 405 ALUTs, 361 registers, and 4 M10K blocks. A full array image would cost more.

The newest piece is a shared engine that reads 121 microphone channels and computes eight magnitude bands, with tagged windows, gap handling, and output hold under backpressure. Five RTL tests pass, and a deliberate gap-handling mutation fails the expected comparison. All of that is against synthetic vectors. Routed timing, resource use, board operation, and features from real mics are all unchecked, and nothing yet carries those feature vectors into a trained FlyBrain model. The array's audio still goes through its existing hardware chain.

| Claim | Evidence so far | Still missing |
|---|---|---|
| Reference model and RTL agree on selected vectors | Bit-exact tests, synthetic RTL sims | Public pinned source and a runnable fixture |
| A small FlyBrain prototype runs in hardware | iCE40 HIL run, one mismatch | Explain the mismatching vector |
| The BMA can compute per-mic features in RTL | 121-channel eight-band block tests | Board load, routed timing/resources, real-audio comparison |
| FlyBrain classifies BMA audio | Nothing integrated | Feature-to-model adapter, weights trained on array data, end-to-end board test |

## A retracted result

I had an accuracy headline comparing the mushroom-body readout to another readout. It's retracted. On the documented 64-bit feature representation the MB head never beat a linear readout at any tested SNR, and a 5-nearest-neighbor baseline over two raw integer features did best. That's about this encoding and this evaluation; other mushroom-body models weren't tested.

If a linear head does as well on the same features, spending FPGA area on the fancier readout because it's bio-inspired makes no sense. Whatever goes on the Cyclone has to earn its place against those baselines.

## Next

On the model side: freeze a small dataset, split, encoding, weights, and hash; record CPU reference outputs including boundary cases; push the same vectors through the RTL and compare every output and cycle count; and keep the linear and 5-NN baselines on exactly the same examples.

On the array side: feed known microphone data through the Cyclone feature block on a board, save the eight-band outputs and tags, and compare them against a host implementation with the same window and gap rules. After that the features can be adapted to a FlyBrain input and scored with weights trained on array data. Synthesis resources, testbench correctness, and acoustic classification get reported separately.

The FlyBrain, training, and firmware repos are private right now, so none of this is clone-and-run yet. That needs a source release or sanitized snapshot, pinned tool versions, model and data provenance, and the golden vectors.