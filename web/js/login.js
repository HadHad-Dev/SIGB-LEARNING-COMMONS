/* login.js · Pantalla de inicio de sesión */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var tabs = [$('tab-est'), $('tab-inv'), $('tab-adm')];
  var panels = [$('panel-est'), $('panel-inv'), $('panel-adm')];
  var err = UTR.errores(['f-mat', 'f-pest', 'f-nom', 'f-ape', 'f-mail', 'f-padm']);

  function select(i) {
    tabs.forEach(function (t, j) { t.setAttribute('aria-selected', j === i ? 'true' : 'false'); panels[j].hidden = j !== i; });
    err.limpiar();
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { select(i); });
    t.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
        var n = (i + (e.key === 'ArrowRight' ? 1 : -1) + 3) % 3; select(n); tabs[n].focus();
      }
    });
  });
  UTR.initOjos();

  /* Cada perfil: valida y devuelve los datos a enviar (o null si hay errores) */
  var perfiles = [
    function () {
      var mat = $('matricula').value.trim(), clave = $('clave-est').value, ok = true;
      if (!/^\d{7}$/.test(mat)) { err.poner('f-mat', 'Esa matrícula no está registrada. Revisa los números de tu credencial.'); ok = false; }
      if (!clave) { err.poner('f-pest', 'Escribe tu contraseña para continuar.'); ok = false; }
      return ok ? { perfil: 'estudiante', matricula: mat, clave: clave } : null;
    },
    function () {
      var nom = $('nombre').value.trim(), ape = $('apellido').value.trim(), ok = true;
      if (!nom) { err.poner('f-nom', 'Escribe tu nombre para continuar.'); ok = false; }
      if (!ape) { err.poner('f-ape', 'Escribe tus apellidos para continuar.'); ok = false; }
      return ok ? { perfil: 'invitado', nombre: nom, apellido: ape } : null;
    },
    function () {
      var mail = $('correo').value.trim(), clave = $('clave-adm').value, ok = true;
      if (!/^\S+@\S+\.\S+$/.test(mail)) { err.poner('f-mail', 'Ese correo no parece válido. Revisa que esté completo.'); ok = false; }
      if (!clave) { err.poner('f-padm', 'Escribe tu contraseña para continuar.'); ok = false; }
      return ok ? { perfil: 'administrador', correo: mail, clave: clave } : null;
    }
  ];
  var fallos = [
    function () { err.poner('f-mat', 'La matrícula o la contraseña no coinciden. Intenta de nuevo.'); err.marcar('f-pest'); },
    function () { err.poner('f-ape', 'No pudimos iniciar tu sesión. Intenta de nuevo.'); },
    function () { err.poner('f-padm', 'El correo o la contraseña no coinciden. Intenta de nuevo.'); err.marcar('f-mail'); }
  ];

  $('form').addEventListener('submit', async function (e) {
    e.preventDefault();
    err.limpiar();
    var i = panels.findIndex(function (p) { return !p.hidden; });
    var datos = perfiles[i]();
    if (!datos) return;
    try {
      await UTR.api.iniciarSesion(datos);   // ← base de datos: ver api.js
      window.location.href = 'servicios.html';
    } catch (x) { fallos[i](); }
  });
})();