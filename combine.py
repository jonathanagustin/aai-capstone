#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
combine_files.py
================================================================================

This script recursively traverses a target directory (or a detected Git project
root if none is specified), collecting files that are not excluded by .combineignore
patterns. The collected files are combined into a single output file with
headers indicating their source paths. It also generates a visual tree structure
of the directory contents, excluding those matched by .combineignore patterns.
The output files and logs are stored in specified locations (default: a `debug`
directory structure).

Features:
- Traverse directories and optionally exclude files/directories using
  .combineignore patterns (supports Git-style wildmatch patterns).
- Combine selected file contents into a single output file, including a
  directory tree structure at the top.
- Respectable performance by using multiple worker threads.
- Logging (INFO-level to stderr, and DEBUG-level to a specified debug log file).
- User-provided arguments control various features like max file size, number
  of workers, and explicit inclusion of certain files.

This code is open-source ready and uses an MIT license as shown above.
"""

import argparse
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Constants and Defaults
DEFAULT_INCLUDE_FILES: List[str] = []
MAX_WORKERS = os.cpu_count() or 8
CHUNK_SIZE = 8192

# Attempt to import dependencies; install if missing
try:
    import pathspec
    from loguru import logger
except ImportError:
    subprocess.check_call([sys.executable, "-m", "ensurepip"])
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "pathspec", "loguru"]
    )
    import pathspec
    from loguru import logger

# Cache to store exclusion match results to avoid repetitive computations
path_match_cache: Dict[Tuple[str, str], bool] = {}


def cached_should_exclude(
    path: str, type_str: str, pathspec_obj: pathspec.PathSpec
) -> bool:
    """
    Determine if a given path should be excluded based on .combineignore patterns.
    Results are cached to improve performance.

    Args:
        path (str): The relative path to check.
        type_str (str): Type of the path ('dir' or 'file').
        pathspec_obj (pathspec.PathSpec): The pathspec object containing ignore patterns.

    Returns:
        bool: True if the path should be excluded, False otherwise.
    """
    cache_key = (path, type_str)
    if cache_key in path_match_cache:
        return path_match_cache[cache_key]

    if type_str == "dir":
        # Ensure directories are checked with a trailing slash for correct matching.
        path_with_slash = path.rstrip("/") + "/"
        is_excluded = pathspec_obj.match_file(path_with_slash)
    else:
        is_excluded = pathspec_obj.match_file(path)

    path_match_cache[cache_key] = is_excluded
    return is_excluded


def should_exclude_directory(
    directory_path: Path, pathspec_obj: pathspec.PathSpec, parent_dir: Path
) -> bool:
    """
    Check if a directory should be excluded based on .combineignore patterns.

    Args:
        directory_path (Path): The full directory path.
        pathspec_obj (pathspec.PathSpec): The loaded ignore patterns.
        parent_dir (Path): The parent directory serving as the relative root.

    Returns:
        bool: True if the directory should be excluded, False otherwise.
    """
    try:
        relative_path = str(directory_path.relative_to(parent_dir))
        return cached_should_exclude(relative_path, "dir", pathspec_obj)
    except Exception:
        logger.exception(f"Error checking directory exclusion for {directory_path}")
        return True


def should_exclude_file(
    file_path: Path,
    include_files: Set[Path],
    pathspec_obj: pathspec.PathSpec,
    max_file_size_kb: int,
    parent_dir: Path,
) -> bool:
    """
    Check if a file should be excluded.
    Criteria:
    - If the file is explicitly included, it won't be excluded.
    - If the file exceeds the max size limit, exclude it.
    - If the file matches the .combineignore patterns, exclude it.

    Args:
        file_path (Path): The file path to evaluate.
        include_files (Set[Path]): Set of explicitly included files.
        pathspec_obj (pathspec.PathSpec): The loaded ignore patterns.
        max_file_size_kb (int): Maximum file size in KB.
        parent_dir (Path): The parent directory serving as the relative root.

    Returns:
        bool: True if the file should be excluded, False otherwise.
    """
    # Check explicit inclusion
    if file_path.resolve() in include_files:
        return False

    try:
        if file_path.stat().st_size > max_file_size_kb * 1024:
            return True
        relative_path = str(file_path.relative_to(parent_dir))
        return cached_should_exclude(relative_path, "file", pathspec_obj)
    except Exception:
        logger.exception(f"Error checking file exclusion for {file_path}")
        return True


def process_single_file(file_path: Path, parent_dir: Path) -> str:
    """
    Read a single file and return its content prefixed with a header
    indicating the file's relative path. If reading fails, return an error message.

    Args:
        file_path (Path): The file to read.
        parent_dir (Path): The parent directory to determine relative paths.

    Returns:
        str: The file's content as a single string, including a header.
    """
    separator_line = "# " + "-" * 62 + " #"
    relative_path = file_path.relative_to(parent_dir)
    header = f"\n\n{separator_line}\n# Source: {relative_path} \n\n"
    content = [header]

    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as infile:
            while True:
                chunk = infile.read(CHUNK_SIZE)
                if not chunk:
                    break
                content.append(chunk)
        return "".join(content)
    except Exception:
        logger.exception(f"Error reading file {file_path}")
        return f"{header}# Error reading file: {traceback.format_exc()}\n"


def traverse_and_collect_files(
    directory: Path,
    parent_dir: Path,
    pathspec_obj: pathspec.PathSpec,
    include_files: Set[Path],
    max_file_size_kb: int,
) -> List[Path]:
    """
    Recursively traverse the given directory, collecting files that are not excluded.

    Sorts directories and files alphabetically (directories first) and recurses into
    non-excluded directories. Files that pass the exclusion checks are collected.

    Args:
        directory (Path): The current directory to process.
        parent_dir (Path): The root directory used for relative paths.
        pathspec_obj (pathspec.PathSpec): The loaded ignore patterns.
        include_files (Set[Path]): Files explicitly included.
        max_file_size_kb (int): Maximum file size in KB.

    Returns:
        List[Path]: A list of file paths that should be processed.
    """
    files_to_process: List[Path] = []
    try:
        with os.scandir(directory) as entries:
            # Sort directories first, then by name
            sorted_entries = sorted(
                entries, key=lambda x: (not x.is_dir(), x.name.lower())
            )
            for entry in sorted_entries:
                entry_path = Path(entry.path)
                if entry.is_dir():
                    if should_exclude_directory(entry_path, pathspec_obj, parent_dir):
                        continue
                    # Recurse into the directory
                    files_to_process.extend(
                        traverse_and_collect_files(
                            entry_path,
                            parent_dir,
                            pathspec_obj,
                            include_files,
                            max_file_size_kb,
                        )
                    )
                elif entry.is_file():
                    # Check if file should be included
                    if not should_exclude_file(
                        entry_path,
                        include_files,
                        pathspec_obj,
                        max_file_size_kb,
                        parent_dir,
                    ):
                        files_to_process.append(entry_path)
    except PermissionError as e:
        logger.warning(f"Permission denied accessing {directory}: {e}")
    except Exception:
        logger.exception(f"Error traversing {directory}")
    return files_to_process


def generate_tree_structure(
    directory: Path,
    parent_dir: Path,
    pathspec_obj: pathspec.PathSpec,
    include_files: Set[Path],
    prefix: str = "",
) -> str:
    """
    Generate a tree-structured string representing directories and files,
    respecting exclusion rules.

    Args:
        directory (Path): The directory to generate a tree for.
        parent_dir (Path): The parent directory for relative paths.
        pathspec_obj (pathspec.PathSpec): The loaded ignore patterns.
        include_files (Set[Path]): Files explicitly included.
        prefix (str): A string prefix used for tree drawing (internal use).

    Returns:
        str: A multi-line string representing the directory tree.
    """
    output = []
    try:
        entries = sorted(
            directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())
        )
    except PermissionError as e:
        logger.warning(f"Permission denied accessing {directory}: {e}")
        return ""

    for i, entry in enumerate(entries):
        is_last_entry = (i == len(entries) - 1)
        connector = "└── " if is_last_entry else "├── "

        if entry.is_dir():
            if should_exclude_directory(entry, pathspec_obj, parent_dir):
                continue
            output.append(f"{prefix}{connector}{entry.name}")
            extension = "    " if is_last_entry else "│   "
            subtree = generate_tree_structure(
                entry, parent_dir, pathspec_obj, include_files, prefix + extension
            )
            if subtree:
                output.append(subtree)
        elif entry.is_file():
            if should_exclude_file(
                entry, include_files, pathspec_obj, sys.maxsize, parent_dir
            ):
                continue
            output.append(f"{prefix}{connector}{entry.name}")

    return "\n".join(output)


def load_combineignore(combineignore_path: Path, label: str) -> pathspec.PathSpec:
    """
    Load ignore patterns from a specified .combineignore file. If the file
    does not exist or cannot be read, returns an empty pattern set.

    Args:
        combineignore_path (Path): Path to the .combineignore file.
        label (str): A label indicating the type (e.g., "global" or "target").

    Returns:
        pathspec.PathSpec: A pathspec object containing the loaded patterns.
    """
    path_match_cache.clear()
    ignore_patterns: List[str] = []
    if combineignore_path.exists():
        try:
            with combineignore_path.open("r", encoding="utf-8") as f:
                ignore_patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith("#")
                ]
            logger.debug(f"Loaded {label} ignore patterns: {ignore_patterns}")
        except Exception:
            logger.exception(f"Error reading {combineignore_path}")
    else:
        logger.debug(f"No {label} .combineignore found.")

    return pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns)


def find_combineignore(start_dir: Path) -> Path:
    """
    Search upward from start_dir for a .combineignore file.
    Returns the first found path, or an empty Path if none found.

    Args:
        start_dir (Path): The starting directory for the search.

    Returns:
        Path: The found .combineignore file path or empty if none found.
    """
    for directory in [start_dir] + list(start_dir.parents):
        combineignore_path = directory / ".combineignore"
        if combineignore_path.exists():
            logger.debug(f"Found .combineignore at {combineignore_path}")
            return combineignore_path
    logger.debug("No .combineignore file found in the directory hierarchy.")
    return Path()


def get_git_project_root() -> Path:
    """
    Placeholder function to determine a Git project root directory.

    Currently returns '.' as the project root.
    This can be extended to run 'git rev-parse --show-toplevel' to find the actual root.

    Returns:
        Path: The detected Git project root directory.
    """
    # Future Improvement: Add logic to detect actual git root if desired.
    return Path(".")


def setup_logging(debug_file: Path) -> None:
    """
    Configure logging with loguru. Outputs INFO-level logs to stderr and
    DEBUG-level logs to a file.

    Args:
        debug_file (Path): Path to the debug log file.
    """
    logger.remove()
    logger.add(debug_file, level="DEBUG", format="{time} {level} {message}", mode="w")
    logger.add(sys.stderr, level="INFO", format="{time} {level} {message}")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for controlling input/output directories,
    logging, file size limits, etc.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Combine files and generate directory tree structure."
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=None,
        help="Directory to process (default: detected via Git root).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="debug/combined.txt",
        help="Output file for combined content (default: debug/combined.txt).",
    )
    parser.add_argument(
        "-t",
        "--tree",
        type=str,
        default="debug/tree.txt",
        help="Output file for tree structure (default: debug/tree.txt).",
    )
    parser.add_argument(
        "--debug",
        type=str,
        default="debug/debug.log",
        help="Debug log file (default: debug/debug.log).",
    )
    parser.add_argument(
        "--include-files",
        nargs="+",
        default=[],
        help="Files to include even if excluded by .combineignore.",
    )
    parser.add_argument(
        "--max-file-size",
        type=int,
        default=10240,
        help="Max file size in KB to process (default: 10240KB).",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=MAX_WORKERS,
        help="Maximum number of worker threads (default: number of CPU cores).",
    )
    parser.add_argument(
        "--global-ignore",
        type=str,
        default=".combineignore",
        help="Path to the global .combineignore file (default: .combineignore).",
    )
    return parser.parse_args()


def combine_pathspecs(
    global_pathspec: pathspec.PathSpec, target_pathspec: pathspec.PathSpec
) -> pathspec.PathSpec:
    """
    Combine two pathspec objects (global and target) into a single set of patterns.

    Args:
        global_pathspec (pathspec.PathSpec): Global ignore patterns.
        target_pathspec (pathspec.PathSpec): Target-level ignore patterns.

    Returns:
        pathspec.PathSpec: A combined pathspec object containing all patterns.
    """
    combined_patterns = []
    if hasattr(global_pathspec, "patterns"):
        combined_patterns.extend(global_pathspec.patterns)
    if hasattr(target_pathspec, "patterns"):
        combined_patterns.extend(target_pathspec.patterns)
    return pathspec.PathSpec(combined_patterns)


def main() -> None:
    """
    Main function to orchestrate:
    - Argument parsing
    - Logging setup
    - Ignore patterns loading
    - File traversal, filtering, and content combination
    - Tree structure generation
    - Output result writing

    On completion, the combined file includes the directory tree at its top.
    """
    start_time = time.time()
    args = parse_arguments()
    script_dir = Path(__file__).resolve().parent

    # Find and load global ignore patterns
    combineignore_path = find_combineignore(script_dir)
    global_pathspec = (
        load_combineignore(combineignore_path, "global")
        if combineignore_path.exists()
        else pathspec.PathSpec.from_lines("gitwildmatch", [])
    )

    # Determine project directory (by default, returns '.')
    try:
        project_dir = get_git_project_root()
    except RuntimeError:
        logger.warning("Using the script's directory as the project root.")
        project_dir = script_dir

    parent_dir = Path(args.directory).resolve() if args.directory else project_dir

    # Load target-level ignore patterns
    target_combineignore_path = parent_dir / ".combineignore"
    target_pathspec = load_combineignore(target_combineignore_path, "target")

    # Combine global and target patterns
    combined_pathspec = combine_pathspecs(global_pathspec, target_pathspec)

    # Set of explicitly included files
    include_files = {(parent_dir / p).resolve() for p in args.include_files} | {
        (parent_dir / p).resolve() for p in DEFAULT_INCLUDE_FILES
    }

    output_file = Path(args.output).resolve()
    tree_file = Path(args.tree).resolve()
    debug_file = Path(args.debug).resolve()
    debug_folder = debug_file.parent
    debug_folder.mkdir(parents=True, exist_ok=True)

    setup_logging(debug_file)

    # Clean up old output files if they exist
    for f in [output_file, tree_file]:
        try:
            if f.exists():
                f.unlink()
        except Exception:
            logger.exception(f"Error removing existing output file {f}")
            sys.exit(1)

    logger.info(f"Starting program. Processing directory: {parent_dir}")

    try:
        # Collect files to process
        files_to_process = traverse_and_collect_files(
            parent_dir, parent_dir, combined_pathspec, include_files, args.max_file_size
        )
        logger.info(f"Total files to process: {len(files_to_process)}")
        logger.info(f"Combining files into {output_file} using {args.max_workers} threads")

        # Read and combine file contents in parallel
        combined_contents = []
        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            future_to_file = {
                executor.submit(process_single_file, fp, parent_dir): fp
                for fp in files_to_process
            }
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    content = future.result()
                    combined_contents.append((file_path, content))
                except Exception:
                    logger.exception(f"Error processing file {file_path}")
                    combined_contents.append(
                        (file_path, f"# Error processing file: {traceback.format_exc()}\n")
                    )

        # Sort contents by file path for consistent output ordering
        combined_contents.sort(key=lambda x: str(x[0]))

        # Write combined file contents
        with output_file.open("w", encoding="utf-8") as outfile:
            for _, content in combined_contents:
                outfile.write(content)

        # Generate and write the tree structure
        logger.info(f"Generating tree structure into {tree_file}")
        tree_output = f"{parent_dir}\n" + generate_tree_structure(
            parent_dir, parent_dir, combined_pathspec, include_files
        )
        with tree_file.open("w", encoding="utf-8") as f:
            f.write(tree_output)

        # Prepend tree structure to the combined file
        with output_file.open("r+", encoding="utf-8") as f:
            existing_content = f.read()
            f.seek(0)
            f.write(f"{tree_output}\n\n{existing_content}")

        # Log a preview of the combined output
        logger.info(f"First 20 lines of {output_file}:")
        try:
            with output_file.open("r", encoding="utf-8") as f:
                for _ in range(20):
                    line = f.readline()
                    if not line:
                        break
                    logger.info(line.strip())
        except Exception:
            logger.exception("Error reading lines from output file for preview.")

        logger.info("Tree structure:")
        logger.info(tree_output)

        # Display debug info content
        logger.debug(f"Debug information (from {debug_file}):")
        try:
            with debug_file.open("r", encoding="utf-8") as f:
                for line in f:
                    logger.debug(line.strip())
        except Exception:
            logger.exception("Could not read debug information.")

        logger.info(f"All output files are located in: {output_file.parent}")

    except Exception:
        logger.exception("An error occurred during processing.")
    finally:
        elapsed = time.time() - start_time
        logger.info(f"Program completed in {elapsed:.2f} seconds.")


if __name__ == "__main__":
    main()
