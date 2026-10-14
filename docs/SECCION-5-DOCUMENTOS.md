# Sección 5 · Documentos: cómo se procesa la información de una obra

Diseño para revisar **antes** de programar. Cubre planos, planillas, presupuestos, cronogramas, reportes de
obra, fotos, permisos y trámites, normativas y contratos: todo lo necesario para ejecutar una obra o un proyecto.

---

## 1. Qué tipos de información maneja y qué datos guarda de cada uno

Todos los documentos comparten una ficha común: obra (o **Biblioteca general** si es del estudio), tipo, título,
descripción, etiquetas, área responsable, nivel de acceso, quién lo subió y cuándo.
Además, cada tipo pide datos propios. Así se puede buscar "el A-101 vigente" o "los permisos que vencen este mes".

| Tipo | Formatos aceptados | Datos propios | Vista previa en el sistema |
|---|---|---|---|
| **Planos** | PDF + archivo editable opcional (DWG, DXF, RVT, IFC, SKP) | N° de plano (A-101), especialidad (Arquitectura, Estructura, Sanitaria, Eléctrica, Gas, Detalles), escala, estado del plano | PDF en pantalla. El editable solo se descarga |
| **Planillas** | XLSX, XLS, CSV | — | Tabla con las primeras 50 filas de cada hoja |
| **Presupuestos** | XLSX, PDF | Monto total y moneda (opcional), proveedor | Tabla (Excel) o PDF |
| **Cronogramas** | XLSX, CSV, MPP, PDF | Fecha de inicio y fin que cubre | Tabla o PDF. El MPP solo se descarga |
| **Reportes de obra** | PDF | Fecha del reporte, número | PDF |
| **Fotos de obra** | JPG, PNG, WEBP, HEIC | Fecha de toma (se lee sola de la foto), lugar o rubro | Galería con miniaturas |
| **Permisos y trámites** | PDF, imágenes | Organismo (municipio, colegio, servicios), N° de expediente, fecha de otorgamiento, **vencimiento** | PDF |
| **Normativas** | PDF | Jurisdicción, año | PDF |
| **Contratos** | PDF, DOCX | Partes, fecha de firma | PDF |
| **Otros** | Cualquiera menos ejecutables | — | Según formato |

**Estado del plano:** En elaboración → Para revisión → **Aprobado para obra** → Reemplazado.
El que va a obra es siempre el último "Aprobado para obra". Al subir una revisión nueva, la anterior pasa sola a "Reemplazado".

**Vencimiento de permisos:** el sistema avisa al responsable de la obra 30 y 7 días antes de que venza un permiso
(cuando esté la sección 6, Notificaciones).

---

## 2. Qué pasa cuando alguien sube un archivo (paso a paso)

1. **Validar.** El formato tiene que estar en la lista de ese tipo (ver tabla). Máximo 300 MB por archivo.
   Nunca se aceptan ejecutables (.exe, .bat, .js, .html, etc.).
2. **Huella digital.** Se calcula el SHA-256 del archivo. Sirve para:
   - avisar si ese mismo archivo ya está subido en la obra (evita duplicados);
   - demostrar después que el archivo no cambió (integridad).
3. **Guardar.** El archivo se guarda en el disco con un nombre interno aleatorio, en
   `media/obras/<código de obra>/<tipo>/`. El nombre original queda en la base. Los archivos **nunca** quedan
   accesibles por un link directo: solo se bajan a través del sistema, que controla el permiso.
4. **Leer datos del archivo, automáticamente:**
   - **Planos:** si el nombre sigue la convención del estudio (`A-101_Planta baja_RevC.pdf`), propone el N° de plano,
     el título y la revisión. La persona confirma o corrige.
   - **Fotos:** fecha de toma (EXIF) y una miniatura. Las fotos HEIC del iPhone se convierten a JPG para poder
     verlas, y se guarda también el original.
   - **Planillas:** cantidad de hojas y de filas.
5. **Asentar** en el registro de actividad: quién, qué archivo, qué versión, huella, tamaño, IP.
6. **Avisar** (sección 6): al equipo de la obra; al cliente solo si el documento está compartido con él.

**Carga múltiple:** se pueden arrastrar varios archivos juntos. Cada uno queda como un documento aparte, con los
datos comunes (obra, tipo, área) cargados una sola vez.

---

## 3. Versiones: nada se pisa

- Cada documento tiene una historia de versiones: **Rev A, Rev B, Rev C…** Subir una versión nueva **no borra**
  la anterior; queda en el historial con su comentario ("se corrigió la cocina").
- El equipo ve todas las versiones. El cliente ve **solo la vigente**.
- En los planos, cada versión puede llevar el PDF y el editable (DWG/RVT) juntos. El editable nunca se comparte con el cliente.

---

## 4. Quién ve y quién hace qué

### Niveles de acceso de cada documento

| Nivel | Quién lo ve | Para qué |
|---|---|---|
| **Equipo de la obra** (por defecto) | Las personas asignadas a esa obra y Gerencia | Planos, planillas, fotos, reportes |
| **Restringido** | Gerencia y el área responsable del documento | Contratos, presupuestos con márgenes, datos sensibles |
| **Compartido con el cliente** | Lo anterior + el cliente de la obra | Planos aprobados, presupuesto acordado, fotos, permisos |

La **Biblioteca general** (normativas, plantillas, documentos del estudio sin obra) la ve todo el personal.

> El nivel "Restringido" existe porque la **confidencialidad** de ciertos datos (costos, márgenes, contratos) es una condición para que el equipo use el sistema.

### Acciones

| Acción | Quién puede |
|---|---|
| Ver y descargar | Según el nivel de acceso |
| Subir documentos a una obra | Cualquier persona del equipo de esa obra |
| Subir versión nueva, editar datos, archivar | Quien lo subió, el área responsable y los responsables de la obra |
| **Compartir con el cliente** (o dejar de compartir) | Responsables de la obra y Gerencia |
| Marcar un plano como "Aprobado para obra" | Dirección Técnica y Gerencia |
| Mandar a la papelera y restaurar | Quien puede editarlo |
| Borrar definitivamente | Solo Gerencia |

---

## 5. Archivar, papelera y borrado

- **Archivar:** el documento deja de aparecer en las listas pero se conserva entero (ej. documentación de una etapa cerrada).
- **Papelera:** se puede restaurar en cualquier momento. No se vacía sola.
- **Borrado definitivo** (solo Gerencia): borra el archivo del disco, pero el registro de actividad conserva qué era,
  quién lo subió, su huella y quién lo borró.

---

## 6. Qué queda asentado (registro de actividad)

Subida · versión nueva · edición de datos (con antes → después) · cambio de nivel de acceso · compartir o dejar de
compartir con el cliente · cambio de estado del plano · archivar · papelera · restauración · borrado definitivo ·
**cada descarga y cada vista**, también las del cliente (quién, qué versión, cuándo, IP).

Con esto se puede responder, por ejemplo, "¿el cliente vio la Rev C del A-101 antes de aprobar?".

---

## 7. Cómo se organiza en pantalla

- **Pestaña Archivos de cada obra:** carpetas por tipo (Planos, Planillas, Fotos…), con contador.
  Los planos se listan como un **índice de planos** (N°, título, especialidad, revisión vigente, estado).
- **Administrador de archivos** (menú Archivos): todos los documentos que la persona puede ver, con filtros por obra,
  tipo, área, nivel de acceso, "subidos por mí" y archivados, y búsqueda por título, N° de plano y etiquetas.
- **Ficha del documento:** vista previa, datos, versiones y actividad del documento.
- **Papelera.**

---

## 8. Lo que queda para más adelante

- **Buscar dentro del contenido** de PDF y planillas: fase 3, junto con la consulta con IA.
- **Reportes del bot de obra:** por ahora se suben a mano como "Reportes de obra". Cuando el bot esté en
  producción, puede dejarlos solo en la obra que corresponda.
- **Copias de seguridad:** los archivos quedan en el disco de esta PC (`media/`). Antes de usarlo con datos reales
  hay que definir una copia automática (disco externo o nube).

## 9. Cambios técnicos que implica

- Nueva dependencia: **Pillow** (miniaturas y fecha de las fotos) y **pillow-heif** (fotos de iPhone).
- El permiso "puede ver documento" pasa a tener en cuenta el nivel de acceso (hoy solo mira la obra).
