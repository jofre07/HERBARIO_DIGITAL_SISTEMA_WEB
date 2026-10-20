import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';
import { FilterOptionsService } from '../../../core/services/filter-options.service';
import { SpeciesService } from '../../../core/services/species.service';
import { StatsService } from '../../../core/services/stats.service';
import { HomeComponent } from './home.component';

describe('HomeComponent', () => {
  let fixture: ComponentFixture<HomeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HomeComponent],
      providers: [
        provideRouter([]),
        {
          provide: FilterOptionsService,
          useValue: {
            getOptions: () => of({
              families: [],
              genera: [],
              species: [],
              collectors: [],
              locations: [],
              habitats: [],
              climates: [],
              conservation_statuses: [],
              common_names: [],
              popular_searches: [],
              image_types: [],
              collection_categories: [],
              collection_specimen_count: 0
            }),
            recordSearch: () => of(undefined)
          }
        },
        {
          provide: SpeciesService,
          useValue: {
            getCatalog: () => of({ count: 0, next: null, previous: null, results: [] })
          }
        },
        {
          provide: StatsService,
          useValue: {
            getStats: () => of({
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
            })
          }
        }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(HomeComponent);
    fixture.detectChanges();
  });

  afterEach(() => fixture.destroy());

  it('renders the page content inside a semantic main landmark', () => {
    const main = fixture.nativeElement.querySelector('main.home-page');

    expect(main).not.toBeNull();
    expect(main.querySelector('.home-hero')).not.toBeNull();
    expect(main.querySelector('.featured-section')).not.toBeNull();
  });
});
