"""PDF handling tools."""

from tools.web_tools import PDFLoaderTool


class PDFProcessor:
    """Utilities for PDF extraction and chunking."""
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extract all text from PDF."""
        raise NotImplementedError("PHASE 1")
    
    @staticmethod
    def chunk_pdf_content(text: str, chunk_size: int = 500) -> list:
        """Split PDF text into overlapping chunks."""
        raise NotImplementedError("PHASE 3")
