#!/usr/bin/env python3
# Shebang for CLI: lets Unix run this script directly with python3 from PATH;
# ignored on import; optional on Windows (py can use it).

"""
JSONL to CSV Converter (Library + CLI)

This module provides a reusable JsonlToCsvConverter class that converts JSON
Lines (.jsonl) files to CSV. It can be used by other classes/modules and also
offers a CLI for direct usage.

Library usage example:
    from jsonl_to_csv import JsonlToCsvConverter

    converter = JsonlToCsvConverter(ensure_ascii=False, overwrite=True)
    result = converter.convert_file("input.jsonl")  # output auto: input.csv
    print(result["records_written"], "records written to", result["output_file"])

CLI examples:
    python jsonl_to_csv.py data.jsonl
    python jsonl_to_csv.py data.jsonl output.csv
    python jsonl_to_csv.py *.jsonl
    python jsonl_to_csv.py "2025-08-27.jsonl"
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple
import glob
import argparse


class JsonlToCsvConverter:
    """
    Converter for transforming JSONL files to CSV.

    Parameters:
        ensure_ascii: Passed to json.dumps for complex values. Defaults to False.
        overwrite: If True, existing output files are overwritten in convert_file.
        logger: Optional callable(str) -> None for messages (e.g., print or logging).
    """

    def __init__(
        self,
        *,
        ensure_ascii: bool = False,
        overwrite: bool = False,
        logger: Optional[callable] = None,
    ) -> None:
        self.ensure_ascii = ensure_ascii
        self.overwrite = overwrite
        self._log = logger if logger is not None else (lambda msg: None)

    def read_jsonl(self, file_path: str | Path) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Read a JSONL file and return (records, warnings).
        Does not raise on invalid JSON lines; those are skipped with a warning.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        data: List[Dict[str, Any]] = []
        warnings: List[str] = []

        with path.open("r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                s = line.strip()
                if not s:
                    continue
                try:
                    obj = json.loads(s)
                    if isinstance(obj, dict):
                        data.append(obj)
                    else:
                        warnings.append(
                            f"Skipping non-object JSON on line {line_num} in {path}"
                        )
                except json.JSONDecodeError as e:
                    warnings.append(
                        f"Skipping invalid JSON on line {line_num} in {path}: {e}"
                    )

        return data, warnings

    @staticmethod
    def get_all_keys(data: Sequence[Dict[str, Any]]) -> List[str]:
        """Extract all unique keys from a sequence of dictionaries."""
        all_keys: Set[str] = set()
        for item in data:
            if isinstance(item, dict):
                all_keys.update(item.keys())
        return sorted(all_keys)

    def flatten_value(self, value: Any) -> str:
        """Convert complex values to a string suitable for CSV."""
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=self.ensure_ascii)
        if value is None:
            return ""
        return str(value)

    def convert_file(
        self, input_file: str | Path, output_file: Optional[str | Path] = None
    ) -> Dict[str, Any]:
        """
        Convert a single JSONL file to CSV.

        Returns:
            {
              "input_file": str,
              "output_file": str,
              "records_written": int,
              "headers": List[str],
              "warnings": List[str],
            }

        Raises:
            FileNotFoundError, FileExistsError, ValueError, OSError on I/O errors.
        """
        in_path = Path(input_file)
        out_path = Path(output_file) if output_file is not None else in_path.with_suffix(".csv")

        records, warnings = self.read_jsonl(in_path)
        if not records:
            # No valid records; still create an empty CSV with no headers? Prefer to raise.
            raise ValueError(f"No valid JSON objects found in '{in_path}'")

        headers = self.get_all_keys(records)
        if not headers:
            raise ValueError(f"No keys found across JSON objects in '{in_path}'")

        if out_path.exists() and not self.overwrite:
            raise FileExistsError(f"Output file already exists: '{out_path}'")

        # Write CSV
        with out_path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction="ignore")
            writer.writeheader()
            for item in records:
                row = {key: self.flatten_value(item.get(key)) for key in headers}
                writer.writerow(row)

        self._log(
            f"Converted '{in_path}' -> '{out_path}' "
            f"({len(records)} records, {len(headers)} columns)"
        )

        return {
            "input_file": str(in_path),
            "output_file": str(out_path),
            "records_written": len(records),
            "headers": headers,
            "warnings": warnings,
        }

    def expand_patterns(self, patterns: Sequence[str]) -> List[str]:
        """
        Expand glob patterns into a list of file paths. Non-pattern strings are passed through.
        """
        expanded: List[str] = []
        for p in patterns:
            if any(ch in p for ch in ["*", "?", "["]):
                matches = glob.glob(p)
                if matches:
                    expanded.extend(matches)
                else:
                    self._log(f"No files match pattern '{p}'")
            else:
                expanded.append(p)
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for f in expanded:
            if f not in seen:
                seen.add(f)
                unique.append(f)
        return unique


def _run_cli() -> None:
    """
    CLI entry point that wraps JsonlToCsvConverter.
    Keeps prior behavior including optional overwrite prompt.
    """
    parser = argparse.ArgumentParser(
        description="Convert JSONL files to CSV format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python jsonl_to_csv.py data.jsonl
  python jsonl_to_csv.py data.jsonl output.csv
  python jsonl_to_csv.py *.jsonl
  python jsonl_to_csv.py "2025-08-27.jsonl"
        """,
    )

    parser.add_argument(
        "input_files",
        nargs="+",
        help="Input JSONL file(s) or pattern (e.g., *.jsonl)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output CSV file (only valid for single input file)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing CSV files without prompting",
    )

    args = parser.parse_args()

    converter = JsonlToCsvConverter(overwrite=args.overwrite, logger=print)

    # Expand inputs
    input_files = converter.expand_patterns(args.input_files)
    if not input_files:
        print("Error: No input files specified or found")
        raise SystemExit(1)

    if args.output and len(input_files) > 1:
        print("Error: Cannot specify single output file for multiple input files")
        raise SystemExit(1)

    exit_code = 0

    for input_file in input_files:
        in_path = Path(input_file)
        if not in_path.exists():
            print(f"Warning: File '{input_file}' not found, skipping...")
            continue

        out_path = Path(args.output) if args.output else in_path.with_suffix(".csv")

        # Prompt if exists and not --overwrite
        if out_path.exists() and not args.overwrite:
            response = input(f"File '{out_path}' already exists. Overwrite? (y/N): ")
            if response.lower() not in ["y", "yes"]:
                print(f"Skipping '{input_file}'")
                continue
            # Temporarily allow overwrite for this call
            temp_converter = JsonlToCsvConverter(overwrite=True, logger=print)
            converter_to_use = temp_converter
        else:
            converter_to_use = converter

        try:
            result = converter_to_use.convert_file(in_path, out_path)
            # Print a brief summary (including first few headers)
            headers = result["headers"]
            head_preview = ", ".join(headers[:5]) + ("..." if len(headers) > 5 else "")
            print(
                f"Successfully converted {result['records_written']} records to '{result['output_file']}'"
            )
            print(f"CSV contains {len(headers)} columns: {head_preview}")
            # Print any warnings
            for w in result["warnings"]:
                print(f"Warning: {w}")
        except FileExistsError as e:
            print(f"Error: {e}")
            exit_code = 1
        except FileNotFoundError as e:
            print(f"Error: {e}")
            exit_code = 1
        except ValueError as e:
            print(f"Warning: {e}")
        except OSError as e:
            print(f"Error writing CSV file '{out_path}': {e}")
            exit_code = 1

        print()  # readability between files

    raise SystemExit(exit_code)


if __name__ == "__main__":
    _run_cli()
