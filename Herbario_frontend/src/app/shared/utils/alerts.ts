import { translateUiText } from '../../core/services/ui-text.service';
import Swal from 'sweetalert2';

export const showSuccess = (title: string, text: string) => {
  return Swal.fire({
    icon: 'success',
    title,
    text,
    allowEscapeKey: false,
    allowOutsideClick: false,
    confirmButtonText: translateUiText('code.shared.utils.alerts.aceptar')
  });
};

export const showError = (title: string, text: string) => {
  return Swal.fire({
    icon: 'error',
    title,
    text,
    allowEscapeKey: false,
    allowOutsideClick: false,
    confirmButtonText: translateUiText('code.shared.utils.alerts.aceptar')
  });
};

export const showConfirm = (title: string, text: string) => {
  return Swal.fire({
    icon: 'warning',
    title,
    text,
    allowEscapeKey: false,
    allowOutsideClick: false,
    showCancelButton: true,
    confirmButtonText: translateUiText('code.shared.utils.alerts.si_continuar'),
    cancelButtonText: translateUiText('actions.cancel')
  });
};
