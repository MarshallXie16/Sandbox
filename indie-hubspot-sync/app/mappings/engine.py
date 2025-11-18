"""
Field mapping engine that reads YAML configuration and transforms data
between IndieStack and HubSpot formats.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal

import yaml

from app.core.logging import get_logger
from app.models.tracking import EntityType

logger = get_logger(__name__)


class MappingEngine:
    """
    Handles field mapping and transformation between IndieStack and HubSpot.

    Loads configuration from YAML and provides methods to:
    - Map IndieStack records to HubSpot properties
    - Map HubSpot objects to IndieStack update payloads
    - Respect directional constraints
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize mapping engine.

        Args:
            config_path: Path to field_mappings.yaml. If None, uses default location.
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "field_mappings.yaml"

        self.config_path = config_path
        self.mappings = self._load_mappings()
        logger.info("mapping_engine_initialized", config_path=str(config_path))

    def _load_mappings(self) -> Dict[str, Any]:
        """Load mapping configuration from YAML file."""
        try:
            with open(self.config_path, "r") as f:
                mappings = yaml.safe_load(f)
            logger.info("mappings_loaded", entity_count=len(mappings))
            return mappings
        except Exception as e:
            logger.error("failed_to_load_mappings", error=str(e), path=str(self.config_path))
            raise

    def get_entity_mappings(self, entity_type: EntityType) -> Dict[str, Any]:
        """
        Get field mappings for a specific entity type.

        Args:
            entity_type: Type of entity (contact, company, deal)

        Returns:
            Dictionary of field mappings for the entity
        """
        entity_key = f"{entity_type.value}s"  # contacts, companies, deals
        return self.mappings.get(entity_key, {}).get("properties", {})

    def indie_to_hubspot(
        self,
        entity_type: EntityType,
        indie_record: Dict[str, Any],
        direction_filter: Optional[Literal["indie_to_hubspot", "bidirectional"]] = None,
    ) -> Dict[str, Any]:
        """
        Transform an IndieStack record to HubSpot properties format.

        Args:
            entity_type: Type of entity being mapped
            indie_record: Record from IndieStack database
            direction_filter: Only include fields with these directions

        Returns:
            Dictionary of HubSpot properties
        """
        mappings = self.get_entity_mappings(entity_type)
        hubspot_properties = {}

        for field_name, mapping_config in mappings.items():
            # Check direction
            direction = mapping_config.get("direction")
            if direction_filter and direction not in [direction_filter, "bidirectional"]:
                continue

            # Skip if direction doesn't allow indie→hubspot
            if direction == "hubspot_to_indie":
                continue

            indie_field = mapping_config["indie_field"]
            hubspot_property = mapping_config["hubspot_property"]
            transform = mapping_config.get("transform")

            # Extract value from indie_record
            value = self._get_nested_value(indie_record, indie_field)

            if value is not None:
                # Apply transformation if specified
                if transform:
                    value = self._apply_transform(transform, value)

                hubspot_properties[hubspot_property] = value

        return hubspot_properties

    def hubspot_to_indie(
        self,
        entity_type: EntityType,
        hubspot_object: Dict[str, Any],
        direction_filter: Optional[Literal["hubspot_to_indie", "bidirectional"]] = None,
    ) -> Dict[str, Any]:
        """
        Transform a HubSpot object to IndieStack update payload.

        Args:
            entity_type: Type of entity being mapped
            hubspot_object: Object from HubSpot API (with 'properties' key)
            direction_filter: Only include fields with these directions

        Returns:
            Dictionary for updating IndieStack record
        """
        mappings = self.get_entity_mappings(entity_type)
        indie_payload = {}

        # HubSpot objects have properties nested under 'properties' key
        hubspot_props = hubspot_object.get("properties", {})

        for field_name, mapping_config in mappings.items():
            # Check direction
            direction = mapping_config.get("direction")
            if direction_filter and direction not in [direction_filter, "bidirectional"]:
                continue

            # Skip if direction doesn't allow hubspot→indie
            if direction == "indie_to_hubspot":
                continue

            indie_field = mapping_config["indie_field"]
            hubspot_property = mapping_config["hubspot_property"]
            transform = mapping_config.get("transform")

            # Extract value from HubSpot properties
            value = hubspot_props.get(hubspot_property)

            if value is not None:
                # Reverse transformation if needed
                if transform:
                    value = self._reverse_transform(transform, value)

                # Set nested value in indie_payload
                self._set_nested_value(indie_payload, indie_field, value)

        return indie_payload

    def get_bidirectional_fields(self, entity_type: EntityType) -> List[str]:
        """
        Get list of fields that sync bidirectionally.

        Args:
            entity_type: Type of entity

        Returns:
            List of indie field names that are bidirectional
        """
        mappings = self.get_entity_mappings(entity_type)
        return [
            config["indie_field"]
            for config in mappings.values()
            if config.get("direction") == "bidirectional"
        ]

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """
        Get value from nested dictionary using dot notation.

        Example: 'details.engagement_score' → data['details']['engagement_score']
        """
        keys = path.split(".")
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None

            if value is None:
                return None

        return value

    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """
        Set value in nested dictionary using dot notation.

        Example: 'details.engagement_score' → data['details']['engagement_score'] = value
        """
        keys = path.split(".")

        # Navigate to the parent of the target key
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the value
        current[keys[-1]] = value

    def _apply_transform(self, transform_name: str, value: Any) -> Any:
        """
        Apply named transformation to a value.

        Args:
            transform_name: Name of transformation function
            value: Value to transform

        Returns:
            Transformed value
        """
        transformers = {
            "datetime_to_timestamp": self._datetime_to_timestamp,
            "date_to_timestamp": self._date_to_timestamp,
            "stage_id_to_hubspot_stage": self._stage_id_to_hubspot_stage,
            "pipeline_id_to_hubspot_pipeline": self._pipeline_id_to_hubspot_pipeline,
        }

        transformer = transformers.get(transform_name)
        if transformer:
            return transformer(value)
        else:
            logger.warning("unknown_transform", transform=transform_name)
            return value

    def _reverse_transform(self, transform_name: str, value: Any) -> Any:
        """
        Apply reverse transformation (HubSpot → IndieStack).

        Args:
            transform_name: Name of transformation function
            value: Value to reverse transform

        Returns:
            Reverse transformed value
        """
        reverse_transformers = {
            "datetime_to_timestamp": self._timestamp_to_datetime,
            "date_to_timestamp": self._timestamp_to_date,
            # Stage/pipeline mappings are one-way for now
        }

        transformer = reverse_transformers.get(transform_name)
        if transformer:
            return transformer(value)
        else:
            return value

    # Transformation functions
    @staticmethod
    def _datetime_to_timestamp(dt: Any) -> Optional[int]:
        """Convert datetime to Unix timestamp (milliseconds)."""
        if isinstance(dt, datetime):
            return int(dt.timestamp() * 1000)
        elif isinstance(dt, str):
            try:
                parsed_dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
                return int(parsed_dt.timestamp() * 1000)
            except Exception:
                return None
        return None

    @staticmethod
    def _timestamp_to_datetime(ts: Any) -> Optional[str]:
        """Convert Unix timestamp (milliseconds) to ISO datetime string."""
        if isinstance(ts, (int, float)):
            try:
                dt = datetime.fromtimestamp(ts / 1000)
                return dt.isoformat()
            except Exception:
                return None
        return None

    @staticmethod
    def _date_to_timestamp(date: Any) -> Optional[int]:
        """Convert date to Unix timestamp (milliseconds)."""
        if isinstance(date, datetime):
            return int(date.timestamp() * 1000)
        elif isinstance(date, str):
            try:
                parsed_date = datetime.fromisoformat(date)
                return int(parsed_date.timestamp() * 1000)
            except Exception:
                return None
        return None

    @staticmethod
    def _timestamp_to_date(ts: Any) -> Optional[str]:
        """Convert Unix timestamp to ISO date string."""
        if isinstance(ts, (int, float)):
            try:
                dt = datetime.fromtimestamp(ts / 1000)
                return dt.date().isoformat()
            except Exception:
                return None
        return None

    @staticmethod
    def _stage_id_to_hubspot_stage(stage_id: Any) -> str:
        """
        Map IndieStack stage ID to HubSpot deal stage.

        TODO: This should be configurable. For now, returning as-is.
        """
        # In production, this would use a lookup table
        return str(stage_id)

    @staticmethod
    def _pipeline_id_to_hubspot_pipeline(pipeline_id: Any) -> str:
        """
        Map IndieStack pipeline ID to HubSpot pipeline.

        TODO: This should be configurable. For now, returning as-is.
        """
        return str(pipeline_id)
