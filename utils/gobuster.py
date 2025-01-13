import subprocess
import logging
import datetime
from datetime import datetime
import os

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(levelname)s] %(name)s:%(funcName)s - %(message)s', level=logging.INFO)

WORDLIST_BIG = "/usr/share/wordlists/seclists/Discovery/Web-Content/big.txt"
WORDLIST_TEST = "./test/sample_wordlist.txt"

def run_gobuster(website_url, output_file_path, threads=10, wordlist=WORDLIST_TEST):

    # Construct the gobuster command
    command = [
        "gobuster", "dir",
        "--url", website_url,
        "--wordlist", wordlist,
        "--threads", str(threads),
        "--no-error",
        "-k"
    ]

    try:
        with open(output_file_path, 'w+') as f:
            
            process = subprocess.Popen(command, stdout=f, stderr=subprocess.PIPE, text=True)
            process.wait()

        logging.info(f"Output written to: {output_file_path}")

        if process.returncode != 0:
            logging.error(f"Gobuster exited with errors: {process.stderr.read()}")
            # new_length= parse_error()
            # command.append(new_length)


    except FileNotFoundError:
        logging.info("Gobuster is not installed or output file not found in PATH.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


def main(website_url, output_folder_path):
    try:
        # Filename  
        output_filename = f"gobuster_{website_url.replace('://', '_')}_{datetime.today().strftime('%Y%m%d')}.txt"
        output_file_path = os.path.join(output_folder_path, output_filename)


        logging.info(f"Running gobuster against {website_url}")
        run_gobuster(website_url=website_url, wordlist=WORDLIST_BIG, output_file_path=output_file_path)

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    # Example usage
    website_url = "http://example.com"
    # website_url = "http://127.0.0.1:8080"

    # Filename
    output_folder_path = "./test/"
    output_filename = f"gobuster_{website_url.replace('://', '_')}_{datetime.today().strftime('%Y%m%d')}.txt"
    output_file_path = os.path.join(output_folder_path, output_filename)

    logging.info(f"Running gobuster against {website_url}")
    run_gobuster(website_url=website_url, wordlist=WORDLIST_TEST, output_file_path=output_file_path)