/* servicios.js · Calendario de eventos de la pantalla de servicios
   Los eventos vienen de UTR.api.consultarEventos (api.js). Se consulta un mes a la vez:
   cada vez que cambias de mes se vuelve a pedir al servidor solo ese rango de fechas. */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var esc = UTR.esc, iso = UTR.iso, deIso = UTR.deIso, corta = UTR.corta, larga = UTR.larga, hoy = UTR.hoy;
  var st = { vista: null, sel: null, auto: true, eventos: [], error: false }, token = 0;

  function primero(d) { return new Date(d.getFullYear(), d.getMonth(), 1); }
  function cap(t) { return t.charAt(0).toUpperCase() + t.slice(1); }
  function porDia() { var m = {}; st.eventos.forEach(function (e) { (m[e.fecha] = m[e.fecha] || []).push(e); }); return m; }
  function dato(e, v) { return '<div class="dato"><span class="etiqueta">' + e + '</span><span>' + v + '</span></div>'; }

  function pintarCal() {
    var v = st.vista, t = iso(hoy()), m = porDia();
    $('ev-mes').textContent = cap(v.toLocaleDateString('es-MX', { month: 'long', year: 'numeric' }));
    var html = ['L', 'M', 'M', 'J', 'V', 'S', 'D'].map(function (x) { return '<span class="cal__sem" aria-hidden="true">' + x + '</span>'; }).join('');
    for (var i = 0; i < (v.getDay() + 6) % 7; i++) html += '<span></span>';
    var n = new Date(v.getFullYear(), v.getMonth() + 1, 0).getDate();
    for (var d = 1; d <= n; d++) {
      var s = iso(new Date(v.getFullYear(), v.getMonth(), d)), c = (m[s] || []).length, cl = 'dia';
      if (s === t) cl += ' dia--hoy';
      if (s === st.sel) cl += ' dia--sel';
      if (c) cl += ' dia--evento';
      html += '<button type="button" class="' + cl + '" data-fecha="' + s + '" aria-pressed="' + (s === st.sel) + '" aria-label="' +
        larga(s) + (c ? ', ' + c + (c === 1 ? ' evento' : ' eventos') : '') + '">' + d + '</button>';
    }
    $('ev-grid').innerHTML = html;
  }

  function pintarDetalle(cargando) {
    var lista = $('ev-lista');
    $('ev-fecha').textContent = cap(deIso(st.sel).toLocaleDateString('es-MX', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }));
    if (cargando) { lista.innerHTML = '<p class="vacio">Cargando eventos…</p>'; return; }
    if (st.error) { lista.innerHTML = '<p class="vacio">No pudimos cargar esta sección.</p>'; return; }
    var del = (porDia()[st.sel] || []).slice().sort(function (a, b) { return a.horaInicio < b.horaInicio ? -1 : 1; });
    lista.innerHTML = del.length ? del.map(function (e) {
      return '<article class="evento" data-id="' + esc(e.id) + '"><h3>' + esc(e.nombre) + '</h3>' +
        '<p class="evento__hora">' + corta(e.fecha) + ' · ' + esc(e.horaInicio) + ' – ' + esc(e.horaFin) + '</p>' +
        dato('Lugar', esc(e.lugar)) + '<p class="item__desc">' + esc(e.descripcion) + '</p></article>';
    }).join('') : '<p class="vacio">No hay eventos este día. Los días con un punto rojo tienen actividades.</p>';
  }

  async function cargarMes() {
    var mi = ++token, v = st.vista, t = iso(hoy());
    var desde = iso(v), hasta = iso(new Date(v.getFullYear(), v.getMonth() + 1, 0));
    st.eventos = []; st.error = false;
    pintarCal(); pintarDetalle(true);
    try {
      // BASE DE DATOS · Consulta de eventos del mes (ver api.js)
      st.eventos = await UTR.api.consultarEventos({ desde: desde, hasta: hasta });
      if (mi !== token) return;
      $('aviso').hidden = true;
      // Si el día se eligió solo (cambio de mes) y no tiene eventos, salta al primer día con eventos
      if (st.auto && st.sel !== t && !porDia()[st.sel] && st.eventos.length) {
        st.sel = st.eventos.map(function (e) { return e.fecha; }).sort()[0];
      }
    } catch (e) {
      if (mi !== token) return;
      st.error = true;
      UTR.aviso('error', '', 'No pudimos cargar los eventos. Intenta de nuevo en unos minutos.');
    }
    pintarCal(); pintarDetalle(false);
  }

  function irA(vista) {
    var h = hoy();
    st.vista = vista; st.auto = true;
    st.sel = (vista.getFullYear() === h.getFullYear() && vista.getMonth() === h.getMonth()) ? iso(h) : iso(vista);
    cargarMes();
  }
  $('ev-prev').addEventListener('click', function () { irA(new Date(st.vista.getFullYear(), st.vista.getMonth() - 1, 1)); });
  $('ev-next').addEventListener('click', function () { irA(new Date(st.vista.getFullYear(), st.vista.getMonth() + 1, 1)); });
  $('ev-hoy').addEventListener('click', function () { irA(primero(hoy())); });
  $('ev-grid').addEventListener('click', function (e) {
    var b = e.target.closest('[data-fecha]');
    if (!b) return;
    st.sel = b.dataset.fecha; st.auto = false;
    pintarCal(); pintarDetalle(false);
  });

  irA(primero(hoy()));
})();