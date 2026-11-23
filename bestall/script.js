// GJORD AV JONATHAN

document.querySelectorAll("button").forEach((button) => {
	if (button.id !== "buy") {
		button.addEventListener("click", btnAction);
	}
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

		img.src = `/assets/images/toppings/${topping}.webp`;
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
		`Pris: ${Object.keys(toppings).length * 7 + 89} kr`;
}

document.getElementById("buy").addEventListener("click", () => {
	const googlePaymentDataRequest = {
		environment: "TEST",
		apiVersion: 2,
		apiVersionMinor: 0,
		merchantInfo: {
			// A merchant ID is available after approval by Google.
			// @see {@link https://developers.google.com/pay/api/web/guides/test-and-deploy/integration-checklist}
			// merchantId: '12345678901234567890',
			merchantName: "GodmorgonKebab",
		},
		allowedPaymentMethods: [
			{
				type: "CARD",
				parameters: {
					allowedAuthMethods: ["PAN_ONLY", "CRYPTOGRAM_3DS"],
					allowedCardNetworks: [
						"AMEX",
						"DISCOVER",
						"INTERAC",
						"JCB",
						"MASTERCARD",
						"VISA",
					],
				},
				tokenizationSpecification: {
					type: "PAYMENT_GATEWAY",
					// Check with your payment gateway on the parameters to pass.
					// @see {@link https://developers.google.com/pay/api/web/reference/request-objects#gateway}
					parameters: {
						gateway: "example",
						gatewayMerchantId: "exampleGatewayMerchantId",
					},
				},
			},
		],
	};

	const request = new PaymentRequest(
		[
			{
				supportedMethods: "https://google.com/pay",
				data: googlePaymentDataRequest,
			},
		],
		{
			total: {
				label: "Total",
				amount: {
					currency: "SEK",
					value: document
						.getElementById("price")
						.textContent.replace("Pris: ", "")
						.replace("kr", "")
						.trim(),
				},
			},
		},
	);
	request.show().then((res) => res.complete("success"));
});
