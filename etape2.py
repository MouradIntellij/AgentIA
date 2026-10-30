import requests, pathlib

MODEL = "llama3.2:latest"
URL = "http://127.0.0.1:11434/api/chat"

# 1. BRAS : lire la matiere locale
cours_path = pathlib.Path("cours/react.txt")
COURS = cours_path.read_text(encoding="utf-8")

SYSTEM = f"""Tu es prof React. Tu utilises UNIQUEMENT le COURS ci-dessous mot-pour-mot.
INTERDIT d'utiliser ta memoire. INTERDIT d'expliquer un concept absent du COURS.
Si le concept demande n'est pas ecrit tel quel dans le COURS, reponds EXACTEMENT :
Hors-matiere - voir manuel.
COURS :
{COURS}"""

import re
def garde_hors_matiere(question):
    mots_q = [w.lower() for w in re.findall(r"[a-zA-Z]+", question) if len(w) > 4]
    cours_low = COURS.lower()
    # si aucun mot important de la question n'est dans le cours -> hors-matiere sans appeler le LLM
    return mots_q and not any(w in cours_low for w in mots_q)


def poser(question):
    if garde_hors_matiere(question):
        return "Hors-matiere - voir manuel. (bloque par garde Python, 0 appel LLM)"

    r = requests.post(URL, json={
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question}
        ],
        "stream": False,
        "options": {"temperature": 0.0}
    }, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"]

if __name__ == "__main__":
    print(f"Cours charge : {len(COURS)} caracteres depuis {cours_path}")
    while True:
        q = input("\nQuestion React (vide=quitter) : ")
        if not q.strip():
            break
        print("\n--- reponse ---\n")
        print(poser(q))