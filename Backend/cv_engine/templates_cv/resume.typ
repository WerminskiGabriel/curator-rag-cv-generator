//#let meta = toml( "info.toml")
#let meta = json( "info.json")

#let section_above_line = eval(meta.layout.section.space_above_line)
#let section_below_line = eval(meta.layout.section.space_below_line)
#let section_below_desc = eval(meta.layout.section.space_below_desc)
#let above_entry_header = eval(meta.layout.section.above_entry_header)
#let above_entry_subtitle = eval(meta.layout.section.above_entry_subtitle)
#let between_highlights = eval(meta.layout.section.between_highlights)
    
#set page(
  paper: "a4",
  margin: (top: 0.75in, bottom: 0.5in, left: 0.75in, right: 0.75in),
  fill: white,
)

#set text(
  font: meta.layout.text.font,
  size: eval(meta.layout.text.size),
  fill: black,
)

#let section-heading(title) = {
  v(section_above_line)
  line(length: 100%, stroke: 0.5pt + black)
  v(section_below_line)
  text(size: 15pt, weight: "bold", fill: black)[#upper(title)]
  v(section_below_desc)
}

#let entry-header(title, date) = {
  grid(
    columns: (1fr, auto),
    column-gutter: 2em,
    text(weight: "bold", size: 10.5pt)[#title],
    text(size: 10.5pt, weight: "bold")[#date]
  )
  v(above_entry_header)
}

#let entry-subtitle(subtitle) = {
  text(size: 10pt, style: "italic")[#subtitle]
  v(above_entry_subtitle)
}

#let icon(path) = box(
  baseline: 20%,
  image(path, height: 10pt)
)




// HEADER
#stack(
  dir: ttb,
  spacing: 6pt,
  text(size: 34pt, weight: "bold")[#meta.personal.first_name #meta.personal.last_name],
  text(size: 15pt, weight: "bold")[#meta.personal.subtitle]
)

#grid(
  columns: (10pt, auto,10pt,auto),
  row-gutter: 8pt,
  column-gutter: (2pt,   70pt, 2pt), 
  align: (center + horizon, left + horizon),

  [#icon("./icons/phone.png") ],[ #link( meta.personal.info.telephone_link)[#meta.personal.info.telephone_label]],
  [#icon("./icons/mail.png") ],[#link(meta.personal.info.email)[#meta.personal.info.email]],
  [#icon("./icons/github.png")],[ #link(meta.personal.info.github_link)[#meta.personal.info.github_label]],
  [#icon("./icons/linkedin.png") ],[#link(meta.personal.info.linkedin_link)[#meta.personal.info.linkedin_label]],
  
)


// ABOUT ME
#section-heading("About Me")

#meta.personal.about.description


// TECHNICAL SKILLS
#section-heading("Skills")

#grid(
  columns: (auto,auto),
  row-gutter: 1em,
  column-gutter: (2em),
  align: (left, left),
   ..meta.skills.entries.map(entry => (
    [#entry.category],
    [#entry.items]
  )).flatten()
) 




// EDUCATION
#section-heading("Education")

#for entry in meta.education.entries {
  entry-header(entry.school, entry.years)
  entry-subtitle(entry.degree)
  
  for highlight in entry.highlights {
    [- #highlight]
  }
  v(between_highlights)
}



// EXPERIENCE
#section-heading("Experience")

#for entry in meta.experience.entries {
  entry-header(entry.position, entry.years)
  
  for highlight in entry.highlights {
    [- #highlight]
  }
  v(between_highlights)
}



// PROJECTS
#section-heading("Projects")

#for entry in meta.projects.entries {
  entry-header(entry.name, entry.tech)
  
  for highlight in entry.highlights {
    [- #highlight]
  }
  v(between_highlights)
}

