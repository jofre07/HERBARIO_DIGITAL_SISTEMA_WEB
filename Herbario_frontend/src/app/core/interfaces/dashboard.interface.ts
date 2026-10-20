export interface DashboardChartPoint {
  label: string;
  value: number;
}

export interface DashboardCharts {
  specimens_by_family: DashboardChartPoint[];
  specimens_by_year: DashboardChartPoint[];
  species_by_conservation_status: DashboardChartPoint[];
}

export interface HerbariumStats {
  species: number;
  specimens: number;
  families: number;
  genera: number;
  images: number;
  collectors: number;
  locations: number;
  collections: number;
  users: number;
  charts: DashboardCharts;
}
