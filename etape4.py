import pathlib, re, json, requests
from http.server import BaseHTTPRequestHandler, HTTPServer

MODEL = "llama3.2:latest"
URL = "http://127.0.0.1:11434/api/chat"
SYSTEM = "Tu es agent prof React. Si question cours, appelle lire_cours. Reponds UNIQUEMENT d'apres l'outil. Sinon: Hors-matiere - voir manuel."
def lire_cours(): return pathlib.Path("cours/react.txt").read_text(encoding="utf-8")
COURS_TXT = lire_cours().lower()
def garde(q):
    mots=[w.lower() for w in re.findall(r"[a-zA-Z]+",q) if len(w)>4]
    return mots and not any(w in COURS_TXT for w in mots)
OUTIL={"type":"function","function":{"name":"lire_cours","description":"Lit cours/react.txt","parameters":{"type":"object","properties":{},"required":[]}}}

def run_agent(q):
    if garde(q):
        _=lire_cours()
        return "[outil] lire_cours() [garde]\nHors-matiere - voir manuel."
    hist=[{"role":"system","content":SYSTEM},{"role":"user","content":q}]
    for _ in range(5):
        r=requests.post(URL,json={"model":MODEL,"messages":hist,"stream":False,"tools":[OUTIL],"options":{"temperature":0.0}},timeout=120).json()["message"]
        hist.append({"role":"assistant","content":r.get("content") or "","tool_calls":r.get("tool_calls")})
        calls=r.get("tool_calls") or []
        if not calls: return r.get("content")
        for c in calls:
            hist.append({"role":"tool","content":lire_cours()[:4000]})
    return "Abandon."

PAGE=b"""<meta charset=utf-8><h2>Agent React - TechWeek (local)</h2>
<input id=q size=60 placeholder='Ex: Que dit le cours sur useState ?'><button onclick="go()">OK</button><pre id=r></pre>
<script>async function go(){r.textContent='...';let x=await fetch('/api',{method:'POST',body:document.getElementById('q').value});r.textContent=await x.text();}</script>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200);self.send_header("Content-type","text/html; charset=utf-8");self.end_headers();self.wfile.write(PAGE)
    def do_POST(self):
        n=int(self.headers.get('Content-Length',0));q=self.rfile.read(n).decode('utf-8', 'ignore')
        rep=run_agent(q)
        b=rep.encode('utf-8');self.send_response(200);self.send_header("Content-type","text/plain; charset=utf-8");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def log_message(self,*a): pass

print("Ouvrez http://127.0.0.1:3000");HTTPServer(("127.0.0.1",3000),H).serve_forever()