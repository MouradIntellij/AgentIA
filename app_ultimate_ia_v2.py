"""
APP ULTIMATE IA vFinal - TechWeek
L'agent qui voit, entend, parle et enseigne.
Lancer : python app_ultimate_ia_v2.py -> http://127.0.0.1:3000
"""
import pathlib, re, json, os, requests, sys, base64
import torch
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from sentence_transformers import SentenceTransformer, util

# ---------- CONFIGURATION ----------
MODEL_RAG = "llama3.2:latest"
MODEL_VISION = "llava"
URL_OLLAMA = "http://127.0.0.1:11434/api/chat"
MODEL_EMBED = 'all-MiniLM-L6-v2'

print("\n--- INITIALISATION DE L'IA ULTIME (STABLE) ---")
try:
    embedder = SentenceTransformer(MODEL_EMBED)
    print("✅ Moteur Sémantique PyTorch prêt.")
except Exception as e:
    print(f"❌ Erreur PyTorch: {e}"); sys.exit()

def RACINE(): return pathlib.Path(".")

# ---------- MOTEUR RAG (PyTorch) ----------
def lire_docx(path):
    try:
        import zipfile
        x = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
        return re.sub(r"<[^>]+>", "", re.sub(r"</w:p[^>]*>", "\n", x))
    except: return ""

def lire_pdf(path):
    try:
        from pypdf import PdfReader
        return "\n".join([(p.extract_text() or "") for p in PdfReader(str(path)).pages])
    except: return ""

def charger_base():
    corpus, sources = [], []
    for d in sorted((RACINE() / "cours").rglob("*.docx")):
        txt = lire_docx(d)
        for p in txt.split('\n'):
            if len(p.strip()) > 40: corpus.append(p.strip()); sources.append(d.name)
    for p in sorted((RACINE() / "cours").rglob("*.pdf")):
        txt = lire_pdf(p)
        for para in txt.split('\n'):
            if len(para.strip()) > 40: corpus.append(para.strip()); sources.append(p.name)
    return corpus, sources

print("Indexation sémantique...")
CORPUS, SOURCES = charger_base()
CORPUS_EMBEDDINGS = embedder.encode(CORPUS, convert_to_tensor=True)
print(f"✅ Indexé {len(CORPUS)} fragments.")

def recherche_semantique(q, top_k=5):
    q_emb = embedder.encode(q, convert_to_tensor=True)
    scores = util.cos_sim(q_emb, CORPUS_EMBEDDINGS)[0]
    top = torch.topk(scores, k=min(top_k, len(CORPUS)))
    res = [f"[{SOURCES[i]}] {CORPUS[i]}" for s, i in zip(top[0], top[1]) if s > 0.20]
    return "\n\n".join(res) if res else "Aucun fragment pertinent."

# ---------- LOGIQUE IA ----------
def run_agent(q, socrates=False, image_b64=None):
    if image_b64:
        system_prompt = "Tu es un expert en analyse de code. Analyse l'image précisément. Identifie les erreurs de syntaxe."
        payload = {
            "model": MODEL_VISION,
            "messages": [{"role": "user", "content": q or "Analyse ce code.", "images": [image_b64]}],
            "stream": False
        }
        try:
            r = requests.post(URL_OLLAMA, json=payload, timeout=120).json()
            return {"type": "vision", "txt": f"[Vision LLava]\n\n{r['message']['content']}"}
        except Exception as e: return {"type": "error", "txt": f"Erreur Vision: {e}"}

    ctx = recherche_semantique(q)
    if socrates:
        system_prompt = f"Tu es Socrate. NE DONNE JAMAIS LA RÉPONSE. Guide l'élève avec des indices basés sur : {ctx}"
    else:
        system_prompt = f"Tu es un tuteur expert. Réponds précisément selon : {ctx}. Si absent, dis 'Hors-matière'."

    try:
        r = requests.post(URL_OLLAMA, json={
            "model": MODEL_RAG,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": q}],
            "stream": False, "options": {"temperature": 0.2}
        }, timeout=120).json()
        return {"type": "cours", "txt": f"[IA Sémantique]\n\n{r['message']['content']}"}
    except Exception as e: return {"type": "error", "txt": f"Erreur IA: {e}"}

# ---------- INTERFACE WEB (STABLE) ----------
# LE 'r' ICI EST OBLIGATOIRE POUR QUE LE JAVASCRIPT FONCTIONNE
PAGE = r"""<!DOCTYPE html><html lang=fr><head><meta charset=utf-8>
<title>Ultimate AI Tutor vFinal</title>
<style>
    body{font-family:'Segoe UI', sans-serif; background:#0f172a; color:#f8fafc; margin:0; display:flex; justify-content:center}
    .app{width:100%; max-width:900px; padding:20px}
    .card{background:#1e293b; padding:25px; border-radius:20px; box-shadow:0 20px 50px rgba(0,0,0,0.5); border:1px solid #334155}
    .header{text-align:center; margin-bottom:30px}
    .controls{display:flex; gap:15px; justify-content:center; margin-bottom:20px; flex-wrap:wrap}
    .btn{padding:10px 20px; border-radius:10px; border:none; cursor:pointer; font-weight:bold; transition:0.3s}
    .btn-blue{background:#3b82f6; color:white}
    .btn-green{background:#10b981; color:white}
    .btn-purple{background:#a855f7; color:white}
    .btn-active{outline: 4px solid #fbbf24; box-shadow: 0 0 15px #fbbf24}
    .input-box{display:flex; gap:10px; background:#334155; padding:15px; border-radius:15px; align-items:center}
    input{flex:1; background:transparent; border:none; color:white; font-size:16px; outline:none}
    pre{background:#020617; color:#38bdf8; padding:20px; border-radius:15px; white-space:pre-wrap; font-size:16px; border:1px solid #334155; min-height:150px}
    .paste-info{text-align:center; font-size:12px; color:#94a3b8; margin-bottom:10px}
</style>
</head><body>
<div class='app'>
    <div class='card'>
        <div class='header'>
            <h1>🌟 Ultimate AI Tutor</h1>
            <p>Vision • Voix • Sémantique • Socrate</p>
        </div>
        <div class='controls'>
            <button id='btnSoc' class='btn btn-blue' onclick='toggleSoc()'>Mode Socrate: OFF</button>
            <button id='btnVoice' class='btn btn-green' onclick='toggleVoiceMode()'>Conversation Vocale: OFF</button>
        </div>
        <p class='paste-info'>💡 Astuce : Faites Ctrl+V pour coller un screenshot de votre code !</p>
        <div class='input-box'>
            <input id='q' placeholder='Posez votre question ou collez une image...'>
            <button class='btn btn-purple' onclick='ask()'>Envoyer</button>
        </div>
        <br>
        <pre id='r'>L'IA est prête. Essayez le Ctrl+V ou la voix !</pre>
    </div>
</div>
<script>
let socrates = false;
let voiceMode = false;
let pastedImageB64 = null;

function toggleSoc(){
    socrates = !socrates;
    document.getElementById('btnSoc').textContent = 'Mode Socrate: ' + (socrates?'ON':'OFF');
    document.getElementById('btnSoc').classList.toggle('btn-active');
}

function toggleVoiceMode(){
    voiceMode = !voiceMode;
    document.getElementById('btnVoice').textContent = 'Conversation Vocale: ' + (voiceMode?'ON':'OFF');
    document.getElementById('btnVoice').classList.toggle('btn-active');
    if(voiceMode) startListen();
}

function speak(text) {
    const msg = new SpeechSynthesisUtterance(text);
    msg.lang = 'fr-FR';
    window.speechSynthesis.speak(msg);
    if(voiceMode) { msg.onend = () => { startListen(); }; }
}

function startListen(){
    if(!voiceMode) return;
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'fr-FR';
    recognition.start();
    document.getElementById('r').textContent = 'Je vous écoute...';
    recognition.onresult = (event) => {
        document.getElementById('q').value = event.results[0][0].transcript;
        ask();
    };
    recognition.onerror = () => { if(voiceMode) setTimeout(startListen, 1000); };
}

window.addEventListener('paste', e => {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
            const blob = items[i].getAsFile();
            const reader = new FileReader();
            reader.onload = (event) => {
                pastedImageB64 = event.target.result.split(',')[1];
                document.getElementById('r').textContent = '🖼️ Image capturée ! Posez votre question ou cliquez sur Envoyer.';
            };
            reader.readAsDataURL(blob);
        }
    }
});

async function ask(){
    let r=document.getElementById('r');
    let q=document.getElementById('q').value;
    if(!q && !pastedImageB64) return;
    r.textContent = 'Analyse en cours...';
    try {
        let res = await fetch('/api', { 
            method: 'POST', 
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({q: q, socrates: socrates, image: pastedImageB64})
        });
        let j = await res.json();
        r.textContent = j.txt;
        let cleanText = j.txt.replace('[Moteur PyTorch Sémantique]', '').replace('[Vision LLava]', '').replace(/\[.*?\]/g, '');
        speak(cleanText);
        pastedImageB64 = null; 
    } catch(e) { r.textContent = 'Erreur serveur.'; }
}
</script>
</body></html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-type", "text/html; charset=utf-8"); self.end_headers()
        self.wfile.write(PAGE.encode('utf-8'))

    def do_POST(self):
        n = int(self.headers['Content-Length'])
        d = json.loads(self.rfile.read(n).decode('utf-8'))
        out = run_agent(d.get('q', ''), d.get('socrates', False), d.get('image', None))
        self.send_response(200); self.send_header("Content-type", "application/json"); self.end_headers()
        self.wfile.write(json.dumps(out).encode('utf-8'))

    def log_message(self, *a): pass

if __name__ == "__main__":
    print("\n🚀 Lancement de l'IA ULTIME sur http://127.0.0.1:3000")
    ThreadingHTTPServer(("127.0.0.1", 3000), H).serve_forever()
