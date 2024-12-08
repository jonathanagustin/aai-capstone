# src/aai_capstone/cli.py
from pathlib import Path
from typing import Optional
import yaml
import sys

from . import ASSETS_DIR, CONFIG_DIR, CONTENT_DIR, OUTPUT_DIR
from .config import TemplateConfig
from .presentation import PresentationBuilder
from .converter import PresentationConverter


class PresentationGenerator:
    """Generate presentations from YAML content files using a given template."""

    def __init__(
        self,
        template_path: Optional[Path] = None,
        config_path: Optional[Path] = None
    ):
        self.template_path = template_path or (ASSETS_DIR / "templates" / "template.pptx")
        self.config_path = config_path or (CONFIG_DIR / "template.yml")
        self.config = TemplateConfig.from_file(self.config_path)
        self.builder = PresentationBuilder(self.template_path, self.config)

    def process_content_file(self, content_path: Path) -> None:
        """Process a single content file and add slides to the presentation."""
        print(f"Processing {content_path.name}...")

        with open(content_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)

        if 'slides' not in content:
            raise ValueError(f"Content file {content_path.name} missing 'slides' field")

        for slide in content['slides']:
            slide_type = slide.get('type')
            if not slide_type:
                raise ValueError(f"Slide in {content_path.name} missing 'type'")

            if slide_type == 'section':
                self.builder.create_section_header(slide['title'])
            elif slide_type == 'content':
                self.builder.create_content_slide(slide['title'], slide['content'])
            elif slide_type == 'comparison':
                self.builder.create_comparison_slide(
                    slide['title'],
                    slide['left_content'],
                    slide['right_content']
                )
            else:
                raise ValueError(f"Unknown slide type: {slide_type} in {content_path.name}")

    def generate_all(self) -> None:
        """Generate presentations for all YAML content files."""
        content_files = sorted(CONTENT_DIR.glob('*.yml'))

        if not content_files:
            raise FileNotFoundError("No content files found in 'content' directory")

        for content_file in content_files:
            output_file = OUTPUT_DIR / f"{content_file.stem}.pptx"
            self.process_content_file(content_file)
            self.builder.save(output_file)
            print(f"Created presentation: {output_file.name}")


def main() -> None:
    """Main entry point for presentation generation CLI."""
    try:
        generator = PresentationGenerator()
        generator.generate_all()
        PresentationConverter.convert_all()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
