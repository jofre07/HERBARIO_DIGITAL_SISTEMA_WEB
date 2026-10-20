import { translateUiText } from '../../core/services/ui-text.service';
import * as L from 'leaflet';

export type MarkerIconType = 'plant' | 'flower' | 'tree' | 'leaf' | 'herb';
export type PlantMarkerSize = 'compact' | 'small' | 'medium' | 'normal';

export const MARKER_ICON_OPTIONS: ReadonlyArray<{
  value: MarkerIconType;
  label: string;
  icon: string;
}> = [
  { value: 'plant', label: translateUiText('code.shared.utils.map_marker.planta'), icon: 'bi-flower1' },
  { value: 'flower', label: translateUiText('code.shared.utils.map_marker.flor'), icon: 'bi-flower2' },
  { value: 'tree', label: translateUiText('code.shared.utils.map_marker.arbol'), icon: 'bi-tree-fill' },
  { value: 'leaf', label: translateUiText('code.shared.utils.map_marker.hoja'), icon: 'bi-leaf-fill' },
  { value: 'herb', label: translateUiText('code.shared.utils.map_marker.hierba'), icon: 'bi-flower3' }
];

export function plantMarkerIcon(
  markerIcon: string = 'plant',
  primary = false,
  size: PlantMarkerSize = 'normal'
): L.DivIcon {
  const option = MARKER_ICON_OPTIONS.find(item => item.value === markerIcon) || MARKER_ICON_OPTIONS[0];
  return L.divIcon({
    className: `plant-map-marker-container plant-map-marker-container--${size}`,
    html: `<span class="plant-map-marker${primary ? ' plant-map-marker-primary' : ''}" aria-hidden="true"><i class="bi ${option.icon}"></i></span>`,
    iconSize: [36, 42],
    iconAnchor: [18, 38],
    popupAnchor: [0, -36]
  });
}
