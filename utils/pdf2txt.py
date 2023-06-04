import os
import io
import codecs

from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter


def pdfparser(data):
    """
        Extract data from a PDF file
        Input: PDF file name
        Output: PDF file content
    """
    fp = open(data, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # Process each page contained in the document.

    for page in PDFPage.get_pages(fp, check_extractable=False):
        interpreter.process_page(page)
        data = retstr.getvalue()
    return data


def convertPDFToText(path):
    """
        Convert a list of PDF files into a list of TXT files
        Input: Path where PDF are saved
    """
    for d in os.listdir(path):
        fileExtension = d.split(".")[-1]
        if fileExtension == "pdf":
            docxFilename = path + d
            print(docxFilename)
            document = pdfparser(docxFilename)
            textFilename = path + d.split(".")[0] + ".txt"
            with codecs.open(textFilename, "w", encoding="utf-8", errors='replace') as text_file:
                print(document, file=text_file)
