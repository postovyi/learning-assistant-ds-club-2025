# pip install pydocx
# pip install pypdf
# pip install markdown-analysis

from mrkdwn_analysis import MarkdownAnalyzer
from pypdf import PdfReader
from docx import Document

from abc import ABC, abstractmethod

class Parser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> str:
        return "This format isn't supported"


class PDFParser(Parser):
    def parse(self, file_path: str):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

class DocxParser(Parser):
    def parse(self, file_path: str) -> str:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text
        return text


class MDParser(Parser):
    def parse(self, file_path: str) -> str:
        analyzer = MarkdownAnalyzer("file.md")
        text = analyzer.text
        return text
class TXTParser(Parser):
    def parse(self, file_path: str) -> str:
        with open(file_path, "r") as f:
            text = f.read()
            return text

def get_parser(file_extension: str) -> Parser:
    parsers = {
        "pdf": PDFParser,
        "docx": DocxParser,
        "md": MDParser,
        "txt": TXTParser
    }
    return parsers.get(file_extension, Parser)()

if __name__ == "__main__":
    try:
        file_path = r"C:\Users\kobol\Downloads\English_report.docx"
        file_extension = file_path.split(".")[-1]
        parser = get_parser(file_extension)
        print(parser.parse(file_path))
    except Exception:
        print("Oops! We have some problems")