import { UiTextPipe } from '../../../shared/pipes/ui-text.pipe';
import { Component, inject, OnInit } from "@angular/core";
import { CommonModule } from "@angular/common";
import { Router, RouterModule } from "@angular/router";
import { FormsModule } from "@angular/forms";
import { SpeciesService } from '../../../core/services/species.service';
import { StatsService } from '../../../core/services/stats.service';
import { SpeciesCatalog } from '../../../core/interfaces/species.interface';
import { HerbariumStats } from '../../../core/interfaces/dashboard.interface';
import { FilterOptionsService } from '../../../core/services/filter-options.service';
import { CountUpDirective } from '../../../shared/directives/count-up.directive';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [UiTextPipe, CommonModule, RouterModule, FormsModule, CountUpDirective],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
  private speciesService = inject(SpeciesService);
  private statsService = inject(StatsService);
  private router = inject(Router);
  private filterOptionsService = inject(FilterOptionsService);

  searchQuery = '';
  selectedFamily = '';
  selectedGenus = '';
  selectedStatus = '';

  families: string[] = [];
  genera: string[] = [];
  statuses: string[] = [];
  featuredSpecies: SpeciesCatalog[] = [];
  popularSearches: string[] = [];
  loadingPopularSearches = true;
  loadingCatalog = true;
  stats: HerbariumStats = {
    species: 0,
    specimens: 0,
    families: 0,
    genera: 0,
    images: 0,
    collectors: 0,
    locations: 0,
    collections: 0,
    users: 0,
    charts: {
      specimens_by_family: [],
      specimens_by_year: [],
      species_by_conservation_status: []
    }
  };

  ngOnInit(): void {
    this.filterOptionsService.getOptions().subscribe({
      next: options => {
        this.families = options.families;
        this.genera = options.genera.map(item => item.name);
        this.statuses = options.conservation_statuses;
        this.popularSearches = options.popular_searches.slice(0, 4);
        this.loadingPopularSearches = false;
      },
      error: () => {
        this.loadingPopularSearches = false;
      }
    });

    this.speciesService.getCatalog(1, 4, { featured: true }).subscribe({
      next: (res) => {
        this.featuredSpecies = res.results;
        this.loadingCatalog = false;
      },
      error: () => {
        this.loadingCatalog = false;
      }
    });

    this.statsService.getStats().subscribe({
      next: stats => this.stats = stats
    });
  }

  onSearch(): void {
    const params = new URLSearchParams();
    const searchTerm = this.searchQuery.trim();
    if (searchTerm) {
      params.set('q', searchTerm);
      this.filterOptionsService.recordSearch(searchTerm).subscribe({
        error: () => undefined
      });
    }
    if (this.selectedFamily) params.set('family', this.selectedFamily);
    if (this.selectedGenus) params.set('genus', this.selectedGenus);
    if (this.selectedStatus) params.set('status', this.selectedStatus);
    this.router.navigate(['/catalogo'], {
      queryParams: Object.fromEntries(params.entries())
    });
  }

  searchPopular(term: string): void {
    this.searchQuery = term;
    this.onSearch();
  }

}
