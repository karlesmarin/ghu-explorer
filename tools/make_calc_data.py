#!/usr/bin/env python3
"""make_calc_data.py - the options table for the model calculator, as a separate file.

  Author: Carles Marin <karlesmarin@gmail.com>  (with Claude, Anthropic, as assistant)

The page is the instrument; this is its catalogue, and it lives apart from it on purpose. Every row
is computed from the VERIFIED characters of Part V -- `fibre.schur` on the two alphabets -- and not
from any hand-kept list:

    Sigma_lambda = s_lambda(1, 1,t,1/t)   the identity component, a graded dimension
    D_lambda     = s_lambda(1,-1,t,1/t)   the reflection coset,   an index

Per irrep, keyed by the Dynkin labels (a,b,c) so the page can look one up from the labels alone:

    dim     the dimension, as the sum of the mode counts (a free control: it must come out right)
    modes   [charge, A, B] with A = (Sigma+D)/2 and B = (Sigma-D)/2, the parity-even and
            parity-odd mode counts -- exactly the pair AHMN write as {A + B(-1)^k2}
    blind   D vanishes identically: the boundary sign is invisible on this multiplet (Part V)
    sides   the three SU(2) character indices of Part IV's closed form, read off the 2-quotient
    zeta    its global sign

`blind` is computed twice by different routes -- the character being empty, and the closed
criterion on the partition -- and the two must agree on every row or this script fails. A
catalogue that disagrees with the theorem it illustrates is worse than no catalogue.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fibre import schur, EVEN, ODD

MAXSUM = int(os.environ.get("CALC_MAXSUM", 7))     # a+b+c <= 7, as the Part III explorer uses
MAXDIM = int(os.environ.get("CALC_MAXDIM", 3000))


def lam_of(a, b, c):
    return [a + b + c, b + c, c, 0]


def blind_by_criterion(lam):
    """Proposition 1 of Part V, in partition coordinates -- the machine-checked branches."""
    l1, l2, l3, _ = lam
    return (l1 % 2 == 1 and l2 % 2 == 0 and l3 % 2 == 1) or \
           (l1 % 2 == 1 and l2 % 2 == 1 and l3 % 2 == 0 and l2 + l3 == l1)


def chi(k):
    """The SU(2) character of highest weight k, as its weight multiplicities."""
    return {k - 2 * i: 1 for i in range(k + 1)}


def convolve(*factors):
    out = {0: 1}
    for f in factors:
        nxt = {}
        for a, va in out.items():
            for b, vb in f.items():
                nxt[a + b] = nxt.get(a + b, 0) + va * vb
        out = nxt
    return out


def box_of(D):
    """Part IV's three indices (p,q,r) of D = zeta * chi_p * chi_q * chi_r, recovered from the
    character by the paper's own inversion and then CHECKED against it.

    The previous version of this function read a triple off the 2-quotient of the beta set and
    nobody ever asked it to reproduce D. It does not: on the 104 non-blind rows of this catalogue
    its triple reproduced the character in ZERO cases, while the triple below reproduces it in all
    104. Proposition "the compression is lossless and invertible" of Part IV pins the multiset:
    e1 = 3 M2/M0 is the sum of the Casimirs C_k = k(k+2), and |M0| = (p+1)(q+1)(r+1). We solve
    those two conditions over the integers and then demand the convolution BE the character --
    a triple that does not is not returned at all.

    Returns (p, q, r, zeta) with p >= q >= r, or None when D is empty (a blind multiplet).
    """
    d = {j: v for j, v in D.items() if v}
    if not d:
        return None
    M0 = sum(d.values())
    M2 = sum(j * j * v for j, v in d.items())
    if M0 == 0:
        return None                       # would not be a single box; the catalogue has none
    e1, rem = divmod(3 * M2, M0)
    if rem:
        return None
    top = max(abs(j) for j in d)          # p+q+r, the support of the convolution
    for p in range(top + 1):
        for q in range(p + 1):
            for r in range(q + 1):
                if (p + 1) * (q + 1) * (r + 1) != abs(M0):
                    continue
                if p * (p + 2) + q * (q + 2) + r * (r + 2) != e1:
                    continue
                prod = convolve(chi(p), chi(q), chi(r))
                for zeta in (1, -1):
                    if all(d.get(k, 0) == zeta * prod.get(k, 0)
                           for k in set(d) | set(prod)):
                        return (p, q, r, zeta)
    return None


def main():
    reps, bad = {}, []
    for a in range(MAXSUM + 1):
        for b in range(MAXSUM + 1 - a):
            for c in range(MAXSUM + 1 - a - b):
                lam = lam_of(a, b, c)
                S, D = schur(lam, EVEN), schur(lam, ODD)
                modes = []
                dim = 0
                for j in sorted(set(S) | set(D)):
                    s, d = S.get(j, 0), D.get(j, 0)
                    A, B = (s + d) // 2, (s - d) // 2
                    dim += A + B
                    if j > 0:
                        modes.append([j / 2.0, A, B])
                if dim > MAXDIM or dim == 0:
                    continue
                blind = not any(v for v in D.values())
                if blind != blind_by_criterion(lam):
                    bad.append("(%d,%d,%d): character says %s, criterion says %s"
                               % (a, b, c, blind, blind_by_criterion(lam)))
                box = None if blind else box_of(D)
                if not blind and box is None:
                    bad.append("(%d,%d,%d): no (p,q,r) reproduces D -- Part IV's closed form "
                               "fails on this row" % (a, b, c))
                # the moments of the coset index, straight from the character. The predictor page
                # computes these from the BOX alone (Part IV) and is checked against these numbers,
                # so they are the truth column of that comparison and must not be derived from it.
                mom = [sum(j ** e * v for j, v in D.items()) for e in (0, 2, 4)]
                reps["%d,%d,%d" % (a, b, c)] = {
                    "dim": dim, "modes": modes, "blind": blind,
                    "sides": None if box is None else list(box[:3]),
                    "zeta": 0 if box is None else box[3],
                    "m": mom,
                }
    if bad:
        sys.exit("FATAL: catalogue disagrees with Proposition 1 on %d rows:\n  %s"
                 % (len(bad), "\n  ".join(bad[:5])))
    out = {
        "note": "Part V options table. modes = [charge, A, B]; A+B(-1)^k2 is AHMN's coefficient. "
                "blind = the boundary sign is invisible on this multiplet (Part V, Lean-checked). "
                "Generated by make_calc_data.py from the verified characters; do not hand-edit.",
        "maxsum": MAXSUM, "maxdim": MAXDIM,
        "adjoint": "1,1,0" if "1,1,0" in reps else None,
        "reps": reps,
    }
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calc_data.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, separators=(",", ":"), sort_keys=True)
    nb = sum(1 for r in reps.values() if r["blind"])
    print("%d irreps (a+b+c <= %d, dim <= %d), %d blind, %d sighted"
          % (len(reps), MAXSUM, MAXDIM, nb, len(reps) - nb))
    print("catalogue agrees with Proposition 1 on every row")
    print("written: %s (%d bytes)" % (p, os.path.getsize(p)))


if __name__ == "__main__":
    main()
