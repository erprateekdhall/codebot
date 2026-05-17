"""
Static Code Analyzer - Neo4j Graph Database
Builds and queries code relationship graph
"""

from neo4j import GraphDatabase
from typing import List, Dict, Optional
from pathlib import Path
import logging
import ast
import asyncio

from config import settings

logger = logging.getLogger(__name__)


class StaticAnalyzer:
    """Static code analysis using AST and graph database"""
    
    def __init__(self):
        self.driver = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize Neo4j connection"""
        try:
            logger.info("Initializing Static Analyzer...")
            
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            
            # Create constraints and indexes
            await self._create_schema()
            
            self.initialized = True
            logger.info("✅ Static Analyzer initialized")
            
        except Exception as e:
            logger.error(f"Static Analyzer init failed: {str(e)}")
            raise
    
    async def _create_schema(self):
        """Create Neo4j schema"""
        with self.driver.session() as session:
            # Create constraints
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (f:File) REQUIRE f.path IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Class) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (fn:Function) REQUIRE fn.id IS UNIQUE",
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    logger.debug(f"Constraint creation: {str(e)}")
    
    async def build_graph(self, repo_path: str):
        """Build code graph from repository"""
        try:
            logger.info(f"Building code graph for {repo_path}")
            repo = Path(repo_path)
            
            # Find all Python files
            python_files = list(repo.rglob("*.py"))
            logger.info(f"Found {len(python_files)} Python files")
            
            for filepath in python_files:
                # Skip excluded patterns
                if any(pattern in str(filepath) for pattern in settings.EXCLUDE_PATTERNS):
                    continue
                
                await self._process_file(filepath)
            
            logger.info("✅ Code graph built successfully")
            
        except Exception as e:
            logger.error(f"Graph building failed: {str(e)}")
            raise
    
    async def _process_file(self, filepath: Path):
        """Process single file and add to graph"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse with AST
            tree = ast.parse(content, filename=str(filepath))
            
            rel_path = str(filepath)
            
            with self.driver.session() as session:
                # Create file node
                session.run("""
                    MERGE (f:File {path: $path})
                    SET f.name = $name
                """, path=rel_path, name=filepath.name)
                
                # Process classes and functions
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        await self._process_class(session, node, rel_path, content)
                    elif isinstance(node, ast.FunctionDef):
                        await self._process_function(session, node, rel_path, content)
        
        except Exception as e:
            logger.debug(f"Error processing {filepath}: {str(e)}")
    
    async def _process_class(self, session, node, filepath: str, content: str):
        """Process class definition"""
        try:
            class_id = f"{filepath}:{node.name}"
            
            # Create class node
            session.run("""
                MERGE (c:Class {id: $id})
                SET c.name = $name,
                    c.filepath = $filepath,
                    c.start_line = $start_line,
                    c.end_line = $end_line
            """, id=class_id, name=node.name, filepath=filepath,
                 start_line=node.lineno, end_line=node.end_lineno or node.lineno)
            
            # Link to file
            session.run("""
                MATCH (f:File {path: $filepath})
                MATCH (c:Class {id: $class_id})
                MERGE (f)-[:CONTAINS]->(c)
            """, filepath=filepath, class_id=class_id)
            
            # Process base classes (inheritance)
            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_name = base.id
                    session.run("""
                        MATCH (c:Class {id: $class_id})
                        MERGE (b:Class {name: $base_name})
                        MERGE (c)-[:INHERITS]->(b)
                    """, class_id=class_id, base_name=base_name)
            
            # Process methods
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_id = f"{class_id}.{item.name}"
                    
                    session.run("""
                        MERGE (m:Function {id: $method_id})
                        SET m.name = $name,
                            m.filepath = $filepath,
                            m.start_line = $start_line,
                            m.end_line = $end_line,
                            m.is_method = true
                    """, method_id=method_id, name=item.name, filepath=filepath,
                         start_line=item.lineno, end_line=item.end_lineno or item.lineno)
                    
                    # Link method to class
                    session.run("""
                        MATCH (c:Class {id: $class_id})
                        MATCH (m:Function {id: $method_id})
                        MERGE (c)-[:CONTAINS]->(m)
                    """, class_id=class_id, method_id=method_id)
                    
                    # Analyze function calls within method
                    await self._analyze_calls(session, item, method_id)
        
        except Exception as e:
            logger.debug(f"Error processing class {node.name}: {str(e)}")
    
    async def _process_function(self, session, node, filepath: str, content: str):
        """Process function definition"""
        try:
            func_id = f"{filepath}:{node.name}"
            
            # Create function node
            session.run("""
                MERGE (fn:Function {id: $id})
                SET fn.name = $name,
                    fn.filepath = $filepath,
                    fn.start_line = $start_line,
                    fn.end_line = $end_line,
                    fn.is_method = false
            """, id=func_id, name=node.name, filepath=filepath,
                 start_line=node.lineno, end_line=node.end_lineno or node.lineno)
            
            # Link to file
            session.run("""
                MATCH (f:File {path: $filepath})
                MATCH (fn:Function {id: $func_id})
                MERGE (f)-[:CONTAINS]->(fn)
            """, filepath=filepath, func_id=func_id)
            
            # Analyze function calls
            await self._analyze_calls(session, node, func_id)
        
        except Exception as e:
            logger.debug(f"Error processing function {node.name}: {str(e)}")
    
    async def _analyze_calls(self, session, node, caller_id: str):
        """Analyze function calls within a function/method"""
        try:
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    # Extract function name
                    callee_name = None
                    
                    if isinstance(child.func, ast.Name):
                        callee_name = child.func.id
                    elif isinstance(child.func, ast.Attribute):
                        callee_name = child.func.attr
                    
                    if callee_name:
                        # Create CALLS relationship
                        session.run("""
                            MATCH (caller:Function {id: $caller_id})
                            MERGE (callee:Function {name: $callee_name})
                            MERGE (caller)-[:CALLS]->(callee)
                        """, caller_id=caller_id, callee_name=callee_name)
        
        except Exception as e:
            logger.debug(f"Error analyzing calls: {str(e)}")
    
    async def find_callers(self, function_name: str) -> List[Dict]:
        """Find all functions that call this function"""
        if not self.initialized:
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (caller:Function)-[:CALLS]->(callee:Function {name: $name})
                    RETURN caller.name as caller_name,
                           caller.filepath as caller_file,
                           caller.start_line as line
                    LIMIT 50
                """, name=function_name)
                
                return [dict(record) for record in result]
        
        except Exception as e:
            logger.error(f"Error finding callers: {str(e)}")
            return []
    
    async def find_callees(self, function_name: str) -> List[Dict]:
        """Find all functions called by this function"""
        if not self.initialized:
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (caller:Function {name: $name})-[:CALLS]->(callee:Function)
                    RETURN callee.name as callee_name,
                           callee.filepath as callee_file,
                           callee.start_line as line
                    LIMIT 50
                """, name=function_name)
                
                return [dict(record) for record in result]
        
        except Exception as e:
            logger.error(f"Error finding callees: {str(e)}")
            return []
    
    async def find_class_dependencies(self, class_name: str) -> List[Dict]:
        """Find dependencies of a class"""
        if not self.initialized:
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (c:Class {name: $name})-[:INHERITS]->(parent:Class)
                    RETURN parent.name as parent_class,
                           parent.filepath as file
                """, name=class_name)
                
                return [dict(record) for record in result]
        
        except Exception as e:
            logger.error(f"Error finding dependencies: {str(e)}")
            return []
    
    async def health_check(self) -> bool:
        """Check if analyzer is healthy"""
        try:
            if not self.initialized:
                return False
            
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    async def close(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.close()
        logger.info("Static Analyzer closed")
