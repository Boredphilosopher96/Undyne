/**
 * Initializes and runs the game.
 */
class Main {
    
    /**
     * The instance of Main used to obtain assets, the renderer, or the game dimensions.
     */
    static #runner;
    
    /**
     * Loads and manages the assets for the game.
     */
    #assetManager;
    
    /**
     * The container on which all the graphics are drawn.
     */
    #gameplayStage;
    
    /**
     * Manages the rendering of the game.
     */
    #rendererManager;
    
    /**
     * Handles the running of the game overall.
     */
    #gameHandler;
    
    /**
     * The width of the game.
     */
    #gameWidth;
    
    /**
     * The height of the game.
     */
    #gameHeight;
    
    /**
     * The last-used time for the update function.
     */
    #previousTime;
    
    /**
     * Initializes an instance of Main.
     */
    constructor() {
        this.#gameplayStage = new PIXI.Container();
        this.#gameWidth = 640;
        this.#gameHeight = 480;
    }
    
    /**
     * Returns the instance of Main used to obtain assets, the renderer, or the game dimensions.
     * @return The instance of Main used to obtain assets, the renderer, or the game dimensions
     */
    static get runner() {
        return this.#runner;
    }
    
    /**
     * Initializes the instance of Main used to obtain assets, the renderer, or the game dimensions.
     */
    static initializeMain() {
        this.#runner = new Main();
    }
    
    /**
     * Adds the renderer and begins the loading of the game.
     */
    load() {
        this.#rendererManager = new RendererManager();
        this.#assetManager = new AssetManager();
    }
    
    /**
     * Waits until the assets are loaded and then starts the game.
     * @param levelDataJson The level data in JSON format to parse
     * @param difficulty The difficulty of the game
     */
    startGame(levelDataJson, difficulty) {
        if(!this.#assetManager.isLoaded()) {
            setTimeout(() => this.startGame(levelDataJson, difficulty), 100);
            return;
        }
        
        //Adds the hover and click SFX to the back home feed button
        const backToHomeFeedButton = document.querySelector("#back-home-feed");
        backToHomeFeedButton.addEventListener(
            "mouseover", () => Main.runner.#assetManager.getAudio("buttonHoverSfx").play()
        );
        backToHomeFeedButton.addEventListener(
            "click", () => Main.runner.#assetManager.getAudio("buttonSelectSfx").play()
        );
        
        this.#gameHandler = new GameHandler(difficulty, levelDataJson, this.#gameplayStage, this.#rendererManager);
        
        KeyboardHandler.initialize(this.#gameHandler);
        
        //Remove the loading message now that the game is about to start
        document.getElementById("loading-container").remove();
        
        this.#previousTime = performance.now();
        requestAnimationFrame(this.update.bind(this));
    }
    
    /**
     * Computes the change since the last update and updates the state of the game objects.
     */
    update() {
        const currentTime = performance.now();
        const deltaMs = MathUtility.clamp(currentTime - this.#previousTime, 0, 100);
        this.#previousTime = currentTime;
        
        this.#gameHandler.update(deltaMs);
        
        requestAnimationFrame(this.update.bind(this));
    }
    
    /**
     * Returns the instance that loads and manages the assets for the game.
     * @return The instance that loads and manages the assets for the game
     */
    get assetManager() {
        return this.#assetManager;
    }
    
    /**
     * Returns the width of the game.
     * @return The width of the game.
     */
    get gameWidth() {
        return this.#gameWidth;
    }
    
    /**
     * Returns the height of the game.
     * @return The height of the game.
     */
    get gameHeight() {
        return this.#gameHeight;
    }
}
