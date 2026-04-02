import os
from .profile_mockup import MY_PROFILE

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cv_template.typ')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'generated_cvs')

def format_experience(exp_list):
    res = ""
    for e in exp_list:
        res += f"=== {e['role']} ({e['company']})\n_{e['years']}_\n{e['description']}\n\n"
    return res

def format_education(edu_list):
    res = ""
    for e in edu_list:
        res += f"=== {e['degree']} ({e['institution']})\n_{e['years']}_\n\n"
    return res

def generate_cv_for_offer(offer):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
        
    # Replace profile placeholders
    template = template.replace('{{FIRST_NAME}}', MY_PROFILE['first_name'])
    template = template.replace('{{LAST_NAME}}', MY_PROFILE['last_name'])
    template = template.replace('{{TITLE}}', MY_PROFILE['title'])
    template = template.replace('{{EMAIL}}', MY_PROFILE['email'])
    template = template.replace('{{PHONE}}', MY_PROFILE['phone'])
    template = template.replace('{{ADDRESS}}', MY_PROFILE['address'])
    template = template.replace('{{SUMMARY}}', MY_PROFILE['summary'])
    
    # Format lists
    skills_str = ", ".join(MY_PROFILE['skills'])
    template = template.replace('{{SKILLS}}', skills_str)
    template = template.replace('{{EXPERIENCE}}', format_experience(MY_PROFILE['experience']))
    template = template.replace('{{EDUCATION}}', format_education(MY_PROFILE['education']))
    
    # Offer placeholders
    offer_title = offer.get('title', 'Developer')
    company = offer.get('company')
    template = template.replace('{{OFFER_TITLE}}', offer_title)
    template = template.replace('{{COMPANY}}', company)
    
    # Save formatted typ file
    filename = f"CV_{MY_PROFILE['first_name']}_{MY_PROFILE['last_name']}_{offer_title.replace(' ', '_')}".replace('/', '_')

    typ_path = os.path.join(OUTPUT_DIR,"typ" )
    pdf_path = os.path.join(OUTPUT_DIR,"pdf" )

    if not os.path.exists(typ_path) : os.makedirs(typ_path)
    if not os.path.exists(pdf_path) : os.makedirs(pdf_path)

    typ_path = os.path.join(OUTPUT_DIR,"typ", f"{filename}.typ")
    pdf_path = os.path.join(OUTPUT_DIR,"pdf", f"{filename}.pdf")

    with open(typ_path, 'w' , encoding='utf-8') as f:
        f.write(template)
        
    # Try compiling using typst
    try:
        import typst
        typst.compile(typ_path, output=pdf_path)
        return pdf_path
    except Exception as e:
        print(f"Typst compilation error: {str(e)}")
        return typ_path
