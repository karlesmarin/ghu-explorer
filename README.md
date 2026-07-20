# 🧭 Orbifold Explorer — SU(4) gauge–Higgs on T²/Z₂

**▶️ [karlesmarin.github.io/ghu-explorer](https://karlesmarin.github.io/ghu-explorer/)**

A single self-contained HTML file. Open `index.html`; no server, no install, no network.
Nothing you type leaves the page.

**What it is for.** If you compute a one-loop Wilson-line potential on T²/Z₂, you probably
halve the search region in α₂. For every representation able to host a Standard-Model quark
generation that halving is invalid, and nothing warns you — a restricted minimiser returns a
boundary point that looks like a vacuum. This page shows you, rather than telling you.

Pick a representation and the potential redraws over the full period-2 torus, the twist
imbalance δ(m) shows which comb of teeth vanishes, the Fourier panel shows the seats that stay
identically empty, and the verdict says which region you may legally search.

**The honest part.** Everything computed from Dynkin labels is a *theorem*, and only for SU(4)
on T²/Z₂. For any other spectrum there is no theorem, so the bottom panel *measures* the two
pairings from an (m,q) table you paste, or tells you from your group's alphabet whether a
centre-parity rule exists at all. Outputs are labelled `theorem`, `measured` or `conjecture`.
The page computes the one-loop potential and where it may be searched; it does not compute a
Higgs mass, which at this order is degenerate by the same theorem.

## 🔧 Build

```
python build.py
```

Inlines `tools/su4_data.json` (119 irreps with a+b+c ≤ 7 and dim ≤ 3000, regenerate with
`sage tools/make_tool_data.sage`) into `src/shell.html`, then **runs the page's own
mathematics headlessly in node and checks it against the numbers in the paper** — the nine
period-1 residuals, and the notch predicate across all 119 representations. A browser tool
that quietly disagreed with the paper it advertises would be worse than no tool, so the build
fails if it does.

## 🎯 The result behind it

Advancing the Wilson line by one period is, up to a Weyl reflection, multiplication by the
central element −**1** ∈ Z(SU(4)). A representation answers with the scalar (−1)^(a+2b+3c),
so the harmonics carrying the opposite sign are identically absent — not suppressed, absent.

## 📚 The series

This explorer accompanies **Part III**. The full arc:

- **Part I — *Anomaly- and Tadpole-Compatible Fermion Completion of 6D SU(4) GHU***
  → [github.com/karlesmarin/ghu-su4-completion](https://github.com/karlesmarin/ghu-su4-completion) · [Zenodo 10.5281/zenodo.21432625](https://doi.org/10.5281/zenodo.21432625)
- **Part II — *Three Gates to a Quark Generation***
  → [github.com/karlesmarin/su4-sm-cell-criterion](https://github.com/karlesmarin/su4-sm-cell-criterion) · [Zenodo 10.5281/zenodo.21432627](https://doi.org/10.5281/zenodo.21432627)
- **Part III — *A Centre-Charge Selection Rule for the Wilson-Line Potential*** (this explorer)
  → [github.com/karlesmarin/centre-parity-selection](https://github.com/karlesmarin/centre-parity-selection) · [Zenodo 10.5281/zenodo.21438226](https://doi.org/10.5281/zenodo.21438226)
- **Part IV — *Schur Functions at (1,−1,t,t⁻¹)***
  → [github.com/karlesmarin/schur-nonidentity-o4](https://github.com/karlesmarin/schur-nonidentity-o4) · [Zenodo 10.5281/zenodo.21463000](https://doi.org/10.5281/zenodo.21463000)

---

Carles Marín · `karlesmarin@gmail.com` · Claude (Anthropic) as AI research assistant
