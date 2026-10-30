"""PARTAGER - expose l'agent sur Internet sans compte, sans cle API, sans redirection de port.

Principe : un tunnel Cloudflare sortant depuis CE PC vers un domaine jetable
https://<random>.trycloudflare.com. Rien n'est ouvert sur le routeur, aucun compte
Cloudflare n'est necessaire. Le tunnel meurt des que ce script s'arrete (Ctrl+C).

    python partager.py            -> protege par une cle aleatoire (?k=...)
    python partager.py --sans-cle -> lien public ouvert (deconseille)
    python partager.py 3002       -> partage app_tp.py au lieu de app_final.py

Journal du tunnel : resultats\\tunnel.log
Lien courant     : resultats\\lien_public.txt
"""
import os, re, sys, time, socket, secrets, pathlib, subprocess, webbrowser, urllib.request

RACINE = pathlib.Path(__file__).resolve().parent
PORTS = {"3000": "app_final.py", "3001": "app_maths.py", "3002": "app_tp.py"}
CF = RACINE / "outils_tunnel" / "cloudflared.exe"
LOG = RACINE / "resultats" / "tunnel.log"
URL_RE = re.compile(r"https://[a-z0-9][a-z0-9-]*\.trycloudflare\.com")


def port_repond(port, timeout=1.5):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            return True
    except OSError:
        return False


def attendre_port(port, limite=45):
    debut = time.time()
    while time.time() - debut < limite:
        if port_repond(port):
            return True
        time.sleep(0.5)
    return False


def attendre_dns(hote, limite=25):
    # Le sous-domaine met quelques secondes a exister cote Cloudflare.
    debut = time.time()
    while time.time() - debut < limite:
        try:
            socket.getaddrinfo(hote, 443)
            return True
        except OSError:
            time.sleep(1)
    return False


def trouver_cloudflared():
    if CF.exists():
        return CF
    import shutil
    sur_path = shutil.which("cloudflared")
    if sur_path:
        return pathlib.Path(sur_path)
    print("cloudflared absent : telechargement (52 Mo, une seule fois)...")
    CF.parent.mkdir(parents=True, exist_ok=True)
    source = ("https://github.com/cloudflare/cloudflared/releases/latest/download/"
              "cloudflared-windows-amd64.exe")
    urllib.request.urlretrieve(source, CF)
    print("cloudflared installe dans outils_tunnel\\")
    return CF


def demarrer_tunnel(exe, port):
    """Ecrit la sortie de cloudflared dans un fichier (jamais dans un pipe : il se remplirait
    et bloquerait le tunnel). http2 d'abord : le QUIC (UDP 7844) est souvent filtre en reseau scolaire."""
    LOG.parent.mkdir(exist_ok=True)
    for protocole in ("http2", "quic"):
        journal = open(LOG, "w", encoding="utf-8", errors="replace")
        cmd = [str(exe), "tunnel", "--url", f"http://127.0.0.1:{port}",
               "--no-autoupdate", "--protocol", protocole]
        p = subprocess.Popen(cmd, stdout=journal, stderr=subprocess.STDOUT, cwd=str(RACINE))
        debut = time.time()
        url = None
        while time.time() - debut < 45:
            if p.poll() is not None:
                break
            try:
                m = URL_RE.search(LOG.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                m = None
            if m:
                url = m.group(0)
                break
            time.sleep(0.5)
        if url:
            return p, url, journal
        p.terminate(); journal.close()
        print(f"  (protocole {protocole} : aucune URL, essai suivant...)")
    return None, None, None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    port = int(args[0]) if args and args[0].isdigit() else 3000
    app = PORTS.get(str(port), "app_final.py")
    sans_cle = "--sans-cle" in sys.argv

    if str(port) not in PORTS:
        print(f"Port {port} inconnu : choisissez 3000 (agent), 3001 (maths) ou 3002 (TP).")
        return 1

    exe = trouver_cloudflared()
    cle = "" if sans_cle else secrets.token_urlsafe(6)
    serveur = None

    if port_repond(port):
        print(f"Un serveur repond deja sur {port} : il est reutilise TEL QUEL.")
        if cle:
            try:
                input("  -> il n'aura donc PAS de cle d'acces. Entree pour continuer, Ctrl+C pour annuler. ")
            except (EOFError, KeyboardInterrupt):
                return 1
            cle = ""
    else:
        env = dict(os.environ)
        if cle:
            env["CLE_ACCES"] = cle
        print(f"Demarrage de {app} sur 127.0.0.1:{port}...")
        serveur = subprocess.Popen([sys.executable, app], cwd=str(RACINE), env=env)
        if not attendre_port(port):
            print(f"ECHEC : {app} ne repond pas sur {port}. Lancez-le a la main pour voir l'erreur.")
            serveur.terminate()
            return 1

    print("Ouverture du tunnel Cloudflare...")
    tunnel, url, journal = demarrer_tunnel(exe, port)
    if not url:
        print("ECHEC : pas d'URL. Le journal est dans resultats\\tunnel.log")
        if serveur:
            serveur.terminate()
        return 1

    hote = url.split("//", 1)[1].split("/", 1)[0]
    if not attendre_dns(hote):
        print("  (le nom n'est pas encore visible en DNS ; le lien peut demander 30 s de plus)")

    lien = url + (f"/?k={cle}" if cle else "")
    (RACINE / "resultats").mkdir(exist_ok=True)
    (RACINE / "resultats" / "lien_public.txt").write_text(lien + "\n", encoding="utf-8")

    print()
    print("=" * 70)
    print("  LIEN PUBLIC (a donner aux etudiants) :")
    print("  " + lien)
    if cle:
        print()
        print(f"  Cle d'acces : {cle}")
        print("  Sans ?k=..., la page affiche 403. Le cookie est pose a la 1re visite.")
    else:
        print("  ATTENTION : aucune protection, toute personne ayant le lien entre.")
    print()
    print("  Lien aussi ecrit dans : resultats\\lien_public.txt")
    print("  Journal du tunnel     : resultats\\tunnel.log")
    print("  Fermer cette fenetre (ou Ctrl+C) = le lien public s'arrete.")
    print("=" * 70)
    print()

    try:
        webbrowser.open(lien)
    except Exception:
        pass

    try:
        while True:
            if tunnel.poll() is not None:
                print("Le tunnel s'est arrete (Cloudflare a coupe). Consultez resultats\\tunnel.log.")
                break
            if serveur and serveur.poll() is not None:
                print(f"{app} s'est arrete (plantage ?). Fermeture du tunnel.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nArret du tunnel...")
    finally:
        tunnel.terminate()
        if journal:
            journal.close()
        if serveur:
            serveur.terminate()
        print("Termine : le lien public ne fonctionne plus.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
