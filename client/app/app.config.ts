export default defineAppConfig({
	ui: {
		// Component Customisation
		formField: {
			slots: {
				root: "my-4",
			},
		},
		input: {
			slots: {
				root: "w-full min-w-32",
			},
		},
		inputNumber: {
			slots: {
				root: "w-full",
			},
		},
		textarea: {
			slots: {
				root: "w-full",
			},
		},
		separator: {
			slots: {
				root: "my-8",
			},
		},
		// Colour Scheme
		colors: {
			// primary: "blue-900",
		},
	},
});
