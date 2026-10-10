#!/usr/bin/env python3
"""Build the public, ATS-friendly resume PDF."""

from pathlib import Path

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "hossein-moazami-resume.pdf"

NAVY = colors.HexColor("#091521")
STEEL = colors.HexColor("#244F73")
STEEL_DARK = colors.HexColor("#183A56")
BRASS = colors.HexColor("#8B5A20")
BRASS_LIGHT = colors.HexColor("#D6B275")
MUTED = colors.HexColor("#53606E")
LINE = colors.HexColor("#C7CCD1")
PAPER = colors.HexColor("#FFFFFF")


def footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 6, width, 6, fill=1, stroke=0)
    canvas.setFillColor(STEEL)
    canvas.rect(0, height - 6, 68 * mm, 6, fill=1, stroke=0)
    canvas.setFillColor(BRASS_LIGHT)
    canvas.rect(68 * mm, height - 6, 25 * mm, 6, fill=1, stroke=0)
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 13 * mm, width - 18 * mm, 13 * mm)
    canvas.setFont("Helvetica", 7.2)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 8.5 * mm, "hossein.cloud")
    page_label = f"Page {doc.page}"
    canvas.drawString(width - 18 * mm - stringWidth(page_label, "Helvetica", 7.2), 8.5 * mm, page_label)
    canvas.restoreState()


def paragraph(text, style):
    return Paragraph(text, style)


def section_title(text, styles):
    return [Spacer(1, 4), paragraph(text.upper(), styles["section"]), Spacer(1, 2)]


def role(company, title, place, dates, bullets, styles):
    items = [
        paragraph(f"<b>{company}</b> &nbsp;|&nbsp; {title}", styles["role"]),
        paragraph(f"{place} &nbsp;|&nbsp; {dates}", styles["role_meta"]),
    ]
    for bullet in bullets:
        items.append(paragraph(bullet, styles["bullet"]))
    items.append(Spacer(1, 3))
    return KeepTogether(items)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    sheet = getSampleStyleSheet()
    styles = {
        "name": ParagraphStyle(
            "Name",
            parent=sheet["Normal"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=27,
            textColor=NAVY,
            spaceAfter=1,
        ),
        "headline": ParagraphStyle(
            "Headline",
            parent=sheet["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=15,
            textColor=STEEL_DARK,
            spaceAfter=4,
        ),
        "contact": ParagraphStyle(
            "Contact",
            parent=sheet["Normal"],
            fontName="Helvetica",
            fontSize=8.7,
            leading=11.5,
            textColor=MUTED,
            linkUnderline=True,
            spaceAfter=0,
        ),
        "section": ParagraphStyle(
            "Section",
            parent=sheet["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.3,
            leading=11,
            textColor=BRASS,
            spaceBefore=0,
            spaceAfter=0,
            borderColor=LINE,
            borderWidth=0,
            borderPadding=0,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=sheet["Normal"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12.5,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=0,
            allowWidows=0,
            allowOrphans=0,
        ),
        "skill": ParagraphStyle(
            "Skill",
            parent=sheet["Normal"],
            fontName="Helvetica",
            fontSize=8.95,
            leading=11.6,
            textColor=NAVY,
            spaceAfter=1.2,
        ),
        "role": ParagraphStyle(
            "Role",
            parent=sheet["Normal"],
            fontName="Helvetica",
            fontSize=9.75,
            leading=12,
            textColor=NAVY,
            keepWithNext=True,
        ),
        "role_meta": ParagraphStyle(
            "RoleMeta",
            parent=sheet["Normal"],
            fontName="Helvetica",
            fontSize=8.25,
            leading=10.3,
            textColor=MUTED,
            spaceAfter=1,
            keepWithNext=True,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=sheet["Normal"],
            fontName="Helvetica",
            fontSize=8.85,
            leading=11.55,
            leftIndent=10,
            firstLineIndent=-7,
            textColor=NAVY,
            bulletIndent=0,
            spaceAfter=0.5,
            allowWidows=0,
            allowOrphans=0,
        ),
        "project": ParagraphStyle(
            "Project",
            parent=sheet["Normal"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=11.5,
            textColor=NAVY,
            spaceAfter=0,
        ),
        "compact": ParagraphStyle(
            "Compact",
            parent=sheet["Normal"],
            fontName="Helvetica",
            fontSize=8.35,
            leading=10.5,
            textColor=NAVY,
            spaceAfter=0,
        ),
    }

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=12 * mm,
        bottomMargin=17 * mm,
        title="Hossein Moazami - DevOps and Platform Engineer",
        author="Hossein Moazami",
        subject="Professional resume",
        keywords="DevOps, Platform Engineering, Kubernetes, Terraform, Ansible, CI/CD, Observability",
    )

    story = [
        paragraph("Hossein Moazami", styles["name"]),
        paragraph("DevOps &amp; Platform Engineer", styles["headline"]),
        paragraph(
            "Tehran, Iran &nbsp;|&nbsp; "
            '<link href="tel:+989371942700" color="#244F73">+98 937 194 2700</link> &nbsp;|&nbsp; '
            '<link href="mailto:hossein.moazami.goodarzi@gmail.com" color="#244F73">hossein.moazami.goodarzi@gmail.com</link>',
            styles["contact"],
        ),
        paragraph(
            '<link href="https://hossein.cloud" color="#244F73">hossein.cloud</link> &nbsp;|&nbsp; '
            '<link href="https://www.linkedin.com/in/hossein-moazami" color="#244F73">linkedin.com/in/hossein-moazami</link> &nbsp;|&nbsp; '
            '<link href="https://github.com/hosseinmoazami" color="#244F73">github.com/hosseinmoazami</link>',
            styles["contact"],
        ),
    ]

    story += section_title("Profile", styles)
    story.append(paragraph(
        "DevOps and platform engineer with 7+ years across production infrastructure and software engineering. Experience includes Kubernetes migration, private-cloud infrastructure, Ansible automation, CI/CD, centralized logging, monitoring, load testing, and application modernization. Brings a software-development perspective to delivery, documentation, mentoring, and production operations.",
        styles["body"],
    ))

    story += section_title("Core skills", styles)
    for label, values in [
        ("Platforms and automation", "Kubernetes clusters, Helm, AWS, Linux, private cloud, Terraform, Ansible"),
        ("Delivery and observability", "GitLab CI/CD, Jenkins, GitOps, Prometheus, Grafana, ELK, OpenTelemetry"),
        ("Data and traffic", "MinIO, PostgreSQL, Nginx, HAProxy"),
        ("Software engineering", "Go, Python, Bash, JavaScript, React.js, REST APIs, FastAPI, Laravel"),
    ]:
        story.append(paragraph(f"<b>{label}:</b> {values}", styles["skill"]))

    story += section_title("Experience", styles)
    story.append(role(
        "NafisLife",
        "DevOps Engineer",
        "Tehran Province, Iran",
        "Apr 2021 - Present",
        [
            "- Orchestrated a legacy-infrastructure migration to Kubernetes, reducing deployment downtime by 30%.",
            "- Automated configuration with Ansible, reducing manual errors by 40% and improving provisioning efficiency by 20%.",
            "- Built and maintained CI/CD, private-cloud infrastructure, and staging and production environments; reduced software release time by 30%.",
            "- Improved visibility with Prometheus, Grafana, and centralized ELK logging; combined load testing and tuning to improve peak response times by 25%.",
        ],
        styles,
    ))
    story.append(role(
        "NafisLife",
        "Software Engineering",
        "Tehran, Iran",
        "Oct 2020 - Apr 2022",
        [
            "- Architected reusable React component libraries and design systems across multiple projects.",
            "- Guided legacy JavaScript modernization through planning, implementation, code review, and mentoring.",
        ],
        styles,
    ))
    story += section_title("Earlier experience", styles)
    story.append(role(
        "ArvanCloud",
        "JavaScript Developer",
        "Tehran, Iran",
        "Feb 2021 - Apr 2021",
        [
            "- Built RESTful API integrations for CDN App, a platform for installing cloud applications on customer websites.",
            "- Created technical documentation and user guidance for cloud-application integration and customization.",
        ],
        styles,
    ))
    story.append(role(
        "Shavaz",
        "DevOps Engineer",
        "Tehran, Iran",
        "Apr 2019 - Apr 2021",
        [
            "- Supported a commerce platform with 600,000+ monthly active users; integrated GitLab CI/CD with Kubernetes, moving deployment cycles from weeks to hours and increasing team productivity by 30%.",
            "- Deployed Prometheus and Grafana monitoring, improving system reliability by 40%, and worked with developers on high-traffic performance issues.",
            "- Configured a four-node MinIO cluster for backups and media, reducing storage rental costs by 25%.",
        ],
        styles,
    ))
    story.append(role(
        "IAEO - Iran Agricultural Engineering Organization",
        "Back-end Developer",
        "Tehran, Iran",
        "Jul 2020 - Oct 2020",
        [
            "- Led a migration from legacy PHP 5 to Laravel.",
            "- Developed and maintained payment and financial features.",
        ],
        styles,
    ))

    story += section_title("Selected public project", styles)
    story.append(paragraph(
        '<b><link href="https://github.com/hosseinmoazami/infra-implementation-hobby" color="#244F73">End-to-end infrastructure lab</link>:</b> Built a four-VM infrastructure lab with a Kubernetes cluster comprising one control-plane node and two worker nodes, plus a dedicated builder, using Terraform/libvirt and Ansible. Added a private registry, GitLab Runner, kube-prometheus-stack, PostgreSQL HA, and a three-replica FastAPI deployment.',
        styles["project"],
    ))
    story.append(Spacer(1, 3))
    story.append(paragraph(
        '<b><link href="https://github.com/hosseinmoazami/monitoring-prometheus-exporter" color="#244F73">Prometheus exporter automation</link>:</b> Created reusable Ansible roles for node, Redis, and IPMI exporters to make monitoring deployment repeatable.',
        styles["project"],
    ))

    story += section_title("Credentials and education", styles)
    story.append(paragraph(
        "<b>Certifications:</b> Certified Linux Network Professional (LPIC-2); Linux Virtualization &amp; Containerization (LPIC-305); CompTIA Network+; Master of Bash Scripting; ReactJS",
        styles["compact"],
    ))
    story.append(paragraph(
        "<b>Education:</b> Bachelor's degree, Computer Software Engineering - Boroujerdi University, 2014 - 2017",
        styles["compact"],
    ))
    story.append(paragraph(
        "<b>Languages:</b> Persian (Native or Bilingual); English (Professional Working); German (Limited Working)",
        styles["compact"],
    ))
    story.append(paragraph(
        "<b>Publication:</b> The application of wireless body sensor network along with Gamification in personal health monitoring",
        styles["compact"],
    ))

    doc.build(story, onFirstPage=footer, onLaterPages=footer)

    reader = PdfReader(str(OUTPUT))
    if len(reader.pages) != 1:
        raise RuntimeError(f"Expected a one-page resume, generated {len(reader.pages)} pages")
    print(OUTPUT)


if __name__ == "__main__":
    build()
