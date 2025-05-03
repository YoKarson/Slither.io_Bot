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

    def get_snake_and_foods():
        """
        Returns the snake's position and a list of food positions from the game.
        """
        script = """
        if (window.snake && window.foods) {
            let snake_x = window.snake.xx;
            let snake_y = window.snake.yy;
            let foods = [];
            for (let i = 0; i < window.foods.length; i++) {
                let f = window.foods[i];
                if (f && f.xx !== undefined && f.yy !== undefined) {
                    foods.push({x: f.xx, y: f.yy});
                }
            }
            return {snake: {x: snake_x, y: snake_y}, foods: foods};
        } else {
            return null;
        }
        """
        return driver.execute_script(script)

    def move_toward_closest_food():
        script = """
        // Get your snake (slither) and all foods
        let snake = window.slither;
        let foods = window.foods || [];
        let snake_x = snake && snake.xx;
        let snake_y = snake && snake.yy;

        // Find the closest food
        let min_dist = Infinity;
        let target = null;
        for (let i = 0; i < foods.length; i++) {
            let f = foods[i];
            if (f && f.xx !== undefined && f.yy !== undefined) {
                let dist = Math.sqrt(Math.pow(f.xx - snake_x, 2) + Math.pow(f.yy - snake_y, 2));
                if (dist < min_dist) {
                    min_dist = dist;
                    target = f;
                }
            }
        }

        // Move toward the closest food
        if (target) {
            let dx = target.xx - snake_x;
            let dy = target.yy - snake_y;
            window.xm = dx;
            window.ym = dy;
            return {snake: {x: snake_x, y: snake_y}, target: {x: target.xx, y: target.yy}, vector: {dx: dx, dy: dy}};
        } else {
            return {snake: {x: snake_x, y: snake_y}, target: null};
        }
        """
        result = driver.execute_script(script)
        print(result)  # For debugging: shows where the snake is moving

    try:
        while True:
            move_toward_closest_food()
            time.sleep(0.1)

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
