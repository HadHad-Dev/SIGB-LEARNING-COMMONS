/* api.js · ÚNICO lugar donde se habla con la base de datos / servidor Python.
   Mientras USAR_MOCK sea true, responde con datos de ejemplo.
   Para conectar: pon USAR_MOCK = false y ajusta API_BASE y las rutas a las de tu backend. */
UTR.api = (function () {
  'use strict';
  var USAR_MOCK = true;
  var API_BASE = '';   // ej. 'http://localhost:8000'

  async function pedir(ruta, opciones) {
    var r = await fetch(API_BASE + ruta, opciones);
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }
  function enviar(ruta, cuerpo) {
    return pedir(ruta, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) });
  }

  /* ---------- Datos de ejemplo (se borran al conectar) ---------- */
  function mas(n) { var d = UTR.hoy(); d.setDate(d.getDate() + n); return UTR.iso(d); }
  var MOCK = {
    libros: [
      { id: 'L-001', titulo: 'Cien años de soledad', autor: 'Gabriel García Márquez', publicacion: '1967', imagen: null, ocupadas: [mas(3), mas(4), mas(5)] },
      { id: 'L-002', titulo: 'Don Quijote de la Mancha', autor: 'Miguel de Cervantes', publicacion: '1605', imagen: null, ocupadas: [] },
      { id: 'L-003', titulo: 'Clean Code', autor: 'Robert C. Martin', publicacion: '2008', imagen: null, ocupadas: [mas(1), mas(2)] }
    ],
    computadoras: [
      { id: 'C-004', nombre: 'PC Biblioteca 04', tipo: 'pc', ocupadas: [mas(2)] },
      { id: 'C-002', nombre: 'Laptop Préstamo 02', tipo: 'laptop', ocupadas: [mas(6), mas(7)] },
      { id: 'C-007', nombre: 'PC Biblioteca 07', tipo: 'pc', ocupadas: [] }
    ],
    equiposElectronicos: [
      { id: 'E-001', nombre: 'Proyector portátil', imagen: null, especificaciones: '3,600 lúmenes, entradas HDMI y VGA', ocupadas: [mas(4)] },
      { id: 'E-002', nombre: 'Tableta de 10 pulgadas', imagen: null, especificaciones: '64 GB, Wi-Fi, lápiz incluido', ocupadas: [] },
      { id: 'E-003', nombre: 'Calculadora gráfica', imagen: null, especificaciones: 'Pantalla gráfica, funciona con pilas AAA', ocupadas: [mas(1)] }
    ],
    objetosPerdidos: [
      { id: 'O-001', nombre: 'Termo metálico negro', descripcion: 'Termo de acero de 750 ml con tapa negra y un rayón en el costado.', lugar: 'Mesa 4 de lectura', encontradoPor: 'Mariana Torres', edificio: 'Learning Commons', imagen: null },
      { id: 'O-002', nombre: 'Calculadora científica', descripcion: 'Calculadora gris con tapa deslizable y las teclas un poco gastadas.', lugar: 'Cubículo 2', encontradoPor: 'Luis Hernández', edificio: 'Learning Commons', imagen: null },
      { id: 'O-003', nombre: 'Audífonos inalámbricos', descripcion: 'Estuche blanco con audífonos dentro, sin marca visible.', lugar: 'Sala de cómputo', encontradoPor: 'Ana Gómez', edificio: 'Learning Commons', imagen: null },
      { id: 'O-004', nombre: 'Libreta de cuadros azul', descripcion: 'Libreta con espiral y apuntes de cálculo en las primeras hojas.', lugar: 'Pasillo de estantes', encontradoPor: 'Jorge Ramírez', edificio: 'Learning Commons', imagen: null },
      { id: 'O-005', nombre: 'Llaves con llavero rojo', descripcion: 'Tres llaves en un aro con llavero de tela rojo.', lugar: 'Mesa 9 de lectura', encontradoPor: 'Carmen Ruiz', edificio: 'Learning Commons', imagen: null },
      { id: 'O-006', nombre: 'Sudadera gris', descripcion: 'Sudadera gris talla M con capucha y cierre a medias.', lugar: 'Aula 3', encontradoPor: 'Pedro Salazar', edificio: 'Edificio A', imagen: null },
      { id: 'O-007', nombre: 'Paraguas negro', descripcion: 'Paraguas plegable negro con mango de plástico.', lugar: 'Entrada principal', encontradoPor: 'Sofía Medina', edificio: 'Edificio A', imagen: null },
      { id: 'O-008', nombre: 'Cargador de laptop', descripcion: 'Cargador negro de 65 W con el cable enrollado.', lugar: 'Aula 5', encontradoPor: 'Diego Vargas', edificio: 'Edificio A', imagen: null },
      { id: 'O-009', nombre: 'Lonchera azul', descripcion: 'Lonchera térmica azul marino con cierre y una bolsa interna.', lugar: 'Mesa 6 de la cafetería', encontradoPor: 'Valeria Ortiz', edificio: 'Cafetería', imagen: null },
      { id: 'O-010', nombre: 'Estuche con lápices', descripcion: 'Estuche de tela verde con lápices, plumas y una goma.', lugar: 'Aula 1', encontradoPor: 'Héctor Flores', edificio: 'Edificio D', imagen: null },
      { id: 'O-011', nombre: 'Credencial de estudiante', descripcion: 'Credencial UTR con funda transparente.', lugar: 'Recepción', encontradoPor: 'Daniela Cruz', edificio: 'Vinculación', imagen: null },
      { id: 'O-012', nombre: 'Lentes con armazón negro', descripcion: 'Lentes de armazón negro con estuche rígido gris.', lugar: 'Laboratorio 2', encontradoPor: 'Raúl Mendoza', edificio: 'Edificio B', imagen: null },
      { id: 'O-013', nombre: 'Memoria USB de 32 GB', descripcion: 'Memoria USB plateada con cordón azul.', lugar: 'Laboratorio 4', encontradoPor: 'Elena Castillo', edificio: 'Edificio C', imagen: null },
      { id: 'O-014', nombre: 'Botella de plástico morada', descripcion: 'Botella morada de 1 litro con calcomanías de estrellas.', lugar: 'Gradas de la cancha', encontradoPor: 'Andrés Navarro', edificio: 'Canchas', imagen: null }
    ],
    eventosBiblioteca: [
      { id: 'EV-001', fecha: mas(-2), horaInicio: '09:00', horaFin: '10:30', nombre: 'Inducción a la biblioteca', lugar: 'Learning Commons', descripcion: 'Recorrido por las áreas y servicios para estudiantes de nuevo ingreso.' },
      { id: 'EV-002', fecha: mas(0), horaInicio: '13:00', horaFin: '14:00', nombre: 'Charla: hábitos de estudio', lugar: 'Sala de lectura', descripcion: 'Consejos prácticos para organizar tu tiempo antes de los exámenes.' },
      { id: 'EV-003', fecha: mas(1), horaInicio: '10:00', horaFin: '12:00', nombre: 'Taller de citación APA', lugar: 'Sala de lectura', descripcion: 'Aprende a citar y armar tus referencias paso a paso con ejemplos.' },
      { id: 'EV-004', fecha: mas(3), horaInicio: '12:00', horaFin: '13:00', nombre: 'Inducción a cubículos', lugar: 'Learning Commons', descripcion: 'Conoce cómo apartar un cubículo y las reglas para usarlo.' },
      { id: 'EV-005', fecha: mas(3), horaInicio: '16:00', horaFin: '17:30', nombre: 'Club de lectura', lugar: 'Sala de lectura', descripcion: 'Comentamos el libro del mes. Puedes llegar aunque no lo hayas terminado.' },
      { id: 'EV-006', fecha: mas(8), horaInicio: '11:00', horaFin: '12:30', nombre: 'Búsqueda en bases de datos', lugar: 'Sala de cómputo', descripcion: 'Practica cómo encontrar artículos y libros digitales para tus proyectos.' },
      { id: 'EV-007', fecha: mas(14), horaInicio: '09:00', horaFin: '15:00', nombre: 'Feria del libro', lugar: 'Auditorio', descripcion: 'Exposición y venta de libros con descuentos para la comunidad UTR.' },
      { id: 'EV-008', fecha: mas(17), horaInicio: '16:00', horaFin: '17:30', nombre: 'Club de lectura', lugar: 'Sala de lectura', descripcion: 'Nueva sesión del club con el libro elegido por el grupo.' },
      { id: 'EV-009', fecha: mas(24), horaInicio: '10:00', horaFin: '11:30', nombre: 'Taller de citación APA', lugar: 'Sala de lectura', descripcion: 'Segunda sesión del taller, con práctica sobre trabajos reales.' }
    ]
  };

  /* ---------- Sesión ---------- */
  // p = { perfil: 'estudiante'|'invitado'|'administrador', matricula?, correo?, nombre?, apellido?, clave? }
  async function iniciarSesion(p) {
    if (!USAR_MOCK) return enviar('/api/login', p);
    if (p.clave !== undefined && p.clave.length < 6) throw new Error('credenciales');   // demo
    return { ok: true };
  }
  // p = { nombre, matricula, carrera, correo, clave }
  async function registrar(p) {
    if (!USAR_MOCK) return enviar('/api/registro', p);
    if (p.matricula === '2201145') { var e = new Error('duplicada'); e.codigo = 'duplicada'; throw e; }   // demo
    return { ok: true };
  }

  /* ---------- Préstamos ---------- */
  // Devuelve { libros: [], computadoras: [], equiposElectronicos: [] }
  async function cargarCatalogo() {
    if (!USAR_MOCK) return pedir('/api/prestamos/catalogo');
    return MOCK;
  }
  // Devuelve un arreglo de fechas 'AAAA-MM-DD' ocupadas del recurso
  async function obtenerFechasOcupadas(cat, id) {
    if (!USAR_MOCK) return (await pedir('/api/prestamos/' + cat + '/' + id + '/ocupadas')).fechas;
    return MOCK[cat].filter(function (x) { return x.id === id; })[0].ocupadas || [];
  }
  // s = { categoria, id, inicio, fin }
  async function enviarSolicitud(s) {
    if (!USAR_MOCK) return enviar('/api/prestamos', s);
    return { ok: true };
  }

  /* ---------- Objetos perdidos ---------- */
  var EDIFICIOS = ['Edificio A', 'Edificio B', 'Edificio C', 'Edificio D', 'Learning Commons', 'Vinculación', 'Cafetería', 'Canchas'];
  function norm(t) { return String(t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); }
  // Devuelve un arreglo con los nombres de los edificios, en el orden en que se muestran
  async function obtenerEdificios() {
    if (!USAR_MOCK) return (await pedir('/api/objetos-perdidos/edificios')).edificios;
    return EDIFICIOS;
  }
  // f = { texto, edificio ('' = todos), pagina (desde 1), porPagina }
  // Devuelve { objetos: [...solo los de esa página], total: N de todos los que cumplen el filtro }
  async function consultarObjetosPerdidos(f) {
    if (!USAR_MOCK) return pedir('/api/objetos-perdidos?' + new URLSearchParams({ texto: f.texto, edificio: f.edificio, pagina: f.pagina, porPagina: f.porPagina }));
    var t = norm(f.texto);
    var res = MOCK.objetosPerdidos.filter(function (o) {
      return (!f.edificio || o.edificio === f.edificio) && (!t || norm(o.nombre + ' ' + o.descripcion + ' ' + o.lugar).indexOf(t) !== -1);
    });
    var ini = (f.pagina - 1) * f.porPagina;
    return { objetos: res.slice(ini, ini + f.porPagina), total: res.length };
  }

  /* ---------- Eventos de la biblioteca ---------- */
  // r = { desde, hasta } en 'AAAA-MM-DD' (incluye ambos días)
  // Devuelve un arreglo de { id, fecha, horaInicio, horaFin, nombre, lugar, descripcion }
  async function consultarEventos(r) {
    if (!USAR_MOCK) return (await pedir('/api/eventos?' + new URLSearchParams({ desde: r.desde, hasta: r.hasta }))).eventos;
    return MOCK.eventosBiblioteca.filter(function (e) { return e.fecha >= r.desde && e.fecha <= r.hasta; });
  }

  return { iniciarSesion: iniciarSesion, registrar: registrar, cargarCatalogo: cargarCatalogo, obtenerFechasOcupadas: obtenerFechasOcupadas, enviarSolicitud: enviarSolicitud,
    obtenerEdificios: obtenerEdificios, consultarEventos: consultarEventos, consultarObjetosPerdidos: consultarObjetosPerdidos };
})();