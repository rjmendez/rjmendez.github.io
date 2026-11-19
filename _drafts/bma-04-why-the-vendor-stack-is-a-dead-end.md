---
layout: single
title: "BMA360, Part 4: Why the Vendor Stack Is a Dead End"
excerpt: "Three shells, no samples. The vendor app talks to the FPGA through a char device with a lie in its ioctl encoding; a 16,128-word sweep of the register space found sixteen mirrors and zero audio FIFOs; and the Cyclone configures itself from its own flash, so Linux never holds the bitstream. I did keep the vendor's meters, though."
tags:
  - Hardware
  - FPGA
  - Reverse Engineering
  - BMA360
---

By this point I had shells on both computers in the tile and still could not read a microphone. The remaining obvious route was the vendor's own application: let `heb_app.bin` run, and borrow its access to the FPGA and the DSPs. This part is why that route does not get you raw audio either, and how I proved each wall instead of assuming it.

The front door: /dev/c1fpga
======

The application reaches the Cyclone through a char device, `/dev/c1fpga` (major 200). The kernel module `c1fpga.ko` maps the FPGA's EMIF chip-select 4 window (physical `0x64000000`) and exposes four ioctls. The first thing I tried failed with `EFAULT`, which sent me into the disassembly, and the disassembly has two good lessons in it.

Lesson one: you will `grep` the binary for the ioctl numbers and find nothing, because the base is stored *negated* so a single add does the subtraction.

```c
/* PSEUDOCODE, reconstructed from c1fpga.ko */
long c1fpga_ioctl(struct file *f, unsigned cmd, unsigned long arg) {
    unsigned idx = cmd + 0x3FFB94FF;        /* == cmd - 0xC0046B01; grep 'C0046B01' finds nothing */
    if (idx > 3) return 0;                  /* unknown cmd: silent success (!) */

    void *uptr;
    copy_from_user(&uptr, (void*)arg, 4);   /* arg is a POINTER TO A POINTER */
    if (!uptr) { printk("null data pointer from user"); return -EFAULT; }

    struct c1fpga_reg r;                     /* 12 bytes, not the 4 the _IOC size claims */
    copy_from_user(&r, uptr, (idx == 3) ? 100 : 12);
    u32 off = r.offset & 0xFFFF;             /* BYTE offset into CS4 */
    switch (idx) {
      case 0: r.value = readw(cs4 + off); copy_to_user(uptr,&r,12); break;  /* read  */
      case 2: writew(r.value, cs4 + off); break;                            /* write */
      /* 1 = kernel-log dump, 3 = 16-way bulk write */
    }
}
```

Lesson two is the `EFAULT`: the ioctl argument is a *pointer to a pointer*, and the struct is 12 bytes even though the `_IOC` size field encodes 4. Once I matched both, my reads lined up with the vendor's own `fpgar` tool:

| path | what you pass | address it hits | `0x22` reaches |
|---|---|---|---|
| my fixed ioctl | 12-byte struct, byte offset | `base + offset` | `0x64000022` yes |
| vendor `fpgar` | full 8-digit address | validated, even-only | `0x64000022` yes |

Reading `0x64000022` returns `0x0117` — the FPGA version. That is also the single best integrity check on the whole board: it is static, so if it ever reads something else, your access path has desynced, not the hardware.

The sweep that found nothing
======

With working reads I did the obvious thing and swept the entire CS4 window — 16,128 words — looking for the audio sample FIFOs the app must be reading. There are none. What is actually there is sixteen 2 KB copies of one register file:

```
0x64000000  bank 0   real registers (version, matrix, meters, DSP control...)
0x64000800  bank 1   MIRROR, except word +0x002 = 0x0010
0x64001000  bank 2   MIRROR, except word +0x002 = 0x0020
   ...      16 banks of 2 KB, identical register file
0x64007800  bank 15  MIRROR, word +0x002 = 0x00f0
0x64008000  reads segfault the driver
0x64010000  wraps: read(0x10004) == read(0x004)
```

The only thing that changes bank to bank is one word that echoes the address: `word[+0x002] = (addr >> 11) << 4`. That killed a standing assumption — there were notes claiming "per-channel routing blocks at `0x64000800 + N*0x800`", and those blocks are simply the same registers seen sixteen times. The negative result is the useful one: **the audio does not pass through a register the OMAP can read.** It stays on the TDM buses between the Cyclone, the SHARCs and the Dante card. There is nothing here to tap.

Borrowing the vendor's ears
======

Not everything in the app was a dead end. It has a metering path — level meters it latches out of the FPGA and reports — and meters I *can* read, because they go through a register. The read is two writes and a read:

```c
/* PSEUDOCODE -- the app's own meter read, reusable from a shell tool */
FpgaWrite(0x90, meter->FpgaAddress & 0xFFFF);  /* latch which meter */
FpgaRead (0x92, &word);                         /* read the pair */
u8 raw = (meter->BytePosition == 0) ? (word & 0xFF) : (word >> 8);
int dB  = 20 - (raw >> 1);                       /* -> dBFS, floored at -99 */
```

Playing a known sound at the tile and watching those levels move was the first hard proof the array actually hears — obtained with no audio path at all, just the vendor's own instrument borrowed through two registers. Levels only, no waveform. But it meant the microphones and the front end were alive, and the problem really was egress, not a dead sensor. I reused this borrow-the-instrument trick later.

The bitstream you cannot hold
======

The last vendor route is the Cyclone bitstream itself — if I could rewrite the FPGA I could add my own egress. Two findings closed that door for now.

First, the Cyclone configures itself. On power-up it loads its own bitstream from a dedicated SPI flash in Active Serial mode. Linux is not in the loop:

```
POWER ON:  Cyclone V --Active Serial--> its own SPI NOR (mt25ql256) --> configured. Linux absent.

UPDATE:    fpgaupdate -> /dev/mt25ql256 (major 155) -> erase/program -> read back (ioctl 0xC0046B0C)
             -> GPIO bit-bang: 127=DCLK, 123=ASDO, 124=DATA0   (3-wire shifter, NO TMS -> not a JTAG TAP)

VERIFY (read-only, free):  fpgar 0x64000022 -> which bitstream is RUNNING (not what's in flash)
```

Second, the one time the vendor update path ran on a long-uptime board, its driver asked the kernel for an order-10 allocation — 4 MiB of *physically contiguous* memory — and failed, leaving the process wedged in uninterruptible `D` state until a power cycle. That is a vendor-driver bug, reproducible, and a good reason not to lean on the update path casually.

And the bitstream is opaque. It is wrapped in the vendor's ASCII container with a CRC-16/ARC over the payload (which does check out), but the payload is not a Xilinx or stock Quartus image — no sync word, entropy around 6.6 so not encrypted, just not a format I can round-trip yet. Rewriting the fabric is a future problem, not this project's path.

The aperture they turned off
======

One more thing the vendor stack showed me, by sweeping the echo-canceller groups and watching which microphones produced signal:

| element group | mics | result |
|---|---|---|
| 0-11 | 1-96 | live |
| 12-14 | **97-120** | **silent** |
| 15 | 121 | live |

Twenty-four of the 121 elements carry nothing in the shipped bitstream. For a conference phone that is fine. For an acoustic camera it is 24 elements of aperture switched off in firmware I cannot yet rewrite — a hard ceiling on what the stock fabric can ever give me.

Scorecard
======

So the vendor stack gives me: register access, level meters, and control of the DSP-load and matrix hardware. It does **not** give me a sample, and the one stage I would need to change — the bitstream — is self-loaded, opaque, and backed by a flaky updater. The audio lives on the TDM bus into the SHARC+ DSPs.

Which means the only place left to stand is on the DSPs themselves. Part 5 is getting my own code to run on one.
