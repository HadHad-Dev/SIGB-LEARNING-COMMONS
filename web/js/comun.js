/* comun.js · Utilidades compartidas de todas las pantallas.
   Se carga primero en cada HTML y expone el objeto global UTR. */
window.UTR = (function () {
  'use strict';
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function esc(t) { return String(t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  /* Fechas (formato interno 'AAAA-MM-DD') */
  function iso(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function deIso(s) { var p = s.split('-'); return new Date(+p[0], p[1] - 1, +p[2]); }
  function corta(s) { var p = s.split('-'); return p[2] + '/' + p[1] + '/' + p[0]; }
  function larga(s) { return deIso(s).toLocaleDateString('es-MX', { day: 'numeric', month: 'long', year: 'numeric' }); }
  function hoy() { var d = new Date(); return new Date(d.getFullYear(), d.getMonth(), d.getDate()); }

  /* Aviso general: necesita <div id="aviso" class="aviso" role="status" hidden></div> */
  function aviso(tipo, titulo, texto) {
    var el = document.getElementById('aviso');
    if (!el) return;
    el.className = 'aviso aviso--' + tipo;
    el.innerHTML = (titulo ? '<strong>' + esc(titulo) + '</strong> ' : '') + esc(texto);
    el.hidden = false;
    el.scrollIntoView({ block: 'nearest' });
  }

  /* Ojo de mostrar/ocultar contraseña (botones .eye con data-for="idDelInput") */
  function initOjos() {
    document.querySelectorAll('.eye').forEach(function (b) {
      b.addEventListener('click', function () {
        var inp = document.getElementById(b.getAttribute('data-for')), ver = inp.type === 'password';
        inp.type = ver ? 'text' : 'password';
        b.setAttribute('aria-pressed', ver ? 'true' : 'false');
        b.setAttribute('aria-label', ver ? 'Ocultar contraseña' : 'Mostrar contraseña');
      });
    });
  }

  /* Errores de formulario. ids = ids de los .field. Guarda el texto de ayuda original
     para restaurarlo en limpiar(). */
  function errores(ids) {
    var ayuda = {};
    function campo(id) { return document.getElementById(id); }
    ids.forEach(function (id) { var h = campo(id).querySelector('.help'); ayuda[id] = h ? h.textContent : ''; });
    return {
      poner: function (id, msg) { var f = campo(id); f.classList.add('error'); f.querySelector('.help').textContent = msg; },
      marcar: function (id) { campo(id).classList.add('error'); },
      limpiar: function () { ids.forEach(function (id) { var f = campo(id); f.classList.remove('error'); f.querySelector('.help').textContent = ayuda[id]; }); }
    };
  }

  return { pad: pad, esc: esc, iso: iso, deIso: deIso, corta: corta, larga: larga, hoy: hoy, aviso: aviso, initOjos: initOjos, errores: errores };
})();