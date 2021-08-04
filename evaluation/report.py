import time
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors, pagesizes
import json

def generate_report_json(report_data, path):
    report = { 
        k: { 
            "metrics" : v["metrics"],
            "passed": {
                key: bool(passed)
                for (key, passed) 
                in v["passed"].items()
            },
            "image_paths": {
                key: str(p) 
                for (key, p) 
                in v["image_paths"].items()
            }
        }
        for (k, v)
        in report_data.items()
    }

    with open(path / "report.json", 'w') as f:
        json.dump(report, f, indent=4)

def generate_report_document(report_data, path, name):
    doc = SimpleDocTemplate(str(path.absolute() / "report.pdf"), 
                        pagesize=pagesizes.A4,
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
        cell_size = (doc.width / 3)
        metrics_data = [
            [
                Paragraph("Metric", stylesheet["Heading4"]),
                Paragraph("Value", stylesheet["Heading4"]),
                Paragraph("Result", stylesheet["Heading4"])
            ],
            [
                Paragraph("SSIM"), 
                Paragraph(f'<code>{result["metrics"]["ssim"]:10.5f}</code>'), 
                Paragraph("Above Threshold" if result["passed"]["ssim"] else '<font color="orange">Below Threshold</font>')
            ],
            [
                Paragraph("PSNR"), 
                Paragraph(f'<code>{result["metrics"]["psnr"]:10.5f}</code>'), 
                Paragraph("Above Threshold" if result["passed"]["psnr"] else '<font color="orange">Below Threshold</font>')
            ],
        ]
        t = Table(metrics_data, 3 * [cell_size])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

        # Candidate and reference image
        image_size = (doc.width / 2)
        margin = {"left": 6, "right": 6, "top": 6, "bottom": 6}
        images_data = [
            [ 
                Paragraph("Reference", stylesheet["Heading4"]), 
                Paragraph("Submission", stylesheet["Heading4"]), 
            ],
            [
                Image(
                    path / result["image_paths"]["reference"], 
                    width=image_size - (margin["left"] + margin["right"]), 
                    height=image_size - (margin["top"] + margin["bottom"])
                ),
                Image(
                    path / result["image_paths"]["candidate"], 
                    width=image_size - (margin["left"] + margin["right"]), 
                    height=image_size - (margin["top"] + margin["bottom"])
                ),
            ]
        ]
        t = Table(images_data, 2 * [image_size])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.25, colors.black),
            ('LEFTPADDING', (0, 1), (-1, -1), margin["left"]),
            ('RIGHTPADDING', (0, 1), (-1, -1), margin["right"]),
            ('TOPPADDING', (0, 1), (-1, -1), margin["top"]),
            ('BOTTOMPADDING', (0, 1), (-1, -1), margin["bottom"])
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

        # computed images
        image_size = (doc.width / 2)
        images_data = [
            [ 
                Paragraph("Difference", stylesheet["Heading4"]),
                Paragraph("5% Threshold", stylesheet["Heading4"]),
            ],
            [
                Image(
                    path / result["image_paths"]["diff"], 
                    width=image_size - (margin["left"] + margin["right"]), 
                    height=image_size - (margin["top"] + margin["bottom"])
                ),
                Image(
                    path / result["image_paths"]["threshold"], 
                    width=image_size - (margin["left"] + margin["right"]), 
                    height=image_size - (margin["top"] + margin["bottom"])
                ),
            ]
        ]
        t = Table(images_data, 2 * [image_size])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.25, colors.black),
            ('LEFTPADDING', (0, 1), (-1, -1), margin["left"]),
            ('RIGHTPADDING', (0, 1), (-1, -1), margin["right"]),
            ('TOPPADDING', (0, 1), (-1, -1), margin["top"]),
            ('BOTTOMPADDING', (0, 1), (-1, -1), margin["bottom"])
        ]))
        story.append(t)
        story.append(Spacer(1, 12))
        
    doc.build(story)
