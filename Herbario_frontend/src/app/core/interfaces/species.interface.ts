import type { Specimen } from './specimen.interface';

export interface Species {
  id: string;
  name: string;
  genus_id: string;
  genus_name: string;
  family_name: string;
  comment: string;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
}

export interface SpeciesWrite {
  name: string;
  genus_id: string;
  comment?: string;
  is_featured?: boolean;
}

export interface SpeciesCatalog {
  id: string;
  name: string;
  genus_name: string;
  family_name: string;
  comment: string;
  is_featured: boolean;
  common_names: string[];
  conservation_status: string | null;
  image_url: string | null;
  specimen_count: number;
  location_names: string[];
  climates: string[];
  habitats: string[];
}

export interface SpeciesCatalogDetail extends Omit<SpeciesCatalog, 'image_url'> {
  image_count: number;
  image_urls: string[];
  specimens: Array<Omit<Specimen, 'image_urls'>>;
}
