"""
Git Analyzer - Repository History and Blame
Uses PostgreSQL for commit data and GitPython for operations
"""

import git
from git import Repo
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import asyncio

from config import settings

logger = logging.getLogger(__name__)


class GitAnalyzer:
    """Git repository analysis and history tracking"""
    
    def __init__(self):
        self.repo = None
        self.db_conn = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize git repo and database connection"""
        try:
            logger.info("Initializing Git Analyzer...")
            
            # Connect to PostgreSQL
            self.db_conn = psycopg2.connect(settings.DATABASE_URL)
            
            # Create tables if not exist
            await self._create_tables()
            
            # Initialize git repository
            if Path(settings.REPO_PATH).exists():
                self.repo = Repo(settings.REPO_PATH)
                logger.info(f"Git repo loaded: {settings.REPO_PATH}")
            else:
                logger.warning(f"Repository not found at {settings.REPO_PATH}")
            
            self.initialized = True
            logger.info("✅ Git Analyzer initialized")
            
        except Exception as e:
            logger.error(f"Git Analyzer init failed: {str(e)}")
            raise
    
    async def _create_tables(self):
        """Create database tables for git data"""
        with self.db_conn.cursor() as cur:
            # Commits table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS commits (
                    sha VARCHAR(40) PRIMARY KEY,
                    author_name VARCHAR(255),
                    author_email VARCHAR(255),
                    commit_date TIMESTAMP,
                    message TEXT,
                    files_changed INTEGER DEFAULT 0,
                    insertions INTEGER DEFAULT 0,
                    deletions INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # File changes table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS file_changes (
                    id SERIAL PRIMARY KEY,
                    commit_sha VARCHAR(40) REFERENCES commits(sha),
                    filepath VARCHAR(500),
                    change_type VARCHAR(20),
                    insertions INTEGER DEFAULT 0,
                    deletions INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Indexes
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_commits_date 
                ON commits(commit_date DESC)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_changes_path 
                ON file_changes(filepath)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_changes_commit 
                ON file_changes(commit_sha)
            """)
            
            self.db_conn.commit()
    
    async def sync_repository(self):
        """Pull latest changes from remote"""
        if not self.repo:
            logger.warning("No repository to sync")
            return
        
        try:
            logger.info("Syncing repository...")
            origin = self.repo.remotes.origin
            await asyncio.to_thread(origin.pull)
            logger.info("✅ Repository synced")
        except Exception as e:
            logger.error(f"Sync failed: {str(e)}")
    
    async def sync_commits(self):
        """Sync all commits to database"""
        if not self.repo:
            logger.warning("No repository available")
            return
        
        try:
            logger.info("Syncing commits to database...")
            
            commits = list(self.repo.iter_commits(settings.GIT_BRANCH))
            logger.info(f"Processing {len(commits)} commits...")
            
            with self.db_conn.cursor() as cur:
                for commit in commits:
                    # Check if already exists
                    cur.execute(
                        "SELECT sha FROM commits WHERE sha = %s",
                        (commit.hexsha,)
                    )
                    
                    if cur.fetchone():
                        continue
                    
                    # Insert commit
                    cur.execute("""
                        INSERT INTO commits 
                        (sha, author_name, author_email, commit_date, message, files_changed)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (sha) DO NOTHING
                    """, (
                        commit.hexsha,
                        commit.author.name,
                        commit.author.email,
                        datetime.fromtimestamp(commit.committed_date),
                        commit.message,
                        len(commit.stats.files)
                    ))
                    
                    # Insert file changes
                    for filepath, stats in commit.stats.files.items():
                        cur.execute("""
                            INSERT INTO file_changes
                            (commit_sha, filepath, change_type, insertions, deletions)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            commit.hexsha,
                            filepath,
                            'modified',
                            stats.get('insertions', 0),
                            stats.get('deletions', 0)
                        ))
                
                self.db_conn.commit()
            
            logger.info("✅ Commits synced to database")
            
        except Exception as e:
            logger.error(f"Commit sync failed: {str(e)}")
            self.db_conn.rollback()
    
    async def get_file_history(
        self,
        filepath: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get commit history for a specific file"""
        try:
            with self.db_conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        c.sha,
                        c.author_name,
                        c.author_email,
                        c.commit_date,
                        c.message,
                        fc.insertions,
                        fc.deletions
                    FROM file_changes fc
                    JOIN commits c ON fc.commit_sha = c.sha
                    WHERE fc.filepath LIKE %s
                    ORDER BY c.commit_date DESC
                    LIMIT %s
                """, (f"%{filepath}%", limit))
                
                return [dict(row) for row in cur.fetchall()]
        
        except Exception as e:
            logger.error(f"Error getting file history: {str(e)}")
            return []
    
    async def get_blame_info(
        self,
        filepath: str,
        line_number: int
    ) -> Optional[Dict]:
        """Get git blame for specific line"""
        if not self.repo:
            return None
        
        try:
            # Get blame information
            blame_list = await asyncio.to_thread(
                self.repo.blame,
                'HEAD',
                filepath
            )
            
            # Find the commit for the line
            current_line = 1
            for commit, lines in blame_list:
                if current_line <= line_number < current_line + len(lines):
                    return {
                        'author': commit.author.name,
                        'email': commit.author.email,
                        'date': datetime.fromtimestamp(commit.committed_date),
                        'sha': commit.hexsha,
                        'message': commit.message.split('\n')[0]
                    }
                current_line += len(lines)
            
            return None
            
        except Exception as e:
            logger.error(f"Blame error: {str(e)}")
            return None
    
    async def get_recent_commits(self, limit: int = 10) -> List[Dict]:
        """Get recent commits"""
        try:
            with self.db_conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        sha,
                        author_name,
                        author_email,
                        commit_date,
                        message,
                        files_changed
                    FROM commits
                    ORDER BY commit_date DESC
                    LIMIT %s
                """, (limit,))
                
                return [dict(row) for row in cur.fetchall()]
        
        except Exception as e:
            logger.error(f"Error getting recent commits: {str(e)}")
            return []
    
    async def get_repository_status(self) -> Dict:
        """Get current repository status"""
        try:
            if not self.repo:
                return {
                    'total_commits': 0,
                    'current_branch': 'unknown',
                    'latest_commit': 'unknown',
                    'total_files': 0,
                    'indexed_files': 0,
                    'last_sync': None,
                    'is_syncing': False
                }
            
            # Get commit count
            with self.db_conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM commits")
                total_commits = cur.fetchone()[0]
            
            # Get latest commit
            latest_commit = self.repo.head.commit
            
            # Count all text/code files (excluding binary and common build artifacts)
            binary_extensions = {'.pyc', '.pyo', '.so', '.dll', '.exe', '.bin', '.class',
                               '.jar', '.war', '.zip', '.tar', '.gz', '.png', '.jpg', '.gif'}
            exclude_patterns = settings.EXCLUDE_PATTERNS

            total_files = 0
            for filepath in Path(settings.REPO_PATH).rglob("*"):
                if filepath.is_file():
                    # Skip excluded directories
                    if any(pattern in str(filepath) for pattern in exclude_patterns):
                        continue
                    # Skip binary files
                    if filepath.suffix.lower() in binary_extensions:
                        continue
                    total_files += 1

            return {
                'total_commits': total_commits,
                'current_branch': self.repo.active_branch.name,
                'latest_commit': latest_commit.hexsha[:8],
                'total_files': total_files,
                'indexed_files': total_files,  # All found files are considered indexed
                'last_sync': datetime.now(),
                'is_syncing': False
            }
        
        except Exception as e:
            logger.error(f"Error getting repo status: {str(e)}")
            return {}
    
    async def search_commits(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict]:
        """Search commits by message or author"""
        try:
            with self.db_conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        sha,
                        author_name,
                        author_email,
                        commit_date,
                        message
                    FROM commits
                    WHERE message ILIKE %s 
                       OR author_name ILIKE %s
                    ORDER BY commit_date DESC
                    LIMIT %s
                """, (f"%{query}%", f"%{query}%", limit))
                
                return [dict(row) for row in cur.fetchall()]
        
        except Exception as e:
            logger.error(f"Error searching commits: {str(e)}")
            return []
    
    async def health_check(self) -> bool:
        """Check if git analyzer is healthy"""
        try:
            if not self.initialized:
                return False
            
            # Test database connection
            with self.db_conn.cursor() as cur:
                cur.execute("SELECT 1")
            
            return True
        
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    async def close(self):
        """Cleanup resources"""
        if self.db_conn:
            self.db_conn.close()
        logger.info("Git Analyzer closed")
