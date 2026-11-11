#!/usr/bin/env python3
"""Verify your Sonic Heroes disc image and extract the files the recompiler reads.

  extract_iso.py ISO OUTDIR [--no-verify-iso]

The image must be Sonic Heroes (USA) G9SE8P revision 0 (SHA-1 dd752c8a...bfe6; to confirm against Redump).
Writes main.dol, the 18 RELs and TSonic.str into OUTDIR (baserom/ by default in the docs; gitignored) and
checks each against its known SHA-1. Nothing is uploaded or shared; never commit these files.
"""
import hashlib
import os
import struct
import sys

ISO_SHA1 = "dd752c8aa64f2f043c32be0f0bd5b8617357bfe6"
FILES = {  # name on disc -> SHA-1 of the extracted file
    "advertiseD.rel": "0b28051533603c5f330b1af7e1959be8e73856ea",
    "autosaveD.rel": "120e89d6ca861f63ecf9c8f2d282bab5b500ab17",
    "movieD.rel": "6e2773a99ec5b05d5634d09521246e3e28bd6de9",
    "stage00D.rel": "3ef757fe69b177792cf6c3ee9fd54fb275df01ba",
    "stage01D.rel": "7c61a97a347c714cd72bdf6cab204b0749e946f2",
    "stage03D.rel": "9e1c377aa780e2bee876a14325263a6b2b541934",
    "stage05D.rel": "76a08d21162462b8c75b124aee8bb213db292bee",
    "stage07D.rel": "89b6ee655fa9bb07ca8ef9d30dc00befcc9295f2",
    "stage09D.rel": "836d0accf611530095e01d5f87c43d35bc87bc3c",
    "stage11D.rel": "79a86badbc61416b3efc14802c536eeaef6cf0aa",
    "stage13D.rel": "c86851d0e26cfb3b9c639c33babfc7768868fab4",
    "stage26D.rel": "e5585aec40ebb843bbd5c9a2d947abeda4acc048",
    "stage27D.rel": "06e4b2926228a64dd7ae81007c75fd9194c402c2",
    "stage28D.rel": "93b0dd05156fa2dee32a64930d354c9e985d7e4a",
    "stage31D.rel": "4c052149e2df1c88c29038dd20e7a53c863c1d09",
    "stage32D.rel": "27d8092da77c4fdb3b53381849966e91d9672e68",
    "stage33D.rel": "8456fb201666c6ea3bf200fcf2fe8dfd2e05ca50",
    "stage40D.rel": "efc22e14f102354f27547b3d68c1df6b5e63fce6",
    "TSonic.str": "2de54e8ff887c417fa96f4b45734e54ad5560e9a",
}
DOL_SHA1 = "9214426b8a3fb1d6fe3dcff09bcc1a959e1e04a8"


def fail(msg):
    print("extract_iso: " + msg, file=sys.stderr)
    sys.exit(1)


def sha1_file(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        fail("usage: extract_iso.py ISO OUTDIR [--no-verify-iso]")
    iso, out = args
    if not os.path.isfile(iso):
        fail("disc image not found: %s" % iso)
    with open(iso, "rb") as f:
        hdr = f.read(0x440)
        if len(hdr) < 0x440 or hdr[:6] != b"G9SE8P":
            fail("not Sonic Heroes (USA): the disc ID is %r, G9SE8P is needed" % hdr[:6])
        if hdr[7] != 0:
            fail("disc revision %d: revision 0 is needed" % hdr[7])
        if "--no-verify-iso" not in sys.argv:
            print("extract_iso: checking the disc image (SHA-1, takes a few seconds)...")
            got = sha1_file(iso)
            if got != ISO_SHA1:
                fail("the disc image's SHA-1 is %s, expected %s (a clean G9SE8P rev 0 dump, "
                     "like Redump's; trimmed/compressed/modified images are not supported)" % (got, ISO_SHA1))
            print("extract_iso: disc image OK (G9SE8P rev 0)")
        dol_off, fst_off, fst_size = struct.unpack(">III", hdr[0x420:0x42C])
        # main.dol: its size from the section table (7 text + 11 data sections)
        f.seek(dol_off)
        dh = f.read(0x100)
        offs = struct.unpack(">18I", dh[0:72])
        sizes = struct.unpack(">18I", dh[0x90:0x90 + 72])
        dol_size = max([0x100] + [o + s for o, s in zip(offs, sizes) if s])
        f.seek(dol_off)
        dol = f.read(dol_size)
        f.seek(fst_off)
        fst = f.read(fst_size)
    os.makedirs(out, exist_ok=True)
    if hashlib.sha1(dol).hexdigest() != DOL_SHA1:
        fail("main.dol does not match (SHA-1 %s)" % hashlib.sha1(dol).hexdigest())
    with open(os.path.join(out, "main.dol"), "wb") as w:
        w.write(dol)
    n = struct.unpack(">I", fst[8:12])[0]
    names = fst[n * 12:]
    found = {}
    for i in range(1, n):
        t, a, b = struct.unpack(">III", fst[i * 12:i * 12 + 12])
        if t >> 24:
            continue
        name = names[t & 0xFFFFFF:].split(b"\0", 1)[0].decode("ascii", "replace")
        if name in FILES:
            found[name] = (a, b)
    with open(iso, "rb") as f:
        for name, want in FILES.items():
            if name not in found:
                fail("%s not found on the disc" % name)
            a, b = found[name]
            f.seek(a)
            data = f.read(b)
            if hashlib.sha1(data).hexdigest() != want:
                fail("%s does not match (SHA-1 %s)" % (name, hashlib.sha1(data).hexdigest()))
            with open(os.path.join(out, name), "wb") as w:
                w.write(data)
    print("extract_iso: wrote main.dol, %d RELs and TSonic.str to %s (all verified)" % (len(FILES) - 1, out))


if __name__ == "__main__":
    main()
