# Handoff — where the tools stand, 2026-08-01

> **Superseded, 2026-08-09, and kept as the record of a line that closed.** Everything below
> describes the three SU(4) pages of July 2026. They are now frozen under `tools-2026-07/`,
> reproduced byte for byte by the builders named here, and the root serves the site of the
> series instead. What the repository holds today is in [`README.md`](README.md); the
> instrument that replaced these three is `app/index.html`. The build commands below still
> run and still pass — only their output path moved, and it is corrected in place.

Carles Marín + Claude (AI assistant). **Read this first; everything below is on disk, nothing
depends on anyone remembering it.**

## State: three tools, all green

```
python build.py          # 1 · Selection rule    -> tools-2026-07/index.html      + node test
python build_calc.py     # 2 · Model calculator  -> tools-2026-07/calculator.html + node test
python build_predict.py  # 3 · eta-meter         -> tools-2026-07/predictor.html  + node test
```

**All three must pass before anything else.** They do not just build: each extracts its own maths
from the built page and runs it in node against numbers produced outside the page — the papers, the
Python engine of Part V, or the character itself. That is the entry condition, and it keeps earning
its keep (see *what the tests caught*).

| | |
|---|---|
| `index.html` | **1 · Selection rule** — which α-domain is legal (Part III) |
| `calculator.html` | **2 · Model calculator** — a matter content in, the Higgs out |
| `predictor.html` | **3 · η-meter** — predicts what η does in closed form, checks itself against the loop sum, releases the field on the potential, and draws the atlas of every multiplet |
| `src/*.html` | the sources; the built pages are generated, do not edit them |
| `tools/*.json` | the data, kept apart from the pages |
| `tools/make_calc_data.py` | regenerates the calculator catalogue; **fails** if a row disagrees with Proposition 1 or if no (p,q,r) reproduces its character. Needs `PYTHONPATH` pointing at `Curiosity/research/smeft_formalization/part_v` for `fibre.py`. |

`build_predict.py` injects the engine and the panel code **extracted from `src/calc_shell.html`**,
so pages 2 and 3 cannot drift apart: there is one implementation of V, of the geometry, of the
relief.

## What each tool does

**2 · Calculator.** Type a content — any content — and read the potential over the torus, its
vacuum, the Higgs mass matrix there, the electroweak verdict, which multiplets are blind to η. The
landscape is a control, not a picture: drag any of the three panels and the reading bar reports **at
the cursor**; double-click drops the field there and it rolls; the relief turns; the cut follows.
`▶ show me` runs a 30 s guided tour. Deep links: `calculator.html#c=4,0,0*3;1,0,1*-1`.

**3 · η-meter.** Opens with the answer in one sentence — *flip η and this Higgs gets lighter, by
this much* — computed from **one integer M₂** with no winding summed, next to the brute-force
Hessian that confirms it. The formulas (F1 box, F2 moments, F3 inversion, F4 prediction, F5
blindness, F6 search) are folded below for whoever wants the machinery. It also
**searches**: given your multiplets it finds multiplicities and signs for which the coset index
cancels identically — a content of sighted multiplets that is blind as a whole. And it draws the
**atlas**: 120 landscapes side by side; in η-difference mode every blind multiplet goes blank.

**The anchor travels with the instrument.** Both pages recompute a published case at load and say so
on themselves: the calculator AHMN's vacuum, the η-meter the agreement between its closed form and
the loop sum.

## What the tests caught, and why they exist

- **A real physics bug.** The engine had `Σ = A + ηB`, putting η on the *identity* half; a blind
  multiplet's potential then moved. Right form: `Σ = A+B` with no η, `ηD = η(A−B)` on the coset half.
- **A column that was pure decoration.** The catalogue printed `box (p,q,r)` and called it Part IV's
  closed form. It reproduced the character in **0 of 104** non-blind rows — `sides()` read the
  2-quotient without subtracting the staircase. Replaced by Part IV's own moment inversion, which
  must convolve back to D or the row aborts the build; cross-checked against the explorer's already
  verified `reduction()`, **104/104**. The guard was validated by running it on the old data (fails
  103/104).
- **A test asserting a convention.** It demanded `α₂ = 0.299` and got `0.701`, the reflected image.
  It compares `min(α₂, 1−α₂)` now. Only invariants may be asserted.
- **A vacuous control.** "η moves a sighted multiplet" failed on the singlet, whose only charge is 0.
- **A fold that merged different wells.** The basin panel folded α₁ as well as α₂. Measured: α₂ has
  period 1, **α₁ has period 2** (half-integer charges; only the coset sign compensates in α₂), both
  reflections exact, and [0,1]² is still a fundamental domain. Now asserted, with the control that
  α₁ is *not* 1-periodic.
- **The minimiser stopped one step short.** `|∇V|` at what the page called the vacuum was 0.15.
  A Newton polish on the 2×2 Hessian takes it to ~1e-12, and the AHMN mass ratio to 1.2045 against
  1.2046 published.

## The one new physical statement in these tools

Derived here and checked on the page: at the symmetric point the **entire** η-dependence of the
Higgs mass matrix is one number,

```
ΔH₁₁ = −2(2π)² L₁ · M₂/8      ΔH₂₂ = −2(2π)² L₂ · M₂/8      ΔH₁₂ = 0 exactly
L₁ = Σ_{k₂ odd}|k|⁻⁶k₁² = 0.7249     L₂ = Σ_{k₂ odd}|k|⁻⁶k₂² = 2.6530
```

with `M₂ = M₀·(C_p+C_q+C_r)/3` from Part IV's box — so a model's η-response is arithmetic, and any
content with `M₂ = 0` is invisible to η at this order however large it is. Verified against the
winding sum on five contents to <0.02 % (the residual is the Hessian's finite difference), with the
blind control and its anti-vacuity control.

## Next, in order

1. **Live selection** in the calculator: recompute on change, ~90 ms debounce, `computing…` on the button.
2. **Images first** in the calculator: landscape → numbers → controls. **Edit the HTML by hand** — a
   regex reorder is what broke the page once and forced the revert to `c22be0d`.
3. **ΔV between the two values of η** as a panel — blank exactly on a blind content.
4. `README.md` still says *companion to Part III* (it is now III–V), and its "7904 partitions" does
   not come from the published Part IV, which says **3060** with parts ≤14 and **4845** with parts
   ≤16 — two ranges that are not summed.
5. The η-meter's search is capped at multiplicity 6 and at the multiplets you have added; a sweep
   over the whole catalogue for collectively blind pairs would be a genuine little result.

## The papers behind the three tools

Part III [10.5281/zenodo.21438226](https://doi.org/10.5281/zenodo.21438226) ·
Part IV [10.5281/zenodo.21463000](https://doi.org/10.5281/zenodo.21463000) ·
Part V [10.5281/zenodo.21727094](https://doi.org/10.5281/zenodo.21727094) ·
code for Part V: [higgs-blind-class](https://github.com/karlesmarin/higgs-blind-class)

Honesty labels are load-bearing and must survive edits: **theorem** (blindness, the count, the
census — machine-checked in Lean 4), **verified** (Part IV's closed form and its inversion —
exhaustive, *not proved*), **measured** (vacuum, masses, mixing, and the η-splitting prediction —
one published case plus the loop sum are the whole validation). The sign of the mixing angle is a
convention; only invariants are shown.
