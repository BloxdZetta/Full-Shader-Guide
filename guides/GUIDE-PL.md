# Bloxd Shader Packs — Kompletny przewodnik (Polski)

🌐 [Wszystkie języki](../README.md) · Pogłębienie: [English](GUIDE-EN.md#part-0--start-from-zero-how-rendering-and-bloxd-shaders-work) · [Français](GUIDE-FR.md)

**Przeczytaj to najpierw.** Doświadczenie nie jest potrzebne. Za dziesięć minut będziesz wiedzieć,
jak gra rysuje obraz, czym jest shader i dokładnie, co shader pack może, a czego nie może.

## 1. Wersja jednominutowa

- Bloxd.io to gra wokselowa: świat składa się z sześcianów (bloków).
- Obraz na ekranie rysuje karta graficzna (GPU), 60 lub więcej razy na sekundę.
- **Shader** to malutki program, który działa na GPU i decyduje o kolorze pikseli.
- **Shader pack** to mały plik `.zip` z kodem shadera. Gra go ładuje i pozwala twojemu kodowi
  przemalować **bloki, wodę i lawę** w trakcie ich rysowania.
- Nie zmieniasz gry. Zmieniasz tylko kolory i światło, dokładnie w momencie rysowania każdego piksela.

## 2. Jak rysowany jest obraz (rendering webowy krok po kroku)

Ekran to siatka maleńkich punktów zwanych **pikselami** (na przykład 1920 × 1080 = około dwa miliony
pikseli). Jeden pełny obraz to **klatka** (frame). Gra rysuje nową klatkę w kółko — dzięki temu ruch
wygląda płynnie.

Pracę dzielą dwa procesory:

| | CPU (procesor główny) | GPU (karta graficzna) |
|---|---|---|
| Zadanie | logika gry, fizyka, sieć | rysowanie milionów pikseli, bardzo szybko, równolegle |
| Styl | kilku pracowników, bardzo mądrych | tysiące pracowników, każdy bardzo prosty |

W internecie łańcuch wygląda tak:

1. Gra działa jako JavaScript w przeglądarce (najnowszy Chrome lub Edge działa najlepiej).
2. Gra rozmawia z GPU przez **WebGPU**, nowoczesne API graficzne przeglądarki.
3. W przeglądarce **Dawn** (z kompilatorem **Tint**) tłumaczy język shaderów **WGSL** na instrukcje
   zrozumiałe dla twojego GPU (Direct3D / Metal / Vulkan, zależnie od systemu).
4. GPU wykonuje shadery i pokazuje gotową klatkę na ekranie.

Sam Bloxd jest zbudowany na silniku wokselowym (**noa-engine**) na frameworku 3D (**Babylon.js**).
Dla każdej klatki potok rysowania robi to:

1. **Chunki.** Świat jest pocięty na kolumny bloków zwane chunkami. Do rysowania przygotowywane są
   tylko chunki blisko ciebie.
2. **Meshing.** Dla każdego chunka silnik buduje *siatkę* (mesh): skórę z trójkątów pokrywającą tylko
   naprawdę widoczne ściany bloków. Ukryte ściany są pomijane.
3. **Atlas tekstur.** Każda ściana bloku bierze obraz z jednego dużego obrazu — **atlasu** — który zawiera
   wszystkie tekstury bloków obok siebie. Każda ściana wie, którego małego kwadracika atlasu użyć
   (współrzędne **UV**).
4. **Krok wierzchołkowy.** GPU uruchamia *vertex shader* na każdym rogu (wierzchołku) każdego trójkąta:
   stawia róg we właściwym miejscu ekranu i przekazuje dane (współrzędne tekstury, wartości światła,
   kierunek ściany…).
5. **Rasteryzacja.** GPU wypełnia każdy trójkąt pikselami. Każdy pokryty piksel staje się **fragmentem**:
   pikselem-kandydatem z interpolowanymi danymi.
6. **Krok fragmentowy.** GPU uruchamia *fragment shader* dla każdego fragmentu: tutaj decyduje się
   finalny kolor piksela. **Tutaj żyją shader packi Bloxda.**
7. **Ekran.** Gotowa klatka jest pokazywana. Potem wszystko powtarza się dla następnej klatki.

```mermaid
flowchart LR
    A[Świat z bloków] --> B[Chunki]
    B --> C[Siatki: tylko widoczne ściany]
    C --> D[Krok wierzchołkowy: układanie rogów]
    D --> E[Rasteryzacja: wypełnianie pikseli]
    E --> F[Krok fragmentowy: TWÓJ PACK maluje]
    F --> G[Ekran]
```

Kluczowa myśl: twój pack nigdy nie widzi „świata". Widzi **jeden fragment naraz** — jeden piksel jednej
ściany bloku — plus trochę danych o tym pikselu. Wszystko, co robi pack, musi być policzone z tych
lokalnych danych.

## 3. Czym jest shader

Shader to mała funkcja (mały kawałek kodu), którą GPU wykonuje ogromną liczbę razy równolegle — raz na
wierzchołek albo raz na fragment. Musi być szybki i samodzielny: bez plików, bez sieci, bez pamięci
poprzedniej klatki.

Packi Bloxda pisze się w **WGSL** (WebGPU Shading Language). Nie piszesz całego shadera. Silnik ma już
swoje shadery; pozwala ci wstawić twój kod w czterech ustalonych punktach, zwanych **hookami** (Sekcja 5).
Wyobraź sobie cztery drzwi: silnik idzie przez swój kod rysowania i przy każdych drzwiach pyta twoją
funkcję: „oto dane tego piksela — chcesz zmienić kolor?"

## 4. Czym jest shader pack Bloxda

Pack to plik `.zip` z:

```
pack.json     (mały plik metadanych)
*.wgsl        (twój kod WGSL — jeden plik lub wiele, w dowolnych folderach)
```

`pack.json` potrzebuje tylko:

```json
{ "apiVersion": 2, "name": "Mój Pack", "author": "ty" }
```

- `apiVersion` musi być liczbą **2**. Stare packi v1 są odrzucane.
- Loader znajduje **każdy** plik `*.wgsl` w zipie i łączy je razem. Kolejność i foldery nie mają znaczenia.
- Całkowity limit WGSL: **256 KB**.

Instalacja: Bloxd → `O` Ustawienia → Grafika → włącz **Use New WebGPU Renderer** → Shader Pack →
**Choose .zip** → **Apply**.

Pack wpływa tylko na **bloki, wodę i lawę**. Niektóre tryby gry całkowicie wyłączają packi.

## 5. Cztery hooki (twoje jedyne drzwi)

| Hook | Kiedy działa | Co kontrolujesz |
|---|---|---|
| `bloxdTerrainSurface` | per fragment, bloki stałe, najpierw | kolor podstawowy, przezroczystość (alfa), własne świecenie (emission) |
| `bloxdTerrainLight` | ten sam fragment, zaraz potem | finalny oświetlony kolor bloków |
| `bloxdLiquidSurface` | per fragment, woda i lawa, najpierw | kolor podstawowy i alfa cieczy |
| `bloxdLiquidLight` | ten sam fragment, zaraz potem | finalny oświetlony kolor cieczy |

Zasady drzwi:

- Surface działa **przed** light, w tym samym fragmencie. Możesz przekazać wartość z surface do light
  zmienną na poziomie modułu (`var<private>`).
- Zawsze zaczynaj od domyślnego wyniku silnika: `bloxdDefaultSurface(...)` lub `bloxdDefaultLight(...)`,
  zmień, co trzeba, i zwróć. Nigdy nie buduj structów wynikowych sam.
- Hooki surface działają przed testem wycinania przezroczystości silnika: na liściach i wycinanych blokach
  `out.alpha` decyduje, czy piksel zostaje czy jest odrzucony; na cieczach to prawdziwy współczynnik
  mieszania; na zwykłych blokach stałych alfa nie robi nic.
- Własne świecenie (`out.emission`) należy tylko do hooków **surface**.
- Jeśli piszesz własny kolor końcowy w hooku light, nałóż mgłę sam na końcu przez
  `bloxdApplyFog(colour, light)` — mgła silnika jest zawsze w scenie, a jej pominięcie sprawia, że dalekie
  bloki świecą przez mgłę.

## 6. Co silnik ci mówi

Dla każdego fragmentu twoje hooki dostają dane. Najprzydatniejsze pola:

| Dane | Znaczenie, prostymi słowami |
|---|---|
| `colour` | kolor tekstury bloku w tym pikselu (z atlasu), przed twoimi zmianami |
| `blockId` | **numeryczne id** bloku (liczba całkowita). Tak traktujesz jeden typ bloku inaczej niż inny — pełna tabela w Części VIII |
| `position` | gdzie ten piksel jest w świecie (x, y, z) |
| `normal` | w którą stronę patrzy ściana (góra, dół, północ…), jako wektor |
| `skyLight` | ile światła nieba dociera do bloku, 0 do 1 — ale **po tone mappingu**: otwarte niebo ≈ 1.0, jeden zgubiony poziom pod drzewem ≈ 0.995 (zobacz Sekcję 7) |
| `blockLight` | światło lamp, pochodni, lawy… jako kolor (kolorowe lampy istnieją) |
| `heldLight` | światło przedmiotu w ręce gracza |
| `skyLightColour` | aktualny odcień nieba (ciemnoniebieski nocą, ciepły o zachodzie) |
| `litColour` | własny oświetlony kolor silnika dla tej powierzchni (przydatny jako baza) |
| `fogVisibility`, `fogColour` | jak zamglony jest piksel i kolor mgły (przychodzi **czarny**, gdy mgła jest wyłączona — obsłuż ten przypadek) |

Funkcje silnika, które możesz wywołać:

| Funkcja | Co ci daje |
|---|---|
| `bloxdDefaultSurface(in)` / `bloxdDefaultLight(surface, light)` | normalny wynik silnika — zawsze twój punkt startu |
| `bloxdApplyFog(colour, light)` | poprawnie wtapia twój kolor we mgłę |
| `bloxdSunDirection()` | wektor jednostkowy do słońca; `(0,0,0)` w światach bez słońca ziemskiego typu; księżyc to dokładnie przeciwny kierunek |
| `bloxdTime()` | sekundy — **wraca do 0 co 3600 sekund** (`bloxdTimeWrap`). Zobacz Sekcję 7 |
| `bloxdEyePosition()` | pozycja kamery (do efektów odległości) |
| `bloxdOriginOffset()` | silnik okresowo przebazowuje współrzędne świata; dodaj ten offset do każdego wzoru opartego na pozycji w świecie, bo wzór będzie widocznie skakał |
| `bloxdFaceBlock(position, normal)` | komórka bloku (współrzędne całkowite) rysowanej ściany — idealna do losowej wariacji per blok |
| `bloxdOpaqueBehind()` | tylko ciecze: znajduje pierwszy stały blok za powierzchnią cieczy — mierzy głębokość wody |

## 7. Pułapki, w które wpadają wszyscy

**Czas się zawija.** `bloxdTime()` liczy sekundy, ale zaczyna od nowa przy 3600. Jeśli animacja używa
surowego czasu, skoczy raz na godzinę. Zawsze animuj pełnymi cyklami wewnątrz wrapa:

```wgsl
sin(6.2831853 * fract(bloxdTime() / bloxdTimeWrap * cycles + phase))
```

Wybierz `cycles` jako liczbę całkowitą. Wtedy wartość w sekundzie 3600 równa się tej w sekundzie 0:
żadnych skoków, nigdy.

**skyLight ma tone mapping.** To nie jest liniowa jasność 0–1. Silnik ściska poziomy światła 0–15 w krzywą:
otwarte niebo to ≈ 1.0, a utrata jednego poziomu to wciąż ≈ 0.995. Jeśli testujesz `skyLight < 0.5` w
oczekiwaniu „w cieniu", prawie nic nie pasuje. Kalibruj progi na prawdziwej krzywej (Część IV podaje
zmierzone wartości).

**Mgła jest zawsze.** Nawet gdy jej nie widzisz, silnik liczy mgłę (czasem odepchniętą bardzo daleko).
Jeśli twój hook light zwróci kolor bez `bloxdApplyFog`, daleki teren będzie za jasny i przebije mgłę.
Mgłę nakładaj na końcu, po pracy z kolorem.

**Oświetlenie może być wyłączone.** Jeśli gra lub ustawienie wyłączy oświetlenie, `skyLight` może w ogóle
nie być wysyłany i efekty „od nieba" po cichu nic nie robią. Pisz efekty tak, by pack wyglądał dobrze i
bez nich.

## 8. Wszystko, co pack MOŻE

- Przemalować dowolny blok, wodę czy lawę — globalnie albo per `blockId`.
- Świecić rzeczami (`out.emission` w hookach surface): lawa, rudy, lampy…
- Animować kolor i alfę w czasie (pulsowanie, płynąca lawa, migocząca woda) — odporne na wrap (Sekcja 7).
- Reagować na cykl dnia i nocy przez `bloxdSunDirection()` i `skyLightColour` (ciepłe zachody, niebieskie
  odcienie księżyca).
- Dodawać proceduralne detale zakotwiczone w świecie: subtelna wariacja per blok hashami
  `bloxdFaceBlock`, odcienie mgły z odległością, przyciemnienie pod wodą z głębokością
  `bloxdOpaqueBehind()`.
- Kolorować (gradować) cały obraz per fragment: kontrast, nasycenie, balans ciepły/zimny — pod warunkiem
  nałożenia mgły na końcu.
- Malować efekty *na* powierzchniach: błyski na rudach, „mokre" przyciemnienie przy poziomie wody, śnieg
  na ścianach do góry (`normal.y`) i podobne triki — wszystko liczone z danych samego fragmentu.
- Używać odległości (`bloxdEyePosition()`), by wygaszać drogie albo zaszumione efekty (tani poziom detali).

## 9. Czego pack NIE MOŻE (granice silnika)

- **Rośliny, trawa i kwiaty** są rysowane przez część silnika niedostępną dla packów. Nie możesz ich
  przemalować ani animować.
- **Brak post-processingu.** Brak dostępu do gotowej klatki, brak współrzędnych ekranu, brak przejść
  blur/bloom/winieta.
- **Brak głębi sceny.** Jedyne zapytanie „co jest za tym" to `bloxdOpaqueBehind()` przez ciecz.
- **Brak prawdziwych map cieni ani ambient occlusion** ponad to, co wartości światła silnika już kodują.
- **Brak nowych obiektów ani cząsteczek** w świecie. Możesz malować tylko na powierzchniach, które już
  istnieją. (Sprytne packi malują efekty nakładane na powierzchnie — zobacz przepisy — ale geometria zawsze
  należy do silnika.)
- **Brak własnych tekstur i samplerów**, brak dodatkowych źródeł danych: twoje jedyne wejścia to argumenty
  hooków i funkcje silnika.
- **Ruch wierzchołków** (giniecie geometrii, fale poruszające rogami) istnieje w silniku, ale **działa tylko
  w paru grach** — nigdy na nim nie polegaj; udawaj ruch animacją koloru/alfy.
- **Samo niebo** (tarcza słońca, skybox, chmury) rysuje silnik. Packi dostają *dane* nieba (kierunek,
  odcień), ale nie rysują nieba.

Jeśli efekt potrzebuje czegoś z tej listy, dziś żaden pack tego nie zrobi — to udowodnione zachowanie
silnika, nie kwestia umiejętności.

## 10. Twój pierwszy pack w pięciu krokach

1. Utwórz `pack.json`:

```json
{ "apiVersion": 2, "name": "Mój Pierwszy Pack", "author": "ty" }
```

2. Utwórz obok `shader.wgsl`:

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

Ten pack robi każdy blok trochę cieplejszym (więcej czerwieni, mniej niebieskiego) i zachowuje oświetlenie
silnika. Linia `_ = surface;` mówi kompilatorowi „to wejście jest celowo nieużywane" — WGSL wymaga tej
prostej formy.

3. Spakuj oba pliki do zipa, z `pack.json` w korzeniu zipa (nie w podfolderze).
4. W grze: Ustawienia → Grafika → **Use New WebGPU Renderer** włączony → Shader Pack → Choose .zip → Apply.
5. Rozejrzyj się: świat powinien być trochę cieplejszy. Zmień trzy liczby i przeładuj, by eksperymentować.

Potem rośnij krok po kroku: jeden efekt naraz, sprawdź go w południe, o zachodzie, nocą, pod wodą i w
jaskini, zanim dodasz następny.

## 11. Dziewięciu twardych zasad

Złamanie którejkolwiek psuje pack albo kończy się odrzuceniem:

1. Nigdy nie definiuj niczego o nazwie zaczynającej się od `BLOXD_` — należą do silnika.
2. Nigdy nie buduj `BloxdSurface` / `BloxdLight` sam — zaczynaj od `bloxdDefaultSurface` /
   `bloxdDefaultLight`.
3. `mod` to słowo zastrzeżone w WGSL — używaj `%`.
4. Bez tekstur, bez samplerów, bez własnych entry pointów i atrybutów, bez UV ekranu.
5. Unikaj `discard` (odrzucany w trybie strict) — używaj `out.alpha`.
6. Hooki cieczy zawsze muszą wypisywać poprawną alfę, w każdej wariancie.
7. Nieużywane wejścia: pisz `_ = wartość;` — forma `let _ =` jest odrzucana.
8. Całkowity WGSL ≤ 256 KB.
9. Silnik kompiluje twój kod w **8 wariantach** (strict/permissive × lit/unlit × teren/ciecz). Twój kod musi
   się kompilować i zachowywać we wszystkich. Bierz w nawiasy mieszane wyrażenia bitowe/przesunięć dla
   kompilatora Tint przeglądarki.

## 12. Mini słowniczek

| Słowo | Znaczenie |
|---|---|
| Klatka (frame) | jeden kompletny obraz na ekranie |
| Piksel / fragment | jeden punkt obrazu / piksel-kandydat w trakcie kolorowania |
| Wierzchołek | róg trójkąta |
| Siatka (mesh) | skóra trójkątów zbudowana z widocznych ścian chunka |
| Atlas (atlas tekstur) | jeden duży obraz ze wszystkimi teksturami bloków |
| UV | współrzędne mówiące, którą część atlasu używa ściana |
| WGSL | język shaderów WebGPU — język packów Bloxda |
| Hook | jedna z czterech funkcji silnika, które pack może zdefiniować |
| skyLight / blockLight | światło z nieba / światło z bloków (lampy, lawa) |
| Wrap (3600 s) | `bloxdTime()` wraca do 0 co godzinę |
| Mgła (fog) | daleki teren wtapia się w kolor mgły |
| Wariant | jeden z 8 sposobów, w jaki silnik kompiluje twój pack |

## 13. Głębiej (rozdziały po angielsku)

| Część | Plik | Zawartość |
|---|---|---|
| I | [01-making](GUIDE-EN.md#part-i--making-a-pack) | format packa, ładowanie wieloplikowe, limity, dystrybucja |
| II | [02-api](GUIDE-EN.md#part-ii--the-api-contract) | pełny kontrakt hooków i structów |
| III | [03-recipes](GUIDE-EN.md#part-iii--recipes) | 12 przepisów produkcyjnych z kodem WGSL |
| IV | [04-realism](GUIDE-EN.md#part-iv--measured-numbers-realism-that-survives-contact-with-the-game) | zmierzone liczby: światło, mgła, optyka wody |
| V | [05-troubleshooting](GUIDE-EN.md#part-v--troubleshooting) | każdy znany błąd i jego naprawa |
| VI | [06-implementation](GUIDE-EN.md#part-vi--implementation--local-validation) | lokalna walidacja w 8 wariantach |
| VII | [07-internals](GUIDE-EN.md#part-vii--engine-internals) | wnętrze silnika (czas, światło, niebo, loader) |
| VIII | [08-block-ids](GUIDE-EN.md#part-viii--the-numeric-block-id-table) | pełna numeryczna tabela id bloków |
| IX | [09-sources](GUIDE-EN.md#part-ix--where-this-knowledge-comes-from-and-what-we-dont-know) | jak ustalono każdy fakt tego przewodnika |
| X | [10-constants](GUIDE-EN.md#part-x--the-constants-register-en) | każda stała (551) z jej rolą |

Pełna wersja francuska: [fr](GUIDE-FR.md) · Wszystkie języki: [index](../README.md). Licencja: MIT.
