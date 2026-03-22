import uuid
import os
import tempfile

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.colors import HexColor, black, blue
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ── COLORS ──────────────────────────────────────────
C_BLACK  = black
C_LINK   = HexColor('#1a0dab')
C_BODY   = HexColor('#111111')
C_RULE   = black

# ── FONT SIZES ──────────────────────────────────────
FS_NAME    = 20
FS_TITLE   = 10.5
FS_CONTACT = 9.5
FS_SECTION = 11
FS_BODY    = 10
FS_BULLET  = 9.5

# ── PAGE MARGINS ────────────────────────────────────
ML = 0.75 * inch
MR = 0.75 * inch
MT = 0.6  * inch
MB = 0.6  * inch


def _styles():
    """Return all paragraph styles used in the resume."""
    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    base = dict(fontName='Times-Roman', fontSize=FS_BODY,
                leading=14, textColor=C_BODY)

    return {
        'name': S('name',
            fontName='Times-Bold', fontSize=FS_NAME,
            leading=24, alignment=TA_CENTER, textColor=C_BLACK,
            spaceAfter=2),

        'subtitle': S('subtitle',
            fontName='Times-Bold', fontSize=FS_TITLE,
            leading=14, alignment=TA_CENTER, textColor=C_BLACK,
            spaceAfter=3),

        'contact': S('contact',
            fontName='Times-Roman', fontSize=FS_CONTACT,
            leading=13, alignment=TA_CENTER, textColor=C_BODY,
            spaceAfter=2),

        'links': S('links',
            fontName='Times-Roman', fontSize=FS_CONTACT,
            leading=13, alignment=TA_CENTER, textColor=C_BODY,
            spaceAfter=4),

        'section_title': S('section_title',
            fontName='Times-Bold', fontSize=FS_SECTION,
            leading=14, textColor=C_BLACK, spaceBefore=7, spaceAfter=3),

        'body': S('body', **base, spaceAfter=2),

        'body_italic': S('body_italic',
            fontName='Times-Italic', fontSize=FS_BULLET,
            leading=13, textColor=C_BODY, spaceAfter=1),

        'bold_left': S('bold_left',
            fontName='Times-Bold', fontSize=FS_BODY,
            leading=13, textColor=C_BLACK),

        'bullet': S('bullet',
            fontName='Times-Roman', fontSize=FS_BULLET,
            leading=13, textColor=C_BODY,
            leftIndent=12, firstLineIndent=0,
            spaceAfter=1),

        'skills': S('skills',
            fontName='Times-Roman', fontSize=FS_BULLET,
            leading=14, textColor=C_BODY, spaceAfter=2),

        'honor': S('honor',
            fontName='Times-Roman', fontSize=FS_BULLET,
            leading=13, textColor=C_BODY,
            leftIndent=12, spaceAfter=1),
    }


def _link(url, text):
    """Return a hyperlink string for Reportlab Paragraph."""
    if not url:
        return text
    href = url if url.startswith('http') else 'https://' + url
    return f'<link href="{href}" color="#1a0dab"><u>{text}</u></link>'


def _section_block(story, title, styles):
    """Add a bold section title + horizontal rule."""
    story.append(Spacer(1, 4))
    story.append(Paragraph(title.upper(), styles['section_title']))
    story.append(HRFlowable(
        width='100%', thickness=0.9, color=C_RULE,
        spaceAfter=4, spaceBefore=0
    ))


def _bullet_lines(text, styles):
    """Convert newline-separated text into bullet Paragraphs."""
    items = []
    for line in (text or '').split('\n'):
        line = line.strip().lstrip('*-•').strip()
        if line:
            # Bold the first phrase before a colon if present
            if ':' in line:
                parts = line.split(':', 1)
                para_text = f'<b>{parts[0]}:</b>{parts[1]}'
            else:
                para_text = line
            items.append(Paragraph(f'• {para_text}', styles['bullet']))
    return items


def _two_col(left_text, right_text, styles, left_bold=True, right_bold=True):
    """Return a Table row with left text and right-aligned date."""
    lf = 'Times-Bold' if left_bold  else 'Times-Roman'
    rf = 'Times-Bold' if right_bold else 'Times-Roman'
    left  = Paragraph(f'<font name="{lf}">{left_text}</font>',  styles['body'])
    right = Paragraph(f'<font name="{rf}">{right_text}</font>',
                      ParagraphStyle('r', fontName=rf, fontSize=FS_BODY,
                                     leading=13, alignment=TA_RIGHT, textColor=C_BLACK))
    t = Table([[left, right]], colWidths=['72%', '28%'])
    t.setStyle(TableStyle([
        ('VALIGN',      (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING',(0,0), (-1,-1), 0),
        ('TOPPADDING',  (0,0), (-1,-1), 0),
        ('BOTTOMPADDING',(0,0),(-1,-1), 0),
    ]))
    return t


def generate_resume(data):
    """
    Generate a PDF resume using ReportLab (pure Python).
    No pdflatex / LaTeX installation required.
    Returns the path to the generated PDF file.
    """
    styles = _styles()

    file_id  = str(uuid.uuid4())
    pdf_path = os.path.join(tempfile.gettempdir(), f'resume_{file_id}.pdf')

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=ML, rightMargin=MR,
        topMargin=MT, bottomMargin=MB,
        title=f"{data.get('name','Resume')} - Resume",
        author=data.get('name',''),
    )

    story = []

    # ── HEADER ────────────────────────────────────────────
    name  = (data.get('name') or 'YOUR NAME').upper()
    title = data.get('title', '')

    story.append(Paragraph(name,  styles['name']))
    if title:
        story.append(Paragraph(f'<b>{title}</b>', styles['subtitle']))

    # Contact line
    contact_parts = []
    if data.get('location'): contact_parts.append(data['location'])
    if data.get('email'):
        contact_parts.append(_link(f"mailto:{data['email']}", data['email']))
    if data.get('phone'):    contact_parts.append(data['phone'])
    if contact_parts:
        story.append(Paragraph(' | '.join(contact_parts), styles['contact']))

    # Links line
    link_parts = []
    if data.get('linkedin'):   link_parts.append(_link(data['linkedin'],   'LinkedIn'))
    if data.get('github'):     link_parts.append(_link(data['github'],     'GitHub'))
    if data.get('portfolio'):  link_parts.append(_link(data['portfolio'],  'Portfolio'))
    if data.get('hackerrank'): link_parts.append(_link(data['hackerrank'],'HackerRank'))
    if data.get('leetcode'):   link_parts.append(_link(data['leetcode'],   'LeetCode'))
    if link_parts:
        story.append(Paragraph(' | '.join(link_parts), styles['links']))

    story.append(Spacer(1, 4))

    # ── SUMMARY ───────────────────────────────────────────
    summary = data.get('summary', '').strip()
    if summary:
        _section_block(story, 'Profile Summary', styles)
        story.append(Paragraph(summary, styles['body']))

    # ── EDUCATION ─────────────────────────────────────────
    edu_raw = data.get('education', '').strip()
    if edu_raw:
        _section_block(story, 'Education', styles)
        # Parse the LaTeX-like blocks from JS into structured data
        # Each entry is separated by \item
        entries = _parse_edu_block(edu_raw)
        for e in entries:
            block = []
            if e.get('degree') or e.get('year'):
                block.append(_two_col(
                    f"<b>{e.get('degree','')}</b>",
                    f"<b>{e.get('year','')}</b>",
                    styles
                ))
            if e.get('school'):
                block.append(Paragraph(e['school'], styles['body']))
            if e.get('grade'):
                block.append(Paragraph(e['grade'],  styles['body']))
            block.append(Spacer(1, 4))
            story.extend(block)

    # ── INTERNSHIP ────────────────────────────────────────
    intern_raw = data.get('internship', '').strip()
    if intern_raw:
        _section_block(story, 'Internship', styles)
        entries = _parse_exp_block(intern_raw)
        for e in entries:
            block = []
            header = e.get('company','')
            if e.get('role'): header += f" \u2014 {e['role']}"
            block.append(_two_col(header, e.get('date',''), styles))
            if e.get('desc'):
                block.append(Paragraph(
                    f'<i>{e["desc"]}</i>', styles['body_italic']))
            block.extend(_bullet_lines(e.get('bullets',''), styles))
            block.append(Spacer(1, 4))
            story.append(KeepTogether(block))

    # ── PROJECTS ──────────────────────────────────────────
    proj_raw = data.get('projects', '').strip()
    if proj_raw:
        _section_block(story, 'Projects', styles)
        entries = _parse_proj_block(proj_raw)
        for e in entries:
            block = []
            name_cell = f"<b>{e.get('name','')}</b>"
            gh_cell   = _link(e.get('github',''), 'GitHub') if e.get('github') else ''
            block.append(_two_col(name_cell, gh_cell, styles, right_bold=False))
            if e.get('tech'):
                block.append(Paragraph(
                    f'<b>Technologies:</b> {e["tech"]}', styles['skills']))
            if e.get('desc'):
                block.append(Paragraph(e['desc'], styles['body_italic']))
            block.extend(_bullet_lines(e.get('bullets',''), styles))
            block.append(Spacer(1, 4))
            story.append(KeepTogether(block))

    # ── SKILLS ────────────────────────────────────────────
    skills_raw = data.get('skills', '').strip()
    if skills_raw:
        _section_block(story, 'Technical Skills', styles)
        for line in skills_raw.split('\n'):
            line = line.strip()
            if not line: continue
            # Convert "\textbf{X:} Y" -> "<b>X:</b> Y"  OR plain "X: Y"
            line = line.replace('\\textbf{', '<b>').replace('}', '</b>', 1) \
                       .replace('\\&', '&').replace('\\\\', '')
            story.append(Paragraph(line, styles['skills']))

    # ── HONORS ────────────────────────────────────────────
    honors_raw = data.get('honors', '').strip()
    if honors_raw:
        _section_block(story, 'Honors & Achievements', styles)
        for line in _extract_items(honors_raw):
            story.append(Paragraph(f'• {line}', styles['honor']))

    # ── CERTIFICATIONS ────────────────────────────────────
    cert_raw = data.get('certifications', '').strip()
    if cert_raw:
        _section_block(story, 'Certifications', styles)
        for line in _extract_items(cert_raw):
            story.append(Paragraph(f'• {line}', styles['honor']))

    # ── BUILD ─────────────────────────────────────────────
    doc.build(story)

    print(f"[ResumeBuilder] PDF created at: {pdf_path}")
    return pdf_path


# ── PARSERS ───────────────────────────────────────────────
# These parse the LaTeX-style strings that collectData() in JS produces

def _parse_edu_block(raw):
    """Parse education LaTeX block into list of dicts."""
    entries = []
    # Split on \item
    items = raw.split('\\item')
    for item in items:
        item = item.strip()
        if not item: continue
        e = {}
        lines = [l.strip() for l in item.split('\n') if l.strip()]
        for i, line in enumerate(lines):
            line = _clean_latex(line)
            if i == 0:
                # First line has degree and year: "Degree\hfill Year"
                parts = line.split('\\hfill') if '\\hfill' in line else [line, '']
                e['degree'] = _clean_latex(parts[0])
                e['year']   = _clean_latex(parts[1]) if len(parts)>1 else ''
            elif i == 1:
                e['school'] = _clean_latex(line)
            elif i == 2:
                e['grade']  = _clean_latex(line)
        if e:
            entries.append(e)
    return entries


def _parse_exp_block(raw):
    """Parse internship/experience LaTeX block into list of dicts."""
    entries = []
    # Split on \noindent\textbf{ which starts each entry
    parts = raw.split('\\noindent')
    for part in parts:
        part = part.strip()
        if not part: continue
        e = {}
        lines = part.split('\n')
        header_line = _clean_latex(lines[0]) if lines else ''

        # "Company -- Role\hfill Date"
        if '\\hfill' in lines[0]:
            left_right = lines[0].split('\\hfill')
            left  = _clean_latex(left_right[0])
            e['date'] = _clean_latex(left_right[1]) if len(left_right)>1 else ''
        else:
            left = header_line
            e['date'] = ''

        if ' -- ' in left:
            parts2 = left.split(' -- ', 1)
            e['company'] = parts2[0]
            e['role']    = parts2[1]
        else:
            e['company'] = left
            e['role']    = ''

        # Collect description and bullets
        desc_lines = []
        bullet_lines = []
        in_items = False
        for line in lines[1:]:
            line_c = line.strip()
            if '\\begin{itemize}' in line_c: in_items = True;  continue
            if '\\end{itemize}'   in line_c: in_items = False; continue
            if in_items and '\\item' in line_c:
                bullet_lines.append(_clean_latex(line_c.replace('\\item','')))
            elif line_c.startswith('\\textit{') or line_c.startswith('\\textbf{'):
                desc_lines.append(_clean_latex(line_c))

        e['desc']    = ' '.join(desc_lines)
        e['bullets'] = '\n'.join(bullet_lines)
        entries.append(e)
    return entries


def _parse_proj_block(raw):
    """Parse projects LaTeX block into list of dicts."""
    entries = []
    parts = raw.split('\\noindent')
    for part in parts:
        part = part.strip()
        if not part: continue
        e = {}
        lines = part.split('\n')

        # First line: Name\hfillGitHub link
        first = lines[0] if lines else ''
        if '\\hfill' in first:
            halves = first.split('\\hfill', 1)
            e['name']   = _clean_latex(halves[0])
            e['github'] = _extract_href(halves[1])
        else:
            e['name'] = _clean_latex(first)
            e['github'] = ''

        tech_lines  = []
        desc_lines  = []
        bullet_lines= []
        in_items = False
        for line in lines[1:]:
            ls = line.strip()
            if '\\begin{itemize}' in ls: in_items = True;  continue
            if '\\end{itemize}'   in ls: in_items = False; continue
            if in_items and '\\item' in ls:
                bullet_lines.append(_clean_latex(ls.replace('\\item', '')))
            elif '\\textbf{Technologies' in ls or 'Technologies:' in _clean_latex(ls):
                tech_lines.append(_clean_latex(ls).replace('Technologies:', '').strip())
            elif ls and not ls.startswith('\\vspace'):
                desc_lines.append(_clean_latex(ls))

        e['tech']    = ' '.join(tech_lines)
        e['desc']    = ' '.join(desc_lines)
        e['bullets'] = '\n'.join(bullet_lines)
        entries.append(e)
    return entries


def _extract_items(raw):
    """Extract bullet items from a LaTeX itemize block."""
    items = []
    for line in raw.split('\n'):
        ls = line.strip()
        if '\\item' in ls:
            item = _clean_latex(ls.replace('\\item', '').strip())
            if item:
                items.append(item)
        elif ls and '\\begin' not in ls and '\\end' not in ls:
            cleaned = _clean_latex(ls)
            if cleaned:
                items.append(cleaned)
    return items


def _clean_latex(text):
    """Strip common LaTeX commands from a string."""
    if not text: return ''
    import re
    text = text.replace('\\textbf{', '').replace('\\textit{', '') \
               .replace('\\href{', '').replace('\\hfill', '') \
               .replace('\\noindent', '').replace('\\raggedright', '') \
               .replace('\\vspace{-4pt}', '').replace('\\\\', '') \
               .replace('\\&', '&').replace('\\%', '%') \
               .replace('\\$', '$').replace('\\_', '_') \
               .replace('\\--', '—')
    # Remove remaining \command{...} patterns
    text = re.sub(r'\\[a-zA-Z]+\*?\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+\*?',            '',     text)
    text = re.sub(r'\{([^}]*)\}',               r'\1',  text)
    return text.strip().strip('\\').strip()


def _extract_href(text):
    r"""Extract URL from \href{url}{text}."""
    import re
    m = re.search(r'\\href\{([^}]+)\}', text)
    if m: return m.group(1)
    # Try plain URL
    m2 = re.search(r'https?://\S+', text)
    if m2: return m2.group(0)
    return ''