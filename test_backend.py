#!/usr/bin/env python3
"""Test script to verify backend functionality"""

import sys
import os
import subprocess

def test_imports():
    """Test if all required Python packages are available"""
    print("Testing Python imports...")
    missing_packages = []
    
    required_packages = [
        'flask',
        'flask_socketio',
        'flask_cors',
        'flask_sqlalchemy',
        'flask_login',
        'flask_bcrypt',
        'psycopg2',
        'sqlalchemy',
        'redis',
        'celery',
        'transformers',
        'torch',
        'peft',
        'numpy',
        'eventlet'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package}: {e}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("\nInstall missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All Python packages are installed!")
    return True

def test_backend_modules():
    """Test if backend modules can be imported"""
    print("\nTesting backend modules...")
    
    # Add backend to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    
    modules_to_test = [
        'config',
        'database',
        'models.judge',
        'models.responder',
        'game_engine',
        'prompts.room_prompts',
        'style_cloaks'
    ]
    
    failed_modules = []
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            failed_modules.append(module)
    
    if failed_modules:
        print(f"\n❌ Failed to import: {', '.join(failed_modules)}")
        return False
    
    print("✅ All backend modules can be imported!")
    return True

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        from config import Config
        from sqlalchemy import create_engine
        
        # Try to connect
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        connection = engine.connect()
        connection.close()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nMake sure PostgreSQL is running:")
        print("  docker-compose up -d postgres")
        return False

def test_redis_connection():
    """Test Redis connection"""
    print("\nTesting Redis connection...")
    
    try:
        import redis
        from config import Config
        
        r = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB,
            password=Config.REDIS_PASSWORD
        )
        r.ping()
        print("✅ Redis connection successful!")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("\nMake sure Redis is running:")
        print("  docker-compose up -d redis")
        return False

def check_models_directory():
    """Check if models directory exists"""
    print("\nChecking models directory...")
    
    models_dir = os.path.join(os.path.dirname(__file__), 'backend', 'models')
    if os.path.exists(models_dir):
        print(f"✅ Models directory exists: {models_dir}")
        return True
    else:
        print(f"❌ Models directory not found: {models_dir}")
        os.makedirs(models_dir, exist_ok=True)
        print(f"✅ Created models directory: {models_dir}")
        return True

def main():
    print("=" * 50)
    print("REVERSE TURING GAME - BACKEND TEST")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run tests
    if not test_imports():
        all_tests_passed = False
    
    if not test_backend_modules():
        all_tests_passed = False
    
    if not check_models_directory():
        all_tests_passed = False
    
    # Optional tests (won't fail the overall test)
    print("\n" + "=" * 50)
    print("OPTIONAL SERVICES (not required for basic testing)")
    print("=" * 50)
    
    test_database_connection()
    test_redis_connection()
    
    # Summary
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✅ BACKEND TESTS PASSED!")
        print("\nTo start the backend:")
        print("  cd backend")
        print("  python app.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please fix the issues above before running the backend.")
    print("=" * 50)

if __name__ == "__main__":
    main()