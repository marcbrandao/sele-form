from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chromium.options import ChromiumOptions
from getpass import getpass
import pyperclip
import requests
import hashlib
import time
import re


# Setting up MLX API
MLX_BASE = "https://api.multilogin.com"
MLX_LAUNCHER = "https://launcher.mlx.yt:45001/api/v1"
LOCALHOST = "http://127.0.0.1"
HEADERS = {'Accept':       'application/json',
           'Content-Type': 'application/json'}


# MLX Sign in credentials
USERNAME = input("Insert your MLX email: ")
PASSWORD = getpass("Insert your MLX password: ")


# Indicate browser's Folder and ProfileID
FOLDER_ID  = input("Insert the desired folder ID: ")
PROFILE_ID = input("Insert the desired profile ID: ")


# Function: Sign-in to get token
def signin() -> str:
    payload = {
        'email': USERNAME,
        'password': hashlib.md5(PASSWORD.encode()).hexdigest()}
    r = requests.post(f'{MLX_BASE}/user/signin', json=payload)

    if (r.status_code != 200):
        print(f'\nError during login: {r.text}\n')
    else:
        response = r.json()['data']
        token = response['token']

    return token


# Function: Start profile - setting up WebDriver:
def start_profile() -> webdriver:
    r = requests.get(f'{MLX_LAUNCHER}/profile/f/{FOLDER_ID}/p/{PROFILE_ID}/start?automation_type=selenium',
                     headers=HEADERS)
    response = r.json()

    if (r.status_code != 200):
        print(f'\nError while starting profile: {r.text}\n')
    else:
        print(f'\nProfile {PROFILE_ID} started.\n')

    selenium_port = response.get('status').get('message')
    driver = webdriver.Remote(command_executor=f'{LOCALHOST}:{selenium_port}', options=ChromiumOptions())

    return driver


# Function: Stop profile - closing the WebDriver:
def stop_profile() -> None:
    r = requests.get(f'{MLX_LAUNCHER}/profile/stop/p/{PROFILE_ID}', headers=HEADERS)

    if (r.status_code != 200):
        print(f'\nError while stopping profile: {r.text}\n')
    else:
        print(f'\nProfile {PROFILE_ID} stopped.\n')


# Get the token
token = signin()
HEADERS.update({"Authorization": f'Bearer {token}'})


# Set up: Selenium WebDriver & MLX
driver = start_profile()

# Set up email Generator URL. Navigate to the page. Wait for it to load.
main_url = 'http://temp-mail.org'
driver.get(main_url)
time.sleep(10)

# Set up Click-to-Copy button ID (DevTools)
button_id = "click-to-copy"
# Locate the button object, click and proceed.
button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, button_id))) #Reproduce this for every element, minimize use of time.sleep()
button.click()
time.sleep(3)



# Open a new tab. Set up the target's URL: Navigate to Trakt. Wait for it to load.
driver.switch_to.new_window('tab')
new_url = 'https://trakt.tv/auth/join'
driver.get(new_url)
time.sleep(12)



# Collected Trakt form elements:
    # Email:          id= "user_email"
    # Username:       id= "user_username"
    # Password:       id= "user_password"
    # ConfirmP:       id= "user_password_confirmation"
    # BoxCheck:       id= "accept_terms_privacy"
    # BoxUncheck:     id= "accept_terms_marketing"

# Filling Trakt Form:

# Email field
email_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "user_email")))
paste_from_clipboard = pyperclip.paste()
email_field.send_keys(paste_from_clipboard)
time.sleep(3)

# Username field
username_field = driver.find_element(By.ID, "user_username")
username = paste_from_clipboard.split('@')[0] # Extracting the username from the email
username_field.send_keys(username)
time.sleep(3)

# Password field
strong_pass = "@StrongPass9"
password_field = driver.find_element(By.ID, "user_password")
password_field.send_keys(strong_pass)
time.sleep(3)

# Confirm Password field
confirm_password_field = driver.find_element(By.ID, "user_password_confirmation")
confirm_password_field.send_keys(strong_pass)
time.sleep(3)

# Accept terms/policy/privacy
accept_terms_privacy_checkbox = driver.find_element(By.ID, "accept_terms_privacy")
if not accept_terms_privacy_checkbox.is_selected():
    accept_terms_privacy_checkbox.click()
time.sleep(3)

# Uncheck Marketing offer
accept_terms_marketing_checkbox = driver.find_element(By.ID, "accept_terms_marketing")
if accept_terms_marketing_checkbox.is_selected():
    accept_terms_marketing_checkbox.click()
time.sleep(3)

# Click to create account and wait for page to load and confirmation mail to arrive
commit_button = driver.find_element(By.NAME, "commit")
commit_button.click()
time.sleep(10)

#Navigate back to the Mail window
driver.switch_to.window(driver.window_handles[0])
time.sleep(10)

# Finding the Confirmation Email
links = driver.find_elements(By.CSS_SELECTOR, "a.viewLink.title-subject")

for link in links:
    
    if "Confirm your email address" in link.text:
        link.click()
        print("Link found!")
        time.sleep(5)
        
        # Wait and click on 'Confirm Account' once clickable
        confirm_account_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'CONFIRM ACCOUNT')]")))
        confirm_account_button.click()
        print("CONFIRM ACCOUNT button clicked.")
        
        # Wait for the final confirmation page to load.
        time.sleep(10)  # Adjust sleep as necessary based on page load times
        
        break