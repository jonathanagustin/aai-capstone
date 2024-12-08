#!/usr/bin/env python3
# src/aai_capstone/validate.py
from __future__ import annotations

import os
import sys
import yaml
from typing import Dict, Any, List
from pathlib import Path
from dataclasses import dataclass
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init()

@dataclass
class ValidationError:
    """Data class for content validation errors."""
    file: str
    message: str
    detail: str = ""

class ContentValidator:
    """Validate the YAML content files against required structure."""
    REQUIRED_SLIDE_TYPES = {'section', 'content', 'comparison'}

    def __init__(self):
        self.errors: List[ValidationError] = []

    def validate_slide_structure(self, slide: Dict[str, Any], filename: str, slide_index: int) -> None:
        """Validate individual slide structure."""
        if not isinstance(slide, dict):
            self.errors.append(ValidationError(
                filename,
                f"Slide {slide_index} must be a dictionary",
                f"Found type: {type(slide)}"
            ))
            return

        # Check required fields
        if 'type' not in slide:
            self.errors.append(ValidationError(
                filename,
                f"Slide {slide_index} missing required field 'type'"
            ))
            return

        if 'title' not in slide:
            self.errors.append(ValidationError(
                filename,
                f"Slide {slide_index} missing required field 'title'"
            ))
            return

        # Validate slide type
        slide_type = slide['type']
        if slide_type not in self.REQUIRED_SLIDE_TYPES:
            self.errors.append(ValidationError(
                filename,
                f"Invalid slide type in slide {slide_index}: {slide_type}",
                f"Allowed types: {', '.join(self.REQUIRED_SLIDE_TYPES)}"
            ))

        # Type-specific validation
        if slide_type == 'content':
            if 'content' not in slide:
                self.errors.append(ValidationError(
                    filename,
                    f"Content slide {slide_index} missing 'content' field"
                ))
            elif not isinstance(slide['content'], list):
                self.errors.append(ValidationError(
                    filename,
                    f"Content slide {slide_index} 'content' must be a list",
                    f"Found type: {type(slide['content'])}"
                ))

        elif slide_type == 'comparison':
            for field in ['left_content', 'right_content']:
                if field not in slide:
                    self.errors.append(ValidationError(
                        filename,
                        f"Comparison slide {slide_index} missing '{field}' field"
                    ))
                elif not isinstance(slide[field], list):
                    self.errors.append(ValidationError(
                        filename,
                        f"Comparison slide {slide_index} '{field}' must be a list",
                        f"Found type: {type(slide[field])}"
                    ))

    def validate_file(self, filepath: str) -> None:
        """Validate a single YAML content file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)

            if not isinstance(content, dict):
                self.errors.append(ValidationError(
                    filepath,
                    "File content must be a dictionary",
                    f"Found type: {type(content)}"
                ))
                return

            # Validate required top-level fields
            if 'title' not in content:
                self.errors.append(ValidationError(
                    filepath,
                    "Missing required field 'title'"
                ))

            if 'slides' not in content:
                self.errors.append(ValidationError(
                    filepath,
                    "Missing required field 'slides'"
                ))
                return

            if not isinstance(content['slides'], list):
                self.errors.append(ValidationError(
                    filepath,
                    "'slides' must be a list",
                    f"Found type: {type(content['slides'])}"
                ))
                return

            # Validate each slide
            for i, slide in enumerate(content['slides'], 1):
                self.validate_slide_structure(slide, filepath, i)

        except yaml.YAMLError as e:
            self.errors.append(ValidationError(
                filepath,
                "YAML parsing error",
                str(e)
            ))
        except Exception as e:
            self.errors.append(ValidationError(
                filepath,
                "Unexpected error during validation",
                str(e)
            ))

    def print_results(self) -> None:
        """Print validation results, using colors for emphasis."""
        if not self.errors:
            print(f"{Fore.GREEN}✓ All content files are valid{Style.RESET_ALL}")
            return

        print(f"\n{Fore.RED}Found {len(self.errors)} validation errors:{Style.RESET_ALL}\n")

        current_file = None
        for error in self.errors:
            if current_file != error.file:
                current_file = error.file
                print(f"\n{Fore.YELLOW}File: {current_file}{Style.RESET_ALL}")

            print(f"{Fore.RED}  ✗ {error.message}{Style.RESET_ALL}")
            if error.detail:
                print(f"    {error.detail}")

def main() -> int:
    """Main function to validate all YAML content files in the 'content' directory."""
    validator = ContentValidator()
    content_dir = Path("content")

    if not content_dir.exists():
        print(f"{Fore.RED}Error: content directory not found{Style.RESET_ALL}")
        return 1

    yaml_files = list(content_dir.glob("*.yml"))
    if not yaml_files:
        print(f"{Fore.YELLOW}Warning: No YAML files found in content directory{Style.RESET_ALL}")
        return 0

    print(f"Validating {len(yaml_files)} content files...")
    for yaml_file in yaml_files:
        print(f"\nChecking {yaml_file.name}...")
        validator.validate_file(str(yaml_file))

    validator.print_results()
    return 1 if validator.errors else 0

if __name__ == "__main__":
    sys.exit(main())
