from .base import ArtifactGenerator
from .docx_generator import DocxGenerator
from .xlsx_generator import XlsxGenerator
from .pptx_generator import PptxGenerator
from .code_generator import CodeArtifactGenerator

def get_generator(artifact_type: str) -> ArtifactGenerator:
    if artifact_type == "docx":
        return DocxGenerator()
    elif artifact_type == "xlsx":
        return XlsxGenerator()
    elif artifact_type == "pptx":
        return PptxGenerator()
    elif artifact_type == "code":
        return CodeArtifactGenerator()
    else:
        raise ValueError(f"Unsupported artifact type: {artifact_type}")
