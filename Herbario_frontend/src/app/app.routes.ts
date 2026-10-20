import { Routes } from "@angular/router";
import { authGuard } from './core/guards/auth.guard';
import { permissionGuard } from './core/guards/permission.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./public/layout/public-layout/public-layout.component').then(m => m.PublicLayoutComponent),
    children: [
      { path: '', loadComponent: () => import('./public/pages/home/home.component').then(m => m.HomeComponent) },
      { path: 'catalogo', loadComponent: () => import('./public/pages/catalog/catalog.component').then(m => m.CatalogComponent) },
      { path: "catalogo/:id", loadComponent: () => import('./public/pages/catalog-detail/catalog-detail.component').then(m => m.CatalogDetailComponent) },
      { path: 'especimenes', loadComponent: () => import('./public/pages/specimens/specimens.component').then(m => m.PublicSpecimensComponent) },
      { path: 'busqueda-avanzada', loadComponent: () => import('./public/pages/advanced-search/advanced-search.component').then(m => m.AdvancedSearchComponent) },
      { path: 'mapa', loadComponent: () => import('./public/pages/map/map.component').then(m => m.MapComponent) },
      { path: 'galeria', loadComponent: () => import('./public/pages/gallery/gallery.component').then(m => m.GalleryComponent) },
      { path: 'colecciones', loadComponent: () => import('./public/pages/collections/collections.component').then(m => m.CollectionsComponent) },
      { path: 'acerca', loadComponent: () => import('./public/pages/about/about.component').then(m => m.AboutComponent) },
    ]
  },
  {
    path: 'login',
    loadComponent: () =>
      import('./features/auth/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'admin',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./layout/main-layout/main-layout.component').then(m => m.MainLayoutComponent),
    children: [
      { path: 'dashboard', loadComponent: () => import('./features/admin/dashboard/dashboard.component').then(m => m.DashboardComponent) },
      { path: 'perfil', loadComponent: () => import('./features/shared/profile/profile.component').then(m => m.ProfileComponent) },
      { path: 'usuarios', canActivate: [permissionGuard], data: { permission: 'auth.view_user' }, loadComponent: () => import('./features/admin/users/users.component').then(m => m.UsersComponent) },
      { path: 'roles', canActivate: [permissionGuard], data: { permission: 'auth.view_group' }, loadComponent: () => import('./features/admin/roles/roles.component').then(m => m.RolesComponent) },
      { path: 'climas', canActivate: [permissionGuard], data: { permission: 'locations.view_climate', type: 'climates', title: 'Gestión de climas', singular: 'Clima', plural: 'Climas', icon: 'partly_cloudy_day', permissionModel: 'climate' }, loadComponent: () => import('./features/locations/environmental-catalog/environmental-catalog.component').then(m => m.EnvironmentalCatalogComponent) },
      { path: 'habitats', canActivate: [permissionGuard], data: { permission: 'locations.view_habitat', type: 'habitats', title: 'Gestión de hábitats', singular: 'Hábitat', plural: 'Hábitats', icon: 'forest', permissionModel: 'habitat' }, loadComponent: () => import('./features/locations/environmental-catalog/environmental-catalog.component').then(m => m.EnvironmentalCatalogComponent) },
      { path: "taxonomia/familias", canActivate: [permissionGuard], data: { permission: 'taxonomy.view_family' }, loadComponent: () => import('./features/taxonomy/families/families.component').then(m => m.FamiliesComponent) },
      { path: "taxonomia/generos", canActivate: [permissionGuard], data: { permission: 'taxonomy.view_genus' }, loadComponent: () => import('./features/taxonomy/genera/genera.component').then(m => m.GeneraComponent) },
      { path: "taxonomia/especies", canActivate: [permissionGuard], data: { permission: 'taxonomy.view_species' }, loadComponent: () => import('./features/taxonomy/species/species.component').then(m => m.SpeciesComponent) },
      { path: "taxonomia/estados", canActivate: [permissionGuard], data: { permission: 'taxonomy.view_status' }, loadComponent: () => import('./features/taxonomy/statuses/statuses.component').then(m => m.StatusesComponent) },
      { path: "taxonomia/nombres-comunes", canActivate: [permissionGuard], data: { permission: 'taxonomy.view_commonname' }, loadComponent: () => import('./features/taxonomy/common-names/common-names.component').then(m => m.CommonNamesComponent) },
      { path: "taxonomia/traducciones", canActivate: [permissionGuard], data: { permission: 'taxonomy.view_translation' }, loadComponent: () => import('./features/taxonomy/translations/translations.component').then(m => m.TranslationsComponent) },
      { path: "taxonomia/estados-conservacion", canActivate: [permissionGuard], data: { permission: 'taxonomy.view_conservationstatus' }, loadComponent: () => import('./features/taxonomy/conservation-statuses/conservation-statuses.component').then(m => m.ConservationStatusesComponent) },
      { path: 'colectores', canActivate: [permissionGuard], data: { permission: 'collectors.view_collector' }, loadComponent: () => import('./features/collectors/collectors.component').then(m => m.CollectorsComponent) },
      { path: 'especimenes', canActivate: [permissionGuard], data: { permission: 'specimens.view_specimen' }, loadComponent: () => import('./features/specimens/specimens.component').then(m => m.SpecimensComponent) },
      { path: 'imagenes', canActivate: [permissionGuard], data: { permission: 'media.view_herbariumimage' }, loadComponent: () => import('./features/media/images.component').then(m => m.ImagesComponent) },
      { path: 'colecciones', canActivate: [permissionGuard], data: { permission: 'collections_app.view_collection' }, loadComponent: () => import('./features/collections/collections.component').then(m => m.CollectionsComponent) },
      { path: 'contenido/acerca', canActivate: [permissionGuard], data: { permission: 'site_content.view_aboutpagecontent' }, loadComponent: () => import('./features/site-content/about-content/about-content.component').then(m => m.AboutContentComponent) },
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' }
    ]
  },
  { path: '**', redirectTo: '' }
];
