# Import necessary Selenium files
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.common.exceptions import TimeoutException


# Method logging into Instagram
def login(bot, username, password):
    # Use a bot to access instagram
    bot.get('https://www.instagram.com/accounts/login/')

    # Input username and password to bot
    username_input = WebDriverWait(bot, TIMEOUT).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']"))
    )
    password_input = WebDriverWait(bot, TIMEOUT).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']"))
    )

    # Submit username
    username_input.clear()
    username_input.send_keys(username)

    # Submit password
    password_input.clear()
    password_input.send_keys(password)

    # Submit login attempt
    login_button = WebDriverWait(bot, TIMEOUT).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    login_button.click()

    # Delay by 10 to allow for loading
    time.sleep(10)


def build_adj_mat(bot, username, attribute, rows):
    bot.get(f'https://www.instagram.com/{username}/')

    # Try-catch for timeout exception
    try:
        if attribute == 'following':
            WebDriverWait(bot, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/following')]"))
            ).click()
        elif attribute == 'followers':
            WebDriverWait(bot, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/followers')]"))
            ).click()
        time.sleep(3)
    except TimeoutException:
        print(f"Unable to find '{attribute}' page for the given user")
        return

    # Use sets as to prevent duplicates
    users = set()
    matrix = set()

    while len(users) < rows:
        user_info = bot.find_elements(By.XPATH, "//a[contains(@href, '/')]")

        for user in user_info:
            if user.get_attribute('href'):
                profile_username = user.get_attribute('href').split("/")[3]
                matrix.add(f"{username}, {profile_username}")
                users.add(profile_username)

        ActionChains(bot).send_keys(Keys.END).perform()
        time.sleep(1)

    # Write the adjacency matrix
    with open(f'{attribute}_adjmat.txt', 'a') as file:
        file.write('\n'.join(matrix))

    # Write down all recorded names for record-keeping
    with open(f'allnodes', 'a') as node_file:
        node_file.write('\n'.join(users))


# Method to create connection with ind. server through cmd
def scrape():
    login_details = ["XXXXXXXXX", "XXXXXXXXX"]

    # Set the username and password
    username = login_details[0]
    password = login_details[1]

    rows = int(input('Enter number of rows in adjacency matrix: ')) # Update to always be max?

    usernames = input("Enter username(s) for Instagram account(s) being scraped: ").split(",")

    attribute = input("Scrape Followers or Following: ")

    # Emulate a mobile client of Instagram to allow for eased access to user information
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")
    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/90.0.1025.166 Mobile Safari/535.19"
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    bot = webdriver.Chrome(executable_path=CM().install(), options=options)

    # Try block to execute scraping process
    try:
        login(bot, username, password)

        for user in usernames:
            user = user.strip()
            build_adj_mat(bot, user, attribute, rows)

    # Terminate scrape
    finally:
        bot.quit()


# Run from cmd
if __name__ == '__main__':
    TIMEOUT = 15
    scrape()
