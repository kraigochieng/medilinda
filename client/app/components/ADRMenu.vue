<template>
	<div class="fixed top-24 right-4 border rounded-sm bg-white p-2">
		<UPopover>
			<Icon name="lucide:menu" />
			<template #content>
				<div>
					<p class="font-semibold">Form Sections</p>
					<p>
						<a href="#institution-details">
							1. Institution Details
						</a>
					</p>
					<p>
						<a href="#patient-details"> 2. Patient Details </a>
					</p>
					<p>
						<a href="#suspected-adverse-reaction">
							3. Suspected Adverse Reaction
						</a>
					</p>
					<p>
						<a href="#medicines"> 4. Medicines </a>
					</p>
					<p>
						<a href="#rechallenge"> 5. Rechallenge/Dechallenge </a>
					</p>
					<p>
						<a href="#grading"> 6. Grading of the Event </a>
					</p>
					<p>
						<a href="#submit">
							7.
							{{
								props.mode == "create" ? "Add Adr" : "Edit ADR"
							}}
							Button
						</a>
					</p>
				</div>
			</template>
		</UPopover>
	</div>
</template>

<script setup lang="ts"></script>

<style></style>
