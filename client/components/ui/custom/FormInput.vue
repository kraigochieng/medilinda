<template>
	<FormField v-slot="{ componentField }" :name="name">
		<div class="form-field-wrapper">
			<FormItem>
			<FormLabel>{{ label }}</FormLabel>
			<FormControl>
				<div ref="inputContainer">
					<Input
						:type="type"
						:placeholder="placeholder"
						v-bind="componentField"
					/>
				</div>
			</FormControl>
			<FormDescription v-if="description">
				{{ description }}
			</FormDescription>
			<FormMessage />
		</FormItem>
		</div>
		
	</FormField>
</template>

<script setup lang="ts">
defineProps<{
	type: string;
	name: string;
	label?: string;
	placeholder: string;
	description?: string;
}>();

// This is because the <Input/> tag is not a plain input
const inputContainer = ref<HTMLElement | null>(null);

defineExpose({
	focus: () => {
		const input = inputContainer.value?.querySelector("input");
		input?.focus();
	},
});
</script>
