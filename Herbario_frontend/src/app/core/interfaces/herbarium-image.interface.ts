export type HerbariumImageVariantName = 'thumbnail' | 'medium' | 'large';

export interface HerbariumImageVariant {
  url: string;
  width?: number;
  height?: number;
  file_size?: number;
  format?: string;
}

export interface AdminImageCover {
  id: string;
  thumbnail_url: string;
  credit: string;
}

export interface AdminImageListItem {
  specimen_id: string;
  catalog_code: string;
  image_count: number;
  cover: AdminImageCover | null;
}

export interface AdminImageAsset {
  id: string;
  credit: string;
  variants: {
    thumbnail: HerbariumImageVariant;
    large: HerbariumImageVariant;
  };
}

export interface AdminImageDetail {
  specimen_id: string;
  catalog_code: string;
  images: AdminImageAsset[];
}

export interface AdminSpecimenOption {
  id: string;
  catalog_code: string;
}

export interface HerbariumImageAsset {
  id: string;
  url: string;
  original_url?: string;
  variants?: Partial<Record<HerbariumImageVariantName, HerbariumImageVariant>>;
  credit: string;
}

export interface HerbariumImage {
  id: string;
  specimen_id: string;
  species_id: string;
  catalog_code: string;
  species_name: string;
  genus_name: string;
  family_name: string;
  collection_date: string | null;
  location_names: string[];
  conservation_status: string | null;
  image_type: string;
  url: string;
  original_url?: string;
  variants?: Partial<Record<HerbariumImageVariantName, HerbariumImageVariant>>;
  credit: string;
  created_at: string;
  updated_at: string;
  images?: HerbariumImageAsset[];
}

export interface HerbariumImageWrite {
  specimen_id: string;
  image?: File;
  credit?: string;
}
