"""
Initialize Knowledge Base Directories
======================================
Creates necessary directories for the knowledge base system
"""

from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def create_directory(path: Path, description: str):
    """Create a directory and log the result"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ {description}: {path.absolute()}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create {description}: {e}")
        return False


def main():
    """Initialize all required directories"""
    print("\n" + "="*60)
    print("Initializing Knowledge Base Directories")
    print("="*60 + "\n")
    
    base_dir = Path(__file__).parent
    
    directories = [
        (base_dir / "data" / "knowledge_base", "Knowledge base storage"),
        (base_dir / "data" / "uploads", "PDF uploads directory"),
        (base_dir / "logs", "Logs directory"),
    ]
    
    success_count = 0
    for dir_path, description in directories:
        if create_directory(dir_path, description):
            success_count += 1
    
    print(f"\n{success_count}/{len(directories)} directories created successfully")
    
    # Create a README in uploads directory
    readme_path = base_dir / "data" / "uploads" / "README.md"
    if not readme_path.exists():
        try:
            with open(readme_path, 'w') as f:
                f.write("""# PDF Uploads Directory

Place your PDF files here for knowledge base processing.

## Supported Files
- CSE Annual Report 2024
- Other financial documents

## Usage
1. Place your PDF file in this directory
2. Run: `python setup_knowledge_base.py`
3. The system will automatically detect and process the PDF

## File Naming
Supported filenames:
- Annual-Report-2024.pdf
- CSE_Annual_Report_2024.pdf
- Any filename ending in .pdf (you'll be prompted to select)
""")
            logger.info(f"✅ Created README in uploads directory")
        except Exception as e:
            logger.warning(f"⚠️  Could not create README: {e}")
    
    print("\n" + "="*60)
    print("Initialization Complete!")
    print("="*60)
    print("\nNext Steps:")
    print("  1. Place your PDF in: data/uploads/")
    print("  2. Run: python validate_knowledge_base.py")
    print("  3. Run: python setup_knowledge_base.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
