import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    TEMPLATE_FOLDER = os.path.join(UPLOAD_FOLDER, 'templates')
    RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, 'resumes')
    OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')
    DATABASE = os.path.join(BASE_DIR, 'templates.db')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'odt', 'rtf'}

    # OnlyOffice settings - Auto-detect environment
    # Check if running locally or in production
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    IS_LOCAL = FLASK_ENV != 'production'

    # Use local URLs for development, Azure URLs for production
    # IMPORTANT: For local Docker, use host.docker.internal so OnlyOffice container can reach Flask
    ONLYOFFICE_URL = "http://localhost:8080" if IS_LOCAL else "https://onlyoffice.reddesert-f6724e64.centralus.azurecontainerapps.io"
    BACKEND_URL = "http://host.docker.internal:5000" if IS_LOCAL else "https://resume-formatter.reddesert-f6724e64.centralus.azurecontainerapps.io"

    # Performance settings
    USE_ML_PARSER = True  # Set to True for better accuracy, False for faster processing
    PARALLEL_WORKERS = 4  # Number of parallel resume processing threads
    
    # ML Model Optimization
    CACHE_ML_MODELS = True  # Cache ML models in memory (faster but uses more RAM)
    USE_LIGHTWEIGHT_MODEL = True  # Use faster, smaller ML model
    BATCH_ENCODE = True  # Encode multiple texts at once (faster)
    MAX_TEXT_LENGTH = 512  # Limit text length for ML processing (faster)
    ENABLE_GPU = False  # Use GPU if available (set to True if you have CUDA)
    
    @staticmethod
    def init_app(app):
        for folder in [Config.TEMPLATE_FOLDER, Config.RESUME_FOLDER, Config.OUTPUT_FOLDER]:
            os.makedirs(folder, exist_ok=True)
