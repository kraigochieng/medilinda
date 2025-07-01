<template>
	<FormField :name="name">
		<FormItem class="flex flex-col">
			<FormLabel>{{ label }}</FormLabel>
			<Popover>
				<PopoverTrigger as-child>
					<FormControl>
						<Button
							variant="outline"
							:class="
								cn(
									'w-[240px] ps-3 text-start font-normal',
									!computedValue && 'text-muted-foreground'
								)
							"
						>
							<span>{{
								computedValue
									? df.format(toDate(computedValue))
									: "Pick a date"
							}}</span>
							<Icon
								name="lucide:calendar"
								class="ms-auto h-4 w-4 opacity-50"
							/>
						</Button>
						<input hidden />
					</FormControl>
				</PopoverTrigger>
				<PopoverContent class="w-auto p-0">
					<Calendar
						v-model:placeholder="placeholder"
						v-model="computedValue"
						:calendar-label="label"
						initial-focus
						:min-value="new CalendarDate(1900, 1, 1)"
						:max-value="today(getLocalTimeZone())"
						@update:model-value="
							(v: any) => {
								if (v) {
									setFieldValue(name, v.toString());
								} else {
									setFieldValue(name, undefined);
								}
							}
						"
					/>
				</PopoverContent>
			</Popover>
			<FormDescription>
				{{ props.description }}
			</FormDescription>
			<FormMessage />
		</FormItem>
	</FormField>
</template>

<script setup lang="ts">
import { cn } from "@/lib/utils";
import {
	CalendarDate,
	DateFormatter,
	getLocalTimeZone,
	parseDate,
	today,
} from "@internationalized/date";
import { toDate } from "radix-vue/date";

const props = defineProps<{
	name: string;
	label: string;
	value?: string;
	description?: string;
	setFieldValue: any;
}>();

const df = new DateFormatter("en-US", {
	dateStyle: "long",
});

const placeholder = ref();

const computedValue = computed({
	get: () => (props.value ? parseDate(props.value) : undefined),
	set: (val) => val,
});
</script>
