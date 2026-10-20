export interface Translation {
  id: string;
  common_name: string;
  common_name_id: string;
  language_id: string;
  language_code: string;
  language_name: string;
  translated_name: string;
  created_at: string;
  updated_at: string;
}

export interface TranslationWrite {
  common_name_id: string;
  language_id: string;
  translated_name: string;
}
