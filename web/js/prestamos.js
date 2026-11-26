/* prestamos.js · Pantalla de préstamos
   Los datos vienen de UTR.api (api.js): cargarCatalogo, obtenerFechasOcupadas y enviarSolicitud. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var esc = UTR.esc, iso = UTR.iso, deIso = UTR.deIso, corta = UTR.corta, larga = UTR.larga, hoy = UTR.hoy, aviso = UTR.aviso;

  var ICONOS = {
    libro: '<rect x="3" y="4" width="4" height="16" rx="1"/><rect x="9" y="4" width="4" height="16" rx="1"/><path d="M15.2 5.6l3.8-1 3 14.2-3.8 1z"/>',
    laptop: '<rect x="4" y="5" width="16" height="11" rx="1.5"/><path d="M2 19h20"/>',
    pc: '<rect x="3" y="4" width="18" height="12" rx="1.5"/><path d="M8 20h8M12 16v4"/>',
    equipo: '<path d="M4 8h3l1.5-2h7L17 8h3a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/><circle cx="12" cy="13" r="3.5"/>'
  };
  function icono(n) { return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + ICONOS[n] + '</svg>'; }

  var NOMBRES = { libros: 'libros', computadoras: 'computadoras', equiposElectronicos: 'equipos electrónicos' };

  var datos = {};

  function buscar(cat, id) { return (datos[cat] || []).filter(function (x) { return x.id === id; })[0]; }

  /* ---- Catálogo ---- */
  function dato(e, v) { return '<div class="dato"><span class="etiqueta">' + e + '</span><span>' + v + '</span></div>'; }
  function tarjeta(cat, it) {
    var nombre = it.titulo || it.nombre;
    var ico = cat === 'libros' ? 'libro' : cat === 'computadoras' ? (it.tipo === 'laptop' ? 'laptop' : 'pc') : 'equipo';
    var media = (it.imagen && cat !== 'computadoras') ? '<img src="' + esc(it.imagen) + '" alt="' + esc(nombre) + '">' : icono(ico);
    var info = cat === 'libros'
      ? dato('Autor', esc(it.autor)) + dato('Publicación', '<span class="mono">' + esc(it.publicacion) + '</span>')
      : cat === 'computadoras' ? '' : dato('Especificaciones', esc(it.especificaciones));
    return '<article class="item" data-id="' + esc(it.id) + '"><div class="item__media item__media--' + cat + '">' + media + '</div>' +
      '<h3>' + esc(nombre) + '</h3>' + info +
      '<button class="btn btn--secundario" type="button" data-accion="solicitar" data-categoria="' + cat + '" data-id="' + esc(it.id) + '">Solicitar préstamo</button></article>';
  }
  function pintar(cat) {
    var sec = $('[data-categoria="' + cat + '"]'), arr = datos[cat] || [];
    $('[data-conteo]', sec).textContent = arr.length + ' en catálogo';
    $('[data-lista]', sec).innerHTML = arr.length ? arr.map(function (it) { return tarjeta(cat, it); }).join('')
      : '<p class="vacio">Por ahora no hay ' + NOMBRES[cat] + ' en el catálogo.</p>';
  }
  document.querySelectorAll('[data-filtro]').forEach(function (b) {
    b.addEventListener('click', function () {
      var f = b.dataset.filtro;
      document.querySelectorAll('[data-filtro]').forEach(function (x) { x.setAttribute('aria-pressed', x === b); });
      document.querySelectorAll('.seccion').forEach(function (s) { s.hidden = f !== 'todos' && s.dataset.categoria !== f; });
    });
  });

  /* ---- Mini calendario ---- */
  var modal = $('#modal'), st = null;
  function msg(t, error) { var m = $('#m-msg'); m.textContent = t || ''; m.classList.toggle('help--error', !!error); }
  function primero(d) { return new Date(d.getFullYear(), d.getMonth(), 1); }
  function hayOcupadas(a, b) {
    for (var d = deIso(a); iso(d) <= b; d.setDate(d.getDate() + 1)) { if (st.ocupadas.has(iso(d))) return true; }
    return false;
  }
  function campo(id, v) { var el = $(id); el.textContent = v ? corta(v) : 'Elige una fecha'; el.classList.toggle('campo-fecha--vacio', !v); }
  function cal() {
    var v = st.vista, h = hoy(), t = iso(h);
    var mes = v.toLocaleDateString('es-MX', { month: 'long', year: 'numeric' });
    $('#cal-mes').textContent = mes.charAt(0).toUpperCase() + mes.slice(1);
    $('#cal-prev').disabled = v <= primero(h);
    var html = ['L', 'M', 'M', 'J', 'V', 'S', 'D'].map(function (x) { return '<span class="cal__sem" aria-hidden="true">' + x + '</span>'; }).join('');
    for (var i = 0; i < (v.getDay() + 6) % 7; i++) html += '<span></span>';
    var n = new Date(v.getFullYear(), v.getMonth() + 1, 0).getDate();
    for (var d = 1; d <= n; d++) {
      var f = new Date(v.getFullYear(), v.getMonth(), d), s = iso(f), ocu = st.ocupadas.has(s), sel = s === st.inicio || s === st.fin, cl = 'dia';
      if (s === t) cl += ' dia--hoy';
      if (ocu) cl += ' dia--ocupado';
      if (sel) cl += ' dia--sel'; else if (st.inicio && st.fin && s > st.inicio && s < st.fin) cl += ' dia--rango';
      html += '<button type="button" class="' + cl + '" data-fecha="' + s + '"' + ((ocu || f < h) ? ' disabled' : '') +
        ' aria-pressed="' + sel + '" aria-label="' + larga(s) + (ocu ? ', ocupado' : '') + '">' + d + '</button>';
    }
    $('#cal-grid').innerHTML = html;
    campo('#f-inicio', st.inicio); campo('#f-fin', st.fin);
  }
  async function abrir(cat, id) {
    var it = buscar(cat, id);
    st = { cat: cat, id: id, nombre: it.titulo || it.nombre, ocupadas: new Set(), inicio: null, fin: null, vista: primero(hoy()) };
    $('#m-item').textContent = st.nombre;
    msg('');
    try { (await UTR.api.obtenerFechasOcupadas(cat, id)).forEach(function (f) { st.ocupadas.add(f); }); }
    catch (e) { msg('No pudimos revisar las fechas ocupadas. Intenta de nuevo.', true); }
    cal();
    modal.showModal();
  }

  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-accion="solicitar"]');
    if (b) abrir(b.dataset.categoria, b.dataset.id);
  });
  $('#cal-grid').addEventListener('click', function (e) {
    var b = e.target.closest('[data-fecha]');
    if (!b) return;
    var s = b.dataset.fecha;
    msg('');
    if (!st.inicio || st.fin || s < st.inicio) { st.inicio = s; st.fin = null; }
    else if (hayOcupadas(st.inicio, s)) msg('Hay fechas ocupadas en ese rango. Elige otras fechas.', true);
    else st.fin = s;
    cal();
  });
  $('#cal-prev').addEventListener('click', function () { st.vista.setMonth(st.vista.getMonth() - 1); cal(); });
  $('#cal-next').addEventListener('click', function () { st.vista.setMonth(st.vista.getMonth() + 1); cal(); });
  $('#m-cancelar').addEventListener('click', function () { modal.close(); });
  $('#m-confirmar').addEventListener('click', async function () {
    if (!st.inicio || !st.fin) { msg('Elige la fecha de inicio y la de devolución.', true); return; }
    try {
      await UTR.api.enviarSolicitud({ categoria: st.cat, id: st.id, inicio: st.inicio, fin: st.fin });
      modal.close();
      aviso('ok', 'Solicitud enviada.', 'Apartaste «' + st.nombre + '» del ' + larga(st.inicio) + ' al ' + larga(st.fin) + '.');
    } catch (e) { msg('No pudimos enviar tu solicitud. Intenta de nuevo.', true); }
  });

  /* ---- Inicio ---- */
  (async function () {
    try {
      datos = await UTR.api.cargarCatalogo();
      Object.keys(NOMBRES).forEach(pintar);
    } catch (e) {
      aviso('error', '', 'No pudimos cargar el catálogo. Intenta de nuevo en unos minutos.');
      document.querySelectorAll('[data-lista]').forEach(function (l) { l.innerHTML = '<p class="vacio">No pudimos cargar esta sección.</p>'; });
    }
  })();
})();