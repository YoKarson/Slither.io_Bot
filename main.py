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

    # --- Function definitions ---


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
        let panicRadius = 80;
        let ignoreRadius = 200;
        let tooCloseRadius = 10; // Ignore food that's too close

        // Attraction: only toward the closest food that's not too close
        let closestFood = null;
        let minFoodDist = Infinity;
        for (let i = 0; i < foods.length; i++) {
            let f = foods[i];
            if (f && f.xx !== undefined && f.yy !== undefined) {
                let dx = f.xx - myX;
                let dy = f.yy - myY;
                let dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < minFoodDist && dist > tooCloseRadius) {
                    minFoodDist = dist;
                    closestFood = f;
                }
            }
        }
        if (closestFood) {
            let dx = closestFood.xx - myX;
            let dy = closestFood.yy - myY;
            attraction.x = dx;
            attraction.y = dy;
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

        let ctx = window._botOverlayCtx;
        ctx.clearRect(0, 0, window._botOverlay.width, window._botOverlay.height);

        // Convert game coordinates to screen coordinates
        function toScreen(x, y) {
            let canvas = window.mc;
            let screenX = (x - window.view_xx) * window.gsc + canvas.width / 2;
            let screenY = (y - window.view_yy) * window.gsc + canvas.height / 2;
            return [screenX, screenY];
        }

        let [snakeScreenX, snakeScreenY] = toScreen(myX, myY);

        // Draw attraction vector
        ctx.strokeStyle = 'lime';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(snakeScreenX, snakeScreenY);
        ctx.lineTo(snakeScreenX + attraction.x * window.gsc, snakeScreenY + attraction.y * window.gsc);
        ctx.stroke();

        // Draw repulsion vector
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(snakeScreenX, snakeScreenY);
        ctx.lineTo(snakeScreenX + repulsion.x * window.gsc, snakeScreenY + repulsion.y * window.gsc);
        ctx.stroke();

        // Draw final movement vector
        ctx.strokeStyle = 'blue';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(snakeScreenX, snakeScreenY);
        ctx.lineTo(snakeScreenX + moveX * window.gsc, snakeScreenY + moveY * window.gsc);
        ctx.stroke();

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

    def move_toward_food_and_avoid_snakes():
        script = """
        try {
            let mySnake = window.slither || window.snake;
            let foods = window.foods || [];
            let allSnakes = window.slithers || [];
            let myX = mySnake && mySnake.xx, myY = mySnake && mySnake.yy;

            if (!mySnake || myX === undefined || myY === undefined) {
                return {error: "Snake not found"};
            }

            // --- Food targeting with timeout/blacklist ---
            if (!window._foodTargetState) {
                window._foodTargetState = {lastTarget: null, lastChange: Date.now(), stuck: false, blacklist: []};
            }
            let state = window._foodTargetState;

            // Parameters
            let min_target_dist = 30;
            let dangerRadius = 200;
            let repulsionFactor = 1000;
            let panicRadius = 80;
            let ignoreRadius = 200;

            // --- Find closest food (with blacklist logic) ---
            let candidates = [];
            for (let i = 0; i < foods.length; i++) {
                let f = foods[i];
                if (f && f.xx !== undefined && f.yy !== undefined) {
                    let dx = f.xx - myX;
                    let dy = f.yy - myY;
                    let dist = Math.sqrt(dx*dx + dy*dy);
                    let id = f.xx + ',' + f.yy;
                    if (dist > min_target_dist && state.blacklist.indexOf(id) === -1) {
                        candidates.push({food: f, dist: dist, id: id});
                    }
                }
            }
            candidates.sort((a, b) => a.dist - b.dist);

            let target = null;
            if (candidates.length > 0) {
                target = candidates[0].food;
            }

            // Blacklist logic
            let targetId = target ? (target.xx + ',' + target.yy) : null;
            if (targetId !== state.lastTarget) {
                state.lastTarget = targetId;
                state.lastChange = Date.now();
                state.stuck = false;
            } else {
                if (Date.now() - state.lastChange > 1000 && targetId) {
                    state.stuck = true;
                    if (state.blacklist.indexOf(targetId) === -1) {
                        state.blacklist.push(targetId);
                    }
                    if (candidates.length > 1) {
                        target = candidates[1].food;
                        state.lastTarget = target.xx + ',' + target.yy;
                        state.lastChange = Date.now();
                        state.stuck = false;
                    } else {
                        target = null;
                    }
                }
            }

            // --- Attraction vector toward target food ---
            let attraction = {x: 0, y: 0};
            if (target) {
                let dx = target.xx - myX;
                let dy = target.yy - myY;
                attraction.x = dx;
                attraction.y = dy;
            }

            // --- Repulsion from enemy snakes ---
            let repulsion = {x: 0, y: 0};
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
            if (minEnemyDist > ignoreRadius) {
                repulsion.x = 0;
                repulsion.y = 0;
            }

            // --- Combine attraction and repulsion ---
            let moveX = attraction.x + repulsion.x;
            let moveY = attraction.y + repulsion.y;
            let mag = Math.sqrt(moveX*moveX + moveY*moveY);
            if (mag > 0) {
                moveX = moveX / mag * 100;
                moveY = moveY / mag * 100;
            }

            window.xm = moveX;
            window.ym = moveY;

            // --- Panic logic for speed boost ---
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

            // --- Return info for debugging/overlay ---
            return {
                move: {x: moveX, y: moveY},
                attraction: attraction,
                repulsion: repulsion,
                minEnemyDist: minEnemyDist,
                target: target,
                stuck: state.stuck
            };
        } catch (e) {
            return {error: e.toString()};
        }
        """
        return driver.execute_script(script)

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
        return enemies;
        """
        return driver.execute_script(script)


    # --- Now call the function ---

    try:
        while True:
            try:
                result = move_toward_food_and_avoid_snakes()
            except Exception as e:
                pass
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass

except Exception as e:
    pass

finally:
    # This block always runs, whether there was an error or not
    # It ensures we always close the browser properly
    time.sleep(2)  # Wait 2 seconds before closing
    driver.quit()  # Close the browser and end the WebDriver session
