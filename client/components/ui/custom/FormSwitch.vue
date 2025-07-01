<template>
	<FormField v-slot="{ value, handleChange }" :name="name">
		<FormItem
			class="flex flex-row items-center justify-between rounded-lg border p-4"
		>
			<div class="space-y-0.5">
				<FormLabel class="text-base">{{ label }}</FormLabel>
				<FormDescription v-if="description">
					{{ description }}
				</FormDescription>
			</div>
			<FormControl>
				<Switch
					:model-value="value"
					:disabled="disabled"
					@update:model-value="handleChange"
				/>
			</FormControl>
			
		</FormItem>
		<FormMessage />
	</FormField>
</template>

<script setup lang="ts">
defineProps<{
	label: string;
	name: string;
	fieldAttrs?: any; // Attributes passed from defineField()
	description?: string;
	disabled?: boolean;
}>();
</script>
