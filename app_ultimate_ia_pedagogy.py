"""
APP ULTIMATE IA vPedagogy_Pro - TechWeek
L'IA Pédagogique Ultime : Mémoire, Vision, Voix et Évaluation Active.
Lancer : python app_ultimate_ia_pedagogy_pro.py -> http://127.0.0.1:3000
"""
import pathlib, re, json, os, requests, sys, base64
import torch
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from sentence_transformers import SentenceTransformer, util
import easyocr

# ---------- CONFIGURATION ----------
MODEL_RAG = "llama3.2:latest"
URL_OLLAMA = "http://127.0.0.1:11434/api/chat"
MODEL_EMBED = 'all-MiniLM-L6-v2'

print("\n--- INITIALISATION DE L'IA PÉDAGOGIQUE PRO ---")
try:
    reader = easyocr.Reader(['en', 'fr'], gpu=torch.cuda.is_available())
    embedder = SentenceTransformer(MODEL_EMBED)
    print("✅ Moteurs PyTorch et OCR prêts.")
except Exception as e:
    print(f"❌ Erreur initialisation: {e}");
    sys.exit()


def RACINE(): return pathlib.Path(".")


# ---------- MOTEUR RAG ----------
def lire_docx(path):
    try:
        import zipfile
        x = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
        return re.sub(r"<[^>]+>", "", re.sub(r"</w:p[^>]*>", "\n", x))
    except:
        return ""


def lire_pdf(path):
    try:
        from pypdf import PdfReader
        return "\n".join([(p.extract_text() or "") for p in PdfReader(str(path)).pages])
    except:
        return ""


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


# ---------- GESTION DE LA MÉMOIRE ----------
# On stocke l'historique par session (ici global pour la démo)
CHAT_HISTORY = []


def run_agent(q, socrates=False, image_b64=None, lang="fr", mode="chat"):
    global CHAT_HISTORY

    # 1. TRAITEMENT OCR
    if image_b64:
        try:
            img_data = base64.b64decode(image_b64)
            with open("temp_ocr.jpg", "wb") as f:
                f.write(img_data)
            result = reader.readtext("temp_ocr.jpg", detail=0)
            q = f"IMAGE ANALYSÉE (OCR) :\n{' '.join(result)}\n\nQUESTION : {q}"
        except Exception as e:
            return {"type": "error", "txt": f"Erreur OCR: {e}"}

    # 2. CONTEXTE RAG
    ctx = recherche_semantique(q, top_k=5)
    lang_instr = "MUST respond EXCLUSIVELY in French." if lang == "fr" else "MUST respond EXCLUSIVELY in English."

    # 3. PROMPTS SPÉCIALISÉS
    if mode == "quiz":
        system_prompt = (
            f"Tu es un examinateur pédagogique. {lang_instr}\n"
            "Tâche : Basé sur l'historique de conversation et les sources, crée un mini-quiz de 3 questions "
            "pour tester la compréhension de l'élève. Ne donne PAS les réponses tout de suite."
            f"\n\nHISTORIQUE : {CHAT_HISTORY[-5:]}\n\nSOURCES : {ctx}"
        )
    elif socrates:
        system_prompt = (
            f"Tu es Socrate, mentor bienveillant. {lang_instr}\n"
            "NE JAMAIS donner la solution. Guide l'élève par des questions."
            f"\n\nSOURCES : {ctx}"
        )
    else:
        system_prompt = (
            f"Tu es un expert tuteur. {lang_instr}\n"
            "Réponds précisément et utilise le Markdown pour le code."
            f"\n\nSOURCES : {ctx}"
        )

    # Construction des messages pour Ollama (incluant l'historique pour la mémoire)
    messages = [{"role": "system", "content": system_prompt}]
    # On ajoute les 6 derniers échanges pour la mémoire
    messages.extend(CHAT_HISTORY[-6:])
    messages.append({"role": "user", "content": q})

    try:
        r = requests.post(URL_OLLAMA, json={
            "model": MODEL_RAG,
            "messages": messages,
            "stream": False, "options": {"temperature": 0.3}
        }, timeout=120).json()

        answer = r['message']['content']
        # On mémorise l'échange
        CHAT_HISTORY.append({"role": "user", "content": q})
        CHAT_HISTORY.append({"role": "assistant", "content": answer})

        return {"type": "cours", "txt": answer}
    except Exception as e:
        return {"type": "error", "txt": f"Erreur IA: {e}"}


# ---------- INTERFACE WEB ----------
PAGE = r"""<!DOCTYPE html><html lang=fr><head><meta charset=utf-8>
<title>Ultimate AI Pedagogy Pro</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<style>
    body{font-family:'Segoe UI', sans-serif; background:#0f172a; color:#f8fafc; margin:0; display:flex; justify-content:center}
    .app{width:100%; max-width:1000px; padding:20px}
    .card{background:#1e293b; padding:25px; border-radius:20px; box-shadow:0 20px 50px rgba(0,0,0,0.5); border:1px solid #334155}
    .header{text-align:center; margin-bottom:30px}
    .controls{display:flex; gap:10px; justify-content:center; margin-bottom:20px; flex-wrap:wrap}
    .btn{padding:10px 18px; border-radius:10px; border:none; cursor:pointer; font-weight:bold; transition:0.3s; color:white}
    .btn-blue{background:#3b82f6} .btn-green{background:#10b981} .btn-purple{background:#a855f7} .btn-orange{background:#f59e0b}
    .btn-active{outline: 4px solid #fbbf24; box-shadow: 0 0 15px #fbbf24}
    .input-box{display:flex; gap:10px; background:#334155; padding:15px; border-radius:15px; align-items:center}
    textarea{flex:1; background:transparent; border:none; color:white; font-size:16px; outline:none; resize:vertical; min-height:50px; font-family: 'Consolas', monospace;}
    #chat-window { background:#020617; color:#f8fafc; padding:20px; border-radius:15px; border:1px solid #334155; height:500px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; margin-bottom:10px; }
    .msg { padding: 12px 18px; border-radius: 15px; max-width: 85%; line-height: 1.5; }
    .user-msg { background: #3b82f6; color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
    .ai-msg { background: #1e293b; color: #f8fafc; align-self: flex-start; border-bottom-left-radius: 2px; border: 1px solid #334155; }
    .ai-msg pre { background: #020617; padding: 15px; border-radius: 10px; overflow-x: auto; border: 1px solid #334155; margin: 10px 0; }
    .status-msg { text-align:center; font-size:13px; color:#94a3b8; margin-bottom:10px; font-style:italic; }
    select{padding:10px; border-radius:10px; background:#334155; color:white; border:none; cursor:pointer}
</style>
</head><body>
<div class='app'>
    <div class='card'>
        <div class='header'>
            <h1>🎓 AI Pedagogy Pro</h1>
            <p>L'agent qui ne se contente pas de répondre, mais qui enseigne.</p>
        </div>
        <div class='controls'>
            <button id='btnSoc' class='btn btn-blue' onclick='toggleSoc()'>Mode Socrate: OFF</button>
            <button id='btnVoice' class='btn btn-green' onclick='toggleVoiceMode()'>Voix: OFF</button>
            <button id='btnQuiz' class='btn btn-orange' onclick='ask("Génère-moi un quiz sur ce qu'on a vu", true)'>📝 Lancer un Quiz</button>
            <button id='btnStop' class='btn btn-purple' onclick='stopVoice()' style='display:none'>🛑 Stop</button>
            <select id='langSelect'>
                <option value='fr'>Français 🇫🇷</option>
                <option value='en'>English 🇺🇸</option>
            </select>
        </div>
        <div id='chat-window'>
            <div class='msg ai-msg'>Bonjour ! Je suis votre tuteur intelligent. Voulez-vous explorer un cours, analyser une image ou tester vos connaissances avec un quiz ?</div>
        </div>
        <div id='status' class='status-msg'></div>
        <div class='input-box'>
            <textarea id='q' placeholder='Posez votre question, collez du code ou une image...' rows='2'></textarea>
            <button class='btn btn-purple' onclick='ask()'>Envoyer</button>
        </div>
    </div>
</div>
<script>
let socrates = false, voiceMode = false, pastedImageB64 = null;

function toggleSoc(){
    socrates = !socrates;
    document.getElementById('btnSoc').textContent = 'Mode Socrate: ' + (socrates?'ON':'OFF');
    document.getElementById('btnSoc').classList.toggle('btn-active');
}

function toggleVoiceMode(){
    voiceMode = !voiceMode;
    document.getElementById('btnVoice').textContent = 'Voix: ' + (voiceMode?'ON':'OFF');
    document.getElementById('btnVoice').classList.toggle('btn-active');
    document.getElementById('btnStop').style.display = voiceMode ? 'block' : 'none';
    if(voiceMode) startListen();
}

function stopVoice() { window.speechSynthesis.cancel(); if(voiceMode) startListen(); }

function speak(text) {
    const lang = document.getElementById('langSelect').value;
    let cleanText = text.replace(/\*/g,'').replace(/#/g,'').replace(/`{1,3}/g,'').replace(/\[.*?\]/g,'').trim();
    const msg = new SpeechSynthesisUtterance(cleanText);
    msg.lang = lang === 'fr' ? 'fr-FR' : 'en-US';
    window.speechSynthesis.speak(msg);
    msg.onend = () => { if(voiceMode) setTimeout(startListen, 500); };
}

function startListen(){
    if(!voiceMode) return;
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = document.getElementById('langSelect').value === 'fr' ? 'fr-FR' : 'en-US';
    recognition.onstart = () => { document.getElementById('status').textContent = '🎤 Je vous écoute...'; };
    recognition.onresult = (event) => {
        document.getElementById('q').value = event.results[0][0].transcript;
    };
    recognition.onspeechend = () => {
        recognition.stop();
        if(document.getElementById('q').value.trim() !== "") { ask(); } 
        else { setTimeout(startListen, 1000); }
    };
    recognition.onerror = () => { if(voiceMode) setTimeout(startListen, 1000); };
    try { recognition.start(); } catch(e) {}
}

async function ask(text_override=null, is_quiz=false){
    let chat = document.getElementById('chat-window');
    let status = document.getElementById('status');
    let q = text_override || document.getElementById('q').value;
    let lang = document.getElementById('langSelect').value;
    if(!q && !pastedImageB64) return;

    let userDiv = document.createElement('div');
    userDiv.className = 'msg user-msg';
    userDiv.textContent = q;
    chat.appendChild(userDiv);
    document.getElementById('q').value = '';
    status.textContent = 'Analyse cognitive en cours...';
    chat.scrollTop = chat.scrollHeight;

    try {
        let res = await fetch('/api', { 
            method: 'POST', 
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({q: q, socrates: socrates, image: pastedImageB64, lang: lang, mode: is_quiz ? 'quiz' : 'chat'})
        });
        let j = await res.json();
        let aiDiv = document.createElement('div');
        aiDiv.className = 'msg ai-msg';
        aiDiv.innerHTML = marked.parse(j.txt); 
        chat.appendChild(aiDiv);
        status.textContent = '';
        chat.scrollTop = chat.scrollHeight;
        hljs.highlightAll();
        if(voiceMode) speak(j.txt);
        pastedImageB64 = null;
    } catch(e) { status.textContent = 'Erreur serveur.'; }
}

window.addEventListener('paste', e => {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
            const blob = items[i].getAsFile();
            const reader = new FileReader();
            reader.onload = (event) => {
                pastedImageB64 = event.target.result.split(',')[1];
                document.getElementById('status').textContent = '🖼️ Image analysée ! Posez votre question.';
            };
            reader.readAsDataURL(blob);
        }
    }
});
</script>
</body></html>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200);
        self.send_header("Content-type", "text/html; charset=utf-8");
        self.end_headers()
        self.wfile.write(PAGE.encode('utf-8'))

    def do_POST(self):
        try:
            n = int(self.headers['Content-Length'])
            d = json.loads(self.rfile.read(n).decode('utf-8'))
            out = run_agent(d.get('q', ''), d.get('socrates', False), d.get('image', None), d.get('lang', 'fr'),
                            d.get('mode', 'chat'))
            self.send_response(200);
            self.send_header("Content-type", "application/json");
            self.end_headers()
            self.wfile.write(json.dumps(out).encode('utf-8'))
        except Exception as e:
            self.send_response(500);
            self.end_headers()
            self.wfile.write(json.dumps({"type": "error", "txt": str(e)}).encode('utf-8'))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print("\n🚀 Lancement de l'IA PÉDAGOGIQUE PRO sur http://127.0.0.1:3000")
    server = ThreadingHTTPServer(("127.0.0.1", 3000), H)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur. Au revoir ! 👋")
        server.shutdown()
        sys.exit(0)
