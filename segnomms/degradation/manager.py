"""
Degradation manager that orchestrates rule application.
"""

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

from ..config import RenderingConfig
from .models import DegradationResult, DegradationWarning, WarningLevel
from .rules import DEGRADATION_RULES, DegradationRule


class DegradationManager:
    """Manages graceful degradation of rendering configurations."""

    def __init__(self, rules: Optional[List[DegradationRule]] = None):
        """
        Initialize the degradation manager.

        Args:
            rules: Custom list of rules, or use default DEGRADATION_RULES
        """
        self.rules = rules or DEGRADATION_RULES
        self.enabled = True  # Can be disabled for testing

    def apply_degradation(
        self, config: RenderingConfig
    ) -> Tuple[RenderingConfig, DegradationResult]:
        """
        Apply all degradation rules to a configuration.

        Args:
            config: The rendering configuration to check and potentially degrade

        Returns:
            Tuple of (degraded_config, result) where:
            - degraded_config: The potentially modified configuration
            - result: DegradationResult with warnings and changes
        """
        if not self.enabled:
            return config, DegradationResult()

        # Deep copy to avoid modifying the original
        working_config = deepcopy(config)
        result = DegradationResult()

        # Apply each rule
        for rule in self.rules:
            warning = rule.check(working_config)

            if warning:
                result.warnings.append(warning)

                # Apply fallback if it's a critical warning or if safe_mode is enabled
                if warning.level == WarningLevel.CRITICAL or config.safe_mode:
                    # Get the config before applying fallback
                    before_dict = working_config.model_dump()

                    # Apply the fallback
                    working_config = rule.apply_fallback(working_config)

                    # Track what changed
                    after_dict = working_config.model_dump()
                    changes = self._find_changes(before_dict, after_dict)

                    for path, change in changes.items():
                        result.changes_made[path] = change

                    result.degradation_applied = True

        return working_config, result

    def check_only(self, config: RenderingConfig) -> List[DegradationWarning]:
        """
        Check for issues without applying degradation.

        Args:
            config: The configuration to check

        Returns:
            List of warnings found
        """
        warnings = []

        for rule in self.rules:
            warning = rule.check(config)
            if warning:
                warnings.append(warning)

        return warnings

    def _find_changes(
        self, before: Dict[str, Any], after: Dict[str, Any], path: str = ""
    ) -> Dict[str, Dict[str, Any]]:
        """
        Find differences between two configuration dictionaries.

        Args:
            before: Configuration before changes
            after: Configuration after changes
            path: Current path in the configuration tree

        Returns:
            Dictionary mapping configuration paths to their changes
        """
        changes = {}

        for key, before_value in before.items():
            current_path = f"{path}.{key}" if path else key
            after_value = after.get(key)

            if isinstance(before_value, dict) and isinstance(after_value, dict):
                # Recurse into nested dictionaries
                nested_changes = self._find_changes(
                    before_value, after_value, current_path
                )
                changes.update(nested_changes)
            elif before_value != after_value:
                # Value changed
                changes[current_path] = {"before": before_value, "after": after_value}

        return changes

    def get_rule_summary(self) -> Dict[str, List[str]]:
        """
        Get a summary of all rules by incompatibility type.

        Returns:
            Dictionary mapping incompatibility types to rule names
        """
        summary: Dict[str, List[str]] = {}

        for rule in self.rules:
            rule_type = str(rule.incompatibility_type.value)
            if rule_type not in summary:
                summary[rule_type] = []
            summary[rule_type].append(rule.name)

        return summary

    def disable(self) -> None:
        """Disable degradation (useful for testing)."""
        self.enabled = False

    def enable(self) -> None:
        """Enable degradation."""
        self.enabled = True
