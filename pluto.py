import argparse
import sys
from utils import csp
from utils import gobuster
from utils import humble
from utils import nuclei
import logging
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(format='[%(levelname)s] %(name)s:%(funcName)s - %(message)s', level=logging.INFO)

def normalize_url(url):
    """Ensure the URL has a valid scheme. Default to HTTPS if missing."""
    parsed_url = urlparse(url)

    if not parsed_url.scheme:
        logging.info(f"No scheme found for {url}. Defaulting to 'https://'.")
        return f"https://{url}"

    return url

def run_csp(website_url, output_folder_path):
    csp.main(website_url=website_url, output_folder_path=output_folder_path)

def run_gobuster(website_url, output_folder_path):
    gobuster.main(website_url=website_url, output_folder_path=output_folder_path)    

def run_humble(website_url, output_folder_path):
    humble.run(website_url=website_url, output_folder_path=output_folder_path)    

def run_nuclei(website_url, output_folder_path):
    nuclei.run(website_url=website_url, output_folder_path=output_folder_path)    


def process_all(website_url, project_path):
    run_csp(website_url, project_path)
    run_gobuster(website_url, project_path)
    run_humble(website_url, project_path)
    run_nuclei(website_url, project_path)

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="A CLI script to automatically perform WAPT tasks.")

    
    parser.add_argument("task", nargs="+", choices=["csp", "gobuster", "humble", "nuclei", "all"],
                        help="Specify which task(s) to execute. Use 'all' as the only argument to execute everything.")

    # Mandatory options
    parser.add_argument("--url", required=True, help="The target url (either domain or full url)")
    parser.add_argument("--project-path", required=True, help="The project folder path")

    # Optional Argumnents
    parser.add_argument("--cookies", required=False, help="Cookies to use: C1=V1; C2=V2;")


    # Parse the arguments
    args = parser.parse_args()

    # Ensure 'all' is the only argument if selected
    if "all" in args.task and len(args.task) > 1:
        logging.error("If 'all' is specified it must be the only argument.")
        sys.exit(1)

    # Execute based on the selected task(s)
    url = normalize_url(args.url)
    output_folder_path = args.project_path

    if "all" in args.task:
        process_all(url, output_folder_path)
    else:
        if "csp" in args.task:
            run_csp(url, output_folder_path)
        if "gobuster" in args.task:
            run_gobuster(url, output_folder_path)
        if "humble" in args.task:
            run_humble(url, output_folder_path)
        if "nuclei" in args.task:
            run_nuclei(url, output_folder_path)
        

if __name__ == "__main__":
    main()
