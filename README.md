# switch-logs
Get logs from a local switch


# JSONL to CSV Converter

A comprehensive Python script that converts JSONL files to CSV format with automatic column detection and robust error handling.

## Features

1. **Automatic Column Detection**: Scans all JSON objects to find unique keys and creates CSV columns accordingly
2. **Multiple File Support**: Can process single files or multiple files using glob patterns (like `*.jsonl`)
3. **Flexible Output**: Auto-generates output filenames or accepts custom output names
4. **Error Handling**: Gracefully handles invalid JSON lines and missing files
5. **Complex Data Handling**: Converts nested objects and arrays to JSON strings in CSV cells
6. **Safety Features**: Prompts before overwriting existing files (unless `--overwrite` is used)

## Usage Examples

```bash
# Convert a single file (creates 2025-08-27.csv)
python jsonl_to_csv.py "2025-08-27.jsonl"

# Convert with custom output name
python jsonl_to_csv.py "2025-08-27.jsonl" -o "my_data.csv"

# Convert multiple files at once
python jsonl_to_csv.py *.jsonl

# Force overwrite existing files
python jsonl_to_csv.py "2025-08-27.jsonl" --overwrite
```

## Command Line Arguments

- `input_files`: One or more JSONL files or glob patterns to convert
- `-o, --output`: Custom output CSV file name (only valid for single input file)
- `--overwrite`: Overwrite existing CSV files without prompting

## Key Functions

- **`read_jsonl()`**: Reads the JSONL file line by line, parsing each JSON object
- **`get_all_keys()`**: Discovers all unique keys across all JSON objects to create CSV headers
- **`flatten_value()`**: Converts complex data types (objects, arrays) to string representations
- **`jsonl_to_csv()`**: Main conversion logic

## Edge Cases Handled

The script handles edge cases like:
- Empty lines in JSONL files
- Invalid JSON on individual lines (skips with warning)
- Missing keys in some objects (fills with empty values)
- Unicode characters (preserves with UTF-8 encoding)
- Nested data structures (converts to JSON strings)

## Requirements

- Python 3.6+
- Standard library modules only (no external dependencies)

## Example JSONL Input

```jsonl
{"name": "Alice", "age": 30, "city": "New York", "hobbies": ["reading", "hiking"]}
{"name": "Bob", "age": 25, "city": "San Francisco", "department": "Engineering"}
{"name": "Carol", "age": 35, "hobbies": ["cooking"], "married": true}
```

## Example CSV Output

```csv
age,city,department,hobbies,married,name
30,New York,,["reading", "hiking"],,Alice
25,San Francisco,Engineering,,,Bob
35,,,["cooking"],true,Carol
```

## Installation

No installation required. Simply download the `jsonl_to_csv.py` script and run it with Python 3.6+.

## License

This script is provided as-is for educational and practical use.
