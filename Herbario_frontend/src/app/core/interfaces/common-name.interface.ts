export interface CommonName {
  id: string;
  species_id: string;
  species_name?: string;
  language_id: string;
  language_code: string;
  language_name: string;
  common_name: string;
  dialect: string;
  region: string;
  created_at: string;
  updated_at: string;
}

export interface CommonNameWrite {
  species_id: string;
  language_id: string;
  common_name: string;
  dialect?: string;
}
