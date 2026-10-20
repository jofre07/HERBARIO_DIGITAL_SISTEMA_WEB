import { translateUiText } from '../services/ui-text.service';
import { Permission } from '../interfaces/permission.interface';

const ACTION_LABELS: Record<string, string> = {
  add: translateUiText('actions.add'),
  change: translateUiText('actions.edit'),
  delete: translateUiText('actions.delete'),
  view: translateUiText('code.core.helpers.permission_label_helper.ver')
};

const RESOURCE_LABELS: Record<string, string> = {
  group: 'roles',
  permission: 'permisos',
  user: 'usuarios',
  logentry: translateUiText('code.core.helpers.permission_label_helper.registros_administrativos'),
  collection: 'colecciones',
  collector: 'colectores',
  climatehabitat: translateUiText('views.features.locations.climate_habitats.climate_habitats.climas_y_habitats'),
  location: 'ubicaciones',
  herbariumimage: translateUiText('code.core.helpers.permission_label_helper.imagenes_del_herbario'),
  specimen: translateUiText('views.features.specimens.specimens.especimenes'),
  commonname: translateUiText('views.features.taxonomy.common_names.common_names.nombres_comunes'),
  conservationstatus: translateUiText('views.features.taxonomy.conservation_statuses.conservation_statuses.estados_de_conservacion'),
  family: 'familias',
  genus: translateUiText('views.features.taxonomy.genera.genera.generos'),
  language: 'idiomas',
  species: 'especies',
  status: 'estados',
  translation: 'traducciones',
  auditlog: translateUiText('code.core.helpers.permission_label_helper.registros_de_auditoria')
};

export interface TranslatedPermission {
  action: string;
  resource: string;
  label: string;
  optionLabel: string;
}

export function translatePermission(permission: string | Permission): TranslatedPermission {
  const rawPermission = typeof permission === 'string'
    ? permission
    : permission.permission || permission.codename;
  const codename = rawPermission.includes('.')
    ? rawPermission.split('.').pop() || rawPermission
    : rawPermission;
  const separatorIndex = codename.indexOf('_');
  const actionCode = separatorIndex >= 0 ? codename.slice(0, separatorIndex) : '';
  const resourceCode = separatorIndex >= 0 ? codename.slice(separatorIndex + 1) : codename;
  const action = ACTION_LABELS[actionCode] || humanize(actionCode || translateUiText('code.core.helpers.permission_label_helper.gestionar'));
  const resource = RESOURCE_LABELS[resourceCode] || humanize(resourceCode);

  return {
    action,
    resource,
    label: `${action} ${resource}`,
    optionLabel: `${capitalize(resource)} — ${action}`
  };
}

function humanize(value: string): string {
  return value.replace(/_/g, ' ').trim().toLowerCase();
}

function capitalize(value: string): string {
  return value ? value.charAt(0).toUpperCase() + value.slice(1) : value;
}
