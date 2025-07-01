<template>
	<FormField v-slot="{ componentField }" :name="name">
		<FormItem>
			<FormLabel>{{ label }}</FormLabel>
			<FormControl>
				<Textarea :placeholder="placeholder" v-bind="componentField" />
			</FormControl>
			<FormDescription>
				{{ description }}
			</FormDescription>
			<FormMessage />
		</FormItem>
	</FormField>
</template>

<script setup lang="ts">
defineProps<{
	label: string;
	name: string;
	fieldAttrs?: any; // Attributes passed from defineField()
	placeholder: string;
	description?: string;
}>();
</script>
