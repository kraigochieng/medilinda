export interface PaginatedResponseInterface<T> {
	items?: T[];
	total: number;
	page: number;
	size: number;
	pages: number;
}
