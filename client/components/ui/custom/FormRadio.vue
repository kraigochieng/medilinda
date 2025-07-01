<script setup lang="ts">
const props = defineProps<{
	name: string;
	label: string;
	description?: string;
	defaultValue?: string;
	options: { value: string; label: string }[];
}>();
</script>

<template>
	<FormField v-slot="{ componentField }" type="radio" :name="name">
		<div class="form-field-wrapper">
			<FormItem>
				<FormLabel class="py-2"> {{ label }}</FormLabel>
				<FormControl>
					<RadioGroup v-bind="componentField" class="flex flex-col md:flex-row md:my-8 md:gap-x-4">
						<FormItem
							v-for="option in options"
							class="flex items-center space-y-0 gap-x-2"
						>
							<FormControl>
								<RadioGroupItem :value="option.value" />
							</FormControl>
							<FormLabel>{{ option.label }}</FormLabel>
						</FormItem>
					</RadioGroup>
				</FormControl>
				<FormDescription v-if="props.description">
					{{ description }}
				</FormDescription>
				<FormMessage />
			</FormItem>
		</div>
	</FormField>
	<!-- <RadioGroup :default-value="defaultValue == undefined ? '' : defaultValue"> -->
</template>
