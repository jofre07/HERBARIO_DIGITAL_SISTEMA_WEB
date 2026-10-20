export interface ApiResponse<T> {
  data: T;
  message?: string;
  code?: string;
}

export interface ApiListResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
