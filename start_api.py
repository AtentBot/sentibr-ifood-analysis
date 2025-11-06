#!/usr/bin/env python3
"""
Startup script for Sentiment Analysis API
Handles initialization, validation, and server startup
"""
import sys
import os
from pathlib import Path
import logging
import argparse

# Get project root (where this script is located)
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_model():
    """Check if model exists"""
    # Try common model locations
    possible_paths = [
        PROJECT_ROOT / "models" / "bert_finetuned",
        PROJECT_ROOT / "model",
        Path("models/bert_finetuned"),
        Path("../models/bert_finetuned"),
    ]
    
    model_path = None
    for path in possible_paths:
        if path.exists():
            model_path = path
            break
    
    if not model_path:
        logger.warning("⚠️  Model not found in common locations:")
        for path in possible_paths:
            logger.warning(f"    - {path}")
        logger.warning("")
        logger.warning("Please ensure the model is trained and accessible.")
        logger.warning("The API will try to load the model from the path specified in .env")
        logger.warning("")
        return True  # Don't fail, let the API try to load
    
    required_files = ["config.json", "pytorch_model.bin", "tokenizer_config.json"]
    missing_files = [f for f in required_files if not (model_path / f).exists()]
    
    if missing_files:
        logger.warning(f"⚠️  Model files incomplete: {missing_files}")
        logger.warning("Model might not load correctly")
    
    logger.info(f"✅ Model found at {model_path}")
    return True


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'transformers',
        'torch',
        'pydantic'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.error(f"❌ Missing required packages: {', '.join(missing)}")
        logger.error("Install with: pip install -r requirements.txt")
        return False
    
    logger.info("✅ All dependencies installed")
    return True


def check_directories():
    """Create required directories"""
    directories = [
        PROJECT_ROOT / "logs",
        PROJECT_ROOT / "data" / "feedback"
    ]
    
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            logger.warning(f"⚠️  Cannot create {directory} (permission denied)")
            logger.warning("The API will try to create it at runtime")
    
    logger.info("✅ Directories ready")
    return True


def start_server(host="0.0.0.0", port=8000, reload=False, workers=1):
    """Start the FastAPI server"""
    import uvicorn
    
    logger.info(f"🚀 Starting Sentiment Analysis API...")
    logger.info(f"   Host: {host}")
    logger.info(f"   Port: {port}")
    logger.info(f"   Workers: {workers}")
    logger.info(f"   Reload: {reload}")
    logger.info(f"   Project Root: {PROJECT_ROOT}")
    logger.info(f"")
    logger.info(f"📡 API will be available at:")
    logger.info(f"   - Main: http://{host}:{port}")
    logger.info(f"   - Docs: http://{host}:{port}/docs")
    logger.info(f"   - ReDoc: http://{host}:{port}/redoc")
    logger.info(f"")
    logger.info(f"📊 Endpoints:")
    logger.info(f"   - Health: GET /health")
    logger.info(f"   - Predict: POST /api/v1/predict")
    logger.info(f"   - Batch: POST /api/v1/predict/batch")
    logger.info(f"   - Metrics: GET /api/v1/metrics")
    logger.info(f"")
    logger.info(f"Press CTRL+C to stop the server")
    logger.info(f"")
    
    try:
        uvicorn.run(
            "src.api.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down server...")
    except Exception as e:
        logger.error(f"❌ Server error: {str(e)}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Start Sentiment Analysis API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start with default settings
  python start_api.py
  
  # Start with hot reload (development)
  python start_api.py --reload
  
  # Start on specific port
  python start_api.py --port 8080
  
  # Start with multiple workers (production)
  python start_api.py --workers 4
        """
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to bind to (default: 8000)'
    )
    
    parser.add_argument(
        '--reload',
        action='store_true',
        help='Enable auto-reload on code changes (development only)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of worker processes (default: 1)'
    )
    
    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='Skip pre-flight checks'
    )
    
    args = parser.parse_args()
    
    logger.info("="*80)
    logger.info("🤖 SENTIMENT ANALYSIS API - STARTUP")
    logger.info("="*80)
    logger.info("")
    
    # Run pre-flight checks
    if not args.skip_checks:
        logger.info("🔍 Running pre-flight checks...")
        logger.info("")
        
        checks = [
            ("Dependencies", check_dependencies),
            ("Directories", check_directories),
            ("Model", check_model)
        ]
        
        for name, check_func in checks:
            if not check_func():
                logger.error(f"❌ {name} check failed")
                logger.info("")
                logger.info("💡 Tips:")
                logger.info("   - Install dependencies: pip install -r requirements.txt")
                logger.info("   - Train model first: python src/training/train.py")
                logger.info("   - Or skip checks: python start_api.py --skip-checks")
                sys.exit(1)
        
        logger.info("")
        logger.info("✅ All checks passed!")
        logger.info("")
    else:
        logger.warning("⚠️  Skipping pre-flight checks")
        logger.info("")
    
    # Start server
    start_server(
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1
    )


if __name__ == "__main__":
    main()
