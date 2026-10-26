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
| `claudecode.svg` | https://raw.githubusercontent.com/lobehub/lobe-icons/8b7bbc433d38437fa2b0cca58ae896917162b812/packages/static-svg/icons/claudecode.svg | `d7eb2d876b49e51c` | Claude Code, in the heading of its install card |
| `claude.svg` | https://raw.githubusercontent.com/lobehub/lobe-icons/8b7bbc433d38437fa2b0cca58ae896917162b812/packages/static-svg/icons/claude.svg | `365a70a7eb3956d9` | Claude Desktop, in the link of the Other Agents card |
| `cursor.svg` | https://raw.githubusercontent.com/lobehub/lobe-icons/8b7bbc433d38437fa2b0cca58ae896917162b812/packages/static-svg/icons/cursor.svg | `0cb51bddf264ae10` | Cursor, in the heading of its install card |
| `codex.svg` | https://raw.githubusercontent.com/lobehub/lobe-icons/8b7bbc433d38437fa2b0cca58ae896917162b812/packages/static-svg/icons/codex.svg | `d08b4e824cd6727e` | Codex, in the heading of its install card |
| `geminicli.svg` | https://raw.githubusercontent.com/lobehub/lobe-icons/8b7bbc433d38437fa2b0cca58ae896917162b812/packages/static-svg/icons/geminicli.svg | `bc9b0199cb4c5dee` | Gemini CLI, in the link of the Other Agents card |

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

## Simple Icons: CC0 1.0 Universal

- Set: Simple Icons, folder `icons/`.
- Project: https://github.com/simple-icons/simple-icons
- Pinned commit: `90646e4bf7f3b89df6c37e65baf3e7bc759a517c` (version 16.36.0)
- Licence file: https://raw.githubusercontent.com/simple-icons/simple-icons/90646e4bf7f3b89df6c37e65baf3e7bc759a517c/LICENSE.md (CC0 1.0 Universal, public domain dedication: https://creativecommons.org/publicdomain/zero/1.0/)
- Change to each file: the attribute `fill="currentColor"` was added to the `svg` element. The path data is unchanged.

| File | Source URL | SHA-256 (start) | Used for |
|---|---|---|---|
| `apple.svg` | https://raw.githubusercontent.com/simple-icons/simple-icons/90646e4bf7f3b89df6c37e65baf3e7bc759a517c/icons/apple.svg | `93439c0957e7e4c5` | Apple silicon, on the platform line of the install section |
| `linux.svg` | https://raw.githubusercontent.com/simple-icons/simple-icons/90646e4bf7f3b89df6c37e65baf3e7bc759a517c/icons/linux.svg | `4c72b822632cf653` | Linux x86_64, on the platform line of the install section |
| `github.svg` | https://raw.githubusercontent.com/simple-icons/simple-icons/90646e4bf7f3b89df6c37e65baf3e7bc759a517c/icons/github.svg | `5e2d81ef6b15846a` | GitHub, next to the GitHub links in the top bar and the footer (/v4) |

The LobeHub set also has an `apple.svg`. It is not used: the Apple and Linux marks come from one set, Simple Icons, so the two look alike.

## Codicons (Microsoft): CC BY 4.0

- Set: Codicons, the icon font of Visual Studio Code, folder `src/icons/`.
- Project: https://github.com/microsoft/vscode-codicons
- Pinned commit: `bcc74f01d4c8e43fbfe375912ef5ecca9cfbc009`
- Licence of the icons: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/ (licence file: https://raw.githubusercontent.com/microsoft/vscode-codicons/bcc74f01d4c8e43fbfe375912ef5ecca9cfbc009/LICENSE).
- Attribution: "vscode" icon from Codicons by Microsoft Corporation, CC BY 4.0. The file is byte-identical to the source file (no change).
- Neither LobeHub Icons nor Simple Icons has a VS Code mark (checked at their pinned commits), so this one mark comes from Codicons.

| File | Source URL | SHA-256 (start) | Used for |
|---|---|---|---|
| `vscode.svg` | https://raw.githubusercontent.com/microsoft/vscode-codicons/bcc74f01d4c8e43fbfe375912ef5ecca9cfbc009/src/icons/vscode.svg | `f9130337f239b034` | VS Code, in the link of the Other Agents card (/v4) |
