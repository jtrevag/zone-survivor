# Web Deploy (itch.io) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package Zone Survivor as a playable HTML5 prototype on itch.io using Pygbag (Pygame → WebAssembly).

**Architecture:** Pygbag compiles the Python/Pygame project to CPython WASM via Pyodide. The main loop must yield control each frame via `await asyncio.sleep(0)`. The rest of the codebase is unchanged. Output is a zip uploaded to itch.io as an HTML5 game.

**Tech Stack:** Python 3.12, Pygame-ce, Pygbag 0.9.x, itch.io HTML5 embed

---

## File Map

| File | Change |
|---|---|
| `main.py` | Refactor `main()` to `async def main()`, add `await asyncio.sleep(0)` per frame, change entry point to `asyncio.run(main())` |
| `requirements.txt` | Add `pygbag` (dev only — does not ship in WASM) |

No other files change. Pygbag bundles everything at build time.

---

## Task 1: Install Pygbag

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Activate venv and install pygbag**

```bash
source .venv/bin/activate
pip install pygbag
```

Expected output includes: `Successfully installed pygbag-...`

- [ ] **Step 2: Verify installation**

```bash
python -m pygbag --version
```

Expected: prints version string (0.9.x or similar).

- [ ] **Step 3: Add pygbag to requirements.txt**

Add this line at the end of `requirements.txt`:

```
pygbag
```

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "chore: add pygbag for web build"
```

---

## Task 2: Refactor main.py to async loop

**Files:**
- Modify: `main.py`

Pygbag requires:
1. `main()` must be `async def`
2. Each frame must call `await asyncio.sleep(0)` — this yields control back to the browser's event loop
3. Entry point must be `asyncio.run(main())` (Pygbag patches this for WASM; it works normally on desktop too)

- [ ] **Step 1: Add `import asyncio` at the top of main.py**

At line 1, before `import pygame`:

```python
import asyncio
import pygame
```

- [ ] **Step 2: Change `def main():` to `async def main():`**

Find line `def main():` and change to:

```python
async def main():
```

- [ ] **Step 3: Add `await asyncio.sleep(0)` at end of the while loop**

The current while loop ends with `pygame.display.flip()`. After that line, add:

```python
        await asyncio.sleep(0)
```

The end of the while loop body should look like:

```python
        pygame.display.flip()
        await asyncio.sleep(0)
```

- [ ] **Step 4: Replace the `if __name__ == "__main__":` block**

Change:

```python
if __name__ == "__main__":
    main()
```

To:

```python
asyncio.run(main())
```

Pygbag patches `asyncio.run` when building for WASM; on desktop it works as normal. The `if __name__` guard is dropped because Pygbag imports `main.py` directly.

- [ ] **Step 5: Verify game still runs on desktop**

```bash
source .venv/bin/activate
python3 main.py
```

Expected: game launches and plays normally. Verify: move, shoot, take damage, level up screen, restart. No change in behavior.

- [ ] **Step 6: Commit**

```bash
git add main.py
git commit -m "feat: refactor main loop to async for Pygbag/web compatibility"
```

---

## Task 3: Test locally with Pygbag dev server

**Files:** (no changes)

Pygbag has a built-in dev server that serves the game locally before you build for distribution. This catches WASM-specific issues early.

- [ ] **Step 1: Run Pygbag dev server**

```bash
source .venv/bin/activate
cd /Users/jamesgale/Documents/zone-survivor
python -m pygbag .
```

Pygbag will print a URL — typically `http://localhost:8000`.

- [ ] **Step 2: Open browser and load the game**

Visit `http://localhost:8000` in Chrome or Firefox. First load is slow (30–60s) — Pyodide downloads ~10MB of runtime. Wait for the game canvas to appear.

- [ ] **Step 3: Smoke-test core gameplay**

Check each of these works in the browser:
- [ ] Player moves with WASD
- [ ] Player rotates to face mouse
- [ ] Left click fires (bullet appears)
- [ ] R key reloads (progress bar shows)
- [ ] Enemy spawns and chases player
- [ ] Taking damage shows HUD HP drop and screen flash
- [ ] XP orb drops on enemy death, XP bar fills
- [ ] Level-up screen appears, upgrade selectable
- [ ] Sound plays (gunshot on click — browser requires user gesture first, so click to fire is fine)

- [ ] **Step 4: Check browser console for errors**

Open DevTools (F12) → Console tab. Note any red errors. Common acceptable warnings: `AudioContext` warnings before first user gesture. Errors to investigate: `ModuleNotFoundError`, `AttributeError`, import failures.

- [ ] **Step 5: Stop dev server**

Ctrl+C in terminal.

---

## Task 4: Build web package

**Files:** (no changes — output goes to `build/web/`)

- [ ] **Step 1: Run Pygbag build**

```bash
source .venv/bin/activate
cd /Users/jamesgale/Documents/zone-survivor
python -m pygbag --build .
```

Expected: creates `build/web/` directory with `index.html`, `*.whl`, and other assets.

- [ ] **Step 2: Locate the distributable zip**

```bash
ls build/web/
```

Pygbag creates `build/web/index.html` and a zip suitable for itch.io. The zip is typically at `build/web/web-archive.zip` or you zip `build/web/` yourself:

```bash
cd build/web && zip -r ../../zone-survivor-web.zip . && cd ../..
```

This produces `zone-survivor-web.zip` at the project root.

- [ ] **Step 3: Note the zip path**

```
/Users/jamesgale/Documents/zone-survivor/zone-survivor-web.zip
```

This is what gets uploaded to itch.io.

- [ ] **Step 4: Commit**

Add `build/` to `.gitignore` if not already present, then commit:

```bash
echo "build/" >> .gitignore
echo "zone-survivor-web.zip" >> .gitignore
git add .gitignore
git commit -m "chore: ignore pygbag build output"
```

---

## Task 5: Create itch.io account and game page (manual steps)

These steps require a browser and cannot be automated.

- [ ] **Step 1: Create itch.io account**

Go to `https://itch.io/register`. Use username `jtrevag` or similar. Verify email.

- [ ] **Step 2: Create new game project**

Go to `https://itch.io/game/new`. Fill in:

| Field | Value |
|---|---|
| Title | Zone Survivor |
| Project URL | `zone-survivor` (or similar) |
| Kind of project | `HTML` |
| Classification | `Games` |

- [ ] **Step 3: Configure game page**

Under **Uploads**, click **Upload files** and upload `zone-survivor-web.zip`. After upload, check **This file will be played in the browser** and set:

| Setting | Value |
|---|---|
| Frame width | 1280 |
| Frame height | 720 |
| Fullscreen button | checked |

- [ ] **Step 4: Set visibility and save**

Set **Visibility** to `Restricted` (shareable link, not public) for prototype testing. Click **Save & view page**.

- [ ] **Step 5: Test the live embed**

Play the game directly on the itch.io page. Run the same smoke test as Task 3, Step 3. Verify it loads and plays correctly in the embedded iframe.

---

## Task 6: Update docs and create PR

**Files:**
- Modify: `docs/CHANGELOG.md`
- Modify: `docs/ROADMAP.md`

- [ ] **Step 1: Add web deploy entry to CHANGELOG.md**

Add under a new section at the top:

```markdown
## Web Deploy — 2026-06-11

- Refactored `main()` to async for Pygbag/WASM compatibility
- Added Pygbag build tooling
- Deployed playable prototype to itch.io (HTML5 embed)
```

- [ ] **Step 2: Add web deploy to ROADMAP.md Post-v1 section**

Under `## Post-v1 (Backlog)`, mark or add:

```markdown
- [x] Web deploy — playable prototype on itch.io (Pygbag/WASM)
```

- [ ] **Step 3: Commit docs**

```bash
git add docs/CHANGELOG.md docs/ROADMAP.md
git commit -m "docs: record web deploy milestone in changelog and roadmap"
```

- [ ] **Step 4: Create PR**

```bash
git push -u origin feat/web-deploy-itchio
gh pr create --title "feat: web deploy — playable HTML5 prototype on itch.io" --body "$(cat <<'EOF'
## Summary
- Refactors `main()` to `async def` with `await asyncio.sleep(0)` per frame for Pygbag/WASM compatibility
- Adds Pygbag to requirements.txt
- Builds and uploads to itch.io as HTML5 game (1280x720)

## Test plan
- [ ] Desktop: `python3 main.py` plays normally
- [ ] Browser (local): `python -m pygbag .` → localhost:8000 loads and plays
- [ ] Browser (live): itch.io page loads and plays, sounds fire on first user gesture

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Potential Issues

### Sound in browser
Browsers block audio until a user gesture. The first gunshot sound plays on left-click (fire), which is already a user gesture — so this should work. If sounds are silent, check DevTools console for `AudioContext` errors.

### Slow first load
Pyodide downloads ~10MB on first visit. Subsequent loads use browser cache. Nothing to fix — just warn users in the itch.io description.

### `array.array` in WASM
`SoundManager` uses `array.array('h')` to build PCM buffers. This is part of Python's stdlib and works in Pyodide/WASM.

### Screen size
The game is 1280×720. Set the itch.io iframe to exactly that. Pygbag centers the canvas automatically.
