# build.py - assemble the single-file explorer, then TEST its maths headlessly in node against
#   the values Python produced for the paper. A browser tool that silently disagrees with the
#   paper it advertises would be worse than no tool.
#   Author: Carles Marin <karlesmarin@gmail.com>  (with Claude, Anthropic, as assistant)
import json, pathlib, subprocess, sys, re

HERE = pathlib.Path(__file__).resolve().parent
SRC  = HERE / "src" / "shell.html"
DATA = HERE / "tools" / "su4_data.json"          # regenerate with tools/make_tool_data.sage
OUT  = HERE / "index.html"

blob = DATA.read_text(encoding="utf-8")
html = SRC.read_text(encoding="utf-8")
assert "/*DATA*/" in html, "data slot missing from shell.html"
html = html.replace("/*DATA*/", "const SU4=" + blob + ";")
OUT.write_text(html, encoding="utf-8")
print("built %s  (%.1f KB, self-contained)" % (OUT.name, len(html) / 1024))

# ---- extract the computation and run it in node against the paper's numbers ----
m = re.search(r"/\* ---------- maths ---------- \*/(.*?)/\* ---------- palette", html, re.S)
assert m, "maths block not found"
maths = m.group(1)

QUOTED_PERIOD = {"4,0,0":0.000,"0,2,1":0.296,"0,1,3":0.210,"1,1,2":0.045,"0,3,1":0.124,
                 "0,4,1":0.118,"1,2,2":0.095,"0,2,3":0.194,"1,3,2":0.023}

test = """
const SU4 = %s;
%s
const NG=104, KMAX=5;
let fail=0;
const want=%s;
for(const k in want){
  const h=SU4.reps[k].h, C=coeffs(h), V=field(C,NG);
  let mean=0; for(const v of V) mean+=v; mean/=V.length;
  let scale=0; for(const v of V) scale=Math.max(scale,Math.abs(v-mean));
  let mx=0;
  for(let i=0;i<NG;i++)for(let j=0;j<NG;j++)
    mx=Math.max(mx,Math.abs(V[i*NG+((j+NG/2)|0)%%NG]-V[i*NG+j]));
  const got=mx/scale, w=want[k], ok=Math.abs(got-w)<0.02;
  if(!ok) fail++;
  console.log((ok?"  ok  ":"  FAIL") + "  " + k.padEnd(8) +
              " period-1 residual " + got.toFixed(3) + "  paper says " + w.toFixed(3));
}
// the notch itself: delta(m) must vanish on even m exactly when a+2b+3c is odd
for(const k in SU4.reps){
  const [a,b,c]=k.split(",").map(Number), d=delta(SU4.reps[k].h);
  const evenZero=Object.keys(d).map(Number).filter(m=>((m%%2)+2)%%2===0).every(m=>d[m]===0);
  const deg=(b%%2===1)&&(((a%%2===1)&&(c%%2===1))||a===c);
  const want=(((a+2*b+3*c)%%2)===1)||deg;
  if(evenZero!==want){ fail++; console.log("  FAIL  notch mismatch at "+k); }
}
console.log(fail? "\\n*** "+fail+" FAILURE(S) ***" : "\\nall checks pass (119 reps + 9 residuals)");
process.exit(fail?1:0);
""" % (blob, maths, json.dumps(QUOTED_PERIOD))

(HERE / "_test.mjs").write_text(test, encoding="utf-8")
r = subprocess.run(["node", str(HERE / "_test.mjs")], capture_output=True, text=True)
print(r.stdout or r.stderr[:2000])
sys.exit(r.returncode)
