from pathlib import Path
from typing import List, Union
from pypdf import PdfReader  
from aimakerspace.text_utils import CharacterTextSplitter

class PDFFileLoader:

    def __init__(self, path: Union[str, Path] = "data/pdfs", *, lazy: bool = False):
        self.path = Path(path).expanduser().resolve()
        self.lazy = lazy
        self._documents: List[str] = []

    def load_documents(self) -> List[str]:
        """Return a list of every PDF’s concatenated plain-text content."""
        if self.lazy:  # streaming generator mode
            return list(self._iter_documents())
        self._documents = list(self._iter_documents())
        return self._documents

    def _iter_documents(self):
        if self.path.is_dir():
            yield from self._load_directory(self.path)
        elif self.path.is_file() and self.path.suffix.lower() == ".pdf":
            yield self._read_pdf(self.path)
        else:
            raise ValueError("Path must be a directory or a .pdf file")

    def _load_directory(self, directory: Path):
        for pdf_path in directory.rglob("*.pdf"):
            # Skip zero-byte or obviously corrupt files early
            if pdf_path.stat().st_size < 1024:
                continue
            yield self._read_pdf(pdf_path)

    @staticmethod
    def _read_pdf(pdf_path: Path) -> str:
        reader = PdfReader(str(pdf_path))
        pages_text = (page.extract_text() or "" for page in reader.pages)
        return "\n".join(pages_text)


if __name__ == "__main__":
    loader = PDFFileLoader()   # scans ./data/pdfs by default
    pdf_docs = loader.load_documents()

    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_texts(pdf_docs)

    print(f"{len(pdf_docs)=}")
    print(f"{len(chunks)=}")
    print(chunks[0][:200], "...")
