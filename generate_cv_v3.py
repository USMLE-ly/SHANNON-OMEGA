#!/usr/bin/env python3
"""
Professional CV Generator v3 - Abraham Mohammed Albosify
Dark navy header band, clean modern template, ATS-optimized.
No green boxes, no dates on courses, Google as hyperlink.
Keywords naturally embedded in body text.
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

        self.navy = (27, 42, 74)
        self.navy_light = (50, 70, 110)
        self.dark = (43, 43, 43)
        self.gray = (120, 120, 120)
        self.light_gray = (230, 232, 236)
        self.white = (255, 255, 255)
        self.link_blue = (30, 90, 180)

    def header(self):
        """Dark navy header band."""
        self.set_fill_color(*self.navy)
        self.rect(0, 0, 210, 38, 'F')
        self.set_fill_color(*self.navy_light)
        self.rect(0, 38, 210, 0.8, 'F')

        self.set_y(7)
        self.set_font('Sans', 'B', 22)
        self.set_text_color(*self.white)
        self.cell(0, 9, 'ABRAHAM MOHAMMED ALBOSIFY', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

        self.set_font('Sans', '', 9)
        self.set_text_color(180, 195, 220)
        self.cell(0, 6, 'Medical Doctor  |  UX Designer  |  Educator  |  Cross-Cultural Facilitator',
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

        self.set_font('Sans', 'I', 7.5)
        self.set_text_color(160, 175, 200)
        self.cell(0, 5.5, 'Benghazi, Libya  |  Arabic (Native)  |  English (Advanced)  |  German (Intermediate)',
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_y(42)

    def section(self, title):
        """Minimal section header with underline — no box."""
        self.ln(2.5)
        y = self.get_y()
        self.set_font('Sans', 'B', 9.5)
        self.set_text_color(*self.navy)
        self.cell(0, 5.5, title.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*self.navy)
        self.set_line_width(0.4)
        self.line(15, self.get_y() + 0.5, 195, self.get_y() + 0.5)
        self.ln(2.5)
        self.set_text_color(*self.dark)

    def entry(self, title, sub=''):
        """Entry title with gray subtitle below."""
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
        """Body paragraph with keywords naturally embedded."""
        self.set_x(18)
        self.set_font('Sans', '', 8.2)
        self.set_text_color(*self.dark)
        self.multi_cell(174, 4.2, text)
        self.ln(0.3)

    def hyperlink(self, text, url, indent=18):
        """Clickable hyperlink line."""
        self.set_x(indent)
        self.set_font('Sans', 'I', 7)
        self.set_text_color(*self.link_blue)
        self.cell(0, 4, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, link=url)

    def bullet(self, text, indent=22):
        """Bullet point with keywords."""
        self.set_x(indent)
        self.set_font('Sans', '', 8.2)
        self.set_text_color(*self.dark)
        self.multi_cell(210 - indent - 15, 4.2, text)
        self.ln(0.2)


def generate(output_path):
    pdf = ProCV()
    pdf.add_page()
    pdf.header()

    # ===== PROFESSIONAL SUMMARY =====
    pdf.section('Professional Summary')
    pdf.body(
        'Dedicated medical doctor with a Google UX Design Professional Certificate, '
        'combining clinical expertise with user research, interaction design, and '
        'cross-cultural facilitation. Skilled in patient care, diagnosis, emergency '
        'medicine, and interdisciplinary collaboration. Trilingual communicator '
        '(Arabic, English, German) experienced in English teaching, graphic design, '
        'and community outreach. Driven by empathy and a commitment to service, '
        'with proven ability to bridge cultures and disciplines through Soliya '
        'facilitation and volunteer work with elderly and underserved communities.'
    )

    # ===== EDUCATION =====
    pdf.section('Education')

    # University of Benghazi — Medicine
    pdf.entry('Bachelor of Medicine', 'University of Benghazi  |  Expected Graduation: June 2027')
    pdf.body(
        'Six-year medical program with comprehensive training in diagnosis, patient '
        'care, clinical decision-making, and emergency medicine. Developed strong '
        'analytical thinking, resilience under pressure, and interdisciplinary '
        'teamwork through clinical rotations and hospital practice.'
    )

    # Google UX Design Professional Certificate
    pdf.set_x(18)
    pdf.set_font('Sans', 'B', 9)
    pdf.set_text_color(*pdf.dark)
    pdf.cell(0, 5, 'Google UX Design Professional Certificate', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(18)
    pdf.set_font('Sans', 'I', 7.5)
    pdf.set_text_color(*pdf.gray)
    pdf.write(4, 'Offered by ')
    pdf.set_text_color(*pdf.link_blue)
    pdf.write(4, 'Google', 'https://coursera.org/verify/professional-cert/6OMZYLOHUHK2')
    pdf.set_text_color(*pdf.gray)
    pdf.write(4, ' via Coursera')
    pdf.ln(5)

    # Course list — each as clickable hyperlink, no dates
    pdf.set_x(18)
    pdf.set_font('Sans', '', 7.5)
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
        pdf.set_text_color(*pdf.link_blue)
        pdf.cell(0, 3.8, f'  \u2022  {name}', new_x=XPos.LMARGIN, new_y=YPos.NEXT, link=url)
    pdf.set_text_color(*pdf.dark)
    pdf.ln(1.5)

    # ===== WORK EXPERIENCE =====
    pdf.section('Work Experience')

    pdf.entry('Medical Doctor', 'Hospital  |  Jan 2024 - Present')
    pdf.body(
        'Provide comprehensive medical care including diagnosis, treatment planning, '
        'emergency management, and patient monitoring. Collaborate with interdisciplinary '
        'teams to deliver patient-centered care in high-pressure clinical environments. '
        'Developed expertise in clinical decision-making, patient communication, '
        'and teamwork through direct patient care and hospital rounds.'
    )

    pdf.entry('English Teacher', 'Elementary School  |  Sep 2023 - Present')
    pdf.body(
        'Teach English to young learners through interactive lesson plans, storytelling, '
        'and engaging activities. Build foundational literacy and communication '
        'confidence. Develop curriculum, assessment methods, and classroom management '
        'strategies tailored to diverse learning needs.'
    )

    pdf.entry('Cross-Cultural Facilitator', 'Soliya  |  Jun 2023 - Present')
    pdf.body(
        'Facilitate structured intercultural dialogues connecting participants across '
        'the globe. Promote mutual respect, global citizenship, and cross-cultural '
        'understanding. Developed advanced skills in conflict resolution, active '
        'listening, group facilitation, and intercultural communication.'
    )

    pdf.entry('Graphic Designer', 'Freelance / Volunteer  |  Jan 2022 - Present')
    pdf.body(
        'Create visual content including branding, digital media, and communication '
        'materials for nonprofits and community organizations. Support social causes '
        'through visual storytelling, design thinking, typography, and creative '
        'problem-solving. Proficient in Figma, Adobe Creative Suite, and design tools.'
    )

    # ===== VOLUNTEER EXPERIENCE =====
    pdf.section('Volunteer Experience')

    pdf.bullet('Hospital Volunteering: Support patients with direct assistance and '
               'emotional care. Demonstrate empathy, patience, and teamwork in '
               'clinical settings alongside medical staff.')
    pdf.bullet('Campus Volunteering: Lead and participate in university community '
               'initiatives, student support programs, and outreach events. Foster '
               'community engagement and social responsibility.')
    pdf.bullet('Elderly Care: Provide companionship, daily assistance, and emotional '
               'support to elderly individuals. Developed compassion, active listening, '
               'and interpersonal sensitivity through direct caregiving.')
    pdf.bullet('Soliya Facilitation: Connect youth across cultures via facilitated '
               'dialogue programs. Build cross-cultural communication, diplomacy, '
               'and global awareness skills.')

    # ===== SKILLS =====
    pdf.section('Skills')
    pdf.set_x(18)
    pdf.set_font('Sans', '', 8.2)
    pdf.set_text_color(*pdf.dark)
    pdf.multi_cell(174, 4.2,
        'Medical & Clinical: Diagnosis, patient care, emergency medicine, clinical '
        'research, interdisciplinary collaboration, treatment planning. '
        'UX Design & Research: User research, wireframing, prototyping (Figma), '
        'usability testing, interaction design, information architecture. '
        'Teaching & Education: Lesson planning, curriculum development, English '
        'instruction, classroom management, child education. '
        'Design & Media: Branding, visual communication, digital media, typography, '
        'Adobe Creative Suite, design thinking. '
        'Soft Skills: Cross-cultural communication, conflict resolution, public '
        'speaking, team leadership, adaptability, critical thinking, empathy.'
    )

    # ===== LANGUAGES =====
    pdf.section('Languages')
    pdf.set_x(18)
    pdf.set_font('Sans', '', 8.5)
    pdf.set_text_color(*pdf.dark)
    pdf.multi_cell(174, 4.5,
        'Arabic (Native)  |  English (Advanced)  |  German (Intermediate B1/B2)'
    )

    pdf.output(output_path)
    print(f'Generated: {output_path}')
    print(f'Size: {os.path.getsize(output_path)} bytes')
    print(f'Pages: {pdf.pages_count}')

if __name__ == '__main__':
    out = '/root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free/Abraham_Albosify_CV.pdf'
    generate(out)
