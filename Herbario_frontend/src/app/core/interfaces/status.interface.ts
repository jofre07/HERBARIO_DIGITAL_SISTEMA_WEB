export interface Status {
  id: string;
  code: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface StatusWrite {
  code: string;
  name: string;
  description?: string;
}
