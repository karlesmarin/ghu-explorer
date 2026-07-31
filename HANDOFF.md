# Handoff — where the tools stand, 2026-07-31

Carles Marín + Claude (AI assistant). **Read this first; everything below is on disk, nothing
depends on anyone remembering it.**

## State: two tools, both green

```
python build.py        # the Part III explorer   -> index.html       + node test
python build_calc.py   # the model calculator    -> calculator.html  + node test
```

**Both must pass before anything else.** They do not just build: each extracts its own maths from
the built page and runs it in node against the numbers Python produced for the papers. That is the
entry condition, and it has already earned its keep — see *what the tests caught* below.

| | |
|---|---|
| `index.html` | **1 · Selection rule** — the Part III explorer, unchanged except for the shared nav |
| `calculator.html` | **2 · Model calculator** — new. A matter content in, physics out |
| `src/shell.html`, `src/calc_shell.html` | the sources; the built pages are generated, do not edit them |
| `tools/su4_data.json`, `tools/calc_data.json` | the data, kept apart from the pages |
| `tools/make_calc_data.py` | regenerates the calculator catalogue **and fails if it disagrees with Proposition 1 on a single row** |

## What the calculator does

Type a matter content — any content, not the handful whose Kaluza–Klein spectra somebody has
written out — and read: the one-loop Wilson-line potential over the torus, its vacuum, the Higgs
mass matrix there, the electroweak verdict, which multiplets are blind to the boundary sign, and
whether the embedding has a coset sector at all. Mode counts come from the Young diagram through
Part IV's closed form; η acts on the coset half alone, which is Part V's theorem.

Deep links: `calculator.html#c=4,0,0*3;1,0,1*-1` — irrep `*` multiplicity, negative for the gauge
sector, optional `:−1` for η. `#c=ahmn` loads AHMN's content.

**The anchor travels with the instrument.** At load the page recomputes AHMN arXiv:2312.08608 and
shows a chip: their published vacuum (0.438, 0.299) and mass ratio. If the port ever drifts, the
page says so itself, on itself.

## What the tests caught, and why they exist

- **A real physics bug.** The engine had `Σ = A + ηB`, which puts η on the *identity* half. The
  potential of a **blind** multiplet then moved when η flipped — the page would have contradicted
  its own theorem on screen. Right form: `Σ = A+B` with no η, and `ηD = η(A−B)` on the coset half.
- **A test asserting a convention.** It demanded `α₂ = 0.299` and got `0.701` — the reflected image
  of the same vacuum. It now compares `min(α₂, 1−α₂)`. The potential is invariant under α → −α; only
  invariants may be asserted, here and in the papers.
- **A vacuous control.** "η moves a sighted multiplet" failed on the singlet, whose only charge is 0
  and which therefore contributes a constant. The control now skips multiplets with no α dependence.

## Next, in order — the first one is what Carles asked for last

1. **The graph as the control.** Drag on the map to move α; a reading bar that never empties shows
   `α · V · masses² · mixing` **at the cursor**, not only at the minimum. Double-click = "drop it
   here" and watch it roll. The 1D cut follows the cursor instead of the vacuum.
2. **Make the flow panel fast.** It evaluates the gradient four times per step, sixty steps, ~500
   seeds: about 1e8 winding sums, so it lags seconds behind the other panels and looks frozen.
   Sample the field **once** on a 48×48 grid and interpolate. (Written and verified once, then lost
   in the revert below.)
3. **Live selection.** Every change recomputes on its own, ~90 ms debounce, button shows `computing…`.
4. **Images first.** Order should be landscape → numbers → controls, opening with a content already
   loaded. **Edit the HTML by hand:** a regex reorder is exactly what broke the page and forced the
   revert to `c22be0d`.
5. **ΔV between the two values of η** — blank exactly on a blind content: the theorem, seen without
   reading a word.
6. Then: `README.md` still says *companion to Part III* (it is now III–V), and its "7904 partitions"
   does not come from the published Part IV, which says **3060** with parts ≤14 and **4845** with
   parts ≤16 — two ranges that are not summed.

## The papers behind the two tools

Part III [10.5281/zenodo.21438226](https://doi.org/10.5281/zenodo.21438226) ·
Part IV [10.5281/zenodo.21463000](https://doi.org/10.5281/zenodo.21463000) ·
Part V [10.5281/zenodo.21727095](https://doi.org/10.5281/zenodo.21727095) ·
code for Part V: [higgs-blind-class](https://github.com/karlesmarin/higgs-blind-class)

Honesty labels are load-bearing and must survive edits: **theorem** (blindness, the count, the
census — machine-checked in Lean 4), **verified** (Part IV's closed form — exhaustive, *not proved*),
**measured** (vacuum, masses, mixing — one published case is the whole validation). The sign of the
mixing angle is a convention; only invariants are shown.
