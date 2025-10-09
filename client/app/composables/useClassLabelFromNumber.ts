export function useClassLabelFromNumber(classNumber: number): string | undefined {
	switch (classNumber) {
		case 0:
			return "certain";
		case 1:
			return "likely";
		case 2:
			return "possible";
		case 3:
			return "unlikely";
		case 4:
			return "unclassified";
		case 5:
			return "unclassifiable";
	}
}
