"""
Agent Orchestrator - Query Routing and Processing
Routes queries to appropriate engines and coordinates responses
"""

import logging
from typing import Dict, Optional
import anthropic
import asyncio

from config import settings
from models.schemas import QueryIntent
from agents.context_builder import ContextBuilder

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates query processing across multiple engines"""
    
    def __init__(
        self,
        rag_engine,
        static_analyzer,
        git_analyzer,
        query_parser,
        exception_parser
    ):
        self.rag_engine = rag_engine
        self.static_analyzer = static_analyzer
        self.git_analyzer = git_analyzer
        self.query_parser = query_parser
        self.exception_parser = exception_parser
        
        # Initialize Claude client
        self.claude_client = anthropic.Anthropic(
            api_key=settings.ANTHROPIC_API_KEY
        )
        
        # Initialize context builder
        self.context_builder = ContextBuilder()
    
    async def process_query(
        self,
        message: str,
        conversation_id: Optional[str] = None
    ) -> Dict:
        """Main query processing logic"""
        try:
            logger.info(f"Processing query: {message[:100]}...")
            
            # First check if it's an exception
            exception_data = await self.exception_parser.parse_exception(message)
            
            if exception_data.has_exception:
                return await self._handle_exception(message, exception_data, conversation_id)
            
            # Parse regular query
            parsed_query = await self.query_parser.parse(message)
            logger.info(f"Detected intent: {parsed_query.intent}")
            
            # Route based on intent
            if parsed_query.intent == QueryIntent.BUG_ANALYSIS:
                return await self._handle_bug_analysis(message, parsed_query, conversation_id)
            
            elif parsed_query.intent == QueryIntent.CODE_SEARCH:
                return await self._handle_code_search(message, parsed_query, conversation_id)
            
            elif parsed_query.intent == QueryIntent.AUTHOR_LOOKUP:
                return await self._handle_author_lookup(message, parsed_query, conversation_id)
            
            elif parsed_query.intent == QueryIntent.CODE_EXPLANATION:
                return await self._handle_explanation(message, parsed_query, conversation_id)
            
            elif parsed_query.intent == QueryIntent.DEPENDENCY_CHECK:
                return await self._handle_dependency_check(message, parsed_query, conversation_id)
            
            else:
                return await self._handle_general_question(message, parsed_query, conversation_id)
        
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}", exc_info=True)
            return {
                "response": f"I encountered an error: {str(e)}. Please try rephrasing your question.",
                "sources": [],
                "git_info": [],
                "intent": "general_question",
                "confidence": "low",
                "conversation_id": conversation_id or "unknown"
            }
    
    async def _handle_exception(self, message: str, exception_data, conversation_id: str) -> Dict:
        """Handle exception analysis"""
        logger.info("Handling exception analysis")
        
        # Gather data from all sources
        results = await asyncio.gather(
            self._get_rag_results(message, n_results=5),
            self._get_git_history(exception_data.files_involved),
            self._get_static_analysis(exception_data.functions_involved),
            return_exceptions=True
        )
        
        rag_results = results[0] if not isinstance(results[0], Exception) else []
        git_results = results[1] if not isinstance(results[1], Exception) else []
        static_results = results[2] if not isinstance(results[2], Exception) else []
        
        # Build context
        context = self.context_builder.build_exception_context(
            exception_data=exception_data,
            rag_results=rag_results,
            git_results=git_results,
            static_results=static_results
        )
        
        # Get Claude analysis
        response = await self._call_claude(
            context=context,
            query=message,
            task="exception_analysis"
        )
        
        return {
            "response": response,
            "sources": self.context_builder.format_sources(rag_results),
            "git_info": self.context_builder.format_git_info(git_results),
            "intent": "bug_analysis",
            "confidence": "high",
            "conversation_id": conversation_id or "unknown"
        }
    
    async def _handle_bug_analysis(self, message: str, parsed_query, conversation_id: str) -> Dict:
        """Handle bug analysis queries"""
        logger.info("Handling bug analysis")
        
        # Use all engines
        results = await asyncio.gather(
            self._get_rag_results(message, n_results=7),
            self._get_git_recent_changes(),
            self._get_dependencies_for_entities(parsed_query.entities),
            return_exceptions=True
        )
        
        rag_results = results[0] if not isinstance(results[0], Exception) else []
        git_results = results[1] if not isinstance(results[1], Exception) else []
        deps_results = results[2] if not isinstance(results[2], Exception) else {}
        
        context = self.context_builder.build_bug_context(
            query=message,
            rag_results=rag_results,
            git_results=git_results,
            deps_results=deps_results
        )
        
        response = await self._call_claude(context, message, "bug_analysis")
        
        return {
            "response": response,
            "sources": self.context_builder.format_sources(rag_results),
            "git_info": self.context_builder.format_git_info(git_results),
            "intent": "bug_analysis",
            "confidence": "high",
            "conversation_id": conversation_id or "unknown"
        }
    
    async def _handle_code_search(self, message: str, parsed_query, conversation_id: str) -> Dict:
        """Handle code search queries"""
        logger.info("Handling code search")
        
        # Primarily use RAG
        rag_results = await self._get_rag_results(message, n_results=10)
        
        context = self.context_builder.build_search_context(
            query=message,
            rag_results=rag_results
        )
        
        response = await self._call_claude(context, message, "code_search")
        
        return {
            "response": response,
            "sources": self.context_builder.format_sources(rag_results),
            "git_info": [],
            "intent": "code_search",
            "confidence": "medium",
            "conversation_id": conversation_id or "unknown"
        }
    
    async def _handle_author_lookup(self, message: str, parsed_query, conversation_id: str) -> Dict:
        """Handle author lookup queries"""
        logger.info("Handling author lookup")
        
        # Use RAG to find files, then Git for history
        rag_results = await self._get_rag_results(message, n_results=5)
        
        # Get git history for found files
        files = [r['metadata']['filepath'] for r in rag_results if 'metadata' in r]
        git_results = await self._get_git_history(files)
        
        context = self.context_builder.build_author_context(
            query=message,
            rag_results=rag_results,
            git_results=git_results
        )
        
        response = await self._call_claude(context, message, "author_lookup")
        
        return {
            "response": response,
            "sources": self.context_builder.format_sources(rag_results),
            "git_info": self.context_builder.format_git_info(git_results),
            "intent": "author_lookup",
            "confidence": "high",
            "conversation_id": conversation_id or "unknown"
        }
    
    async def _handle_explanation(self, message: str, parsed_query, conversation_id: str) -> Dict:
        """Handle code explanation queries"""
        logger.info("Handling code explanation")
        
        # Use RAG + Static Analysis
        rag_results = await self._get_rag_results(message, n_results=7)
        deps = await self._get_dependencies_for_entities(parsed_query.entities)
        
        context = self.context_builder.build_explanation_context(
            query=message,
            rag_results=rag_results,
            deps_results=deps
        )
        
        response = await self._call_claude(context, message, "explanation")
        
        return {
            "response": response,
            "sources": self.context_builder.format_sources(rag_results),
            "git_info": [],
            "intent": "code_explanation",
            "confidence": "high",
            "conversation_id": conversation_id or "unknown"
        }
    
    async def _handle_dependency_check(self, message: str, parsed_query, conversation_id: str) -> Dict:
        """Handle dependency analysis queries"""
        logger.info("Handling dependency check")
        
        # Primarily use static analysis
        deps = await self._get_dependencies_for_entities(parsed_query.entities)
        rag_results = await self._get_rag_results(message, n_results=5)
        
        context = self.context_builder.build_dependency_context(
            query=message,
            deps_results=deps,
            rag_results=rag_results
        )
        
        response = await self._call_claude(context, message, "dependency_check")
        
        return {
            "response": response,
            "sources": self.context_builder.format_sources(rag_results),
            "git_info": [],
            "intent": "dependency_check",
            "confidence": "medium",
            "conversation_id": conversation_id or "unknown"
        }
    
    async def _handle_general_question(self, message: str, parsed_query, conversation_id: str) -> Dict:
        """Handle general questions"""
        logger.info("Handling general question")
        
        # Light RAG search
        rag_results = await self._get_rag_results(message, n_results=3)
        
        context = self.context_builder.build_general_context(
            query=message,
            rag_results=rag_results
        )
        
        response = await self._call_claude(context, message, "general")
        
        return {
            "response": response,
            "sources": self.context_builder.format_sources(rag_results),
            "git_info": [],
            "intent": "general_question",
            "confidence": "low",
            "conversation_id": conversation_id or "unknown"
        }
    
    async def _get_rag_results(self, query: str, n_results: int = 5) -> list:
        """Get results from RAG engine"""
        try:
            return await self.rag_engine.search(query, n_results=n_results)
        except Exception as e:
            logger.error(f"RAG search failed: {str(e)}")
            return []
    
    async def _get_git_history(self, files: list) -> list:
        """Get git history for files"""
        try:
            all_history = []
            for file in files[:5]:  # Limit to 5 files
                history = await self.git_analyzer.get_file_history(file, limit=3)
                all_history.extend(history)
            return all_history
        except Exception as e:
            logger.error(f"Git history failed: {str(e)}")
            return []
    
    async def _get_git_recent_changes(self) -> list:
        """Get recent commits"""
        try:
            return await self.git_analyzer.get_recent_commits(limit=10)
        except Exception as e:
            logger.error(f"Git recent commits failed: {str(e)}")
            return []
    
    async def _get_dependencies_for_entities(self, entities: dict) -> dict:
        """Get dependencies for extracted entities"""
        try:
            deps = {}
            
            # Get dependencies for functions
            for func in entities.get('functions', [])[:5]:
                callers = await self.static_analyzer.find_callers(func)
                callees = await self.static_analyzer.find_callees(func)
                deps[func] = {'callers': callers, 'callees': callees}
            
            return deps
        except Exception as e:
            logger.error(f"Dependency analysis failed: {str(e)}")
            return {}
    
    async def _get_static_analysis(self, functions: list) -> dict:
        """Get static analysis for functions"""
        return await self._get_dependencies_for_entities({'functions': functions})
    
    async def _call_claude(self, context: str, query: str, task: str) -> str:
        """Call Claude API for analysis"""
        try:
            # Build prompt based on task
            prompts = {
                "exception_analysis": f"""Analyze this exception and provide:
1. Root cause
2. Why it's happening
3. Exact fix with code
4. How to prevent it

Context:
{context}

User query: {query}""",
                
                "bug_analysis": f"""Analyze this bug:
{context}

User query: {query}

Provide root cause and solution.""",
                
                "code_search": f"""Based on this code context:
{context}

Answer: {query}""",
                
                "author_lookup": f"""Based on git history:
{context}

Answer: {query}""",
                
                "explanation": f"""You are a helpful code teacher explaining code to someone who may not be a programmer.

Your task: Explain the code logic in simple, clear language.

IMPORTANT GUIDELINES:
1. **Use Plain English**: Avoid technical jargon. If you must use technical terms, explain them.
2. **Focus on WHAT it does, not HOW**: Explain the purpose and logic, not just the syntax.
3. **Use Analogies**: Compare to real-world concepts when helpful.
4. **Be Conversational**: Write like you're talking to a friend, not writing documentation.
5. **Structure your explanation**:
   - Start with: "This code does X" (high-level purpose)
   - Then: Explain the main logic step-by-step
   - End with: Why this approach makes sense or what problem it solves

6. **ONLY show code snippets if specifically asked** - otherwise, just explain the logic in words.

Code Context:
{context}

User Question: {query}

Provide a clear, friendly explanation that anyone can understand.""",
                
                "dependency_check": f"""Analyze dependencies:
{context}

User query: {query}""",
                
                "general": f"""You are a helpful assistant with knowledge of this codebase.

Answer the user's question clearly and concisely. Use the provided context to give accurate information.

Guidelines:
- Provide direct, clear answers
- Use plain language when possible
- If the question is about architecture or design decisions, explain the reasoning
- Reference specific files or code when relevant
- If you don't have enough context to answer fully, say so

Code Context:
{context}

User Question: {query}

Provide a helpful, informative answer."""
            }
            
            prompt = prompts.get(task, prompts["general"])
            
            # Call Claude
            message = await asyncio.to_thread(
                self.claude_client.messages.create,
                model=settings.CLAUDE_MODEL,
                max_tokens=settings.CLAUDE_MAX_TOKENS,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Claude API call failed: {str(e)}")
            return f"I encountered an error analyzing this query. Please try again."
    
    async def analyze_bug(
        self,
        description: str,
        stack_trace: Optional[str] = None,
        affected_files: Optional[list] = None
    ) -> Dict:
        """Direct bug analysis endpoint"""
        message = f"{description}\n\n{stack_trace or ''}"
        return await self.process_query(message)
    
    async def process_query_stream(self, message: str, conversation_id: str):
        """Streaming version (for future implementation)"""
        # For now, just yield the complete response
        result = await self.process_query(message, conversation_id)
        yield result['response']
