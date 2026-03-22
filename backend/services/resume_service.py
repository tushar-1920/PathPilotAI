import pdfkit

def generate_resume_pdf(html):

    pdf = pdfkit.from_string(html, False)

    return pdf