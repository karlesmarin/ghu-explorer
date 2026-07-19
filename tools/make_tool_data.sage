# make_tool_data.sage - precompute the (m,q) weight histograms the browser tool needs, so the
#   page can draw the potential and the Fourier support live with no server and no dependencies.
#   Author: Carles Marin <karlesmarin@gmail.com>  (with Claude, Anthropic, as assistant)
import json
A3 = WeylCharacterRing("A3", style="coroots")

MAXL   = 7      # a+b+c <= MAXL
MAXDIM = 3000

def hist_mq(L):
    boxes = sum((i+1)*L[i] for i in range(3)); h = {}
    for w, mult in A3(*L).weight_multiplicities().items():
        n = [ZZ(w[i] + QQ(boxes)/4) for i in range(4)]
        k = "%d,%d" % (int(n[1]-n[3]), int(n[2] % 2))
        h[k] = int(h.get(k, 0) + int(mult))
    return h

out = {}
for a in range(MAXL+1):
    for b in range(MAXL+1):
        for c in range(MAXL+1):
            if not (1 <= a+b+c <= MAXL): continue
            d = int(A3(a,b,c).degree())
            if d > MAXDIM: continue
            h = {str(k): int(v) for k, v in hist_mq((a,b,c)).items()}
            out["%d,%d,%d" % (int(a),int(b),int(c))] = {"dim": int(d), "h": h}

# the gauge adjoint enters every potential with the opposite loop sign
GAUGE = {k: int(v) for k, v in
         {"1,0":2, "-1,0":2, "1,1":2, "-1,1":2, "2,0":1, "0,0":1, "-2,0":1}.items()}
blob = {"reps": out, "gauge": GAUGE, "wg": float(0.35),
        "note": "(m,q) histograms for SU(4) irreps, m = n2-n4, q = n3 mod 2; "
                "gauge is the calibrated VEV-dependent adjoint list with weight wg."}
open("tools/su4_data.json", "w").write(json.dumps(blob, separators=(",", ":")))
print("wrote tools/su4_data.json:", len(out), "reps, max dim", MAXDIM)
print("sample:", sorted(out)[:6])
