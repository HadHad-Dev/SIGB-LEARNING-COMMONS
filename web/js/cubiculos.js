/* cubiculos.js · Pantalla de cubículos
   Los datos vienen de UTR.api (api.js): cargarCubiculos y reservarCubiculo.
   Reglas: reservas entre 7:30 am y 4:30 pm, máximo 1 hora, sin empalmar horas apartadas.
   Estas reglas se validan aquí para avisarte rápido; el servidor debe volver a validarlas.
   Para probar el estado "actual" a otra hora, abre la página con ?hora=10:15 */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var esc = UTR.esc;
  var INI = 450, FIN = 990, PASO = 30, MAX = 60;   // minutos desde las 00:00 (7:30 a 16:30)
  var MSG_LIMITE = 'Solo puedes apartar el cubículo por máximo 1 hora entre las 7:30 am y las 4:30 pm.';
  var fecha = UTR.iso(UTR.hoy()), cubiculos = [], modal = $('modal');

  function aMin(h) { var p = h.split(':'); return +p[0] * 60 + +p[1]; }
  function hm(m) { return UTR.pad(Math.floor(m / 60)) + ':' + UTR.pad(m % 60); }
  function mono(m) { return '<span class="mono">' + hm(m) + '</span>'; }
  function ahora() {
    var q = new URLSearchParams(window.location.search).get('hora');
    if (q && /^\d{1,2}:\d{2}$/.test(q)) return aMin(q);
    var d = new Date(); return d.getHours() * 60 + d.getMinutes();
  }
  function busca(id) { return cubiculos.filter(function (c) { return c.id === id; })[0]; }
  function bloqueEn(c, min) { return c.bloques.filter(function (b) { return aMin(b.inicio) <= min && min < aMin(b.fin); })[0]; }
  function choca(c, ini, fin) { return c.bloques.some(function (b) { return aMin(b.inicio) < fin && ini < aMin(b.fin); }); }
  function palabra(t) { return t === 'ocupado' ? 'Ocupado' : 'Reservado'; }

  /* Estado actual del cubículo según la hora de ahora */
  function estado(c) {
    var a = ahora();
    if (a < INI || a >= FIN) return { clase: 'cerrado', html: 'Fuera de horario' };
    var b = bloqueEn(c, a);
    if (!b) return { clase: 'libre', html: 'Libre' };
    return { clase: b.tipo, html: palabra(b.tipo) + ' de ' + mono(aMin(b.inicio)) + ' a ' + mono(aMin(b.fin)) };
  }

  function tarjeta(c) {
    var e = estado(c), seg = '', m;
    for (m = INI; m < FIN; m += PASO) { var b = bloqueEn(c, m); seg += '<span class="franja' + (b ? ' franja--' + b.tipo : '') + '"></span>'; }
    var lista = c.bloques.slice().sort(function (x, y) { return aMin(x.inicio) - aMin(y.inicio); }).map(function (b) {
      return '<li class="estado estado--' + b.tipo + '">' + palabra(b.tipo) + ' ' + mono(aMin(b.inicio)) + ' – ' + mono(aMin(b.fin)) + '</li>';
    }).join('');
    return '<article class="cubiculo' + (e.clase === 'ocupado' ? ' cubiculo--ocupado' : '') + '" data-id="' + esc(c.id) + '">' +
      '<h2>' + esc(c.nombre) + '</h2><span class="estado estado--' + e.clase + '">' + e.html + '</span>' +
      '<div><div class="franjas" aria-hidden="true">' + seg + '</div><div class="franjas__horas" aria-hidden="true"><span>7:30</span><span>12:00</span><span>16:30</span></div></div>' +
      '<div class="dato"><span class="etiqueta">Horas apartadas hoy</span>' + (lista ? '<ul class="bloques">' + lista + '</ul>' : '<span>Sin horas apartadas.</span>') + '</div>' +
      '<button class="btn btn--secundario" type="button" data-accion="reservar" data-id="' + esc(c.id) + '">Reservar</button></article>';
  }
  function pintar() { $('lista').innerHTML = cubiculos.map(tarjeta).join(''); }

  async function cargar() {
    try {
      // BASE DE DATOS · Consulta de cubículos, horas ocupadas y reservadas de la fecha (ver api.js)
      cubiculos = await UTR.api.cargarCubiculos(fecha);
      $('aviso').hidden = true;
      pintar();
    } catch (e) {
      UTR.aviso('error', '', 'No pudimos cargar los cubículos. Intenta de nuevo en unos minutos.');
      $('lista').innerHTML = '<p class="vacio">No pudimos cargar esta sección.</p>';
    }
  }

  /* ---- Reserva ---- */
  function msg(t, error) { var m = $('r-msg'); m.textContent = t || ''; m.classList.toggle('help--error', !!error); }
  function validar(c, ini, dur) {
    if (dur <= 0 || dur > MAX || ini < INI || ini + dur > FIN) return MSG_LIMITE;
    if (choca(c, ini, ini + dur)) return 'Ese horario ya está ocupado o reservado. Elige otra hora.';
    return null;
  }
  function resumen() {
    var v = $('r-inicio').value;
    $('r-resumen').innerHTML = v ? 'Tu reserva: ' + mono(+v) + ' a ' + mono(+v + +$('r-dur').value) : '';
  }
  function pintarInicios() {
    var c = busca($('r-cub').value), previo = $('r-inicio').value, h = '', libre = null;
    for (var m = INI; m < FIN; m += PASO) {
      var b = bloqueEn(c, m);
      if (!b && libre === null) libre = m;
      h += '<option value="' + m + '"' + (b ? ' disabled' : '') + '>' + hm(m) + (b ? ' · ' + b.tipo : '') + '</option>';
    }
    $('r-inicio').innerHTML = h;
    var ok = previo && !bloqueEn(c, +previo) ? previo : libre;
    if (ok !== null) $('r-inicio').value = ok;
    msg(libre === null ? 'Este cubículo no tiene horas libres hoy. Prueba con otro.' : '', libre === null);
    resumen();
  }
  function abrir(id) {
    $('r-cub').innerHTML = cubiculos.map(function (c) { return '<option value="' + esc(c.id) + '">' + esc(c.nombre) + '</option>'; }).join('');
    $('r-cub').value = id;
    $('r-dur').value = '60';
    $('m-info').innerHTML = 'Hoy, ' + UTR.corta(fecha) + ' · de ' + mono(INI) + ' a ' + mono(FIN) + ' · máximo 1 hora';
    $('r-inicio').innerHTML = '';
    pintarInicios();
    modal.showModal();
  }

  $('lista').addEventListener('click', function (e) {
    var b = e.target.closest('[data-accion="reservar"]');
    if (b) abrir(b.dataset.id);
  });
  $('r-cub').addEventListener('change', pintarInicios);
  $('r-inicio').addEventListener('change', function () { msg(''); resumen(); });
  $('r-dur').addEventListener('change', function () { msg(''); resumen(); });
  $('r-cancelar').addEventListener('click', function () { modal.close(); });
  $('r-confirmar').addEventListener('click', async function () {
    var c = busca($('r-cub').value), v = $('r-inicio').value, dur = +$('r-dur').value;
    if (!v) { msg('Elige una hora de inicio.', true); return; }
    var ini = +v, er = validar(c, ini, dur);
    if (er) { msg(er, true); return; }
    try {
      // BASE DE DATOS · Guardar la reserva (el servidor vuelve a validar horario y empalmes) (ver api.js)
      await UTR.api.reservarCubiculo({ cubiculoId: c.id, fecha: fecha, inicio: hm(ini), fin: hm(ini + dur) });
      modal.close();
      await cargar();
      UTR.aviso('ok', 'Reserva confirmada.', 'Apartaste el ' + c.nombre + ' de ' + hm(ini) + ' a ' + hm(ini + dur) + '.');
    } catch (x) {
      if (x.codigo === 'ocupado') { msg('Ese horario ya se ocupó. Elige otra hora.', true); await cargar(); pintarInicios(); }
      else msg('No pudimos guardar tu reserva. Intenta de nuevo.', true);
    }
  });

  $('hoy').textContent = UTR.corta(fecha);
  cargar();
  setInterval(function () { if (cubiculos.length) pintar(); }, 60000);   // mantiene el estado actual al día
})();