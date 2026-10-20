export interface Genus {
  id: string;
  name: string;
  family_id: string;
  family_name: string;
  comment: string;
  created_at: string;
  updated_at: string;
}

export interface GenusWrite {
  name: string;
  family_id: string;
  comment?: string;
}
