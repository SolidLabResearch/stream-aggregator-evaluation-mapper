# Feather RDF Mapper

A robust CLI tool to map and convert `.feather` data files into RDF triples (N-Triples format) based on a specified ontology.

## Features

- **Flexible Input**: Process a single `.feather` file or an entire directory recursively.
- **Metric Filtering**: Filter for specific metrics (e.g., `environment.temperature`, `org.dyamand.types.health.SpO2`).
- **Resampling**: Support for resampling data at a specified rate (in seconds).
- **Event Limiting**: Limit the number of processed events for quick testing.
- **Modern Packaging**: Uses `pyproject.toml` for easy installation and dependency management.

## Installation

It is highly recommended to use a virtual environment.

```bash
# Clone the repository
git clone <repo-url>
cd stream-aggregator-evaluation-mapper

# Install the package in editable mode
pip install -e .
```

This will install all necessary dependencies and provide the `feather-mapper` command globally in your environment.

## Usage

You can run the mapper using the installed `feather-mapper` command:

```bash
feather-mapper -i <input_path> -o <output_file> [options]
```

Alternatively, you can still run it as a script:

```bash
python3 mapper/cli.py -i <input_path> -o <output_file> [options]
```

### Arguments

- `-i`, `--input`: (Required) Path to a single `.feather` file or a directory containing `.feather` files.
- `-o`, `--output`: (Required) Path to the output `.nt` (RDF) file.
- `-m`, `--metrics`: (Optional) Space-separated list of metrics to filter by.
- `-n`, `--limit`: (Optional) Maximum number of total events to process.
- `-s`, `--sample-rate`: (Optional) Resampling rate in seconds.

### Examples

**Process a single file for specific metrics:**
```bash
feather-mapper -i data/participant6.feather -o output/results.nt -m environment.temperature wearable.skt
```

**Process a directory with resampling and an event limit:**
```bash
feather-mapper -i /path/to/dataset/ -o output/spo2_data.nt -m org.dyamand.types.health.SpO2 -n 1000 -s 2.0
```

## Testing

To run the unit tests:

```bash
python3 -m unittest discover mapper/tests
```

## License

This code is copyrighted by [Ghent University - imec](https://www.ugent.be/ea/idlab/en) and released under the [MIT Licence](./LICENCE).

## Contact

For any questions, please contact [Kush](mailto:kushagrasingh.bisen@ugent.be).
