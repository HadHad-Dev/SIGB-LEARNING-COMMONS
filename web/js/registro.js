/* registro.js · Pantalla de crear cuenta */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var err = UTR.errores(['f-nom', 'f-mat', 'f-car', 'f-mail', 'f-pw']);
  UTR.initOjos();

  $('form').addEventListener('submit', async function (e) {
    e.preventDefault();
    err.limpiar();
    var ok = true;
    function fallo(id, m) { err.poner(id, m); ok = false; }

    var nombre = $('nombre').value.trim(), mat = $('matricula').value.trim(), carrera = $('carrera').value,
        correo = $('correo').value.trim(), clave = $('clave').value;
    if (nombre.split(/\s+/).filter(Boolean).length < 2) fallo('f-nom', 'Escribe tu nombre y al menos un apellido.');
    if (!/^\d{7}$/.test(mat)) fallo('f-mat', 'Escribe los 7 números de tu matrícula, tal como aparecen en tu credencial.');
    if (!carrera) fallo('f-car', 'Elige la carrera que cursas.');
    if (!/^\S+@utr\.edu\.mx$/i.test(correo)) fallo('f-mail', 'Escribe tu correo institucional, por ejemplo 2201145@utr.edu.mx.');
    if (clave.length < 8) fallo('f-pw', 'Tu contraseña necesita al menos 8 caracteres.');
    if (!ok) return;

    try {
      await UTR.api.registrar({ nombre: nombre, matricula: mat, carrera: carrera, correo: correo, clave: clave });   // ← base de datos: ver api.js
      window.location.href = 'login.html';
    } catch (x) {
      if (x.codigo === 'duplicada') err.poner('f-mat', 'Esa matrícula ya tiene una cuenta registrada. Inicia sesión o revisa tus números.');
      else err.poner('f-nom', 'No pudimos crear tu cuenta. Intenta de nuevo.');
    }
  });
})();