export interface ClimateHabitat {
  id: string;
  location_id: string;
  climate: string;
  habitat: string;
  created_at: string;
  updated_at: string;
}

export interface ClimateHabitatWrite {
  location_id: string;
  climate?: string;
  habitat?: string;
}

export interface MapPoint {
  id: string;
  catalog_code: string;
  species_id: string;
  species_name: string;
  family_name: string;
  latitude: number;
  longitude: number;
  location_name: string;
  image_url: string;
}
