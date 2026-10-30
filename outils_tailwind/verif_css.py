"""Verifie que TOUTES les classes Tailwind des 3 pages existent dans static/app.css.
Lancer depuis la racine du projet : python outils_tailwind/verif_css.py"""
import ast, os, pathlib, re

os.chdir(pathlib.Path(__file__).resolve().parent.parent)
css = open("static/app.css", encoding="utf-8").read()

def esc(t):
    return "".join(("\\" + c) if c in ".:/[]%(),#!<>=+'\"&~*" else c for c in t)

total = 0
for app in ["app_final.py", "app_tp.py", "app_maths.py"]:
    tree = ast.parse(open(app, encoding="utf-8").read())
    page = next(n.value.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
                for t in n.targets if isinstance(t, ast.Name) and t.id == "PAGE")
    classes = set()
    for m in re.finditer(r"class=(?:\"([^\"]*)\"|'([^']*)'|([A-Za-z0-9_\-]+))", page):
        for c in (m.group(1) or m.group(2) or m.group(3) or "").split():
            if re.fullmatch(r"[A-Za-z0-9_\-./\[\]%():#,]+", c):
                classes.add(c)
    manque = sorted(c for c in classes if ("." + esc(c)) not in css)
    total += len(manque)
    print(f"{app}: {len(classes)} classes, manquantes = {manque}")
print("RESULTAT :", "OK - CSS complet" if total == 0 else f"{total} classe(s) a reconstruire")
