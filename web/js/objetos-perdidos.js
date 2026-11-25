/* objetos-perdidos.js · Pantalla de objetos perdidos
   Los datos vienen de UTR.api (api.js):
     - obtenerEdificios()            → llena el filtro de edificio
     - consultarObjetosPerdidos(f)   → trae SOLO la página pedida, ya filtrada
   Cada vez que cambian la búsqueda, el edificio o la página, se vuelve a consultar.
   Así, al conectar la base de datos (USAR_MOCK = false en api.js) el filtrado y la
   paginación los hace el servidor y esta pantalla no necesita cambios. */
(function () {
  'use strict';
  var $ = function (s) { return document.querySelector(s); };
  var esc = UTR.esc;
  var POR_PAGINA = 6;
  var st = { texto: '', edificio: '', pagina: 1 };
  var token = 0, temporizador = null;

  var ICONO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 8h14l-1 12H6L5 8z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>';

  function dato(e, v) { return '<div class="dato"><span class="etiqueta">' + e + '</span><span>' + v + '</span></div>'; }
  function tarjeta(o) {
    var media = o.imagen ? '<img src="' + esc(o.imagen) + '" alt="' + esc(o.nombre) + '">' : ICONO;
    return '<article class="item" data-id="' + esc(o.id) + '"><div class="item__media">' + media + '</div>' +
      '<h3>' + esc(o.nombre) + '</h3><p class="item__desc">' + esc(o.descripcion) + '</p>' +
      dato('Encontrado en', esc(o.lugar)) + dato('Lo encontró', esc(o.encontradoPor)) + dato('Edificio', esc(o.edificio)) + '</article>';
  }

  /* Números de página a mostrar: 1 … 4 5 6 … 12 */
  function numeros(a, t) {
    var r = [], i;
    if (t <= 7) { for (i = 1; i <= t; i++) r.push(i); return r; }
    r.push(1);
    if (a > 3) r.push('…');
    for (i = Math.max(2, a - 1); i <= Math.min(t - 1, a + 1); i++) r.push(i);
    if (a < t - 2) r.push('…');
    r.push(t);
    return r;
  }
  function pintarPaginas(total) {
    var t = Math.ceil(total / POR_PAGINA), nav = $('#paginacion');
    nav.hidden = t <= 1;
    if (t <= 1) { nav.innerHTML = ''; return; }
    var h = '<button class="btn btn--secundario" type="button" data-pagina="' + (st.pagina - 1) + '"' + (st.pagina === 1 ? ' disabled' : '') + '>Anterior</button>';
    numeros(st.pagina, t).forEach(function (p) {
      h += p === '…' ? '<span class="pag-punto" aria-hidden="true">…</span>'
        : '<button type="button" class="pag-num" data-pagina="' + p + '"' + (p === st.pagina ? ' aria-current="page"' : '') + ' aria-label="Página ' + p + '">' + p + '</button>';
    });
    h += '<button class="btn btn--secundario" type="button" data-pagina="' + (st.pagina + 1) + '"' + (st.pagina === t ? ' disabled' : '') + '>Siguiente</button>';
    nav.innerHTML = h;
  }

  async function cargar() {
    var mi = ++token, lista = $('#lista');
    try {
      // BASE DE DATOS · Consulta de registros: texto + edificio + página (ver api.js)
      var r = await UTR.api.consultarObjetosPerdidos({ texto: st.texto, edificio: st.edificio, pagina: st.pagina, porPagina: POR_PAGINA });
      if (mi !== token) return;                       // llegó una respuesta más nueva
      var t = Math.max(1, Math.ceil(r.total / POR_PAGINA));
      if (st.pagina > t) { st.pagina = t; return cargar(); }   // la página ya no existe
      $('#aviso').hidden = true;
      $('#conteo').textContent = r.total + (r.total === 1 ? ' objeto' : ' objetos');
      lista.innerHTML = r.objetos.length ? r.objetos.map(tarjeta).join('')
        : '<p class="vacio">' + ((st.texto || st.edificio) ? 'No encontramos objetos con esos filtros. Prueba con otra palabra o con otro edificio.' : 'Por ahora no hay objetos reportados.') + '</p>';
      pintarPaginas(r.total);
    } catch (e) {
      if (mi !== token) return;
      UTR.aviso('error', '', 'No pudimos cargar los objetos. Intenta de nuevo en unos minutos.');
      lista.innerHTML = '<p class="vacio">No pudimos cargar esta sección.</p>';
      $('#paginacion').hidden = true;
    }
  }

  $('#buscar').addEventListener('input', function (e) {
    clearTimeout(temporizador);
    temporizador = setTimeout(function () { st.texto = e.target.value.trim(); st.pagina = 1; cargar(); }, 250);
  });
  $('#edificio').addEventListener('change', function (e) { st.edificio = e.target.value; st.pagina = 1; cargar(); });
  $('#paginacion').addEventListener('click', function (e) {
    var b = e.target.closest('[data-pagina]');
    if (!b || b.disabled) return;
    st.pagina = +b.dataset.pagina;
    cargar();
    $('#t-objetos').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  (async function () {
    try {
      // BASE DE DATOS · Lista de edificios para el filtro (ver api.js)
      (await UTR.api.obtenerEdificios()).forEach(function (n) {
        var o = document.createElement('option'); o.value = n; o.textContent = n; $('#edificio').appendChild(o);
      });
    } catch (e) { /* si falla, el filtro queda en "Todos los edificios" */ }
    cargar();
  })();
})();