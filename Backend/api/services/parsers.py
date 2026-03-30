import os
from pathlib import Path


def parser_path(file_path):
    if not os.path.exists(file_path):
        raise Exception(f"File `{file_path}` does not exist")

    extension = file_path.split('.')[-1].lower()
    if extension == "pdf":
        txt_str = pdf_parser(file_path)
    elif extension in ["png", "jpg", "jpeg"]:
        txt_str = img_parser(file_path)
    else :
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
    full_text = ""
    for page in doc:
        blocks = page.get_text("blocks")
        # extracts a page’s text blocks as a list of items like: (x0, y0, x1, y1, "lines in block", block_no, block_type)

        for block in blocks:
            # block_type == 0 -> text type , 1 -> image type
            if block[6] == 0:
                full_text += block[4]  # + "\n"
    return full_text

def img_parser(file_path):
    try:
        import fitz
    except ImportError as e:
        print(f"make sure u installed pymupdf {e}")

    full_text = ""
    doc = fitz.open(file_path)

    for page in doc:
            pix = page.get_pixmap() #get_images():
            # OCR the image, make a 1-page PDF from it

            pdfdata = pix.pdfocr_tobytes()  # 1-page PDF in memory
            ocrpdf = fitz.open("pdf", pdfdata)  # open as PDF document

            for page in ocrpdf:  # .get_text()
                blocks = page.get_text("blocks")
                # extracts a page’s text blocks as a list of items like: (x0, y0, x1, y1, "lines in block", block_no, block_type)

                for block in blocks:
                    # block_type == 0 -> text type , 1 -> image type
                    if block[6] == 0:
                        full_text += block[4]  # + "\n"
    return full_text


"""
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
files_path = ROOT_DIR / "media" / "import_files" / "CV_NO_COLUMNS_1.pdf" 
files_path = ROOT_DIR / "media" / "import_files" / "CV_NO_COLUMNS_1.png" 
files_path = str(files_path)
print( parser_path(files_path) )
"""