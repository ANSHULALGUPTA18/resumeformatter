"""
Azure Application Insights Integration
Automatically tracks all user activities, performance, and errors
"""

import os
import logging
from functools import wraps
from flask import request, g
from typing import Dict, Optional

# Azure Application Insights imports
try:
    from opencensus.ext.azure.log_exporter import AzureLogHandler
    from opencensus.ext.flask.flask_middleware import FlaskMiddleware
    from opencensus.ext.azure.trace_exporter import AzureExporter
    from opencensus.trace.samplers import ProbabilitySampler
    INSIGHTS_AVAILABLE = True
except ImportError:
    INSIGHTS_AVAILABLE = False
    print("⚠️  Azure Application Insights packages not installed")


class InsightsTracker:
    """
    Wrapper for Azure Application Insights tracking.
    Handles initialization, logging, and custom event tracking.
    """

    def __init__(self, app=None):
        self.app = app
        self.connection_string = None
        self.logger = None
        self.enabled = False

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize Application Insights with Flask app."""
        self.app = app
        self.connection_string = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')

        if not self.connection_string:
            print("⚠️  Application Insights not configured (missing APPLICATIONINSIGHTS_CONNECTION_STRING)")
            print("💡 Add APPLICATIONINSIGHTS_CONNECTION_STRING to your .env file when ready")
            self.enabled = False
            return

        if not INSIGHTS_AVAILABLE:
            print("⚠️  Azure Application Insights packages not installed")
            print("💡 Run: pip install opencensus-ext-azure opencensus-ext-flask")
            self.enabled = False
            return

        try:
            # Initialize Flask middleware for automatic request tracking
            middleware = FlaskMiddleware(
                app,
                exporter=AzureExporter(connection_string=self.connection_string),
                sampler=ProbabilitySampler(rate=1.0),  # Track 100% of requests
            )

            # Initialize logging handler
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)

            # Add Azure handler
            azure_handler = AzureLogHandler(connection_string=self.connection_string)
            logger.addHandler(azure_handler)

            self.logger = logger
            self.enabled = True

            print("✅ Application Insights enabled - tracking active")
            print(f"📊 View analytics at: https://portal.azure.com")

        except Exception as e:
            print(f"❌ Failed to initialize Application Insights: {e}")
            self.enabled = False

    def track_event(self, event_name: str, properties: Optional[Dict] = None, measurements: Optional[Dict] = None):
        """
        Track a custom event with optional properties and measurements.

        Args:
            event_name: Name of the event (e.g., "template_selected", "output_generated")
            properties: Dictionary of string properties (e.g., {"user_id": "123", "template_name": "Florida"})
            measurements: Dictionary of numeric measurements (e.g., {"processing_time_ms": 1234, "files_count": 5})

        Example:
            tracker.track_event(
                "output_generated",
                properties={"user_id": "user@example.com", "template_id": "template-123"},
                measurements={"files_processed": 5, "processing_time_ms": 1234}
            )
        """
        if not self.enabled or not self.logger:
            return

        try:
            # Combine properties and measurements for logging
            log_data = {
                "custom_dimensions": properties or {},
                "custom_measurements": measurements or {}
            }

            self.logger.info(f"Event: {event_name}", extra=log_data)

        except Exception as e:
            print(f"⚠️  Failed to track event '{event_name}': {e}")

    def track_user_login(self, user_id: str, user_email: str, user_name: str = None):
        """Track user login event."""
        self.track_event(
            "user_login",
            properties={
                "user_id": user_id,
                "user_email": user_email,
                "user_name": user_name or "Unknown"
            }
        )

    def track_template_selection(self, user_id: str, template_id: str, template_name: str):
        """Track template selection."""
        self.track_event(
            "template_selected",
            properties={
                "user_id": user_id,
                "template_id": template_id,
                "template_name": template_name
            }
        )

    def track_resume_upload(self, user_id: str, file_count: int):
        """Track resume upload."""
        self.track_event(
            "resume_uploaded",
            properties={"user_id": user_id},
            measurements={"file_count": file_count}
        )

    def track_output_generated(
        self,
        user_id: str,
        template_id: str,
        template_name: str,
        input_count: int,
        output_count: int,
        processing_time_ms: float,
        success: bool = True
    ):
        """Track output generation (most important metric)."""
        self.track_event(
            "output_generated",
            properties={
                "user_id": user_id,
                "template_id": template_id,
                "template_name": template_name,
                "success": str(success)
            },
            measurements={
                "input_files": input_count,
                "output_files": output_count,
                "processing_time_ms": processing_time_ms
            }
        )

    def track_download(self, user_id: str, file_name: str):
        """Track file download."""
        self.track_event(
            "file_downloaded",
            properties={
                "user_id": user_id,
                "file_name": file_name
            }
        )

    def track_error(self, error_type: str, error_message: str, user_id: str = None):
        """Track application errors."""
        if not self.enabled or not self.logger:
            return

        try:
            properties = {
                "error_type": error_type,
                "error_message": error_message
            }
            if user_id:
                properties["user_id"] = user_id

            self.logger.error(f"Error: {error_type}", extra={"custom_dimensions": properties})

        except Exception as e:
            print(f"⚠️  Failed to track error: {e}")


# Global instance
_tracker_instance = None


def get_insights_tracker() -> InsightsTracker:
    """Get or create global InsightsTracker instance."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = InsightsTracker()
    return _tracker_instance


def track_route(event_name: str = None):
    """
    Decorator to automatically track Flask route calls.

    Usage:
        @app.route('/api/format')
        @track_route("format_resume")
        def format_resume():
            # Your code here
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            tracker = get_insights_tracker()

            # Auto-generate event name from function name if not provided
            evt_name = event_name or f"route_{f.__name__}"

            # Get user info from request if available
            user_id = getattr(g, 'user_id', None) or request.headers.get('X-User-Id', 'anonymous')

            # Track the route call
            tracker.track_event(
                evt_name,
                properties={
                    "user_id": user_id,
                    "method": request.method,
                    "path": request.path
                }
            )

            return f(*args, **kwargs)

        return decorated_function
    return decorator
