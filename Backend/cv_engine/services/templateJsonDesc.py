from pydantic import BaseModel, EmailStr, Field


class PersonalInfo(BaseModel):
    telephone_label: str = Field(description="Formatted phone number for display, e.g., '+48 123 456 789'")
    telephone_link: str = Field(description="Technical tel: link for links, e.g., 'tel:+48123456789'")
    email: EmailStr = Field(description="Professional contact email address")
    github_label: str = Field(description="GitHub profile label, e.g., 'github.com/username'")
    github_link: str = Field(description="Full URL to the GitHub profile, e.g., 'https://github.com/johndoe'")
    linkedin_label: str = Field(description="LinkedIn profile label, e.g., 'linkedin.com/in/username'")
    linkedin_link: str = Field(
        description="Full URL to the LinkedIn profile, e.g., 'https://www.linkedin.com/in/johndoe'")


class PersonalAbout(BaseModel):
    description: str = Field(description="A concise and professional career summary (prose)")


class Personal(BaseModel):
    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
    subtitle: str = Field(description="Header below the name, e.g., 'Software Engineering Student'")
    info: PersonalInfo
    about: PersonalAbout


class SkillEntry(BaseModel):
    category: str = Field(description="Skill category name, e.g., 'Languages,'Programming','Technologies',")
    items: str = Field(
        description="Comma-separated list of specific skills, e.g., Languages->'English (C1),Polish(Native)', Programming -> 'Python, Java, C, C++, SQL', Technologies -> 'Django, Docker,Git, Linux, LaTeX' ")


class Skills(BaseModel):
    entries: list[SkillEntry]


class EducationEntry(BaseModel):
    school: str = Field(description="Full name of the institution")
    years: str = Field(description="Duration of study, e.g., '2024 – Present', '2025-2028'")
    degree: str = Field(description="Bachelor's Degree in Computer Science")
    highlights: list[str] = Field(description="Key academic achievements or relevant coursework")


class Education(BaseModel):
    entries: list[EducationEntry]


class ExperienceEntry(BaseModel):
    position: str = Field(description="Job title and company name")
    years: str = Field(description="Employment dates")
    highlights: list[str] = Field(description="Bullet points describing responsibilities and achievements")


class Experience(BaseModel):
    entries: list[ExperienceEntry]


class ProjectEntry(BaseModel):
    name: str = Field(description="Project title")
    tech: str = Field(description="Technologies used, e.g., 'Python / FastAPI / Docker'")
    highlights: list[str] = Field(description="Bullet points describing the technical impact and features")


class Projects(BaseModel):
    entries: list[ProjectEntry]


class LayoutText(BaseModel):
    size: str
    font: str


class LayoutSection(BaseModel):
    space_above_line: str
    space_below_line: str
    space_below_desc: str
    above_entry_header: str
    above_entry_subtitle: str
    between_highlights: str


class Layout(BaseModel):
    text: LayoutText
    section: LayoutSection


class ResumeTemplate(BaseModel):
    personal: Personal
    skills: Skills
    education: Education
    experience: Experience
    projects: Projects
    layout: Layout
