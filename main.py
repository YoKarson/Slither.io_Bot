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

    def move_greedy_avoid_snakes():
        script = """
        let mySnake = window.slither;
        let foods = window.foods || [];
        let allSnakes = window.slithers || [];
        let attraction = {x: 0, y: 0};
        let repulsion = {x: 0, y: 0};
        let myX = mySnake && mySnake.xx, myY = mySnake && mySnake.yy;

        // Parameters
        let dangerRadius = 200;
        let repulsionFactor = 1000;
        let panicRadius = 80; // Panic if enemy is this close
        let ignoreRadius = 300; // Ignore enemies farther than this

        // Attraction to food
        for (let i = 0; i < foods.length; i++) {
            let f = foods[i];
            if (f && f.xx !== undefined && f.yy !== undefined) {
                let dx = f.xx - myX;
                let dy = f.yy - myY;
                let dist = Math.sqrt(dx*dx + dy*dy);
                let weight = 1 / (dist + 1e-5);
                attraction.x += dx * weight;
                attraction.y += dy * weight;
            }
        }

        // Repulsion from enemy snake segments & find nearest
        let minEnemyDist = Infinity;
        for (let i = 0; i < allSnakes.length; i++) {
            let s = allSnakes[i];
            if (s && s !== mySnake && s.pts) {
                for (let j = 0; j < s.pts.length; j++) {
                    let pt = s.pts[j];
                    if (pt && pt.xx !== undefined && pt.yy !== undefined) {
                        let dx = myX - pt.xx;
                        let dy = myY - pt.yy;
                        let dist = Math.sqrt(dx*dx + dy*dy);
                        if (dist < dangerRadius) {
                            let weight = repulsionFactor / (dist + 1e-5);
                            repulsion.x += dx * weight;
                            repulsion.y += dy * weight;
                        }
                        if (dist < minEnemyDist) {
                            minEnemyDist = dist;
                        }
                    }
                }
            }
        }

        // If the closest enemy is far away, ignore repulsion
        if (minEnemyDist > ignoreRadius) {
            repulsion.x = 0;
            repulsion.y = 0;
        }

        // Combine attraction and repulsion
        let moveX = attraction.x + repulsion.x;
        let moveY = attraction.y + repulsion.y;

        // Normalize movement vector to avoid excessive speed
        let mag = Math.sqrt(moveX*moveX + moveY*moveY);
        if (mag > 0) {
            moveX = moveX / mag * 100;
            moveY = moveY / mag * 100;
        }

        window.xm = moveX;
        window.ym = moveY;

        // Speed boost if enemy is very close
        if (minEnemyDist < panicRadius) {
            if (typeof window.setAcceleration === "function") {
                window.setAcceleration(1);
            }
            if (!window._spaceHeld) {
                window._spaceHeld = true;
                document.body.dispatchEvent(new KeyboardEvent('keydown', {keyCode: 32}));
            }
        } else {
            if (typeof window.setAcceleration === "function") {
                window.setAcceleration(0);
            }
            if (window._spaceHeld) {
                window._spaceHeld = false;
                document.body.dispatchEvent(new KeyboardEvent('keyup', {keyCode: 32}));
            }
        }

        console.log("Nearest enemy distance:", minEnemyDist);

        return {
            move: {x: moveX, y: moveY},
            attraction: attraction,
            repulsion: repulsion,
            minEnemyDist: minEnemyDist
        };
        """
        return driver.execute_script(script)

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
        let snake = window.slither;
        let foods = window.foods || [];
        let snake_x = snake && snake.xx;
        let snake_y = snake && snake.yy;
        let snake_ang = snake && snake.ang;

        let min_target_dist = 30; // Increase this if needed
        let min_dist = Infinity;
        let target = null;

        function angleDiff(a, b) {
            let diff = a - b;
            while (diff < -Math.PI) diff += 2 * Math.PI;
            while (diff > Math.PI) diff -= 2 * Math.PI;
            return Math.abs(diff);
        }

        for (let i = 0; i < foods.length; i++) {
            let f = foods[i];
            if (f && f.xx !== undefined && f.yy !== undefined) {
                let dx = f.xx - snake_x;
                let dy = f.yy - snake_y;
                let dist = Math.sqrt(dx*dx + dy*dy);
                if (dist > min_target_dist) {
                    let food_ang = Math.atan2(dy, dx);
                    if (angleDiff(food_ang, snake_ang) < Math.PI / 2) { // within 90 degrees of heading
                        if (dist < min_dist) {
                            min_dist = dist;
                            target = f;
                        }
                    }
                }
            }
        }

        if (target) {
            let dx = target.xx - snake_x;
            let dy = target.yy - snake_y;
            window.xm = dx;
            window.ym = dy;
            return {snake: {x: snake_x, y: snake_y, ang: snake_ang}, target: {x: target.xx, y: target.yy}, vector: {dx: dx, dy: dy}};
        } else {
            window.xm = 0;
            window.ym = 0;
            return {snake: {x: snake_x, y: snake_y, ang: snake_ang}, target: null};
        }
        """
        result = driver.execute_script(script)

    def log_enemy_snake_positions():
        script = """
        // Get all snakes except the player's own
        let allSnakes = window.slithers || [];
        let mySnake = window.slither;
        let enemies = [];
        for (let i = 0; i < allSnakes.length; i++) {
            let s = allSnakes[i];
            if (s && s !== mySnake && s.pts && s.pts.length > 0) {
                // Collect all segment positions for this snake
                let segments = [];
                for (let j = 0; j < s.pts.length; j++) {
                    let pt = s.pts[j];
                    if (pt && pt.xx !== undefined && pt.yy !== undefined) {
                        segments.push({x: pt.xx, y: pt.yy});
                    }
                }
                enemies.push({id: i, segments: segments});
            }
        }
        console.log("Enemy snakes:", enemies); // For debugging
        return enemies;
        """
        return driver.execute_script(script)

    try:
        while True:
            result = move_greedy_avoid_snakes()
            print("Nearest enemy distance:", result.get("minEnemyDist"))
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
