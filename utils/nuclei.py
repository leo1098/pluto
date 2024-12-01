import subprocess
import logging
import datetime
from datetime import datetime
import os

logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(levelname)s] %(name)s:%(funcName)s - %(message)s', level=logging.INFO)

def run_nuclei(website_url: str, output_folder_path: str) -> None:
    """
    Run a Nuclei scan on a target URL.

    Args:
        target (str): The target URL or file containing URLs.
        output_file (str): Path to save the Nuclei output.

    Raises:
        subprocess.CalledProcessError: If the Nuclei command fails.
    """

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"nuclei_{website_url.replace('://', '_')}_{timestamp}.txt"
    output_file_path = os.path.join(output_folder_path, output_filename)

    command = ["nuclei", "-u", website_url, "-o", output_file_path]

    try:
        subprocess.run(command, check=True)
        logging.info(f"Nuclei scan completed successfully. Results saved to {output_file_path}.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during scan: {e}")

# Example usage
if __name__ == "__main__":
    run_nuclei(
        target="https://example.com",
        output_folder_path="./test/"
    )
