import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from undetected_chromedriver import Chrome
import pyautogui
import time
import pyperclip
import pygetwindow as gw
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

MIXES_BUTTON_XPATH = ".//yt-formatted-string[text()='Миксеви' or text()='Mixes']"
TITLE_XPATH = ".//div[@class='playlist-items style-scope ytd-playlist-panel-renderer']//h4/span"
SONG_XPATH = ".//div[@class='playlist-items style-scope ytd-playlist-panel-renderer']//a[@id='wc-endpoint']"
SEARCH_SONG_XPATH = "(.//yt-formatted-string[text()='{}'])[1]/.."
INPUT_XPATH = ".//input[@id='url']"
DOWNLOAD_BUTTON_XPATH = ".//a[text()='Download']"
CONVERT_BUTTON_XPATH = ".//input[@value='Convert']"

def get_current_url(driver):
    try:
        current_url = driver.current_url
        # print(f"Current URL: {current_url}")
        return current_url
    except Exception as e:
        print("Error:", e)
        return None

def move_cursor_to_element(driver, xpath):
    try:
        # Finding the element
        element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))

        # Getting screen dimensions
        screen_width, screen_height = pyautogui.size()

        # Getting browser window dimensions
        window_size = driver.get_window_size()
        window_width = window_size['width']
        window_height = window_size['height']

        # Getting browser window position on screen
        window_position = driver.get_window_position()
        window_x = window_position['x']
        window_y = window_position['y']

        # Getting element position on the page
        element_location = element.location_once_scrolled_into_view
        x = element_location['x']
        y = element_location['y']
        width = element.size['width']
        height = element.size['height']

        # Printing element coordinates
        # print(f"Element coordinates: x={x}, y={y}")

        # Calculating element center relative to the browser window
        center_x = (window_x + x + width / 2) * screen_width / window_width
        
        # Getting browser header height
        browser_navigation_panel_height = driver.execute_script('return window.outerHeight - window.innerHeight;')
        center_y = (window_y + y + height / 2 + browser_navigation_panel_height) * screen_height / window_height

        # Printing element center coordinates
        # print(f"Element center coordinates: x={center_x}, y={center_y}")

        # Moving cursor to the center of the element
        pyautogui.moveTo(center_x, center_y, duration=2)

        # Checking cursor position
        current_x, current_y = pyautogui.position()
        # print(f"Current cursor position: x={current_x}, y={current_y}")

        # Clicking on the element
        # pyautogui.click()
    except Exception as e:
        print("Error:", e)

def move_mouse_and_click(driver, xpath_element):
    try:
        move_cursor_to_element(driver=driver, xpath=xpath_element)
        time.sleep(1)
        pyautogui.click()
        
        print("Clicked the button.")
    except Exception as e:
        print("Error:", e)

def open_new_tab(driver, url):
    try:
        # Opening a new tab using Ctrl + T
        body = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        body.send_keys(Keys.CONTROL + 't')

        # Switching to the newly opened tab
        driver.switch_to.window(driver.window_handles[-1])

        # Open the URL in the new tab
        driver.get(url)

        print(f"Opened a new tab with URL: {url}")
    except Exception as e:
        print("Error:", e)

def scroll_element(driver, xpath, scroll_by_pixels):
    try:
        # Finding the element
        element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))

        # Scrolling the element using JavaScript
        driver.execute_script("arguments[0].scrollTop += arguments[1];", element, scroll_by_pixels)
        print(f"Scrolled by {scroll_by_pixels} pixels.")
    except Exception as e:
        print("Error:", e)

def find_elements_by_xpath(driver, xpath):
    try:
        # Finding elements by the given XPath expression
        elements = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, xpath)))
        return elements
    except Exception as e:
        print("Error:", e)
        return []

def find_element_by_xpath(driver, xpath):
    try:
        # Finding an element by the given XPath expression
        element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        return element
    except Exception as e:
        print("Error:", e)
        return None

def close_last_tab(driver):
    try:
        # Getting a list of all open tabs
        tabs = driver.window_handles

        # If there is more than one tab, close the last tab
        if len(tabs) > 1:
            # Switching to the last tab
            driver.switch_to.window(tabs[-1])

            # Closing the last tab
            driver.close()

            # Switching to the previous tab
            driver.switch_to.window(tabs[-2])
            print("Last tab has been closed.")
        else:
            print("Only one tab is open. Cannot close the last tab.")
    except Exception as e:
        print("Error:", e)

def copy_and_paste(value):
    pyperclip.copy(value)  # Copying URL to the clipboard
    pyautogui.hotkey('ctrl', 'v')

def press_key(key):
    pyautogui.press(key)

def list_files(directory):
    """Function to load file names from the specified directory"""
    try:
        # Load file names in the directory
        filenames = os.listdir(directory)
        return filenames
    except FileNotFoundError:
        print(f"Directory {directory} does not exist.")
        return []

def split_filename_extension(filename):
    """Function to separate the file name from the extension"""
    name, extension = os.path.splitext(filename)
    return name, extension

def prepare_song_links(driver):
    new_tab = "https://www.youtube.com/results?search_query={}"
    elements = find_elements_by_xpath(driver, TITLE_XPATH)
    titles = []
    downloaded_songs = [split_filename_extension(file_name)[0] for file_name in list_files(os.path.abspath('.\downloads'))]

    for element in elements:
        title = element.get_attribute("title")
        if not title in downloaded_songs:
            titles.append(title)

        if len(titles) == 1:
            break

    links = []
    for title in titles:
        try:
            open_new_tab(driver, new_tab.format(title))
            xpath = SEARCH_SONG_XPATH.format(title)
            element = find_element_by_xpath(driver, xpath)
            link = element.get_attribute("href")
            links.append(link)
            time.sleep(3)
        except Exception as e:
            print(e)

    return links

def download_songs(driver, links):
    try:
        open_new_tab(driver, "https://y2mate.nu/woNO/")
        for link in links:
            move_mouse_and_click(driver, INPUT_XPATH)
            copy_and_paste(link)
            move_mouse_and_click(driver, CONVERT_BUTTON_XPATH)
            move_mouse_and_click(driver, DOWNLOAD_BUTTON_XPATH)

            press_key("enter")
            open_new_tab(driver, "https://y2mate.nu/woNO/")
    except Exception as e:
        print(e)

def scrape(driver, xpath):
    try:        
        move_mouse_and_click(driver, xpath)

        url = get_current_url(driver)

        while(not "start_radio" in url):
            print("Please select a mix to download.")
            time.sleep(10)
            url = get_current_url(driver)

        links = prepare_song_links(driver)

        download_songs(driver, links)
        
        print("Clicked the button.")
    except Exception as e:
        print("Error:", e)

# def init_browser():
#     options = Options()
#     options.add_argument('--disable-extensions')
#     user_data_dir = os.path.join(os.path.dirname(__file__), 'user_data')
#     options.add_argument(f'--user-data-dir={user_data_dir}')
#     driver = Chrome(options=options)
#     driver.maximize_window()
#     driver.get("https://www.youtube.com")

#     return driver

def init_browser():
    options = Options()
    
    # Set the download path
    download_path = os.path.abspath('.\downloads')
    os.makedirs(download_path, exist_ok=True)

    # Define Chrome preferences
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    # Add arguments to Chrome
    options.add_argument('--disable-extensions')
    user_data_dir = os.path.join(os.path.dirname(__file__), 'user_data')
    options.add_argument(f'--user-data-dir={user_data_dir}')

    # Initialize Chrome WebDriver with specified options
    driver = webdriver.Chrome(options=options)
    
    # Maximize the browser window
    driver.maximize_window()
    
    # Open YouTube page
    driver.get("https://www.youtube.com")

    return driver

def main():
    driver = init_browser()

    scrape(driver, MIXES_BUTTON_XPATH)

    time.sleep(10)
    driver.quit()

if __name__ == "__main__":
    main()