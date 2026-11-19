---
layout: single
title: "BMA360, Part 3: The Dante Card Is a Second Computer"
excerpt: "The Brooklyn-3 card looked dark from the main board. It isn't. It's a Zynq running its own Linux, reachable over an internal Ethernet link, with its own flash partitions one dd apart. And its PL does the packetizing, which matters later."
tags:
  - Hardware
  - Zynq
  - Dante
  - BMA360
  - Reverse Engineering
---

Part 2 got me a shell on the OMAP. But the OMAP is only half the tile. The audio leaves the main board over a card-edge TDM bus and lands on an Audinate Brooklyn-3 module — a Xilinx Zynq-7000 XC7Z015 with its own QSPI flash. For a while my notes called the card "dark": no console found, no obvious way in. The way I was wrong is the useful part.

The card is not dark, it is on the network
======

The main board and the Brooklyn-3 card are joined by an internal Ethernet link, not just the audio TDM bus. From the OMAP shell, the card's own management interface is one subnet away:

```
board$ ip link set eth1 up
board$ ip addr add <card-subnet-ip>/16 dev eth1
board$ ip neigh show
  <card-ip> dev eth1 lladdr <REDACTED-MAC> REACHABLE
board$ ping -c2 <card-ip>
  2 packets transmitted, 2 received, 0% packet loss
board$ busybox nc -w2 <card-ip> 23
  (port 23 open; everything else refused)
board$ busybox telnet <card-ip>
  <hostname> login:
```

A telnet login prompt. The "dark card" was just a card I had not brought the link up to. Every earlier note that treated the Zynq as unreachable was corrected by that one transcript.

Its own Linux, its own flash
======

Once on the card it is plainly a second Linux system, and its flash is carved into named partitions through a Zynq flash driver (char major 90; the block nodes are major 31, mtdblock):

```
/dev/flash/skd         c 90 0     /dev/flash/fsbl        c 90 2
/dev/flash/safefpga    c 90 4     /dev/flash/safeboot    c 90 6
/dev/flash/safebootenv c 90 8     /dev/flash/fpga        c 90 10
/dev/flash/boot        c 90 12    /dev/flash/bootenv     c 90 14
/dev/flash/kernel      c 90 16    /dev/flash/rootfs      c 90 18
/dev/flash/userblock   b 31 10    /dev/flash/userarea    c 90 20
/dev/flash/brdinfo     c 90 22    /dev/flash/license     b 31 12
/dev/flash/config      c 90 30    /dev/flash/image       c 90 34
```

Note the pattern: a `safefpga`/`safeboot` pair mirroring the live `fpga`/`boot` ones — the same parachute idea as the OMAP's safe kernel, one level down. The `fsbl` (first-stage boot loader) is a single `dd` away. These nodes are created at boot by the driver, so searching the rootfs image on disk for `/dev/flash` finds nothing; you only see them on a running card.

The boot stages announce themselves over the card's own serial lines. Its device tree brings up two `xuartps` ports as `u-boot,dm-pre-reloc`, meaning there is console output from the very first boot stage, at 115200:

```
serial0 = /amba/serial@e0000000
serial1 = /amba/serial@e0001000     (both xuartps, both pre-reloc)
```

The physical fallback
======

If the internal link is ever unavailable, the card is a Mini-PCI Type III module (Amp 1318228-1, 124 pins) and the console is on the card edge. The reliable, non-NDA part of that connector is the power and ground map, which is all you actually need to probe safely:

```
Connector: Mini-PCI Type III, 124 pins (2 rows x 62); KEY between pins 2 & 3
 3.3V    19, 24, 28, 63, 70, 88, 89
 VCC5VA  123        3.3VAUX  124
 GND     23, 27, 55, 62, 69, 74, 77, 82, 83, 85, 119, 120
Edge functions (module datasheet): 2x RS232 | 4x GPIO | 2x SPI | 1x I2C
                                   8x SDIN + 8x SDOUT (TDM) | RGMII | word clock
```

One honest gap, flagged because it can cost you a chip: the exact signal-to-pin assignment for the RS-232 console is under NDA and I do not have it, and the MIO bank's I/O voltage (`VCC_IO`) is undocumented — it may be 1.8 V. Measure before you attach a 3.3 V dongle. Find the console the slow way: TX idles high, so scope the candidates for an idle-high line that bursts at power-up.

Why this card matters to the project
======

Two facts from the card change the plan later.

First, the eight-channel ceiling is not a hardware limit of the module — the Brooklyn-3 supports far more Dante channels. Eight is a configuration choice in the main-board FPGA's TDM output, which means the question "what are the eight channels?" is a question about the Cyclone's config, not about this card.

Second, and this is the one that bites in Part 8: on the stock bitstream the Zynq's **programmable logic packetizes the audio itself, and the processor side never sees the samples**. The ARM on this card is as blind to PCM as the OMAP is. So "just read the audio off the Dante card's Linux" is not a path either. If I want raw samples out through this card, I have to put my own logic in its PL — not write a userspace program on it.

That is both computers in the tile with a shell on each — OMAP Linux and Brooklyn-3 Linux — and audio I still cannot touch from either of them. The next part is about why the obvious remaining route, the vendor application and the Cyclone bitstream, is also a dead end, and how I proved it rather than assumed it.
