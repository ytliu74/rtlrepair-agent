"""Compact the Word export for the instructor's two-page limit; preserve content."""
from pathlib import Path
from xml.dom import minidom
from zipfile import ZipFile


def child(parent, name):
    for node in parent.childNodes:
        if node.nodeType == node.ELEMENT_NODE and node.tagName == name:
            return node
    node = parent.ownerDocument.createElement(name)
    parent.appendChild(node)
    return node


def set_body_font(runs):
    fonts = child(runs, "w:rFonts")
    # Explicit font names must not be overridden by theme font references.
    for attribute in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme", "csTheme"):
        if fonts.hasAttribute("w:" + attribute):
            fonts.removeAttribute("w:" + attribute)
    for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.setAttribute("w:" + attribute, "Arial")


path = Path("proposal/capstone_proposal.docx")
with ZipFile(path) as archive:
    entries = [(entry, archive.read(entry.filename)) for entry in archive.infolist()]

with ZipFile(path, "w") as archive:
    for entry, data in entries:
        if entry.filename == "word/styles.xml":
            xml = minidom.parseString(data)
            defaults = child(xml.documentElement, "w:docDefaults")
            set_body_font(child(child(defaults, "w:rPrDefault"), "w:rPr"))
            for style in xml.getElementsByTagName("w:style"):
                identifier = style.getAttribute("w:styleId")
                if identifier in {"Normal", "BodyText", "FirstParagraph", "Compact", "Caption", "ImageCaption"}:
                    set_body_font(child(style, "w:rPr"))
                if identifier in {"Normal", "BodyText", "FirstParagraph", "Heading2", "Caption", "ImageCaption"}:
                    size = "24" if identifier == "Heading2" else "22"
                    runs = child(style, "w:rPr")
                    child(runs, "w:sz").setAttribute("w:val", size)
                    child(runs, "w:szCs").setAttribute("w:val", size)
                    spacing = child(child(style, "w:pPr"), "w:spacing")
                    spacing.setAttribute("w:before", "100" if identifier == "Heading2" else "0")
                    spacing.setAttribute("w:after", "60")
                    spacing.setAttribute("w:line", "240")
                    spacing.setAttribute("w:lineRule", "auto")
            data = xml.toxml(encoding="UTF-8")
        elif entry.filename == "word/document.xml":
            xml = minidom.parseString(data)
            # Keep the setup instructions together on page two, matching the PDF.
            for paragraph in xml.getElementsByTagName("w:p"):
                text = "".join(
                    node.firstChild.data
                    for node in paragraph.getElementsByTagName("w:t")
                    if node.firstChild is not None
                )
                if text == "Section 5. Reproducibility and Run Instructions":
                    child(child(paragraph, "w:pPr"), "w:pageBreakBefore")
            for margin in xml.getElementsByTagName("w:pgMar"):
                for side in ("top", "bottom", "left", "right"):
                    margin.setAttribute("w:" + side, "1152")  # 0.8 inches, matching PDF.
            data = xml.toxml(encoding="UTF-8")
        archive.writestr(entry, data)

print("Word export formatted: 11-point Arial body, 12-point headings, 0.8-inch margins.")
