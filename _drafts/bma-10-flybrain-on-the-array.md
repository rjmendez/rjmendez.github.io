---
layout: single
title: "BMA360, Part 10: What FlyBrain Does—and Does Not—Run on the Array"
excerpt: "FlyBrain has host-side training and reference models, FPGA prototypes, and a new 121-microphone feature-engine experiment. None is yet a FlyBrain classifier running in the BMA360 audio path."
tags:
  - Hardware
  - FPGA
  - Machine Learning
  - BMA360
---

FlyBrain is a parallel research track, not a feature already running in the Bird Microphone Array. The host-side work supplies training tools and a CPU reference for small models. FPGA work asks whether selected operations can become compact, predictable hardware. The connection to the BMA360 is still an experiment: there is no integrated FlyBrain bitstream classifying the array's audio.

That distinction matters because there are two very different stories here. One is about learning and testing a small model. The other is about connecting a real 121-microphone signal path to that model on a specific board. The first has useful results. The second is not finished.

## What the model is

The design is inspired by the insect mushroom-body circuit: an input encoder expands a feature vector into a sparse set of Kenyon-cell (KC) activations; a small readout maps those activations to class scores. The current FPGA core is integer logic, with no floating-point datapath. One tested shape uses 64 input bits, 256 KCs, fan-in 6, and 16 winners (`K=16`). Those are implementation parameters, not biological constants.

The host side is where the CPU reference models, tests, and training tools live. A separate SageMaker pipeline has trained encoders from ant-data Parquet files and exported model bundles with SHA-256 sidecars; that pipeline is not necessarily a CPU-only training run. It is FlyBrain training, not a trained BMA bird detector. The Python reference is valuable because it gives the hardware a target: for the same input and weights, the RTL should produce the same result and take the specified number of cycles.

The learning goal is small-model design and biological inspiration, not a claim that a biologically inspired circuit must beat ordinary classifiers. The present FPGA core performs inference; that is a property of the prototype and its test path, not a rule that FlyBrain can never learn or adapt on chip.

## CPU reference and FPGA are different jobs

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

The host model is not just a slow substitute for hardware. It is the reference implementation used to define what the circuit should compute. A useful hardware comparison holds the inputs, weights, feature encoding, and decision rule constant. Otherwise, a faster FPGA number may describe a different model rather than an acceleration.

There are several FPGA results, and they should not be collapsed into one BMA milestone. A small iCE40 HX1K prototype with 256 KCs matched 2,762 of 2,762 simulation vectors, then 3,386 of 3,387 hardware-in-the-loop vectors. The one HIL mismatch remains a mismatch; it is not an exact pass. A separate modern core measured 722 inferences per second on a VU47P. In that setup, training speed improved by at most about 1.2 times, so the FPGA result is more interesting as an edge-inference experiment than as a training accelerator. Neither result is a run on the BMA360's processors, and neither is an apples-to-apples CPU-versus-FPGA measurement for the array workload.

## What is actually in the BMA work

The BMA-specific FlyBrain RTL is on the mainboard Cyclone V side, not in the Brooklyn-3 card's Zynq programmable logic. The Zynq is the Dante interface; it is not the FPGA where ClearOne's mainboard audio processing lives.

The Cyclone-side prototype includes two feature encoders: a thermometer-style v1 and a level-invariant v2. A `brain_slot` wrapper connects an encoder to the mushroom-body core, exposes a result register, and records a dropped start. In the source-tree inspection, no top-level design instantiated `brain_slot`, and the `mb_core` source was not included in that tree. The wrapper was therefore not part of a built BMA bitstream. A synthesis figure for the core alone—405 ALUTs, 361 registers, and four M10K blocks—is not the resource use of a complete, integrated array image.

The newest BMA-facing experiment is a different block: a shared engine that reads 121 microphone channels and computes eight magnitude bands, with tagged windows, gap handling, and output hold under backpressure. Five focused RTL tests passed, and a deliberate gap-handling mutation failed the expected comparison. That establishes behavior against synthetic test vectors. It does not establish routed timing, FPGA resource use, operation on the board, or correct features from real microphones. There is not yet an adapter carrying those feature vectors into a trained FlyBrain model.

The actual array path still runs through its existing hardware audio chain. Neither the host-side Python model nor the experimental feature engine has replaced that path. The evidence ladder is therefore:

| Claim | Evidence so far | Still missing |
|---|---|---|
| The reference model and RTL agree on selected vectors | Bit-exact tests and synthetic RTL simulations | Public, pinned source and a complete reader-runnable fixture |
| A small FlyBrain prototype can run in hardware | A separate iCE40 HIL run, with one mismatch | Explain or resolve the mismatching vector |
| The BMA can compute per-microphone features in RTL | 121-channel, eight-band block tests | Board load, routed timing/resources, real-audio comparison |
| FlyBrain classifies BMA audio | No integrated result | Feature-to-model adapter, weights trained for array data, and an end-to-end board test |

## The result that should not be advertised

An older accuracy headline comparing the mushroom-body model with another readout has been retracted. On the documented 64-bit feature representation, the MB head did not beat a linear readout at any tested SNR; a 5-nearest-neighbor baseline over two raw integer features performed best in that comparison. That is a useful result about this encoding and evaluation—not a verdict on all mushroom-body models.

It also changes the engineering question. If a linear head performs as well or better on the same features, there is no reason to spend FPGA area reproducing the more complicated readout just because it is biologically inspired. The point of the experiment is to find out which parts are useful, not to protect a preferred answer.

## How to reproduce the next meaningful result

First freeze a small dataset and its split, feature encoding, model weights, and hash. Record the CPU reference outputs for boundary cases as well as ordinary inputs. Then run the same vectors through the RTL and compare every defined output and cycle count—not just the final accuracy. Keep the linear and nearest-neighbor baselines on exactly the same examples and features.

For the BMA feature engine, the next gate is a board capture: feed known microphone data through the Cyclone block, save its eight-band outputs and tags, and compare them with a host implementation of the same window and gap rules. Only after that should those features be adapted to a FlyBrain input shape and scored with weights trained for the array data. Report synthesis resources and routed timing separately from testbench correctness; report acoustic classification separately from both.

There is a publication limitation: the relevant FlyBrain, training, and firmware repositories are private at the time of writing. This post records the evidence and the reproduction gates, but it is not yet a public clone-and-run package. A reader-facing reproduction requires a source release or sanitized snapshot, pinned tool versions, model/data provenance, and the golden vectors.

The honest conclusion is modest. The host work gives the FPGA experiments a reference and a training path. The FPGA work has produced testable model blocks and a new array-feature engine. The BMA360 has not yet run those pieces as an integrated acoustic classifier. That is a concrete next experiment—not a result to write as if it has already happened.
