"""
Contact source interfaces and implementations.
Provides abstraction for loading contacts from various sources.
"""
import csv
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.core.logging import logger
from app.models import RecipientSegment


class ContactSource(ABC):
    """
    Abstract base class for contact sources.

    Contact sources provide recipients for campaigns from various systems.
    """

    @abstractmethod
    def load_contacts(self) -> List[Dict[str, Any]]:
        """
        Load contacts from the source.

        Returns:
            List of contact dictionaries with keys: email, name, segment, details
        """
        pass


class CSVContactSource(ContactSource):
    """
    CSV file contact source.

    Loads contacts from a CSV file with configurable column mapping.
    """

    def __init__(
        self,
        file_path: str,
        email_column: str = "email",
        name_column: str = "name",
        segment_column: Optional[str] = "segment",
        default_segment: RecipientSegment = RecipientSegment.OTHER,
        extra_columns: Optional[List[str]] = None
    ):
        """
        Initialize CSV contact source.

        Args:
            file_path: Path to CSV file
            email_column: Column name for email addresses (required)
            name_column: Column name for names
            segment_column: Column name for segment (optional)
            default_segment: Default segment if not specified
            extra_columns: Additional columns to include in details
        """
        self.file_path = Path(file_path)
        self.email_column = email_column
        self.name_column = name_column
        self.segment_column = segment_column
        self.default_segment = default_segment
        self.extra_columns = extra_columns or []

        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

    def load_contacts(self) -> List[Dict[str, Any]]:
        """
        Load contacts from CSV file.

        Returns:
            List of contact dictionaries

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If required columns are missing
        """
        contacts = []

        try:
            with open(self.file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                # Validate required columns
                if self.email_column not in reader.fieldnames:
                    raise ValueError(f"Required column '{self.email_column}' not found in CSV")

                logger.info(f"Loading contacts from {self.file_path}")

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    email = row.get(self.email_column, "").strip()

                    # Skip rows without email
                    if not email:
                        logger.warning(f"Skipping row {row_num}: missing email")
                        continue

                    # Basic email validation
                    if "@" not in email:
                        logger.warning(f"Skipping row {row_num}: invalid email '{email}'")
                        continue

                    # Extract name
                    name = row.get(self.name_column, "").strip() or None

                    # Extract segment
                    segment = self.default_segment
                    if self.segment_column and self.segment_column in row:
                        segment_value = row[self.segment_column].strip().lower()
                        try:
                            segment = RecipientSegment(segment_value)
                        except ValueError:
                            logger.warning(
                                f"Row {row_num}: Invalid segment '{segment_value}', "
                                f"using default '{self.default_segment.value}'"
                            )

                    # Extract extra fields for details
                    details = {}
                    for col in self.extra_columns:
                        if col in row and row[col]:
                            details[col] = row[col].strip()

                    # Add all non-standard columns to details
                    standard_cols = {self.email_column, self.name_column, self.segment_column}
                    for key, value in row.items():
                        if key not in standard_cols and value:
                            details[key] = value.strip()

                    contacts.append({
                        "email": email,
                        "name": name,
                        "segment": segment,
                        "details": details
                    })

                logger.info(f"Loaded {len(contacts)} contacts from CSV")
                return contacts

        except csv.Error as e:
            logger.error(f"CSV parsing error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading contacts from CSV: {e}")
            raise


class IndieStackContactSource(ContactSource):
    """
    IndieStack CRM contact source.

    Future implementation for loading contacts from IndieStack CRM.
    This is a placeholder for future integration.
    """

    def __init__(
        self,
        api_url: str,
        api_key: str,
        filters: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize IndieStack contact source.

        Args:
            api_url: IndieStack API URL
            api_key: API authentication key
            filters: Optional filters for contact query
        """
        self.api_url = api_url
        self.api_key = api_key
        self.filters = filters or {}
        logger.info("IndieStack contact source initialized (not yet implemented)")

    def load_contacts(self) -> List[Dict[str, Any]]:
        """
        Load contacts from IndieStack CRM.

        This is a placeholder implementation.

        Returns:
            List of contact dictionaries

        Raises:
            NotImplementedError: This feature is not yet implemented
        """
        raise NotImplementedError(
            "IndieStack integration is not yet implemented. "
            "Please use CSVContactSource for now."
        )
