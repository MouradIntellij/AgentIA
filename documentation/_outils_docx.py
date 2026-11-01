# -*- coding: utf-8 -*-
"""Boite a outils de mise en page Word pour le conducteur d'atelier.

Aucun contenu pedagogique ici : uniquement des fonctions de forme
(styles, blocs commande, encadres, tableaux, en-tete/pied de page, sommaire).
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# Palette
ENCRE = "0F172A"
BLEU = "1D4ED8"
BLEU_CLAIR = "EFF6FF"
VERT = "0F766E"
VERT_CLAIR = "ECFDF5"
AMBRE = "B45309"
AMBRE_CLAIR = "FFFBEB"
ROUGE = "B91C1C"
ROUGE_CLAIR = "FEF2F2"
GRIS = "64748B"
GRIS_CLAIR = "F1F5F9"
GRIS_BORD = "CBD5E1"
BLANC = "FFFFFF"


# ------------------------------------------------------------------ bas niveau
def _shd(el_pr, fill):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    el_pr.append(shd)


def shade_paragraph(p, fill):
    _shd(p._p.get_or_add_pPr(), fill)


def shade_cell(cell, fill):
    _shd(cell._tc.get_or_add_tcPr(), fill)


def _borders(el_pr, sides, color, sz=8, space=0):
    bdr = OxmlElement("w:pBdr" if el_pr.tag.endswith("}pPr") else "w:tcBorders")
    for side in sides:
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), str(space))
        el.set(qn("w:color"), color)
        bdr.append(el)
    el_pr.append(bdr)


def paragraph_border(p, sides=("left",), color=BLEU, sz=18, space=6):
    _borders(p._p.get_or_add_pPr(), sides, color, sz, space)


def cell_border(cell, sides=("left",), color=BLEU, sz=24):
    _borders(cell._tc.get_or_add_tcPr(), sides, color, sz)


def table_borders(table, color=GRIS_BORD, sz=4):
    tblPr = table._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{edge}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), str(sz))
        e.set(qn("w:space"), "0")
        e.set(qn("w:color"), color)
        b.append(e)
    tblPr.append(b)


def cell_margins(table, left=110, right=110, top=60, bottom=60):
    tblPr = table._tbl.tblPr
    mar = OxmlElement("w:tblCellMar")
    for side, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        e = OxmlElement(f"w:{side}")
        e.set(qn("w:w"), str(val))
        e.set(qn("w:type"), "dxa")
        mar.append(e)
    tblPr.append(mar)


def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def row_no_split(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def keep_together(p):
    p.paragraph_format.keep_together = True
    p.paragraph_format.keep_with_next = False


def add_field(par, instr, placeholder="1"):
    run = par.add_run()
    f1 = OxmlElement("w:fldChar"); f1.set(qn("w:fldCharType"), "begin")
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr
    f2 = OxmlElement("w:fldChar"); f2.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t"); t.text = placeholder
    f3 = OxmlElement("w:fldChar"); f3.set(qn("w:fldCharType"), "end")
    for e in (f1, it, f2, t, f3):
        run._r.append(e)
    return run


# ------------------------------------------------------------------ document
def nouveau_document():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(1.8)
    sec.left_margin = Cm(2.1)
    sec.right_margin = Cm(2.1)
    sec.header_distance = Cm(0.9)
    sec.footer_distance = Cm(0.9)
    sec.different_first_page_header_footer = True

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor.from_string("1F2937")
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.12

    h1 = doc.styles["Heading 1"]
    h1.font.name = "Calibri"
    h1.font.size = Pt(19)
    h1.font.bold = True
    h1.font.color.rgb = RGBColor.from_string(BLANC)
    h1.paragraph_format.space_before = Pt(0)
    h1.paragraph_format.space_after = Pt(12)
    h1.paragraph_format.page_break_before = True
    h1.paragraph_format.keep_with_next = True
    h1.paragraph_format.left_indent = Cm(0)
    h1.paragraph_format.right_indent = Cm(0)

    h2 = doc.styles["Heading 2"]
    h2.font.name = "Calibri"
    h2.font.size = Pt(13.5)
    h2.font.bold = True
    h2.font.color.rgb = RGBColor.from_string(BLEU)
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(4)
    h2.paragraph_format.keep_with_next = True

    h3 = doc.styles["Heading 3"]
    h3.font.name = "Calibri"
    h3.font.size = Pt(11.5)
    h3.font.bold = True
    h3.font.color.rgb = RGBColor.from_string(VERT)
    h3.paragraph_format.space_before = Pt(10)
    h3.paragraph_format.space_after = Pt(3)
    h3.paragraph_format.keep_with_next = True

    for name in ("List Bullet", "List Number"):
        st = doc.styles[name]
        st.font.name = "Calibri"
        st.font.size = Pt(10.5)
        st.paragraph_format.space_after = Pt(3)
        st.paragraph_format.line_spacing = 1.1
    return doc


def entete_pied(doc, titre_gauche, titre_droit):
    sec = doc.sections[0]
    # En-tete des pages 2+
    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = hp.add_run(titre_gauche)
    r.font.size = Pt(8)
    r.font.color.rgb = RGBColor.from_string(GRIS)
    r.font.name = "Calibri"
    hp.add_run("\t\t")
    r2 = hp.add_run(titre_droit)
    r2.font.size = Pt(8)
    r2.font.color.rgb = RGBColor.from_string(GRIS)
    r2.font.name = "Calibri"
    paragraph_border(hp, ("bottom",), GRIS_BORD, 4, 4)

    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run("Page ")
    r.font.size = Pt(8); r.font.color.rgb = RGBColor.from_string(GRIS)
    add_field(fp, " PAGE ", "1")
    r = fp.add_run(" sur ")
    r.font.size = Pt(8); r.font.color.rgb = RGBColor.from_string(GRIS)
    add_field(fp, " NUMPAGES ", "40")
    r = fp.add_run("   ·   Atelier TechWeek · Collège LaSalle · Automne 2026")
    r.font.size = Pt(8); r.font.color.rgb = RGBColor.from_string(GRIS)


def saut_page(doc):
    doc.add_page_break()


def para(doc, texte="", taille=10.5, gras=False, couleur=None, italique=False,
         align=None, avant=0, apres=5, interligne=1.12, garder=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(avant)
    p.paragraph_format.space_after = Pt(apres)
    p.paragraph_format.line_spacing = interligne
    if align:
        p.alignment = align
    if garder:
        p.paragraph_format.keep_together = True
    if texte:
        r = p.add_run(texte)
        r.font.size = Pt(taille)
        r.bold = gras
        r.italic = italique
        r.font.name = "Calibri"
        if couleur:
            r.font.color.rgb = RGBColor.from_string(couleur)
    return p


def riche(doc, morceaux, taille=10.5, align=None, avant=0, apres=5, interligne=1.12):
    """morceaux = [(texte, {bold, italic, color, size, mono}), ...]"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(avant)
    p.paragraph_format.space_after = Pt(apres)
    p.paragraph_format.line_spacing = interligne
    if align:
        p.alignment = align
    for texte, st in morceaux:
        r = p.add_run(texte)
        r.font.size = Pt(st.get("size", taille))
        r.bold = st.get("bold", False)
        r.italic = st.get("italic", False)
        if st.get("mono"):
            r.font.name = "Consolas"
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        else:
            r.font.name = "Calibri"
        if st.get("color"):
            r.font.color.rgb = RGBColor.from_string(st["color"])
    return p


def h1(doc, numero, titre, sous_titre=None, nouvelle_page=True):
    p = doc.add_paragraph(style="Heading 1")
    p.paragraph_format.page_break_before = nouvelle_page
    shade_paragraph(p, ENCRE)
    p.paragraph_format.left_indent = Cm(0.25)
    p.paragraph_format.right_indent = Cm(0.25)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(f" {numero}. {titre}" if numero is not None else f" {titre}")
    r.font.color.rgb = RGBColor.from_string(BLANC)
    r.bold = True
    r.font.size = Pt(19)
    r.font.name = "Calibri"
    if sous_titre:
        q = doc.add_paragraph()
        q.paragraph_format.space_before = Pt(4)
        q.paragraph_format.space_after = Pt(10)
        r = q.add_run(sous_titre)
        r.italic = True
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor.from_string(GRIS)
    return p


def h2(doc, titre):
    p = doc.add_paragraph(style="Heading 2")
    r = p.add_run(titre)
    r.font.name = "Calibri"
    paragraph_border(p, ("bottom",), "DBEAFE", 8, 3)
    return p


def h3(doc, titre):
    p = doc.add_paragraph(style="Heading 3")
    p.add_run(titre)
    return p


def puces(doc, items, taille=10.5, style="List Bullet", apres=3):
    for it in items:
        p = doc.add_paragraph(style=style)
        p.paragraph_format.space_after = Pt(apres)
        p.paragraph_format.line_spacing = 1.1
        if isinstance(it, tuple):
            texte, detail = it
            r = p.add_run(texte)
            r.bold = True
            r.font.size = Pt(taille)
            r.font.name = "Calibri"
            r2 = p.add_run(" — " + detail)
            r2.font.size = Pt(taille)
            r2.font.name = "Calibri"
        else:
            r = p.add_run(it)
            r.font.size = Pt(taille)
            r.font.name = "Calibri"


def bloc(doc, etiquette, texte, couleur=ENCRE, fond=GRIS_CLAIR, taille=9, mono=True):
    lab = doc.add_paragraph()
    lab.paragraph_format.space_before = Pt(7)
    lab.paragraph_format.space_after = Pt(2)
    lab.paragraph_format.keep_with_next = True
    r = lab.add_run(etiquette.upper())
    r.font.size = Pt(7.5)
    r.bold = True
    r.font.name = "Calibri"
    r.font.color.rgb = RGBColor.from_string(couleur)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.left_indent = Cm(0.1)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.keep_together = True
    shade_paragraph(p, fond)
    paragraph_border(p, ("left",), couleur, 24, 8)

    lignes = texte.split("\n")
    for i, ligne in enumerate(lignes):
        r = p.add_run(ligne)
        r.font.size = Pt(taille)
        r.font.name = "Consolas" if mono else "Calibri"
        if mono:
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        r.font.color.rgb = RGBColor.from_string("111827")
        if i < len(lignes) - 1:
            r.add_break()
    return p


def encadre(doc, etiquette, texte, couleur=BLEU, fond=BLEU_CLAIR, taille=10):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    cell = t.cell(0, 0)
    cell.width = Cm(16.6)
    shade_cell(cell, fond)
    cell_border(cell, ("left",), couleur, 30)
    cell_margins(t, left=160, right=160, top=90, bottom=90)
    row_no_split(t.rows[0])

    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(etiquette.upper())
    r.font.size = Pt(7.5)
    r.bold = True
    r.font.name = "Calibri"
    r.font.color.rgb = RGBColor.from_string(couleur)

    p2 = cell.add_paragraph()
    p2.paragraph_format.space_after = Pt(0)
    p2.paragraph_format.line_spacing = 1.1
    r = p2.add_run(texte)
    r.font.size = Pt(taille)
    r.font.name = "Calibri"
    r.font.color.rgb = RGBColor.from_string("1F2937")

    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(4)
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.line_spacing = Pt(3)
    return t


def tableau(doc, entetes, lignes, largeurs=None, taille=8.8, entete_fond=ENCRE,
            zebre=True, aligne_gauche=True):
    t = doc.add_table(rows=1, cols=len(entetes))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    table_borders(t, GRIS_BORD, 4)
    cell_margins(t, 90, 90, 45, 45)

    hdr = t.rows[0]
    repeat_header(hdr)
    for i, h in enumerate(entetes):
        c = hdr.cells[i]
        shade_cell(c, entete_fond)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(taille)
        r.font.name = "Calibri"
        r.font.color.rgb = RGBColor.from_string(BLANC)

    for j, ligne in enumerate(lignes):
        row = t.add_row()
        for i, val in enumerate(ligne):
            c = row.cells[i]
            if zebre and j % 2 == 1:
                shade_cell(c, "F8FAFC")
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            if not aligne_gauche:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            # gras local avec **...**
            morceaux = str(val).split("**")
            for k, m in enumerate(morceaux):
                if not m:
                    continue
                r = p.add_run(m)
                r.font.size = Pt(taille)
                r.font.name = "Calibri"
                r.bold = (k % 2 == 1)
                r.font.color.rgb = RGBColor.from_string("1F2937")

    if largeurs:
        for row in t.rows:
            for i, w in enumerate(largeurs):
                row.cells[i].width = Cm(w)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(0)
    return t


def fiche_etape(doc, fichier, duree, mode, sortie):
    t = doc.add_table(rows=1, cols=4)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    table_borders(t, "E2E8F0", 4)
    cell_margins(t, 100, 100, 50, 50)
    vals = [(fichier, "FICHIER"), (duree, "DURÉE"), (mode, "MODE"), (sortie, "SORTIE")]
    for i, (v, lab) in enumerate(vals):
        c = t.rows[0].cells[i]
        c.width = Cm(4.15)
        shade_cell(c, GRIS_CLAIR)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(lab)
        r.font.size = Pt(6.8)
        r.bold = True
        r.font.color.rgb = RGBColor.from_string(GRIS)
        p2 = c.add_paragraph()
        p2.paragraph_format.space_after = Pt(0)
        r = p2.add_run(v)
        r.font.size = Pt(9)
        r.bold = True
        r.font.name = "Consolas" if i == 0 else "Calibri"
        r.font.color.rgb = RGBColor.from_string(ENCRE)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(1)
    return t


def sommaire(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Sommaire")
    r.font.size = Pt(18)
    r.bold = True
    r.font.color.rgb = RGBColor.from_string(ENCRE)

    note = doc.add_paragraph()
    note.paragraph_format.space_after = Pt(10)
    r = note.add_run("Le sommaire se met à jour tout seul à l'ouverture : si les numéros de page "
                     "sont absents, faites Ctrl+A puis F9 (ou clic droit → Mettre à jour les champs).")
    r.font.size = Pt(8.5)
    r.italic = True
    r.font.color.rgb = RGBColor.from_string(GRIS)

    par = doc.add_paragraph()
    add_field(par, ' TOC \\o "1-2" \\h \\z \\u ', "Sommaire — Ctrl+A puis F9 pour afficher les pages")
