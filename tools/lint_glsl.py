#!/usr/bin/env python3
"""Flag GLSL patterns that broke deko3d's uam compiler on the Sonic Riders port.

1. A vector component chosen at run time:  v[i], m[i >> 2][i & 3]
   uam miscompiled this (wrong values for components 1-3), so every vertex was garbage.
2. A local array indexed at run time: float r[4]; ... r[idx]
   This forced ~194 KB of per-warp scratch memory on the Switch GPU.

Use explicit selects instead (a pick()/select helper). Indexing an array of vec4 uniforms
or a UBO/SSBO array with a run-time index is fine; only the cases above are flagged.
Silence a reviewed line with a trailing comment:  // lint: index-ok

Usage: lint_glsl.py FILE [FILE...]   exit 1 if anything is flagged.
"""
import re
import sys

# Windows pipes default to the ANSI code page; Claude Code reads UTF-8.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

VEC_DECL = re.compile(r"\b(?:[iub]?vec[234]|mat[234](?:x[234])?)\s+(\w+)\s*(?:[=;,)])")
LOCAL_ARRAY_DECL = re.compile(r"^[ \t]+(?:const\s+)?(?:float|int|uint|bool|[iub]?vec[234])\s+(\w+)\s*\[\s*\w+\s*\]\s*[;=]")
SUBSCRIPT = re.compile(r"\b(\w+)\s*\[([^\[\]]+)\]")
DOUBLE_SUBSCRIPT = re.compile(r"\b(\w+)\s*\[[^\[\]]+\]\s*\[([^\[\]]+)\]")
CONSTANT_INDEX = re.compile(r"^\s*(\d+u?|[A-Z][A-Z0-9_]*)\s*$")


def strip_comments(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), src, flags=re.S)
    return src


def lint(path: str) -> list[str]:
    raw = open(path, encoding="utf-8", errors="replace").read()
    raw_lines = raw.splitlines()
    code_lines = strip_comments(raw).splitlines()
    vectors, local_arrays = set(), set()
    for line in code_lines:
        code = line.split("//", 1)[0]
        vectors.update(VEC_DECL.findall(code))
        m = LOCAL_ARRAY_DECL.match(code)
        if m:
            local_arrays.add(m.group(1))

    problems = []
    for n, line in enumerate(code_lines, 1):
        original = raw_lines[n - 1] if n - 1 < len(raw_lines) else line
        if "lint: index-ok" in original:
            continue
        code = line.split("//", 1)[0]
        if LOCAL_ARRAY_DECL.match(code):
            continue
        for m in DOUBLE_SUBSCRIPT.finditer(code):
            if not CONSTANT_INDEX.match(m.group(2)):
                problems.append(f"{path}:{n}: run-time component index into '{m.group(1)}[..]' "
                                f"([{m.group(2).strip()}]); use an explicit select")
        for m in SUBSCRIPT.finditer(code):
            name, index = m.group(1), m.group(2)
            if CONSTANT_INDEX.match(index):
                continue
            if name in vectors:
                problems.append(f"{path}:{n}: run-time index into vector '{name}' ([{index.strip()}]); "
                                "use an explicit select")
            elif name in local_arrays:
                problems.append(f"{path}:{n}: run-time index into local array '{name}' ([{index.strip()}]); "
                                "this costs GPU scratch memory on the Switch, use selects or unroll")
    return problems


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    problems = []
    for path in sys.argv[1:]:
        problems += lint(path)
    for p in problems:
        print(p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
