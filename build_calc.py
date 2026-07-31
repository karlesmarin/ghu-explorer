# build_calc.py - assemble the single-file Model Calculator, then TEST its engine headlessly in
#   node against the numbers Python produced for Part V. Same rule as build.py: a browser tool that
#   silently disagrees with the paper it advertises would be worse than no tool.
#   Author: Carles Marin <karlesmarin@gmail.com>  (with Claude, Anthropic, as assistant)
#
# The anchor is AHMN arXiv:2312.08608. Their published vacuum is (0.438, 0.299) and their published
# mass matrix, normalised to m11, is (1, 1.2341, -0.1690) -- eq. (4.2). The Python engine
# (part_v/ghu_potential.py) reproduces the vacuum exactly and the ratio to 0.1%; this test demands
# the JavaScript do the same, because the JS is a SECOND implementation and a second implementation
# is either a control or a liar.
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "src" / "calc_shell.html"
DATA = HERE / "tools" / "calc_data.json"          # regenerate with tools/make_calc_data.py
OUT = HERE / "calculator.html"

blob = DATA.read_text(encoding="utf-8")
html = SRC.read_text(encoding="utf-8")
assert "/*__DATA__*/{}" in html, "data slot missing from calc_shell.html"
html = html.replace("/*__DATA__*/{}", blob)
OUT.write_text(html, encoding="utf-8")
print("built %s  (%.1f KB, self-contained)" % (OUT.name, len(html) / 1024))

# ---- extract the engine and run it in node against the published numbers ----
m = re.search(r"/\* ---------- the engine.*?\*/(.*?)/\* ---------- the catalogue", html, re.S)
assert m, "engine block not found"
engine = m.group(1)

test = """
const DATA = %s;
const KMAX = 10, GRID = 72;
%s
let fail = 0;
const near = (got, want, tol, what) => {
  const ok = Math.abs(got - want) <= tol;
  if (!ok) fail++;
  console.log((ok ? "  ok  " : "  FAIL") + "  " + what.padEnd(34) +
              got.toFixed(4) + "   published " + want.toFixed(4));
};

// 1. the anchor: AHMN's content is 3 x 35 minus the gauge adjoint 15, their eq. (4.1)
const AHMN = [{key:'4,0,0',n:3,eta:1,role:1},{key:'1,0,1',n:1,eta:1,role:-1}];
const sp = spectrum(AHMN);
const [a1, a2] = minimise(sp);
near(a1, 0.438, 0.002, "AHMN vacuum alpha1");
// alpha2 -> -alpha2 is an exact symmetry, so the two images are the same vacuum:
near(Math.min(a2, 1 - a2), 0.299, 0.002, "AHMN vacuum alpha2 (mod reflection)");
const [hxx, hyy, hxy] = hessian(sp, a1, a2);
near(hyy / hxx, 1.2341, 0.02, "mass matrix m22/m11");
near(Math.abs(hxy / hxx), 0.1690, 0.01, "mass matrix |m12|/m11");
const [e1, e2] = eig(hxx, hyy, hxy);
near(Math.sqrt(e1 / e2), 1.2046, 0.01, "Higgs mass ratio");

// 2. the theorem, as the page advertises it: on a content of blind multiplets the boundary sign
//    cannot move ONE number. Not "moves little" -- cannot move.
const blind = Object.keys(DATA.reps).filter(k => DATA.reps[k].blind).slice(0, 6);
let moved = 0;
for (const k of blind) {
  const plus  = spectrum([{key:k,n:1,eta:1,role:1}]);
  const minus = spectrum([{key:k,n:1,eta:-1,role:1}]);
  for (const [x, y] of [[0.13,0.41],[0.5,0.5],[0.77,0.09]])
    if (Math.abs(V(plus,x,y) - V(minus,x,y)) > 1e-12) moved++;
}
if (moved) { fail++; console.log("  FAIL  eta moved the potential on a blind multiplet, " + moved + " times"); }
else console.log("  ok    eta cannot move the potential on any of " + blind.length + " blind multiplets");

// 3. and the control that makes check 2 mean something: on a SIGHTED multiplet it must move
// a multiplet whose only charge is 0 contributes a CONSTANT and cannot move anything --
// excluding it is not weakening the control, it is choosing one that can fail
const sighted = Object.keys(DATA.reps)
  .filter(k => !DATA.reps[k].blind && DATA.reps[k].modes.length).slice(0, 6);
let still = 0;
for (const k of sighted) {
  const plus  = spectrum([{key:k,n:1,eta:1,role:1}]);
  const minus = spectrum([{key:k,n:1,eta:-1,role:1}]);
  if (Math.abs(V(plus,0.13,0.41) - V(minus,0.13,0.41)) < 1e-9) still++;
}
if (still) { fail++; console.log("  FAIL  eta did NOT move " + still + " sighted multiplets -- the test is vacuous"); }
else console.log("  ok    eta does move all " + sighted.length + " sighted multiplets tested");

console.log(fail ? "\\n*** " + fail + " FAILURE(S) ***"
                 : "\\nall checks pass (AHMN anchor + blindness, with its control)");
process.exit(fail ? 1 : 0);
""" % (blob, engine)

(HERE / "_test_calc.mjs").write_text(test, encoding="utf-8")
r = subprocess.run(["node", str(HERE / "_test_calc.mjs")], capture_output=True, text=True)
print(r.stdout or r.stderr[:2000])
sys.exit(r.returncode)
