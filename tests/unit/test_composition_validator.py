"""Tests for CompositionValidator class rename and deprecation.

This module tests:
- CompositionValidator can be imported and instantiated
- Phase4Validator still works as a deprecated alias
- Deprecation warning is emitted when using Phase4Validator
- Module-level deprecation warning for phase4.py module
"""

from __future__ import annotations

import importlib
import sys
import warnings


class TestCompositionValidatorImport:
    """Test that CompositionValidator can be imported correctly."""

    def test_import_composition_validator_from_phase4_module(self) -> None:
        """Test direct import from phase4 module."""
        from segnomms.validation.phase4 import CompositionValidator

        assert CompositionValidator is not None

    def test_import_composition_validator_from_validation_package(self) -> None:
        """Test import from validation package."""
        from segnomms.validation import CompositionValidator

        assert CompositionValidator is not None

    def test_composition_validator_instantiation(self) -> None:
        """Test that CompositionValidator can be instantiated."""
        from segnomms.validation.phase4 import CompositionValidator

        # Minimal valid parameters for instantiation
        validator = CompositionValidator(
            qr_version=1,
            error_level="M",
            matrix_size=21,
        )
        assert validator is not None
        assert hasattr(validator, "validate_all")


class TestPhase4ValidatorDeprecation:
    """Test that Phase4Validator is deprecated but still works."""

    def test_phase4_validator_alias_works(self) -> None:
        """Test that Phase4Validator can still be used."""
        from segnomms.validation.phase4 import Phase4Validator

        # Should work without error
        validator = Phase4Validator(
            qr_version=1,
            error_level="M",
            matrix_size=21,
        )
        assert validator is not None

    def test_phase4_validator_is_same_as_composition_validator(self) -> None:
        """Test that Phase4Validator is the same class as CompositionValidator."""
        from segnomms.validation.phase4 import CompositionValidator, Phase4Validator

        assert Phase4Validator is CompositionValidator

    def test_phase4_validator_import_from_package_emits_warning(self) -> None:
        """Test that importing Phase4Validator from package emits deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Import from validation package (not phase4 module directly)
            # This should trigger the __getattr__ deprecation warning
            from segnomms.validation import Phase4Validator  # noqa: F401

            # Check that a deprecation warning was issued
            deprecation_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, DeprecationWarning)
                and "Phase4Validator" in str(warning.message)
            ]
            assert len(deprecation_warnings) >= 1, (
                f"Expected deprecation warning for Phase4Validator, "
                f"got warnings: {[str(x.message) for x in w]}"
            )


class TestCompositionValidatorFunctionality:
    """Test that CompositionValidator functionality is preserved."""

    def test_validate_all_method_exists(self) -> None:
        """Test that validate_all method exists and is callable."""
        from segnomms.validation.phase4 import CompositionValidator

        validator = CompositionValidator(
            qr_version=1,
            error_level="M",
            matrix_size=21,
        )
        assert callable(getattr(validator, "validate_all", None))

    def test_validate_frame_safety_method_exists(self) -> None:
        """Test that validate_frame_safety method exists."""
        from segnomms.validation.phase4 import CompositionValidator

        validator = CompositionValidator(
            qr_version=1,
            error_level="M",
            matrix_size=21,
        )
        assert callable(getattr(validator, "validate_frame_safety", None))

    def test_validate_centerpiece_safety_method_exists(self) -> None:
        """Test that validate_centerpiece_safety method exists."""
        from segnomms.validation.phase4 import CompositionValidator

        validator = CompositionValidator(
            qr_version=1,
            error_level="M",
            matrix_size=21,
        )
        assert callable(getattr(validator, "validate_centerpiece_safety", None))


class TestPhase4ModuleDeprecation:
    """Test that importing from phase4 module emits deprecation warning."""

    def test_phase4_module_import_emits_warning(self) -> None:
        """Test that importing from phase4 module emits deprecation warning."""
        # Remove phase4 from sys.modules to ensure fresh import
        modules_to_remove = [key for key in sys.modules.keys() if "phase4" in key]
        for mod in modules_to_remove:
            del sys.modules[mod]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Fresh import should trigger module-level deprecation
            importlib.import_module("segnomms.validation.phase4")

            # Check that a deprecation warning was issued about the module
            module_deprecation_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, DeprecationWarning)
                and "phase4" in str(warning.message).lower()
                and "module" in str(warning.message).lower()
            ]
            assert len(module_deprecation_warnings) >= 1, (
                f"Expected module deprecation warning for phase4, "
                f"got warnings: {[str(x.message) for x in w]}"
            )

    def test_composition_module_no_deprecation_warning(self) -> None:
        """Test that importing from composition module does NOT emit warning."""
        # Remove composition from sys.modules to ensure fresh import
        modules_to_remove = [key for key in sys.modules.keys() if "composition" in key]
        for mod in modules_to_remove:
            del sys.modules[mod]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Fresh import of composition should NOT trigger warning
            importlib.import_module("segnomms.validation.composition")

            # Check that no deprecation warning was issued about composition
            composition_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, DeprecationWarning)
                and "composition" in str(warning.message).lower()
            ]
            assert len(composition_warnings) == 0, (
                f"Did not expect deprecation warning for composition, "
                f"got warnings: {[str(x.message) for x in w]}"
            )
