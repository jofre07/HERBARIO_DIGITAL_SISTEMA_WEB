export interface FilterOptionRelation {
  name: string;
  family_name?: string;
  genus_name?: string;
}

export interface PublicFilterOptions {
  families: string[];
  genera: FilterOptionRelation[];
  species: FilterOptionRelation[];
  collectors: string[];
  locations: string[];
  habitats: string[];
  climates: string[];
  conservation_statuses: string[];
  common_names: string[];
  popular_searches: string[];
  image_types: Array<{ value: string; label: string }>;
  collection_categories: Array<{ value: string; label: string; count: number }>;
  collection_specimen_count: number;
}
