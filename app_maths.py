"""APP MATHS - meme agent, autre cours : calcul differentiel.
Preuve d'adaptabilite : DOSSIER=cours_maths/ seul, outils derives/integrales/limites/graphe,
interface sans boutons code, equations LaTeX (MathJax) + graphiques matplotlib.
Lancer : python app_maths.py -> http://127.0.0.1:3001"""
import pathlib, re, json, io, base64, sys, requests
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL = "llama3.2:latest"
URL = "http://127.0.0.1:11434/api/chat"
PORT = 3001
DOSSIER = pathlib.Path("cours_maths")
SYSTEM = ("Tu es tuteur de calcul differentiel. Tu reponds UNIQUEMENT d'apres le resultat "
          "de l'outil lire_maths. Cite la SOURCE. Les calculs fournis sont deja verifies, recopie-les tels quels.")

def lire_docx(p):
    import zipfile
    x = zipfile.ZipFile(p).read("word/document.xml").decode("utf-8")
    return re.sub(r"<[^>]+>", "", re.sub(r"</w:p[^>]*>", "\n", x))

def lire_dossier():
    tout = ""
    if not DOSSIER.exists(): return "Aucun doc maths."
    for d in sorted(DOSSIER.rglob("*.docx")):
        try: tout += f"\n\n=== SOURCE: {d.name} ===\n" + lire_docx(d)[:5000]
        except Exception: pass
    for t in sorted(DOSSIER.rglob("*.txt")):
        try: tout += f"\n\n=== SOURCE: {t.name} ===\n" + t.read_text(encoding="utf-8")[:5000]
        except Exception: pass
    return tout[:16000] if tout.strip() else "Aucun doc maths."

def passages(q, gros, max_car=3000):
    mots = [w.lower() for w in re.findall(r"[a-zA-Zéèêàç]{4,}", q)]
    STOP = {"cours", "quoi", "quand", "comment", "avec", "faire", "donne", "quelle"}
    rares = [m for m in mots if m not in STOP] or mots
    paras = [p.strip() for p in re.split(r"\n+", gros) if len(p.strip()) > 30]
    src, notes = "?", []
    for p in paras:
        if p.startswith("=== SOURCE:"): src = p; continue
        pl = p.lower()
        if any(m in pl for m in rares): notes.append(f"[{src}] {p}")
    out = "\n".join(notes)[:max_car]
    return out if out.strip() else "\n".join(paras[:10])[:max_car]

def demander_llm(question, contexte):
    r = requests.post(URL, json={"model": MODEL, "messages": [
        {"role": "system", "content": SYSTEM}, {"role": "user", "content": question},
        {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": "lire_maths", "arguments": {}}}]},
        {"role": "tool", "content": contexte}],
        "stream": False, "options": {"temperature": 0.0}}, timeout=120).json()["message"]
    return r.get("content") or ""

# ---------- OUTILS CALCUL (Python verifie, LaTeX affiche) ----------
def _expr(s):
    import sympy as sp
    x = sp.Symbol("x")
    return sp.sympify(s.replace("^", "**")), x

def expliquer_ia(operation, expression, resultat_latex):
    # Hybride : Python a calcule (vrai), l'IA explique la methode (verrouillee).
    try:
        ctx = passages(operation + " " + expression, lire_dossier(), 1500)
        r = requests.post(URL, json={"model": MODEL, "messages": [
            {"role": "system", "content": "Tuteur de maths. Explique la METHODE en 3 lignes max a partir du COURS et du RESULTAT fourni. Recopie le resultat tel quel, ne le recalcule jamais, n'invente aucune autre valeur."},
            {"role": "user", "content": f"OPERATION: {operation} de {expression}\nRESULTAT VERIFIE: ${resultat_latex}$\nCOURS:\n{ctx}\nExplique les etapes a l'etudiant."}],
            "stream": False, "options": {"temperature": 0.2}}, timeout=90).json()["message"]
        return "\n\nEXPLICATION IA (verrouillee) :\n" + (r.get("content") or "")
    except Exception as e:
        return f"\n\nIA indisponible ({e}) - le resultat Python ci-dessus reste valable."

def derivee(s):
    import sympy as sp
    try:
        e, x = _expr(s)
        d = sp.diff(e, x)
        return {"ok": True, "txt": f"Dérivée de ${sp.latex(e)}$ : $${sp.latex(d)}$$", "latex": sp.latex(d)}
    except Exception as e: return {"ok": False, "txt": f"Expression illisible : {e}"}

def integrale(s):
    import sympy as sp
    try:
        e, x = _expr(s)
        res = sp.integrate(e, x)
        return {"ok": True, "txt": f"Primitive de ${sp.latex(e)}$ : $${sp.latex(res)} + C$$", "latex": sp.latex(res)}
    except Exception as e: return {"ok": False, "txt": f"Expression illisible : {e}"}

def limite(s):
    import sympy as sp
    try:
        e, x = _expr(s)
        res = sp.limit(e, x, 0)
        return {"ok": True, "txt": f"Limite en 0 de ${sp.latex(e)}$ : $${sp.latex(res)}$$", "latex": sp.latex(res)}
    except Exception as e: return {"ok": False, "txt": f"Expression illisible : {e}"}

def graphe(s):
    try:
        import sympy as sp
        import numpy as np
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        e, x = _expr(s)
        f = sp.lambdify(x, e, "numpy")
        xs = np.linspace(-5, 5, 400)
        ys = f(xs)
        fig, ax = plt.subplots()
        ax.plot(xs, ys)
        ax.axhline(0, linewidth=0.8); ax.axvline(0, linewidth=0.8)
        ax.set_title(f"y = {s}")
        buf = io.BytesIO(); fig.savefig(buf, format="png", bbox_inches="tight"); plt.close(fig)
        return {"ok": True, "img": base64.b64encode(buf.getvalue()).decode()}
    except Exception as e: return {"ok": False, "txt": f"Graphe impossible : {e}"}

PAGE = """<!DOCTYPE html><html lang=fr><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<link rel='stylesheet' href='/app.css'>
<script defer src='/mathjax.js'></script>
<title>Agent Maths - Calcul differentiel</title></head>
<body class='bg-indigo-50 min-h-screen'><div class='max-w-4xl mx-auto p-4'>
<header class='bg-indigo-900 text-white rounded-2xl p-5 mb-4'>
<h1 class='text-xl font-bold'>Agent Maths - Calcul differentiel</h1>
<p class='text-sm text-indigo-200'>Meme agent que React : LLM + Python + RAG, mais DOSSIER=cours_maths/, outils derivee/integrale/limite/graphe, LaTeX + courbes.</p>
<div class='mt-3 flex flex-wrap gap-2'>
<button onclick="go('derive')" class='bg-emerald-400 text-black px-3 py-1 rounded'>Derivee</button>
<button onclick="go('integre')" class='bg-sky-400 text-black px-3 py-1 rounded'>Integrale</button>
<button onclick="go('limite')" class='bg-amber-400 text-black px-3 py-1 rounded'>Limite en 0</button>
<button onclick="go('graphe')" class='bg-fuchsia-400 text-black px-3 py-1 rounded'>Tracer graphe</button>
<button onclick="cours()" class='bg-white text-black px-3 py-1 rounded'>Question cours</button>
</div></header>
<main class='bg-white rounded-2xl p-4 shadow'>
<input id='e' class='w-full border rounded p-2' value='x**3 + 2*x' placeholder="Expression en x, ex: x**3 + 2*x, sin(x), ln(x+1)">
<input id='q' class='w-full border rounded p-2 mt-2' placeholder="Question cours, ex: definition de la derivee ?">
<pre id='r' class='mt-4 bg-slate-900 text-green-200 p-3 rounded-xl whitespace-pre-wrap text-sm'>Entrez une expression, choisissez un outil.</pre>
<div id='src' class='mt-2 text-xs'></div>
<img id='g' class='mt-2 max-w-full hidden border rounded'>
</main></div>
<script>
async function post(d){let x=await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});return x.json();}
async function go(a){r.textContent='...';g.classList.add('hidden');let j=await post({a:a,e:e.value});r.textContent=j.txt;if(j.latex){r.innerHTML=j.txt+'<br>$$'+j.latex+'$$';}if(j.img){g.src='data:image/png;base64,'+j.img;g.classList.remove('hidden');}if(window.MathJax){MathJax.typesetPromise();}showsrc(j);}
async function cours(){r.textContent='...';g.classList.add('hidden');let j=await post({a:'cours',q:q.value||e.value});r.textContent=j.txt;showsrc(j);if(window.MathJax){MathJax.typesetPromise();}}
function showsrc(j){src.innerHTML=(j.sources&&j.sources.length)?'<b>Sources (cours_maths/) :</b> '+j.sources.map(x=>"<span class=inline-block bg-indigo-100 border border-indigo-500 rounded px-2 py-0.5 m-0.5>"+x+"</span>").join(''):'';}
</script></body></html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        p = self.path.split("?")[0]
        if p in ("/app.css", "/mathjax.js"):
            rel = "static/app.css" if p == "/app.css" else "static/mathjax-tex-svg.js"
            typ = "text/css; charset=utf-8" if p == "/app.css" else "application/javascript; charset=utf-8"
            base = pathlib.Path(getattr(sys, "_MEIPASS", "."))
            try: b = (base / rel).read_bytes()
            except Exception: b = b""
            self.send_response(200); self.send_header("Content-type", typ)
            self.send_header("Cache-Control", "max-age=600")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
            return
        b = PAGE.encode("utf-8")
        self.send_response(200); self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store"); self.send_header("Pragma", "no-cache")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_POST(self):
        import sympy  # noqa: precharge verifiee
        n = int(self.headers.get("Content-Length", 0))
        d = json.loads(self.rfile.read(n).decode("utf-8"))
        a = d.get("a")
        if a == "derive":
            r = derivee(d.get("e", ""))
            txt = "[derivee Python + IA explique]\n" + r.get("txt", "")
            if r.get("ok"): txt += expliquer_ia("derivee", d.get("e", ""), r["latex"])
            out = {"txt": txt, "latex": r.get("latex"), "sources": ["sympy.diff (verifie)", "llama3.2 (explication)"]}
        elif a == "integre":
            r = integrale(d.get("e", ""))
            txt = "[integrale Python + IA explique]\n" + r.get("txt", "")
            if r.get("ok"): txt += expliquer_ia("integrale", d.get("e", ""), r["latex"])
            out = {"txt": txt, "latex": r.get("latex"), "sources": ["sympy.integrate (verifie)", "llama3.2 (explication)"]}
        elif a == "limite":
            r = limite(d.get("e", ""))
            txt = "[limite Python + IA explique]\n" + r.get("txt", "")
            if r.get("ok"): txt += expliquer_ia("limite en 0", d.get("e", ""), r["latex"])
            out = {"txt": txt, "latex": r.get("latex"), "sources": ["sympy.limit (verifie)", "llama3.2 (explication)"]}
        elif a == "graphe":
            r = graphe(d.get("e", ""))
            if r.get("ok"):
                txt = "[graphe matplotlib + IA lit]\nCourbe y = " + d.get("e", "") + expliquer_ia("lecture de graphe", d.get("e", ""), "courbe affichee ci-dessus")
                out = {"txt": txt, "img": r.get("img"), "sources": ["matplotlib (verifie)", "llama3.2 (lecture)"]}
            else: out = {"txt": r.get("txt", ""), "sources": []}
        else:
            q = d.get("q", "")
            ctx = passages(q, lire_dossier())
            try: txt = "[outil] lire_maths() [RAG]\n" + demander_llm(q, ctx)
            except Exception as e: txt = f"LLM indisponible ({e}). Passages :\n{ctx[:1000]}"
            srcs = sorted(set(re.findall(r"===\s*SOURCE:?\s*([^=\]]+)", ctx)))[:6]
            out = {"txt": txt, "sources": [s.strip() for s in srcs] or ["cours_maths/"]}
        b = json.dumps(out).encode("utf-8")
        self.send_response(200); self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass

print("BUILD app-maths v3 (offline, multithread) - Ouvrez http://127.0.0.1:3001")
ThreadingHTTPServer(("127.0.0.1", 3001), H).serve_forever()
