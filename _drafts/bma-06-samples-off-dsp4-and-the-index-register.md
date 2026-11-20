---
layout: single
title: "BMA360, Part 6: Samples Off DSP4, and an Index Register That Lied"
excerpt: "One pointer in data memory names the buffer the DSP just filled. Copy it, and you have a frame of real microphone audio. Form a beam from that same snapshot and it is bit-exact — but only as a mechanism, not a direction. Then a word-versus-byte addressing bug made my first egress read 42 of 48 words wrong while swearing it was fine."
tags:
  - Hardware
  - SHARC
  - DSP
  - Reverse Engineering
  - BMA360
---

Part 5 got my code running inside DSP4's interrupt. This part is the first real microphone audio out of the chip — and a long, instructive fight with an addressing bug that produced confidently wrong numbers. This is where it's easy to overclaim, so I'll mark proven versus not as I go.

The receive ring
======

DSP4 takes microphone audio on serial port 0 (SPORT0), 24-bit words, and the ISR drops each frame into one of three buffers arranged as a ring. A single pointer in data memory always holds the address of the buffer currently in use:

```
DATA MEMORY
  0x256dc4  -> pointer: current buffer  (always one of the three below)
  0x256dc8  buffer A \
  0x257068  buffer B  > 3-buffer descriptor ring, frame = 21 words = 0x54 bytes
  0x257308  buffer C /

FRAME LAYOUT (21 words/slot-set)
  slot 0..3  mic audio        slot 5,6  mic audio
  slot 4     NON-mic (sparse spikes, not a microphone)
  slot 7..18 zero (unused in stock config)
  slot 19    sync  0xff00
  slot 20    sync  0x123456
```

![DSP4's receive ring: one pointer in data memory names the buffer the ISR just filled, cycling through three buffers; each 21-word frame carries mic audio, zeros, and two constant sync witnesses (0xff00, 0x123456) that give the read a built-in alignment check. Measured, read-only, on one array.](/images/BMA360_dsp4_receive_ring.svg)

The sync words are the gift. Slots 19 and 20 carry constant witnesses (`ff00`, `123456`) in every single frame, so any read that does not land those two constants in the right place is misaligned — you get an alignment check for free, built into the data. The ISR advances the frame counter about 6000 times a second, and the pointer at `0x256dc4` is never anything but one of the three buffer addresses. That is a clean, self-checking place to read from.

A frame of real audio
======

Reading the pointer, then copying the buffer it names, gives a frame of actual microphone noise floor — the active slots sit around −61 to −86 dBFS and wander the way a live acoustic floor does, while the zero slots stay zero and the sync slots stay constant. That is the first microphone audio I pulled off the array through my own path rather than the vendor's meters.

The sync witnesses passed 24 of 24 frames, so the read was aligned. This is a measured, read-only result on one array.

The beam that is only a mechanism
======

The tempting next step: form a beam. On a single captured snapshot, owner code copied the pointer-named block and summed it into a beam, and the result was **bit-exact** against the reference computation on that same snapshot — in memory, with no live audio egress involved.

What this proves, and what it doesn't:

> It proves the **mechanism**: I can read the right memory, copy the right block, and run the beam arithmetic to a bit-exact result on a snapshot. It proves **nothing** about direction, beam quality, DOA, or acoustic-camera tracking. There is no steering claim here. One snapshot, in memory, bit-exact arithmetic — that is the entire claim.

The per-slot levels from that window were `0:-67 1:-65 2:-71 3:-72 5:-78 6:-79` dBFS. Real numbers, real mechanism, zero directional meaning.

The index register that lied
======

Now the bug — the useful part if you're reproducing this. To make egress efficient I wanted the copy loop to use the SHARC's indexed addressing — load through an index register `I4` with a displacement — instead of absolute addresses. My first egress probe reported success: it installed, it ran one armed pass, miss count zero. Then I compared the index-addressed copy against the absolute-addressed copy word for word.

**42 of the 48 compared words were different.** (The other 6 matched by chance — they were zero in both.) The probe had told me "pass" while reading the wrong memory, because "pass" only meant "the pass completed," not "the bytes are right." Two confident lies: the tool's own status, and my mental model of the addressing.

The root cause is a units mismatch in how the SHARC forms addresses, and it is a genuine trap:

```
SHARC address arithmetic -- the trap
  DM(disp, I4)     indexed load  : effective addr = I4 + 4*disp     (disp is in WORDS)
  MODIFY <imm>     immediate      : pointer      += imm             (imm is in BYTES)

  same intent, two different units. Mix them and every indexed
  access is off by a factor of four -- which is what 42/48-wrong looks like.
```

The measured pattern — frame 0, slot `s` returning ring word `4*s` — pointed to a factor-of-four address-unit error. The follow-up silicon run confirmed the unit distinction: indexed displacement is word-scaled, while ordinary `MODIFY` remains byte-scaled.

Fixing it
======

The host model and the probe were corrected to represent the word-scaled indexed displacement. The follow-up probe was then checked on DSP4 at the same id-39 patch point:

| stage | what it was | result |
|---|---|---|
| probe v1, DSP4 id-39 | index-addressed copy compared with absolute copy | 42/48 words **different**; frame 0 slot `s` read word `4*s` |
| emulator correction | indexed displacement modeled in words; ordinary `MODIFY` remains byte-scaled | host-tested |
| probe v2, B/bma1 DSP4 id-39 | armed pass `seq=2`, buffer `00256dc8`, `miss=0` | **0/48 wrong**; per-slot dBFS matched (`0:-68 1:-70 2:-85 3:-89 5:-80 6:-81`); sync 24/24; clean unpatch |
| levels hook | one remaining indexed-load caller corrected to use the silicon unit | open change; host-tested, not loaded on a board |

Probe v2 confirms the address-unit rule at this patch point. It does not validate the separate levels-hook caller or prove a multi-frame delay ring; those are different code paths and need their own checks.

Where this leaves the array
======

I can read a frame of real microphone audio off DSP4, with alignment proven by the sync witnesses, using the absolute-address copy; the corrected indexed copy now matches it word for word at id-39. I can form a bit-exact beam from the same snapshot in memory. Neither result establishes direction or quality, and the separate levels-hook caller and multi-frame delay ring remain to be checked. What I still cannot say is *what actually leaves the tile* on the eight Dante channels — and the firmware itself contradicts itself about that. That contradiction is Part 7.
