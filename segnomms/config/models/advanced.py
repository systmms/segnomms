"""Advanced QR configuration models.

This module contains configuration classes for advanced QR code features
and utilities.
"""

import logging
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Set up logger for configuration warnings
logger = logging.getLogger(__name__)


class AdvancedQRConfig(BaseModel):
    """Advanced QR code generation features configuration.

    Provides control over advanced QR code features including ECI mode for
    international character encoding, mask pattern selection for visual
    optimization, and structured append for multi-symbol QR sequences.

    Attributes:
        eci_enabled: Enable Extended Channel Interpretation mode
        encoding: Character encoding (UTF-8, ISO-8859-1, etc.)
        mask_pattern: Manual mask pattern selection (0-7 for QR, 0-3 for Micro QR)
        auto_mask: Use automatic mask pattern optimization
        structured_append: Enable structured append for multi-symbol sequences
        symbol_count: Desired number of symbols for structured append
        boost_error: Auto-increase error correction for structured append
    """

    model_config = ConfigDict(validate_default=True, extra="forbid")

    # ECI (Extended Channel Interpretation) Configuration
    eci_enabled: bool = Field(
        default=False,
        description="Enable ECI mode for international character encoding",
    )
    encoding: Optional[str] = Field(
        default=None,
        description="Character encoding (UTF-8, ISO-8859-1, Shift_JIS, etc.)",
    )

    # Mask Pattern Configuration
    mask_pattern: Optional[int] = Field(
        default=None,
        ge=0,
        le=7,
        description="Manual mask pattern selection (0-7 for QR, 0-3 for Micro QR)",
    )
    auto_mask: bool = Field(
        default=True,
        description="Use automatic mask pattern optimization when mask_pattern is None",
    )

    # Structured Append Configuration
    structured_append: bool = Field(
        default=False,
        description="Enable structured append for multi-symbol QR sequences",
    )
    symbol_count: Optional[int] = Field(
        default=None,
        ge=2,
        le=16,
        description="Desired number of symbols for structured append (2-16)",
    )
    boost_error: bool = Field(
        default=True,
        description="Auto-increase error correction for structured append sequences",
    )

    @field_validator("encoding")
    @classmethod
    def validate_encoding(cls, v: Optional[str]) -> Optional[str]:
        """Validate encoding is a known character encoding."""
        if v is None:
            return v

        # Common encodings that Segno supports
        supported_encodings = {
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

        # Normalize encoding name
        normalized = v.upper().replace("-", "_").replace(" ", "_")

        # Check if it's a known encoding
        if normalized not in {
            enc.upper().replace("-", "_") for enc in supported_encodings
        }:
            logger.warning(f"Encoding '{v}' may not be supported by all QR scanners")

        return v

    @model_validator(mode="after")
    def validate_mask_pattern_consistency(self) -> "AdvancedQRConfig":
        """Ensure mask pattern configuration is consistent."""
        if self.mask_pattern is not None and self.auto_mask:
            # If manual mask is specified, disable auto mask
            self.auto_mask = False

        return self

    @model_validator(mode="after")
    def validate_structured_append_config(self) -> "AdvancedQRConfig":
        """Validate structured append configuration."""
        if self.structured_append and self.symbol_count is None:
            # Default to 2 symbols if structured append is enabled but count not specified
            self.symbol_count = 2

        if not self.structured_append and self.symbol_count is not None:
            logger.warning("symbol_count specified but structured_append is disabled")

        return self

    @model_validator(mode="after")
    def validate_eci_encoding_consistency(self) -> "AdvancedQRConfig":
        """Validate ECI and encoding configuration consistency."""
        if self.eci_enabled and self.encoding is None:
            # Default to UTF-8 when ECI is enabled but no encoding specified
            self.encoding = "UTF-8"

        if self.encoding and not self.eci_enabled:
            logger.info(
                f"Using encoding '{self.encoding}' without ECI mode for broader compatibility"
            )

        return self
