import io
import json
import pathlib
import sys
import threading
from abc import ABC, abstractmethod
from datetime import datetime

from loguru import logger
from omegaconf import OmegaConf


class PipelineStage(ABC):
    """Abstract base class for pipeline stages."""

    def __init__(self):
        """Initialize the pipeline stage."""
        self.name = self.__class__.__name__.lower()
        self.cfg = OmegaConf.load("params.yaml")
  
    def execute(self):
        """Execute the pipeline stage in a separate thread."""
        logger.info(f"EXECUTING STAGE: {self.name}")
        start_time = datetime.now()

        def thread_run():
            try:
                self.run()
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(f"COMPLETED STAGE: {self.name} in {duration:.2f}s")
            except Exception as e:
                logger.error(f"FAILED STAGE: {self.name}")
                logger.error(f"Error: {str(e)}")
                logger.error("Full error:", exc_info=True)
                sys.exit(1)
            finally:
                logger.complete()

        thread = threading.Thread(target=thread_run)
        thread.start()
        thread.join()

    @abstractmethod
    def run(self):
        """Execute stage-specific logic."""
        pass
