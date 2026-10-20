export interface ConservationStatus {
  id: string;
  species_id: string;
  species_name?: string;
  status_id: string;
  status_code: string;
  status_name: string;
  created_at: string;
  updated_at: string;
}

export interface ConservationStatusWrite {
  species_id: string;
  status_id: string;
}
