import json
import logging
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from app.models.user import User
from app.models.medication import Medication
from app.models.prescription import Prescription

# Configure module-level logger
logger = logging.getLogger(__name__)

# #region agent log
DEBUG_LOG_PATH = r"c:\Users\Noga\OneDrive\Desktop\Wond\.cursor\debug.log"
def _debug_log(location: str, message: str, data: dict = None, hypothesis_id: str = None):
    try:
        log_entry = {
            "sessionId": "debug-session",
            "runId": "initial",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(time.time() * 1000)
        }
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass
# #endregion


class DatabaseManager:
    """
    Database Manager for handling JSON-based pharmacy database operations.
    
    Purpose (Why):
    This class provides a centralized interface for loading, saving, and querying
    the pharmacy database. It manages the JSON file storage and provides type-safe
    access to users, medications, and prescriptions using Pydantic models.
    
    Implementation (What):
    Uses JSON file storage with Pydantic models for validation. Provides methods
    for loading/saving the database and querying by ID or name. Handles file I/O
    operations and converts between JSON and Pydantic models.
    
    Attributes:
        db_path: Path to the database JSON file
        _data: Internal cache of loaded database data
    """
    
    def __init__(self, db_path: str = "data/database.json"):
        """
        Initialize the DatabaseManager.
        
        Args:
            db_path: Path to the database JSON file (default: "data/database.json")
        """
        # Get the project root directory (parent of app/)
        project_root = Path(__file__).parent.parent.parent
        self.db_path = project_root / db_path
        self._data: Optional[Dict[str, Any]] = None
    
    def load_db(self) -> Dict[str, Any]:
        """
        Load the database from JSON file.
        
        Purpose (Why):
        Loads the pharmacy database from JSON storage into memory cache for fast access.
        This method provides the foundation for all database queries and operations.
        
        Implementation (What):
        Reads the JSON file from disk, parses it, and stores it in the internal cache.
        Uses UTF-8 encoding to support Hebrew characters. Validates file existence
        before attempting to read.
        
        Returns:
            Dictionary containing 'users', 'medications', and 'prescriptions' lists
            
        Raises:
            FileNotFoundError: If the database file doesn't exist
            json.JSONDecodeError: If the JSON file is invalid
        """
        if not self.db_path.exists():
            logger.error(f"Database file not found: {self.db_path}")
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        # #region agent log
        load_start = time.time()
        _debug_log("app/database/db.py:load_db:start", "Database load started", {"db_path": str(self.db_path)}, "H1")
        # #endregion
        
        logger.debug(f"Loading database from: {self.db_path}")
        with open(self.db_path, 'r', encoding='utf-8') as f:
            self._data = json.load(f)
        
        # #region agent log
        load_duration = (time.time() - load_start) * 1000
        _debug_log("app/database/db.py:load_db:complete", "Database load complete", {"duration_ms": load_duration}, "H1")
        # #endregion
        
        user_count = len(self._data.get("users", []))
        med_count = len(self._data.get("medications", []))
        presc_count = len(self._data.get("prescriptions", []))
        logger.info(f"Database loaded: {user_count} users, {med_count} medications, {presc_count} prescriptions")
        
        return self._data
    
    def save_db(self, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Save the database to JSON file.
        
        Purpose (Why):
        Persists database changes to disk storage. Allows the system to maintain
        data consistency and recover state after application restarts.
        
        Implementation (What):
        Writes the database dictionary to JSON file with proper formatting.
        Creates parent directories if they don't exist. Updates internal cache
        after successful save. Uses UTF-8 encoding to support Hebrew characters.
        
        Args:
            data: Optional dictionary to save. If None, saves the cached _data.
            
        Raises:
            ValueError: If no data is provided and _data is None
            IOError: If file write fails
        """
        if data is None:
            data = self._data
        
        if data is None:
            logger.error("Attempted to save database with no data available")
            raise ValueError("No data to save. Load database first or provide data parameter.")
        
        # Ensure the directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"Saving database to: {self.db_path}")
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Update cache
        self._data = data
        logger.info("Database saved successfully")
    
    def get_medication_by_id(self, medication_id: str) -> Optional[Medication]:
        """
        Get a medication by its ID.
        
        Purpose (Why):
        Retrieves a specific medication record by its unique identifier. This is
        the primary method for accessing medication details when the ID is known,
        enabling efficient lookups for tool operations.
        
        Implementation (What):
        Searches through the cached medications list for a matching ID. If data
        is not loaded, automatically loads the database. Returns a validated
        Pydantic Medication model instance if found.
        
        Args:
            medication_id: The medication ID to search for
            
        Returns:
            Medication model instance if found, None otherwise
        """
        if self._data is None:
            self.load_db()
        
        for med_data in self._data.get("medications", []):
            if med_data.get("medication_id") == medication_id:
                logger.debug(f"Found medication: {medication_id}")
                return Medication(**med_data)
        
        logger.warning(f"Medication not found: {medication_id}")
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.
        
        Purpose (Why):
        Retrieves a specific user record by their unique identifier. Enables
        access to user information and their associated prescriptions for
        customer service operations.
        
        Implementation (What):
        Searches through the cached users list for a matching ID. If data is
        not loaded, automatically loads the database. Returns a validated
        Pydantic User model instance if found.
        
        Args:
            user_id: The user ID to search for
            
        Returns:
            User model instance if found, None otherwise
        """
        if self._data is None:
            self.load_db()
        
        for user_data in self._data.get("users", []):
            if user_data.get("user_id") == user_id:
                logger.debug(f"Found user: {user_id}")
                return User(**user_data)
        
        logger.warning(f"User not found: {user_id}")
        return None
    
    def get_prescriptions_by_user(self, user_id: str) -> List[Prescription]:
        """
        Get all prescriptions for a specific user.
        
        Purpose (Why):
        Retrieves all prescription records associated with a user. This enables
        the system to provide users with their prescription history and verify
        prescription validity for medication purchases.
        
        Implementation (What):
        Filters the prescriptions list by user_id and returns all matching
        records as validated Pydantic Prescription model instances. If data is
        not loaded, automatically loads the database.
        
        Args:
            user_id: The user ID to get prescriptions for
            
        Returns:
            List of Prescription model instances for the user (empty list if none found)
        """
        if self._data is None:
            self.load_db()
        
        prescriptions = []
        for presc_data in self._data.get("prescriptions", []):
            if presc_data.get("user_id") == user_id:
                prescriptions.append(Prescription(**presc_data))
        
        logger.debug(f"Found {len(prescriptions)} prescriptions for user: {user_id}")
        return prescriptions
    
    def search_medications_by_name(self, name: str, language: Optional[str] = None) -> List[Medication]:
        """
        Search medications by name (supports Hebrew and English).
        
        Purpose (Why):
        Enables fuzzy search for medications by name in both Hebrew and English.
        This is the primary method for finding medications when users provide
        medication names rather than IDs, supporting natural language queries.
        
        Implementation (What):
        Performs case-insensitive partial matching against medication names in
        the specified language(s). Searches both Hebrew and English names if
        language is not specified. Prevents duplicate results by tracking
        already-added medications. If data is not loaded, automatically loads
        the database.
        
        Args:
            name: The medication name to search for (case-insensitive, partial match)
            language: Optional language filter ('he' for Hebrew, 'en' for English).
                     If None, searches both languages.
        
        Returns:
            List of Medication model instances matching the search (empty list if none found)
        """
        if self._data is None:
            self.load_db()
        
        if not name or not name.strip():
            logger.warning("Empty search name provided")
            return []
        
        name_lower = name.lower().strip()
        results = []
        
        for med_data in self._data.get("medications", []):
            medication_id = med_data.get("medication_id")
            already_added = any(m.medication_id == medication_id for m in results)
            
            if already_added:
                continue
            
            # Search in Hebrew name
            if language is None or language == "he":
                name_he = med_data.get("name_he", "").lower()
                if name_lower in name_he:
                    results.append(Medication(**med_data))
                    continue
            
            # Search in English name
            if language is None or language == "en":
                name_en = med_data.get("name_en", "").lower()
                if name_lower in name_en:
                    results.append(Medication(**med_data))
                    continue
            
            # Search in brand names (regardless of language filter)
            # This allows finding medications by their brand names
            # e.g., "Acamol" will find medications with "Acamol" in brand_names
            brand_names = med_data.get("brand_names", [])
            found_in_brands = False
            for brand_name in brand_names:
                if name_lower in brand_name.lower():
                    results.append(Medication(**med_data))
                    found_in_brands = True
                    break
            
            if found_in_brands:
                continue
            
            # Search in active ingredients (regardless of language filter)
            # This allows finding medications by their active ingredient names
            # e.g., "Paracetamol" will find medications with "Paracetamol" in active_ingredients
            active_ingredients = med_data.get("active_ingredients", [])
            for ingredient in active_ingredients:
                ingredient_lower = ingredient.lower()
                # Extract the base ingredient name (before dosage info like "500mg")
                # e.g., "Paracetamol 500mg" -> "paracetamol"
                ingredient_base = ingredient_lower.split()[0] if ingredient_lower.split() else ""
                if name_lower in ingredient_lower or name_lower == ingredient_base:
                    results.append(Medication(**med_data))
                    break
        
        logger.debug(f"Search for '{name}' (lang={language}) found {len(results)} results")
        return results
    
    def search_users_by_name_or_email(self, name_or_email: str) -> List[User]:
        """
        Search users by name or email address.
        
        Purpose (Why):
        Enables finding users when they provide their name or email address instead
        of user_id. This supports natural language queries where users identify
        themselves by name or email, which is more user-friendly than requiring
        technical IDs. Supports case-insensitive partial matching for flexible search.
        
        Implementation (What):
        Performs case-insensitive partial matching against user names and email
        addresses. Searches both fields simultaneously and returns all matching
        users. If data is not loaded, automatically loads the database. Returns
        empty list if no matches found.
        
        Args:
            name_or_email: The name or email address to search for (case-insensitive, partial match)
        
        Returns:
            List of User model instances matching the search (empty list if none found)
        """
        if self._data is None:
            self.load_db()
        
        if not name_or_email or not name_or_email.strip():
            logger.warning("Empty search name_or_email provided")
            return []
        
        search_term = name_or_email.lower().strip()
        results = []
        
        for user_data in self._data.get("users", []):
            user_id = user_data.get("user_id")
            already_added = any(u.user_id == user_id for u in results)
            
            if already_added:
                continue
            
            # Search in name
            name = user_data.get("name", "").lower()
            if search_term in name:
                results.append(User(**user_data))
                continue
            
            # Search in email
            email = user_data.get("email", "").lower()
            if search_term in email:
                results.append(User(**user_data))
                continue
        
        logger.debug(f"Search for '{name_or_email}' found {len(results)} users")
        return results

