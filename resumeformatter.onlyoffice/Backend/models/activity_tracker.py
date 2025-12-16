"""
Activity Tracking Models and Database Schema
Implements Option C: Hybrid approach with activity logs and user statistics
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os

class ActivityTracker:
    """
    Tracks user activities and maintains statistics.
    Implements hybrid approach with detailed logs and aggregated stats.
    """

    def __init__(self, db_path: str = None):
        """Initialize the activity tracker with database connection."""
        if db_path is None:
            # Use analytics.db in the Backend directory
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'analytics.db')

        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Activity Logs Table - stores every user action
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                user_email TEXT NOT NULL,
                user_name TEXT,
                event_type TEXT NOT NULL,
                template_id TEXT,
                template_name TEXT,
                metadata TEXT,
                session_id TEXT,
                ip_address TEXT,
                success BOOLEAN DEFAULT 1,
                error_message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # User Statistics Table - aggregated counters per user
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_statistics (
                user_id TEXT PRIMARY KEY,
                user_email TEXT NOT NULL,
                user_name TEXT,
                total_templates_selected INTEGER DEFAULT 0,
                total_resumes_uploaded INTEGER DEFAULT 0,
                total_outputs_generated INTEGER DEFAULT 0,
                total_downloads INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                first_seen DATETIME,
                last_active DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Indexes for better query performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_activity_user_id
            ON activity_logs(user_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_activity_timestamp
            ON activity_logs(timestamp)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_activity_event_type
            ON activity_logs(event_type)
        ''')

        conn.commit()
        conn.close()

    def log_activity(
        self,
        user_id: str,
        user_email: str,
        event_type: str,
        user_name: str = None,
        template_id: str = None,
        template_name: str = None,
        metadata: Dict = None,
        session_id: str = None,
        ip_address: str = None,
        success: bool = True,
        error_message: str = None
    ) -> int:
        """
        Log a user activity.

        Event types:
        - login: User logged in
        - logout: User logged out
        - template_select: User selected a template
        - template_upload: User uploaded a new template
        - template_delete: User deleted a template
        - resume_upload: User uploaded resume(s)
        - output_generated: Resume formatting completed
        - download: User downloaded formatted resume
        - error: An error occurred

        Returns:
            int: Activity log ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Convert metadata dict to JSON string
        metadata_json = json.dumps(metadata) if metadata else None

        # Insert activity log
        cursor.execute('''
            INSERT INTO activity_logs (
                user_id, user_email, user_name, event_type,
                template_id, template_name, metadata,
                session_id, ip_address, success, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, user_email, user_name, event_type,
            template_id, template_name, metadata_json,
            session_id, ip_address, success, error_message
        ))

        activity_id = cursor.lastrowid

        # Update user statistics
        self._update_user_statistics(cursor, user_id, user_email, user_name, event_type)

        conn.commit()
        conn.close()

        return activity_id

    def _update_user_statistics(
        self,
        cursor,
        user_id: str,
        user_email: str,
        user_name: str,
        event_type: str
    ):
        """Update aggregated user statistics based on event type."""

        # Check if user exists in statistics
        cursor.execute(
            'SELECT user_id FROM user_statistics WHERE user_id = ?',
            (user_id,)
        )

        user_exists = cursor.fetchone() is not None

        if not user_exists:
            # Create new user statistics entry
            cursor.execute('''
                INSERT INTO user_statistics (
                    user_id, user_email, user_name,
                    first_seen, last_active
                ) VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (user_id, user_email, user_name))

        # Update counters based on event type
        update_field = None

        if event_type == 'template_select':
            update_field = 'total_templates_selected'
        elif event_type == 'resume_upload':
            update_field = 'total_resumes_uploaded'
        elif event_type == 'output_generated':
            update_field = 'total_outputs_generated'
        elif event_type == 'download':
            update_field = 'total_downloads'
        elif event_type == 'login':
            update_field = 'total_sessions'

        if update_field:
            cursor.execute(f'''
                UPDATE user_statistics
                SET {update_field} = {update_field} + 1,
                    last_active = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
        else:
            # Just update last_active for other events
            cursor.execute('''
                UPDATE user_statistics
                SET last_active = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))

    def get_user_statistics(self, user_id: str) -> Optional[Dict]:
        """Get aggregated statistics for a specific user."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM user_statistics WHERE user_id = ?
        ''', (user_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def get_user_activity_logs(
        self,
        user_id: str,
        limit: int = 100,
        event_type: str = None
    ) -> List[Dict]:
        """Get activity logs for a specific user."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if event_type:
            cursor.execute('''
                SELECT * FROM activity_logs
                WHERE user_id = ? AND event_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, event_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM activity_logs
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))

        rows = cursor.fetchall()
        conn.close()

        activities = []
        for row in rows:
            activity = dict(row)
            # Parse metadata JSON
            if activity.get('metadata'):
                try:
                    activity['metadata'] = json.loads(activity['metadata'])
                except:
                    pass
            activities.append(activity)

        return activities

    def get_all_users_statistics(
        self,
        limit: int = None,
        order_by: str = 'last_active DESC'
    ) -> List[Dict]:
        """Get statistics for all users (for admin dashboard)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = f'SELECT * FROM user_statistics ORDER BY {order_by}'
        if limit:
            query += f' LIMIT {limit}'

        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_analytics_overview(self, days: int = 30) -> Dict:
        """
        Get overview analytics for admin dashboard.

        Returns aggregated stats for the specified time period.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total users
        cursor.execute('SELECT COUNT(*) FROM user_statistics')
        total_users = cursor.fetchone()[0]

        # Active users (last 7 days)
        cursor.execute('''
            SELECT COUNT(*) FROM user_statistics
            WHERE last_active >= datetime('now', '-7 days')
        ''')
        active_users_7d = cursor.fetchone()[0]

        # Total outputs generated
        cursor.execute('SELECT SUM(total_outputs_generated) FROM user_statistics')
        total_outputs = cursor.fetchone()[0] or 0

        # Outputs in time period
        cursor.execute('''
            SELECT COUNT(*) FROM activity_logs
            WHERE event_type = 'output_generated'
            AND timestamp >= datetime('now', ? || ' days')
        ''', (f'-{days}',))
        outputs_period = cursor.fetchone()[0]

        # Most popular templates
        cursor.execute('''
            SELECT template_name, COUNT(*) as count
            FROM activity_logs
            WHERE event_type = 'output_generated'
            AND template_name IS NOT NULL
            AND timestamp >= datetime('now', ? || ' days')
            GROUP BY template_name
            ORDER BY count DESC
            LIMIT 5
        ''', (f'-{days}',))
        popular_templates = [
            {'name': row[0], 'count': row[1]}
            for row in cursor.fetchall()
        ]

        # Daily activity (last 30 days)
        cursor.execute('''
            SELECT
                DATE(timestamp) as date,
                COUNT(*) as activity_count
            FROM activity_logs
            WHERE timestamp >= datetime('now', '-30 days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        ''')
        daily_activity = [
            {'date': row[0], 'count': row[1]}
            for row in cursor.fetchall()
        ]

        conn.close()

        return {
            'total_users': total_users,
            'active_users_7d': active_users_7d,
            'total_outputs': total_outputs,
            'outputs_last_30d': outputs_period,
            'popular_templates': popular_templates,
            'daily_activity': daily_activity
        }

    def search_users(self, query: str) -> List[Dict]:
        """Search users by email or name."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM user_statistics
            WHERE user_email LIKE ? OR user_name LIKE ?
            ORDER BY last_active DESC
        ''', (f'%{query}%', f'%{query}%'))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]


# Global instance
_tracker_instance = None

def get_tracker() -> ActivityTracker:
    """Get or create global ActivityTracker instance."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = ActivityTracker()
    return _tracker_instance
