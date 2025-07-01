<template>
	<FormField v-slot="{ value }" :name="props.name">
		<div class="form-field-wrapper">
			<FormItem>
				<FormLabel v-if="props.label">{{ props.label }}</FormLabel>
				<NumberField
					class="gap-2 w-max"
					:min="props.min"
					:model-value="value"
					:step="step"
					v-bind="
						props.formatOptions
							? { formatOptions: props.formatOptions }
							: {}
					"
					@update:model-value="
						(v) => {
							if (v) {
								myValue = v;
							} else {
								myValue = undefined;
							}
						}
					"
				>
					<NumberFieldContent>
						<NumberFieldDecrement />
						<FormControl>
							<NumberFieldInput />
						</FormControl>
						<NumberFieldIncrement />
					</NumberFieldContent>
				</NumberField>
				<FormDescription v-if="props.description">
					{{ props.description }}
				</FormDescription>
				<FormMessage />
			</FormItem>
		</div>
	</FormField>
</template>

<script setup lang="ts">
const myValue = defineModel<number>();

const props = withDefaults(
	defineProps<{
		name: string;
		label?: string;
		description?: string;
		min?: number;
		max?: number;
		step?: number;
		formatOptions?: Intl.NumberFormatOptions;
	}>(),
	{
		min: 0,
		step: 1,
	}
);
</script>
