"""
Context Builder - Merges Results from Multiple Engines
Formats and combines data for Claude analysis
"""

import logging
from typing import List, Dict

from models.schemas import CodeSnippet, GitInfo

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds comprehensive context from multiple data sources"""
    
    def build_exception_context(
        self,
        exception_data,
        rag_results: List[Dict],
        git_results: List[Dict],
        static_results: Dict
    ) -> str:
        """Build context for exception analysis"""
        
        parts = []
        
        # Exception details
        parts.append("=== EXCEPTION DETAILS ===")
        parts.append(f"Type: {exception_data.exception_type}")
        parts.append(f"Message: {exception_data.exception_message}")
        
        if exception_data.time_context:
            parts.append(f"Time Context: {', '.join(exception_data.time_context)}")
        
        if exception_data.affected_users:
            parts.append(f"Affected Users: {', '.join(exception_data.affected_users)}")
        
        parts.append("")
        
        # Stack trace
        if exception_data.stack_trace:
            parts.append("=== STACK TRACE ===")
            for frame in exception_data.stack_trace:
                parts.append(f"File: {frame.get('filepath', 'unknown')}")
                parts.append(f"  Line {frame.get('line_number', '?')} in {frame.get('function', 'unknown')}")
            parts.append("")
        
        # Relevant code
        if rag_results:
            parts.append("=== RELEVANT CODE ===")
            for i, result in enumerate(rag_results[:5], 1):
                parts.append(f"\n--- Result {i} ---")
                parts.append(f"File: {result.get('metadata', {}).get('filepath', 'unknown')}")
                parts.append(f"Score: {result.get('score', 0):.2f}")
                parts.append(f"\n{result.get('code', '')}")
            parts.append("")
        
        # Git history
        if git_results:
            parts.append("=== RECENT CHANGES ===")
            for commit in git_results[:5]:
                parts.append(f"Author: {commit.get('author_name', 'unknown')}")
                parts.append(f"Date: {commit.get('commit_date', 'unknown')}")
                parts.append(f"Message: {commit.get('message', 'unknown')}")
                parts.append("")
        
        # Dependencies
        if static_results:
            parts.append("=== DEPENDENCIES ===")
            for func, deps in static_results.items():
                parts.append(f"\nFunction: {func}")
                if deps.get('callers'):
                    parts.append(f"  Called by: {[c.get('caller_name') for c in deps['callers']]}")
                if deps.get('callees'):
                    parts.append(f"  Calls: {[c.get('callee_name') for c in deps['callees']]}")
        
        return "\n".join(parts)
    
    def build_bug_context(
        self,
        query: str,
        rag_results: List[Dict],
        git_results: List[Dict],
        deps_results: Dict
    ) -> str:
        """Build context for bug analysis"""
        
        parts = []
        
        parts.append("=== QUERY ===")
        parts.append(query)
        parts.append("")
        
        if rag_results:
            parts.append("=== RELEVANT CODE ===")
            for i, result in enumerate(rag_results[:5], 1):
                meta = result.get('metadata', {})
                parts.append(f"\n--- {meta.get('name', 'unknown')} ({meta.get('type', 'code')}) ---")
                parts.append(f"File: {meta.get('filepath', 'unknown')}")
                parts.append(f"Lines: {meta.get('start_line', '?')}-{meta.get('end_line', '?')}")
                parts.append(f"\n{result.get('code', '')}")
            parts.append("")
        
        if git_results:
            parts.append("=== RECENT COMMITS ===")
            for commit in git_results[:3]:
                parts.append(f"{commit.get('commit_date', 'unknown')} - {commit.get('author_name', 'unknown')}")
                parts.append(f"  {commit.get('message', 'unknown')}")
            parts.append("")
        
        if deps_results:
            parts.append("=== DEPENDENCIES ===")
            for func, deps in list(deps_results.items())[:3]:
                parts.append(f"\n{func}:")
                if deps.get('callers'):
                    parts.append(f"  Used by: {', '.join([c.get('caller_name', '?') for c in deps['callers'][:5]])}")
                if deps.get('callees'):
                    parts.append(f"  Uses: {', '.join([c.get('callee_name', '?') for c in deps['callees'][:5]])}")
        
        return "\n".join(parts)
    
    def build_search_context(
        self,
        query: str,
        rag_results: List[Dict]
    ) -> str:
        """Build context for code search"""
        
        parts = []
        
        parts.append(f"Search query: {query}\n")
        
        if rag_results:
            parts.append(f"Found {len(rag_results)} relevant code segments:\n")
            
            for i, result in enumerate(rag_results, 1):
                meta = result.get('metadata', {})
                parts.append(f"\n=== Result {i}: {meta.get('name', 'unknown')} ===")
                parts.append(f"Type: {meta.get('type', 'code')}")
                parts.append(f"File: {meta.get('filepath', 'unknown')}")
                parts.append(f"Location: Lines {meta.get('start_line', '?')}-{meta.get('end_line', '?')}")
                parts.append(f"Relevance: {result.get('score', 0):.2f}")
                parts.append(f"\nCode:\n{result.get('code', '')}")
        else:
            parts.append("No matching code found.")
        
        return "\n".join(parts)
    
    def build_author_context(
        self,
        query: str,
        rag_results: List[Dict],
        git_results: List[Dict]
    ) -> str:
        """Build context for author lookup"""
        
        parts = []
        
        parts.append(f"Query: {query}\n")
        
        if git_results:
            parts.append("=== GIT HISTORY ===\n")
            
            # Group by file
            by_file = {}
            for commit in git_results:
                # Extract filename from rag results if available
                file = "unknown"
                if rag_results:
                    file = rag_results[0].get('metadata', {}).get('filepath', 'unknown')
                
                if file not in by_file:
                    by_file[file] = []
                by_file[file].append(commit)
            
            for file, commits in list(by_file.items())[:5]:
                parts.append(f"\n--- {file} ---")
                for commit in commits[:3]:
                    parts.append(f"{commit.get('author_name', 'unknown')} <{commit.get('author_email', 'unknown')}>")
                    parts.append(f"  Date: {commit.get('commit_date', 'unknown')}")
                    parts.append(f"  Message: {commit.get('message', 'unknown')}")
                    parts.append("")
        
        if rag_results:
            parts.append("\n=== RELEVANT CODE ===")
            for result in rag_results[:3]:
                meta = result.get('metadata', {})
                parts.append(f"\nFile: {meta.get('filepath', 'unknown')}")
                parts.append(f"Function: {meta.get('name', 'unknown')}")
        
        return "\n".join(parts)
    
    def build_explanation_context(
        self,
        query: str,
        rag_results: List[Dict],
        deps_results: Dict
    ) -> str:
        """Build context for code explanation"""
        
        parts = []
        
        parts.append(f"Explain: {query}\n")
        
        if rag_results:
            parts.append("=== CODE TO EXPLAIN ===\n")
            
            for i, result in enumerate(rag_results[:5], 1):
                meta = result.get('metadata', {})
                parts.append(f"\n--- {meta.get('name', 'unknown')} ---")
                parts.append(f"Type: {meta.get('type', 'code')}")
                parts.append(f"File: {meta.get('filepath', 'unknown')}")
                parts.append(f"\n{result.get('code', '')}")
        
        if deps_results:
            parts.append("\n=== CALL RELATIONSHIPS ===")
            for func, deps in list(deps_results.items())[:3]:
                parts.append(f"\n{func}:")
                if deps.get('callers'):
                    parts.append(f"  Called by: {', '.join([c.get('caller_name', '?') for c in deps['callers'][:5]])}")
                if deps.get('callees'):
                    parts.append(f"  Calls: {', '.join([c.get('callee_name', '?') for c in deps['callees'][:5]])}")
        
        return "\n".join(parts)
    
    def build_dependency_context(
        self,
        query: str,
        deps_results: Dict,
        rag_results: List[Dict]
    ) -> str:
        """Build context for dependency analysis"""
        
        parts = []
        
        parts.append(f"Query: {query}\n")
        
        if deps_results:
            parts.append("=== DEPENDENCY GRAPH ===\n")
            
            for func, deps in deps_results.items():
                parts.append(f"\n--- {func} ---")
                
                if deps.get('callers'):
                    parts.append("\nCalled by:")
                    for caller in deps['callers'][:10]:
                        parts.append(f"  • {caller.get('caller_name', '?')} in {caller.get('caller_file', '?')}")
                
                if deps.get('callees'):
                    parts.append("\nCalls:")
                    for callee in deps['callees'][:10]:
                        parts.append(f"  • {callee.get('callee_name', '?')} in {callee.get('callee_file', '?')}")
        
        if rag_results:
            parts.append("\n=== RELATED CODE ===")
            for result in rag_results[:3]:
                meta = result.get('metadata', {})
                parts.append(f"\n{meta.get('name', 'unknown')} ({meta.get('filepath', 'unknown')})")
        
        return "\n".join(parts)
    
    def build_general_context(
        self,
        query: str,
        rag_results: List[Dict]
    ) -> str:
        """Build context for general questions"""
        
        parts = []
        
        parts.append(f"Question: {query}\n")
        
        if rag_results:
            parts.append("=== RELEVANT CODE CONTEXT ===\n")
            
            for i, result in enumerate(rag_results, 1):
                meta = result.get('metadata', {})
                parts.append(f"\n--- Context {i} ---")
                parts.append(f"From: {meta.get('filepath', 'unknown')}")
                parts.append(f"\n{result.get('code', '')[:500]}...")  # Truncate
        else:
            parts.append("No specific code context available.")
        
        return "\n".join(parts)
    
    def format_sources(self, rag_results: List[Dict]) -> List[CodeSnippet]:
        """Format RAG results as CodeSnippet objects"""
        sources = []
        
        for result in rag_results:
            meta = result.get('metadata', {})
            
            sources.append(CodeSnippet(
                file=meta.get('filepath', 'unknown'),
                function=meta.get('name'),
                start_line=meta.get('start_line', 0),
                end_line=meta.get('end_line', 0),
                code=result.get('code', ''),
                relevance_score=result.get('score', 0.0)
            ))
        
        return sources
    
    def format_git_info(self, git_results: List[Dict]) -> List[GitInfo]:
        """Format git results as GitInfo objects"""
        git_info = []
        
        for commit in git_results:
            try:
                git_info.append(GitInfo(
                    author=commit.get('author_name', 'unknown'),
                    email=commit.get('author_email', 'unknown'),
                    date=commit.get('commit_date'),
                    message=commit.get('message', ''),
                    sha=commit.get('sha', 'unknown'),
                    lines_added=commit.get('insertions'),
                    lines_deleted=commit.get('deletions')
                ))
            except Exception as e:
                logger.debug(f"Error formatting git info: {str(e)}")
                continue
        
        return git_info
