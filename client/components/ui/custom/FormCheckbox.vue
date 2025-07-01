<template>
	<FormField
		v-slot="{ value, handleChange }"
		type="checkbox"
		:name="props.name"
	>
		<FormItem>
			<FormControl>
				<Checkbox
					:model-value="value"
					@update:model-value="handleChange"
				/>
			</FormControl>
			<FormLabel v-if="props.label">{{ props.label }}</FormLabel>
			<FormDescription v-if="props.description">
				{{ props.description }}
			</FormDescription>
			<FormMessage />
		</FormItem>
	</FormField>
</template>

<script setup lang="ts">
const props = defineProps<{
	name: string;
	label?: string;
	description?: string;
}>();
</script>
