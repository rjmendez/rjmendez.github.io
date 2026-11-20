---
layout: single
title: "BMA360, Part 6: Samples Off DSP4, and an Index Register That Lied"
excerpt: "One pointer in data memory names the buffer the DSP just filled. Copy it and you have a frame of real microphone noise floor. Then a word-versus-byte addressing bug made my first indexed copy read 42 of 48 words wrong while reporting a clean pass."
tags:
  - Hardware
  - SHARC
  - DSP
  - Reverse Engineering
  - BMA360
---

Part 5 got my code running inside DSP4's interrupt. This part is the first microphone audio out of the chip, a register readout that does not agree with it, and an addressing bug that produced confident wrong numbers.

The receive ring
======

DSP4 receives on serial port 0 (SPORT0) in 24-bit words. Each time the interrupt runs, DMA has filled one buffer of 8 frames, and the vendor code keeps three of those buffers in a ring. One pointer in data memory, `0x256dc4`, always holds the address of one of the three.

![DSP4's receive ring. A pointer at 0x256dc4 names one of three buffers at 0x256dc8, 0x257068 and 0x257308. The ISR runs about 6000 times a second and each pass fills one buffer of 8 frames of 21 words, 48 kHz per slot. With other DSPs loaded too, a frame carries mic audio in slots 0 to 3, 5 and 6, a non-mic stream in slot 4, zeros in 7 to 18, and the sync constants 0x0000ff00 and 0x00123456 in slots 19 and 20. With only DSP4 loaded, slots 0 to 3, 5 and 6 are zero and slot 4 and the sync words remain.](/images/bma/dsp4-receive-ring-light.svg){: .only-light}
![DSP4's receive ring. A pointer at 0x256dc4 names one of three buffers at 0x256dc8, 0x257068 and 0x257308. The ISR runs about 6000 times a second and each pass fills one buffer of 8 frames of 21 words, 48 kHz per slot. With other DSPs loaded too, a frame carries mic audio in slots 0 to 3, 5 and 6, a non-mic stream in slot 4, zeros in 7 to 18, and the sync constants 0x0000ff00 and 0x00123456 in slots 19 and 20. With only DSP4 loaded, slots 0 to 3, 5 and 6 are zero and slot 4 and the sync words remain.](/images/bma/dsp4-receive-ring-dark.svg){: .only-dark}

```
DATA MEMORY (DSP4)
  0x256dc4  pointer to the current buffer
  0x256dc8  buffer A \
  0x257068  buffer B  > 3 buffers x 8 frames x 21 words (0x2a0 bytes each)
  0x257308  buffer C /
```

The interrupt runs at 5999.6 per second on the stock image; 8 frames per pass makes 48 kHz. Slots 19 and 20 hold the same two constants, `0x0000ff00` and `0x00123456`, in every frame. A copy that does not find them at words 19 and 20 started in the wrong place, so every read I take checks them first.

A frame of real audio
======

With DSP4 loaded alongside other DSPs, loaded one at a time, my hook reads the pointer and copies the buffer it names. This is one such copy, from the fourth hook session on array B:

![Bar chart of the peak level in each of the 21 slots of one frame from DSP4 with other DSPs loaded too. Slots 0 to 3, 5 and 6 sit between -65 and -79 dBFS. Slot 4 reads -10 dBFS and is sparse spikes, not a microphone. Slots 7 to 18 are exact zero. Slots 19 and 20 are the sync constants, -42 and -17 dBFS.](/images/bma/p06-frame-levels-light.svg){: .only-light}
![Bar chart of the peak level in each of the 21 slots of one frame from DSP4 with other DSPs loaded too. Slots 0 to 3, 5 and 6 sit between -65 and -79 dBFS. Slot 4 reads -10 dBFS and is sparse spikes, not a microphone. Slots 7 to 18 are exact zero. Slots 19 and 20 are the sync constants, -42 and -17 dBFS.](/images/bma/p06-frame-levels-dark.svg){: .only-dark}

Six slots carry a microphone noise floor. Across those sessions it sat between -61 and -85 dBFS and moved around the way a live acoustic floor does. Slot 4 is something else: sparse spikes up to -10 dBFS. The sync words were in place in 24 of 24 frames.

In the same pass the hook summed those six slots into a broadside beam and compared it with the same sum computed from the snapshot. The two match bit for bit. That shows my code copies the right block and does the arithmetic right. It says nothing about direction or beam quality: six slots, no delays, one snapshot.

What is actually in the slots
======

With only DSP4 loaded, the same buffer looks different. Here are 128 frames, 16 dumps of 8 frames each, read straight over SPI:

![A grid of 128 raw frames by 21 slots with only DSP4 loaded. Slots 19 and 20 hold the sync constants in all 128 frames. Slot 4 is the only other non-zero slot, with 17 distinct values including 0x00ffff01 and small integers such as 0x10, 0x07 and 0x04. Slots 0 to 3, 5 and 6 are exactly zero.](/images/bma/p06-lone-dsp4-light.svg){: .only-light}
![A grid of 128 raw frames by 21 slots with only DSP4 loaded. Slots 19 and 20 hold the sync constants in all 128 frames. Slot 4 is the only other non-zero slot, with 17 distinct values including 0x00ffff01 and small integers such as 0x10, 0x07 and 0x04. Slots 0 to 3, 5 and 6 are exactly zero.](/images/bma/p06-lone-dsp4-dark.svg){: .only-dark}

No microphone audio at all, just slot 4 counting through small values and the sync words. So I wrote a hook that copies SPORT0's own registers into data memory, because SPI can read data memory but not the `0x31xxxxxx` register space:

![A table of DSP4's SPORT0 and DMA registers as copied out by the hook, only DSP4 loaded. CTL_A c2000171 (transmit, 24-bit), CTL_B 00000171 (receive), MCTL 00001401 (multichannel, 21-slot window), CS0 00000001 on both halves (only slot 0 enabled, highlighted), CS1 to CS3 zero, DIV 00170020 (external clock and frame sync), DMA0 ADDRSTART 28256dc8, DMA1 ADDRSTART 28257308, XCNT a8 and XMOD 4 (168 four-byte words, 8 frames of 21), CFG 00114221 and 00114223.](/images/bma/p06-sport0-regs-light.svg){: .only-light}
![A table of DSP4's SPORT0 and DMA registers as copied out by the hook, only DSP4 loaded. CTL_A c2000171 (transmit, 24-bit), CTL_B 00000171 (receive), MCTL 00001401 (multichannel, 21-slot window), CS0 00000001 on both halves (only slot 0 enabled, highlighted), CS1 to CS3 zero, DIV 00170020 (external clock and frame sync), DMA0 ADDRSTART 28256dc8, DMA1 ADDRSTART 28257308, XCNT a8 and XMOD 4 (168 four-byte words, 8 frames of 21), CFG 00114221 and 00114223.](/images/bma/p06-sport0-regs-dark.svg){: .only-dark}

The DMA geometry matches the ring exactly: 168 words of 4 bytes, 8 frames of 21. The surprise is the channel select. `CS0 = 0x00000001` enables only slot 0 of the 21-slot window, on both halves. By the hardware reference the SPORT should write slot 0 and nothing else, so the sync words and slot 4 are probably written by the firmware, and with only DSP4 loaded slot 0 itself is zero.

That leaves an open question I have not closed. With other DSPs loaded alongside DSP4, slots 1 to 3, 5 and 6 carry a noise floor that looks exactly like microphones, and a nine-DSP reload sets CS0 back to `1`. On array A, setting CS0 to `0x001fffff` with the stock FPGA image still showed mic data in slots 0 to 6. Where the words in slots 1 to 6 come from with only slot 0 enabled, I do not know yet. My own DSP image will set CS0 to `0x1fffff` explicitly and not depend on the answer.

The index register that lied
======

To make the copy loop cheaper I wanted it to load through an index register, `DM(disp, I4)`, instead of 48 absolute addresses. The first probe installed, ran one armed pass, and reported zero misses. Then I compared the indexed copy against an absolute copy taken in the same pass, word for word.

![Two bar charts comparing the indexed copy (red) with the absolute copy (blue) per slot. Probe v1: 42 of 48 words differ; the indexed copy reads -10 dBFS in slot 1 (it read word 4, the slot-4 stream), -17 in slot 5 (word 20, the sync word 0x123456) and zero in slots 2 and 3 (words 8 and 12). Probe v2: 0 of 48 words differ and every slot matches.](/images/bma/p06-idxprobe-light.svg){: .only-light}
![Two bar charts comparing the indexed copy (red) with the absolute copy (blue) per slot. Probe v1: 42 of 48 words differ; the indexed copy reads -10 dBFS in slot 1 (it read word 4, the slot-4 stream), -17 in slot 5 (word 20, the sync word 0x123456) and zero in slots 2 and 3 (words 8 and 12). Probe v2: 0 of 48 words differ and every slot matches.](/images/bma/p06-idxprobe-dark.svg){: .only-dark}

42 of the 48 words were different. The other 6 matched only because both sides were zero. "Zero misses" meant the pass completed, not that the words were right.

The wrong values gave the cause away. In frame 0 the indexed copy of slot `s` held ring word `4*s`: slot 1 got the slot-4 stream, slot 5 got the `0x123456` sync word, slots 2 and 3 got the zeros at words 8 and 12. Every displacement was four times too large.

```
SHARC+ address arithmetic, as measured at this patch point
  DM(disp, I4)     effective byte address = I4 + 4*disp     (disp counts WORDS)
  MODIFY(I4, imm)  I4 += imm                                 (imm counts BYTES)
```

My assembler and emulator treated both as bytes. Probe v2 emits word displacements for `DM(disp, I4)` and leaves `MODIFY` in bytes. On DSP4, at the same patch point, it matched the absolute copy in all 48 words.

| stage | what it was | result |
|---|---|---|
| probe v1 | indexed copy against absolute copy, same pass | 42/48 words different; frame 0 slot `s` read word `4*s` |
| emulator fix | `DM(disp, I4)` displacement in words, `MODIFY` in bytes | host-tested |
| probe v2 | same comparison, array B DSP4 | 0/48 wrong; per-slot levels identical (`0:-68 1:-70 2:-85 3:-89 5:-80 6:-81`); sync 24/24; clean unpatch |
| levels hook | ran on DSP4 on 2026-11-16 with the byte assumption | its per-slot peaks are invalid; the corrected caller is merged and host-tested, not yet loaded on a board |

Where this leaves the array
======

I can copy a frame of DSP4's receive ring with alignment checked by the sync words, and the indexed copy now matches the absolute one word for word. The noise floor in slots 0 to 3, 5 and 6 is real, but the register readout says the SPORT only captures slot 0, and I have not reconciled the two. What leaves the tile on the eight Dante channels is Part 7.
