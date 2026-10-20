export interface SpecimenLocation {
  id: string;
  location_id: string;
  location_name: string;
  latitude: string;
  longitude: string;
  location_comment: string;
  climate_id: string | null;
  climate_name: string;
  habitat_id: string | null;
  habitat_name: string;
  comment: string;
  marker_icon: string;
  is_primary: boolean;
  order: number;
}

export interface Specimen {
  id: string;
  catalog_code: string;
  is_published: boolean;
  collection_date: string;
  collection_number: string;
  morphological_description: string;
  species_id: string;
  species_name: string;
  genus_name: string;
  family_name: string;
  collector_id: string;
  collector_name: string;
  locations: SpecimenLocation[];
  location_id: string | null;
  latitude: string | null;
  longitude: string | null;
  conservation_status: string | null;
  image_urls: string[];
  image_count: number;
  created_at: string;
  updated_at: string;
}

export interface SpecimenListItem {
  id: string;
  catalog_code: string;
  species_name: string;
  genus_name: string;
  family_name: string;
  collector_name: string | null;
  primary_location_name: string | null;
  location_count: number;
  is_published: boolean;
}

export interface SpecimenNamedOption {
  id: string;
  name: string;
}

export interface SpecimenLocationOption extends SpecimenNamedOption {
  latitude: string;
  longitude: string;
  comment: string;
}

export interface SpecimenFormOptions {
  species: SpecimenNamedOption[];
  collectors: SpecimenNamedOption[];
  locations: SpecimenLocationOption[];
  climates: SpecimenNamedOption[];
  habitats: SpecimenNamedOption[];
}

export interface SpecimenLocationWrite {
  location_id?: string;
  new_location?: {
    name: string;
    latitude: string;
    longitude: string;
    comment?: string;
  };
  climate_id?: string | null;
  habitat_id?: string | null;
  comment?: string;
  marker_icon?: string;
  is_primary: boolean;
  order: number;
}

export interface SpecimenWrite {
  catalog_code: string;
  is_published: boolean;
  collection_date?: string;
  collection_number?: string;
  morphological_description?: string;
  species_id: string;
  collector_id?: string | null;
  locations: SpecimenLocationWrite[];
}
