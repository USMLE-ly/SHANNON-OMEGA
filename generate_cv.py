#!/usr/bin/env python3
"""
Professional CV Generator - Abraham Mohammed Albosify
Inspired by the reference design with embedded keywords, ATS-friendly,
Google certificate hyperlinks, and a clean professional layout.
"""

import os
from fpdf import FPDF, XPos, YPos
import textwrap

FONT_DIR = '/usr/share/fonts/truetype/liberation/'

class ProfessionalCV(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.set_auto_page_break(auto=True, margin=15)
        # Register fonts
        self.add_font('Sans', '', os.path.join(FONT_DIR, 'LiberationSans-Regular.ttf'))
        self.add_font('Sans', 'B', os.path.join(FONT_DIR, 'LiberationSans-Bold.ttf'))
        self.add_font('Sans', 'I', os.path.join(FONT_DIR, 'LiberationSans-Italic.ttf'))
        self.add_font('Sans', 'BI', os.path.join(FONT_DIR, 'LiberationSans-BoldItalic.ttf'))
        
        # Color palette
        self.green = (22, 85, 54)       # Dark green for headers
        self.light_green = (235, 242, 237)  # Light green accent
        self.dark = (43, 43, 43)          # Dark text
        self.gray = (120, 120, 120)       # Gray for secondary text
        self.white = (255, 255, 255)
        self.link_blue = (0, 80, 180)     # Hyperlink color
        self.rule_color = (200, 215, 205) # Rule lines

    def header_block(self):
        """Dark green header with name and title."""
        self.set_fill_color(*self.green)
        self.rect(0, 0, 210, 36, 'F')
        # Name
        self.set_y(6)
        self.set_font('Sans', 'B', 21)
        self.set_text_color(*self.white)
        self.cell(0, 9, 'Abraham Mohammed Albosify', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        # Title
        self.set_font('Sans', '', 9)
        self.cell(0, 6, 'Medical Doctor  |  UX Designer  |  Educator  |  Cross-Cultural Facilitator', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        # Contact bar
        self.set_y(36)
        self.set_fill_color(*self.light_green)
        self.rect(0, 36, 210, 6.5, 'F')
        self.set_font('Sans', 'I', 7.5)
        self.set_text_color(*self.dark)
        self.set_y(37)
        self.cell(0, 5, 'Benghazi, Libya  |  Arabic (Native)  |  English (Advanced)  |  German (Intermediate)', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_y(44)

    def section_title(self, title):
        """Section header with green background."""
        self.ln(3)
        self.set_fill_color(*self.green)
        self.rect(15, self.get_y(), 180, 5.5, 'F')
        self.set_font('Sans', 'B', 9.5)
        self.set_text_color(*self.white)
        self.cell(0, 5.5, f'  {title}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*self.dark)
        self.ln(2)

    def entry_title(self, title, subtitle=''):
        """Bold title with optional gray subtitle on same line."""
        self.set_x(18)
        self.set_font('Sans', 'B', 9)
        self.set_text_color(*self.dark)
        self.cell(0, 5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if subtitle:
            self.set_x(18)
            self.set_font('Sans', 'I', 7.5)
            self.set_text_color(*self.gray)
            self.cell(0, 4, subtitle, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(*self.dark)

    def body_text(self, text):
        """ATS-friendly body text with embedded keywords."""
        self.set_x(18)
        self.set_font('Sans', '', 8.2)
        self.set_text_color(*self.dark)
        self.multi_cell(174, 4.2, text)
        self.ln(0.5)

    def add_link_line(self, label, url):
        """Hyperlink line."""
        self.set_x(18)
        self.set_font('Sans', 'I', 7)
        self.set_text_color(*self.link_blue)
        self.cell(0, 4, label, new_x=XPos.LMARGIN, new_y=YPos.NEXT, link=url)

    def bullet_point(self, text, indent=22):
        """Single bullet point with embedded keywords."""
        self.set_x(indent)
        self.set_font('Sans', '', 8.2)
        self.set_text_color(*self.dark)
        # Calculate width
        w = 210 - indent - 15
        self.multi_cell(w, 4.2, text)
        self.ln(0.3)

    def footer_note(self):
        """Footer with certification links."""
        self.ln(4)
        self.set_draw_color(*self.rule_color)
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

def generate_cv(output_path):
    pdf = ProfessionalCV()
    pdf.add_page()
    
    # ===== HEADER =====
    pdf.header_block()
    
    # ===== PROFESSIONAL SUMMARY =====
    pdf.section_title('PROFESSIONAL SUMMARY')
    pdf.body_text(
        'Dedicated medical doctor with a Google UX Design Professional Certificate, '
        'passionate about helping people and giving back to the community. Combines '
        'clinical expertise with UX research, graphic design, English teaching, and '
        'cross-cultural facilitation through Soliya. Trilingual communicator '
        '(Arabic, English, German) with proven ability to connect across cultures '
        'and disciplines. Strong skills in diagnosis, patient care, user research, '
        'wireframing, prototyping, and intercultural dialogue.'
    )
    
    # ===== EDUCATION =====
    pdf.section_title('EDUCATION')
    
    # Medicine
    pdf.entry_title('Bachelor of Medicine', 'University of Benghazi  |  Oct 2020 - Jun 2027')
    pdf.body_text(
        'Six-year medical program with comprehensive clinical training in '
        'diagnosis, patient care, and emergency medicine. Expected graduation: '
        'June 2, 2027. Developed strong analytical thinking, problem-solving, '
        'and interdisciplinary collaboration skills.'
    )
    
    # Google UX Certificate
    pdf.entry_title('Google UX Design Professional Certificate', 'Google via Coursera  |  Dec 2025 - Jan 2026')
    pdf.body_text(
        'Comprehensive 8-course program authorized by Google, covering the full '
        'UX design process: user research, wireframing, high-fidelity prototyping '
        'in Figma, usability testing, and dynamic UI design for web and mobile.'
    )
    pdf.add_link_line('  >> Verify Full Certificate: https://coursera.org/verify/professional-cert/6OMZYLOHUHK2',
                      'https://coursera.org/verify/professional-cert/6OMZYLOHUHK2')
    
    # ===== GOOGLE COURSERA COURSES TABLE =====
    pdf.ln(2)
    pdf.set_x(18)
    pdf.set_font('Sans', 'B', 7)
    pdf.set_fill_color(240, 245, 240)
    pdf.cell(100, 4.5, '  Course', 1, 0, '', True)
    pdf.cell(18, 4.5, 'Date', 1, 0, 'C', True)
    pdf.cell(48, 4.5, '  Verify', 1, 1, '', True)
    
    courses = [
        ('Foundations of User Experience (UX) Design', 'Jan 10', 'GFU4WR0LWN9D'),
        ('Start the UX Design Process: Empathize, Define & Ideate', 'Jan 11', 'CPNZ4778S27Q'),
        ('Build Wireframes & Low-Fidelity Prototypes', 'Jan 10', 'BM81ZCT6VKQL'),
        ('Conduct UX Research & Test Early Concepts', 'Jan 11', 'R5LP730C04M1'),
        ('Create High-Fidelity Designs & Prototypes in Figma', 'Jan 11', 'BOP84AQRTNLD'),
        ('Build Dynamic User Interfaces (UI) for Websites', 'Jan 12', '9MHCWIIB2X7P'),
        ('Design for Social Good & Prepare for Jobs', 'Jan 12', '4SHEQFH9CRQH'),
        ('Accelerate Your Job Search with AI', 'Jan 12', 'NM24A5RORD77'),
    ]
    for name, date, cid in courses:
        url = f'https://coursera.org/verify/{cid}'
        pdf.set_font('Sans', '', 6.8)
        pdf.cell(100, 4, f'  {name}', 1)
        pdf.cell(18, 4, date, 1, 0, 'C')
        pdf.set_text_color(*pdf.link_blue)
        pdf.cell(48, 4, '  Verify', 1, 1, '', link=url)
        pdf.set_text_color(*pdf.dark)
    
    # ===== WORK EXPERIENCE =====
    pdf.ln(3)
    pdf.section_title('WORK EXPERIENCE')
    
    # Medical Doctor
    pdf.entry_title('Medical Doctor', 'Hospital  |  Jan 2024 - Present')
    pdf.body_text(
        'Providing comprehensive medical care with empathy and precision. '
        'Diagnosing and treating patients, making critical clinical decisions '
        'in emergency settings, and collaborating across interdisciplinary teams. '
        'Developed resilience, calm under pressure, and strong patient communication '
        'through direct patient care and clinical rounds.'
    )
    
    # English Teacher
    pdf.entry_title('English Teacher', 'Elementary School  |  Sep 2023 - Present')
    pdf.body_text(
        'Teaching English language skills to young children through engaging '
        'lesson plans and interactive activities. Building confidence in '
        'communication and fostering a supportive learning environment for '
        'language acquisition. Developed curriculum and assessment methods.'
    )
    
    # Soliya Facilitator
    pdf.entry_title('Cross-Cultural Facilitator', 'Soliya  |  Jun 2023 - Present')
    pdf.body_text(
        'Facilitating intercultural dialogues between participants from diverse '
        'backgrounds worldwide. Promoting mutual respect, global citizenship, '
        'and cross-cultural understanding through structured conversation and '
        'active listening. Skilled in conflict resolution and group facilitation.'
    )
    
    # Graphic Designer
    pdf.entry_title('Graphic Designer', 'Freelance / Volunteer  |  Jan 2022 - Present')
    pdf.body_text(
        'Creating visual content including branding, digital media, and communication '
        'materials for nonprofit organizations and community projects. Supporting '
        'social causes through effective visual storytelling, design thinking, '
        'and creative problem-solving.'
    )
    
    # ===== VOLUNTEER EXPERIENCE =====
    pdf.section_title('VOLUNTEER EXPERIENCE')
    
    vols = [
        ('Hospital Volunteering',
         'Supporting patients and medical staff with direct assistance in clinical '
         'settings. Demonstrating empathy, teamwork, and patient-centered care.'),
        ('Campus Volunteering',
         'Active participation in university community initiatives and student support '
         'programs. Organized events and fostered community engagement.'),
        ('Elderly Care',
         'Providing companionship, daily assistance, and emotional support to elderly '
         'community members. Developed patience, compassion, and interpersonal skills.'),
        ('Soliya Facilitation',
         'Connecting young people from different cultures through structured facilitated '
         'dialogue programs. Advanced skills in cross-cultural communication and diplomacy.'),
    ]
    for title, desc in vols:
        pdf.set_x(18)
        pdf.set_font('Sans', 'B', 8.5)
        pdf.cell(0, 4.5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.bullet_point(desc)
        pdf.ln(0.5)
    
    # ===== SKILLS =====
    pdf.section_title('SKILLS')
    pdf.set_x(18)
    pdf.set_font('Sans', '', 8.5)
    pdf.set_text_color(*pdf.dark)
    pdf.multi_cell(174, 4.2,
        'Medical Knowledge & Clinical Care (Expert): Diagnosis, patient care, emergency '
        'medicine, and interdisciplinary collaboration. '
        'Teaching & Education (Advanced): Lesson planning, English language instruction, '
        'and curriculum development for children. '
        'UX Design & Research (Advanced): User research, wireframing, prototyping in Figma, '
        'and usability testing. '
        'Graphic Design (Advanced): Visual communication, branding, digital media, '
        'and nonprofit outreach. '
        'Cross-Cultural Communication (Advanced): Intercultural dialogue facilitation, '
        'conflict resolution, and global citizenship education. '
        'Community Engagement (Expert): Volunteer management, community outreach, '
        'and social impact initiatives.'
    )
    
    # ===== LANGUAGES =====
    pdf.section_title('LANGUAGES')
    pdf.set_x(18)
    pdf.set_font('Sans', '', 8.5)
    pdf.multi_cell(174, 4.5,
        'Arabic (Native)  |  English (Advanced - TOEFL/IELTS equivalent)  |  '
        'German (Intermediate - B1/B2)'
    )
    
    # ===== FOOTER =====
    pdf.footer_note()
    
    # Output
    pdf.output(output_path)
    print(f'Generated: {output_path}')
    print(f'Size: {os.path.getsize(output_path)} bytes')
    print(f'Pages: {pdf.pages_count}')

if __name__ == '__main__':
    out = '/root/Documents/Codex/2026-06-08/make-the-deepseek-v4-flash-free/Abraham_Albosify_Professional_CV.pdf'
    generate_cv(out)
