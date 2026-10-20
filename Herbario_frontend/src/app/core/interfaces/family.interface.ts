export interface Family {
  id: string;
  name: string;
  comment: string;
  created_at: string;
  updated_at: string;
}

export interface FamilyWrite {
  name: string;
  comment?: string;
}
