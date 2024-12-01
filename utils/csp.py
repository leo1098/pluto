import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup  # For HTML parsing
import time
import logging
import os.path
from datetime import datetime
# from pyhtml2pdf import converter

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(levelname)s] %(module)s:%(funcName)s - %(message)s', level=logging.INFO)

def fetch_csp(website_url):
    """Fetch the CSP from the headers or meta tags of the provided URL."""
    logging.info(f'Fetching CSP from {website_url}')
    csp = ""

    try:
        # Send a GET request to the target URL
        response = requests.get(website_url, timeout=10)
        response.raise_for_status()  # Raise an exception for non-200 responses

        # Try to fetch the CSP from headers
        csp = response.headers.get('Content-Security-Policy') or \
              response.headers.get('Content-Security-Policy-Report-Only')

        if csp:
            logging.info(f"Successfully fetched CSP from headers of {website_url}: {csp} ")
            return csp

        # If no CSP in headers, parse the HTML for meta tags
        logging.info(f"No CSP found in headers, checking meta tags in {website_url}")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for a <meta> tag with 'http-equiv="Content-Security-Policy"'
        meta_tag_csp = soup.find('meta', attrs={'http-equiv': 'Content-Security-Policy'})

        if meta_tag_csp and meta_tag_csp.get('content'):
            csp = meta_tag_csp['content']
            logging.info(f"Successfully fetched CSP from meta tag in {website_url}")
            return csp

        logging.info(f"No CSP found in meta tags for {website_url}")
        return csp

    except requests.RequestException as e:
        logging.error(f"Failed to fetch CSP: {e}")
        raise Exception(f"Error fetching CSP from {website_url}: {str(e)}")


def evaluate_csp(csp, output_file, website_url):
    """Send the retrieved CSP to the CSP evaluator, modify the content, and save to PDF."""
    csp_evaluator_url = 'https://csp-evaluator.withgoogle.com'
    full_url = f"{csp_evaluator_url}?csp={requests.utils.quote(csp)}"

    chrome_driver_path = '/mnt/CYBERX/pluto/chrome-linux/chromedriver'  # Replace with your ChromeDriver path
    chrome_binary_location = '/mnt/CYBERX/pluto/chrome-linux/chrome'

    # Configure Selenium to run Chrome in headless mode
    chrome_options = Options()
    chrome_options.binary_location = chrome_binary_location
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-dev-shm-usage")


    # Start the Selenium WebDriver session with Chrome
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Load the CSP evaluator page and allow time to render
        driver.get(full_url)
        time.sleep(2)

        # Click the 'Expand All' button to reveal more content
        expand_all_button = driver.find_element(By.ID, 'expand_all')
        expand_all_button.click()
        time.sleep(1)

        # Parse the expanded page HTML with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Process the HTML (e.g., inline CSS, modify content, etc.)
        process_html(soup, website_url=website_url)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        logging.info(f"HTML saved as {output_file}")

        # Save the modified HTML to a temporary file
        # temp_html = "temp_csp_evaluation.html"
        # with open(temp_html, 'w', encoding='utf-8') as f:
        #     f.write(str(soup))

        # Open the temporary HTML file in the browser to print to PDF
        # converter.convert(f"file://{os.path.abspath(temp_html)}", output_file, install_driver=False)
        # time.sleep(2)  

        # logging.info(f"PDF saved as {output_file}")

    finally:
        driver.quit()


def process_html(soup, base_url='https://csp-evaluator.withgoogle.com', website_url=''):
    """Process HTML to update links, remove unwanted elements, and customize content."""

    # Process all <link> tags with 'stylesheet' rel
    logging.info('Processing relative URLs')
    for tag in soup.find_all('link', href=True):
        href = tag['href']
        if href.startswith('/'):
            tag['href'] = f"{base_url}{href}"

    # Update the 'src' attribute for the evaluator logo image
    evaluator_logo = soup.find('img', id='evaluator_logo')
    if evaluator_logo and evaluator_logo.get('src', '').startswith('/'):
        old_src = evaluator_logo['src']
        evaluator_logo['src'] = f"{base_url}{old_src}"

    # List of element IDs to remove
    ids_to_remove = ['example_bad', 'example_good', 'check', 'csp-version', 'version-help', 'expand_all']

    logging.info('Removing unwanted elements by ID')
    for element_id in ids_to_remove:
        element = soup.find(id=element_id)
        if element:
            element.decompose()

    # Remove the <footer> element
    footer = soup.find('footer')
    if footer:
        logging.info('Removing <footer> element')
        footer.decompose()

    # Remove <p> element with content that starts with 'CSP Evaluator allows developers'
    logging.info("Removing specific <p> element with matching content")
    for p_tag in soup.find_all('p'):
        if 'CSP Evaluator allows developers' in p_tag.get_text():
            p_tag.decompose()
            break

     # Remove all <br> elements
    logging.info('Removing all <br> elements')
    for br in soup.find_all('br'):
        br.decompose()

    # Modify the <h3> element with content 'CSP Evaluator'
    h3_tag = soup.find('h3', string='CSP Evaluator')
    if h3_tag:
        h3_tag.string = f"{h3_tag.string} report for {website_url}"

    logging.info('HTML processing completed.')


def main(website_url, output_folder_path):
    try:
        logging.warn(f"Performing CSP evaluation for: {website_url}")

        # Step 1: Fetch the CSP for the given URL
        csp = fetch_csp(website_url)
        
        if csp == "":
            logging.error(f"No CSP found for {website_url}, skipping CSP evaluation")
            return


        # Step 2: Evaluate the CSP and expand all findings
        filename = f"csp_{website_url.replace('://', '_')}_{datetime.today().strftime('%Y%m%d')}.html"
        output_file_path = os.path.join(output_folder_path, filename)
        
        evaluate_csp(csp, output_file_path, website_url)

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":

    website_url = 'google.com'

    try:
        website_url = normalize_url(website_url)  # Ensure the URL has a valid scheme

        # Step 1: Fetch the CSP for the given URL
        csp = fetch_csp(website_url)
        
        if csp == "":
            logging.error(f"No CSP found for {website_url}, skipping CSP evaluation")
            raise Exception(f"Error fetching CSP from {website_url}: {str(e)}")


        # Step 2: Evaluate the CSP and expand all findings
        output_folder_path = "./test/"
        filename = f"csp_{website_url.replace('://', '_')}_{datetime.today().strftime('%Y%m%d')}.html"
        output_file = os.path.join(output_folder_path, filename)
        
        evaluate_csp(csp, output_file, website_url)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
