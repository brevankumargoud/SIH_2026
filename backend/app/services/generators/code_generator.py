import os
from typing import Dict, Any, Tuple
from .base import ArtifactGenerator

class CodeArtifactGenerator(ArtifactGenerator):
    def generate(self, filepath: str, data: Dict[str, Any]) -> str:
        code_content = data.get("code", "")
        
        # Add a header comment to preserve metadata
        header = f"# Source: {data.get('source', 'AI Agent Generated')}\n"
        if data.get("language"):
            header += f"# Language: {data.get('language')}\n"
        header += "\n"
        
        with open(filepath, "w", encoding="utf-8") as f:
            if filepath.endswith(".py") or filepath.endswith(".sh"):
                f.write(header)
            elif filepath.endswith(".js") or filepath.endswith(".ts") or filepath.endswith(".cpp"):
                f.write(f"// Source: {data.get('source', 'AI Agent Generated')}\n\n")
            f.write(code_content)
            
        return filepath

    def validate(self, filepath: str) -> Tuple[bool, str]:
        base_valid, msg = super().validate(filepath)
        if not base_valid:
            return False, msg
            
        # Optional syntax validation for Python
        if filepath.endswith(".py"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    compile(f.read(), filepath, "exec")
            except SyntaxError as e:
                return False, f"Python Syntax Error: {e}"
            except Exception as e:
                return False, f"Validation read error: {e}"
                
        return True, "Valid Code Artifact."
