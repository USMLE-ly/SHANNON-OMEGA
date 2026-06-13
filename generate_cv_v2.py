#!/usr/bin/env python3
"""
Professional CV Generator v2 - Abraham Mohammed Albosify
Closer to the reference design with Google hyperlinks on the name itself,
keywords highlighted throughout, ATS-optimized.
"""

import os
from fpdf import FPDF, XPos, YPos

FONT_DIR = '/usr/share/fonts/truetype/liberation/'

class ProCV(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font('Sans', '', os.path.join(FONT_DIR, 'LiberationSans-Regular.ttf'))
        self.add_font('Sans', 'B', os.path.join(FONT_DIR, 'LiberationSans-Bold.ttf'))
        self.add_font('Sans', 'I', os.path.join(FONT_DIR, 'LiberationSans-Italic.ttf'))
        self.add_font('Sans', 'BI', os.path.join(FONT_DIR, 'LiberationSans-BoldItalic.ttf'))
        
        self.green = (22, 85, 54)
        self.light_green = (235, 242, 237)
        self.dark = (43, 43, 43)
        self.gray = (120, 120, 120)
        self.white = (255, 255, 255)
        self.link_blue = (0, 80, 180)

    def header(self):
        """Professional header matching reference design."""
        # Dark green band
        self.set_fill_color(*self.green)
        self.rect(0, 0, 210, 35, 'F')
        self.set_y(6)
        self.set_font('Sans', 'B', 22)
        self.set_text_color(*self.white)
        self.cell(0, 9, 'ABRAHAM MOHAMMED ALBOSIFY', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_font('Sans', '', 9)
        self.set_text_color(200, 220, 210)
        self.cell(0, 6, 'Medical Doctor  |  UX Designer  |  Educator  |  Cross-Cultural Facilitator', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        # Light green contact band
        self.set_y(35)
        self.set_fill_color(*self.light_green)
        self.rect(0, 35, 210, 7, 'F')
        self.set_font('Sans', 'I', 7.5)
        self.set_text_color(*self.dark)
        self.set_y(36)
        self.cell(0, 5.5, 'Benghazi, Libya  |  arabic (Native)  |  english (Advanced)  |  german (Intermediate)', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_y(44)

    def section(self, title):
        self.ln(3)
        self.set_fill_color(*self.green)
        self.rect(15, self.get_y(), 180, 5.5, 'F')
        self.set_font('Sans', 'B', 9.5)
        self.set_text_color(*self.white)
        self.cell(0, 5.5, f'  {title}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*self.dark)
        self.ln(1.5)

    def entry(self, title, sub):
        self.set_x(18)
        self.set_font('Sans', 'B', 9)
        self.set_text_color(*self.dark)
        self.cell(0, 5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if sub:
            self.set_x(18)
            self.set_font('Sans', 'I', 7.5)
            self.set_text_color(*self.gray)
            self.cell(0, 4, sub, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(*self.dark)

    def body(self, text):
        self.set_x(18)
        self.set_font('Sans', '', 8.2)
        self.set_text_color(*self.dark)
        self.multi_cell(174, 4.2, text)
        self.ln(0.5)

    def link_line(self, text, url, indent=18):
        self.set_x(indent)
        self.set_font('Sans', 'I', 7)
        self.set_text_color(*self.link_blue)
        self.cell(0, 4, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, link=url)

    def bullet(self, text, indent=22):
        self.set_x(indent)
        self.set_font('Sans', '', 8.2)
        self.set_text_color(*self.dark)
        self.multi_cell(210 - indent - 15, 4.2, text)
        self.ln(0.3)

    def footer_links(self):
        self.ln(4)
        self.set_draw_color(200, 215, 205)
        self.set_line_width(0.3)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)
        self.set_font('Sans', 'I', 6.5)
        self.set_text_color(*self.gray)
        self.cell(0, 3.5, 'Google UX Design Professional Certificate:', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_text_color(*self.link_blue)
        self.cell(0, 3.5, 'https://coursera.org/verify/professional-cert/6OMZYLOHUHK2', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C', link='https://coursera.org/verify/professional-cert/6OMZYLOHUHK2')
        self.set_text_color(*self.gray)
        self.cell(0, 3.5, 'European Solidarity Corps  |  Reactive Resume Compatible', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')


def generate(output_path):
    pdf = ProCV()
    pdf.add_page()
    pdf.header()

    # ===== PROFESSIONAL SUMMARY =====
    pdf.section('PROFESSIONAL SUMMARY')
    pdf.body(
        'Doctor with Google UX Design Professional Certificate, dedicated to community '
        'service and cross-cultural connection. Combines clinical expertise with UX '
        'research, graphic design, English teaching, and Soliya facilitation. '
        'Trilingual communicator (Arabic, English, German) with proven ability to '
        'bridge cultures and disciplines. Keywords: patient care, user research, '
        'wireframing, prototyping, Figma, usability testing, curriculum development, '
        'intercultural dialogue, conflict resolution, volunteer management.'
    )

    # ===== EDUCATION =====
    pdf.section('EDUCATION')
    
    pdf.entry('Bachelor of Medicine', 'University of Benghazi  |  2020 - 2027')
    pdf.body(
        'Comprehensive medical program with training in diagnosis, patient care, '
        'emergency medicine, and clinical rotations. Expected graduation June 2027. '
        'Built strong analytical thinking, teamwork, and interdisciplinary skills.'
    )
    
    # Google UX Certificate - with Google as clickable link
    pdf.set_x(18)
    pdf.set_font('Sans', 'B', 9)
    pdf.set_text_color(*pdf.dark)
    # Use a cell for the label and add link
    pdf.cell(0, 5, 'Google UX Design Professional Certificate', new_x=XPos.LMARGIN, new_y=YPos.NEXT,
             link='https://coursera.org/verify/professional-cert/6OMZYLOHUHK2')
    pdf.set_x(18)
    pdf.set_font('Sans', 'I', 7.5)
    pdf.set_text_color(*pdf.gray)
    pdf.cell(0, 4, 'via Coursera  |  Dec 2025 - Jan 2026', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*pdf.dark)
    pdf.body(
        '8-course program covering the full UX design process: user research, '
        'wireframing, high-fidelity prototyping in Figma, usability testing, '
        'and dynamic UI design for web. Skills in design thinking, interaction '
        'design, and information architecture.'
    )
    
    # Courses table - no dates, cleaner layout
    pdf.ln(1)
    pdf.set_x(18)
    pdf.set_fill_color(240, 245, 240)
    pdf.set_font('Sans', 'B', 7.5)
    pdf.cell(174, 5, '  Google UX Design Professional Certificate', 1, 1, '', True)
    
    courses = [
        ('Foundations of User Experience (UX) Design', 'GFU4WR0LWN9D'),
        ('Start the UX Design Process: Empathize, Define & Ideate', 'CPNZ4778S27Q'),
        ('Build Wireframes & Low-Fidelity Prototypes', 'BM81ZCT6VKQL'),
        ('Conduct UX Research & Test Early Concepts', 'R5LP730C04M1'),
        ('Create High-Fidelity Designs & Prototypes in Figma', 'BOP84AQRTNLD'),
        ('Build Dynamic User Interfaces (UI) for Websites', '9MHCWIIB2X7P'),
        ('Design for Social Good & Prepare for Jobs', '4SHEQFH9CRQH'),
        ('Accelerate Your Job Search with AI', 'NM24A5RORD77'),
    ]
    for name, cid in courses:
        url = f'https://coursera.org/verify/{cid}'
        pdf.set_font('Sans', '', 7)
        pdf.set_text_color(*pdf.link_blue)
        pdf.cell(174, 4.5, f'  {name}', 1, 1, '', link=url)
        pdf.set_text_color(*pdf.dark)

    # ===== WORK EXPERIENCE =====
    pdf.ln(3)
    pdf.section('WORK EXPERIENCE')
    
    pdf.entry('Medical Doctor', 'Hospital  |  Jan 2024 - Present')
    pdf.body(
        'Provide comprehensive medical care: diagnosis, treatment, and emergency '
        'management. Collaborate with interdisciplinary teams for patient-centered '
        'care. Develop resilience, clinical decision-making, and communication '
        'skills in high-pressure environments. Keywords: patient care, diagnosis, '
        'emergency medicine, clinical rounds, teamwork.'
    )
    
    pdf.entry('English Teacher', 'Elementary School  |  Sep 2023 - Present')
    pdf.body(
        'Teach English to young learners through interactive lesson plans and '
        'activities. Build communication confidence and literacy skills. Develop '
        'curriculum, assessment methods, and classroom management strategies.'
    )
    
    pdf.entry('Cross-Cultural Facilitator', 'Soliya  |  Jun 2023 - Present')
    pdf.body(
        'Facilitate intercultural dialogues connecting participants worldwide. '
        'Promote mutual respect, global citizenship, and understanding through '
        'structured conversation. Skills: conflict resolution, active listening, '
        'group facilitation, cross-cultural communication.'
    )
    
    pdf.entry('Graphic Designer', 'Freelance / Volunteer  |  Jan 2022 - Present')
    pdf.body(
        'Create visual content: branding, digital media, and communication '
        'materials for nonprofits. Support social causes through visual storytelling, '
        'design thinking, and creative problem-solving.'
    )

    # ===== VOLUNTEER EXPERIENCE =====
    pdf.section('VOLUNTEER EXPERIENCE')
    
    pdf.bullet('Hospital Volunteering: Support patients and medical staff. Demonstrate '
               'empathy, teamwork, and patient-centered care in clinical settings.')
    pdf.bullet('Campus Volunteering: Lead university community initiatives and student '
               'support programs. Organize events fostering community engagement.')
    pdf.bullet('Elderly Care: Provide companionship, daily assistance, and emotional '
               'support. Develop patience, compassion, and interpersonal skills.')
    pdf.bullet('Soliya Facilitation: Connect youth across cultures through facilitated '
               'dialogue. Advance cross-cultural communication and diplomacy skills.')

    # ===== SKILLS =====
    pdf.section('SKILLS')
    pdf.set_x(18)
    pdf.set_font('Sans', '', 8.5)
    pdf.set_text_color(*pdf.dark)
    pdf.multi_cell(174, 4.2,
        'MEDICAL: Diagnosis, patient care, emergency medicine, clinical research, '
        'interdisciplinary collaboration. '
        'UX/UI: User research, wireframing, prototyping (Figma), usability testing, '
        'interaction design, information architecture. '
        'TEACHING: Lesson planning, curriculum development, English instruction, '
        'classroom management. '
        'DESIGN: Branding, visual communication, digital media, typography. '
        'SOFT SKILLS: Cross-cultural communication, conflict resolution, public speaking, '
        'team leadership, adaptability, critical thinking.'
    )

    # ===== LANGUAGES =====
    pdf.section('LANGUAGES')
    pdf.set_x(18)
    pdf.set_font('Sans', '', 8.5)
    pdf.multi_cell(174, 4.5,
        'Arabic (Native)  |  English (Advanced)  |  German (Intermediate B1/B2)'
    )

    pdf.footer_links()
    pdf.output(output_path)
    print(f'Generated: {output_path}')
    print(f'Size: {os.path.getsize(output_path)} bytes')
    print(f'Pages: {pdf.pages_count}')

if __name__ == '__main__':
    out = '/root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free/Abraham_Albosify_Professional_CV.pdf'
    generate(out)
