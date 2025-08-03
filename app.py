import gradio as gr
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
import os

def generate_pdf(data, photo=None):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, data['name'])
    c.setFont("Helvetica", 10)
    c.drawString(100, 735, data['contact'])

    y = 700
    if photo is not None and os.path.exists(photo.name):
        try:
            img = ImageReader(photo.name)
            c.drawImage(img, 450, y - 60, width=80, height=80, mask='auto')
        except:
            pass
        y -= 90

    def section(title):
        nonlocal y
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y, title)
        y -= 15
        c.setFont("Helvetica", 10)

    def lines(text_list):
        nonlocal y
        for line in text_list:
            c.drawString(120, y, f"- {line}")
            y -= 12
        y -= 5

    section("Summary")
    lines(data["summary"].split("\n"))

    section("Education")
    lines(data["education"])

    section("Experience")
    lines(data["experience"])

    section("Skills")
    c.drawString(120, y, ", ".join(data["skills"]))
    y -= 20

    if data.get("projects"):
        section("Projects")
        lines(data["projects"])

    c.save()
    buffer.seek(0)
    return buffer

def create_resume(name, contact, summary, education, experience, skills, projects, photo):
    data = {
        "name": name,
        "contact": contact,
        "summary": summary,
        "education": education.strip().split('\n'),
        "experience": experience.strip().split('\n'),
        "skills": skills.strip().split(','),
        "projects": projects.strip().split('\n') if projects else [],
    }
    pdf = generate_pdf(data, photo)
    with open("resume_output.pdf", "wb") as f:
        f.write(pdf.getvalue())
    return "resume_output.pdf"

with gr.Blocks(title="Resume Builder") as demo:
    gr.Markdown("## Professional Resume Builder\nFill in your details to generate a PDF resume.")

    with gr.Row():
        with gr.Column():
            name = gr.Textbox(label="Full Name")
            contact = gr.Textbox(label="Contact (Email / Phone / LinkedIn)")
            summary = gr.Textbox(label="Summary", lines=3)
            education = gr.Textbox(label="Education (one per line)", lines=4)
            experience = gr.Textbox(label="Experience (one per line)", lines=4)
            skills = gr.Textbox(label="Skills (comma-separated)")
            projects = gr.Textbox(label="Projects (optional, one per line)", lines=3)
            photo = gr.File(label="Upload Profile Photo (optional)", file_types=[".jpg", ".png", ".jpeg"])
            submit = gr.Button("Generate Resume")
        
        with gr.Column():
            output = gr.File(label="Download Resume")

    submit.click(fn=create_resume, 
                 inputs=[name, contact, summary, education, experience, skills, projects, photo],
                 outputs=output)

demo.launch()
