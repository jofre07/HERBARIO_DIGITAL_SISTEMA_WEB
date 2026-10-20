export type CollectionType = 'destacada' | 'amenazada' | 'reciente' | 'local' | 'general';

export interface Collection {
  id: string;
  name: string;
  description: string;
  collection_type: CollectionType;
  collection_type_label: string;
  specimen_ids: string[];
  specimen_count: number;
  species_count: number;
  location_count: number;
  image_url: string | null;
  family_names: string[];
  location_names: string[];
  conservation_statuses: string[];
  created_at: string;
  updated_at: string;
}

export interface CollectionWrite {
  name: string;
  description?: string;
  collection_type?: CollectionType;
  specimen_ids?: string[];
}
