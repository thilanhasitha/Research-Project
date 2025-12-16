"""
Quick diagnostic script to check backend startup issues
Run this inside the container to see what's failing
"""
import sys

print("="*60)
print(" Backend Diagnostic Check")
print("="*60)

# Check 1: Python version
print("\n1. Python Version:")
print(f"   {sys.version}")

# Check 2: Import core dependencies
print("\n2. Checking Core Dependencies:")
dependencies = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("motor", "Motor (MongoDB async)"),
    ("pymongo", "PyMongo"),
    ("langchain", "LangChain"),
    ("langchain_community", "LangChain Community"),
    ("ollama", "Ollama"),
    ("pydantic", "Pydantic"),
    ("dotenv", "python-dotenv"),
]

failed_imports = []
for module, name in dependencies:
    try:
        __import__(module)
        print(f"    {name}")
    except ImportError as e:
        print(f"    {name}: {e}")
        failed_imports.append((module, name))

# Check 3: Environment variables
print("\n3. Environment Variables:")
import os
env_vars = ["MONGO_URI", "DB_NAME", "OLLAMA_HOST", "OLLAMA_MODEL"]
for var in env_vars:
    value = os.getenv(var)
    if value:
        # Mask password in MongoDB URI
        if "MONGO_URI" in var and "@" in value:
            masked = value.split("://")[0] + "://***:***@" + value.split("@")[1]
            print(f"    {var}: {masked}")
        else:
            print(f"    {var}: {value}")
    else:
        print(f"     {var}: Not set")

# Check 4: Try importing app components
print("\n4. Checking Application Components:")
components = [
    ("app.Database.mongo_client", "MongoClient"),
    ("app.llm.LLMFactory", "LLMFactory"),
    ("app.llm.client.ollama_client", "OllamaClient"),
    ("app.models.rss_model", "RSSNews model"),
    ("app.services.news.rss_service", "RSSService"),
    ("app.routes.rss_routes", "RSS routes"),
]

app_failures = []
for module, name in components:
    try:
        __import__(module)
        print(f"    {name}")
    except Exception as e:
        print(f"    {name}: {e}")
        app_failures.append((module, name, str(e)))

# Check 5: Try to import main app
print("\n5. Checking Main Application:")
try:
    from app.main import app as fastapi_app
    print(f"    FastAPI app imported successfully")
    print(f"    App title: {fastapi_app.title}")
except Exception as e:
    print(f"    Failed to import app: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*60)
if failed_imports or app_failures:
    print(" ISSUES FOUND")
    if failed_imports:
        print(f"\n Missing {len(failed_imports)} dependencies:")
        for module, name in failed_imports:
            print(f"   - {name} ({module})")
        print("\n   Fix: pip install -r requirements.txt")
    
    if app_failures:
        print(f"\n {len(app_failures)} app component(s) failed to load:")
        for module, name, error in app_failures:
            print(f"   - {name}: {error[:80]}")
else:
    print(" ALL CHECKS PASSED")
    print("\n   Your backend should be able to start!")
print("="*60)
