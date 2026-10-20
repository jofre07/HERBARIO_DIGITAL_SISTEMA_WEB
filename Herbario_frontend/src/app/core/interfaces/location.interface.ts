export interface Location {
  id: string;
  name: string;
  latitude: string;
  longitude: string;
  comment: string;
  specimen_count?: number;
  created_at: string;
  updated_at: string;
}

export interface LocationWrite {
  name: string;
  latitude: string;
  longitude: string;
  comment?: string;
}

export interface MapPoint {
  id: string;
  catalog_code: string;
  species_id: string;
  species_name: string;
  genus_name: string;
  family_name: string;
  common_names: string[];
  collector_name: string | null;
  latitude: string;
  longitude: string;
  location_name: string;
  image_url: string | null;
  is_primary?: boolean;
  marker_icon?: string;
}
