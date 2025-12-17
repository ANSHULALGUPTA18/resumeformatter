"""
Azure Monitor OpenTelemetry Integration
Supports Live Metrics, distributed tracing, and real-time monitoring
"""

import os
from typing import Dict, Optional
from flask import Flask, request

# Azure Monitor OpenTelemetry imports
try:
    from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter, AzureMonitorMetricExporter, AzureMonitorLogExporter
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    from opentelemetry.semconv.resource import ResourceAttributes
    MONITOR_AVAILABLE = True
except ImportError as e:
    MONITOR_AVAILABLE = False
    print(f"[WARN] Azure Monitor OpenTelemetry not available: {e}")


class AzureMonitorTracker:
    """
    Azure Monitor tracker using OpenTelemetry SDK.
    Supports Live Metrics and real-time monitoring.
    """

    def __init__(self, app=None):
        self.app = app
        self.connection_string = None
        self.enabled = False
        self.tracer = None
        self.meter = None

        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize Azure Monitor with Flask app."""
        self.app = app
        self.connection_string = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')

        if not self.connection_string:
            print("[WARN] Application Insights not configured (missing APPLICATIONINSIGHTS_CONNECTION_STRING)")
            self.enabled = False
            return

        if not MONITOR_AVAILABLE:
            print("[WARN] Azure Monitor OpenTelemetry packages not installed")
            print("[INFO] Run: pip install azure-monitor-opentelemetry-exporter opentelemetry-instrumentation-flask")
            self.enabled = False
            return

        try:
            # Create resource with service information
            resource = Resource.create({
                ResourceAttributes.SERVICE_NAME: "resume-formatter-backend",
                ResourceAttributes.SERVICE_VERSION: "1.0.0",
            })

            # Set up tracing (for requests and dependencies)
            trace_exporter = AzureMonitorTraceExporter(connection_string=self.connection_string)
            tracer_provider = TracerProvider(resource=resource)
            tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
            trace.set_tracer_provider(tracer_provider)
            self.tracer = trace.get_tracer(__name__)

            # Set up metrics (for performance counters)
            metric_reader = PeriodicExportingMetricReader(
                AzureMonitorMetricExporter(connection_string=self.connection_string),
                export_interval_millis=5000  # Export every 5 seconds for Live Metrics
            )
            meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
            metrics.set_meter_provider(meter_provider)
            self.meter = metrics.get_meter(__name__)

            # Create custom metrics
            self.output_counter = self.meter.create_counter(
                "resume.outputs.generated",
                description="Number of resume outputs generated"
            )

            self.processing_time = self.meter.create_histogram(
                "resume.processing.time",
                unit="ms",
                description="Resume processing time in milliseconds"
            )

            # Instrument Flask automatically (this enables Live Metrics)
            FlaskInstrumentor().instrument_app(app)

            self.enabled = True
            print("[OK] Azure Monitor OpenTelemetry enabled - Live Metrics active")
            print("[INFO] View Live Metrics at: https://portal.azure.com")

        except Exception as e:
            print(f"[ERROR] Failed to initialize Azure Monitor: {e}")
            import traceback
            traceback.print_exc()
            self.enabled = False

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
        """Track output generation event."""
        if not self.enabled:
            return

        try:
            # Create a span for this operation
            with self.tracer.start_as_current_span("output_generated") as span:
                # Add attributes to the span
                span.set_attribute("user_id", user_id)
                span.set_attribute("template_id", template_id)
                span.set_attribute("template_name", template_name)
                span.set_attribute("input_files", input_count)
                span.set_attribute("output_files", output_count)
                span.set_attribute("success", success)

                # Record metrics
                self.output_counter.add(
                    output_count,
                    {
                        "user_id": user_id,
                        "template_name": template_name,
                        "success": str(success)
                    }
                )

                self.processing_time.record(
                    processing_time_ms,
                    {
                        "template_name": template_name,
                        "file_count": str(input_count)
                    }
                )

        except Exception as e:
            print(f"[WARN] Failed to track event: {e}")

    def track_event(self, event_name: str, properties: Optional[Dict] = None, measurements: Optional[Dict] = None):
        """Track a custom event."""
        if not self.enabled:
            return

        try:
            with self.tracer.start_as_current_span(event_name) as span:
                if properties:
                    for key, value in properties.items():
                        span.set_attribute(key, str(value))

                if measurements:
                    for key, value in measurements.items():
                        span.set_attribute(f"measurement.{key}", float(value))

        except Exception as e:
            print(f"[WARN] Failed to track event '{event_name}': {e}")


# Global instance
_tracker_instance = None


def get_monitor_tracker() -> AzureMonitorTracker:
    """Get or create global AzureMonitorTracker instance."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = AzureMonitorTracker()
    return _tracker_instance
