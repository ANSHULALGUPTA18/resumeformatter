"""
Application Insights Integration Example
This file shows how to integrate tracking into your Flask app.py

IMPORTANT: This is just an EXAMPLE. Your actual app.py already exists.
Use this as a reference to add tracking to your existing routes.
"""

from flask import Flask, request, jsonify
from utils.insights_tracker import InsightsTracker, get_insights_tracker
import time

# Initialize Flask app
app = Flask(__name__)

# Initialize Application Insights
tracker = InsightsTracker(app)


# ==============================================================================
# EXAMPLE 1: Track Template Selection
# ==============================================================================
@app.route('/api/templates/<template_id>/select', methods=['POST'])
def select_template(template_id):
    """Example of tracking template selection"""

    # Get user info (from Azure AD token or session)
    user_id = request.headers.get('X-User-Id', 'user@example.com')

    # Your existing business logic here...
    template_name = "Florida Resume Template"  # Get from database

    # 📊 TRACK THE EVENT
    tracker.track_template_selection(
        user_id=user_id,
        template_id=template_id,
        template_name=template_name
    )

    return jsonify({"success": True})


# ==============================================================================
# EXAMPLE 2: Track Resume Upload
# ==============================================================================
@app.route('/api/upload', methods=['POST'])
def upload_resumes():
    """Example of tracking resume uploads"""

    user_id = request.headers.get('X-User-Id', 'user@example.com')

    # Get uploaded files
    files = request.files.getlist('files')
    file_count = len(files)

    # Your existing business logic here...
    # Process files, save to storage, etc.

    # 📊 TRACK THE EVENT
    tracker.track_resume_upload(
        user_id=user_id,
        file_count=file_count
    )

    return jsonify({"success": True, "files_uploaded": file_count})


# ==============================================================================
# EXAMPLE 3: Track Output Generation (MOST IMPORTANT!)
# ==============================================================================
@app.route('/api/format', methods=['POST'])
def format_resumes():
    """Example of tracking output generation"""

    user_id = request.headers.get('X-User-Id', 'user@example.com')
    template_id = request.json.get('template_id')
    template_name = request.json.get('template_name')

    # Start timing
    start_time = time.time()

    try:
        # Your existing business logic here...
        # Format resumes, generate outputs, etc.
        input_files = 5  # Number of input resumes
        output_files = 5  # Number of formatted outputs

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # 📊 TRACK THE EVENT (Success case)
        tracker.track_output_generated(
            user_id=user_id,
            template_id=template_id,
            template_name=template_name,
            input_count=input_files,
            output_count=output_files,
            processing_time_ms=processing_time,
            success=True
        )

        return jsonify({
            "success": True,
            "outputs": output_files,
            "processing_time_ms": processing_time
        })

    except Exception as e:
        # Calculate processing time even on error
        processing_time = (time.time() - start_time) * 1000

        # 📊 TRACK THE EVENT (Failure case)
        tracker.track_output_generated(
            user_id=user_id,
            template_id=template_id,
            template_name=template_name,
            input_count=0,
            output_count=0,
            processing_time_ms=processing_time,
            success=False
        )

        # Track the error too
        tracker.track_error(
            error_type="format_error",
            error_message=str(e),
            user_id=user_id
        )

        return jsonify({"success": False, "error": str(e)}), 500


# ==============================================================================
# EXAMPLE 4: Track Downloads
# ==============================================================================
@app.route('/api/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Example of tracking file downloads"""

    user_id = request.headers.get('X-User-Id', 'user@example.com')

    # Your existing business logic here...
    file_name = f"formatted_resume_{file_id}.docx"

    # 📊 TRACK THE EVENT
    tracker.track_download(
        user_id=user_id,
        file_name=file_name
    )

    # Return the file...
    return jsonify({"success": True})


# ==============================================================================
# EXAMPLE 5: Track User Login
# ==============================================================================
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Example of tracking user login"""

    # Get user info from Azure AD token
    user_id = "user-id-from-token"
    user_email = "user@example.com"
    user_name = "John Doe"

    # Your existing authentication logic here...

    # 📊 TRACK THE EVENT
    tracker.track_user_login(
        user_id=user_id,
        user_email=user_email,
        user_name=user_name
    )

    return jsonify({"success": True})


# ==============================================================================
# EXAMPLE 6: Track Custom Events
# ==============================================================================
@app.route('/api/custom-action', methods=['POST'])
def custom_action():
    """Example of tracking any custom event"""

    user_id = request.headers.get('X-User-Id', 'user@example.com')

    # Your existing business logic here...

    # 📊 TRACK A CUSTOM EVENT
    tracker.track_event(
        event_name="custom_action_performed",
        properties={
            "user_id": user_id,
            "action_type": "export_pdf",
            "source": "web"
        },
        measurements={
            "execution_time_ms": 123.45,
            "items_processed": 10
        }
    )

    return jsonify({"success": True})


# ==============================================================================
# EXAMPLE 7: Track Errors
# ==============================================================================
@app.errorhandler(500)
def handle_500(error):
    """Example of tracking server errors"""

    user_id = request.headers.get('X-User-Id', 'unknown')

    # 📊 TRACK THE ERROR
    tracker.track_error(
        error_type="server_error",
        error_message=str(error),
        user_id=user_id
    )

    return jsonify({"error": "Internal server error"}), 500


# ==============================================================================
# QUICK INTEGRATION CHECKLIST
# ==============================================================================
"""
✅ 1. Install packages:
      pip install opencensus-ext-azure opencensus-ext-flask

✅ 2. Add to .env:
      APPLICATIONINSIGHTS_CONNECTION_STRING=your-connection-string

✅ 3. Import in app.py:
      from utils.insights_tracker import InsightsTracker

✅ 4. Initialize after creating Flask app:
      tracker = InsightsTracker(app)

✅ 5. Add tracking calls in your routes:
      - tracker.track_template_selection()
      - tracker.track_resume_upload()
      - tracker.track_output_generated()  ← Most important!
      - tracker.track_download()

✅ 6. Restart backend and test

✅ 7. View data in Azure Portal after 2-5 minutes
"""

# ==============================================================================
# WHERE TO ADD TRACKING IN YOUR ACTUAL APP.PY
# ==============================================================================
"""
Based on your app structure, add tracking in these places:

1. After Flask app initialization:
   from utils.insights_tracker import InsightsTracker
   tracker = InsightsTracker(app)

2. In your /api/format route (when resumes are formatted):
   tracker.track_output_generated(...)

3. In your /api/templates/<id> route (when template selected):
   tracker.track_template_selection(...)

4. In your download route (when users download results):
   tracker.track_download(...)

5. In your authentication callback (when users log in):
   tracker.track_user_login(...)

That's it! Application Insights will automatically track all HTTP requests,
performance, and errors. You just need to add these custom events for
business-specific tracking.
"""


if __name__ == '__main__':
    print("📊 Application Insights Example")
    print("=" * 50)
    print("This is just an example file showing how to integrate tracking.")
    print("Use this as a reference to add tracking to your actual app.py")
    print("=" * 50)

    # Test if insights is configured
    if tracker.enabled:
        print("✅ Application Insights is configured and ready!")
        print("📈 Data will appear in Azure Portal after 2-5 minutes")
    else:
        print("⚠️  Application Insights not configured yet")
        print("💡 Follow AZURE_INSIGHTS_SETUP.md to set it up")
