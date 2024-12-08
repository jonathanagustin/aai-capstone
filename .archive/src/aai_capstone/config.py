# src/aai_capstone/config.py
from dataclasses import dataclass
from typing import List, Dict, Any
import yaml
from pathlib import Path


@dataclass
class TemplateConfig:
    """Configuration for the PowerPoint template, including layouts and dimensions."""
    path: str
    dimensions: Dict[str, float]
    layouts: List[Dict[str, Any]]

    @classmethod
    def from_file(cls, config_path: Path) -> 'TemplateConfig':
        """Load template configuration from a YAML file.

        Args:
            config_path (Path): Path to the YAML config file.

        Returns:
            TemplateConfig: Loaded template configuration.
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Template configuration not found: {config_path}")

        with config_path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return cls(
            path=data['template']['path'],
            dimensions=data['template']['dimensions'],
            layouts=data['layouts']
        )

    def get_layout_by_name(self, name: str) -> Dict[str, Any]:
        """Get a layout configuration by its name."""
        layout = next((l for l in self.layouts if l['name'] == name), None)
        if not layout:
            raise ValueError(f"Layout '{name}' not found in template configuration")
        return layout
