export function useAdrQuery(params = { offset: 0, limit: 0 }) {
	return useQuery({
		queryKey: ["adrs", params],
		queryFn: async () => {
			const response = await fetchAdrs(params);
			if (response?.error) throw new Error(response.error.value?.message);
			return response?.data.value;
		},
	});
}

const getQuery = useQuery({
	queryKey: ["adrs", { offset: 0, limit: 10 }],
	queryFn: async () => (await fetchAdrs({ offset: 0, limit: 10 })) || [],
});
