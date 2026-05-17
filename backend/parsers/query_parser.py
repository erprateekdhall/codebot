"""
Query Parser - Intent Detection and Entity Extraction
Analyzes user queries to determine what they're asking for
"""

import re
import logging
from typing import Dict, List
from enum import Enum

from models.schemas import QueryIntent, ParsedQuery

logger = logging.getLogger(__name__)


class QueryParser:
    """Parse and classify user queries"""
    
    def __init__(self):
        # Define patterns for each intent
        self.intent_patterns = {
            QueryIntent.BUG_ANALYSIS: [
                r'\b(bug|error|issue|fail|crash|broken|not working|exception)\b',
                r'\b(traceback|stack trace|ValueError|TypeError|Exception)\b',
                r'\b(why.*not|why.*fail|what.*wrong|what.*happening)\b',
                r'\b(fix|debug|solve|resolve)\b',
            ],
            QueryIntent.CODE_SEARCH: [
                r'\b(find|search|locate|where is|show me)\b.*\b(function|class|method|code)\b',
                r'\b(get me|give me)\b.*\b(code|implementation|function)\b',
                r'\b(which file|which module)\b',
            ],
            QueryIntent.AUTHOR_LOOKUP: [
                r'\b(who wrote|who created|who modified|who changed|who made)\b',
                r'\b(author|committer|developer|programmer)\b.*\b(of|for)\b',
                r'\b(last modified by|last changed by|written by)\b',
                r'\b(git blame|blame)\b',
            ],
            QueryIntent.CODE_EXPLANATION: [
                r'\b(explain|how does|what does|how works)\b',
                r'\b(understand|clarify|describe|tell me about)\b',
                r'\b(walk me through|show me how)\b',
                r'\b(what is|what are)\b.*\b(this|that)\b',
                r'\b(layman|simple|plain english|easy|beginner|non-technical)\b.*\b(term|language|way)\b',
                r'\b(in simple|in plain|in easy)\b',
                r'\b(logic|purpose|idea|concept)\b.*\b(behind|of)\b',
                r'\b(why)\b.*\b(used|needed|required|implemented|added|included)\b',
                r'\b(why)\b.*\b(project|codebase|application|system)\b',
            ],
            QueryIntent.DEPENDENCY_CHECK: [
                r'\b(depends on|dependency|dependencies)\b',
                r'\b(what uses|what calls|who calls|who uses)\b',
                r'\b(impact|affect|break)\b',
                r'\b(if I change|if I modify|if I delete|if I remove)\b',
                r'\b(call graph|dependency graph)\b',
            ],
        }
    
    async def parse(self, message: str) -> ParsedQuery:
        """Parse user query and extract information"""
        try:
            message_lower = message.lower()
            
            # Detect intent
            detected_intent = self._detect_intent(message_lower)
            
            # Extract entities
            entities = self._extract_entities(message)
            
            # Extract keywords
            keywords = self._extract_keywords(message_lower)
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                detected_intent,
                entities,
                keywords
            )
            
            return ParsedQuery(
                intent=detected_intent,
                entities=entities,
                keywords=keywords,
                original_message=message,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Query parsing failed: {str(e)}")
            # Return default
            return ParsedQuery(
                intent=QueryIntent.GENERAL_QUESTION,
                entities={},
                keywords=[],
                original_message=message,
                confidence=0.3
            )
    
    def _detect_intent(self, message: str) -> QueryIntent:
        """Detect query intent from message"""
        intent_scores = {}
        
        # Score each intent
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    score += 1
            intent_scores[intent] = score
        
        # Return intent with highest score
        if max(intent_scores.values()) > 0:
            return max(intent_scores, key=intent_scores.get)
        else:
            return QueryIntent.GENERAL_QUESTION
    
    def _extract_entities(self, message: str) -> Dict[str, List[str]]:
        """Extract entities from message"""
        entities = {
            "files": [],
            "functions": [],
            "classes": [],
            "errors": [],
            "variables": []
        }
        
        # Extract file references
        file_pattern = r'\b(\w+\.(py|js|java|go|ts|jsx|tsx))\b'
        entities["files"] = re.findall(file_pattern, message)
        entities["files"] = [f[0] for f in entities["files"]]
        
        # Extract function references (with parentheses)
        function_pattern = r'\b([a-z_][a-z0-9_]*)\(\)'
        entities["functions"] = re.findall(function_pattern, message, re.IGNORECASE)
        
        # Extract class references (capitalized words)
        class_pattern = r'\b([A-Z][a-zA-Z0-9]+)\b'
        entities["classes"] = re.findall(class_pattern, message)
        
        # Extract error messages in quotes
        error_pattern = r'["\']([^"\']+)["\']'
        entities["errors"] = re.findall(error_pattern, message)
        
        # Extract code in backticks
        code_pattern = r'`([^`]+)`'
        code_refs = re.findall(code_pattern, message)
        entities["variables"].extend(code_refs)
        
        return entities
    
    def _extract_keywords(self, message: str) -> List[str]:
        """Extract important keywords"""
        # Common stopwords to exclude
        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at',
            'to', 'for', 'of', 'and', 'or', 'but', 'not', 'with', 'by',
            'from', 'this', 'that', 'these', 'those', 'i', 'you', 'it',
            'can', 'could', 'would', 'should', 'will', 'do', 'does', 'did',
            'have', 'has', 'had', 'be', 'been', 'being', 'my', 'your', 'me'
        }
        
        # Extract words
        words = re.findall(r'\b\w+\b', message.lower())
        
        # Filter and return
        keywords = [
            w for w in words
            if w not in stopwords and len(w) > 2
        ]
        
        return keywords[:10]  # Top 10 keywords
    
    def _calculate_confidence(
        self,
        intent: QueryIntent,
        entities: Dict,
        keywords: List[str]
    ) -> float:
        """Calculate confidence score"""
        score = 0.5  # Base score
        
        # Higher confidence if we found specific entities
        if entities.get("files"):
            score += 0.15
        if entities.get("functions"):
            score += 0.15
        if entities.get("classes"):
            score += 0.1
        
        # Higher confidence if we have good keywords
        if len(keywords) >= 3:
            score += 0.1
        
        # Cap at 1.0
        return min(score, 1.0)
