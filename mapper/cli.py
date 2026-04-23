import argparse
import sys
import os

# Add the parent directory to sys.path to allow running this script directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mapper.process import process_input
from mapper.core import logger

def main() -> None:
    """
    Entrypoint for the Feather to RDF Mapper CLI.
    Parses command line arguments and initiates the data processing.
    """
    parser = argparse.ArgumentParser(description="Feather to RDF (Turtle) Mapper CLI")
    
    parser.add_argument("-i", "--input", required=True, 
                        help="Path to a single .feather file or a directory containing .feather files")
    
    parser.add_argument("-o", "--output", required=True, 
                        help="Path to the output .nt (RDF) file")
    
    parser.add_argument("-m", "--metrics", nargs="+", 
                        help="List of metrics to filter by (e.g., environment.temperature wearable.skt)")
    
    parser.add_argument("-n", "--limit", type=int, 
                        help="Maximum number of total events to process")
    
    parser.add_argument("-s", "--sample-rate", type=float, 
                        help="Resampling rate in seconds (optional)")

    args = parser.parse_args()

    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        process_input(
            input_path=args.input,
            output_file=args.output,
            metrics=args.metrics,
            limit=args.limit,
            sample_rate=args.sample_rate
        )
    except KeyboardInterrupt:
        logger.info("Process interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
