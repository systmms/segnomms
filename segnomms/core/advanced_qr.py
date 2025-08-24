"""Advanced QR code generation with ECI, mask patterns, and structured append.

This module provides enhanced QR code generation capabilities including:
- ECI (Extended Channel Interpretation) mode for international character encoding
- Manual mask pattern selection for visual optimization
- Structured append for multi-symbol QR code sequences

The module integrates with Segno's advanced features while providing
proper error handling, validation, and fallback mechanisms.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypedDict, Union

import segno
from segno import QRCode

from ..config import AdvancedQRConfig


class SegnoMakeParams(TypedDict, total=False):
    """Type definition for segno.make() parameters."""
    error: Optional[str]
    version: Optional[int]
    encoding: Optional[str]
    eci: bool  # segno expects bool, not Optional[bool]
    mask: Optional[int]


class SegnoSequenceParams(TypedDict, total=False):
    """Type definition for segno.make_sequence() parameters."""
    error: Optional[str]
    boost_error: bool  # segno expects bool, not Optional[bool]
    encoding: Optional[str]
    mask: Optional[int]
    symbol_count: Optional[int]
    version: Optional[int]


class AnalysisDict(TypedDict, total=False):
    """Type definition for encoding analysis results."""
    ascii_compatible: bool
    latin1_compatible: bool
    requires_unicode: bool
    total_chars: int
    ascii_chars: int
    extended_chars: int
    has_cjk: bool


class RecommendationsDict(TypedDict):
    """Type definition for encoding recommendations."""
    recommended_encoding: Optional[str]
    needs_eci: bool
    analysis: AnalysisDict
    alternatives: List[str]

logger = logging.getLogger(__name__)


@dataclass
class QRGenerationResult:
    """Result of advanced QR code generation.

    Attributes:
        qr_codes: List of generated QR codes (single code or sequence)
        is_sequence: Whether result is a structured append sequence
        metadata: Additional metadata about generation process
        warnings: Any warnings generated during creation
        fallback_used: Whether fallback generation was used
    """

    qr_codes: List[QRCode]
    is_sequence: bool
    metadata: Dict[str, Any]
    warnings: List[str]
    fallback_used: bool


class AdvancedQRGenerator:
    """Advanced QR code generator with ECI, mask patterns, and structured append.

    This class provides enhanced QR code generation capabilities while maintaining
    compatibility with standard QR codes. It includes proper error handling and
    fallback mechanisms for maximum reliability.
    """

    def __init__(self) -> None:
        """Initialize the advanced QR generator."""
        self.supported_encodings = {
            "UTF-8",
            "UTF-16",
            "UTF-32",
            "ISO-8859-1",
            "ISO-8859-2",
            "ISO-8859-3",
            "ISO-8859-4",
            "ISO-8859-5",
            "ISO-8859-6",
            "ISO-8859-7",
            "ISO-8859-8",
            "ISO-8859-9",
            "ISO-8859-10",
            "ISO-8859-11",
            "ISO-8859-13",
            "ISO-8859-14",
            "ISO-8859-15",
            "ISO-8859-16",
            "Shift_JIS",
            "CP932",
            "EUC-JP",
            "GB2312",
            "GBK",
            "GB18030",
            "BIG5",
            "CP1252",
            "ASCII",
        }

    def generate_qr(
        self,
        content: str,
        config: AdvancedQRConfig,
        error: str = "M",
        version: Optional[int] = None,
    ) -> QRGenerationResult:
        """Generate QR code(s) with advanced features.

        Args:
            content: Data to encode in the QR code(s)
            config: Advanced QR configuration
            error: Error correction level ('L', 'M', 'Q', 'H')
            version: QR code version (None for automatic)

        Returns:
            QRGenerationResult with generated QR code(s) and metadata
        """
        warnings: List[str] = []
        metadata: Dict[str, Any] = {}
        fallback_used = False

        try:
            if config.structured_append:
                return self._generate_structured_append(
                    content, config, error, version, warnings, metadata
                )
            else:
                return self._generate_single_qr(
                    content, config, error, version, warnings, metadata
                )

        except Exception as e:
            logger.warning(f"Advanced QR generation failed: {e}")
            warnings.append(f"Advanced generation failed, using fallback: {str(e)}")
            fallback_used = True

            # Fallback to basic QR generation
            try:
                qr = segno.make(content, error=error, version=version)
                metadata["fallback_reason"] = str(e)
                metadata["fallback_method"] = "basic_segno"

                return QRGenerationResult(
                    qr_codes=[qr],
                    is_sequence=False,
                    metadata=metadata,
                    warnings=warnings,
                    fallback_used=fallback_used,
                )
            except Exception as fallback_error:
                logger.error(f"Fallback QR generation also failed: {fallback_error}")
                raise RuntimeError(f"QR generation failed: {fallback_error}") from e

    def _generate_single_qr(
        self,
        content: str,
        config: AdvancedQRConfig,
        error: str,
        version: Optional[int],
        warnings: List[str],
        metadata: Dict[str, Any],
    ) -> QRGenerationResult:
        """Generate a single QR code with advanced features."""

        # Prepare Segno parameters
        segno_params: SegnoMakeParams = {"error": error, "version": version}

        # Add encoding if specified
        if config.encoding:
            segno_params["encoding"] = config.encoding
            metadata["encoding"] = config.encoding

            # Validate encoding
            if config.encoding not in self.supported_encodings:
                warnings.append(
                    f"Encoding '{config.encoding}' may not be widely supported"
                )

        # Add ECI mode if enabled
        if config.eci_enabled:
            segno_params["eci"] = True
            metadata["eci_enabled"] = True

            # ECI requires encoding
            if not config.encoding:
                segno_params["encoding"] = "UTF-8"
                metadata["encoding"] = "UTF-8"
                warnings.append(
                    "ECI enabled without encoding specified, defaulting to UTF-8"
                )

            # Warn about ECI compatibility
            warnings.append("ECI mode enabled - ensure target scanners support ECI")

        # Add mask pattern if specified
        if config.mask_pattern is not None:
            segno_params["mask"] = config.mask_pattern
            metadata["mask_pattern"] = config.mask_pattern
            metadata["auto_mask"] = False
        else:
            metadata["auto_mask"] = config.auto_mask

        # Generate the QR code
        try:
            qr = segno.make(content, **segno_params)

            # Add metadata about the generated QR
            metadata.update(
                {
                    "version": qr.version,
                    "error_level": qr.error,
                    "symbol_size": qr.symbol_size(),
                    "data_length": len(content),
                    "used_mask": qr.mask if hasattr(qr, "mask") else None,
                }
            )

            # Check if mask pattern was applied correctly
            if config.mask_pattern is not None and hasattr(qr, "mask"):
                if qr.mask != config.mask_pattern:
                    warnings.append(
                        f"Requested mask pattern {config.mask_pattern} "
                        f"but QR uses mask {qr.mask}"
                    )

            return QRGenerationResult(
                qr_codes=[qr],
                is_sequence=False,
                metadata=metadata,
                warnings=warnings,
                fallback_used=False,
            )

        except Exception as e:
            # Try without ECI if ECI fails
            if config.eci_enabled and "eci" in segno_params:
                logger.info(f"ECI mode failed ({e}), retrying without ECI")
                warnings.append(
                    f"ECI mode failed, using encoding without ECI: {str(e)}"
                )

                # Remove ECI and retry
                segno_params_fallback: SegnoMakeParams = segno_params.copy()
                del segno_params_fallback["eci"]
                metadata["eci_fallback"] = True

                qr = segno.make(content, **segno_params_fallback)
                metadata.update(
                    {
                        "version": qr.version,
                        "error_level": qr.error,
                        "symbol_size": qr.symbol_size(),
                        "data_length": len(content),
                        "used_mask": qr.mask if hasattr(qr, "mask") else None,
                    }
                )

                return QRGenerationResult(
                    qr_codes=[qr],
                    is_sequence=False,
                    metadata=metadata,
                    warnings=warnings,
                    fallback_used=True,
                )
            else:
                raise

    def _generate_structured_append(
        self,
        content: str,
        config: AdvancedQRConfig,
        error: str,
        version: Optional[int],
        warnings: List[str],
        metadata: Dict[str, Any],
    ) -> QRGenerationResult:
        """Generate structured append QR code sequence."""

        # Prepare Segno parameters for sequence
        sequence_params: SegnoSequenceParams = {"error": error, "boost_error": config.boost_error}

        # Add encoding if specified
        if config.encoding:
            sequence_params["encoding"] = config.encoding
            metadata["encoding"] = config.encoding

        # Note: ECI is not supported by segno.make_sequence()
        # Only add encoding for structured append
        if config.eci_enabled:
            metadata["eci_enabled"] = True
            warnings.append("ECI mode not supported for structured append sequences")
            
            if not config.encoding:
                sequence_params["encoding"] = "UTF-8"
                metadata["encoding"] = "UTF-8"
                warnings.append(
                    "ECI requested for sequence but not supported, using UTF-8 encoding"
                )

        # Add mask pattern if specified
        if config.mask_pattern is not None:
            sequence_params["mask"] = config.mask_pattern
            metadata["mask_pattern"] = config.mask_pattern

        # Add symbol count or version
        if config.symbol_count:
            sequence_params["symbol_count"] = config.symbol_count
            metadata["requested_symbol_count"] = config.symbol_count
        elif version:
            sequence_params["version"] = version
            metadata["requested_version"] = version
        else:
            # Default to 2 symbols if neither specified
            sequence_params["symbol_count"] = 2
            metadata["requested_symbol_count"] = 2
            warnings.append(
                "No symbol count or version specified for sequence, defaulting to 2 symbols"
            )

        try:
            # Generate structured append sequence
            sequence = segno.make_sequence(content, **sequence_params)

            # Convert to list if it's not already
            if hasattr(sequence, "__iter__"):
                qr_codes = list(sequence)
            else:
                # Single QR returned - structured append not needed
                qr_codes = [sequence]
                warnings.append(
                    "Content fits in single QR code, structured append not used"
                )

            # Collect metadata from all QR codes in sequence
            metadata.update(
                {
                    "actual_symbol_count": len(qr_codes),
                    "total_data_length": len(content),
                    "sequence_info": [],
                }
            )

            for i, qr in enumerate(qr_codes):
                qr_info = {
                    "symbol_number": i + 1,
                    "version": qr.version,
                    "symbol_size": qr.symbol_size(),
                    "designator": getattr(qr, "designator", None),
                    "used_mask": qr.mask if hasattr(qr, "mask") else None,
                }
                metadata["sequence_info"].append(qr_info)

            # Check if sequence was split as expected
            if config.symbol_count and len(qr_codes) != config.symbol_count:
                warnings.append(
                    f"Requested {config.symbol_count} symbols but generated {len(qr_codes)}"
                )

            return QRGenerationResult(
                qr_codes=qr_codes,
                is_sequence=len(qr_codes) > 1,
                metadata=metadata,
                warnings=warnings,
                fallback_used=False,
            )

        except Exception as e:
            # Try fallback - since ECI is already not in sequence_params, 
            # try without encoding if encoding was the issue
            if config.encoding and "encoding" in sequence_params:
                logger.info(
                    f"Structured append with encoding failed ({e}), retrying with default encoding"
                )
                warnings.append(
                    f"Structured append encoding failed, using fallback: {str(e)}"
                )

                sequence_params_fallback: SegnoSequenceParams = sequence_params.copy()
                del sequence_params_fallback["encoding"]
                metadata["encoding_fallback"] = True

                sequence = segno.make_sequence(content, **sequence_params_fallback)
                qr_codes = (
                    list(sequence) if hasattr(sequence, "__iter__") else [sequence]
                )

                metadata.update(
                    {
                        "actual_symbol_count": len(qr_codes),
                        "total_data_length": len(content),
                        "sequence_info": [
                            {
                                "symbol_number": i + 1,
                                "version": qr.version,
                                "symbol_size": qr.symbol_size(),
                                "designator": getattr(qr, "designator", None),
                                "used_mask": qr.mask if hasattr(qr, "mask") else None,
                            }
                            for i, qr in enumerate(qr_codes)
                        ],
                    }
                )

                return QRGenerationResult(
                    qr_codes=qr_codes,
                    is_sequence=len(qr_codes) > 1,
                    metadata=metadata,
                    warnings=warnings,
                    fallback_used=True,
                )
            else:
                raise

    def validate_config(self, config: AdvancedQRConfig) -> List[str]:
        """Validate advanced QR configuration and return warnings.

        Args:
            config: Configuration to validate

        Returns:
            List of validation warning messages
        """
        warnings = []

        # ECI validation
        if config.eci_enabled:
            if not config.encoding:
                warnings.append("ECI enabled without encoding specification")
            else:
                if config.encoding not in self.supported_encodings:
                    warnings.append(
                        f"Encoding '{config.encoding}' may not be supported"
                    )

            warnings.append("ECI mode may not be supported by all QR code scanners")

        # Mask pattern validation
        if config.mask_pattern is not None:
            if not 0 <= config.mask_pattern <= 7:
                warnings.append(
                    f"Mask pattern {config.mask_pattern} is outside valid range 0-7"
                )

        # Structured append validation
        if config.structured_append:
            if config.symbol_count and config.symbol_count > 16:
                warnings.append("Structured append supports maximum 16 symbols")

            warnings.append(
                "Structured append requires scanners that support multi-symbol sequences"
            )

        return warnings

    def get_encoding_recommendations(self, content: str) -> RecommendationsDict:
        """Get encoding recommendations for the given content.

        Args:
            content: Content to analyze

        Returns:
            Dictionary with encoding recommendations and analysis
        """
        analysis: AnalysisDict = {}
        recommendations: RecommendationsDict = {
            "recommended_encoding": None,
            "needs_eci": False,
            "analysis": analysis,
            "alternatives": [],
        }

        try:
            # Test ASCII encoding
            content.encode("ascii")
            recommendations["recommended_encoding"] = "ASCII"
            analysis["ascii_compatible"] = True
        except UnicodeEncodeError:
            analysis["ascii_compatible"] = False

            try:
                # Test ISO-8859-1 (Latin-1)
                content.encode("iso-8859-1")
                recommendations["recommended_encoding"] = "ISO-8859-1"
                analysis["latin1_compatible"] = True
            except UnicodeEncodeError:
                analysis["latin1_compatible"] = False

                # Requires UTF-8
                recommendations["recommended_encoding"] = "UTF-8"
                recommendations["needs_eci"] = True
                analysis["requires_unicode"] = True

        # Count different character types
        analysis["total_chars"] = len(content)
        analysis["ascii_chars"] = sum(1 for c in content if ord(c) < 128)
        analysis["extended_chars"] = analysis["total_chars"] - analysis["ascii_chars"]
        analysis["has_cjk"] = any(
            "\u4e00" <= c <= "\u9fff"  # CJK Unified Ideographs
            or "\u3040" <= c <= "\u309f"  # Hiragana
            or "\u30a0" <= c <= "\u30ff"  # Katakana
            for c in content
        )

        # Add alternative recommendations
        if recommendations["recommended_encoding"] == "UTF-8":
            if analysis["has_cjk"]:
                recommendations["alternatives"] = ["Shift_JIS", "GB2312", "BIG5"]
            else:
                recommendations["alternatives"] = ["UTF-16", "UTF-32"]

        return recommendations


def create_advanced_qr_generator() -> AdvancedQRGenerator:
    """Create an AdvancedQRGenerator instance.

    Returns:
        Configured AdvancedQRGenerator instance
    """
    return AdvancedQRGenerator()
