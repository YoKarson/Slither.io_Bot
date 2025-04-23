from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Get to the game
driver.get("https://slither.io")

try:
    # Wait for nickname input field
    nickname_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "nick"))
    )
    
    # Enter nickname
    nickname_input.clear()
    nickname_input.send_keys("PythonBot")
    
    # Find and click the play button using its class
    play_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btnt"))
    )
    play_button.click()
    
    # Wait for game to start
    time.sleep(2)

    def move_snake(x, y):
        """
        Move the snake by setting the game's internal xm and ym variables
        x, y: coordinates relative to the center of the screen
        """
        # Update the game's mouse position variables
        script = f"""
        window.xm = {x};
        window.ym = {y};
        """
        driver.execute_script(script)

    try:
        # (100,0)   -> move right
        # (0,100)   -> move down
        # (-100,0)  -> move left
        # (0,-100)  -> move up
        square_pattern = [(400, 0), (0, 400), (-400, 0), (0, -400)]
        
        while True:
            for x, y in square_pattern:
                move_snake(x, y)
                time.sleep(0.5)

    except KeyboardInterrupt:
        # This catches when user presses Ctrl+C to stop the program
        # It allows for a graceful exit instead of a crash
        print("Stopping bot...")

except Exception as e:
    # This catches any other errors that might occur in the main try block
    # (like failing to find elements, JavaScript errors, etc)
    print(f"Error: {e}")  # Print the basic error message
    import traceback
    print(traceback.format_exc())  # Print the full error stack trace for debugging

finally:
    # This block always runs, whether there was an error or not
    # It ensures we always close the browser properly
    time.sleep(2)  # Wait 2 seconds before closing
    driver.quit()  # Close the browser and end the WebDriver session
