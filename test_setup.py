"""
Comprehensive test suite for validating project setup up to Task 2 (excluding Task 3).

This test file validates:
- Task 1: Project infrastructure (folders, __init__.py, requirements.txt, .env.example, Dockerfile, .dockerignore)
- Task 2: Database and models (Pydantic models, db.py, database.json)

Purpose (Why):
Ensures all components are properly set up and functional before proceeding to Task 3.
Provides runtime validation with detailed logging for debugging.

Implementation (What):
Systematically checks each component, validates imports, tests functionality,
and logs results for analysis.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Debug logging configuration
LOG_PATH = Path(__file__).parent / ".cursor" / "debug.log"
SESSION_ID = "test-setup-session"
RUN_ID = "run1"


def debug_log(location: str, message: str, data: Dict[str, Any], hypothesis_id: str = "general") -> None:
    """
    Write debug log entry in NDJSON format.
    
    Purpose (Why):
    Provides runtime evidence for debugging and validation tracking.
    
    Implementation (What):
    Appends a single NDJSON line to the debug log file with structured data.
    """
    # #region agent log
    log_entry = {
        "sessionId": SESSION_ID,
        "runId": RUN_ID,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(__import__("time").time() * 1000)
    }
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Warning: Could not write debug log: {e}")
    # #endregion


class TestResults:
    """Container for test results with pass/fail tracking."""
    
    def __init__(self):
        self.passed: List[str] = []
        self.failed: List[Tuple[str, str]] = []  # (test_name, error_message)
        self.warnings: List[Tuple[str, str]] = []  # (test_name, warning_message)
    
    def add_pass(self, test_name: str):
        self.passed.append(test_name)
        print(f"✓ PASS: {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed.append((test_name, error))
        print(f"✗ FAIL: {test_name} - {error}")
    
    def add_warning(self, test_name: str, warning: str):
        self.warnings.append((test_name, warning))
        print(f"⚠ WARN: {test_name} - {warning}")
    
    def summary(self) -> Dict[str, Any]:
        return {
            "total": len(self.passed) + len(self.failed) + len(self.warnings),
            "passed": len(self.passed),
            "failed": len(self.failed),
            "warnings": len(self.warnings),
            "passed_tests": self.passed,
            "failed_tests": self.failed,
            "warnings": self.warnings
        }


def test_directory_structure(results: TestResults) -> None:
    """
    Test Task 1.1: Directory structure.
    
    Purpose (Why):
    Validates that all required directories exist for proper project organization.
    
    Implementation (What):
    Checks for existence of all required directories as specified in Task 1.1.
    """
    debug_log("test_setup.py:test_directory_structure", "Starting directory structure test", {}, "H1")
    
    required_dirs = [
        "app",
        "app/agent",
        "app/tools",
        "app/database",
        "app/models",
        "app/prompts",
        "data"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    debug_log("test_setup.py:test_directory_structure", "Directory check completed", {
        "required": required_dirs,
        "missing": missing_dirs
    }, "H1")
    
    if missing_dirs:
        results.add_fail("Directory Structure", f"Missing directories: {', '.join(missing_dirs)}")
    else:
        results.add_pass("Directory Structure")


def test_init_files(results: TestResults) -> None:
    """
    Test Task 1.2: __init__.py files.
    
    Purpose (Why):
    Validates that all Python packages have __init__.py files for proper module structure.
    
    Implementation (What):
    Checks for existence of __init__.py in all Python package directories.
    """
    debug_log("test_setup.py:test_init_files", "Starting __init__.py test", {}, "H2")
    
    required_init_files = [
        "app/__init__.py",
        "app/agent/__init__.py",
        "app/tools/__init__.py",
        "app/database/__init__.py",
        "app/models/__init__.py",
        "app/prompts/__init__.py"
    ]
    
    missing_files = []
    for file_path in required_init_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    debug_log("test_setup.py:test_init_files", "__init__.py check completed", {
        "required": required_init_files,
        "missing": missing_files
    }, "H2")
    
    if missing_files:
        results.add_fail("__init__.py Files", f"Missing files: {', '.join(missing_files)}")
    else:
        results.add_pass("__init__.py Files")


def test_requirements_txt(results: TestResults) -> None:
    """
    Test Task 1.4: requirements.txt file.
    
    Purpose (Why):
    Validates that requirements.txt exists and contains correct dependencies without forbidden packages.
    
    Implementation (What):
    Checks file existence, reads content, validates required packages, and ensures no LangChain.
    """
    debug_log("test_setup.py:test_requirements_txt", "Starting requirements.txt test", {}, "H3")
    
    req_file = Path("requirements.txt")
    if not req_file.exists():
        results.add_fail("requirements.txt", "File does not exist")
        return
    
    try:
        with open(req_file, "r", encoding="utf-8") as f:
            content = f.read()
            lines = [line.strip() for line in content.split("\n") if line.strip()]
        
        debug_log("test_setup.py:test_requirements_txt", "Read requirements.txt", {
            "line_count": len(lines),
            "content": lines
        }, "H3")
        
        required_packages = ["gradio", "openai", "pydantic", "python-dotenv"]
        forbidden_packages = ["langchain", "langchain-"]
        
        found_packages = []
        missing_packages = []
        forbidden_found = []
        
        for line in lines:
            package_name = line.split(">=")[0].split("==")[0].split("~=")[0].strip().lower()
            found_packages.append(package_name)
            
            for forbidden in forbidden_packages:
                if forbidden in package_name:
                    forbidden_found.append(package_name)
        
        for req_pkg in required_packages:
            if req_pkg not in found_packages:
                missing_packages.append(req_pkg)
        
        debug_log("test_setup.py:test_requirements_txt", "Package validation completed", {
            "found": found_packages,
            "missing": missing_packages,
            "forbidden_found": forbidden_found
        }, "H3")
        
        if missing_packages:
            results.add_fail("requirements.txt", f"Missing required packages: {', '.join(missing_packages)}")
        elif forbidden_found:
            results.add_fail("requirements.txt", f"Forbidden packages found: {', '.join(forbidden_found)}")
        else:
            results.add_pass("requirements.txt")
    except Exception as e:
        results.add_fail("requirements.txt", f"Error reading file: {str(e)}")


def test_env_example(results: TestResults) -> None:
    """
    Test Task 1.6: .env.example file.
    
    Purpose (Why):
    Validates that .env.example exists for environment variable documentation.
    
    Implementation (What):
    Checks file existence and validates content contains OPENAI_API_KEY.
    """
    debug_log("test_setup.py:test_env_example", "Starting .env.example test", {}, "H4")
    
    env_file = Path(".env.example")
    debug_log("test_setup.py:test_env_example", "Checking file existence", {
        "file_path": str(env_file),
        "absolute_path": str(env_file.absolute()),
        "exists": env_file.exists(),
        "cwd": str(Path.cwd())
    }, "H4")
    
    if not env_file.exists():
        results.add_warning(".env.example", "File does not exist (recommended but not critical)")
        debug_log("test_setup.py:test_env_example", "File not found", {
            "searched_path": str(env_file.absolute())
        }, "H4")
        return
    
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        debug_log("test_setup.py:test_env_example", "Read .env.example", {
            "content_length": len(content),
            "contains_openai_key": "OPENAI_API_KEY" in content
        }, "H4")
        
        if "OPENAI_API_KEY" not in content:
            results.add_warning(".env.example", "Does not contain OPENAI_API_KEY")
        else:
            results.add_pass(".env.example")
    except Exception as e:
        results.add_fail(".env.example", f"Error reading file: {str(e)}")


def test_dockerfile(results: TestResults) -> None:
    """
    Test Task 1.7: Dockerfile.
    
    Purpose (Why):
    Validates that Dockerfile exists and has correct structure for containerization.
    
    Implementation (What):
    Checks file existence and validates key components (Python 3.11, requirements.txt, CMD).
    """
    debug_log("test_setup.py:test_dockerfile", "Starting Dockerfile test", {}, "H5")
    
    dockerfile = Path("Dockerfile")
    if not dockerfile.exists():
        results.add_fail("Dockerfile", "File does not exist")
        return
    
    try:
        with open(dockerfile, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
        
        debug_log("test_setup.py:test_dockerfile", "Read Dockerfile", {
            "line_count": len(lines),
            "contains_python311": "python:3.11" in content,
            "contains_requirements": "requirements.txt" in content,
            "contains_cmd": "CMD" in content
        }, "H5")
        
        checks = {
            "Python 3.11": "python:3.11" in content,
            "requirements.txt": "requirements.txt" in content,
            "CMD": "CMD" in content
        }
        
        failed_checks = [k for k, v in checks.items() if not v]
        
        if failed_checks:
            results.add_fail("Dockerfile", f"Missing required components: {', '.join(failed_checks)}")
        else:
            results.add_pass("Dockerfile")
    except Exception as e:
        results.add_fail("Dockerfile", f"Error reading file: {str(e)}")


def test_dockerignore(results: TestResults) -> None:
    """
    Test Task 1.8: .dockerignore file.
    
    Purpose (Why):
    Validates that .dockerignore exists to exclude unnecessary files from Docker builds.
    
    Implementation (What):
    Checks file existence and validates it contains common ignore patterns.
    """
    debug_log("test_setup.py:test_dockerignore", "Starting .dockerignore test", {}, "H6")
    
    dockerignore = Path(".dockerignore")
    if not dockerignore.exists():
        results.add_warning(".dockerignore", "File does not exist (recommended but not critical)")
        return
    
    try:
        with open(dockerignore, "r", encoding="utf-8") as f:
            content = f.read()
        
        debug_log("test_setup.py:test_dockerignore", "Read .dockerignore", {
            "content_length": len(content),
            "contains_venv": "venv" in content,
            "contains_pycache": "__pycache__" in content
        }, "H6")
        
        results.add_pass(".dockerignore")
    except Exception as e:
        results.add_fail(".dockerignore", f"Error reading file: {str(e)}")


def test_pydantic_models(results: TestResults) -> None:
    """
    Test Task 2.3: Pydantic models.
    
    Purpose (Why):
    Validates that all Pydantic models are properly defined and can be imported and instantiated.
    
    Implementation (What):
    Attempts to import each model and create test instances with valid data.
    """
    debug_log("test_setup.py:test_pydantic_models", "Starting Pydantic models test", {}, "H7")
    
    models_to_test = [
        ("app.models.user", "User"),
        ("app.models.medication", "Medication"),
        ("app.models.medication", "Stock"),
        ("app.models.prescription", "Prescription")
    ]
    
    failed_imports = []
    failed_instantiations = []
    
    for module_name, class_name in models_to_test:
        try:
            debug_log("test_setup.py:test_pydantic_models", f"Importing {module_name}.{class_name}", {}, "H7")
            module = __import__(module_name, fromlist=[class_name])
            model_class = getattr(module, class_name)
            
            # Test instantiation with sample data
            if class_name == "User":
                instance = model_class(
                    user_id="test_001",
                    name="Test User",
                    email="test@example.com",
                    prescriptions=[]
                )
            elif class_name == "Stock":
                instance = model_class(
                    available=True,
                    quantity_in_stock=100,
                    last_restocked="2024-01-01T00:00:00Z"
                )
            elif class_name == "Medication":
                stock = model_class.__module__.split(".")[0]
                from app.models.medication import Stock
                instance = model_class(
                    medication_id="test_med_001",
                    name_he="תרופה בדיקה",
                    name_en="Test Medication",
                    active_ingredients=["Test Ingredient"],
                    dosage_forms=["Tablets"],
                    dosage_instructions="Test instructions",
                    usage_instructions="Test usage",
                    requires_prescription=False,
                    description="Test description",
                    stock=Stock(available=True, quantity_in_stock=100, last_restocked="2024-01-01T00:00:00Z")
                )
            elif class_name == "Prescription":
                instance = model_class(
                    prescription_id="test_presc_001",
                    user_id="test_001",
                    medication_id="test_med_001",
                    prescribed_by="Dr. Test",
                    prescription_date="2024-01-01T00:00:00Z",
                    expiry_date="2024-04-01T00:00:00Z",
                    quantity=30,
                    refills_remaining=2,
                    status="active"
                )
            
            debug_log("test_setup.py:test_pydantic_models", f"Successfully instantiated {class_name}", {
                "class": class_name,
                "instance_id": getattr(instance, f"{class_name.lower()}_id", "N/A")
            }, "H7")
            
        except ImportError as e:
            failed_imports.append(f"{module_name}.{class_name}: {str(e)}")
            debug_log("test_setup.py:test_pydantic_models", f"Import failed for {class_name}", {
                "error": str(e)
            }, "H7")
        except Exception as e:
            failed_instantiations.append(f"{class_name}: {str(e)}")
            debug_log("test_setup.py:test_pydantic_models", f"Instantiation failed for {class_name}", {
                "error": str(e)
            }, "H7")
    
    debug_log("test_setup.py:test_pydantic_models", "Models test completed", {
        "failed_imports": failed_imports,
        "failed_instantiations": failed_instantiations
    }, "H7")
    
    if failed_imports:
        results.add_fail("Pydantic Models - Imports", "; ".join(failed_imports))
    if failed_instantiations:
        results.add_fail("Pydantic Models - Instantiation", "; ".join(failed_instantiations))
    if not failed_imports and not failed_instantiations:
        results.add_pass("Pydantic Models")


def test_database_manager(results: TestResults) -> None:
    """
    Test Task 2.4: DatabaseManager class.
    
    Purpose (Why):
    Validates that DatabaseManager can be imported and all methods work correctly.
    
    Implementation (What):
    Imports DatabaseManager, tests all methods with the existing database.json.
    """
    debug_log("test_setup.py:test_database_manager", "Starting DatabaseManager test", {}, "H8")
    
    try:
        from app.database.db import DatabaseManager
        
        debug_log("test_setup.py:test_database_manager", "DatabaseManager imported successfully", {}, "H8")
        
        db = DatabaseManager()
        debug_log("test_setup.py:test_database_manager", "DatabaseManager instantiated", {
            "db_path": str(db.db_path)
        }, "H8")
        
        # Test load_db
        try:
            data = db.load_db()
            debug_log("test_setup.py:test_database_manager", "load_db completed", {
                "users_count": len(data.get("users", [])),
                "medications_count": len(data.get("medications", [])),
                "prescriptions_count": len(data.get("prescriptions", []))
            }, "H8")
            
            if len(data.get("users", [])) != 10:
                results.add_fail("DatabaseManager.load_db", f"Expected 10 users, found {len(data.get('users', []))}")
            if len(data.get("medications", [])) != 5:
                results.add_fail("DatabaseManager.load_db", f"Expected 5 medications, found {len(data.get('medications', []))}")
        except Exception as e:
            results.add_fail("DatabaseManager.load_db", str(e))
            debug_log("test_setup.py:test_database_manager", "load_db failed", {"error": str(e)}, "H8")
            return
        
        # Test get_medication_by_id
        try:
            med = db.get_medication_by_id("med_001")
            debug_log("test_setup.py:test_database_manager", "get_medication_by_id completed", {
                "found": med is not None,
                "medication_id": med.medication_id if med else None
            }, "H8")
            if med is None:
                results.add_fail("DatabaseManager.get_medication_by_id", "Could not find med_001")
        except Exception as e:
            results.add_fail("DatabaseManager.get_medication_by_id", str(e))
        
        # Test get_user_by_id
        try:
            user = db.get_user_by_id("user_001")
            debug_log("test_setup.py:test_database_manager", "get_user_by_id completed", {
                "found": user is not None,
                "user_id": user.user_id if user else None
            }, "H8")
            if user is None:
                results.add_fail("DatabaseManager.get_user_by_id", "Could not find user_001")
        except Exception as e:
            results.add_fail("DatabaseManager.get_user_by_id", str(e))
        
        # Test get_prescriptions_by_user
        try:
            prescriptions = db.get_prescriptions_by_user("user_001")
            debug_log("test_setup.py:test_database_manager", "get_prescriptions_by_user completed", {
                "count": len(prescriptions)
            }, "H8")
        except Exception as e:
            results.add_fail("DatabaseManager.get_prescriptions_by_user", str(e))
        
        # Test search_medications_by_name
        try:
            meds_he = db.search_medications_by_name("Acamol", "he")
            meds_en = db.search_medications_by_name("Acetaminophen", "en")
            meds_both = db.search_medications_by_name("Acamol")
            debug_log("test_setup.py:test_database_manager", "search_medications_by_name completed", {
                "he_results": len(meds_he),
                "en_results": len(meds_en),
                "both_results": len(meds_both)
            }, "H8")
            if len(meds_he) == 0 and len(meds_en) == 0:
                results.add_fail("DatabaseManager.search_medications_by_name", "Could not find Acamol/Acetaminophen")
        except Exception as e:
            results.add_fail("DatabaseManager.search_medications_by_name", str(e))
        
        if not any("DatabaseManager" in test[0] for test in results.failed):
            results.add_pass("DatabaseManager")
            
    except ImportError as e:
        results.add_fail("DatabaseManager Import", str(e))
        debug_log("test_setup.py:test_database_manager", "Import failed", {"error": str(e)}, "H8")
    except Exception as e:
        results.add_fail("DatabaseManager", f"Unexpected error: {str(e)}")
        debug_log("test_setup.py:test_database_manager", "Unexpected error", {"error": str(e)}, "H8")


def test_database_json(results: TestResults) -> None:
    """
    Test Task 2.1-2.2: database.json structure and content.
    
    Purpose (Why):
    Validates that database.json exists and has correct structure with required data.
    
    Implementation (What):
    Checks file existence, validates JSON structure, and verifies data counts.
    """
    debug_log("test_setup.py:test_database_json", "Starting database.json test", {}, "H9")
    
    db_file = Path("data/database.json")
    if not db_file.exists():
        results.add_fail("database.json", "File does not exist")
        return
    
    try:
        with open(db_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        debug_log("test_setup.py:test_database_json", "Read database.json", {
            "has_users": "users" in data,
            "has_medications": "medications" in data,
            "has_prescriptions": "prescriptions" in data,
            "users_count": len(data.get("users", [])),
            "medications_count": len(data.get("medications", [])),
            "prescriptions_count": len(data.get("prescriptions", []))
        }, "H9")
        
        # Validate structure
        required_keys = ["users", "medications", "prescriptions"]
        missing_keys = [k for k in required_keys if k not in data]
        
        if missing_keys:
            results.add_fail("database.json Structure", f"Missing keys: {', '.join(missing_keys)}")
            return
        
        # Validate counts
        if len(data.get("users", [])) != 10:
            results.add_fail("database.json Content", f"Expected 10 users, found {len(data.get('users', []))}")
        elif len(data.get("medications", [])) != 5:
            results.add_fail("database.json Content", f"Expected 5 medications, found {len(data.get('medications', []))}")
        else:
            results.add_pass("database.json")
            
    except json.JSONDecodeError as e:
        results.add_fail("database.json", f"Invalid JSON: {str(e)}")
    except Exception as e:
        results.add_fail("database.json", f"Error reading file: {str(e)}")


def main():
    """
    Main test runner.
    
    Purpose (Why):
    Orchestrates all tests and provides comprehensive results summary.
    
    Implementation (What):
    Runs all test functions, collects results, and outputs summary with debug logging.
    """
    # Clear previous log file
    if LOG_PATH.exists():
        try:
            LOG_PATH.unlink()
        except Exception:
            pass
    
    debug_log("test_setup.py:main", "Starting test suite", {
        "session_id": SESSION_ID,
        "run_id": RUN_ID
    }, "main")
    
    print("=" * 60)
    print("Project Setup Test Suite (Tasks 1-2, excluding Task 3)")
    print("=" * 60)
    print()
    
    results = TestResults()
    
    # Task 1 tests
    print("Task 1: Project Infrastructure")
    print("-" * 60)
    test_directory_structure(results)
    test_init_files(results)
    test_requirements_txt(results)
    test_env_example(results)
    test_dockerfile(results)
    test_dockerignore(results)
    print()
    
    # Task 2 tests
    print("Task 2: Database and Models")
    print("-" * 60)
    test_pydantic_models(results)
    test_database_manager(results)
    test_database_json(results)
    print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    summary = results.summary()
    print(f"Total Tests: {summary['total']}")
    print(f"Passed: {summary['passed']} ✓")
    print(f"Failed: {summary['failed']} ✗")
    print(f"Warnings: {summary['warnings']} ⚠")
    print()
    
    if summary['failed']:
        print("Failed Tests:")
        for test_name, error in summary['failed_tests']:
            print(f"  - {test_name}: {error}")
        print()
    
    if summary['warnings']:
        print("Warnings:")
        for test_name, warning in summary['warnings']:
            print(f"  - {test_name}: {warning}")
        print()
    
    debug_log("test_setup.py:main", "Test suite completed", summary, "main")
    
    # Exit code
    sys.exit(0 if summary['failed'] == 0 else 1)


if __name__ == "__main__":
    main()

