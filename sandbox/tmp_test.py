import pathlib, re, random, json, ast, requests, subprocess, tempfile, os
from http.server import BaseHTTPRequestHandler, HTTPServer

MODEL = "llama3.2:latest"
URL = "http://127.0.0.1:11434/api/chat"
def lire_cours(): return pathlib.Path("cours/react.txt").read_text(encoding="utf-8")
COURS_TXT = lire_cours().lower()
SYSTEM = "Tu es agent prof React. Cours via lire_cours. Code via corriger_code. Sinon Hors-matiere."
OUTIL=[
 {"type":"function","function":{"name":"lire_cours","description":"Lit cours/react.txt","parameters":{"type":"object","properties":{},"required":[]}}},
 {"type":"function","function":{"name":"corriger_code","description":"Corrige code React/Python colle par l'etudiant. Appelle-la des que tu vois du code.","parameters":{"type":"object","properties":{"code":{"type":"string"}},"required":["code"]}}}
]

QUIZ=[
 {"q":"Pour modifier count avec useState ?","choix":["A) count=count+1","B) setCount(count+1)","C) update(count)"],"rep":"B"},
 {"q":"useEffect(..., [count]) se relance quand ?","choix":["A) toujours","B) quand count change","C) jamais"],"rep":"B"},
]
status=None
def run_quiz():
    global status
    status=random.sample(QUIZ,2)
    return {"type":"quiz","questions":[{"q":x["q"],"choix":x["choix"]} for x in status]}
def corrige_quiz(L):
    global status
    if not status: return {"type":"score","txt":"Lance d'abord le quiz"}
    s=sum(1 for i,x in enumerate(status) if i<len(L) and L[i]==x["rep"])
    d=" ".join([f"{i+1}:{L[i] if i<len(L) else '?'}={'OK' if i<len(L) and L[i]==x['rep'] else 'NON->'+x['rep']}" for i,x in enumerate(status)])
    status=None
    return {"type":"score","txt":f"Score {s}/2 - {d}"}

# --- OUTIL 2 = VOTRE correcteur, deterministe ---
def corriger_code(code):
    erreurs=[]
    if re.search(r"\bcount\s*=",code) and "setCount" not in code:
        erreurs.append("Ligne count= : interdit par le cours. Utilisez setCount(count+1).")
    if re.search(r"function\s+[a-z]",code):
        erreurs.append("Composant en minuscule : mettez majuscule ex: function Carte().")
    if "useState" in code and "useState(0)" not in code and "useState(" not in code:
        erreurs.append("useState mal initialise.")
    # Analyse statique Python : noms utilises mais jamais definis (ex: status vs actif)
    try:
        tree = ast.parse(code)
        definis = set(dir(__builtins__) if isinstance(__builtins__, dict) else dir(__builtins__)) | {"True","False","None","print","len","range","random","QUIZ"}
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names: definis.add((a.asname or a.name).split(".")[0])
            elif isinstance(n, ast.ImportFrom):
                for a in n.names: definis.add(a.asname or a.name)
            elif isinstance(n, ast.FunctionDef): definis.add(n.name)
            elif isinstance(n, ast.ClassDef): definis.add(n.name)
            elif isinstance(n, ast.arg): definis.add(n.arg)
            elif isinstance(n, (ast.Assign, ast.AnnAssign, ast.For, ast.With)):
                for t in ast.walk(n):
                    if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store): definis.add(t.id)
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id not in definis:
                erreurs.append(f"Nom inconnu : '{n.id}' utilise mais jamais defini (verifiez actif vs status, import manquant ?).")
                definis.add(n.id)  # 1 seule fois
    except SyntaxError as e:
        erreurs.append(f"Erreur syntaxe ligne {e.lineno} : {e.msg}")
    txt="CORRECTION PYTHON (regles du cours) :\n"+("\n".join("- "+e for e in erreurs) if erreurs else "- OK cote React.")
    # Si vrai Python, on l'execute pour montrer l'erreur reelle
    if "def " in code or "print(" in code:
        pathlib.Path("sandbox").mkdir(exist_ok=True)
        fp=pathlib.Path("sandbox/tmp_test.py");fp.write_text(code,encoding="utf-8")
        try:
            p=subprocess.run(["python",str(fp)],capture_output=True,text=True,timeout=10)
            out=(p.stdout+p.stderr)[-1500:]
            txt+=f"\n\nEXECUTION python (code {p.returncode}) :\n{out if out.strip() else '(aucune sortie)'}"
        except Exception as e:
            txt+=f"\n\nEXECUTION impossible : {e}"
    return {"type":"code","txt":"[outil] corriger_code()\n"+txt}

def run_agent(q):
    # PORTE : si ca ressemble a du code, on ne demande meme pas au LLM
    if "```" in q or "function " in q or "def " in q or "setCount" in q or "useState" in q or "<div" in q:
        code=q.replace("```","").strip()
        return corriger_code(code)
    r=requests.post(URL,json={"model":MODEL,"messages":[{"role":"system","content":SYSTEM},{"role":"user","content":q}],"stream":False,"tools":OUTIL,"options":{"temperature":0.0}},timeout=120).json()["message"]
    for c in (r.get("tool_calls") or []):
        if c["function"]["name"]=="corriger_code":
            arg=c["function"].get("arguments",{})
            if isinstance(arg,str):
                try: arg=json.loads(arg)
                except: arg={"code":q}
            return corriger_code(arg.get("code",q))
        if c["function"]["name"]=="lire_cours":
            cc=lire_cours()
            r2=requests.post(URL,json={"model":MODEL,"messages":[{"role":"system","content":SYSTEM},{"role":"user","content":q},{"role":"assistant","content":"","tool_calls":r["tool_calls"]},{"role":"tool","content":cc[:4000]}],"stream":False,"options":{"temperature":0.0}},timeout=120).json()["message"]
            return {"type":"cours","txt":"[outil] lire_cours()\n"+(r2.get("content") or "")}
    return {"type":"cours","txt":r.get("content") or ""}

PAGE=b"""<meta charset=utf-8><style>body{font-family:Arial;max-width:750px;margin:20px}button{padding:8px;margin:4px}pre{background:#eee;padding:10px;white-space:pre-wrap}textarea{width:100%;height:90px}</style>
<h2>Agent React - Etape 6 (cours + quiz + corrige-code)</h2>
<input id=q size=55 placeholder='Question cours'><button onclick="cours()">Cours</button><button onclick="quiz()">Quiz</button>
<pre id=r></pre><div id=quiz></div>
<h3>Colle ton code :</h3><textarea id=code>function carte(){ count=count+1; return <div/> }</textarea><br><button onclick="code()">Corriger mon code</button>
<script>
async function post(d){let x=await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});return x.json();}
async function cours(){r.textContent='...';let j=await post({a:'cours',q:q.value});r.textContent=j.txt;}
async function quiz(){let j=await post({a:'quiz'});let d=document.getElementById('quiz');d.innerHTML='';j.questions.forEach((e,i)=>{d.innerHTML+=`<p><b>${i+1}. ${e.q}</b><br>`+e.choix.map(c=>`<label><input type=radio name=q${i} value='${c[0]}'> ${c}</label><br>`).join('')+'</p>';});d.innerHTML+=`<button onclick="corr()">Corriger</button>`;}
async function corr(){let L=[0,1].map(i=>{let e=document.querySelector(`input[name=q${i}]:checked`);return e?e.value:'?';});let j=await post({a:'corr',lettres:L});r.textContent='[outil] verifier_reponse()\\n'+j.txt;}
async function code(){r.textContent='...';let j=await post({a:'code',q:document.getElementById('code').value});r.textContent=j.txt;}
</script>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200);self.send_header("Content-type","text/html; charset=utf-8");self.end_headers();self.wfile.write(PAGE)
    def do_POST(self):
        n=int(self.headers.get('Content-Length',0));d=json.loads(self.rfile.read(n).decode('utf-8'))
        if d.get('a')=='quiz': out=run_quiz()
        elif d.get('a')=='corr': out=corrige_quiz(d.get('lettres',[]))
        elif d.get('a')=='code': out=corriger_code(d.get('q',''))
        else: out=run_agent(d.get('q',''))
        b=json.dumps(out).encode('utf-8')
        self.send_response(200);self.send_header("Content-type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def log_message(self,*a): pass
print("Ouvrez http://127.0.0.1:3000");HTTPServer(("127.0.0.1",3000),H).serve_forever()