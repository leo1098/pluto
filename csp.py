import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup  # For HTML parsing
import time
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_csp(url):
    """Fetch the CSP from the provided URL using Google's CSP Evaluator API."""
    logging.info('Fetching CSP')
    csp_evaluator_url = 'https://csp-evaluator.withgoogle.com/getCSP'
    
    # Send the POST request to fetch the CSP
    payload = {'url': url}
    response = requests.post(csp_evaluator_url, data=payload)
    
    if response.status_code != 200:
        logging.error('Failed to fetch CSP')
        raise Exception(f"Failed to fetch CSP: {response.status_code}")
    
    csp = response.json().get('csp')
    if not csp:
        raise ValueError(f"No CSP field found in the response for {url}")
    
    return csp

def evaluate_csp(csp, output_file):
    """Send the retrieved CSP to the CSP evaluator and emulate clicking 'expand all'."""
    csp_evaluator_url = 'https://csp-evaluator.withgoogle.com'
    full_url = f"{csp_evaluator_url}?csp={requests.utils.quote(csp)}"
    
    # Set the path to ChromeDriver (ensure it's installed)
    chrome_driver_path = '/home/kali/.local/bin/chromedriver'  # Replace with your ChromeDriver path
    
    # Configure Selenium to run Chrome in headless mode
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')

    # Start the Selenium WebDriver session with Chrome
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Load the page and allow time to render
        driver.get(full_url)
        time.sleep(2)

        # Click the 'Expand All' button
        expand_all_button = driver.find_element(By.ID, 'expand_all')
        expand_all_button.click()
        time.sleep(1)

        # Parse the expanded page HTML with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Download and inline the stylesheets
        process_html(soup)

        # Save the modified HTML to a file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        logging.info(f"Expanded CSP evaluation saved to {output_file}")

    finally:
        driver.quit()

def process_html(soup, base_url='https://csp-evaluator.withgoogle.com'):

    # Process all <link> tags with 'stylesheet' rel
    logging.info('Processing relative urls')
    for tag in soup.find_all('link', href=True):
        href = tag['href']
        if href.startswith('/'):
            tag['href'] = f"{base_url}{href}"
    
    evaluator_logo = soup.find('img', id='evaluator_logo')
    if evaluator_logo and evaluator_logo.get('src', '').startswith('/'):
        old_src = evaluator_logo['src']
        evaluator_logo['src'] = f"{base_url}{old_src}"

    
    # List of element IDs to remove
    ids_to_remove = ['example_bad', 'example_good', 'check', 'csp-version', 'version-help', 'expand_all']

    # Remove elements with specific IDs
    logging.info('Removing unwanted elements')
    for element_id in ids_to_remove:
        element = soup.find(id=element_id)
        if element:
            element.decompose()  # Remove the element from the HTML
            # logging.info(f"Removed element with ID: {element_id}")

    # Modify <h3> element with content 'CSP Evaluator'
    h3_tag = soup.find('h3', string='CSP Evaluator')
    if h3_tag:
        h3_tag.string = f"{h3_tag.string} report for {website_url}"

    logging.info('HTML processing completed.')

    

if __name__ == "__main__":
    website_url = input("Enter the website URL: ")

    try:
        # Step 1: Fetch the CSP for the given URL
        csp = fetch_csp(website_url)
        logging.info(f"Content Security Policy for {website_url}:\n{csp}")
        
        # Step 2: Evaluate the CSP and expand all findings
        output_file = "csp_evaluation_expanded.html"
        evaluate_csp(csp, output_file)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
