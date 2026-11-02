# -*- coding: utf-8 -*-
"""Index de recherche BM25 pour un livre PDF entier (aucune dependance en plus de pypdf).

Le probleme : un livre de 300 pages ne tient pas dans la fenetre du modele (8 192 tokens).
La reponse naive est de tronquer le livre -> l'agent ne connait que les 5 premieres pages.
La reponse RAG est d'indexer tout le livre, puis de n'envoyer que les meilleurs morceaux :

  1. pypdf extrait le texte, page par page ;
  2. le texte est decoupe en morceaux de ~900 caracteres, chacun etiquete avec sa page ;
  3. un index BM25 (Python pur, ~40 lignes) note les morceaux pour une question ;
  4. seuls les 4-5 meilleurs morceaux partent au modele, avec "=== SOURCE: livre.pdf p.42 ===".

Resultat : le modele voit ~2 000 caracteres, mais la bibliotheque peut faire 500 pages,
et chaque citation porte un numero de page verifiable.

Le cache JSON (cours/cache_index/) evite de re-extraire le PDF a chaque demarrage.
"""
import hashlib
import json
import math
import pathlib
import re
import unicodedata
from collections import Counter

TAILLE_MORCEAU = 900     # caracteres par morceau envoye au modele
RECOUVREMENT = 150       # on garde la fin du morceau precedent pour ne pas couper une idee
K1 = 1.5                 # parametres BM25 classiques
B = 0.75

# Mots vides : ils ne discriminent rien et fausseraient le classement.
STOP = {
    "alors", "aussi", "autre", "autres", "avec", "avoir", "bien", "cela", "cent", "cette",
    "ceux", "chaque", "comme", "comment", "dans", "depuis", "des", "donc", "dont", "elle",
    "elles", "encore", "entre", "etre", "fait", "faire", "fois", "font", "hors", "ici",
    "jamais", "leur", "leurs", "lors", "mais", "meme", "moins", "montre", "nous", "parce",
    "parmi", "pendant", "peut", "plus", "plusieurs", "pour", "pourquoi", "quand", "que",
    "quel", "quelle", "quelles", "quels", "qui", "quoi", "sans", "selon", "sera", "ses",
    "son", "sont", "sous", "sur", "tous", "tout", "toute", "toutes", "tres", "trop", "une",
    "vers", "voir", "votre", "vous", "cours", "explique", "donne", "matiere", "chapitre",
    "page", "livre", "selon", "ainsi", "apres", "avant", "chez", "cela", "celui", "celle",
    # petits mots outils qui ne discriminent rien (ils faisaient apparaitre un livre
    # pour une question hors sujet, ex. "la tarte aux pommes" -> "aux")
    "aux", "par", "pas", "ces", "cet", "nos", "vos", "mes", "tes", "mon", "ton", "ma", "ta",
    "notre", "est", "dans", "pour", "avec", "plus", "moins", "tout", "tous", "toute",
    "toutes", "bien", "peu", "tres", "trop", "aussi", "alors", "donc", "car", "mais",
    "leur", "leurs", "meme", "memes", "chaque", "quel", "quelle", "quels", "quelles",
}


def _racine(mot):
    """Pluriel simplifie : 'etats' et 'etat' doivent se rencontrer (pas de stemming lourd)."""
    if len(mot) > 4 and mot.endswith(("s", "x")) and not mot.endswith(("ss", "ux")):
        return mot[:-1]
    return mot


def _plat(texte):
    """Minuscules sans accents : 'RÉDUCTEUR' et 'reducteur' doivent se rencontrer."""
    texte = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in texte if not unicodedata.combining(c)).lower()


def mots(texte):
    """Tokens utiles : 3 caracteres minimum, sans mots vides, pluriel ramene au singulier."""
    return [_racine(m) for m in re.findall(r"[a-z0-9]{3,}", _plat(texte)) if m not in STOP]


def extraire_pdf(chemin):
    """Retourne [(numero_de_page, texte)] — une page illisible ne fait pas echouer le livre."""
    from pypdf import PdfReader

    pages = []
    for numero, page in enumerate(PdfReader(str(chemin)).pages, 1):
        try:
            texte = page.extract_text() or ""
        except Exception:
            texte = ""
        pages.append((numero, texte))
    return pages


def decouper(pages):
    """Decoupe page par page en morceaux de ~TAILLE_MORCEAU, avec recouvrement."""
    morceaux = []
    for numero, texte in pages:
        texte = re.sub(r"[ \t]+", " ", texte or "")
        texte = re.sub(r"\n{3,}", "\n\n", texte).strip()
        if len(texte) < 40:          # page blanche ou scannee : inutile d'indexer du vide
            continue
        paragraphes = [p.strip() for p in texte.split("\n") if p.strip()]
        tampon = ""
        for paragraphe in paragraphes:
            if tampon and len(tampon) + len(paragraphe) + 1 > TAILLE_MORCEAU:
                morceaux.append({"page": numero, "texte": tampon.strip()})
                depart = max(0, len(tampon) - RECOUVREMENT)
                tampon = tampon[depart:] + "\n" + paragraphe
            else:
                tampon = (tampon + "\n" + paragraphe).strip()
            # paragraphe geant (ex. un tableau mal extrait) : on le coupe a la main
            while len(tampon) > TAILLE_MORCEAU * 2:
                morceaux.append({"page": numero, "texte": tampon[:TAILLE_MORCEAU]})
                tampon = tampon[TAILLE_MORCEAU - RECOUVREMENT:]
        if len(tampon.strip()) > 40:
            morceaux.append({"page": numero, "texte": tampon.strip()})
    return morceaux


class IndexLivre:
    """Index BM25 d'un PDF. Usage : idx = IndexLivre.charger(chemin) puis idx.contexte(question)."""

    def __init__(self, nom, morceaux, pages_total=0):
        self.nom = nom
        self.morceaux = morceaux
        self.pages_total = pages_total or max((m["page"] for m in morceaux), default=0)
        self._preparer()

    def _preparer(self):
        self.doc_mots = [mots(m["texte"]) for m in self.morceaux]
        self.tf = [Counter(d) for d in self.doc_mots]
        self.longueurs = [len(d) for d in self.doc_mots]
        self.n = len(self.morceaux)
        self.moyenne = (sum(self.longueurs) / self.n) if self.n else 0.0
        self.df = Counter()
        for d in self.doc_mots:
            self.df.update(set(d))
        self.vocabulaire = set(self.df)   # tous les mots du livre (pour la garde hors-matiere)

    def _idf(self, mot):
        df = self.df.get(mot, 0)
        return math.log(1 + (self.n - df + 0.5) / (df + 0.5))

    def chercher(self, question, k=8):
        """Les k morceaux les plus pertinents : [(score, morceau)]."""
        requete = list(dict.fromkeys(mots(question)))
        if not requete or not self.n:
            return []
        scores = []
        for i in range(self.n):
            dl = self.longueurs[i] or 1
            score = 0.0
            for mot in requete:
                f = self.tf[i].get(mot)
                if not f:
                    continue
                score += self._idf(mot) * f * (K1 + 1) / (
                    f + K1 * (1 - B + B * dl / (self.moyenne or 1)))
            if score > 0:
                scores.append((score, i))
        scores.sort(key=lambda x: -x[0])
        return [(s, self.morceaux[i]) for s, i in scores[:k]]

    def contexte(self, question, k=8, max_car=1800):
        """Texte pret a envoyer au modele : 4-5 pages, chacune avec son entete SOURCE."""
        resultats = self.chercher(question, k)
        if not resultats:
            return ""
        pages_vues, blocs, total = set(), [], 0
        for _, morceau in resultats:
            page = morceau["page"]
            if page in pages_vues:
                continue
            bloc = "[=== SOURCE: %s p.%d ===] %s" % (self.nom, page, morceau["texte"].strip())
            if blocs and total + len(bloc) > max_car:
                break
            blocs.append(bloc)
            total += len(bloc)
            pages_vues.add(page)
        return "\n\n".join(blocs)

    @classmethod
    def charger(cls, chemin, dossier_cache=None, force=False):
        """Charge l'index, ou le construit une fois puis le relit depuis le cache JSON."""
        chemin = pathlib.Path(chemin)
        etat = chemin.stat()
        empreinte = hashlib.sha1(
            ("%s|%d|%d" % (chemin.name, etat.st_size, int(etat.st_mtime))).encode()).hexdigest()[:10]
        cache = pathlib.Path(dossier_cache) if dossier_cache else (chemin.parent / "cache_index")
        cache.mkdir(parents=True, exist_ok=True)
        fichier = cache / ("%s-%s.json" % (chemin.stem, empreinte))

        if fichier.exists() and not force:
            try:
                d = json.loads(fichier.read_text(encoding="utf-8"))
                return cls(d["nom"], d["morceaux"], d.get("pages_total", 0))
            except Exception:
                pass  # cache corrompu : on reconstruit

        pages = extraire_pdf(chemin)
        morceaux = decouper(pages)
        index = cls(chemin.stem, morceaux, len(pages))
        try:
            fichier.write_text(json.dumps(
                {"nom": index.nom, "morceaux": morceaux, "pages_total": len(pages)},
                ensure_ascii=False), encoding="utf-8")
            for vieux in cache.glob("%s-*.json" % chemin.stem):
                if vieux != fichier:
                    vieux.unlink(missing_ok=True)
        except Exception:
            pass  # disque en lecture seule : l'index reste en memoire
        return index


def indexer_dossier(dossier, seuil_car=20000, dossier_cache=None):
    """Tous les PDF d'un dossier assez gros pour justifier un index (les petits restent lus en entier)."""
    indexes = []
    for pdf in sorted(pathlib.Path(dossier).rglob("*.pdf")):
        try:
            pages = extraire_pdf(pdf)
            if sum(len(t) for _, t in pages) < seuil_car:
                continue
            indexes.append(IndexLivre.charger(pdf, dossier_cache))
        except Exception:
            continue
    return indexes
