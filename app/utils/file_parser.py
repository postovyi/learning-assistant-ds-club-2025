from mrkdwn_analysis import MarkdownAnalyzer
from pypdf import PdfReader
from docx import Document

from abc import ABC, abstractmethod

class Parser(ABC):
    @abstractmethod
    @staticmethod
    def parse(file_path: str) -> str:
        raise NotImplementedError("This format isn't supported")


class PDFParser(Parser):
    @staticmethod
    def parse(file_path: str):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

class DocxParser(Parser):
    @staticmethod
    def parse(file_path: str) -> str:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text
        return text


class MDParser(Parser):
    @staticmethod
    def parse(file_path: str) -> str:
        analyzer = MarkdownAnalyzer(file_path)
        text = analyzer.text
        return text
class TXTParser(Parser):
    @staticmethod
    def parse(file_path: str) -> str:
        with open(file_path, "r") as f:
            text = f.read()
            return text

def get_parser(file_extension: str) -> Parser:
    parsers = {
        "pdf": PDFParser(),
        "docx": DocxParser(),
        "md": MDParser(),
        "txt": TXTParser()
    }
    return parsers.get(file_extension, Parser)