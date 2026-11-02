"""ETAPE 10 - Ressources React : livre + sites populaires.
Livre : mettez VOTRE PDF legal dans cours/livres/ (pas de PDF pirate dans l'atelier).
Liste ci-dessous = 100% legal et gratuit."""
LIVRE = {
    "titre": "Le(s) livre(s) de cours/livres/ (votre copie legale)",
    "fichier": "cours/livres/",
    "mode": "Deposez ici VOTRE PDF (copie legale ou extrait libre de droits). S'il depasse 20 000 caracteres, il est indexe page par page.",
    "chapitres": [
        ("Ch.1 JSX/Composants", "banque: jsx, composant, props"),
        ("Ch.2 States/evenements", "banque: usestate, formulaire, evenements, conditionnel, listes"),
        ("Ch.3 Hooks avances", "banque: useeffect, cleanup, useref, usememo, usecallback, usecontext, usereducer"),
        ("Ch.4 Donnees/navigation", "banque: fetch, chargement, router, lifting, lire_fichier"),
    ],
}
SITES = [
    ("React officiel - react.dev", "https://react.dev", "Doc de reference : hooks, useState, useEffect, exemples officiels."),
    ("MDN React", "https://developer.mozilla.org/fr/docs/Web/JavaScript", "Bases JS utiles a React (tableaux, fetch, modules)."),
    ("JavaScript.info", "https://javascript.info", "JS moderne (promesses, fetch, classes) utilise dans nos snippets."),
    ("Vite - vite.dev", "https://vite.dev", "Creer un projet React en 1 commande pour tester nos codes."),
    ("Tailwind CSS - tailwindcss.com", "https://tailwindcss.com", "Styliser les composants de la banque."),
    ("JSONPlaceholder", "https://jsonplaceholder.typicode.com", "Fausse API gratuite pour tester notre snippet fetch."),
    ("Ollama - ollama.com", "https://ollama.com/download", "Installer le moteur LLM local de l'atelier."),
    ("Hugging Face - transformers", "https://huggingface.co/docs/transformers", "Doc officielle etape 9 (tokens, pipeline)."),
]

def texte_ressources():
    t = ["[Ressources React - livre + web]\n", f"LIVRE : {LIVRE['titre']}\n{LIVRE['mode']}\nDossier : {LIVRE['fichier']}\n"]
    import pathlib
    pdfs = sorted(pathlib.Path("cours/livres").glob("*.pdf")) if pathlib.Path("cours/livres").exists() else []
    t.append("PDF presents : " + (", ".join(p.name for p in pdfs) if pdfs else "(aucun - ajoutez-en un)") + "\n")
    t.append("Correspondance chapitres <-> banque codes :")
    t += [f"  - {c[0]}  ->  {c[1]}" for c in LIVRE["chapitres"]]
    t.append("\nSITES POPULAIRES :")
    t += [f"  - {n} : {u}\n    {d}" for n, u, d in SITES]
    return "\n".join(t)


if __name__ == "__main__":
    print(texte_ressources())
