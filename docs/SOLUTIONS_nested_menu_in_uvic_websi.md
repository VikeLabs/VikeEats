from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

def scrape_nested_menu(url: str, parent_selector: str = "nav"):
    """
    Scrapes deeply nested menu items from a given URL by using Selenium 
    to execute JavaScript and handle dynamic dropdown visibility.

    Args:
        url (str): The target URL containing the complex menu structure.
        parent_selector (str): CSS selector for the main navigation element.

    Returns:
        list[dict]: A list of dictionaries, each containing the 
                     menu item text and its link/URL.
    """
    print(f"[*] Initializing headless browser for URL: {url}")
    # Initialize Chrome WebDriver (Ensure ChromeDriver is accessible in PATH or defined)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run without opening a visible UI
    options.add_argument("--no-sandbox") # Bypass OS security restrictions for stability
    driver = webdriver.Chrome(options=options)

    try:
        # 1. Navigate to the page
        driver.get(url)
        print("[*] Page loaded successfully. Waiting for navigation elements...")

        # Wait up to 10 seconds for the main navigation structure to appear
        wait = WebDriverWait(driver, 15)
        try:
            main_nav_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"{parent_selector}"))
            )
        except Exception as e:
             print(f"[!] Warning: Could not find the main navigation using selector '{parent_selector}'. Falling back to general DOM extraction.")
             # If specific navigation element fails, proceed with broader scrape attempt
             pass

        # 2. Simulating Interaction (The critical step)
        # Many dropdowns require a mouse hover or an initial click on the parent item
        try:
            print("[*] Attempting to trigger dynamic menu elements...")
            # A common strategy is finding all known 'dropdown triggers' and clicking them 
            # to force visibility of children (e.g., a div with class .dropdown-parent).
            trigger_elements = driver.find_elements(By.CSS_SELECTOR, ".has-dropdown button")
            for trigger in trigger_elements:
                try:
                    # Click the trigger element to ensure JS loads the hidden menu
                    trigger.click() 
                    time.sleep(0.5) # Give time for the transition/DOM update
                except Exception as click_error:
                    print(f"    [!] Could not reliably click a dropdown trigger: {click_error}")

            # Wait briefly again to allow all potential async content loading
            time.sleep(2) 

        except Exception as e:
             print(f"[!] Error during interaction phase (this might be normal): {e}")


        # 3. Extraction of Nested Elements
        # Assuming menu items are consistently structured under a container class, 
        # we target all potential link elements within the navigation area.
        menu_items = driver.find_elements(By.CSS_SELECTOR, f"{parent_selector} a[href]")
        
        scraped_data = []
        for item in menu_items:
            text = item.get_attribute("innerText").strip()
            link = item.get_attribute("href")
            # Filter out generic links or empty entries
            if text and link and len(text) > 1:
                scraped_data.append({
                    "menu_item": text,
                    "url": link
                })

        return scraped_data

    except Exception as e:
        print(f"[!!!] A critical error occurred during scraping: {e}")
        return []
    finally:
        driver.quit() # Crucial: Always close the driver instance

# --- Example Usage/Demonstration (Requires a local environment setup with Selenium) ---

# Replace this URL and selector with the target details (e.g., sandwich lab page)
TARGET_URL = "https://www.uvic.ca/example-lab-page" 
PARENT_SELECTOR = "#main-navigation-bar" # Use a specific high-level CSS selector for the main menu

# scraped_menu = scrape_nested_menu(TARGET_URL, PARENT_SELECTOR)
# print("\n--- Scraped Menu Results ---")
# if scraped_menu:
#     print(json.dumps(scraped_menu, indent=4))
# else:
#     print("No menu items were successfully extracted.")
