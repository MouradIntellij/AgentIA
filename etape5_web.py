import pathlib, re, random, json, requests
from http.server import BaseHTTPRequestHandler, HTTPServer

MODEL = "llama3.2:latest"
URL = "http://127.0.0.1:11434/api/chat"
def lire_cours(): return pathlib.Path("cours/react.txt").read_text(encoding="utf-8")
COURS_TXT = lire_cours().lower()
SYSTEM = "Tu es agent prof React. Pour le cours utilise l'outil lire_cours. Sinon: Hors-matiere."
OUTIL=[{"type":"function","function":{"name":"lire_cours","description":"Lit cours/react.txt","parameters":{"type":"object","properties":{},"required":[]}}}]

QUIZ = [
    {"q":"Pour modifier count avec useState, on fait ?","choix":["A) count=count+1","B) setCount(count+1)","C) update(count)"],"rep":"B"},
    {"q":"useEffect(..., [count]) se relance quand ?","choix":["A) a chaque fois","B) quand count change","C) jamais"],"rep":"B"},
    {"q":"Props sert a ?","choix":["A) parent->enfant","B) enfant->parent","C) rien"],"rep":"A"},
    {"q":"Un composant s'ecrit ?","choix":["A) function Carte(){return <div/>}","B) function carte()","C) <div>"],"rep":"A"},
]
actif = None

def run_quiz():
    global actif
    actif = random.sample(QUIZ, 2)
    return {"type":"quiz","questions":[{"q":x["q"],"choix":x["choix"]} for x in actif]}

def corrige_quiz(lettres):
    global actif
    if not actif: return {"type":"score","txt":"Clique d'abord Lancer Quiz"}
    score = sum(1 for i,x in enumerate(actif) if i < len(lettres) and lettres[i]==x["rep"])
    detail = " ".join([f"{i+1}:{lettres[i] if i < len(lettres) else '?'}={'OK' if i < len(lettres) and lettres[i]==x['rep'] else 'NON->'+x['rep']}" for i,x in enumerate(actif)])
    actif = None
    return {"type":"score","txt":f"Score {score}/2 - {detail}"}

def run_agent(q):
    r = requests.post(URL,json={"model":MODEL,"messages":[{"role":"system","content":SYSTEM},{"role":"user","content":q}],"stream":False,"tools":OUTIL,"options":{"temperature":0.0}},timeout=120).json()["message"]
    if r.get("tool_calls"):
        c = lire_cours()
        r2 = requests.post(URL,json={"model":MODEL,"messages":[{"role":"system","content":SYSTEM},{"role":"user","content":q},{"role":"assistant","content":"","tool_calls":r["tool_calls"]},{"role":"tool","content":c[:4000]}],"stream":False,"options":{"temperature":0.0}},timeout=120).json()["message"]
        return {"type":"cours","txt":"[outil] lire_cours()\n"+(r2.get("content") or "")}
    return {"type":"cours","txt":r.get("content")}

PAGE = b"""<meta charset=utf-8><style>body{font-family:Arial;max-width:700px;margin:20px}button{padding:8px;margin:4px}pre{background:#eee;padding:10px;white-space:pre-wrap}#quiz{border:1px solid #999;padding:10px;margin-top:10px}</style>
<h2>Agent React - Etape 5 Web (local)</h2>
<input id=q size=55 placeholder='Ex: Que dit le cours sur useState ?'><button onclick="cours()">Cours</button><button onclick="quiz()">Lancer Quiz</button>
<pre id=r></pre><div id=quiz></div>
<script>
async function post(d){let x=await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});return x.json();}
async function cours(){r.textContent='...';let j=await post({a:'cours',q:q.value});r.textContent=j.txt;}
async function quiz(){r.textContent='';let j=await post({a:'quiz'});show(j);}
function show(j){let d=document.getElementById('quiz');d.innerHTML='';j.questions.forEach((e,i)=>{d.innerHTML+=`<p><b>${i+1}. ${e.q}</b><br>`+e.choix.map(c=>`<label><input type=radio name=q${i} value='${c[0]}'> ${c}</label><br>`).join('')+'</p>';});d.innerHTML+=`<button onclick="corr()">Corriger</button>`;}
async function corr(){let L=[0,1].map(i=>{let e=document.querySelector(`input[name=q${i}]:checked`);return e?e.value:'?';});let j=await post({a:'corr',lettres:L});document.getElementById('r').textContent='[outil] verifier_reponse() [Python]\\n'+j.txt;}
</script>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200);self.send_header("Content-type","text/html; charset=utf-8");self.end_headers();self.wfile.write(PAGE)
    def do_POST(self):
        n=int(self.headers.get('Content-Length',0));d=json.loads(self.rfile.read(n).decode('utf-8'))
        if d.get('a')=='quiz': out=run_quiz()
        elif d.get('a')=='corr': out=corrige_quiz(d.get('lettres',[]))
        else: out=run_agent(d.get('q',''))
        b=json.dumps(out).encode('utf-8')
        self.send_response(200);self.send_header("Content-type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def log_message(self,*a): pass

print("Ouvrez http://127.0.0.1:3000");HTTPServer(("127.0.0.1",3000),H).serve_forever()
