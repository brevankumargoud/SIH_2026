from typing import Dict, Any, Tuple
import os

class ArtifactGenerator:
    """Base interface for all artifact generators."""
    def generate(self, filepath: str, data: Dict[str, Any]) -> str:
        """Generates the file and returns the filepath."""
        raise NotImplementedError()

    def validate(self, filepath: str) -> Tuple[bool, str]:
        """Validates the artifact. Returns (is_valid, validation_message)."""
        if not os.path.exists(filepath):
            return False, "File does not exist."
        if os.path.getsize(filepath) == 0:
            return False, "File is empty."
        return True, "Valid."
