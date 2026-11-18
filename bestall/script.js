document.querySelectorAll("button").forEach((button) => {
	button.addEventListener("click", btnAction);
});

const toppings = {};

function btnAction(event) {
	const btn = event.target;
	const topping = btn.textContent
		.toLowerCase()
		.split(" ")[0]
		.trim()
		.replace(/å/g, "a")
		.replace(/ä/g, "a")
		.replace(/ö/g, "o");

	toppings[topping] = !toppings[topping];

	if (toppings[topping]) {
		btn.style.filter = "brightness(0.8)";

		const img = document.createElement("img");

		img.src = `/assets/images/toppings/${topping}.png`;
		img.alt = btn.textContent;
		img.id = `layer-${topping}`;

		if (topping === "ost") {
			img.style.zIndex = -1;
		} else if (topping.endsWith("sas") || topping.endsWith("dressing")) {
			img.style.zIndex = 2;
		}

		document.getElementById("pizza").appendChild(img);
	} else {
		btn.style.filter = "brightness(1)";

		const existingImg = document.getElementById(`layer-${topping}`);
		if (existingImg) {
			existingImg.remove();
		}

		delete toppings[topping];
	}

	document.getElementById("price").textContent =
		`Pris: ${(Object.keys(toppings).length * 7 + 89)} kr`;
}
