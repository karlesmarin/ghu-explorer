# build_predict.py - assemble the eta-meter, the third tool, and TEST it in node.
#   Author: Carles Marin <karlesmarin@gmail.com>  (with Claude, Anthropic, as assistant)
#
# This page makes a prediction and then checks itself against the brute force, on screen. So the
# build has to hold it to exactly that: the closed form of Part IV must reproduce the moments the
# character gives, the inversion must give the box back, and the eta-splitting predicted from ONE
# number must be the splitting the winding sum actually produces. Anything less and the page is
# advertising a theorem it cannot demonstrate.
#
# The engine and the panels are not copied here: they are extracted from src/calc_shell.html at
# build time, so the two pages cannot drift apart.
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "src" / "predict_shell.html"
CALC = HERE / "src" / "calc_shell.html"
DATA = HERE / "tools" / "calc_data.json"
OUT = HERE / "predictor.html"


def block(text, start, end):
    m = re.search(re.escape(start) + r"(.*?)" + re.escape(end), text, re.S)
    assert m, "block not found: %s" % start
    return m.group(1)


calc = CALC.read_text(encoding="utf-8")
engine = block(calc, "/* ---------- the engine", "/* ---------- the catalogue")
panels = block(calc, "/* ---------- the panels", "/* ---------- the self-check")
engine = "/* ---------- the engine" + engine
panels = "/* ---------- the panels" + panels

blob = DATA.read_text(encoding="utf-8")
html = SRC.read_text(encoding="utf-8")
for slot, piece in (("/*__DATA__*/{}", blob), ("/*__ENGINE__*/", engine), ("/*__PANELS__*/", panels)):
    assert slot in html, "slot missing from predict_shell.html: %s" % slot
    html = html.replace(slot, piece)
OUT.write_text(html, encoding="utf-8")
print("built %s  (%.1f KB, self-contained)" % (OUT.name, len(html) / 1024))

# ---- the page's own claims, run headlessly ----
maths = "/* ---------- the closed form" + block(html, "/* ---------- the closed form", "/* ---------- the page")

test = """
const DATA = %s;
const KMAX = 10, GRID = 72;
%s
%s
let fail = 0;
const near = (got, want, tol, what) => {
  const ok = Math.abs(got - want) <= tol;
  if (!ok) fail++;
  console.log((ok ? "  ok  " : "  FAIL") + "  " + what.padEnd(38) +
              got.toFixed(4) + "   truth " + want.toFixed(4));
};

// 1. Part IV's closed form for the moments, against the moments of the character itself.
//    M0 = zeta (p+1)(q+1)(r+1),  M2/M0 = e1/3,  M4/M0 = (2/3)e2 + (1/5) sum C^2 - (4/15) e1.
let m0bad = 0, m2bad = 0, m4bad = 0, n = 0;
for (const [key, r] of Object.entries(DATA.reps)) {
  if (r.blind) { if (r.m[0] || r.m[1] || r.m[2]) { fail++; console.log("  FAIL  blind row with moments: " + key); } continue; }
  n++;
  const [M0, M2, M4] = momentsOfBox(r.sides, r.zeta);
  if (M0 !== r.m[0]) m0bad++;
  if (Math.abs(M2 - r.m[1]) > 1e-9) m2bad++;
  if (Math.abs(M4 - r.m[2]) > 1e-9) m4bad++;
}
if (m0bad || m2bad || m4bad) {
  fail++;
  console.log("  FAIL  closed-form moments wrong on M0/" + m0bad + " M2/" + m2bad + " M4/" + m4bad + " of " + n);
} else console.log("  ok    M0, M2, M4 from the box match the character on all " + n + " sighted rows");

// 2. and backwards: three moments give the box back (Part IV, the inversion).
let invbad = 0;
for (const [key, r] of Object.entries(DATA.reps)) {
  if (r.blind) continue;
  const got = boxFromMoments(r.m[0], r.m[1], r.m[2]);
  if (!got || got.join() !== r.sides.slice().sort((a, b) => b - a).join()) invbad++;
}
if (invbad) { fail++; console.log("  FAIL  the inversion misses the box on " + invbad + " rows"); }
else console.log("  ok    M0,M2,M4 -> (p,q,r) recovers the box on all " + n + " sighted rows");

// 3. THE PREDICTION. The eta-splitting of the Higgs mass matrix at the origin, from M2 alone and
//    two lattice constants, against the same splitting computed by brute force from the potential.
const CONTENTS = [
  [{key:'4,0,0',n:3,eta:1,role:1},{key:'1,0,1',n:1,eta:1,role:-1}],     // AHMN
  [{key:'4,0,0',n:1,eta:1,role:1}],
  [{key:'1,0,1',n:1,eta:1,role:-1}],
  [{key:'0,0,2',n:2,eta:-1,role:1},{key:'2,0,0',n:1,eta:1,role:1},{key:'1,0,1',n:1,eta:1,role:-1}],
  [{key:'0,2,0',n:1,eta:1,role:1},{key:'4,0,0',n:2,eta:-1,role:1}],
];
for (let i = 0; i < CONTENTS.length; i++) {
  const rows = CONTENTS[i];
  const P = predict(rows);                                    // closed form: no winding sum at all
  const plus  = spectrum(rows.map(r => ({...r, eta:  r.eta})));
  const minus = spectrum(rows.map(r => ({...r, eta: -r.eta})));
  const hp = hessian(plus, 0, 0), hm = hessian(minus, 0, 0);
  const meas = [hp[0] - hm[0], hp[1] - hm[1], hp[2] - hm[2]];
  const tol = v => Math.max(2e-3 * Math.abs(v), 1e-6);
  near(P.dHxx, meas[0], tol(meas[0]), "content " + i + ": eta-split of Vxx");
  near(P.dHyy, meas[1], tol(meas[1]), "content " + i + ": eta-split of Vyy");
  near(P.dHxy, meas[2], 1e-6,         "content " + i + ": eta-split of Vxy (must be 0)");
}

// 4. the control that makes 3 mean something: a BLIND content must predict, and measure, zero.
const blindKeys = Object.keys(DATA.reps).filter(k => DATA.reps[k].blind).slice(0, 4);
const blindRows = blindKeys.map(k => ({key: k, n: 1, eta: 1, role: 1}));
const Pb = predict(blindRows);
const hbp = hessian(spectrum(blindRows), 0, 0);
const hbm = hessian(spectrum(blindRows.map(r => ({...r, eta: -1}))), 0, 0);
const moved = Math.max(...[0,1,2].map(i => Math.abs(hbp[i] - hbm[i])));
if (Math.abs(Pb.M2) > 1e-12 || moved > 1e-9) {
  fail++; console.log("  FAIL  a blind content predicted " + Pb.M2 + " and moved " + moved);
} else console.log("  ok    blind content: M2 = 0 predicted, and the brute force does not move");

// 5. and its own control: a SIGHTED content must have a non-zero prediction, or check 4 is vacuous.
const sighted = predict([{key:'4,0,0',n:1,eta:1,role:1}]);
if (Math.abs(sighted.dHxx) < 1e-6) { fail++; console.log("  FAIL  the prediction is identically zero -- check 4 proves nothing"); }
else console.log("  ok    a sighted content predicts a non-zero splitting (" + sighted.dHxx.toFixed(2) + ")");

// 6. F6 claims it can find a content of SIGHTED multiplets that is blind as a whole. That is a
//    strong claim, so it is checked the hard way: the combination it returns must make the brute
//    force refuse to move under a flip of eta, and the multiplets in it must each move on their own.
const cand = ['4,0,0', '0,0,4'];                 // two different 35s -- the search decides the rest
const sol = searchBlind(cand);
if (sol.none) { fail++; console.log("  FAIL  the search found nothing on " + cand.join(' + ')); }
else {
  const rws = sol.keys.map((k, i) => ({key: k, n: Math.abs(sol.combo[i]),
                                       eta: sol.combo[i] > 0 ? 1 : -1, role: 1}));
  const P = predict(rws);
  const hp = hessian(spectrum(rws), 0.11, 0.37);
  const hm = hessian(spectrum(rws.map(r => ({...r, eta: -r.eta}))), 0.11, 0.37);
  const vp = V(spectrum(rws), 0.11, 0.37), vm = V(spectrum(rws.map(r => ({...r, eta: -r.eta}))), 0.11, 0.37);
  const moved = Math.max(Math.abs(vp - vm), ...[0,1,2].map(i => Math.abs(hp[i] - hm[i])));
  const eachMoves = sol.keys.every(k => {
    const one = [{key: k, n: 1, eta: 1, role: 1}];
    return Math.abs(V(spectrum(one), 0.11, 0.37) -
                    V(spectrum(one.map(r => ({...r, eta: -1}))), 0.11, 0.37)) > 1e-9;
  });
  if (Math.abs(P.M2) > 1e-12 || moved > 1e-9 || !eachMoves) {
    fail++;
    console.log("  FAIL  collective blindness is wrong: M2=" + P.M2 + " moved=" + moved + " eachMoves=" + eachMoves);
  } else {
    console.log("  ok    collective blindness: " +
      sol.keys.map((k, i) => Math.abs(sol.combo[i]) + "x(" + k + ") eta=" + (sol.combo[i] > 0 ? "+1" : "-1")).join(" + ") +
      " -- each multiplet sees eta, the content does not");
  }
}

// 7. the conventions every panel rests on, MEASURED. The square the pages draw is alpha in [0,1]^2
//    and the basin panel folds points onto each other; both are only honest if these hold.
const spA = spectrum(CONTENTS[0]);
for (const [x, y] of [[0.13, 0.41], [0.77, 0.09]]) {
  const v0 = V(spA, x, y);
  near(V(spA, x, 1 - y), v0, 1e-9, "alpha2 -> -alpha2 exact at " + x);
  near(V(spA, -x, -y),   v0, 1e-9, "alpha -> -alpha exact at " + x);
  near(V(spA, x, y + 1), v0, 1e-9, "period 1 in alpha2 at " + x);
  near(V(spA, x + 2, y), v0, 1e-6, "period 2 in alpha1 at " + x);
}
// the control: the period in alpha1 is NOT 1. If it were, "period 2" above would say nothing.
if (Math.abs(V(spA, 1.13, 0.41) - V(spA, 0.13, 0.41)) < 1e-6) {
  fail++; console.log("  FAIL  alpha1 turns out to be 1-periodic -- the domain claim is vacuous");
} else console.log("  ok    alpha1 is NOT 1-periodic (the charges are half-integers), so 2 is the period");
// and the consequence the pages depend on: scanning [0,1]^2 misses no vacuum, because the other
// half of the alpha1 period is the mirror image of the one drawn.
let inside = Infinity, outside = Infinity;
for (let i = 0; i <= 200; i++) for (let j = 0; j <= 100; j++) {
  const x = 2 * i / 200, v = V(spA, x, j / 100);
  if (x <= 1) inside = Math.min(inside, v); else outside = Math.min(outside, v);
}
if (outside < inside - 1e-6) { fail++; console.log("  FAIL  a deeper vacuum lives outside the drawn square: " + outside + " < " + inside); }
else console.log("  ok    [0,1]^2 is a fundamental domain: nothing deeper in the half not drawn");

console.log(fail ? "\\n*** " + fail + " FAILURE(S) ***"
                 : "\\nall checks pass (closed form + inversion + prediction vs brute force)");
process.exit(fail ? 1 : 0);
""" % (blob, engine, maths)

(HERE / "_test_predict.mjs").write_text(test, encoding="utf-8")
r = subprocess.run(["node", str(HERE / "_test_predict.mjs")], capture_output=True, text=True)
print(r.stdout or r.stderr[:2000])
sys.exit(r.returncode)
