/**
 * Represents a button on the screen.
 */
class Button extends GraphicsObject {
    
    /**
     * The button sprite.
     */
    #sprite;
    
    /**
     * The button hover sprite.
     */
    #hoverSprite;
    
    /**
     * The visibility of this button.
     */
    #visible;
    
    /**
     * The time it takes to transition from the normal button to the hover button.
     */
    #transitionTime;
    
    /**
     * The time spent hovering over the button up to the transition time.
     */
    #hoverTime;
    
    /**
     * True if the mouse is hovering over the button.
     */
    #hovering;
    
    /**
     * The button action.
     */
    #buttonAction;
    
    /**
     * Initializes a button.
     * @param x The x-position of the button.
     * @param y The y-position of the button.
     * @param width The width of the button.
     * @param height The height of the button.
     * @param imageName The name of the image associated with the button
     * @param buttonAction The action to take on button click/touch
     * @param imageHoverName The name of the image associated with the button on hover
     * @param hoverAction The action to take on button mouseover
     * @param transitionMs The time it will take to transition between the normal button sprite and the hover sprite
     * @param gameplayStage The container on which all the graphics are drawn
     */
    constructor(x, y, width, height, imageName, buttonAction, imageHoverName, hoverAction, transitionMs,
        gameplayStage) {
        super();
        
        this.#sprite = new PIXI.Sprite(Main.runner.assetManager.getTexture(imageName));
        this.#sprite.x = x;
        this.#sprite.y = y;
        this.#sprite.width = width;
        this.#sprite.height = height;
        this.#sprite.interactive = true;
        this.#sprite.buttonMode = true;
        this.#sprite.on("mousedown", buttonAction);
        this.#sprite.on("touchdown", buttonAction);
        this.#buttonAction = buttonAction;
        this.#visible = true;
        
        /*
         * If the image hover name is not null, set up the hover transition between the image with imageName and the
         * image with imageHoverName
         */
        if(imageHoverName !== null && imageHoverName !== undefined) {
            this.#hoverSprite = new PIXI.Sprite(Main.runner.assetManager.getTexture(imageHoverName));
            this.#hoverSprite.x = x;
            this.#hoverSprite.y = y;
            this.#hoverSprite.width = width;
            this.#hoverSprite.height = height;
            
            this.#transitionTime = transitionMs;
            this.#hoverTime = 0;
            this.#hovering = false;
            
            this.#sprite.on("mouseover", () => {
                hoverAction();
                this.#hovering = true;
            });
            this.#sprite.on("mouseout", () => {this.#hovering = false;});
            
            gameplayStage.addChild(this.#hoverSprite);
        }
        else {
            this.#hoverSprite = null;
        }
        
        gameplayStage.addChild(this.#sprite);
    }
    
    /**
     * Performs the action normally done when clicking the button.
     */
    click() {
        this.#buttonAction();
    }
    
    /**
     * Returns the visibility of this button.
     * @return The visibility of this button
     */
    get visible() {
        return this.#visible;
    }
    
    /**
     * Sets the visibility of this button.
     * @param visibility The new visibility of the button
     */
    set visible(visibility) {
        this.#sprite.visible = visibility;
        this.#hoverSprite.visible = visibility;
        this.#visible = visibility;
    }
    
    /**
     * Updates the opacity of the button if a hover image is provided.
     * @param deltaMs The The time that has passed since the last update of the button
     */
    update(deltaMs) {
        if(this.#hoverSprite !== null && this.#sprite.visible === true) {
            this.#hoverTime += this.#hovering ? deltaMs : -deltaMs;
            this.#hoverTime = MathUtility.clamp(this.#hoverTime, 0, this.#transitionTime);
            
            this.#sprite.alpha = 1 - this.#hoverTime / this.#transitionTime;
        }
        else {
            this.#sprite.alpha = 1;
        }
    }
}
