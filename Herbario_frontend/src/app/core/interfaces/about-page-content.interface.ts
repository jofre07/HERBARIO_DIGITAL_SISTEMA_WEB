export interface AboutContentCard {
  title: string;
  description: string;
}

export interface AboutPageContent {
  introduction_title: string;
  introduction_body: string;
  introduction_image_url: string | null;
  impact_items: AboutContentCard[];
  mission: string;
  vision: string;
  values: string[];
  team_title: string;
  team_subtitle: string;
  team_members: AboutContentCard[];
  contact_address: string;
  contact_email: string;
  contact_phone: string;
  institution: string;
  updated_at: string | null;
}

export type AboutPageContentUpdate = Omit<AboutPageContent, 'introduction_image_url' | 'updated_at'>;

export const DEFAULT_ABOUT_PAGE_CONTENT: AboutPageContent = {
  introduction_title: '¿Qué es el Herbario Digital?',
  introduction_body: 'El Herbario Digital es una plataforma web para gestionar, consultar y difundir información sobre la diversidad vegetal. Reúne especímenes recolectados, datos taxonómicos, ubicaciones geográficas, imágenes y recursos que apoyan la investigación, la educación y la conservación.',
  introduction_image_url: null,
  impact_items: [
    { title: 'Conservación', description: 'Contribuye al conocimiento y la conservación de la flora regional y nacional.' },
    { title: 'Investigación', description: 'Facilita el acceso a datos organizados para la consulta científica.' },
    { title: 'Educación', description: 'Ofrece recursos digitales para el aprendizaje y la formación académica.' },
    { title: 'Colaboración', description: 'Favorece el trabajo conjunto entre estudiantes, docentes e investigadores.' }
  ],
  mission: 'Gestionar y difundir información botánica de calidad mediante herramientas digitales, contribuyendo a la investigación, la educación y la conservación de la biodiversidad vegetal.',
  vision: 'Ser un referente en la gestión digital de colecciones botánicas y promover el conocimiento de la flora para las futuras generaciones.',
  values: ['Rigor científico', 'Transparencia', 'Responsabilidad ambiental', 'Colaboración y acceso abierto'],
  team_title: 'Equipo institucional',
  team_subtitle: 'Funciones que sostienen la gestión científica y digital del herbario.',
  team_members: [
    { title: 'Coordinación', description: 'Planificación y dirección del herbario' },
    { title: 'Curaduría', description: 'Gestión de colecciones botánicas' },
    { title: 'Investigación', description: 'Estudio y validación taxonómica' },
    { title: 'Gestión de datos', description: 'Administración de registros digitales' }
  ],
  contact_address: 'Campus Politécnico, Calceta, Manabí',
  contact_email: 'herbario@espam.edu.ec',
  contact_phone: '+593 5 268 2776',
  institution: 'ESPAM MFL',
  updated_at: null
};
