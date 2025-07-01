<template>
	<FormField :name="props.name">
		<div class="form-field-wrapper">
			<FormItem>
				<FormLabel v-if="props.label">
					{{ props.label }}
				</FormLabel>
				<FormControl>
					<div class="flex space-x-2">
						<Select v-model="selectedYear">
							<SelectTrigger>
								<SelectValue placeholder="Date"> </SelectValue>
							</SelectTrigger>
							<SelectContent>
								<SelectGroup>
									<SelectItem
										v-for="year in years"
										:key="year"
										:value="year"
									>
										{{ year }}
									</SelectItem>
								</SelectGroup>
							</SelectContent>
						</Select>
						<Select v-model="selectedMonth">
							<SelectTrigger>
								<SelectValue placeholder="Month"> </SelectValue>
							</SelectTrigger>
							<SelectContent>
								<SelectGroup>
									<SelectItem
										v-for="(month, index) in months"
										:key="month"
										:value="String(index + 1)"
									>
										{{ month }}
									</SelectItem>
								</SelectGroup>
							</SelectContent>
						</Select>
						<Select
							v-model="selectedDay"
							:disabled="
								selectedYear == '' || selectedMonth == ''
							"
						>
							<SelectTrigger>
								<SelectValue placeholder="Day"> </SelectValue>
							</SelectTrigger>
							<SelectContent>
								<SelectGroup>
									<SelectItem
										v-for="(day, index) in daysInMonth"
										:key="day"
										:value="String(day)"
									>
										{{ day }}
									</SelectItem>
								</SelectGroup>
							</SelectContent>
						</Select>
					</div>
				</FormControl>
				<FormDescription> {{ props.description }} </FormDescription>
				<FormMessage />
			</FormItem>
		</div>
	</FormField>
</template>

<script setup lang="ts">
import { getLocalTimeZone, today } from "@internationalized/date";

const value = defineModel<string>();

const props = withDefaults(
	defineProps<{
		name: string;
		label?: string;
		description?: string;
		maxYear?: string;
		defaultYear?: string;
		defaultMonth?: string;
		defaultDay?: string;
	}>(),
	{
		maxYear: "1900",
	}
);

const selectedDay = ref<string | undefined>(
	props.defaultDay ? props.defaultDay : undefined
);
const selectedMonth = ref<string | undefined>(
	props.defaultMonth ? props.defaultMonth : undefined
);
const selectedYear = ref<string | undefined>(
	props.defaultYear ? props.defaultYear : undefined
);

const months = [
	"January",
	"February",
	"March",
	"April",
	"May",
	"June",
	"July",
	"August",
	"September",
	"October",
	"November",
	"December",
];

const years = Array.from(
	{ length: today(getLocalTimeZone()).year - Number(props.maxYear) + 1 },
	(_, i) => String(Number(props.maxYear) + i)
).reverse();

// Check if a year is a leap year
const isLeapYear = (year: number) => {
	return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
};

// Compute how many days are valid for the selected month/year
const daysInMonth = computed(() => {
	if (!selectedMonth.value || !selectedYear.value) return 31; // default

	const month = Number(selectedMonth.value);
	const year = Number(selectedYear.value);

	if (month === 2) {
		return isLeapYear(year) ? 29 : 28;
	}

	return [4, 6, 9, 11].includes(month) ? 30 : 31; // Apr, Jun, Sep, Nov -> 30 days
});

// To set the string
watchEffect(() => {
	if (selectedYear.value && selectedMonth.value && selectedDay.value) {
		const dobString = `${selectedYear.value}-${String(
			selectedMonth.value
		).padStart(2, "0")}-${String(selectedDay.value).padStart(2, "0")}`;
		value.value = dobString;
	} else {
		value.value = undefined;
	}
});

// Reset selected day if month/year change and current day becomes invalid
watchEffect(() => {
	if (selectedYear.value && selectedMonth.value) {
		if (
			selectedDay.value &&
			Number(selectedDay.value) > daysInMonth.value
		) {
			selectedDay.value = undefined;
		}
	}
});
</script>
