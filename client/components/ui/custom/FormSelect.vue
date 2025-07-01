<template>
	<FormField v-slot="{ componentField }" :name="name" v-bind="fieldAttrs">
		<FormItem>
			<FormLabel v-if="label">{{ label }}</FormLabel>
			<Select v-bind="componentField">
				<FormControl>
					<SelectTrigger>
						<SelectValue :placeholder="placeholder" />
					</SelectTrigger>
				</FormControl>
				<SelectContent>
					<SelectGroup>
						<SelectItem
							v-for="option in options"
							:value="option.value"
						>
							{{ option.label }}
						</SelectItem>
					</SelectGroup>
				</SelectContent>
			</Select>
			<FormMessage />
		</FormItem>
	</FormField>
</template>

<script setup lang="ts">
defineProps<{
	name: string;
	label?: string;
	fieldAttrs?: any; // Attributes passed from defineField()
	placeholder: string;
	options: { value: string; label: string }[];
}>();
</script>
