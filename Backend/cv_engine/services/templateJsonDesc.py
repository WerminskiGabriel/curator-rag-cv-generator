from pydantic import BaseModel, Field, RootModel


class PersonalInfo(BaseModel):
    telephone_label: str = Field(description="Formatted phone number for display, e.g., '+48 123 456 789'")
    telephone_link: str = Field(
        description="Formated phone number for links, has to have tel: prefix and no spaces, e.g., 'tel:+48123456789' or 'tel:123456789' ",
        pattern=r"^tel:\+?[0-9]+$")
    email: str = Field(description="Professional contact email address")
    github_label: str = Field(description="GitHub profile label, e.g., 'github.com/username'")
    github_link: str = Field(description="Full URL to the GitHub profile, e.g., 'https://github.com/johndoe'",
                             pattern=r"^https://(www\.)?github\.com/[a-zA-Z0-9_-]+/?$")
    linkedin_label: str = Field(description="LinkedIn profile label, e.g., 'linkedin.com/in/username'")
    linkedin_link: str = Field(
        description="Full URL to the LinkedIn profile, e.g., 'https://www.linkedin.com/in/johndoe'",
        pattern=r"^https://www\.linkedin\.com/in/[a-zA-Z0-9_-]+/?$")
    description: str = Field(
        description="A concise and professional career summary (prose), IT SHOUlD BE Inside info field not outside of it")


class Personal(BaseModel):
    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
    subtitle: str = Field(description="Header below the name, e.g., 'Software Engineering Student'")
    info: PersonalInfo


class SkillEntry(BaseModel):
    category: str = Field(description="Skill category name, e.g., 'Languages,'Programming','Technologies',")
    items: list[str] = Field(
        description="Array of strings. Each skill must be seperate element : e.g., Languages->['English (C1)','Polish(Native)'], Programming -> ['Python', 'Java', 'C', 'C++', 'SQL'], Technologies -> ['Django', 'Docker','Git', 'Linux', 'LaTeX'] ")


class EducationEntry(BaseModel):
    school: str = Field(description="Full name of the institution")
    years: str = Field(description="Duration of study, e.g., '2024 – Present', '2025-2028'")
    degree: str = Field(description="Bachelor's Degree in Computer Science")
    highlights: list[str] = Field(description="Key academic achievements or relevant coursework")


class ExperienceEntry(BaseModel):
    position: str = Field(description="Job title and company name")
    years: str = Field(description="Employment dates")
    highlights: list[str] = Field(description="Bullet points describing responsibilities and achievements")


class ProjectEntry(BaseModel):
    name: str = Field(description="Project title")
    tech: str = Field(description="Technologies used, e.g., 'Python / FastAPI / Docker'")
    highlights: list[str] = Field(
        description="Bullet points describing the technical impact and features, e.g. : ['highlight1','highlight2']")


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


class SkillsList(BaseModel):
    skillsList: list[SkillEntry] = Field(
        description="wrap it in  the 'skillsList' key. Output format: skillsList:[{}, {}]"
    )


class EducationList(BaseModel):
    educationList: list[EducationEntry] = Field(
        description="wrap it in  the 'educationList' key. Output format: educationList:[{}, {}]"
    )


class ExperienceList(BaseModel):
    experienceList: list[ExperienceEntry] = Field(
        description="wrap it in  the 'experienceList' key. Output format: experienceList:[{}, {}]"
    )


class ProjectList(BaseModel):
    projectList: list[ProjectEntry] = Field(
        description=" wrap it in  the 'projectList' key. Output format: projectList:[{}, {}]"
    )


class ResumeTemplate(BaseModel):
    personal: Personal
    skills: SkillsList
    education: EducationList
    experience: ExperienceList
    projects: ProjectList
    layout: Layout
