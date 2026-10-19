# Bloxd Shader Packs — Guía completa (Español)

🌐 [Todos los idiomas](README.md) · En profundidad: [English](GUIDE-EN.md#part-0--start-from-zero-how-rendering-and-bloxd-shaders-work) · [Français](GUIDE-FR.md)

**Lee esto primero.** No necesitas experiencia. En diez minutos sabrás cómo el juego dibuja su
imagen, qué es un shader y exactamente qué puede y qué no puede hacer un shader pack.

> **Alcance: API v2.** Esta guía describe `apiVersion: 2` y la ruta actual WebGPU/Lite. No cambies `apiVersion` por anticipado para una versión futura.

## 1. La versión de un minuto

- Bloxd.io es un juego voxel: el mundo está hecho de cubos (bloques).
- La imagen en tu pantalla la dibuja tu tarjeta gráfica (GPU), 60 o más veces por segundo.
- Un **shader** es un programa diminuto que corre en la GPU y decide el color de los píxeles.
- Un **shader pack** es un pequeño archivo `.zip` con código shader. El juego lo carga y deja que
  tu código recoloree **bloques, agua y lava** mientras se dibujan.
- No cambias el juego. Solo cambias colores y luz, en el momento exacto en que cada píxel se dibuja.

## 2. Cómo se dibuja la imagen (renderizado web, paso a paso)

Tu pantalla es una cuadrícula de puntos diminutos llamados **píxeles** (por ejemplo 1920 × 1080 =
unos dos millones de píxeles). Una imagen completa es un **frame**. El juego dibuja un frame nuevo
una y otra vez: eso hace que el movimiento se vea suave.

Dos procesadores comparten el trabajo:

| | CPU (procesador principal) | GPU (tarjeta gráfica) |
|---|---|---|
| Trabajo | lógica del juego, física, red | dibujar millones de píxeles, muy rápido, en paralelo |
| Estilo | pocos trabajadores, muy inteligentes | miles de trabajadores, cada uno muy simple |

En la web, la cadena es así:

1. El juego corre como JavaScript en tu navegador (Chrome o Edge reciente es lo mejor).
2. El juego habla con la GPU mediante **WebGPU**, la API gráfica moderna del navegador.
3. Dentro del navegador, **Dawn** (con su compilador **Tint**) traduce el lenguaje de shaders
   **WGSL** a instrucciones que tu GPU entiende (Direct3D / Metal / Vulkan, según tu sistema).
4. La GPU ejecuta los shaders y pone el frame terminado en pantalla.

Bloxd está construido con un motor voxel (**noa-engine**) sobre un framework 3D (**Babylon.js**).
Para cada frame, la tubería de dibujo hace esto:

1. **Chunks.** El mundo se corta en columnas de bloques llamadas chunks. Solo se preparan para
   dibujar los chunks cercanos a ti.
2. **Meshing.** Para cada chunk, el motor construye una *malla* (mesh): una piel de triángulos que
   cubre solo las caras de bloque realmente visibles. Las caras ocultas se saltan.
3. **Atlas de texturas.** Cada cara de bloque toma su imagen de una sola imagen grande, el **atlas**,
   que contiene todas las texturas de bloques una junto a otra. Cada cara sabe qué cuadradito del
   atlas usar (sus coordenadas **UV**).
4. **Paso de vértices.** La GPU ejecuta un *vertex shader* en cada esquina (vértice) de cada
   triángulo: coloca la esquina en el lugar correcto de tu pantalla y pasa datos (coordenadas de
   textura, valores de luz, dirección de la cara…).
5. **Rasterización.** La GPU rellena cada triángulo con píxeles. Cada píxel cubierto se convierte en
   un **fragmento**: un píxel candidato con datos interpolados.
6. **Paso de fragmentos.** La GPU ejecuta un *fragment shader* por cada fragmento: aquí se decide el
   color final del píxel. **Aquí viven los shader packs de Bloxd.**
7. **Pantalla.** Se muestra el frame terminado. Luego todo se repite para el siguiente frame.

```mermaid
flowchart LR
    A[Mundo de bloques] --> B[Chunks]
    B --> C[Mallas: solo caras visibles]
    C --> D[Paso de vértices: colocar esquinas]
    D --> E[Rasterizar: rellenar píxeles]
    E --> F[Paso de fragmentos: TU PACK recolorea]
    F --> G[Pantalla]
```

Idea clave: tu pack nunca ve «el mundo». Ve **un fragmento a la vez** — un píxel de una cara de
bloque — más algunos datos sobre ese píxel. Todo lo que hace un pack debe calcularse desde esos
datos locales.

## 3. Qué es un shader

Un shader es una función pequeña (un trozo de código) que la GPU ejecuta un número enorme de veces
en paralelo — una vez por vértice, o una vez por fragmento. Debe ser rápido y autosuficiente: sin
archivos, sin red, sin memoria del frame anterior.

Los packs de Bloxd se escriben en **WGSL** (WebGPU Shading Language). No escribes un shader completo. El motor ya tiene sus shaders; te deja insertar código en seis puntos fijos llamados **hooks** (Sección 5): dos programas (terreno y líquido) × tres etapas (vertex, surface, light). En una puerta vertex pregunta dónde va una esquina; en surface y light pregunta cómo debe verse al final este píxel.

## 4. Qué es un shader pack de Bloxd

Un pack es un archivo `.zip` con:

```
pack.json     (pequeño archivo de metadatos)
*.wgsl        (tu código WGSL — un archivo o muchos, en cualquier carpeta)
```

`pack.json` solo necesita:

```json
{ "apiVersion": 2, "name": "Mi Pack", "author": "tú" }
```

- `apiVersion` debe ser exactamente el número JSON **2** (no una cadena). Los packs v1 antiguos se rechazan.
- El importador acepta una carpeta o **un** `.zip`. Tras normalizar rutas debe quedar exactamente un `pack.json`; si todos los archivos comparten una carpeta raíz, se elimina sola.
- El manifiesto es un objeto JSON UTF-8 de ≤ **65 536 bytes**. `name` no puede quedar vacío tras recortar; `author` es opcional: cadena o `null`; las demás claves se ignoran.
- Fuentes: **1–256** archivos `.wgsl`, ordenados por ruta; total descomprimido ≤ **262 144 bytes**; rutas duplicadas y UTF-8 inválido se rechazan; otros archivos se ignoran.
- El zip puede tener ≤ **33 554 432 bytes** y ≤ **1 024 entradas**; solo se leen stored/deflate; Zip64, multidisco y cifrado se rechazan.

Instala así: Bloxd → `O` Ajustes → Gráficos → activar **Use New WebGPU Renderer** → Shader Pack → elegir carpeta o `.zip` → **Apply** → **recargar la página**. Sin WebGPU usable, el pack puede guardarse pero queda bloqueado.

Un pack solo afecta a **bloques, agua y lava**. Algunos modos de juego desactivan los packs por
completo.

## 5. Los seis hooks (tus únicas puertas)

| Hook | Cuándo corre | Qué controlas |
|---|---|---|
| `bloxdTerrainVertex` | por vértice, terreno, antes de proyectar | posición mundial de cada esquina (solo juegos allow) |
| `bloxdTerrainSurface` | por fragmento, bloques sólidos, primero | color base, transparencia (alfa), brillo propio (emission) |
| `bloxdTerrainLight` | el mismo fragmento, justo después | color final iluminado de los bloques |
| `bloxdLiquidVertex` | por vértice, líquidos, antes de proyectar | posición mundial de cada esquina líquida (solo juegos allow) |
| `bloxdLiquidSurface` | por fragmento, agua y lava, primero | color base y alfa de los líquidos |
| `bloxdLiquidLight` | el mismo fragmento, justo después | color final iluminado de los líquidos |

Reglas de las puertas:

- Surface corre **antes** que light, en el mismo fragmento. Puedes pasar un valor de surface a light
  con una variable a nivel de módulo (`var<private>`).
- Empieza siempre desde el resultado por defecto del motor: `bloxdDefaultSurface(...)` o
  `bloxdDefaultLight(...)`, cambia lo que necesites y devuélvelo. Nunca construyas tú mismo las
  estructuras de resultado.
- Los hooks de surface corren antes de la prueba de recorte por transparencia del motor: en hojas y
  bloques recortados, `out.alpha` decide si el píxel se queda o se descarta; en líquidos es el factor
  real de mezcla; en bloques sólidos normales el alfa no hace nada.
- El brillo propio (`out.emission`) pertenece solo a los hooks de **surface**.
- Si escribes tu propio color final en un hook de light, aplica la niebla tú mismo al final con
  `bloxdApplyFog(colour, light)`: la niebla del motor siempre está en la escena, y saltarla hace que
  los bloques lejanos brillen a través de la niebla.

- Si falta una etapa líquida, cae al hook de terreno equivalente; si falta la pareja surface/light, la etapa usa el defecto del motor. Vertex es opcional; empieza con `bloxdDefaultVertex(...)`.
- Un hook vertex o un `discard` alcanzable no rechaza el pack: apaga ese programa en strict, y strict es la política por defecto.
- `out.alpha` existe solo bajo `BLOXD_ALPHA` (ausente solo en terreno+strict); los líquidos siempre tienen alpha. El RGB que devuelve light reemplaza el RGB final: usa `bloxdApplyFog` para mantener la niebla.

## 6. Qué te dice el motor

Para cada fragmento, tus hooks reciben datos. Los campos más útiles:

| Dato | Significado, en palabras simples |
|---|---|
| `colour` | el color de textura del bloque en este píxel (desde el atlas), antes de tus cambios |
| `blockId` | el **id numérico** del bloque (un número entero). Así tratas un tipo de bloque distinto de otro — tabla completa en la Parte VIII |
| `position` | dónde está este píxel en el mundo (x, y, z) |
| `normal` | hacia dónde apunta la cara (arriba, abajo, norte…), como vector |
| `skyLight` | cuánta luz del cielo llega a este bloque, de 0 a 1 — pero **con tone mapping**: cielo abierto ≈ 1.0, un nivel perdido bajo un árbol ≈ 0.995 (ver Sección 7) |
| `blockLight` | luz de lámparas, antorchas, lava… como color (existen lámparas de colores) |
| `heldLight` | luz del objeto en la mano del jugador |
| `skyLightColour` | el tinte actual del cielo (azul oscuro de noche, cálido al atardecer) |
| `litColour` | el color iluminado propio del motor para esta superficie (útil como base) |
| `fogVisibility`, `fogColour` | qué tan nublado está este píxel y el color de la niebla (llega **negro** cuando la niebla está apagada — maneja ese caso) |

Funciones del motor que puedes llamar:

| Función | Qué te da |
|---|---|
| `bloxdDefaultSurface(in)` / `bloxdDefaultLight(surface, light)` | el resultado normal del motor — siempre tu punto de partida |
| `bloxdDefaultVertex(in)` | resultado vertex sin cambios — punto de partida de los hooks vertex |
| `bloxdApplyFog(colour, light)` | mezcla tu color en la niebla correctamente |
| `bloxdSunDirection()` | vector unitario hacia el sol; `(0,0,0)` en mundos sin sol tipo Tierra; la luna es exactamente la dirección opuesta |
| `bloxdTime()` | segundos — **vuelve a 0 cada 3600 segundos** (`bloxdTimeWrap`). Ver Sección 7 |
| `bloxdEyePosition()` | la posición de la cámara (para efectos de distancia) |
| `bloxdOriginOffset()` | el motor recentra periódicamente las coordenadas del mundo; suma este offset a cualquier patrón basado en posición del mundo, o tu patrón saltará visiblemente |
| `bloxdFaceBlock(position, normal)` | la celda de bloque (coordenadas enteras) de la cara que dibujas — perfecta para variación aleatoria por bloque |
| `bloxdOpaqueBehind()` | solo surface/light de líquido bajo `BLOXD_SCENE_DEPTH`: `{found, position, distance}` tras este píxel exacto; grosor = `distance` menos ojo→superficie |

## 7. Las trampas en las que caen todos

**El tiempo se reinicia.** `bloxdTime()` cuenta segundos pero vuelve a empezar en 3600. Si tu
animación usa el tiempo crudo, saltará una vez por hora. Anima siempre con ciclos enteros dentro del
reinicio (wrap):

```wgsl
sin(6.2831853 * fract(bloxdTime() / bloxdTimeWrap * cycles + phase))
```

Elige `cycles` como número entero. Entonces el valor en el segundo 3600 iguala al del segundo 0: sin
saltos, nunca.

**skyLight tiene tone mapping.** No es un brillo lineal 0–1. El motor comprime los niveles de luz
0–15 en una curva: el cielo abierto es ≈ 1.0 y perder un nivel aún se lee ≈ 0.995. Si pruebas
`skyLight < 0.5` esperando «en sombra», casi nada coincidirá. Calibra los umbrales sobre la curva
real (la Parte IV da valores medidos).

**La niebla siempre está.** Aunque no la veas, el motor calcula niebla (a veces empujada muy lejos).
Si tu hook de light devuelve un color sin `bloxdApplyFog`, el terreno lejano se verá demasiado
brillante y atravesará la niebla. Aplica la niebla al final, después de tu trabajo de color.

**Unlit no quita los campos.** La cabecera da valores neutros: `skyLight=1`, `blockLight=0`, `heldLight=0`, `directional=0` y colores de luz blancos. Protege la lógica de cielo con `#ifdef BLOXD_LIGHTING` si en unlit debe apagarse.

## 8. Todo lo que un pack SÍ puede hacer

- Recolorear cualquier bloque, agua o lava — globalmente o por `blockId`.
- Hacer brillar cosas (`out.emission` en hooks de surface): lava, minerales, lámparas…
- Animar color y alfa con el tiempo (pulsos, lava que fluye, agua que brilla) — a prueba de
  reinicio (Sección 7).
- Reaccionar al ciclo día/noche mediante `bloxdSunDirection()` y `skyLightColour` (atardeceres
  cálidos, tintes azules de luna).
- Añadir detalle procedural anclado al mundo: variación sutil por bloque con hashes
  `bloxdFaceBlock`, tintes de niebla por distancia, oscurecimiento bajo el agua con la profundidad
  de `bloxdOpaqueBehind()`.
- Etalonar toda la imagen por fragmento: contraste, saturación, balance cálido/frío — siempre que
  la niebla se aplique al final.
- Pintar efectos *sobre* superficies: destellos en minerales, oscurecimiento «mojado» cerca del
  nivel del agua, nieve en caras hacia arriba (`normal.y`) y trucos similares — todo calculado desde
  los datos del propio fragmento.
- Usar la distancia (`bloxdEyePosition()`) para desvanecer efectos caros o ruidosos (nivel de
  detalle barato).

## 9. Lo que un pack NO puede hacer (límites del motor)

- **Plantas, hierba y flores** las dibuja una parte del motor que los packs no pueden alcanzar. No
  puedes recolorearlas ni animarlas.
- **Sin post-proceso.** No tienes acceso al frame terminado, ni coordenadas de pantalla, ni pases de
  desenfoque/bloom/viñeta.
- **Sin profundidad de escena.** La única consulta «qué hay detrás» es `bloxdOpaqueBehind()` a través
  de un líquido.
- **Sin mapas de sombras reales ni oclusión ambiental** más allá de lo que los valores de luz del
  motor ya codifican.
- **Sin objetos ni partículas nuevas** en el mundo. Solo puedes pintar sobre superficies que ya
  existen. (Los packs ingeniosos pintan efectos superpuestos sobre superficies — ver las recetas —
  pero la geometría siempre es del motor.)
- **Sin texturas ni samplers** propios, sin fuentes de datos extra: tus únicos datos son los
  argumentos de los hooks y las funciones del motor.
- **El movimiento de vértices depende de la política.** Los hooks vertex son reales, pero solo corren en juegos allow; strict es el defecto y apaga ese programa. Nunca hagas depender el look central o la legibilidad de esquinas movidas.
- **El cielo mismo** (disco solar, skybox, nubes) lo dibuja el motor. Los packs reciben *datos* del
  cielo (dirección, tinte) pero no dibujan el cielo.

Si un efecto necesita algo de esta lista, hoy ningún pack puede hacerlo: es comportamiento probado
del motor, no un problema de habilidad.

## 10. Tu primer pack en cinco pasos

1. Crea `pack.json`:

```json
{ "apiVersion": 2, "name": "Mi Primer Pack", "author": "tú" }
```

2. Crea `shader.wgsl` junto a él:

```wgsl
fn bloxdTerrainSurface(surface: BloxdSurfaceIn) -> BloxdSurface {
    var out = bloxdDefaultSurface(surface);
    out.colour = out.colour * vec3f(1.05, 1.0, 0.92);
    return out;
}

fn bloxdTerrainLight(surface: BloxdSurface, light: BloxdLightIn) -> BloxdLight {
    var out = bloxdDefaultLight(surface, light);
    _ = surface;
    return out;
}
```

Este pack hace cada bloque un poco más cálido (más rojo, menos azul) y mantiene la iluminación del
motor. La línea `_ = surface;` le dice al compilador «esta entrada no se usa a propósito»: WGSL
exige esta forma simple.

3. Mantén los archivos en una carpeta para importar carpeta, o zipealos. Lo más claro: `pack.json` junto al WGSL en el nivel superior; una única carpeta envolvente compartida también vale y se elimina.

4. En el juego: Ajustes → Gráficos → **Use New WebGPU Renderer** activado → Shader Pack → elegir carpeta o `.zip` → Apply → **recargar la página**.

5. Mira a tu alrededor: el mundo debería verse un poco más cálido. Cambia los tres números y recarga
   para experimentar.

Luego crece paso a paso: un efecto cada vez, compruébalo al mediodía, al atardecer, de noche, bajo
el agua y en una cueva antes de añadir el siguiente.

## 11. Las nueve reglas duras

Romper cualquiera rompe el pack o hace que lo rechacen:

1. Nunca definas `BLOXD_*` ni ningún nombre `bloxd*` salvo los seis hooks. Directivas solo `#define/#ifdef/#ifndef/#else/#endif` al inicio de línea; `#define` es una bandera global sin valor y no puede vivir en un condicional.

2. Nunca construyas `BloxdVertex` / `BloxdSurface` / `BloxdLight`: parte de `bloxdDefaultVertex` / `bloxdDefaultSurface` / `bloxdDefaultLight`.

3. `mod` es palabra reservada en WGSL: usa `%`.
4. Sin atributos `@…`, entry points, texturas, samplers, `override/enable/requires/diagnostic`, clases de almacenamiento extra, doble guion bajo ni UV de pantalla.

5. Un hook vertex o `discard` alcanzable apaga ese programa en strict (por defecto), no rechaza el pack. Para seguridad strict, evítalos o protege el efecto.

6. `out.alpha` existe solo bajo `BLOXD_ALPHA` (ausente solo terreno+strict). El alpha líquido existe en cada variante; el de terreno necesita guarda.

7. Entradas sin uso: escribe `_ = valor;` — la forma `let _ =` se rechaza.
8. Límites exactos: manifiesto ≤65 536 bytes; 1–256 WGSL; WGSL total ≤262 144 bytes; zip ≤33 554 432 bytes y ≤1 024 entradas.

9. El motor compila **8 variantes**: allow/strict × lit/unlit × terreno/líquido. Defines: `BLOXD_STRICT`, `BLOXD_LIGHTING`, `BLOXD_SCENE_DEPTH` solo líquido, `BLOXD_ALPHA` ausente solo terreno+strict. Debe compilar y comportarse en todas; parentiza bits/shift para Tint.

## 12. Mini glosario

| Palabra | Significado |
|---|---|
| Frame | una imagen completa en pantalla |
| Pixel / fragment | un punto de la imagen / un píxel candidato que se está coloreando |
| Vertex | una esquina de un triángulo |
| Mesh (malla) | la piel de triángulos construida desde las caras visibles de un chunk |
| Atlas (atlas de texturas) | la única imagen grande con todas las texturas de bloques |
| UV | coordenadas que dicen qué parte del atlas usa una cara |
| WGSL | el lenguaje de shaders de WebGPU — el idioma de los packs de Bloxd |
| Hook | una de las seis funciones del motor que puede definir un pack (vertex/surface/light × terreno/líquido) |
| skyLight / blockLight | luz del cielo / luz de bloques (lámparas, lava) |
| Wrap (3600 s) | `bloxdTime()` reiniciándose a 0 cada hora |
| Fog (niebla) | el terreno lejano fundiéndose en el color de la niebla |
| Variante | una de las 8 formas en que el motor compila tu pack |

## 13. Referencia exacta de la API v2

Esta sección es la referencia exacta actual; si un resumen corto suena más simple, mandan estas reglas. Describe solo la API v2; una futura versión necesitará una verificación nueva.

- **Importación:** exactamente un manifiesto tras normalizar; `apiVersion` número 2; manifiesto ≤65 536 bytes; 1–256 `.wgsl` por ruta, total ≤262 144 bytes; zip ≤33 554 432 bytes/1 024 entradas, solo stored/deflate.
- **Variantes/defines:** allow/strict × lit/unlit × terreno/líquido. `BLOXD_SCENE_DEPTH` solo líquido; `BLOXD_ALPHA` ausente solo terreno+strict.
- **Strict/unlit:** strict es el defecto; vertex/discard apagan strict en vez de rechazar; unlit da `skyLight=1`, block/held/directional a cero y blanco.
- **Guardas:** alpha de terreno bajo `BLOXD_ALPHA`; profundidad solo en surface/light líquido bajo `BLOXD_SCENE_DEPTH`; alcanzar `bloxdOpaqueBehind()` desde vertex es error.
- **Profundidad líquida:** snapshot antes de transparentes de terreno, píxel exacto, sin color detrás y sin ver el propio líquido ni transparentes posteriores; grosor óptico = `behind.distance − distance(eye, surface.position)`.
- **Ejecución:** requiere Lite WebGPU; fallback WebGL = sin pack; cambios tras recargar; `bloxdTime()=performance.now()/1000 mod 3600`; curva skyLight `1−(1−x/(3−2x))³`, `x=level/15`.

## 14. Profundizar (capítulos en inglés)

| Parte | Archivo | Contenido |
|---|---|---|
| I | [01-making](GUIDE-EN.md#part-i--making-a-pack) | formato del pack, carga multi-archivo, límites, distribución |
| II | [02-api](GUIDE-EN.md#part-ii--the-api-contract) | el contrato completo de hooks y structs |
| III | [03-recipes](GUIDE-EN.md#part-iii--recipes) | 12 recetas de producción con código WGSL |
| IV | [04-realism](GUIDE-EN.md#part-iv--measured-numbers-realism-that-survives-contact-with-the-game) | números medidos: luz, niebla, óptica del agua |
| V | [05-troubleshooting](GUIDE-EN.md#part-v--troubleshooting) | cada fallo conocido y su arreglo |
| VI | [06-implementation](GUIDE-EN.md#part-vi--implementation--local-validation) | validación local en las 8 variantes |
| VII | [07-internals](GUIDE-EN.md#part-vii--engine-internals) | internos del motor (tiempo, luz, cielo, cargador) |
| VIII | [08-block-ids](GUIDE-EN.md#part-viii--the-numeric-block-id-table) | la tabla numérica completa de ids de bloques |
| IX | [09-sources](GUIDE-EN.md#part-ix--where-this-knowledge-comes-from-and-what-we-dont-know) | cómo se estableció cada hecho de esta guía |
| X | [10-constants](GUIDE-EN.md#part-x--the-constants-register-en) | cada constante (551) con su rol |

Versión completa en francés: [fr](GUIDE-FR.md) · Todos los idiomas: [índice](README.md). Licencia: MIT.
