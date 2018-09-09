---
title: 'ViaSat rm4100 Console Access'
date: 2018-09-8
permalink: /posts/2018/09/rm4100-console/
tags:
  - Hardware
  - UART
  - U-Boot
  - Reverse Engineering
---

This is part of a series on reversing the ViaSat rm4100 satellite modem.

Changing Memory
======

Using a hex editor we can go ahead and change the values at the following addresses.

![Memory_before](/images/Memory_before.png)

cli_enable sounds fun right? 9 seconds should be enough to find that pesky ANY key.

![Memory_after](/images/Memory_after.png)

Swapping the bytes back with dd and ready to write to a chip.

![Memory_after_ready_to_flash](/images/Memory_after_ready_to_flash.png)

Writing to flash.

![MX29GL256FLT2I-90Q_writing](/images/MX29GL256FLT2I-90Q_writing.png)

Verify that it wrote what I wanted.

![MX29GL256FLT2I-90Q_verify](/images/MX29GL256FLT2I-90Q_verify.png)

Heat up the soldering iron, its time to burn things for science!


Hardware
======

To speed things up we can use some extra flash memory chips to practice on, they don't take repeated heating and cooling very well and this tinkering will probably kill some.

This is what we will be removing

![MX29GL256FLT2I-90Q_on_board](/images/MX29GL256FLT2I-90Q_on_board.jpg)

Tools
------

Chipquik low temp solder: This lets us use less heat to remove the component and prevents damage to the pads and component. It isnt really solder, this stuff contains bismuth and will expand when it crystalizes. This will give you some disgusting looking solder joints that will also be brittle as hell, its important to clean this a few times with fresh solder and braid.

![Chipquik_box](/images/Chipquik_box.jpg)
![Chipquik_alloy](/images/Chipquik_alloy.jpg)

Amtech 559 flux: I love this stuff, it doesnt burn up the same way as other fluxes and does not deposit a hard layer of rosin after use. It also doesn't stink as bad when you hit it with a hot air wand.

![Amtech_559_flux](/images/Amtech_559_flux.jpg)

Rip and Replace
------

Apply quite a bit of the flux to cover the area we are working on, Chipquik likes to smear all over the board and this will keep things contained and clean.

![MX29GL256FLT2I-90Q_fluxed](/images/MX29GL256FLT2I-90Q_fluxed.jpg)

Enough is applied to cover all of the leads on the flash chip, this gives us a bit more thermal mass to work with when removing. This is applied like one is drag soldering with a soldering iron.

![MX29GL256FLT2I-90Q_chipquik](/images/MX29GL256FLT2I-90Q_chipquik.jpg)

The chip itself can be unsulated frim the hot air with kapton tape or a special nozzle can be used, I like the tape because it gives me a bit of a handle to jiggle the chip with while heating. Not much force is needed, just enough to see if the chip is ready to move and possibly to work some of the low temp alloy into the solder joints.

![MX29GL256FLT2I-90Q_pads_removed](/images/MX29GL256FLT2I-90Q_pads_removed.jpg)

The pads are looking extra disgusting, they will be cleaned with desoldering braid and get a fresh coating of leaded solder and braided again to remove all of that gross stuff. The pads get a bead of flux on them and the flash chip is put in place on top of these.

![MX29GL256FLT2I-90Q_placed](/images/MX29GL256FLT2I-90Q_placed.jpg)

With the chip lined up and pin 1 verified we can start tacking it to the board, it really helps to solder the four corners of the flash chip down first before drag soldering. Keep enough flux on the leads here and keep the solder on the iron under control to prevent bridges, if to much is applied it can be removed with braid.

![MX29GL256FLT2I-90Q_drag_soldered_clean_flux.jpg](/images/MX29GL256FLT2I-90Q_drag_soldered_clean_flux.jpg)

Work Smarter Not Harded
------

Previously I traced the contacts from a bga component and verified with an oscilloscope, this kind of saved some time to verify that these were also broken out to the pin header on the back of the board. I'll leave it up to the reader to decide on this one. :D

![RM4100_debug_header](/images/RM4100_debug_header.jpg)


Booting
======

Using the pins identified before lets boot the modem.

```
Entering UART passthrough! Press Ctrl-X to abort...

UT_BOOT v1.2.4 (Build time: Nov 24 2010 - 10:25:58) (Based on U-Boot 1.1.1)

CN3010_LF_P1 board revision major:1, minor:0, serial #: unknown
OCTEON CN5020-SCP pass 1.1, Core clock: 300 MHz, DDR clock: 300 MHz (600 Mhz data rate)
DRAM:  256 MB
Clearing DRAM...... done
*** Warning - bad CRC, using default environment

Flash: 32 MB
BIST check passed.
Net:   octeth0, octeth1, octeth2
Hit any key to stop autoboot:  0
Octeon cn3010_lf_p1# ?
?       - alias for 'help'
askenv  - get environment variables from stdin
autoscr - run script from memory
base    - print or set address offset
bdinfo  - print Board Info structure
bootelf - Boot from an ELF image in memory
bootoct - Boot from an Octeon Executive ELF image in memory
bootoctelf - Boot a generic ELF image in memory. NOTE: This command does not support
             simple executive applications, use bootoct for those.
bootoctlinux - Boot from a linux ELF image in memory
cmp     - memory compare
coninfo - print console devices and informations
cp      - memory copy
crc32   - checksum calculation
dhcp    - invoke DHCP client to obtain IP/boot params
echo    - echo args to console
erase   - erase FLASH memory
exit    - exit script
ext2load- load binary file from a Ext2 filesystem
ext2ls  - list files in a directory (default /)
flinfo  - print FLASH memory information
freeprint    - Print list of free bootmem blocks
go      - start application at address 'addr'
gunzip  - Uncompress an in memory gzipped file
help    - print online help
itest    - return true/false on integer compare
loadb   - load binary file over serial line (kermit mode)
loop    - infinite loop on address range
md      - memory display
md5   - MD5 hash calculation
mii     - MII utility commands
mm      - memory modify (auto-incrementing)
mtest   - simple RAM test
mw      - memory write (fill)
namedalloc    - Allocate a named bootmem block
namedfree    - Free a named bootmem block
namedprint    - Print list of named bootmem blocks
nm      - memory modify (constant address)
ping    - send ICMP ECHO_REQUEST to network host
printenv- print environment variables
protect - enable or disable FLASH write protection
read64    - read 64 bit word from 64 bit address
read64b    - read 8 bit word from 64 bit address
read64l    - read 32 bit word from 64 bit address
read64s    - read 16 bit word from 64 bit address
read_cmp    - read and compare memory to val
reset   - Perform RESET of the CPU
run     - run commands in an environment variable
saveenv - save environment variables to persistent storage
setenv  - set environment variables
setexpr - set environment variable as the result of eval expressionsleep   - delay execution for some time
test    - minimal test like /bin/sh
tftpboot- boot image via network using TFTP protocol
version - print monitor version
vsat_crc_check   - Verify the CRC in the header of a software image is valid.
vsat_get_sw_version   - Get the software version from the header of a software image.
vsat_ledtest   - configure LEDs
vsat_mtest   - quick RAM test
write64    - write 64 bit word to 64 bit address
write64b    - write 8 bit word to 64 bit address
write64l    - write 32 bit word to 64 bit address
write64s    - write 16 bit word to 64 bit address
Octeon cn3010_lf_p1#
```

Looks like that worked and we now have access to the U-Boot console. Lets see what the environment variables are.

```
Octeon cn3010_lf_p1# printenv
bootdelay=5
baudrate=115200
download_baudrate=115200
bootloader_flash_update=protect off ${uboot_flash_addr} +${uboot_flash_size};erase ${uboot_flash_addr} +${uboot_flash_size};cp.b ${fileaddr} ${uboot_flash_addr} ${uboot_flash_size}
burn_app=erase ${flash_unused_addr} +${filesize};cp.b ${fileaddr} ${flash_unused_addr} ${filesize}
bf=bootoct ${flash_unused_addr} forceboot numcores=${numcores}
nuke_env=protect off ${env_sector_addr} +${env_sector_size}; erase ${env_sector_addr} +${env_sector_size}
autoload=n
netretry=no
cli_enable=1
coremask=3
ethaddr=DE:AD:BE:EF:04:00
ipaddr=192.168.100.1
serverip=192.168.100.10
max_sw_size=1C00000
sw_hdr_len=14
sw0_flash_offset=80000
sw0_size=e00000
sw1_flash_offset=e80000
sw1_size=e00000
sw0_indicator=0
sw1_indicator=1
current_sw_image=0
calc_sw_size_long=setexpr sw_copy_len_long ${sw_copy_len} / 4; setexpr len_mod ${sw_copy_len} % 4; if test ${len_mod} != 0; then setexpr sw_copy_len_long ${sw_copy_len_long} + 1; fi
calc_sw_vars=setenv sw_start_addr ${sw_addr}; setenv sw_copy_len ${sw_size}; run calc_sw_size_long
clear_sw_vars=setenv sw_addr; setenv sw_start_addr; setenv sw_copy_len; setenv sw_copy_len_long
wr_image_setup=setexpr sw_addr ${flash_base_addr} + ${sw0_flash_offset}; sw_size=${filesize}
wr_image_finish=erase ${sw_addr} +${sw0_size}; cp.l ${fileaddr} ${sw_start_addr} ${sw_copy_len_long}; setenv current_sw_image ${sw0_indicator}; setenv sw0_size ${sw_size}; run clear_sw_vars; saveenv
wr_image=run wr_image_setup; run calc_sw_vars; run wr_image_finish
get_boot_args=if test ${cli_enable} = 0; then cli_arg=console=NULL; if test ${bootdelay} > 0; then setenv bootdelay 0; saveenv; fi; fi; setenv boot_args coremask=${coremask} ${cli_arg} mem=${sdram_size_dec}
boot_ram=run get_boot_args; bootoctlinux ${loadaddr} ${boot_args}
load_sw_from_flash=run calc_sw_vars; cp.l ${sw_start_addr} ${loadaddr} ${sw_copy_len_long}; run clear_sw_vars
boot_flash=run load_sw_from_flash; run boot_ram
boot_sw0=echo Booting Software Image 0; setenv booting_sw_image 0; setexpr sw_addr ${flash_base_addr} + ${sw0_flash_offset}; sw_size=${sw0_size}; run boot_flash; echo Failed to boot SW Image 0; setenv current_sw_image 1; saveenv
boot_sw1=echo Booting Software Image 1; setenv booting_sw_image 1; setexpr sw_addr ${flash_base_addr} + ${sw1_flash_offset}; sw_size=${sw1_size}; run boot_flash; echo Failed to boot SW Image 1; setenv current_sw_image 0; saveenv
boot_sw=vsat_mtest; if test ${current_sw_image} = ${sw0_indicator}; then run boot_sw0; run boot_sw1; else run boot_sw1; run boot_sw0; fi
bootcmd=run boot_sw
loadaddr=aa00000
numcores=2
stdin=serial
stdout=serial
stderr=serial
env_addr=bfbfe000
env_size=2000
env_sector_addr=bfbe0000
env_sector_size=20000
flash_base_addr=bdc00000
flash_size=2000000
uboot_flash_addr=bdc00000
uboot_flash_size=50000
flash_unused_addr=bdc50000
flash_unused_size=1fae000
ethact=octeth0
sdram_size_dec=268435456
ver=UT_BOOT v1.2.4

Environment size: 2919/8188 bytes
Octeon cn3010_lf_p1#
```
Those were the wrong memory addresses it seems... but on failure it will roll over to some defaults.

![uboot_fallback_values](/images/uboot_fallback_values.png)

How about a regular boot now?

```
ELF file is 64 bit
Attempting to allocate memory for ELF segment: addr: 0xffffffff80100000 (adjusted to: 0x0000000000100000), size 0x11b4bf0
Allocated memory for ELF segment: addr: 0xffffffff80100000, size 0x11b4bf0
Processing PHDR 0
  Loading 10e6200 bytes at ffffffff80100000
  Clearing ce9f0 bytes at ffffffff811e6200
## Loading Linux kernel with entry point: 0xffffffff8052bce0 ...
Bootloader: Done loading app on coremask: 0x3
Linux version 3.10.20-rt14 (jperhach@vcalfutd03) (gcc version 4.7.0 (Cavium Inc. Version: SDK_3_1_0 build 32) ) #2 SMP PREEMPT Tue Feb 16 15:45:44 PST 2016
CVMSEG size: 2 cache lines (256 bytes)
Cavium Inc. SDK-3.1
bootconsole [early0] enabled
CPU revision is: 000d0601 (Cavium Octeon+)
Checking for the multiply/shift bug... no.
Checking for the daddiu bug... no.
Determined physical RAM map:
 memory: 0000000006000000 @ 0000000001e00000 (usable)
 memory: 0000000007c00000 @ 0000000008000000 (usable)
 memory: 0000000000618000 @ 0000000000100000 (usable)
 memory: 0000000000ad8000 @ 0000000000718000 (usable after init)
Wasting 14336 bytes for tracking 256 unused pages
Initrd not found or empty - disabling initrd
Using LF P1 Device Tree <ffffffff80754840> DTB size 7305.
Copying FDT from fdt<ffffffff80754840> to initial_boot_params<8000000001e02000>
Storing fdt addr as: 0x1e02000
Using internal Device Tree.
software IO TLB [mem 0x0218b000-0x021cb000] (0MB) mapped at [800000000218b000-80000000021cafff]
Zone ranges:
  DMA32    [mem 0x00100000-0xefffffff]
  Normal   empty
Movable zone start for each node
Early memory node ranges
  node   0: [mem 0x00100000-0x011effff]
  node   0: [mem 0x01e00000-0x07dfffff]
  node   0: [mem 0x08000000-0x0fbfffff]
Primary instruction cache 32kB, virtually tagged, 4 way, 64 sets, linesize 128 bytes.
Primary data cache 16kB, 64-way, 2 sets, linesize 128 bytes.
Secondary unified cache 128kB, 8-way, 128 sets, linesize 128 bytes.
PERCPU: Embedded 11 pages/cpu @80000000021d9000 s12800 r8192 d24064 u45056
Built 1 zonelists in Zone order, mobility grouping on.  Total pages: 59777
Kernel command line:  bootoctlinux aa00000 coremask=3 console=ttyS0,115200 mtdparts=phys_mapped_flash:512k(uboot),14m(SWImage0),14m(SWImage1),128k(certs),3328k(jffs2),-(root)
PID hash table entries: 1024 (order: 1, 8192 bytes)
Dentry cache hash table entries: 32768 (order: 7, 524288 bytes)
Inode-cache hash table entries: 16384 (order: 5, 131072 bytes)
Memory: 220608k/242624k available (4324k kernel code, 22016k reserved, 1914k data, 11104k init, 0k highmem)
SLUB: HWalign=128, Order=0-3, MinObjects=0, CPUs=2, Nodes=1
Preemptible hierarchical RCU implementation.
        RCU debugfs-based tracing is enabled.
        RCU restricting CPUs from NR_CPUS=16 to nr_cpu_ids=2.
NR_IRQS:255
Calibrating delay loop (skipped) preset value.. 600.00 BogoMIPS (lpj=3000000)
pid_max: default: 32768 minimum: 501
Mount-cache hash table entries: 256
Checking for the daddi bug... no.
Performance counters: octeon PMU enabled, 2 64-bit counters available to each CPU, irq 7
SMP: Booting CPU01 (CoreId  1)...
CPU revision is: 000d0601 (Cavium Octeon+)
Brought up 2 CPUs
NET: Registered protocol family 16
Installing handlers for error tree at: ffffffff806b2cb0
bio: create slab <bio-0> at 0
SCSI subsystem initialized
usbcore: registered new interface driver usbfs
usbcore: registered new interface driver hub
usbcore: registered new device driver usb
EDAC MC: Ver: 3.0.0
Switching to clocksource OCTEON_CVMCOUNT
NET: Registered protocol family 2
TCP established hash table entries: 2048 (order: 3, 32768 bytes)
TCP bind hash table entries: 2048 (order: 3, 32768 bytes)
TCP: Hash tables configured (established 2048 bind 2048)
TCP: reno registered
UDP hash table entries: 256 (order: 1, 8192 bytes)
UDP-Lite hash table entries: 256 (order: 1, 8192 bytes)
NET: Registered protocol family 1
octeon_pci_console: Console not created.
/proc/octeon_perf: Octeon performance counter interface loaded
NTFS driver 2.1.30 [Flags: R/O].
jffs2: version 2.2. (NAND) © 2001-2006 Red Hat, Inc.
msgmni has been set to 430
alg: No test for stdrng (krng)
Block layer SCSI generic (bsg) driver version 0.4 loaded (major 253)
io scheduler noop registered
io scheduler cfq registered (default)
octeon_gpio 1070000000800.gpio-controller: octeon gpio register base 8001070000000800
octeon_gpio 1070000000800.gpio-controller: OCTEON GPIO
Serial: 8250/16550 driver, 2 ports, IRQ sharing disabled
1180000000800.serial: ttyS0 at MMIO 0x1180000000800 (irq = 34) is a OCTEON
console [ttyS0] enabled, bootconsole disabled
console [ttyS0] enabled, bootconsole disabled
1180000000c00.serial: ttyS1 at MMIO 0x1180000000c00 (irq = 35) is a OCTEON
brd: module loaded
loop: module loaded
slram: not enough parameters.
spi-octeon 1070000001000.spi: octeon spi register base 8001070000001000
octeon_spi_setup cs 0 speed 16000000 mode 00000003 bpw 8 irq 0 cs-gpio 14
SPI: (2) Set TX for chipselect 0 gpio 14
octeon_spi_setup cs 1 speed 16000000 mode 00000003 bpw 8 irq 0 cs-gpio 15
SPI: (2) Set TX for chipselect 1 gpio 15
octeon_spi_setup cs 2 speed 2000000 mode 00000001 bpw 8 irq 0 cs-gpio 16
SPI: (2) Set TX for chipselect 2 gpio 16
octeon_spi_setup cs 3 speed 16000000 mode 00000003 bpw 8 irq 0 cs-gpio 17
SPI: (2) Set TX for chipselect 3 gpio 17
spi-octeon 1070000001000.spi: OCTEON SPI bus driver
mdio-octeon 1180000001800.mdio: octeon mdio register base 8001180000001800
libphy: mdio-octeon: probed
mdio-octeon 1180000001800.mdio: Version 1.0
octeon-ethernet 2.0
Memory range 8000000001400000 - 8000000001990fff reserved for hardware
Memory range 8000000001991000 - 80000000019dbfff reserved for hardware
Memory range 80000000019dc000 - 8000000001a5bfff reserved for hardware
Memory range 8000000001a5c000 - 8000000001a9bfff reserved for hardware
Interface 0 has 3 ports (RGMII)
octeon_mgmt 1070000100000.ethernet: Version 2.0
Octeon POW only ethernet driver
Waiting for another core to setup the IPD hardware...Done
POW acquired message handle 16
ehci_hcd: USB 2.0 'Enhanced' Host Controller (EHCI) Driver
ehci-platform: EHCI generic platform driver
ohci_hcd: USB 1.1 'Open' Host Controller (OHCI) Driver
OcteonUSB 16f0010000000.usbc: Octeon Host Controller
OcteonUSB 16f0010000000.usbc: new USB bus registered, assigned bus number 1
OcteonUSB 16f0010000000.usbc: irq 56, io mem 0x00000000
usb usb1: New USB device found, idVendor=1d6b, idProduct=0002
usb usb1: New USB device strings: Mfr=3, Product=2, SerialNumber=1
usb usb1: Product: Octeon Host Controller
usb usb1: Manufacturer: Linux 3.10.20-rt14 Octeon USB
usb usb1: SerialNumber: 16f0010000000.usbc
hub 1-0:1.0: USB hub found
hub 1-0:1.0: 1 port detected
OcteonUSB: Registered HCD for port 0 on irq 56
usbcore: registered new interface driver usb-storage
i2c /dev entries driver
i2c-octeon 1180000001000.i2c: version 2.5
octeon_wdt: Initial granularity 5 Sec
watchdog: Software Watchdog: cannot register miscdev on minor=130 (err=-16).
watchdog: Software Watchdog: a legacy watchdog module is probably present.
softdog: Software Watchdog Timer: 0.08 initialized. soft_noboot=0 soft_margin=60 sec soft_panic=0 (nowayout=0)
device-mapper: ioctl: 4.24.0-ioctl (2013-01-15) initialised: dm-devel@redhat.com
EDAC DEVICE0: Giving out device to module 'octeon-cpu' controller 'cache': DEV 'octeon_pc_edac' (INTERRUPT)
EDAC DEVICE1: Giving out device to module 'octeon-l2c' controller 'octeon_l2c_err': DEV 'octeon_l2c_edac' (POLLED)
Netfilter messages via NETLINK v0.30.
nf_conntrack version 0.5.0 (1723 buckets, 6892 max)
NF_TPROXY: Transparent proxy support initialized, version 4.1.0
NF_TPROXY: Copyright (c) 2006-2007 BalaBit IT Ltd.
ipip: IPv4 over IPv4 tunneling driver
gre: GRE over IPv4 demultiplexor driver
ip_gre: GRE over IPv4 tunneling driver
ip_tables: (C) 2000-2006 Netfilter Core Team
arp_tables: (C) 2002 David S. Miller
Initializing XFRM netlink socket
NET: Registered protocol family 10
mip6: Mobile IPv6
sit: IPv6 over IPv4 tunneling driver
ip6_gre: GRE over IPv6 tunneling driver
NET: Registered protocol family 17
Bridge firewalling registered
L2 lock: TLB refill 256 bytes
L2 lock: General exception 128 bytes
L2 lock: low-level interrupt 128 bytes
L2 lock: interrupt 640 bytes
L2 lock: memcpy 1152 bytes
Bootbus flash: Setting flash for 32MB flash at 0x1dc00000
phys_mapped_flash: Found 1 x16 devices at 0x0 in 16-bit bank. Manufacturer ID 0x0000c2 Chip ID 0x00227e
Amd/Fujitsu Extended Query Table at 0x0040
  Amd/Fujitsu Extended Query version 1.3.
number of CFI chips: 1
6 cmdlinepart partitions found on MTD device phys_mapped_flash
Creating 6 MTD partitions on "phys_mapped_flash":
0x000000000000-0x000000080000 : "uboot"
0x000000080000-0x000000e80000 : "SWImage0"
0x000000e80000-0x000001c80000 : "SWImage1"
0x000001c80000-0x000001ca0000 : "certs"
0x000001ca0000-0x000001fe0000 : "jffs2"
0x000001fe0000-0x000002000000 : "root"
Freeing unused kernel memory: 11104K (ffffffff80718000 - ffffffff811f0000)
0
Activating swap...done.
Remounting root filesystem...done.
/etc/rc.d/rcS.d/S90Viasat starting
Fri Jan  1 00:00:00 UTC 2010
Setup fw_printenv
Mount NVRAM
Source persistent local UT environment
Saving Bad Env image to /mnt/jffs2/logs/bad-boot.env
ethaddr in ENV looks OK
hwid in ENV looks OK
serial_number in ENV looks OK
part_number in ENV looks OK
## Error: "Modem_SN" not defined
## Error: "Modem_PN" not defined
## Error: "ethaddr1" not defined
bootLoader_check
UT_BOOT_CHECK: Bootloader file excluded from UT build to save flash space
UT_BOOT_CHECK: Please check production_root file if you wish to include it again
*******************************************
SW VERSION: UT v3.7.3.1 build 25
HW VERSION: 7 - P3_V1
*******************************************
CVMX_SHARED: 0x103b0000-0x10520000
Active coremask = 0x3
Loading Kernel Modules
<1> ad45110_probe (ad45110)
<1> ad45110 f(sample) 16000000 Hz
<1> Enabling SPI mode for ad45110
Loading consumer FPGA driver
rl_fpga_probe (rl-fpga) irq 0 chip_select 0 max speed 16000000 hz
 rlfpga_major is 251
<1> ad9743_probe (ad9743) using ioctl irq 0 cs-gpio 16
<1> f(sample) 2000000 Hz
ad9743_major is 250
Loading Cavium Crypto driver
alg: No test for ecb(des3) (ecb-des3)
Character device rlfpga is major number 251
Character device ad9743 is major number 250
MIMQ /mac_input Open error
mq_open: No such file or directory
mimIf: Failed to open MIM queue: /mac_input!
StatPush: Using default config
device eth0 entered promiscuous mode
IPv6: ADDRCONF(NETDEV_UP): eth0: link is not ready
device eth1 entered promiscuous mode
sysctl: short write
net.ipv4.tcp_slow_start_after_idle = 0
net.ipv4.tcp_rmem = 4096 5000000 5000000
eth1: 1000 Mbps Full duplex, port 1
eth2: 1000 Mbps Full duplex, port 2
net.ipv4.tcp_wmem = 4096 5000000 5000000
net.ipv6.conf.all.forwarding = 1
vm.dirty_background_ratio = 5
 Running usb_hotplug daemon for USB Plug/Play
net.ipv4.conf.lo.force_igmp_version = 2
net.ipv4.conf.eth0.force_igmp_version = 2
net.ipv4.conf.eth1.force_igmp_version = 2
net.ipv4.conf.eth2.force_igmp_version = 2
net.ipv4.conf.pow0.force_igmp_version = 2
Starting internet superserver: inetd.
CVMX_SHARED: 0x103b0000-0x10520000
Active coremask = 0x3
POW ioctl CAVIUM_NET_IOCTL_GMSGHDL; acquired 16
loading FPGA ...
Locking SPI bus ...
FPGA load success...
FPGA load complete signalled
Unlocking SPI bus...
```

It seems to hang here, the following messages are repeated.

```
loading FPGA ...
Locking SPI bus ...
FPGA load success...
FPGA load complete signalled
Unlocking SPI bus...
```

Lets reboot and see whats going on.


```
UT_BOOT v1.2.4 (Build time: Nov 24 2010 - 10:25:58) (Based on U-Boot 1.1.1)

CN3010_LF_P1 board revision major:1, minor:0, serial #: unknown
OCTEON CN5020-SCP pass 1.1, Core clock: 300 MHz, DDR clock: 300 MHz (600 Mhz data rate)
DRAM:  256 MB
Clearing DRAM...... done
Flash: 32 MB
BIST check passed.
Net:   octeth0, octeth1, octeth2
Hit any key to stop autoboot:  0
Starting RAM Test...
Pattern AAAAAAAA  Writing...  Reading...  Pass
Pattern 55555555  Writing...  Reading...  Pass
RAM Test = Pass
Booting Software Image 1
argv[2]: coremask=3
argv[3]: console=NULL
argv[4]: mem=268435456
Software CRC Check = Pass
Uncompressing 0xd3ec49@0xaa00014 to 0x10ef898@0xc600000
ELF file is 64 bit
Attempting to allocate memory for ELF segment: addr: 0xffffffff80100000 (adjusted to: 0x0000000000100000), size 0x11b4bf0
Allocated memory for ELF segment: addr: 0xffffffff80100000, size 0x11b4bf0
Processing PHDR 0
  Loading 10ee200 bytes at ffffffff80100000
  Clearing c69f0 bytes at ffffffff811ee200
## Loading Linux kernel with entry point: 0xffffffff8052b710 ...
Bootloader: Done loading app on coremask: 0x3
Linux version 3.10.20-rt14 (jperhach@vcalfutd03) (gcc version 4.7.0 (Cavium Inc. Version: SDK_3_1_0 build 32) ) #2 SMP PREEMPT Wed May 18 14:18:35 PDT 2016
CVMSEG size: 2 cache lines (256 bytes)
Cavium Inc. SDK-3.1
bootconsole [early0] enabled
CPU revision is: 000d0601 (Cavium Octeon+)
Checking for the multiply/shift bug... no.
Checking for the daddiu bug... no.
Determined physical RAM map:
 memory: 0000000006000000 @ 0000000001e00000 (usable)
 memory: 0000000007c00000 @ 0000000008000000 (usable)
 memory: 0000000000618000 @ 0000000000100000 (usable)
 memory: 0000000000ad8000 @ 0000000000718000 (usable after init)
Wasting 14336 bytes for tracking 256 unused pages
Initrd not found or empty - disabling initrd
Using LF P1 Device Tree <ffffffff80754740> DTB size 7305.
Copying FDT from fdt<ffffffff80754740> to initial_boot_params<8000000001e02000>
Storing fdt addr as: 0x1e02000
Using internal Device Tree.
software IO TLB [mem 0x0218b000-0x021cb000] (0MB) mapped at [800000000218b000-80000000021cafff]
Zone ranges:
  DMA32    [mem 0x00100000-0xefffffff]
  Normal   empty
Movable zone start for each node
Early memory node ranges
  node   0: [mem 0x00100000-0x011effff]
  node   0: [mem 0x01e00000-0x07dfffff]
  node   0: [mem 0x08000000-0x0fbfffff]
Primary instruction cache 32kB, virtually tagged, 4 way, 64 sets, linesize 128 bytes.
Primary data cache 16kB, 64-way, 2 sets, linesize 128 bytes.
Secondary unified cache 128kB, 8-way, 128 sets, linesize 128 bytes.
PERCPU: Embedded 11 pages/cpu @80000000021d9000 s12800 r8192 d24064 u45056
Built 1 zonelists in Zone order, mobility grouping on.  Total pages: 59777
Kernel command line:  bootoctlinux aa00000 coremask=3 console=NULL mtdparts=phys_mapped_flash:512k(uboot),14m(SWImage0),14m(SWImage1),128k(certs),3328k(jffs2),-(root)
PID hash table entries: 1024 (order: 1, 8192 bytes)
Dentry cache hash table entries: 32768 (order: 7, 524288 bytes)
Inode-cache hash table entries: 16384 (order: 5, 131072 bytes)
Memory: 220608k/242624k available (4322k kernel code, 22016k reserved, 1915k data, 11104k init, 0k highmem)
SLUB: HWalign=128, Order=0-3, MinObjects=0, CPUs=2, Nodes=1
Preemptible hierarchical RCU implementation.
        RCU debugfs-based tracing is enabled.
        RCU restricting CPUs from NR_CPUS=16 to nr_cpu_ids=2.
NR_IRQS:255
Calibrating delay loop (skipped) preset value.. 600.00 BogoMIPS (lpj=3000000)
pid_max: default: 32768 minimum: 501
Mount-cache hash table entries: 256
Checking for the daddi bug... no.
Performance counters: octeon PMU enabled, 2 64-bit counters available to each CPU, irq 7
SMP: Booting CPU01 (CoreId  1)...
CPU revision is: 000d0601 (Cavium Octeon+)
Brought up 2 CPUs
NET: Registered protocol family 16
Installing handlers for error tree at: ffffffff806b2cb0
bio: create slab <bio-0> at 0
SCSI subsystem initialized
usbcore: registered new interface driver usbfs
usbcore: registered new interface driver hub
usbcore: registered new device driver usb
EDAC MC: Ver: 3.0.0
Switching to clocksource OCTEON_CVMCOUNT
NET: Registered protocol family 2
TCP established hash table entries: 2048 (order: 3, 32768 bytes)
TCP bind hash table entries: 2048 (order: 3, 32768 bytes)
TCP: Hash tables configured (established 2048 bind 2048)
TCP: reno registered
UDP hash table entries: 256 (order: 1, 8192 bytes)
UDP-Lite hash table entries: 256 (order: 1, 8192 bytes)
NET: Registered protocol family 1
octeon_pci_console: Console not created.
/proc/octeon_perf: Octeon performance counter interface loaded
NTFS driver 2.1.30 [Flags: R/O].
jffs2: version 2.2. (NAND) © 2001-2006 Red Hat, Inc.
msgmni has been set to 430
alg: No test for stdrng (krng)
Block layer SCSI generic (bsg) driver version 0.4 loaded (major 253)
io scheduler noop registered
io scheduler cfq registered (default)
octeon_gpio 1070000000800.gpio-controller: octeon gpio register base 8001070000000800
octeon_gpio 1070000000800.gpio-controller: OCTEON GPIO
Serial: 8250/16550 driver, 2 ports, IRQ sharing disabled
1180000000800.serial: ttyS0 at MMIO 0x1180000000800 (irq = 34) is a OCTEON
1180000000c00.serial: ttyS1 at MMIO 0x1180000000c00 (irq = 35) is a OCTEON
brd: module loaded
loop: module loaded
slram: not enough parameters.
spi-octeon 1070000001000.spi: octeon spi register base 8001070000001000
octeon_spi_setup cs 0 speed 16000000 mode 00000003 bpw 8 irq 0 cs-gpio 14
SPI: (2) Set TX for chipselect 0 gpio 14
octeon_spi_setup cs 1 speed 16000000 mode 00000003 bpw 8 irq 0 cs-gpio 15
SPI: (2) Set TX for chipselect 1 gpio 15
octeon_spi_setup cs 2 speed 2000000 mode 00000001 bpw 8 irq 0 cs-gpio 16
SPI: (2) Set TX for chipselect 2 gpio 16
octeon_spi_setup cs 3 speed 16000000 mode 00000003 bpw 8 irq 0 cs-gpio 17
SPI: (2) Set TX for chipselect 3 gpio 17
spi-octeon 1070000001000.spi: OCTEON SPI bus driver
mdio-octeon 1180000001800.mdio: octeon mdio register base 8001180000001800
libphy: mdio-octeon: probed
mdio-octeon 1180000001800.mdio: Version 1.0
octeon-ethernet 2.0
Memory range 8000000001400000 - 8000000001990fff reserved for hardware
Memory range 8000000001991000 - 80000000019dbfff reserved for hardware
Memory range 80000000019dc000 - 8000000001a5bfff reserved for hardware
Memory range 8000000001a5c000 - 8000000001a9bfff reserved for hardware
Memory range 8000000001a9c000 - 8000000001ccbfff reserved for hardware
Interface 0 has 3 ports (RGMII)
octeon_mgmt 1070000100000.ethernet: Version 2.0
Octeon POW only ethernet driver
Waiting for another core to setup the IPD hardware...Done
POW acquired message handle 16
ehci_hcd: USB 2.0 'Enhanced' Host Controller (EHCI) Driver
ehci-platform: EHCI generic platform driver
ohci_hcd: USB 1.1 'Open' Host Controller (OHCI) Driver
OcteonUSB 16f0010000000.usbc: Octeon Host Controller
OcteonUSB 16f0010000000.usbc: new USB bus registered, assigned bus number 1
OcteonUSB 16f0010000000.usbc: irq 56, io mem 0x00000000
usb usb1: New USB device found, idVendor=1d6b, idProduct=0002
usb usb1: New USB device strings: Mfr=3, Product=2, SerialNumber=1
usb usb1: Product: Octeon Host Controller
usb usb1: Manufacturer: Linux 3.10.20-rt14 Octeon USB
usb usb1: SerialNumber: 16f0010000000.usbc
hub 1-0:1.0: USB hub found
hub 1-0:1.0: 1 port detected
OcteonUSB: Registered HCD for port 0 on irq 56
usbcore: registered new interface driver usb-storage
i2c /dev entries driver
i2c-octeon 1180000001000.i2c: version 2.5
octeon_wdt: Initial granularity 5 Sec
watchdog: Software Watchdog: cannot register miscdev on minor=130 (err=-16).
watchdog: Software Watchdog: a legacy watchdog module is probably present.
softdog: Software Watchdog Timer: 0.08 initialized. soft_noboot=0 soft_margin=60 sec soft_panic=0 (nowayout=0)
device-mapper: ioctl: 4.24.0-ioctl (2013-01-15) initialised: dm-devel@redhat.com
EDAC DEVICE0: Giving out device to module 'octeon-cpu' controller 'cache': DEV 'octeon_pc_edac' (INTERRUPT)
EDAC DEVICE1: Giving out device to module 'octeon-l2c' controller 'octeon_l2c_err': DEV 'octeon_l2c_edac' (POLLED)
Netfilter messages via NETLINK v0.30.
nf_conntrack version 0.5.0 (1723 buckets, 6892 max)
NF_TPROXY: Transparent proxy support initialized, version 4.1.0
NF_TPROXY: Copyright (c) 2006-2007 BalaBit IT Ltd.
ipip: IPv4 over IPv4 tunneling driver
gre: GRE over IPv4 demultiplexor driver
ip_gre: GRE over IPv4 tunneling driver
ip_tables: (C) 2000-2006 Netfilter Core Team
arp_tables: (C) 2002 David S. Miller
Initializing XFRM netlink socket
NET: Registered protocol family 10
mip6: Mobile IPv6
sit: IPv6 over IPv4 tunneling driver
ip6_gre: GRE over IPv6 tunneling driver
NET: Registered protocol family 17
Bridge firewalling registered
L2 lock: TLB refill 256 bytes
L2 lock: General exception 128 bytes
L2 lock: low-level interrupt 128 bytes
L2 lock: interrupt 640 bytes
L2 lock: memcpy 1152 bytes
Bootbus flash: Setting flash for 32MB flash at 0x1dc00000
phys_mapped_flash: Found 1 x16 devices at 0x0 in 16-bit bank. Manufacturer ID 0x0000c2 Chip ID 0x00227e
Amd/Fujitsu Extended Query Table at 0x0040
  Amd/Fujitsu Extended Query version 1.3.
number of CFI chips: 1
6 cmdlinepart partitions found on MTD device phys_mapped_flash
Creating 6 MTD partitions on "phys_mapped_flash":
0x000000000000-0x000000080000 : "uboot"
0x000000080000-0x000000e80000 : "SWImage0"
0x000000e80000-0x000001c80000 : "SWImage1"
0x000001c80000-0x000001ca0000 : "certs"
0x000001ca0000-0x000001fe0000 : "jffs2"
0x000001fe0000-0x000002000000 : "root"
turn off boot console early0
```

Well poop, it looks like part of the manufacturing process reloads these settings. Lets remove the flash again!