---
title: 'Embedded hardware firmware extraction and analysys: Part 2 MIPS'
date: 2019-02-18
permalink: /posts/2019/02/Indeed_CTF_Embedded_2/
tags:
  - Hardware
  - UART
  - U-Boot
  - MIPS
  - ARM
  - Binary
  - Reverse Engineering
---

MIPS Network Appliance
======

## What we will be seeing today

The victim today is a DPH153-AT, manufactured by Cisco and sold by AT&T as a wireless cell signal booster. The device has some anti tampering features in the form of these pin headers and shunts, some of these shunts are real and some of them are "fake" having no conductive material. The case has plastic fingers that lock into the assembly around the shunts and will rip them off the board and effectivly scatter them if the case is pulled open. When these shunts do not match the original configuration when it was closed in the factory the device will flag itself as having been tampered with and phone home to the mothership when connected. To bypass this I have taken a Chinesium drill bit and used it to mill away the fingers from the case. Inside of the case five main areas can be identified.

![Bad Idea](/images/DPH153-Drill.jpg)
![Plastic Fingers](/images/DPH153-Fingers.jpg)
![Factory Original](/images/DPH153-NotTampered2.jpg)
![Not Tampered](/images/DPH153-NotTampered1.jpg)
![Back of PCB](/images/DPH153-BoardBack.jpg)
![Front of PCB](/images/DPH153-BoardFront.jpg)

### Power:
Converts 12volts DC into 5v, 3.3v, and 1.2v power rails. This isnt an area we are concerned with.

### Cellular radio:
Acts as a small cellular tower transmitter, does have some interesting areas but still not an easy path of attack.

### FPGA+CPU and its own ram and flash memory:
This is extremely interesting, a very powerful processor with connections to the cellular radio. This module is doing the signal processing and heavy math behind the cellular tower, needs more investigation but no obvious points of entry.

### GPS module:
Used by the device to determine precise time and if it is in an area where it is allowed to transmit without interfering with other towers. Has super capacitor for a real time clock and a UART connection that transmits GPS data, interesting but not an easy path of attack.

### Network interconnect:
Lower power MIPS CPU with its own ram and flash memory, has an ethernet chip and low voltage signaling to a switch on a chip and the FPGA module that also connects to the higher voltage external ports. This provides a convenient UART port for us with boot messages! Lets poke at this.

The tool I'm using for the UART interface is a JTAGULATOR, hot pink and ready to kick some ass. [http://www.grandideastudio.com/jtagulator/](http://www.grandideastudio.com/jtagulator/)

![jtagulator](/images/jtagulator.jpg)

The UART has ground, TX, RX, and +3.3v pins. We only really care about ground and the data lines.

![jtagulator UART](/images/jtagulator_UART.jpg)

Wired up and ready to go.

![jtagulator DPH153](/images/jtagulator_DPH153.jpg)

The jtagulator looks like a USB serial adapter and can be configured to act as a UART passthrough.

Watching this boot will just show us some status messages but not drop us to a root shell or a login prompt. The terminal seems to be disabled after Linux boots, lets see what we can do before that happens.

A U-Boot shell for debugging is available, reading some of the messages lets us know where to look in ram for where the flash memory is loaded, on devices like this flash memory is so slow and error prone that it is faster and safer to load everything into a ramdisk.

```
U-Boot 1.1.3 (Jan  7 2009 - 12:26:56)
Board: Ralink APSoC DRAM:  16 MB
relocate_code Pointer at: 80fb0000
flash_protect ON: from 0xBF000000 to 0xBF01EF67
protect on 0
protect on 1
protect on 2
protect on 3
protect on 4
protect on 5
protect on 6
protect on 7
protect on 8
flash_protect ON: from 0xBF020000 to 0xBF02FFFF
protect on 9
============================================ 
Ralink UBoot Version: 3.7.1
-------------------------------------------- 
ASIC 2150_MP2 (MAC to GigaMAC Mode)
DRAM COMPONENT: 128Mbits 
DRAM BUS: 16BIT 
Total memory: 16 MBytes
Date:Jan  7 2009  Time:12:26:56
============================================ 
icache: sets:256, ways:4, linesz:32 ,total:32768
dcache: sets:128, ways:4, linesz:32 ,total:16384 
 ##### The CPU freq = 384 MHZ #### 
SDRAM bus set to 16 bit 
 SDRAM size =16 Mbytes
Please choose the operation: 
   1: Load system code to SDRAM via TFTP. 
   2: Load system code then write to Flash via TFTP. 
   3: Boot system code via Flash (default).
   4: Entr boot command line interface.
   9: Load Boot Loader code then write to Flash via TFTP. 
You choosed 4
Net:   
 eth_register  
Eth0 (10/100-M)
 enetvar=ethaddr,Eth addr:00:AA:BB:CC:DD:18
 00:AA:BB:CC:DD:18:
 eth_current->name = Eth0 (10/100-M)
4: System Enter Boot Command Line Interface.
U-Boot 1.1.3 (Jan  7 2009 - 12:26:56)
 main_loop !! 
 In main_loop !! 
 CONFIG_BOOTDELAY 
### main_loop entered: bootdelay=3
### main_loop: bootcmd="tftp"
RT2150 # ? md
md [.b, .w, .l] address [# of objects]
    - memory display
RT2150 # md.b 0xBF000000 16777216
bf000000: ff 00 00 10 00 00 00 00 fd 00 00 10 00 00 00 00    ................
bf000010: 19 02 00 10 00 00 00 00 17 02 00 10 00 00 00 00    ................
bf000020: 15 02 00 10 00 00 00 00 13 02 00 10 00 00 00 00    ................
bf000030: 11 02 00 10 00 00 00 00 0f 02 00 10 00 00 00 00    ................
bf000040: 0d 02 00 10 00 00 00 00 0b 02 00 10 00 00 00 00    ................
bf000050: 09 02 00 10 00 00 00 00 07 02 00 10 00 00 00 00    ................
bf000060: 05 02 00 10 00 00 00 00 03 02 00 10 00 00 00 00    ................
bf000070: 01 02 00 10 00 00 00 00 ff 01 00 10 00 00 00 00    ................
bf000080: fd 01 00 10 00 00 00 00 fb 01 00 10 00 00 00 00    ................
bf000090: f9 01 00 10 00 00 00 00 f7 01 00 10 00 00 00 00    ................
bf0000a0: f5 01 00 10 00 00 00 00 f3 01 00 10 00 00 00 00    ................
bf0000b0: f1 01 00 10 00 00 00 00 ef 01 00 10 00 00 00 00    ................
bf0000c0: ed 01 00 10 00 00 00 00 eb 01 00 10 00 00 00 00    ................
bf0000d0: e9 01 00 10 00 00 00 00 e7 01 00 10 00 00 00 00    ................
bf0000e0: e5 01 00 10 00 00 00 00 e3 01 00 10 00 00 00 00    ................
bf0000f0: e1 01 00 10 00 00 00 00 df 01 00 10 00 00 00 00    ................
bf000100: dd 01 00 10 00 00 00 00 db 01 00 10 00 00 00 00    ................
bf000110: d9 01 00 10 00 00 00 00 d7 01 00 10 00 00 00 00    ................
bf000120: d5 01 00 10 00 00 00 00 d3 01 00 10 00 00 00 00    ................
bf000130: d1 01 00 10 00 00 00 00 cf 01 00 10 00 00 00 00    ................
bf000140: cd 01 00 10 00 00 00 00 cb 01 00 10 00 00 00 00    ................
bf000150: c9 01 00 10 00 00 00 00 c7 01 00 10 00 00 00 00    ................
bf000160: c5 01 00 10 00 00 00 00 c3 01 00 10 00 00 00 00    ................
bf000170: c1 01 00 10 00 00 00 00 bf 01 00 10 00 00 00 00    ................
bf000180: bd 01 00 10 00 00 00 00 bb 01 00 10 00 00 00 00    ................
bf000190: b9 01 00 10 00 00 00 00 b7 01 00 10 00 00 00 00    ................
bf0001a0: b5 01 00 10 00 00 00 00 b3 01 00 10 00 00 00 00    ................
bf0001b0: b1 01 00 10 00 00 00 00 af 01 00 10 00 00 00 00    ................
bf0001c0: ad 01 00 10 00 00 00 00 ab 01 00 10 00 00 00 00    ................
bf0001d0: a9 01 00 10 00 00 00 00 a7 01 00 10 00 00 00 00    ................
bf0001e0: a5 01 00 10 00 00 00 00 a3 01 00 10 00 00 00 00    ................
```

# LIVE DEMO!!!!1

With this running overnight we can record the output and use an awesome tool to process the output.

```
python3 ~/uboot-mdb-dump/uboot_mdb_to_image.py < dumpflash_mdb.txt > dumpflash.bin
```

Our resulting file can be run through binwalk to get some useful information, keep in mind that this will return some false positive matches on files magic bytes. Moving to extraction will give us multiple Linux filesystems and more.

```
binwalk dumpflash.bin -Mre
```

```
ls -laht _dumpflash.bin.extracted/_E20040.extracted/_2C5000.extracted/cpio-root/
total 60K
drwxr-xr-x 15 rjmendez rjmendez 4.0K Feb 10 02:53 .
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 10 02:53 bin
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 10 02:53 sys
drwxr-xr-x  4 rjmendez rjmendez 4.0K Feb 10 02:53 dev
drwxr-xr-x  5 rjmendez rjmendez 4.0K Feb 10 02:53 etc
drwxr-xr-x  3 rjmendez rjmendez 4.0K Feb 10 02:53 etc_ro
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 10 02:53 home
drwxr-xr-x  3 rjmendez rjmendez 4.0K Feb 10 02:53 lib
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 10 02:53 sbin
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 10 02:53 tmp
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 10 02:53 mnt
drwxr-xr-x  4 rjmendez rjmendez 4.0K Feb 10 02:53 usr
drwxr-xr-x  3 rjmendez rjmendez 4.0K Feb 10 02:53 ..
lrwxrwxrwx  1 rjmendez rjmendez   11 Feb 10 02:53 init -> bin/busybox
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 10 02:53 proc
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 10 02:53 var
```

We can run these binaries with proot.

```
proot -q "qemu-mipsel" -S cpio-root /usr/sbin/ipc_server
```

In a second window run the following and observe the output.

```
proot -q "qemu-mipsel" -S cpio-root /usr/sbin/ipc_client
ipc_client ip command
command list: reset factory_reset tamper download_finished
```

In yet another window run the following.

```
sudo tcpdump -Xni lo port 3001
```

Then in the previous window run the client tamper command.

```
proot -q "qemu-mipsel" -S ../cpio-root /usr/sbin/ipc_client 127.0.0.1 tamper
[IPC]The response: 81
```

Observe the resulting network traffic.

```
23:04:08.935497 IP 127.0.0.1.52124 > 127.0.0.1.3001: Flags [P.], seq 1:138, ack 1, win 342, options [nop,nop,TS val 40852168 ecr 40852168], length 137
    0x0000:  4500 00bd 8460 4000 4006 b7d8 7f00 0001  E....`@.@.......
    0x0010:  7f00 0001 cb9c 0bb9 49e0 de97 3d76 d0ac  ........I...=v..
    0x0020:  8018 0156 feb1 0000 0101 080a 026f 5ac8  ...V.........oZ.
    0x0030:  026f 5ac8 0800 0000 0000 0000 0000 0000  .oZ.............
    0x0040:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x0050:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x0060:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x0070:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x0080:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x0090:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x00a0:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x00b0:  0000 0000 0000 0000 0000 0000 00         .............
23:04:08.935506 IP 127.0.0.1.3001 > 127.0.0.1.52124: Flags [.], ack 138, win 350, options [nop,nop,TS val 40852168 ecr 40852168], length 0
    0x0000:  4500 0034 8a64 4000 4006 b25d 7f00 0001  E..4.d@.@..]....
    0x0010:  7f00 0001 0bb9 cb9c 3d76 d0ac 49e0 df20  ........=v..I...
    0x0020:  8010 015e fe28 0000 0101 080a 026f 5ac8  ...^.(.......oZ.
    0x0030:  026f 5ac8                                .oZ.
23:04:08.935665 IP 127.0.0.1.3001 > 127.0.0.1.52124: Flags [P.], seq 1:170, ack 138, win 350, options [nop,nop,TS val 40852168 ecr 40852168], length 169
    0x0000:  4500 00dd 8a65 4000 4006 b1b3 7f00 0001  E....e@.@.......
    0x0010:  7f00 0001 0bb9 cb9c 3d76 d0ac 49e0 df20  ........=v..I...
    0x0020:  8018 015e fed1 0000 0101 080a 026f 5ac8  ...^.........oZ.
    0x0030:  026f 5ac8 8100 0000 0000 0000 0000 0000  .oZ.............
    0x0040:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x0050:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x0060:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x0070:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x0080:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x0090:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x00a0:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x00b0:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x00c0:  0000 0000 0000 0000 0000 0000 0000 0000  ................
    0x00d0:  0000 0000 0000 0000 0000 0000 00         .............
```

However there is a problem, the server does not recognize the command!

```
[IPC]cmd_dispatch(662): Unknown request type(8)
```

Instead of using the client try this command instead.

```
cat <(python3 -c "import sys; sys.stdout.write('\x08'+'\x00'*136)") | ncat 127.0.0.1 3001 | hd
00000000  81 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
000000a9
```

## Question: What is the value that will trigger a tamper reset?

Open the ipc_server binary with radare2 and examine its strings with izz.

```
radare2 usr/sbin/ipc_server 
 -- Sharing your latest session to Facebook ...
[0x00400a40]> izz
[Strings]
Num Paddr      Vaddr      Len Size Section  Type  String
000 0x000000f4 0x004000f4  19  20 (.interp) ascii /lib/ld-uClibc.so.0
001 0x000001ae 0x004001ae   4  10 (.dynamic) utf16le @\n瀀\b blocks=Basic Latin,CJK Unified Ideographs
002 0x00000248 0x00400248   6  28 (.hash) utf32le \r4\a#,\v
003 0x00000310 0x00400310   4  20 (.hash) utf32le :%.&
004 0x00000789 0x00400789   5   6 (.dynstr) ascii _fini
005 0x0000078f 0x0040078f  13  14 (.dynstr) ascii __uClibc_main
006 0x0000079d 0x0040079d  23  24 (.dynstr) ascii __deregister_frame_info
007 0x000007b5 0x004007b5  21  22 (.dynstr) ascii __register_frame_info
008 0x000007cb 0x004007cb  19  20 (.dynstr) ascii _Jv_RegisterClasses
009 0x000007df 0x004007df  14  15 (.dynstr) ascii libshared.so.0
010 0x000007ee 0x004007ee  16  17 (.dynstr) ascii _DYNAMIC_LINKING
011 0x000007ff 0x004007ff   9  10 (.dynstr) ascii __RLD_MAP
012 0x00000809 0x00400809  21  22 (.dynstr) ascii _GLOBAL_OFFSET_TABLE_
013 0x0000081f 0x0040081f   4   5 (.dynstr) ascii fork
014 0x00000824 0x00400824   7   8 (.dynstr) ascii waitpid
015 0x0000082c 0x0040082c   6   7 (.dynstr) ascii setsid
016 0x00000833 0x00400833   4   5 (.dynstr) ascii exit
017 0x00000838 0x00400838   6   7 (.dynstr) ascii evalsh
018 0x0000083f 0x0040083f   6   7 (.dynstr) ascii memset
019 0x00000846 0x00400846   6   7 (.dynstr) ascii strlen
020 0x0000084d 0x0040084d  10  11 (.dynstr) ascii backticksh
021 0x00000858 0x00400858   8   9 (.dynstr) ascii isIntStr
022 0x00000861 0x00400861   6   7 (.dynstr) ascii strstr
023 0x00000868 0x00400868  12  13 (.dynstr) ascii _eval_nowait
024 0x00000875 0x00400875   7   8 (.dynstr) ascii strncpy
025 0x0000087d 0x0040087d   6   7 (.dynstr) ascii signal
026 0x00000884 0x00400884   5   6 (.dynstr) ascii close
027 0x0000088a 0x0040088a   6   7 (.dynstr) ascii perror
028 0x00000891 0x00400891   9  10 (.dynstr) ascii log_level
029 0x0000089b 0x0040089b   6   7 (.dynstr) ascii printf
030 0x000008a2 0x004008a2   5   6 (.dynstr) ascii chdir
031 0x000008a8 0x004008a8   5   6 (.dynstr) ascii umask
032 0x000008ae 0x004008ae   6   7 (.dynstr) ascii memcmp
033 0x000008b5 0x004008b5   7   8 (.dynstr) ascii isdigit
034 0x000008bd 0x004008bd   4   5 (.dynstr) ascii atoi
035 0x000008c2 0x004008c2   4   5 (.dynstr) ascii free
036 0x000008c7 0x004008c7  12  13 (.dynstr) ascii fork_process
037 0x000008d4 0x004008d4   5   6 (.dynstr) ascii sleep
038 0x000008da 0x004008da   6   7 (.dynstr) ascii strdup
039 0x000008e1 0x004008e1   6   7 (.dynstr) ascii sscanf
040 0x000008e8 0x004008e8   6   7 (.dynstr) ascii malloc
041 0x000008ef 0x004008ef   6   7 (.dynstr) ascii strcpy
042 0x000008f6 0x004008f6  11  12 (.dynstr) ascii daemon_init
043 0x00000902 0x00400902   6   7 (.dynstr) ascii socket
044 0x00000909 0x00400909  10  11 (.dynstr) ascii setsockopt
045 0x00000914 0x00400914   4   5 (.dynstr) ascii bind
046 0x00000919 0x00400919   6   7 (.dynstr) ascii listen
047 0x00000920 0x00400920   6   7 (.dynstr) ascii accept
048 0x00000927 0x00400927  14  15 (.dynstr) ascii read_from_peer
049 0x00000936 0x00400936  12  13 (.dynstr) ascii cmd_dispatch
050 0x00000943 0x00400943  13  14 (.dynstr) ascii write_to_peer
051 0x00000951 0x00400951   9  10 (.dynstr) ascii inet_addr
052 0x0000095b 0x0040095b   6   7 (.dynstr) ascii select
053 0x00000962 0x00400962   4   5 (.dynstr) ascii read
054 0x00000967 0x00400967   4   5 (.dynstr) ascii puts
055 0x0000096c 0x0040096c   4   5 (.dynstr) ascii time
056 0x00000971 0x00400971   4   5 (.dynstr) ascii send
057 0x00000976 0x00400976   7   8 (.dynstr) ascii connect
058 0x0000097e 0x0040097e   9  10 (.dynstr) ascii libc.so.0
059 0x00000988 0x00400988   6   7 (.dynstr) ascii _ftext
060 0x0000098f 0x0040098f   6   7 (.dynstr) ascii _fdata
061 0x0000099a 0x0040099a   6   7 (.dynstr) ascii _edata
062 0x000009a1 0x004009a1  11  12 (.dynstr) ascii __bss_start
063 0x000009ad 0x004009ad   5   6 (.dynstr) ascii _fbss
064 0x000009b3 0x004009b3   4   5 (.dynstr) ascii _end
065 0x000009f1 0x004009f1   4   5 (.init) ascii \v9'\t
066 0x00000a21 0x00400a21   4   5 (.init) ascii A9'\t
067 0x00000aa3 0x00400aa3   5   7 (.text)  utf8 <0Μ'! blocks=Basic Latin,Greek and Coptic
068 0x00000bab 0x00400bab   5   7 (.text)  utf8 <(͜'! blocks=Basic Latin,Combining Diacritical Marks
069 0x00000c63 0x00400c63   5   7 (.text)  utf8 <p̜'! blocks=Basic Latin,Combining Diacritical Marks
070 0x0000107b 0x0040107b   5   7 (.text)  utf8 <XȜ'! blocks=Basic Latin,Latin Extended-B
071 0x0000121f 0x0040121f   4   5 (.text) ascii $! @
072 0x000014ff 0x004014ff   4   5 (.text) ascii $!8@
073 0x00001577 0x00401577   5   7 (.text)  utf8 <\Ü'! blocks=Basic Latin,Latin-1 Supplement
074 0x0000168a 0x0040168a   7  16 (.text) utf16le `\bϠh➽耜辄 blocks=Basic Latin,Greek and Coptic,Dingbats,CJK Unified Ideographs
075 0x00001796 0x00401796   5   6 (.text) ascii s&!  
076 0x00001e75 0x00401e75   4   5 (.text) ascii XB$\b
077 0x00001e85 0x00401e85   4   5 (.text) ascii Xc$\f
078 0x000021ee 0x004021ee   5   6 (.text) ascii D&!(@
079 0x0000220e 0x0040220e   4   5 (.text) ascii D&!(
080 0x0000222e 0x0040222e   4   5 (.text) ascii D&!(
081 0x000024eb 0x004024eb   4   7 (.text)  utf8 <賜'! blocks=Basic Latin,CJK Unified Ideographs
082 0x000026e6 0x004026e6   4   5 (.text) ascii c0%8
083 0x00002a0e 0x00402a0e   5   6 (.text) ascii B$! @
084 0x00002b47 0x00402b47   4   5 (.text) ascii &!  
085 0x00002b7b 0x00402b7b   4   5 (.text) ascii &! @
086 0x00002be3 0x00402be3   4   5 (.text) ascii &! `
087 0x00002c23 0x00402c23   4   5 (.text) ascii $!( 
088 0x00002ecf 0x00402ecf   4   5 (.text) ascii <$(R
089 0x00002f43 0x00402f43   4   5 (.text) ascii <! @
090 0x000033bc 0x004033bc   5   6 (.text) ascii hVc$!
091 0x00003478 0x00403478   4   5 (.text) ascii \!9'
092 0x000034d0 0x004034d0   4   5 (.text) ascii x-9'
093 0x000034fc 0x004034fc   4   5 (.text) ascii p29'
094 0x00003608 0x00403608   4   5 (.text) ascii x#9'
095 0x00003660 0x00403660   4   5 (.text) ascii 0)9'
096 0x0000377a 0x0040377a   6  14 (.text) utf16le `\bϠ ➽‡ blocks=Basic Latin,Greek and Coptic,Dingbats,General Punctuation
097 0x00003853 0x00403853   4   5 (.text) ascii 4!  
098 0x000038a3 0x004038a3   4   5 (.text) ascii '!  
099 0x000038e7 0x004038e7   4   5 (.text) ascii '!  
100 0x00003933 0x00403933   4   5 (.text) ascii $! @
101 0x00003a1f 0x00403a1f   4   5 (.text) ascii $! `
102 0x00003e3f 0x00403e3f   4   5 (.text) ascii '! @
103 0x00003eea 0x00403eea   5  12 (.text) utf16le `\bϠǘ➽ blocks=Basic Latin,Greek and Coptic,Latin Extended-B,Dingbats
104 0x00003ffa 0x00403ffa   4  10 (.text) utf16le @\tᡀ‡ blocks=Basic Latin,Mongolian,General Punctuation
105 0x0000416e 0x0040416e   7  16 (.text) utf16le `\bϠ@➽耸辙 blocks=Basic Latin,Greek and Coptic,Dingbats,CJK Unified Ideographs
106 0x000041dc 0x004041dc   4   5 (.text) ascii xXc$
107 0x00004519 0x00404519   4   5 (.fini) ascii \n9'\t
108 0x00004540 0x00404540  29  30 (.rodata) ascii [IPC]%s(%d): waitpid fail...\n
109 0x00004560 0x00404560  12  13 (.rodata) ascii fork_process
110 0x00004574 0x00404574  26  27 (.rodata) ascii [IPC]%s(%d): fork fail...\n
111 0x00004590 0x00404590  47  48 (.rodata) ascii [IPC]%s(%d): Receive change_log_level CMD ... \n
112 0x000045c0 0x004045c0  20  21 (.rodata) ascii cmd_change_log_level
113 0x000045d8 0x004045d8  41  42 (.rodata) ascii [IPC]%s(%d): Receive reboot_now CMD ... \n
114 0x00004604 0x00404604  14  15 (.rodata) ascii cmd_reboot_now
115 0x00004614 0x00404614  26  27 (.rodata) ascii killall -SIGUSR1 gpio_task
116 0x00004630 0x00404630  44  45 (.rodata) ascii [IPC]%s(%d): Receive factory_reset CMD ... \n
117 0x00004660 0x00404660  17  18 (.rodata) ascii cmd_factory_reset
118 0x00004674 0x00404674  26  27 (.rodata) ascii killall -SIGUSR2 gpio_task
119 0x00004690 0x00404690  45  46 (.rodata) ascii [IPC]%s(%d): Receive switch_boot_fw CMD ... \n
120 0x000046c0 0x004046c0  18  19 (.rodata) ascii cmd_switch_fw_boot
121 0x000046d4 0x004046d4  14  15 (.rodata) ascii change_boot.sh
122 0x000046e4 0x004046e4   6   7 (.rodata) ascii image-
123 0x000046ec 0x004046ec   7   8 (.rodata) ascii router-
124 0x000046f4 0x004046f4  87  88 (.rodata) ascii [IPC]%s(%d): more than two ".". We only need to collect 3 integers between first 2 "."\n
125 0x0000474c 0x0040474c  13  14 (.rodata) ascii strip_version
126 0x0000475c 0x0040475c  38  39 (.rodata) ascii [IPC]%s(%d): index:%d buf:%s value:%d\n
127 0x00004784 0x00404784  53  54 (.rodata) ascii [IPC]%s(%d): less than two ".". The format is error.\n
128 0x000047bc 0x004047bc  26  27 (.rodata) ascii [IPC]%s(%d): input url:%s\n
129 0x000047d8 0x004047d8  32  33 (.rodata) ascii [IPC]%s(%d): input url error:%s\n
130 0x00004804 0x00404804  44  45 (.rodata) ascii ipc_client 192.168.157.186 download_finished
131 0x00004834 0x00404834  30  31 (.rodata) ascii cs_client get sys/upgradefw_on
132 0x00004854 0x00404854  64  65 (.rodata) ascii [IPC]%s(%d): memory fail after 'cs_client get sys/upgradefw_on'\n
133 0x00004898 0x00404898  24  25 (.rodata) ascii cmd_do_software_download
134 0x000048b4 0x004048b4  26  27 (.rodata) ascii cs_client get sys/boot_loc
135 0x000048d0 0x004048d0  60  61 (.rodata) ascii [IPC]%s(%d): memory fail after 'cs_client get sys/boot_loc'\n
136 0x00004910 0x00404910  93  94 (.rodata) ascii [IPC]%s(%d): strlen(c_req->do_software_download.sw_dld_uri) (%d)is larger than defination(%d)
137 0x00004970 0x00404970  29  30 (.rodata) ascii cs_client get switch/mii_pins
138 0x00004990 0x00404990  63  64 (.rodata) ascii [IPC]%s(%d): memory fail after 'cs_client get switch/mii_pins'\n
139 0x000049d0 0x004049d0  86  87 (.rodata) ascii [IPC]%s(%d): The filename is not valid, no image- or router- as prefix. sw_dld_uri:%s\n
140 0x00004a28 0x00404a28  89  90 (.rodata) ascii [IPC]%s(%d): The firmware version is lower than 1.0.31, forbid to upgrade. sw_dld_uri:%s\n
141 0x00004a84 0x00404a84  26  27 (.rodata) ascii cs_client get sys/swdirurl
142 0x00004aa0 0x00404aa0  32  33 (.rodata) ascii cs_client get sys/fw/%d/swdirurl
143 0x00004ac4 0x00404ac4  29  30 (.rodata) ascii cs_client set sys/swdirurl %s
144 0x00004ae4 0x00404ae4  32  33 (.rodata) ascii cs_client set sys/do_upgradefw 1
145 0x00004b08 0x00404b08  27  28 (.rodata) ascii cs_client get sys/fw_status
146 0x00004b24 0x00404b24   9  10 (.rodata) ascii Completed
147 0x00004b30 0x00404b30  10  11 (.rodata) ascii InProgress
148 0x00004b3c 0x00404b3c  41  42 (.rodata) ascii [IPC]%s(%d): Upload firmware InProgress \n
149 0x00004b68 0x00404b68  35  36 (.rodata) ascii cs_client set sys/fw/%d/swdirurl %s
150 0x00004b8c 0x00404b8c  54  55 (.rodata) ascii [IPC]%s(%d): Upload firmware fail! Take too much time\n
151 0x00004bc4 0x00404bc4  36  37 (.rodata) ascii [IPC]%s(%d): Upload firmware fail! \n
152 0x00004bec 0x00404bec  32  33 (.rodata) ascii cs_client set sys/fw_status Idle
153 0x00004c10 0x00404c10  40  41 (.rodata) ascii [IPC]%s(%d): Upload firmware Completed \n
154 0x00004c3c 0x00404c3c  54  55 (.rodata) ascii [IPC]%s(%d): memory fail. cs_client get sys/fw_status\n
155 0x00004c74 0x00404c74  57  58 (.rodata) ascii [IPC]%s(%d): The firmware is the same, skip this upgrade\n
156 0x00004cb0 0x00404cb0  58  59 (.rodata) ascii [IPC]%s(%d): Uploading firmware, Please wait.............\n
157 0x00004cec 0x00404cec  85  86 (.rodata) ascii [IPC]%s(%d): The firmware version is same as 1.1.0, forbid to upgrade. sw_dld_uri:%s\n
158 0x00004d44 0x00404d44  51  52 (.rodata) ascii [IPC]%s(%d): Receive do_software_download CMD ... \n
159 0x00004d78 0x00404d78  16  17 (.rodata) ascii cs_client commit
160 0x00004d8c 0x00404d8c  23  24 (.rodata) ascii cmd_get_software_status
161 0x00004da4 0x00404da4  53  54 (.rodata) ascii [IPC]%s(%d): memory fail. cs_client get sys/swdirurl\n
162 0x00004ddc 0x00404ddc  50  51 (.rodata) ascii [IPC]%s(%d): Receive get_software_status CMD ... \n
163 0x00004e10 0x00404e10  45  46 (.rodata) ascii [IPC]%s(%d): Receive cmd_get_uptime CMD ... \n
164 0x00004e40 0x00404e40  14  15 (.rodata) ascii cmd_get_uptime
165 0x00004e50 0x00404e50  16  17 (.rodata) ascii cat /proc/uptime
166 0x00004e64 0x00404e64  20  21 (.rodata) ascii %lu.%02lu %lu.%02lu\n
167 0x00004e7c 0x00404e7c  43  44 (.rodata) ascii [IPC]%s(%d): memory fail. cat /proc/uptime\n
168 0x00004ea8 0x00404ea8  15  16 (.rodata) ascii cmd_set_telnetd
169 0x00004eb8 0x00404eb8  42  43 (.rodata) ascii [IPC]%s(%d): Receive set_telnetd CMD ... \n
170 0x00004ee4 0x00404ee4  29  30 (.rodata) ascii cs_client set wizard/remove 1
171 0x00004f04 0x00404f04  29  30 (.rodata) ascii cs_client set wizard/enable 1
172 0x00004f24 0x00404f24  29  30 (.rodata) ascii cs_client set wizard/enable 0
173 0x00004f44 0x00404f44  40  41 (.rodata) ascii [IPC]%s(%d): Receive sleep %ds CMD ... \n
174 0x00004f70 0x00404f70   9  10 (.rodata) ascii cmd_sleep
175 0x00004f7c 0x00404f7c  36  37 (.rodata) ascii [IPC]%s(%d): Receive crash CMD ... \n
176 0x00004fa4 0x00404fa4   9  10 (.rodata) ascii cmd_crash
177 0x00004fb8 0x00404fb8  58  59 (.rodata) ascii cs_client set firewall/pf/add_rule "%s %d 192.168.157.186"
178 0x00004ff4 0x00404ff4  58  59 (.rodata) ascii cs_client set firewall/pf/del_rule "%s %d 192.168.157.186"
179 0x00005030 0x00405030   4   5 (.rodata) ascii both
180 0x00005038 0x00405038  16  17 (.rodata) ascii cmd_set_port_fwd
181 0x0000504c 0x0040504c  14  15 (.rodata) ascii cmd_set_cs_cmd
182 0x0000505c 0x0040505c  37  38 (.rodata) ascii [IPC]%s(%d): Receive set_cs CMD ... \n
183 0x00005084 0x00405084  29  30 (.rodata) ascii [IPC]%s(%d): Receive cmd: %s\n
184 0x000050a4 0x004050a4  76  77 (.rodata) ascii strlen(c_req->set_bandwidth.us_bw_wan) (%d) is larger than definitation(%d)\n
185 0x000050f4 0x004050f4  82  83 (.rodata) ascii strlen(c_req->set_bandwidth.bw_measure_addr) (%d) is larger than definitation(%d)\n
186 0x00005148 0x00405148  85  86 (.rodata) ascii strlen(c_req->set_bandwidth.us_bw_measure_freq) (%d) is larger than definitation(%d)\n
187 0x000051a0 0x004051a0  75  76 (.rodata) ascii strlen(c_req->set_bandwidth.us_bw_ap) (%d) is larger than definitation(%d)\n
188 0x000051ec 0x004051ec  34  35 (.rodata) ascii cs_client set qos/set/us_bw_wan %s
189 0x00005214 0x00405214  40  41 (.rodata) ascii cs_client set qos/set/bw_measure_addr %s
190 0x00005240 0x00405240  43  44 (.rodata) ascii cs_client set qos/set/us_bw_measure_freq %s
191 0x0000526c 0x0040526c  33  34 (.rodata) ascii cs_client set qos/set/us_bw_ap %s
192 0x00005290 0x00405290  44  45 (.rodata) ascii [IPC]%s(%d): Receive set_bandwidth CMD ... \n
193 0x000052c0 0x004052c0  17  18 (.rodata) ascii cmd_set_bandwidth
194 0x000052d4 0x004052d4  31  32 (.rodata) ascii cs_client get qos/get/us_bw_wan
195 0x000052f4 0x004052f4  46  47 (.rodata) ascii cs_client get qos/get/us_bw_wan_measure_status
196 0x00005324 0x00405324  45  46 (.rodata) ascii cs_client get qos/get/us_bw_wan_last_measured
197 0x00005354 0x00405354  40  41 (.rodata) ascii cs_client get qos/get/us_bw_wan_measured
198 0x00005380 0x00405380  30  31 (.rodata) ascii cs_client get qos/get/us_bw_ap
199 0x000053a0 0x004053a0  39  40 (.rodata) ascii cs_client get qos/get/us_bw_ap_measured
200 0x000053c8 0x004053c8  65  66 (.rodata) ascii [IPC]%s(%d): memory fail.cs_client get qos/get/us_bw_ap_measured\n
201 0x0000540c 0x0040540c  17  18 (.rodata) ascii cmd_get_bandwidth
202 0x00005420 0x00405420  57  58 (.rodata) ascii [IPC]%s(%d): memory fail. cs_client get qos/get/us_bw_ap\n
203 0x0000545c 0x0040545c  67  68 (.rodata) ascii [IPC]%s(%d): memory fail. cs_client get qos/get/us_bw_wan_measured\n
204 0x000054a0 0x004054a0  72  73 (.rodata) ascii [IPC]%s(%d): memory fail. cs_client get qos/get/us_bw_wan_last_measured\n
205 0x000054ec 0x004054ec  74  75 (.rodata) ascii [IPC]%s(%d): memory fail. cs_client get qos/get/us_bw_wan_measure_status.\n
206 0x00005538 0x00405538  58  59 (.rodata) ascii [IPC]%s(%d): memory fail. cs_client get qos/get/us_bw_wan\n
207 0x00005574 0x00405574  44  45 (.rodata) ascii [IPC]%s(%d): Receive get_bandwidth CMD ... \n
208 0x000055a4 0x004055a4  50  51 (.rodata) ascii [IPC]%s(%d): Receive clear_device_tamper CMD ... \n
209 0x000055d8 0x004055d8  23  24 (.rodata) ascii cmd_clear_device_tamper
210 0x000055f0 0x004055f0  32  33 (.rodata) ascii cs_client set sys/learn_tamper 1
211 0x00005614 0x00405614  38  39 (.rodata) ascii [IPC]%s(%d): Unknown request type(%x)\n
212 0x0000563c 0x0040563c  12  13 (.rodata) ascii cmd_dispatch
213 0x0000564c 0x0040564c  25  26 (.rodata) ascii [IPC]%s(%d): Request %x \n
214 0x000056ac 0x004056ac  21  22 (.rodata) ascii opening stream socket
215 0x000056c4 0x004056c4  45  46 (.rodata) ascii sock_socket: failed setsockopt(SO_REUSEADDR)\n
216 0x000056f4 0x004056f4  48  49 (.rodata) ascii [IPC]%s(%d): Can't read request head from peer \n
217 0x00005728 0x00405728   4   5 (.rodata) ascii main
218 0x00005730 0x00405730  68  69 (.rodata) ascii [IPC]%s(%d): Can't alloc buffer for this request, drop this request.
219 0x00005778 0x00405778  48  49 (.rodata) ascii [IPC]%s(%d): Can't read request data from peer \n
220 0x000057ac 0x004057ac  28  29 (.rodata) ascii [IPC]%s(%d): accept error!\n 
221 0x000057cc 0x004057cc  42  43 (.rodata) ascii [IPC]%s(%d): A connection is established.\n
222 0x000057f8 0x004057f8  21  22 (.rodata) ascii binding stream socket
223 0x00005810 0x00405810  21  22 (.rodata) ascii Error occur in select
224 0x00005828 0x00405828  14  15 (.rodata) ascii Timeout occur.
225 0x00005838 0x00405838  20  21 (.rodata) ascii Unexpect Error occur
226 0x00005850 0x00405850  18  19 (.rodata) ascii failed ipc connect
227 0x00005d31 0x00000001   9  10 (.shstrtab) ascii .shstrtab
228 0x00005d3b 0x0000000b   7   8 (.shstrtab) ascii .interp
229 0x00005d43 0x00000013   8   9 (.shstrtab) ascii .reginfo
230 0x00005d4c 0x0000001c   8   9 (.shstrtab) ascii .dynamic
231 0x00005d55 0x00000025   5   6 (.shstrtab) ascii .hash
232 0x00005d5b 0x0000002b   7   8 (.shstrtab) ascii .dynsym
233 0x00005d63 0x00000033   7   8 (.shstrtab) ascii .dynstr
234 0x00005d6b 0x0000003b   5   6 (.shstrtab) ascii .init
235 0x00005d71 0x00000041   5   6 (.shstrtab) ascii .text
236 0x00005d77 0x00000047  11  12 (.shstrtab) ascii .MIPS.stubs
237 0x00005d83 0x00000053   5   6 (.shstrtab) ascii .fini
238 0x00005d89 0x00000059   7   8 (.shstrtab) ascii .rodata
239 0x00005d91 0x00000061   9  10 (.shstrtab) ascii .eh_frame
240 0x00005d9b 0x0000006b   6   7 (.shstrtab) ascii .ctors
241 0x00005da2 0x00000072   6   7 (.shstrtab) ascii .dtors
242 0x00005da9 0x00000079   4   5 (.shstrtab) ascii .jcr
243 0x00005dae 0x0000007e   5   6 (.shstrtab) ascii .data
244 0x00005db4 0x00000084   8   9 (.shstrtab) ascii .rld_map
245 0x00005dbd 0x0000008d   4   5 (.shstrtab) ascii .got
246 0x00005dc2 0x00000092   4   5 (.shstrtab) ascii .bss
247 0x00005dc7 0x00000097   4   5 (.shstrtab) ascii .pdr
```

If you poked at the TCP values you may have seen some of these, what the hell is this wizard doing though? Lets do the same thing on the /bin/wizard binary to see what its messages are.

```
radare2 bin/wizard 
 -- Virtual machines are great, but you lose the ability to kick the hardware.
[0x004008d0]> izz
[Strings]
Num Paddr      Vaddr      Len Size Section  Type  String
000 0x000000f4 0x004000f4  19  20 (.interp) ascii /lib/ld-uClibc.so.0
001 0x000001b6 0x004001b6   4  10 (.dynamic) utf16le @\n瀀\b blocks=Basic Latin,CJK Unified Ideographs
002 0x00000679 0x00400679   5   6 (.dynstr) ascii _fini
003 0x0000067f 0x0040067f  13  14 (.dynstr) ascii __uClibc_main
004 0x0000068d 0x0040068d  23  24 (.dynstr) ascii __deregister_frame_info
005 0x000006a5 0x004006a5  21  22 (.dynstr) ascii __register_frame_info
006 0x000006bb 0x004006bb  19  20 (.dynstr) ascii _Jv_RegisterClasses
007 0x000006cf 0x004006cf   4   5 (.dynstr) ascii fork
008 0x000006d4 0x004006d4   6   7 (.dynstr) ascii setsid
009 0x000006db 0x004006db   5   6 (.dynstr) ascii chdir
010 0x000006e1 0x004006e1   5   6 (.dynstr) ascii umask
011 0x000006e7 0x004006e7   4   5 (.dynstr) ascii exit
012 0x000006ec 0x004006ec  10  11 (.dynstr) ascii backticksh
013 0x000006f7 0x004006f7   6   7 (.dynstr) ascii sscanf
014 0x000006fe 0x004006fe   4   5 (.dynstr) ascii free
015 0x00000703 0x00400703   6   7 (.dynstr) ascii memset
016 0x0000070a 0x0040070a   6   7 (.dynstr) ascii strlen
017 0x00000711 0x00400711   6   7 (.dynstr) ascii memcpy
018 0x00000718 0x00400718   4   5 (.dynstr) ascii atoi
019 0x0000071d 0x0040071d   6   7 (.dynstr) ascii strcpy
020 0x00000724 0x00400724   7   8 (.dynstr) ascii sprintf
021 0x0000072c 0x0040072c   9  10 (.dynstr) ascii server_fd
022 0x00000736 0x00400736   6   7 (.dynstr) ascii sendto
023 0x0000073d 0x0040073d   6   7 (.dynstr) ascii evalsh
024 0x00000744 0x00400744   9  10 (.dynstr) ascii inet_addr
025 0x0000074e 0x0040074e   6   7 (.dynstr) ascii memcmp
026 0x00000755 0x00400755   4   5 (.dynstr) ascii puts
027 0x0000075a 0x0040075a  11  12 (.dynstr) ascii daemon_init
028 0x00000766 0x00400766   6   7 (.dynstr) ascii socket
029 0x0000076d 0x0040076d   8   9 (.dynstr) ascii m_server
030 0x00000776 0x00400776  10  11 (.dynstr) ascii setsockopt
031 0x00000781 0x00400781   4   5 (.dynstr) ascii bind
032 0x00000786 0x00400786   8   9 (.dynstr) ascii m_client
033 0x0000078f 0x0040078f   9  10 (.dynstr) ascii rcvBuffer
034 0x00000799 0x00400799  10  11 (.dynstr) ascii sendBuffer
035 0x000007a4 0x004007a4   8   9 (.dynstr) ascii recvfrom
036 0x000007ad 0x004007ad  12  13 (.dynstr) ascii product_test
037 0x000007ba 0x004007ba  13  14 (.dynstr) ascii libnvram.so.0
038 0x000007c8 0x004007c8  16  17 (.dynstr) ascii _DYNAMIC_LINKING
039 0x000007d9 0x004007d9   9  10 (.dynstr) ascii __RLD_MAP
040 0x000007e3 0x004007e3  21  22 (.dynstr) ascii _GLOBAL_OFFSET_TABLE_
041 0x000007f9 0x004007f9  14  15 (.dynstr) ascii libshared.so.0
042 0x00000808 0x00400808   9  10 (.dynstr) ascii libc.so.0
043 0x00000812 0x00400812   6   7 (.dynstr) ascii _ftext
044 0x00000819 0x00400819   6   7 (.dynstr) ascii _fdata
045 0x00000824 0x00400824   6   7 (.dynstr) ascii _edata
046 0x0000082b 0x0040082b  11  12 (.dynstr) ascii __bss_start
047 0x00000837 0x00400837   5   6 (.dynstr) ascii _fbss
048 0x0000083d 0x0040083d   4   5 (.dynstr) ascii _end
049 0x0000087c 0x0040087c   5   6 (.init) ascii 8\n9'\t
050 0x000008ac 0x004008ac   5   6 (.init) ascii p19'\t
051 0x0000094c 0x0040094c   4   5 (.text) ascii pAB$
052 0x0000096c 0x0040096c   4   5 (.text) ascii 4@B$
053 0x00000994 0x00400994   4   5 (.text) ascii 4@!$
054 0x000009bc 0x004009bc   4   5 (.text) ascii 4@B$
055 0x00000a1c 0x00400a1c   4   5 (.text) ascii pA!$
056 0x00000bb2 0x00400bb2   6  14 (.text) utf16le `\bϠ ➽‡ blocks=Basic Latin,Greek and Coptic,Dingbats,General Punctuation
057 0x00000c60 0x00400c60   5   6 (.text) ascii  4B$\r
058 0x00000cc4 0x00400cc4   4   5 (.text) ascii $4B$
059 0x00000ddd 0x00400ddd   4   5 (.text) ascii AB$ 
060 0x00000f18 0x00400f18   5   6 (.text) ascii  4B$\r
061 0x0000100f 0x0040100f   4   5 (.text) ascii $!  
062 0x00001247 0x00401247   4   5 (.text) ascii '! @
063 0x0000133b 0x0040133b   4   5 (.text) ascii '! `
064 0x00001532 0x00401532   4   5 (.text) ascii c$! 
065 0x00001a77 0x00401a77   4   5 (.text) ascii $!( 
066 0x00001abb 0x00401abb   4   7 (.text)  utf8 <襜'! blocks=Basic Latin,CJK Unified Ideographs
067 0x00001efa 0x00401efa   4   5 (.text) ascii c$! 
068 0x000024ae 0x004024ae   5   6 (.text) ascii #2!( 
069 0x000024b6 0x004024b6   5   6 (.text) ascii F$! `
070 0x0000255b 0x0040255b   4   5 (.text) ascii $!(@
071 0x00002b9d 0x00402b9d   4   5 (.text) ascii ;B$\b
072 0x000033d8 0x004033d8   5   6 (.fini) ascii 0\t9'\t
073 0x00003404 0x00403404  19  20 (.rodata) ascii cat /etc_ro/version
074 0x00003418 0x00403418   5   6 (.rodata) ascii FW:%s
075 0x00003424 0x00403424   5   6 (.rodata) ascii 3.7.1
076 0x0000342c 0x0040342c  26  27 (.rodata) ascii /usr/sbin/cs_client get %s
077 0x00003448 0x00403448  38  39 (.rodata) ascii /usr/sbin/cs_client get sys/serial_num
078 0x00003474 0x00403474  29  30 (.rodata) ascii %hhx:%hhx:%hhx:%hhx:%hhx:%hhx
079 0x00003494 0x00403494  29  30 (.rodata) ascii [WIZARD]Enter ===== %s =====\n
080 0x000034b4 0x004034b4  18  19 (.rodata) ascii retirve_infomation
081 0x000034c8 0x004034c8  37  38 (.rodata) ascii BackdoorPacketRetrieveInformation_Ack
082 0x000034f0 0x004034f0  13  14 (.rodata) ascii sys/fw/0/name
083 0x00003500 0x00403500  13  14 (.rodata) ascii sys/fw/1/name
084 0x00003510 0x00403510  11  12 (.rodata) ascii %s %s %s %s
085 0x0000351c 0x0040351c  10  11 (.rodata) ascii sndbuf:%s\n
086 0x00003528 0x00403528  15  16 (.rodata) ascii backdoor_remove
087 0x00003538 0x00403538  24  25 (.rodata) ascii BackdoorPacketRemove_Ack
088 0x00003554 0x00403554  39  40 (.rodata) ascii /usr/sbin/cs_client set wizard/remove 1
089 0x0000357c 0x0040357c  39  40 (.rodata) ascii /usr/sbin/cs_client set wizard/enable 0
090 0x000035a4 0x004035a4  39  40 (.rodata) ascii /usr/sbin/cs_client set sys/mp_wizard 0
091 0x000035cc 0x004035cc  26  27 (.rodata) ascii /usr/sbin/cs_client commit
092 0x000035e8 0x004035e8  22  23 (.rodata) ascii set_to_button_led_test
093 0x00003600 0x00403600  36  37 (.rodata) ascii BackdoorPacketSetToButtonLedTest_Ack
094 0x00003628 0x00403628  15  16 (.rodata) ascii killall soft_wd
095 0x00003638 0x00403638  74  75 (.rodata) ascii soft_wd -t 5 -p config_server -p gpio_task@"gpio_task -u" -p port_detector
096 0x00003684 0x00403684  17  18 (.rodata) ascii killall gpio_task
097 0x00003698 0x00403698  12  13 (.rodata) ascii gpio_task -u
098 0x000036a8 0x004036a8  12  13 (.rodata) ascii retrive_macs
099 0x000036b8 0x004036b8  30  31 (.rodata) ascii BackdoorPacketRetrieveMACs_Ack
100 0x000036d8 0x004036d8   9  10 (.rodata) ascii wan/0/mac
101 0x000036e4 0x004036e4   9  10 (.rodata) ascii load_macs
102 0x000036f0 0x004036f0  77  78 (.rodata) ascii WAN MAC:%02x:%02x:%02x:%02x:%02x:%02x  LAN MAC:%02x:%02x:%02x:%02x:%02x:%02x\n
103 0x00003740 0x00403740  73  74 (.rodata) ascii G MAC:%02x:%02x:%02x:%02x:%02x:%02x  A MAC:%02x:%02x:%02x:%02x:%02x:%02x\n
104 0x0000378c 0x0040378c  26  27 (.rodata) ascii BackdoorPacketLoadMACs_Ack
105 0x000037a8 0x004037a8  63  64 (.rodata) ascii /usr/sbin/cs_client set wan/0/mac %02x:%02x:%02x:%02x:%02x:%02x
106 0x000037e8 0x004037e8  18  19 (.rodata) ascii restore_to_default
107 0x000037fc 0x004037fc  34  35 (.rodata) ascii BackdoorPacketRestoreToDefault_Ack
108 0x00003820 0x00403820  31  32 (.rodata) ascii /usr/sbin/cs_client restore all
109 0x00003840 0x00403840  29  30 (.rodata) ascii cfg_flash -s -n backdoor -v 0
110 0x00003860 0x00403860  14  15 (.rodata) ascii refresh_tamper
111 0x00003870 0x00403870  36  37 (.rodata) ascii BackdoorPacketRefreshTamperProof_Ack
112 0x00003898 0x00403898  42  43 (.rodata) ascii /usr/sbin/cs_client set sys/learn_tamper 1
113 0x000038c4 0x004038c4  12  13 (.rodata) ascii check_tamper
114 0x000038d4 0x004038d4  34  35 (.rodata) ascii BackdoorPacketCheckTamperProof_Ack
115 0x000038f8 0x004038f8  23  24 (.rodata) ascii sys/check_tamper_status
116 0x00003910 0x00403910  36  37 (.rodata) ascii [WIZARD] Check Tamper Status --> %d\n
117 0x0000393c 0x0040393c  16  17 (.rodata) ascii sys/tamper_proof
118 0x00003950 0x00403950  34  35 (.rodata) ascii [WIZARD] Flash tamper position:%s\n
119 0x00003974 0x00403974  24  25 (.rodata) ascii sys/current_tamper_proof
120 0x00003990 0x00403990  36  37 (.rodata) ascii [WIZARD] Current tamper position:%s\n
121 0x000039b8 0x004039b8  18  19 (.rodata) ascii retrive_serial_num
122 0x000039cc 0x004039cc  35  36 (.rodata) ascii BackdoorPacketRetrieveSerialNum_Ack
123 0x000039f0 0x004039f0  15  16 (.rodata) ascii load_serial_num
124 0x00003a00 0x00403a00  31  32 (.rodata) ascii BackdoorPacketLoadSerialNum_Ack
125 0x00003a20 0x00403a20  41  42 (.rodata) ascii /usr/sbin/cs_client set sys/serial_num %s
126 0x00003a4c 0x00403a4c  37  38 (.rodata) ascii BackdoorPacketRetrieveInformation_Req
127 0x00003a74 0x00403a74  36  37 (.rodata) ascii BackdoorPacketSetToButtonLedTest_Req
128 0x00003a9c 0x00403a9c  24  25 (.rodata) ascii BackdoorPacketRemove_Req
129 0x00003ab8 0x00403ab8  30  31 (.rodata) ascii BackdoorPacketRetrieveMACs_Req
130 0x00003ad8 0x00403ad8  26  27 (.rodata) ascii BackdoorPacketLoadMACs_Req
131 0x00003af4 0x00403af4  34  35 (.rodata) ascii BackdoorPacketRestoreToDefault_Req
132 0x00003b18 0x00403b18  35  36 (.rodata) ascii BackdoorPacketRetrieveSerialNum_Req
133 0x00003b3c 0x00403b3c  31  32 (.rodata) ascii BackdoorPacketLoadSerialNum_Req
134 0x00003b5c 0x00403b5c  36  37 (.rodata) ascii BackdoorPacketRefreshTamperProof_Req
135 0x00003b84 0x00403b84  34  35 (.rodata) ascii BackdoorPacketCheckTamperProof_Req
136 0x00003ba8 0x00403ba8   9  10 (.rodata) ascii 234.2.2.7
137 0x00003bb4 0x00403bb4  14  15 (.rodata) ascii Unknow request
138 0x00003bc4 0x00403bc4  11  12 (.rodata) ascii 192.168.1.1
139 0x00003bd4 0x00403bd4  21  22 (.rodata) ascii [WIZARD] Start WIZARD
140 0x00003bec 0x00403bec  38  39 (.rodata) ascii [WIZARD] Create multicast socket fail!
141 0x00003c14 0x00403c14  44  45 (.rodata) ascii [WIZARD] Create multicast socket succesded! 
142 0x00003c44 0x00403c44  11  12 (.rodata) ascii sys/op_mode
143 0x00003c50 0x00403c50   8   9 (.rodata) ascii lan/0/ip
144 0x00003c5c 0x00403c5c  42  43 (.rodata) ascii [WIZARD] MultiCast process receive error!!
145 0x00003c88 0x00403c88  59  60 (.rodata) ascii [WIZARD] Fail to SetSockopt IP_ADD_MEMBERSHIP when Ezconf!!
146 0x00003cc4 0x00403cc4   8   9 (.rodata) ascii wan/0/ip
147 0x00003cd0 0x00403cd0  58  59 (.rodata) ascii [WIZARD] Fail to SetSockopt IP_MULTICAST_TTL when Ezconf!!
148 0x00003d0c 0x00403d0c  59  60 (.rodata) ascii [WIZARD] Fail to SetSockopt IP_MULTICAST_LOOP when Ezconf!!
149 0x00003d48 0x00403d48  35  36 (.rodata) ascii [WIZARD] MultiCastcast bind fail!! 
150 0x00003d6c 0x00403d6c  54  55 (.rodata) ascii [WIZARD] Fail to SetSockopt SO_REUSEADDR when Ezconf!!
151 0x00004469 0x00000001   9  10 (.shstrtab) ascii .shstrtab
152 0x00004473 0x0000000b   7   8 (.shstrtab) ascii .interp
153 0x0000447b 0x00000013   8   9 (.shstrtab) ascii .reginfo
154 0x00004484 0x0000001c   8   9 (.shstrtab) ascii .dynamic
155 0x0000448d 0x00000025   5   6 (.shstrtab) ascii .hash
156 0x00004493 0x0000002b   7   8 (.shstrtab) ascii .dynsym
157 0x0000449b 0x00000033   7   8 (.shstrtab) ascii .dynstr
158 0x000044a3 0x0000003b   5   6 (.shstrtab) ascii .init
159 0x000044a9 0x00000041   5   6 (.shstrtab) ascii .text
160 0x000044af 0x00000047  11  12 (.shstrtab) ascii .MIPS.stubs
161 0x000044bb 0x00000053   5   6 (.shstrtab) ascii .fini
162 0x000044c1 0x00000059   7   8 (.shstrtab) ascii .rodata
163 0x000044c9 0x00000061   9  10 (.shstrtab) ascii .eh_frame
164 0x000044d3 0x0000006b   6   7 (.shstrtab) ascii .ctors
165 0x000044da 0x00000072   6   7 (.shstrtab) ascii .dtors
166 0x000044e1 0x00000079   4   5 (.shstrtab) ascii .jcr
167 0x000044e6 0x0000007e   5   6 (.shstrtab) ascii .data
168 0x000044ec 0x00000084   8   9 (.shstrtab) ascii .rld_map
169 0x000044f5 0x0000008d   4   5 (.shstrtab) ascii .got
170 0x000044fa 0x00000092   4   5 (.shstrtab) ascii .bss
171 0x000044ff 0x00000097   4   5 (.shstrtab) ascii .pdr
```

## Question: What does the backdoor in /bin/wizard seem to be capable of?
Side note: This work has been done by others, what is interesting was that it was patched. Can you tell what the manufacturer changed? [https://fail0verflow.com/blog/2012/microcell-fail/](https://fail0verflow.com/blog/2012/microcell-fail/)
