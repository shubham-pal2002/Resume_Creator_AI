import gradio as gr
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
import textwrap
import re

def draw_wrapped_text(c, text, x, y, max_chars=90, line_height=12, font="Helvetica", font_size=10, bold=False):
    lines = textwrap.wrap(text, width=max_chars)
    c.setFont("Helvetica-Bold" if bold else font, font_size)
    for line in lines:
        c.drawString(x, y, line)
        y -= line_height
    return y

def generate_pdf(data, photo=None):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    top_margin = height - 50
    name_y = top_margin

    # --- Draw Name ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, name_y, data['name'])

    # --- Contact Info Cleanup ---
    raw_contact = data['contact']
    contact_info = re.sub(r'\s{2,}', '\n', raw_contact)  # 2+ spaces = new line
    contact_lines = [line.strip() for line in contact_info.split('\n') if line.strip()]

    # --- Handle Profile Photo (top right) ---
    photo_height = 0
    photo_top = name_y - 10
    if photo and os.path.exists(photo.name):
        try:
            img = ImageReader(photo.name)
            img_width, img_height = 90, 110
            c.drawImage(img, width - 130, photo_top - img_height + 10, width=img_width, height=img_height, mask='auto')
            photo_height = img_height
        except Exception as e:
            print("Image error:", e)

    # --- Draw Contact Info just below Name ---
    contact_y = name_y - 20
    for line in contact_lines:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, contact_y, line)
        contact_y -= 12
    contact_bottom = contact_y

    # --- Set y after image and contact info ---
    min_y_after_header = min(contact_bottom, photo_top - photo_height - 10)
    y = min_y_after_header - 20  # Start sections from here

    def add_section(title, content, bullet=False):
        nonlocal y
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, title)
        y -= 15
        c.setFont("Helvetica", 10)

        if isinstance(content, str):
            content_lines = content.split('\n')
        else:
            content_lines = content

        for line in content_lines:
            line = line.strip()
            if line:
                if bullet:
                    y = draw_wrapped_text(c, f"- {line}", 60, y, max_chars=100, line_height=12)
                else:
                    y = draw_wrapped_text(c, line, 60, y, max_chars=100, line_height=12)
        y -= 10

    # Sections
    add_section("Summary", data['summary'], bullet=False)
    add_section("Education", data['education'], bullet=True)
    add_section("Experience", data['experience'], bullet=True)
    add_section("Skills", data['skills'], bullet=True)
    if data.get("projects"):
        add_section("Projects", data['projects'], bullet=True)

    c.save()
    buffer.seek(0)
    return buffer

def create_resume(name, contact, summary, education, experience, skills, projects, photo):
    cleaned_skills = [s.strip() for s in skills.replace('\n', ',').split(',') if s.strip()]
    data = {
        "name": name,
        "contact": contact,
        "summary": summary,
        "education": education.strip().split('\n'),
        "experience": experience.strip().split('\n'),
        "skills": cleaned_skills,
        "projects": projects.strip().split('\n') if projects else [],
    }
    pdf = generate_pdf(data, photo)
    output_path = "resume_output.pdf"
    with open(output_path, "wb") as f:
        f.write(pdf.getvalue())
    return output_path

with gr.Blocks(title="Resume Builder") as demo:
    gr.Markdown("## Professional Resume Builder\nEnter your details to generate a clean PDF resume.")

    with gr.Row():
        with gr.Column():
            name = gr.Textbox(label="Full Name")
            contact = gr.Textbox(label="Contact Info (type each field with 2+ spaces between)", lines=3, placeholder="Email:...   Mob:...   LinkedIn:...   GitHub:...")
            summary = gr.Textbox(label="Summary", lines=4)
            education = gr.Textbox(label="Education (one per line)", lines=4)
            experience = gr.Textbox(label="Experience (one per line)", lines=4)
            skills = gr.Textbox(label="Skills (comma or newline separated)", placeholder="Python, NLP, Generative AI", lines=2)
            projects = gr.Textbox(label="Projects (optional, one per line)", lines=3)
            photo = gr.File(label="Upload Profile Photo (optional)", file_types=[".jpg", ".png", ".jpeg"])
            submit = gr.Button("Generate Resume")

        with gr.Column():
            output = gr.File(label="Download Your Resume")

    submit.click(fn=create_resume, 
                 inputs=[name, contact, summary, education, experience, skills, projects, photo],
                 outputs=output)

demo.launch()
