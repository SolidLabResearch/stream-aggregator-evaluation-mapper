import os
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime
from .core import annotate_event, logger

def process_file(file_path: str, output_file: str, metrics: Optional[List[str]], limit: Optional[int] = None, sample_rate: Optional[float] = None) -> int:
    """
    Processes a single feather file and appends results to the output file.
    
    Args:
        file_path: Path to the .feather file.
        output_file: Path to the .nt file where results will be appended.
        metrics: Optional list of metric IDs to filter for.
        limit: Optional maximum number of events to process from this file.
        sample_rate: Optional resampling rate in seconds.
        
    Returns:
        The number of successfully processed events.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return 0

    logger.info(f"Processing file: {file_path}")
    try:
        df = pd.read_feather(file_path)
    except Exception as e:
        logger.error(f"Error reading feather file {file_path}: {e}")
        return 0

    # Filter by metrics if provided
    if metrics:
        df = df[df['Metric'].isin(metrics)]

    if df.empty:
        logger.warning(f"No matching metrics found in {file_path}")
        return 0

    # Handle resampling if requested
    if sample_rate:
        df['Sampling-Timestamp'] = pd.to_datetime(df['Timestamp'].astype(str))
        df.set_index('Sampling-Timestamp', inplace=True)
        df = df.resample(f'{sample_rate}S').first().dropna().reset_index()

    count = 0
    current_date = datetime.now()
    date_prefix = current_date.strftime("%Y-%m-%d")

    with open(output_file, 'a') as f:
        for _, row in df.iterrows():
            if limit and count >= limit:
                break

            # Original logic for timestamp construction
            # Assumes 'Timestamp' might be HH:MM:SS.mmm or similar
            ts_str = str(row['Timestamp'])
            
            # Check if it looks like just a time (e.g., HH:MM:SS.mmm)
            # A full ISO timestamp should have a date part (e.g., YYYY-MM-DD)
            if len(ts_str) < 15 or 'T' not in ts_str and ts_str.count('-') < 2:
                # Prepend the current date
                parts = ts_str.split()
                time_part = parts[-1] if parts else ts_str
                time_value = f"{date_prefix}T{time_part}"
                if '.' not in time_value:
                    time_value += ".000"
                if not time_value.endswith('Z'):
                    time_value += 'Z'
            else:
                time_value = ts_str

            event: Dict[str, Any] = {
                'sourceId': row['Sensor'],
                'metricId': row['Metric'],
                'value': row['Value'],
                'timestamp': time_value
            }

            result = annotate_event(event)
            if result:
                f.write(result + '\n')
                count += 1

    logger.info(f"Finished processing {file_path}. Processed {count} events.")
    return count

def process_input(input_path: str, output_file: str, metrics: Optional[List[str]], limit: Optional[int] = None, sample_rate: Optional[float] = None) -> None:
    """
    Handles both single file and directory input, processing all .feather files found.
    
    Args:
        input_path: Path to a file or directory.
        output_file: Path to the .nt file for output.
        metrics: Optional list of metrics to filter.
        limit: Optional total maximum events across all files.
        sample_rate: Optional resampling rate.
    """
    # Ensure output file is clean or at least exists
    if os.path.exists(output_file):
        logger.info(f"Appending to existing output file: {output_file}")
    else:
        logger.info(f"Creating new output file: {output_file}")

    total_count = 0
    if os.path.isfile(input_path):
        total_count = process_file(input_path, output_file, metrics, limit, sample_rate)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.endswith('.feather'):
                    file_path = os.path.join(root, file)
                    current_limit = limit - total_count if limit else None
                    if limit and current_limit <= 0:
                        break
                    count = process_file(file_path, output_file, metrics, current_limit, sample_rate)
                    if count:
                        total_count += count
            if limit and total_count >= limit:
                break
    else:
        logger.error(f"Invalid input path: {input_path}")

    logger.info(f"Total events processed: {total_count}")
