import time
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

def generate_report_document(report_data, path, name):
    doc = SimpleDocTemplate(str(path.absolute()),
                        rightMargin=18,leftMargin=18,
                        topMargin=72,bottomMargin=18)
    stylesheet = getSampleStyleSheet()
    story=[]

    # Header
    story.append(Paragraph(f"{name} - Certification Report",  stylesheet["Heading1"]))
    story.append(Paragraph(f"{time.ctime()}"))
    story.append(Spacer(1, 12))

    # List each test case with results
    for name, result in report_data.items():
        story.append(Paragraph(name, stylesheet["Heading2"]))

        # Evaluated metrics
        metrics_data = [
            [
                Paragraph("Metric", stylesheet["Heading4"]),
                Paragraph("Value", stylesheet["Heading4"]),
                Paragraph("Result", stylesheet["Heading4"])
            ],
            [
                Paragraph("SSIM"), 
                Paragraph(f'<code>{result["metrics"]["ssim"]:10.5f}</code>'), 
                Paragraph("Passed" if result["passed"]["ssim"] else '<font color="red">Failed</font>')
            ],
            [
                Paragraph("PSNR"), 
                Paragraph(f'<code>{result["metrics"]["psnr"]:10.5f}</code>'), 
                Paragraph("Passed" if result["passed"]["psnr"] else '<font color="red">Failed</font>')
            ],
        ]
        t = Table(metrics_data, 3 * [2.5 * inch])
        t.setStyle(TableStyle([
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

        # Image Comparison
        images_data = [
            [ 
                Paragraph("Reference", stylesheet["Heading4"]), 
                Paragraph("Submission", stylesheet["Heading4"]), 
                Paragraph("Difference", stylesheet["Heading4"])
            ],
            [
                Image(result["images"]["reference_path"], width=2*inch, height=2*inch),
                Image(result["images"]["candidate_path"], width=2*inch, height=2*inch),
                Image(result["images"]["diff_path"], width=2*inch, height=2*inch),
            ]
        ]
        t = Table(images_data, 3 * [2.5 * inch])
        t.setStyle(TableStyle([
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))
        
    doc.build(story)
