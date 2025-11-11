// Pequeñas utilidades UI (por ahora vacío, listo para agregar)
document.addEventListener('DOMContentLoaded', ()=> {
  // ejemplo: focus en primer input si existe
  const firstInput = document.querySelector('input:not([type=hidden])');
  if(firstInput) firstInput.focus();
});
