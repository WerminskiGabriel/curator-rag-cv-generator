import os


def parser_path(file_path):
    if not os.path.exists(file_path):
        raise Exception(f"File `{file_path}` does not exist")

    extension = file_path.split('.')[-1].lower()
    if extension == "pdf":
        txt_str = pdf_parser(file_path)
    elif extension in ["png", "jpg", "jpeg"]:
        txt_str = img_parser(file_path)
    elif extension == "docx":
        txt_str = doc_parser(file_path)
    else:
        raise Exception("File extension not supported")
    return txt_str


def pdf_parser(file_path):
    """
    parses pdfs( imgs | text) to txt in blocks
    """
    try:
        import fitz
    except ImportError as e:
        print(f"make sure u installed pymupdf {e}")

    # TextPage.extractDICT()
    doc = fitz.open(file_path)
    full_text = ["FILETYPE:PDF\n"]
    for page in doc:
        blocks = page.get_text("blocks")
        # extracts a page’s text blocks as a list of items like:
        # (x0, y0, x1, y1, "lines in block", block_no, block_type)

        for block in blocks:
            # block_type == 0 -> text type , 1 -> image type
            if block[6] == 0:
                full_text.append(block[4])  # + "\n"

    return "".join(full_text)


def img_parser(file_path):
    try:
        import fitz
    except ImportError as e:
        print(f"make sure u installed pymupdf {e}")

    full_text = ["FILETYPE:img\n"]
    doc = fitz.open(file_path)

    for page in doc:
        pix = page.get_pixmap()  # get_images():
        # OCR the image, make a 1-page PDF from it

        pdfdata = pix.pdfocr_tobytes()  # 1-page PDF in memory
        ocrpdf = fitz.open("pdf", pdfdata)  # open as PDF document

        for page in ocrpdf:  # .get_text()
            blocks = page.get_text("blocks")
            # extracts a page’s text blocks as a list of items like:
            # (x0, y0, x1, y1, "lines in block", block_no, block_type)

            for block in blocks:
                # block_type == 0 -> text type , 1 -> image type
                if block[6] == 0:
                    full_text.append(block[4])

    return "".join(full_text)


def doc_parser(file_path):
    try:
        from docx import Document
    except ImportError as e:
        print(e)

    # Load the document
    doc = Document(file_path)

    # Extract text from all paragraphs
    full_text = ["FILETYPE:DOCX\n"]
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)

    # Join all paragraphs into a single string
    text_content = '\n'.join(full_text)

    return text_content
