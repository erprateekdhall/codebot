"""
Code Chunking Engine
Splits code files into meaningful chunks for RAG indexing
"""

import ast
import logging
from typing import List, Dict
from pathlib import Path
import hashlib

from config import settings
from models.schemas import CodeChunk

logger = logging.getLogger(__name__)


class CodeChunker:
    """Chunks code files into meaningful segments"""
    
    def __init__(self):
        self.chunk_counter = 0
    
    async def chunk_repository(self, repo_path: str) -> List[CodeChunk]:
        """Chunk entire repository"""
        try:
            logger.info(f"Chunking repository: {repo_path}")
            repo = Path(repo_path)
            all_chunks = []

            # Define all supported file extensions
            code_extensions = {
                # Programming languages
                '.py', '.java', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.cpp', '.c',
                '.h', '.hpp', '.cs', '.php', '.rb', '.swift', '.kt', '.scala', '.r', '.m',
                # Web
                '.html', '.htm', '.css', '.scss', '.sass', '.less', '.vue',
                # Config & Data
                '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.conf', '.config',
                # Scripts & Shell
                '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
                # Documentation
                '.md', '.txt', '.rst', '.adoc',
                # Build & Package
                '.gradle', '.maven', '.pom', '.properties', '.env', '.dockerignore',
                # Database
                '.sql', '.graphql', '.prisma',
                # Other
                '.dockerfile', '.makefile', '.cmake'
            }

            # Binary and excluded extensions
            binary_extensions = {
                '.pyc', '.pyo', '.so', '.dll', '.dylib', '.exe', '.bin', '.class',
                '.jar', '.war', '.ear', '.zip', '.tar', '.gz', '.bz2', '.7z',
                '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp',
                '.mp3', '.mp4', '.avi', '.mov', '.pdf', '.doc', '.docx'
            }

            # Get all files in repository
            for filepath in repo.rglob("*"):
                # Skip directories
                if filepath.is_dir():
                    continue

                # Skip excluded patterns
                if any(pattern in str(filepath) for pattern in settings.EXCLUDE_PATTERNS):
                    continue

                # Get file extension
                ext = filepath.suffix.lower()

                # Skip binary files
                if ext in binary_extensions:
                    continue

                # Only process known code extensions or files without extensions (like Dockerfile, Makefile)
                if ext not in code_extensions and ext != '':
                    # Check if it's a special file without extension
                    if filepath.name.lower() not in ['dockerfile', 'makefile', 'readme', 'license', 'cmakelists.txt']:
                        continue

                # Check file size
                try:
                    if filepath.stat().st_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                        logger.warning(f"Skipping large file: {filepath}")
                        continue
                except:
                    continue

                # Determine language
                lang = self._detect_language(filepath)

                try:
                    chunks = await self.chunk_file(filepath, lang)
                    all_chunks.extend(chunks)
                except Exception as e:
                    logger.debug(f"Error processing {filepath}: {str(e)}")
                    continue

            logger.info(f"Created {len(all_chunks)} chunks from repository")
            return all_chunks

        except Exception as e:
            logger.error(f"Repository chunking failed: {str(e)}")
            return []

    def _detect_language(self, filepath: Path) -> str:
        """Detect file language from extension"""
        ext = filepath.suffix.lower()
        ext_map = {
            '.py': 'python',
            '.java': 'java',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
        }
        return ext_map.get(ext, 'generic')
    
    async def chunk_file(self, filepath: Path, language: str = "python") -> List[CodeChunk]:
        """Chunk a single file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if language == "python":
                return await self._chunk_python(filepath, content)
            else:
                # Fallback: simple line-based chunking
                return await self._chunk_generic(filepath, content, language)
        
        except Exception as e:
            logger.debug(f"Error chunking {filepath}: {str(e)}")
            return []
    
    async def _chunk_python(self, filepath: Path, content: str) -> List[CodeChunk]:
        """Chunk Python file using AST"""
        chunks = []
        
        try:
            tree = ast.parse(content)
            lines = content.split('\n')
            
            # Extract module-level docstring
            module_doc = ast.get_docstring(tree)
            
            # Process each top-level node
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    chunks.append(self._create_class_chunk(
                        node, lines, filepath, content
                    ))
                    
                    # Also chunk methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            chunks.append(self._create_method_chunk(
                                item, node.name, lines, filepath, content
                            ))
                
                elif isinstance(node, ast.FunctionDef):
                    chunks.append(self._create_function_chunk(
                        node, lines, filepath, content
                    ))
            
            # If no chunks created, create one for entire file
            if not chunks:
                chunks.append(self._create_file_chunk(filepath, content))
            
            return chunks
            
        except SyntaxError as e:
            logger.debug(f"Syntax error in {filepath}: {str(e)}")
            # Return file as single chunk
            return [self._create_file_chunk(filepath, content)]
    
    def _create_class_chunk(
        self,
        node: ast.ClassDef,
        lines: List[str],
        filepath: Path,
        full_content: str
    ) -> CodeChunk:
        """Create chunk for class"""
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        code = '\n'.join(lines[start_line-1:end_line])
        
        # Extract methods
        methods = [
            item.name for item in node.body
            if isinstance(item, ast.FunctionDef)
        ]
        
        # Extract imports used
        imports = self._extract_imports(full_content)
        
        return CodeChunk(
            chunk_id=self._generate_id(str(filepath), node.name, "class"),
            type="class",
            name=node.name,
            code=code,
            filepath=str(filepath),
            start_line=start_line,
            end_line=end_line,
            language="python",
            methods=methods,
            imports=imports
        )
    
    def _create_function_chunk(
        self,
        node: ast.FunctionDef,
        lines: List[str],
        filepath: Path,
        full_content: str
    ) -> CodeChunk:
        """Create chunk for function"""
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        code = '\n'.join(lines[start_line-1:end_line])
        imports = self._extract_imports(full_content)
        
        return CodeChunk(
            chunk_id=self._generate_id(str(filepath), node.name, "function"),
            type="function",
            name=node.name,
            code=code,
            filepath=str(filepath),
            start_line=start_line,
            end_line=end_line,
            language="python",
            methods=[],
            imports=imports
        )
    
    def _create_method_chunk(
        self,
        node: ast.FunctionDef,
        class_name: str,
        lines: List[str],
        filepath: Path,
        full_content: str
    ) -> CodeChunk:
        """Create chunk for method"""
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        code = '\n'.join(lines[start_line-1:end_line])
        imports = self._extract_imports(full_content)
        
        return CodeChunk(
            chunk_id=self._generate_id(str(filepath), f"{class_name}.{node.name}", "method"),
            type="method",
            name=f"{class_name}.{node.name}",
            code=code,
            filepath=str(filepath),
            start_line=start_line,
            end_line=end_line,
            language="python",
            methods=[],
            imports=imports
        )
    
    def _create_file_chunk(self, filepath: Path, content: str) -> CodeChunk:
        """Create chunk for entire file"""
        lines = content.split('\n')
        imports = self._extract_imports(content)
        
        return CodeChunk(
            chunk_id=self._generate_id(str(filepath), "module", "module"),
            type="module",
            name=filepath.stem,
            code=content,
            filepath=str(filepath),
            start_line=1,
            end_line=len(lines),
            language="python",
            methods=[],
            imports=imports
        )
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        imports = []
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except:
            pass
        
        return imports
    
    async def _chunk_generic(
        self,
        filepath: Path,
        content: str,
        language: str
    ) -> List[CodeChunk]:
        """Generic chunking for non-Python files"""
        chunks = []
        lines = content.split('\n')
        
        # Simple strategy: chunk by size
        chunk_size = settings.RAG_CHUNK_SIZE
        overlap = settings.RAG_CHUNK_OVERLAP
        
        start = 0
        while start < len(lines):
            end = min(start + chunk_size, len(lines))
            chunk_lines = lines[start:end]
            code = '\n'.join(chunk_lines)
            
            chunks.append(CodeChunk(
                chunk_id=self._generate_id(str(filepath), f"chunk_{start}", "code"),
                type="code",
                name=f"{filepath.stem}_chunk_{start}",
                code=code,
                filepath=str(filepath),
                start_line=start + 1,
                end_line=end,
                language=language,
                methods=[],
                imports=[]
            ))
            
            start = end - overlap if end < len(lines) else end
        
        return chunks
    
    def _generate_id(self, filepath: str, name: str, type: str) -> str:
        """Generate unique chunk ID"""
        unique_string = f"{filepath}:{name}:{type}"
        return hashlib.md5(unique_string.encode()).hexdigest()
