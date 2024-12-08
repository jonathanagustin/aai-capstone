# src/aai_capstone/converter.py
from pathlib import Path
import subprocess
from typing import Optional
from . import OUTPUT_DIR


class PresentationConverter:
    """Handles conversion of PPTX files to PDF using LibreOffice headless mode."""

    @staticmethod
    def convert_to_pdf(
        pptx_path: Path,
        output_dir: Optional[Path] = None
    ) -> None:
        """Convert a PPTX file to PDF using LibreOffice.

        Args:
            pptx_path (Path): Path to the PPTX file.
            output_dir (Optional[Path]): Directory to save the PDF.
        """
        output_dir = output_dir or OUTPUT_DIR
        output_dir.mkdir(exist_ok=True)

        print(f"Converting {pptx_path.name} to PDF...")
        try:
            result = subprocess.run(
                [
                    'libreoffice',
                    '--headless',
                    '--convert-to', 'pdf',
                    str(pptx_path),
                    '--outdir', str(output_dir)
                ],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Successfully converted {pptx_path.name}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Conversion to PDF failed for {pptx_path.name}: {e.stderr}")

    @classmethod
    def convert_all(cls, directory: Optional[Path] = None) -> None:
        """Convert all PPTX files in the given directory to PDF."""
        directory = directory or OUTPUT_DIR
        pptx_files = list(directory.glob('*.pptx'))

        if not pptx_files:
            print("No PPTX files found to convert.")
            return

        print(f"Converting {len(pptx_files)} presentations to PDF...")
        for pptx_file in pptx_files:
            cls.convert_to_pdf(pptx_file, directory)
