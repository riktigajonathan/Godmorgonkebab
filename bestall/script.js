document.querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', btnAction);
});

const toppings = {};

function btnAction(event) {
    const btn = event.target;
    const topping = btn.innerText.toLowerCase().split(' ')[0].trim();
    
    toppings[topping] = !toppings[topping];

    if (toppings[topping]) {
        btn.style.filter = "brightness(0.5)";

        const img = document.createElement("img");
        img.src = `assets/images/toppings/${topping}.png`;
        img.id = `layer-${topping}`;
        document.getElementById("pizza").appendChild(img);
    } else {
        btn.style.filter = "brightness(1)";

        const existingImg = document.getElementById(`layer-${topping}`);
        if (existingImg) {
            existingImg.remove();
        }
    }
}