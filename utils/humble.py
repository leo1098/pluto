import subprocess
import logging
import datetime
import os

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(levelname)s] %(name)s:%(funcName)s - %(message)s', level=logging.INFO)

def run_humble(website_url, output_folder_path):
    try:
        # Prepare the output filename and path
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"humble_{website_url.replace('://', '_')}_{timestamp}.pdf"
        output_file_path = os.path.join(output_folder_path, output_filename)

        # Construct the humble command
        command = [
            "humble",
            "-u", website_url,
            "-o", "pdf",
            "-of", output_filename,
            "-op", output_folder_path
        ]

        logging.info(f"Executing command: {' '.join(command)}")

        # Run the command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            logging.info(f"Humble analysis completed. Output saved to: {output_file_path}")
        else:
            logging.error(f"Humble analysis failed with return code {process.returncode}. Error: {stderr}")

    except FileNotFoundError:
        logging.error("Humble is not installed or not found in PATH.")
    except Exception as e:
        logging.error(f"An error occurred while running humble: {str(e)}")

def main(website_url, output_folder_path):
    try:
        logging.info(f"Running humble analysis against {website_url}")
        run_humble(website_url, output_folder_path)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    # Example usage
    website_url = "http://example.com"
    output_folder_path = "./test/"  # Save output in the current directory

    main(website_url, output_folder_path)