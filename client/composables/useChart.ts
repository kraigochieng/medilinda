import type { ApexOptions } from "apexcharts";
import { startCase, toLower } from "lodash";

export function usePieChart(title: string, labels: string[], data: number[]) {
	const formattedLabels = labels.map((c) => startCase(toLower(c)));
	return {
		options: {
			chart: {
				type: "pie",
				fontFamily: "Inter",
				width: 200,
				height: 200,
			},
			labels: formattedLabels,
			title: {
				text: title,
				align: "left",
			},
			responsive: [
				{
					breakpoint: 480,
					options: {
						chart: { width: 200 },
						legend: { position: "bottom" },
					},
				},
			],
		} as ApexOptions,
		series: data as ApexNonAxisChartSeries,
	};
}

export function useBarChart(
	title: string,
	categories: string[],
	data: number[],
	barColors?: string[]
) {
	const formattedCategories = categories.map((c) => startCase(toLower(c)));
	const fallbackColor = "#254e75";

	return {
		options: {
			chart: {
				type: "bar",
				fontFamily: "Inter",
				// width: 200,
				// height: 200,
			},
			fill: {
				colors: ["#254E75"],
			},

			// color: (opts: any) => {
			// 	// opts.dataPointIndex gives the index of the current bar
			// 	if (barColors && barColors[opts.dataPointIndex]) {
			// 		return barColors[opts.dataPointIndex];
			// 	}
			// 	return fallbackColor;
			// },
			xaxis: { categories: formattedCategories },
			title: {
				text: title,
				align: "left",
			},
			plotOptions: {
				bar: { horizontal: true },
			},
		} as ApexOptions,
		series: [{ name: title, data }] as ApexAxisChartSeries,
	};
}

export function useLineChart(
	title: string,
	categories: string[],
	data: number[]
) {
	const formattedCategories = categories.map((c) => startCase(toLower(c)));

	return {
		options: {
			chart: {
				type: "line",
				fontFamily: "Inter",
				// width: 200,
				// height: 200,
				zoom: { enabled: false },
			},
			fill: {
				colors: ["#254E75"],
			},
			stroke: {
				curve: "straight",
			},
			xaxis: { categories: formattedCategories },
			title: {
				text: title,
				align: "left",
			},
			plotOptions: {
				bar: { horizontal: true },
			},
		} as ApexOptions,
		series: [{ name: title, data }] as ApexAxisChartSeries,
	};
}
