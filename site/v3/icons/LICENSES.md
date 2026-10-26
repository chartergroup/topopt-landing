# Icon sources and licences

The files in this folder are one-colour SVG marks. The page draws them with CSS masks, so they follow the text colour. No mark was drawn by hand: each file is a file of the open icon set named below. The brand marks belong to their owners. They are shown only to name the supported tools.

## LobeHub Icons: MIT licence

- Set: LobeHub Icons, package `@lobehub/icons-static-svg`, folder `packages/static-svg/icons/`.
- Project: https://github.com/lobehub/lobe-icons
- Pinned commit: `8b7bbc433d38437fa2b0cca58ae896917162b812`
- Licence file: https://raw.githubusercontent.com/lobehub/lobe-icons/8b7bbc433d38437fa2b0cca58ae896917162b812/LICENSE
- The files are the monochrome variants (no `-color` files). Each file is byte-identical to the source file (SHA-256 start in the table).

| File | Source URL | SHA-256 (start) | Used for |
|---|---|---|---|
| `claudecode.svg` | https://raw.githubusercontent.com/lobehub/lobe-icons/8b7bbc433d38437fa2b0cca58ae896917162b812/packages/static-svg/icons/claudecode.svg | `d7eb2d876b49e51c` | Claude Code, in the install card |
| `claude.svg` | https://raw.githubusercontent.com/lobehub/lobe-icons/8b7bbc433d38437fa2b0cca58ae896917162b812/packages/static-svg/icons/claude.svg | `365a70a7eb3956d9` | Claude Desktop, on the agent line |
| `cursor.svg` | https://raw.githubusercontent.com/lobehub/lobe-icons/8b7bbc433d38437fa2b0cca58ae896917162b812/packages/static-svg/icons/cursor.svg | `0cb51bddf264ae10` | Cursor, on the agent line |
| `codex.svg` | https://raw.githubusercontent.com/lobehub/lobe-icons/8b7bbc433d38437fa2b0cca58ae896917162b812/packages/static-svg/icons/codex.svg | `d08b4e824cd6727e` | Codex CLI, on the agent line |
| `geminicli.svg` | https://raw.githubusercontent.com/lobehub/lobe-icons/8b7bbc433d38437fa2b0cca58ae896917162b812/packages/static-svg/icons/geminicli.svg | `bc9b0199cb4c5dee` | Gemini CLI, on the agent line |

Licence text (copy of the `LICENSE` file at the pinned commit):

```text
MIT License

Copyright (c) 2023 LobeHub

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Tabler Icons: MIT licence

- Set: Tabler Icons, folder `icons/outline/`.
- Project: https://github.com/tabler/tabler-icons
- Pinned commit: `ab7315d660c76f97d4b9ae9b2ff2aacba1d61730`
- Licence file: https://raw.githubusercontent.com/tabler/tabler-icons/ab7315d660c76f97d4b9ae9b2ff2aacba1d61730/LICENSE
- A generic processor icon. The Apple logo is not used: Apple's guidelines for third parties allow the word Apple in a compatibility phrase, but not the Apple Logo. The file is byte-identical to the source file.

| File | Source URL | SHA-256 (start) | Used for |
|---|---|---|---|
| `cpu.svg` | https://raw.githubusercontent.com/tabler/tabler-icons/ab7315d660c76f97d4b9ae9b2ff2aacba1d61730/icons/outline/cpu.svg | `d9ecd8e0f4a140f8` | Apple silicon, on the platform line of the install section |

Licence text (copy of the `LICENSE` file at the pinned commit):

```text
MIT License

Copyright (c) 2020-2026 Paweł Kuna

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Simple Icons: CC0 1.0 Universal

- Set: Simple Icons, folder `icons/`.
- Project: https://github.com/simple-icons/simple-icons
- Pinned commit: `90646e4bf7f3b89df6c37e65baf3e7bc759a517c` (version 16.36.0)
- Licence file: https://raw.githubusercontent.com/simple-icons/simple-icons/90646e4bf7f3b89df6c37e65baf3e7bc759a517c/LICENSE.md (CC0 1.0 Universal, public domain dedication: https://creativecommons.org/publicdomain/zero/1.0/)
- Change to each file: the attribute `fill="currentColor"` was added to the `svg` element. The path data is unchanged.

| File | Source URL | SHA-256 (start) | Used for |
|---|---|---|---|
| `linux.svg` | https://raw.githubusercontent.com/simple-icons/simple-icons/90646e4bf7f3b89df6c37e65baf3e7bc759a517c/icons/linux.svg | `4c72b822632cf653` | Linux x86_64, on the platform line |

`linux.svg` is Tux, the Linux penguin. Tux was drawn by Larry Ewing (lewing@isc.tamu.edu) with The GIMP; his notice allows use if he and The GIMP are acknowledged. Linux is a registered trademark of Linus Torvalds.

## No icon

- VS Code: neither set has a VS Code mark (checked at the two pinned commits). The page names it as text only.
