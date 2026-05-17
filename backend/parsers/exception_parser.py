"""
Exception Parser - Stack Trace Analysis
Parses exception logs and extracts structured information
"""

import re
import logging
from typing import Dict, List

from models.schemas import ExceptionData

logger = logging.getLogger(__name__)


class ExceptionParser:
    """Parse and analyze exception logs"""
    
    def __init__(self):
        pass
    
    async def parse_exception(self, message: str) -> ExceptionData:
        """Parse exception from message"""
        try:
            exception_data = ExceptionData(
                has_exception=False,
                exception_type=None,
                exception_message=None,
                stack_trace=[],
                files_involved=[],
                functions_involved=[],
                line_numbers={},
                time_context=[],
                affected_users=[]
            )
            
            # Check if message contains exception
            if not self._has_exception(message):
                return exception_data
            
            exception_data.has_exception = True
            
            # Extract exception type and message
            exc_type, exc_msg = self._extract_exception_info(message)
            exception_data.exception_type = exc_type
            exception_data.exception_message = exc_msg
            
            # Parse stack trace
            stack_frames = self._parse_stack_trace(message)
            exception_data.stack_trace = stack_frames
            
            # Extract files and functions
            for frame in stack_frames:
                if frame.get("filename"):
                    exception_data.files_involved.append(frame["filename"])
                if frame.get("function"):
                    exception_data.functions_involved.append(frame["function"])
                if frame.get("filename") and frame.get("line_number"):
                    exception_data.line_numbers[frame["filename"]] = frame["line_number"]
            
            # Remove duplicates
            exception_data.files_involved = list(set(exception_data.files_involved))
            exception_data.functions_involved = list(set(exception_data.functions_involved))
            
            # Extract time context
            exception_data.time_context = self._extract_time_context(message)
            
            # Extract affected users
            exception_data.affected_users = self._extract_affected_users(message)
            
            return exception_data
            
        except Exception as e:
            logger.error(f"Exception parsing failed: {str(e)}")
            return ExceptionData(has_exception=False)
    
    def _has_exception(self, message: str) -> bool:
        """Check if message contains an exception"""
        patterns = [
            r'Traceback \(most recent call last\)',
            r'\w+(Error|Exception):',
            r'at \w+\.\w+\([^)]+\)',  # JavaScript stack traces
            r'^\s*File "[^"]+", line \d+',
        ]
        
        for pattern in patterns:
            if re.search(pattern, message, re.MULTILINE):
                return True
        
        return False
    
    def _extract_exception_info(self, message: str) -> tuple:
        """Extract exception type and message"""
        # Python exceptions
        error_pattern = r'(\w+(?:Error|Exception)):\s*(.+?)(?:\n|$)'
        match = re.search(error_pattern, message)
        
        if match:
            return match.group(1), match.group(2).strip()
        
        # Java exceptions
        java_pattern = r'(\w+(?:Exception)):\s*(.+?)(?:\n|$)'
        match = re.search(java_pattern, message)
        
        if match:
            return match.group(1), match.group(2).strip()
        
        return None, None
    
    def _parse_stack_trace(self, message: str) -> List[Dict]:
        """Parse stack trace frames"""
        frames = []
        
        # Python stack trace pattern
        # File "/path/to/file.py", line 123, in function_name
        py_pattern = r'File "([^"]+)",\s*line\s*(\d+),\s*in\s*(\w+)'
        
        for match in re.finditer(py_pattern, message):
            filepath = match.group(1)
            line_number = int(match.group(2))
            function_name = match.group(3)
            
            # Extract filename from path
            filename = filepath.split('/')[-1]
            
            frames.append({
                'filepath': filepath,
                'filename': filename,
                'line_number': line_number,
                'function': function_name
            })
        
        # JavaScript stack trace pattern
        # at functionName (file.js:123:45)
        js_pattern = r'at\s+(\w+)\s+\(([^:]+):(\d+):\d+\)'
        
        for match in re.finditer(js_pattern, message):
            function_name = match.group(1)
            filepath = match.group(2)
            line_number = int(match.group(3))
            
            filename = filepath.split('/')[-1]
            
            frames.append({
                'filepath': filepath,
                'filename': filename,
                'line_number': line_number,
                'function': function_name
            })
        
        return frames
    
    def _extract_time_context(self, message: str) -> List[str]:
        """Extract time-related context"""
        time_patterns = [
            r'\b(yesterday|today|tonight|this morning)\b',
            r'\b(last (week|month|night|hour))\b',
            r'\b(after|since|before)\s+(deployment|release|update|yesterday)\b',
            r'\b(\d{4}-\d{2}-\d{2})\b',  # Dates
            r'\b(\d{1,2}:\d{2}\s*(?:AM|PM)?)\b',  # Times
        ]
        
        time_context = []
        
        for pattern in time_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    time_context.extend([m for m in matches[0] if m])
                else:
                    time_context.extend(matches)
        
        return list(set(time_context))
    
    def _extract_affected_users(self, message: str) -> List[str]:
        """Extract information about affected users"""
        user_patterns = [
            r'\b(mobile|web|ios|android|desktop|api)\s+users?\b',
            r'\b(all|some|many|few)\s+users?\b',
            r'\b(production|staging|dev)\s+users?\b',
        ]
        
        affected = []
        
        for pattern in user_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            affected.extend(matches)
        
        return list(set(affected))
    
    def extract_code_snippet(self, message: str) -> str:
        """Extract code snippet if present"""
        # Code in triple backticks
        code_pattern = r'```(?:\w+)?\n(.*?)\n```'
        match = re.search(code_pattern, message, re.DOTALL)
        
        if match:
            return match.group(1)
        
        # Code in single backticks (inline)
        inline_pattern = r'`([^`]+)`'
        match = re.search(inline_pattern, message)
        
        if match:
            return match.group(1)
        
        return None
