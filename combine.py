#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Set, Tuple

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


DEFAULT_INCLUDE_FILES = []
MAX_WORKERS = os.cpu_count() or 8
CHUNK_SIZE = 8192

path_match_cache: Dict[Tuple[str, str], bool] = {}


def cached_should_exclude(
    path: str, type_str: str, pathspec_obj: pathspec.PathSpec
) -> bool:
    cache_key = (path, type_str)
    if cache_key in path_match_cache:
        return path_match_cache[cache_key]

    if type_str == "dir":
        path_with_slash = path.rstrip("/") + "/"
        is_excluded = pathspec_obj.match_file(path_with_slash)
    else:
        is_excluded = pathspec_obj.match_file(path)

    path_match_cache[cache_key] = is_excluded
    return is_excluded


def should_exclude_directory(
    directory_path: Path, pathspec_obj: pathspec.PathSpec, parent_dir: Path
) -> bool:
    try:
        relative_path = str(directory_path.relative_to(parent_dir))
        return cached_should_exclude(relative_path, "dir", pathspec_obj)
    except Exception as e:
        logger.error(f"Error checking directory exclusion for {directory_path}: {e}")
        return True


def should_exclude_file(
    file_path: Path,
    include_files: Set[Path],
    pathspec_obj: pathspec.PathSpec,
    max_file_size_kb: int,
    parent_dir: Path,
) -> bool:
    if file_path.resolve() in include_files:
        return False

    try:
        if file_path.stat().st_size > max_file_size_kb * 1024:
            return True
        relative_path = str(file_path.relative_to(parent_dir))
        return cached_should_exclude(relative_path, "file", pathspec_obj)
    except Exception as e:
        logger.error(f"Error checking file exclusion for {file_path}: {e}")
        return True


def process_single_file(file_path: Path, parent_dir: Path) -> str:
    separator_line = "# " + "-" * 62 + " #"
    relative_path = file_path.relative_to(parent_dir)
    content = [f"\n\n{separator_line}\n# Source: {relative_path} \n\n"]

    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as infile:
            while chunk := infile.read(CHUNK_SIZE):
                content.append(chunk)
        return "".join(content)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return f"{content[0]}# Error reading file: {e}\n"


def traverse_and_collect_files(
    directory: Path,
    parent_dir: Path,
    pathspec_obj: pathspec.PathSpec,
    include_files: Set[Path],
    max_file_size_kb: int,
) -> List[Path]:
    files_to_process = []
    try:
        with os.scandir(directory) as entries:
            sorted_entries = sorted(
                entries, key=lambda x: (not x.is_dir(), x.name.lower())
            )
            for entry in sorted_entries:
                entry_path = Path(entry.path)
                if entry.is_dir():
                    if should_exclude_directory(entry_path, pathspec_obj, parent_dir):
                        continue
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
    except Exception as e:
        logger.error(f"Error traversing {directory}: {e}")
    return files_to_process


def generate_tree_structure(
    directory: Path,
    parent_dir: Path,
    pathspec_obj: pathspec.PathSpec,
    include_files: Set[Path],
    prefix: str = "",
) -> str:
    output = []
    try:
        entries = sorted(
            directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())
        )
    except PermissionError as e:
        logger.warning(f"Permission denied accessing {directory}: {e}")
        return ""

    for i, entry in enumerate(entries):
        is_last_entry = i == len(entries) - 1
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
    path_match_cache.clear()
    ignore_patterns = []
    if combineignore_path.exists():
        try:
            with combineignore_path.open("r") as f:
                ignore_patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith("#")
                ]
            logger.debug(f"Loaded {label} ignore patterns: {ignore_patterns}")
        except Exception as e:
            logger.error(f"Error reading {combineignore_path}: {e}")
    return pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns)


def find_combineignore(start_dir: Path) -> Path:
    for directory in [start_dir] + list(start_dir.parents):
        combineignore_path = directory / ".combineignore"
        if combineignore_path.exists():
            print(f"Found .combineignore at {combineignore_path}")
            return combineignore_path
    print("No .combineignore file found in the directory hierarchy.")
    return Path()


def get_git_project_root() -> Path:
    return Path(".")


def setup_logging(debug_file: Path) -> None:
    logger.remove()
    logger.add(debug_file, level="DEBUG", format="{time} {level} {message}", mode="w")
    logger.add(sys.stderr, level="INFO", format="{time} {level} {message}")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combine files and generate directory tree structure."
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=None,
        help="Directory to process (default: detected via Git)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="debug/combined.txt",
        help="Output file for combined content",
    )
    parser.add_argument(
        "-t",
        "--tree",
        type=str,
        default="debug/tree.txt",
        help="Output file for tree structure",
    )
    parser.add_argument(
        "--debug", type=str, default="debug/debug.log", help="Debug log file"
    )
    parser.add_argument(
        "--include-files",
        nargs="+",
        default=[],
        help="Files to include even if excluded by .combineignore",
    )
    parser.add_argument(
        "--max-file-size",
        type=int,
        default=10240,
        help="Maximum file size in KB to process",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=MAX_WORKERS,
        help="Maximum number of worker threads",
    )
    parser.add_argument(
        "--global-ignore",
        type=str,
        default=".combineignore",
        help="Path to the global .combineignore file",
    )
    return parser.parse_args()


def combine_pathspecs(
    global_pathspec: pathspec.PathSpec, target_pathspec: pathspec.PathSpec
) -> pathspec.PathSpec:
    combined_patterns = []
    if hasattr(global_pathspec, "patterns"):
        combined_patterns.extend(global_pathspec.patterns)
    if hasattr(target_pathspec, "patterns"):
        combined_patterns.extend(target_pathspec.patterns)
    return pathspec.PathSpec(combined_patterns)


def main():
    start_time = time.time()
    args = parse_arguments()
    script_dir = Path(__file__).resolve().parent
    combineignore_path = find_combineignore(script_dir)

    try:
        project_dir = get_git_project_root()
    except RuntimeError:
        project_dir = script_dir
        print("Using the script's directory as the project root.")

    parent_dir = Path(args.directory).resolve() if args.directory else project_dir

    global_pathspec = (
        load_combineignore(combineignore_path, "global")
        if combineignore_path.exists()
        else pathspec.PathSpec.from_lines("gitwildmatch", [])
    )

    target_combineignore_path = parent_dir / ".combineignore"
    target_pathspec = load_combineignore(target_combineignore_path, "target")
    combined_pathspec = combine_pathspecs(global_pathspec, target_pathspec)

    include_files = {(parent_dir / p).resolve() for p in args.include_files} | {
        (parent_dir / p).resolve() for p in DEFAULT_INCLUDE_FILES
    }

    output_file = Path(args.output).resolve()
    tree_file = Path(args.tree).resolve()
    debug_file = Path(args.debug).resolve()
    debug_folder = debug_file.parent
    debug_folder.mkdir(parents=True, exist_ok=True)

    setup_logging(debug_file)

    try:
        if output_file.exists():
            output_file.unlink()
        if tree_file.exists():
            tree_file.unlink()
    except Exception as e:
        logger.error(f"Error removing existing output files: {e}")
        sys.exit(1)

    logger.info(f"Starting program. Processing directory: {parent_dir}")

    try:
        files_to_process = traverse_and_collect_files(
            parent_dir, parent_dir, combined_pathspec, include_files, args.max_file_size
        )
        logger.info(f"Total files to process: {len(files_to_process)}")
        logger.info(
            f"Combining files into {output_file} using {args.max_workers} threads"
        )

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
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    combined_contents.append(
                        (file_path, f"# Error processing file: {e}\n")
                    )

        combined_contents.sort(key=lambda x: str(x[0]))

        with output_file.open("w", encoding="utf-8") as outfile:
            for _, content in combined_contents:
                outfile.write(content)

        logger.info(f"Generating tree structure into {tree_file}")
        tree_output = f"{parent_dir}\n" + generate_tree_structure(
            parent_dir, parent_dir, combined_pathspec, include_files
        )
        with tree_file.open("w", encoding="utf-8") as f:
            f.write(tree_output)

        with output_file.open("r+", encoding="utf-8") as f:
            content = f.read()
            f.seek(0)
            f.write(f"{tree_output}\n\n{content}")

        logger.info(f"\nFirst few lines of {output_file}:")
        with output_file.open("r", encoding="utf-8") as f:
            print("".join(f.readline() for _ in range(20)))

        logger.info(f"\nTree structure (from {tree_file}):")
        print(tree_output)

        logger.info(f"\nDebug information (from {debug_file}):")
        with debug_file.open("r", encoding="utf-8") as f:
            print(f.read())

        logger.info(
            f"\nAll output files are located in the debug folder: {output_file.parent}"
        )

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.debug(f"Error details: {traceback.format_exc()}")
    finally:
        elapsed = time.time() - start_time
        logger.info(f"Program completed in {elapsed:.2f} seconds.")


if __name__ == "__main__":
    main()
