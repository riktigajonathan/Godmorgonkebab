document.querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', btnAction);
});

var toppings = {};

function btnAction(event) {
    const btn = event.target;

    var topping = btn.innerText.toLowerCase().split(' ')[0].trim();
    toppings[topping] = !(toppings[topping] || false);

    btn.innerText = topping.charAt(0).toUpperCase() + topping.slice(1);

    if (toppings[topping]) {
        btn.style.filter = "brightness(0.5)";
    } else {
        btn.style.filter = "brightness(1)";
    }
}