var game_started = false;
var update_time;
var difficulty = "hard";

function init_game() {
    gamestate = new GameState();
    undyne = new Undyne();
    box = new Box();
    heart = new Heart();
    
    gameplay_stage.addChild(hp_text);
    gameplay_stage.addChild(time_text);
    gameplay_stage.addChild(love_text);
    
    start_game();
}

function start_game() {
    if(game_started == false) {
        game_started = true;
        
        gameplay_stage.alpha = 0;
        gamestate.level = 1;
        gamestate.restartGame(difficulty);
        
        update_time = new Date().getTime();
        requestAnimationFrame(update);
    }
}

function stop_game() {
    game_started = false;
}

// main game loop
function update() {
    
    if(game_started == true) {
        requestAnimationFrame(update);
    }
    
    var current_time = new Date().getTime();
    var delta_ms = clamp(current_time - update_time, 0, 100);
    
    update_time = current_time;
    
    scene.update(delta_ms);
    
    render();
    
}

window.onload = function() {
    
    setup_rendering();
    start_preload();
    
}
