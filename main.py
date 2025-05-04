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

    # --- Wait until snake is present before starting timer ---
    def is_snake_present():
        script = "return window.slither !== null && window.slither !== undefined;"
        return driver.execute_script(script)

    while True:
        try:
            if is_snake_present():
                break
        except Exception:
            pass
        time.sleep(0.1)

    # --- Lifespan tracking ---
    life_start_time = time.time()  # Record the start time

    def is_snake_alive():
        # Returns True if the snake is still alive, False otherwise
        script = "return window.slither !== null && window.slither !== undefined;"
        return driver.execute_script(script)

    # --- Function definitions ---


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
        if (window._foodCollectedCount === undefined) window._foodCollectedCount = 0;
        if (window._lastFoodTargetId === undefined) window._lastFoodTargetId = null;

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
            let panicRadius = 90;
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
                        window._foodBlacklistEvents = (window._foodBlacklistEvents || 0) + 1;
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
            let result = {
                move: {x: moveX, y: moveY},
                attraction: attraction,
                repulsion: repulsion,
                minEnemyDist: minEnemyDist,
                target: target,
                stuck: state.stuck
            };
            window._lastMoveResult = result;

            if (targetId !== window._lastFoodTargetId && window._lastFoodTargetId !== null) {
                window._foodCollectedCount += 1;
            }
            window._lastFoodTargetId = targetId;

            return result;
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

    def inject_overlay_script():
        script = """
        (function() {
            // Remove old overlay if exists
            let old = document.getElementById('slither-bot-overlay');
            if (old) old.remove();

            // Create overlay canvas
            let overlay = document.createElement('canvas');
            overlay.id = 'slither-bot-overlay';
            overlay.style.position = 'absolute';
            overlay.style.left = '0';
            overlay.style.top = '0';
            overlay.style.pointerEvents = 'none';
            overlay.style.zIndex = 10000;
            document.body.appendChild(overlay);

            function updateOverlay() {
                let c = document.getElementById('slither-bot-overlay');
                if (!c) return;
                let w = window.innerWidth, h = window.innerHeight;
                c.width = w; c.height = h;
                let ctx = c.getContext('2d');
                ctx.clearRect(0, 0, w, h);

                // Get game variables
                let mySnake = window.slither || window.snake;
                let allSnakes = window.slithers || [];
                let state = window._foodTargetState || {};
                let target = null;
                if (state.lastTarget) {
                    let parts = state.lastTarget.split(',');
                    if (parts.length === 2) {
                        let tx = parseFloat(parts[0]), ty = parseFloat(parts[1]);
                        target = {xx: tx, yy: ty};
                    }
                }

                // Parameters (should match your JS logic)
                let dangerRadius = 200;
                let ignoreRadius = 200;
                let panicRadius = 90;

                // Camera offset
                let view_xx = window.view_xx || 0;
                let view_yy = window.view_yy || 0;
                let view_ang = window.view_ang || 0;
                let view_dist = window.gsc || 1;

                // Helper: world to screen
                function worldToScreen(wx, wy) {
                    let cx = w/2, cy = h/2;
                    let dx = wx - view_xx, dy = wy - view_yy;
                    // Rotate by -view_ang
                    let ang = -view_ang;
                    let rx = dx * Math.cos(ang) - dy * Math.sin(ang);
                    let ry = dx * Math.sin(ang) + dy * Math.cos(ang);
                    // Scale
                    rx *= view_dist; ry *= view_dist;
                    return [cx + rx, cy + ry];
                }

                // Draw danger zone around our snake
                if (mySnake) {
                    let [sx, sy] = worldToScreen(mySnake.xx, mySnake.yy);
                    ctx.beginPath();
                    ctx.arc(sx, sy, dangerRadius * view_dist, 0, 2 * Math.PI);
                    ctx.strokeStyle = 'rgba(255,0,0,0.2)';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }

                // Draw panic zone around our snake
                if (mySnake) {
                    let [sx, sy] = worldToScreen(mySnake.xx, mySnake.yy);
                    ctx.beginPath();
                    ctx.arc(sx, sy, panicRadius * view_dist, 0, 2 * Math.PI);
                    ctx.strokeStyle = 'rgba(255,165,0,0.3)'; // orange, semi-transparent
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }

                // Draw boxes/circles around enemy snakes within ignoreRadius
                if (mySnake) {
                    let myX = mySnake.xx, myY = mySnake.yy;
                    for (let i = 0; i < allSnakes.length; i++) {
                        let s = allSnakes[i];
                        if (s && s !== mySnake && s.pts && s.pts.length > 0) {
                            // Find closest segment to our snake
                            let minDist = Infinity, minPt = null;
                            for (let j = 0; j < s.pts.length; j++) {
                                let pt = s.pts[j];
                                if (pt && pt.xx !== undefined && pt.yy !== undefined) {
                                    let dx = myX - pt.xx;
                                    let dy = myY - pt.yy;
                                    let dist = Math.sqrt(dx*dx + dy*dy);
                                    if (dist < minDist) {
                                        minDist = dist;
                                        minPt = pt;
                                    }
                                }
                            }
                            if (minDist < ignoreRadius) {
                                // Draw a red box around the closest segment
                                let [ex, ey] = worldToScreen(minPt.xx, minPt.yy);
                                ctx.save();
                                ctx.strokeStyle = 'red';
                                ctx.lineWidth = 2;
                                ctx.beginPath();
                                ctx.rect(ex - 10, ey - 10, 20, 20);
                                ctx.stroke();
                                ctx.restore();
                            }
                        }
                    }
                }

                // Draw attraction/repulsion/move vectors
                if (window._lastMoveResult && mySnake) {
                    let [sx, sy] = worldToScreen(mySnake.xx, mySnake.yy);
                    let mv = window._lastMoveResult;

                    // Attraction (blue)
                    ctx.beginPath();
                    ctx.moveTo(sx, sy);
                    ctx.lineTo(sx + mv.attraction.x, sy + mv.attraction.y);
                    ctx.strokeStyle = 'blue';
                    ctx.lineWidth = 3;
                    ctx.stroke();

                    // Repulsion (red)
                    ctx.beginPath();
                    ctx.moveTo(sx, sy);
                    ctx.lineTo(sx + mv.repulsion.x, sy + mv.repulsion.y);
                    ctx.strokeStyle = 'red';
                    ctx.lineWidth = 3;
                    ctx.stroke();

                    // Final move (orange)
                    ctx.beginPath();
                    ctx.moveTo(sx, sy);
                    ctx.lineTo(sx + mv.move.x, sy + mv.move.y);
                    ctx.strokeStyle = 'orange';
                    ctx.lineWidth = 3;
                    ctx.stroke();
                }

                requestAnimationFrame(updateOverlay);
            }
            updateOverlay();
        })();
        """
        driver.execute_script(script)

    driver.execute_script("""
    window._lastKnownSnakeSize = 0;
    window._foodCollected = 0;
    window._lastSnakeLength = (window.slither || window.snake)?.sc || 0;
    window._lastSnakeAlive = true;
    setInterval(function() {
        let snake = window.slither || window.snake;
        if (snake && snake.sc !== undefined) {
            window._lastKnownSnakeSize = snake.sc;
            if (snake.sc > window._lastSnakeLength) {
                window._foodCollected += (snake.sc - window._lastSnakeLength);
            }
            window._lastSnakeLength = snake.sc;
            window._lastSnakeAlive = true;
        } else {
            window._lastSnakeAlive = false;
        }
    }, 100);
    """)

    inject_overlay_script()

    # --- Now call the function ---

    try:
        while True:
            if not is_snake_alive():
                break  # Snake is dead, exit loop
            try:
                result = move_toward_food_and_avoid_snakes()
            except Exception as e:
                pass
            time.sleep(0.1)

        # --- Lifespan calculation ---
        life_end_time = time.time()
        lifespan = life_end_time - life_start_time
        final_snake_size = driver.execute_script("return (window.slither?.sct || window.snake?.sct || 0);")
        food_collected_count = driver.execute_script("return window._foodCollectedCount || 0;")
        food_blacklist_events = driver.execute_script("return window._foodBlacklistEvents || 0;")
        print(f"Your snake lived for {lifespan:.2f} seconds.")
        print(f"Final snake size: {final_snake_size}")
        print(f"Total food collected: {food_collected_count}")
        print(f"Food blacklist events: {food_blacklist_events}")

    except KeyboardInterrupt:
        pass

except Exception as e:
    pass

finally:
    # This block always runs, whether there was an error or not
    # It ensures we always close the browser properly
    time.sleep(2)  # Wait 2 seconds before closing
    driver.quit()  # Close the browser and end the WebDriver session
