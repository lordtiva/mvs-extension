#set page(
  paper: "us-letter",
  margin: (x: 1.05in, y: 1.0in),
  numbering: "1",
)
#set text(
  font: "New Computer Modern",
  size: 10.5pt,
  lang: "es",
)
#set par(
  justify: true,
  leading: 0.62em,
  first-line-indent: 1.4em,
)
#show table: set par(justify: false)
#show table: set text(hyphenate: false)
#set heading(numbering: "1.1")
#show heading: it => {
  set text(weight: "bold")
  if it.level == 1 {
    v(1.15em, weak: true)
    block(text(size: 12.5pt, it))
    v(0.55em, weak: true)
  } else if it.level == 2 {
    v(0.9em, weak: true)
    block(text(size: 11pt, it))
    v(0.45em, weak: true)
  }
}

#let thm_box(title, body) = {
  v(0.65em, weak: true)
  block(width: 100%, breakable: true)[
    #set par(first-line-indent: 0pt)
    *#title.* #emph(body)
  ]
  v(0.65em, weak: true)
}

#let proof_block(title: "Demostración", body) = {
  v(0.45em, weak: true)
  block(width: 100%, breakable: true)[
    #set par(first-line-indent: 0pt)
    #emph(title + ".") #body #h(1fr) $square.stroked$
  ]
  v(0.65em, weak: true)
}

#align(center)[
  #v(0.15in)
  #text(size: 16.5pt, weight: "bold")[Barreras de Bellman Afines Dependientes del Estado, Equivalencia Asintótica y la Curva en U Institucional]
  #v(0.75em)
  #text(size: 11.5pt)[Extensiones Analíticas, Certificados Reforzados y Microfundaciones sobre _Minimum Viable Scale_ (Milei y Reidel, 2026)]
  #v(1.1em)
  #text(size: 12pt, weight: "semibold")[Marcelo Segura#footnote[Documento Técnico de Trabajo (preprint). El desarrollo analítico, la edición técnica y las rutinas de verificación simbólica y numérica en Python contaron con asistencia de herramientas de inteligencia artificial bajo la dirección, supervisión crítica y plena responsabilidad del autor.]]
  #v(0.45em)
  #text(size: 10pt)[Noviembre 2026]
  #v(1.1em)
]

#pad(x: 2.0em)[
  #align(center)[*Resumen (Abstract)*]
  #v(0.3em)
  #set text(size: 9.5pt)
  #set par(first-line-indent: 0pt)
  Este trabajo desarrolla cuatro contribuciones analíticas y extensiones estructurales sobre el modelo de supervivencia óptima con rendimientos crecientes a escala, complementariedad bruta y trabajo endógeno de Milei y Reidel (2026, _Minimum Viable Scale: Bellman Barriers and the Economics of Survival_). *Primero*, en el certificado de Barreras de Bellman de Primer Paso (FPBB) de la Sección 7.2, identificamos un término de holgura omitido en la construcción en bloques de dos períodos: al comparar cualquier transición individual $(x, y) in M times M$ con el par $(h, b)$ a igual esfuerzo laboral, la ganancia de consumo retiene simultáneamente el diferencial de capital inicial $q(h - x)$ y el diferencial de ahorro $(y - b)$. Mediante una barrera afín dependiente del estado $B_1 (x)$ de un solo paso, reducimos el techo de la barrera en casi cinco unidades ($-43.0465$ frente a $-38.1442$), *casi triplicamos el margen de calibración de permanencia* (de $2.564$ a $7.4665$ uniforme y $7.7756$ en $b = 0.10$) y *reducimos a la mitad el plazo máximo certificado de entrada* a $H = lr([0.28, infinity))$ (de $46$ a *$23$ períodos*, $24$ uniforme). Extendemos además el certificado a la banda previa $M_0 = lr([0.05, 0.10))$ con cota explícita $tau_(.1) <= 10$ períodos, y certificamos analíticamente mediante descomposición de Wronskiano y aritmética de intervalos que la Tabla 5 de salidas adversas ($12$ subintervalos finitos) colapsa a dos evaluaciones en frontera sin mínimos interiores, elevando el margen de salida en $M$ de $0.0436$ a $> 0.0947$ y el margen global FPBB de $0.0423$ ($0.04$) a *$> 0.0571$* ($+35\%$). *Segundo*, resolvemos la pregunta abierta de la Nota al pie 1 estableciendo el isomorfismo finito $S_A^("fix") (overline(L)) = overline(L) S_(A overline(L)^r)^("fix") (1)$, formulando una condición variacional precisa para $S_A^("fix") (1) < S_A$, y demostrando bajo la condición de paciencia que cuando $A -> infinity$ tanto la frontera con trabajo endógeno como con trabajo fijo convergen a $s_infinity^* = (delta\/c_K)^(1\/r)$ ($S_A \/ S_A^("fix") (overline(L)) -> 1$), respaldado numéricamente por iteración de función de valor (VFI). *Tercero*, microfundamos la Sección 4.3 mediante gasto público productivo tipo Barro (1990) y carga regulatoria improductiva $(tau_p, tau_u)$, separando la curva en U exacta de la cota certificada $overline(S)(tau)$ y del piso físico $kappa(tau)$, la simetría por pares de $S(tau)$ a $A_0$ finito y el perfil límite asintótico cuando $A_0 -> infinity$. *Cuarto*, formalizamos la descentralización empresarial manteniendo la contabilidad factorial exacta $(theta\/mu) Y_t$, el crecimiento sin techo en unidades de eficiencia y los certificados estocásticos de Bellman bajo un proceso Markoviano explícito mediante parada opcional de Doob.
  #v(0.65em)
  *Palabras clave.* escala mínima viable; barreras de Bellman de primer paso (FPBB); cotas de tiempo de entrada; oferta laboral endógena; curva en U institucional. \
  *Códigos JEL.* C61, D24, D61, H21, O41.
]

#v(0.7em)

= Introducción

En _Minimum Viable Scale: Bellman Barriers and the Economics of Survival_, Milei y Reidel (2026) establecen una teoría unificada de la supervivencia económica cuando la tecnología agregada exhibe rendimientos crecientes a escala ($1 < theta < 2$), complementariedad bruta entre capital y trabajo ($rho = -d < 0$) y oferta laboral endógena con utilidad logarítmica sobre el consumo y el ocio ($L in [0, 1]$). Su resultado central muestra que, bajo una condición de paciencia ($beta[q + theta delta] > 1$) y productividad suficientemente elevada ($A > A_*$), existe una única Escala Mínima Viable $S_p$ estrictamente superior al umbral de reposición física $kappa_p$ (*Teorema 1*). En la banda intermedia $(kappa_p, S_p)$, aunque es físicamente factible sostener el stock de capital indefinidamente con consumo y ocio positivos, todo sendero óptimo decide liquidar gradualmente el capital hacia la extinción porque el retorno neto futuro no compensa el sacrificio de consumo y ocio presentes. En la frontera $S_p$, las trayectorias óptimas de extinción y supervivencia coexisten alcanzando el mismo bienestar total pero generando un quiebre hacia arriba (*upward kink*) en la función de valor (*Teorema 2*). Adicionalmente, dado que las sendas de liquidación diferida aproximan arbitrariamente bien el bienestar inicial óptimo (*Proposición 3*), los autores introducen el método de *Barreras de Bellman de Primer Paso* (*First Passage Bellman Barriers*, FPBB) para certificar analíticamente el ingreso en tiempo finito a una región productiva objetivo $H$ sin resolver la función de valor exacta $V_p (K)$.

Pese al rigor del marco de Milei y Reidel (2026), un análisis detenido de su construcción computacionalmente verificada en la Sección 7 y el Apéndice F, así como de las preguntas abiertas señaladas en el cuerpo del artículo, revela cuatro brechas analíticas susceptibles de cierre preciso sin alterar los axiomas del modelo ni ampliar su caja paramétrica:

1. *Afilamiento simultáneo de la barrera de permanencia y certificación global de las salidas adversas (Sección 3):* En el Teorema 9 de Milei y Reidel (2026), sobre la caja paramétrica (7.3) para la región de tránsito $M = lr([0.10, 0.28))$ y la región objetivo $H = lr([0.28, infinity))$, una barrera constante es imposible porque en el extremo superior $h = 0.28$ la recompensa de liquidar hacia $b = 0.10$ supera el bienestar alcanzable desde $b$. Los autores sortean esta obstrucción construyendo una barrera de bloques de $N = 2$ períodos que arroja $B(K) <= -38.144176$, un margen de permanencia $> 2.564$, un plazo máximo de entrada de $tau_H <= 46$ períodos y un margen global del certificado de $0.04$ (cuyo mínimo en su Tabla 5 es $0.0423$). Demostramos en el *Lema 1* y el *Teorema 9\** que el agrupamiento en pares de la ecuación (7.6) descarta aproximadamente la mitad de la disipación disponible en cada transición individual $(x, y) in M times M$: una barrera afín de *un solo paso* $B_1 (x)$ retiene ambos términos simultáneamente, mejora la cota superior de la barrera a $-43.046512$, eleva el margen de permanencia a *$> 7.4665$* ($> 7.7755$ en $b = 0.10$) y reduce exactamente a la mitad el plazo máximo de entrada a *$tau_H <= 23$ períodos* ($24$ uniforme). Asimismo, cerramos la brecha sin cota de la Figura 6 en la banda previa $M_0 = lr([0.05, 0.10))$ certificando *$tau_(.1) <= 10$ períodos* (*Proposición 1\**) y demostramos mediante un certificado de aritmética de intervalos sobre el Wronskiano y la segunda derivada (*Proposición 1\*\**) la ausencia de mínimos interiores en $M$ y $H_1$, reduciendo la Tabla 5 original a dos evaluaciones en frontera que elevan el margen de salida en $M$ a $> 0.0947$ y el margen global FPBB a *$> 0.0571$* ($+35\%$).
2. *Resolución asintótica e isomorfismo finito entre trabajo endógeno y fijo (Sección 4):* En la Nota al pie 1 (página 2), Milei y Reidel (2026) dejan como pregunta abierta la comparación entre la frontera $S_A$ con trabajo endógeno y la frontera $S_A^("fix") (overline(L))$ con trabajo exógenamente fijo. En el *Teorema 3\** probamos el isomorfismo exacto para todo $A$ finito, $S_A^("fix") (overline(L)) = overline(L) S_(A overline(L)^r)^("fix") (1)$, formulamos la condición variacional exacta bajo la cual $S_A^("fix") (1) < S_A$, y demostramos que bajo la condición de paciencia (2.3) (la cual fuerza $beta theta > 1$) tanto $A^(1\/r) S_A$ como $A^(1\/r) S_A^("fix") (overline(L))$ convergen al límite físico común $(delta\/c_K)^(1\/r)$, cerrando el cociente $S_A \/ S_A^("fix") (overline(L)) -> 1$ cuando $A -> infinity$, junto con una verificación numérica directa de fronteras por VFI.
3. *Microfundación institucional y curva en U fiscal–regulatoria (Sección 5):* En la Sección 4.3, los autores modelan distorsiones mediante una pérdida multiplicativa exógena $A_e = (1 - tau) A$, advirtiendo expresamente que su aplicación a impuestos o regulaciones exige contabilizar los beneficios productivos de los ingresos recaudados. Acoplando la tecnología CES con provisión pública equilibrada de infraestructura y derechos de propiedad tipo Barro (1990) junto con carga burocrática improductiva ($tau = tau_p + tau_u$), derivamos el *Teorema 10*: caracterizamos las dos trampas físicas de extinción ($tau < tau_(min)$ y $tau > tau_(max)$), establecemos la curva en U diferenciable exacta tanto para el piso físico $kappa(tau)$ como para la cota superior certificada $overline(S)(tau)$ con mínimo único en $tau^* = alpha\/(1+alpha)$, probamos la simetría de conjuntos de nivel de $S(tau)$ para todo $A_0$ finito y su perfil límite exacto cuando $A_0 -> infinity$, además de la monotonicidad estricta frente a burocracia improductiva $tau_u$.
4. *Descentralización empresarial, crecimiento sostenido y barreras estocásticas (Sección 6):* Finalmente, extendemos el núcleo determinista de planificador central con techo estacionario $K_p^+$ en tres direcciones: (i) descentralización bajo competencia monopolística (Dixit y Stiglitz, 1977) con contabilidad factorial exacta $(theta\/mu) Y_t$ y externalidades (Romer, 1986), probando que fragmentar empresas en $M$ unidades equivale a destruir productividad según $A\/M^(theta-1)$ (*Proposición 2\**); (ii) crecimiento balanceado aumentador de trabajo a tasa $g > 0$, que elimina el techo $K_p^+$ y genera despegue exponencial perpetuo («palo de hockey») preservando cada certificado en unidades de eficiencia (*Proposición 3\**); y (iii) extensión probabilística de las FPBB bajo condiciones explícitas de integrabilidad y transiciones Markovianas de régimen mediante el Teorema de Parada Opcional de Doob (*Teorema 11*), cuantificando cómo reducir $tau_H$ de $46$ a $23$ eleva al cuadrado la cota de supervivencia $(1 - p)^(tau_H)$ ante shocks severos.

El resto del artículo se organiza como sigue. La Sección 2 sitúa nuestras contribuciones en la literatura económica y de control óptimo verificado. La Sección 3 desarrolla las barreras afines de un paso, la cota de cruce previo y la reducción de la Tabla 5. La Sección 4 resuelve la Nota al pie 1 y presenta la verificación numérica asintótica. La Sección 5 deriva la curva en U institucional y descompone gasto productivo frente a peso muerto regulatorio. La Sección 6 formaliza la descentralización, el crecimiento sin techo y las barreras estocásticas. La Sección 7 concluye.

= Literatura Relacionada y Posicionamiento Teórico

Nuestros resultados se articulan en la intersección de cuatro líneas de investigación económica y matemática, cerrando en cada una limitaciones específicas respecto de las pruebas cuantitativas de supervivencia y las implicancias institucionales del modelo de Milei y Reidel (2026).

== Crecimiento óptimo no cóncavo, umbrales de Skiba y trampas de pobreza

Desde las contribuciones pioneras de Skiba (1978), Majumdar y Mitra (1982) y Dechert y Nishimura (1983), la teoría del crecimiento óptimo ha documentado que las tecnologías no convexas o con rendimientos crecientes locales dividen el espacio de estados mediante un umbral crítico de indiferencia donde coexisten trayectorias óptimas convergentes hacia la extinción o hacia un régimen próspero. Posteriormente, Mitra y Ray (1984) generalizaron las condiciones de existencia y monotonicidad a conjuntos factibles no convexos, mientras que Kamihigashi y Roy (2007) y Akao, Kamihigashi y Nishimura (2011) establecieron caracterizaciones globales en tiempo discreto sin diferenciabilidad ni concavidad, extendidas recientemente al tiempo continuo por Akao, Ishii, Kamihigashi y Nishimura (2022). En paralelo, la literatura de desarrollo económico formalizó trampas de pobreza basadas en externalidades de umbral en capital humano (Azariadis y Drazen, 1990) e imperfecciones crediticias con inversiones indivisibles (Galor y Zeira, 1993), mientras que Wagener (2020) caracterizó geométricamente los puntos de inflexión (*tipping points*) mediante variedades de indiferencia y principios de envolvente. No obstante, como señalan Kraay y McKenzie (2014) al evaluar la evidencia empírica, la mayoría de los modelos teóricos clásicos de umbrales operan con trabajo fijo y solo demuestran convergencia asintótica cualitativa, sin acotar cuánto tiempo tarda una economía que supera el umbral crítico en alcanzar un régimen productivo autosostenido. Nuestro *Teorema 9\** y la *Proposición 1\** suplen precisamente esta carencia en el modelo con trabajo endógeno de Milei y Reidel (2026), proporcionando plazos explícitos de entrada garantizada ($tau_(.1) <= 10$ y $tau_H <= 23$ períodos).

== Oferta laboral endógena y complementariedad factorial bajo rendimientos crecientes

La función de producción de elasticidad de sustitución constante (CES) introducida por Arrow, Chenery, Minhas y Solow (1961) desempeña un papel central cuando la elasticidad de sustitución entre capital y trabajo es inferior a la unidad ($rho < 0$), escenario documentado empíricamente por Klump, McAdam y Willman (2007) para economías agregadas. Cuando la tecnología CES se combina con elección endógena de horas trabajadas y utilidad no separable o dependiente del ocio, de Hek (1998) demostró que las preferencias consumo–ocio pueden engendrar multiplicidad de estados estacionarios y trampas de desarrollo incluso bajo tecnologías convexas, mientras que Benhabib y Farmer (1994) exhibieron indeterminación y fluctuaciones endógenas bajo rendimientos crecientes agregados. En el caso de Milei y Reidel (2026), la combinación de rendimientos crecientes ($1 < theta < 2$), complementariedad bruta ($rho = -d < 0$) y desutilidad logarítmica del trabajo impide comparar directamente la frontera $S_A$ frente al modelo canónico de trabajo fijo (Nota al pie 1). Nuestro *Teorema 3\** resuelve esa comparación analítica: establece un isomorfismo exacto para productividad finita $A$ y prueba que, en el límite $A -> infinity$ sobre la escala crítica $A^(-1\/r)$, el trabajo óptimo tiende a cero pero más lentamente que el capital ($K_t\/L_t -> 0$), haciendo que el término de ocio desaparezca algebraicamente y ambos regímenes converjan al mismo problema límite.

== Barreras de Bellman, dualidad y certificados estocásticos de primer paso

El método FPBB de Milei y Reidel (2026) conecta la programación dinámica clásica (Bellman, 1957; Stokey, Lucas y Prescott, 1989) y los teoremas de envolvente sin diferenciabilidad (Milgrom y Segal, 2002) con cuatro tradiciones técnicas: la viabilidad en horizonte finito (Bertsekas, 1972), las funciones de almacenamiento disipativo (Willems, 1972; Grüne, Müller, Kellett y Weller, 2021), los iterados finitos de Lyapunov en control no lineal (Geiselhart, Gielen, Lazar y Wirth, 2014; Noroozi, Geiselhart, Grüne y Wirth, 2020) y la dualidad de programación lineal y valoración de opciones americanas (Haugh y Kogan, 2004; Gaitsgory, Parkinson y Shvartsman, 2019). Sin embargo, la construcción aplicada de la Sección 7.2 de Milei y Reidel (2026) utiliza bloques de dos pasos ($N = 2$) con una función de referencia constante, descartando la mitad de las ganancias de consumo por arista, y discretiza la región $M union H$ en doce intervalos finitos en su Tabla 5 para acotar salidas adversas. Al sustituir la referencia constante por una barrera afín dependiente del estado en un solo paso ($N = 1$) y probar monotonía estricta de las holgas de salida adversa (*Proposición 1\*\**), reducimos a la mitad la cota de tiempo de entrada y elevamos el margen global certificado en un $35\%$. Más aún, mientras el FPBB original es estrictamente determinista, nuestro *Teorema 11* extiende el método al ámbito estocástico mediante supermartingalas y el Teorema de Parada Opcional de Doob (1953), conectando el plazo de entrada determinista con la probabilidad de sobrevivir shocks agregados en tránsito.

== Bienes públicos productivos, distorsiones regulatorias y estructura de mercado

Finalmente, la Sección 4.3 de Milei y Reidel (2026) se apoya en la literatura moderna de mala asignación factorial y costos regulatorios —donde Restuccia y Rogerson (2008), Hsieh y Klenow (2009), Garicano, Lelarge y Van Reenen (2016) y Trebbi, Zhang y Simkovic (2026) cuantifican cómo cuñas regulatorias dependientes del tamaño empresarial y cargas de cumplimiento deprimen la productividad total de los factores (TFP). Como advierten los propios autores (pág. 10), modelar impuestos o regulaciones únicamente como una pérdida pura $A_e = (1 - tau) A$ ignora el retorno productivo del gasto público y la protección de derechos de propiedad (Barro, 1990; Futagami, Morita y Shibata, 1993; Acemoglu, Johnson y Robinson, 2005). Nuestro *Teorema 10* unifica ambas perspectivas en una fórmula cerrada bivariada $A_e (tau_p, tau_u) = A_0 tau_p^alpha (1 - tau_p - tau_u)$ que reproduce la monotonía anti-burocracia de Milei y Reidel sobre $tau_u$ y genera la curva en U sobre $tau_p$. Asimismo, las extensiones de la Sección 6 muestran cómo descentralizar rendimientos crecientes sin pérdidas operativas mediante competencia monopolística (Dixit y Stiglitz, 1977) o externalidades de escala (Romer, 1986), revelando que fragmentar empresas en $M$ unidades replica exactamente un colapso de TFP $A\/M^(theta-1)$.

= Barreras de Bellman Afines de Un Paso, Plazo de Entrada y Afilamiento del Certificado Global

== El marco paramétrico y la holgura en la construcción de dos períodos

Siguiendo la Sección 7 de Milei y Reidel (2026), consideramos la tecnología CES armónica con parámetros $(theta, rho, w) = (3\/2, -1, 1\/2)$, donde la función de producción y la utilidad por período son:
$ F_A (K, L) = A ( (2 K L) / (K + L) )^(3/2), quad u(C, L) = eta log C + (1 - eta) log(1 - L), quad C + K' <= q K + F_A (K, L), $
sobre la caja paramétrica (7.3) del artículo original:
$ A in [0.749, 0.751], quad beta in [0.9699, 0.9701], quad q in [0.9199, 0.9201], quad eta in [0.6999, 0.7001]. $
Para la región de tránsito $M = lr([b, h)) = lr([0.10, 0.28))$ y la región objetivo $H = lr([h, infinity)) = lr([0.28, infinity))$, sea $r(K, s) = max_(0 <= L < 1) {eta log(q K + F_A (K, L) - s) + (1 - eta) log(1 - L)}$ el retorno reducido en un período. Las constantes verificadas racionalmente en las ecuaciones (7.5) y la página 59 de Milei y Reidel (2026) son:
$ hat(R) = -0.996 > r(h, b), quad Delta_2 = 0.2997 < (eta_- beta_- q_- (h - b)) / (q_+ h + F_(A_+) (h, 1) - b) = 0.2997787, $
con consumo máximo factible $C_(max) = q h + F_A (h, 1) - b <= C_(max)^+ = 0.37495167$, piso del testigo en $M$ dado por $W_M (K) >= W_M (b) > -35.579855 > -35.58$ y techo de continuación irrestricto $Psi^sharp (K) = Psi(K) - 10\/301 >= V(K)$, donde $Psi(h) < -27.83$ (y más precisamente $Psi(0.28) = -27.837112$, $Psi^sharp (0.28) = -27.870334$).

En la página 22 de Milei y Reidel (2026), para una cadena de dos transiciones internas $x -> y -> z$ en $M$, los autores acotan cada arista por separado:
$ r(x, y) <= r(h, b) - (eta (y - b)) / C_(max), quad r(y, z) <= r(h, b) - (eta q (h - y)) / C_(max), $
sumando ambas para obtener $[hat(R) - r(x, y)] + beta [hat(R) - r(y, z)] >= Delta_2$ y definiendo la barrera de dos períodos $B_0 = hat(R)\/(1 - beta) - Delta_2\/(1 - beta^2) <= -38.144176$.

Observemos, sin embargo, qué ocurre en *una única transición* cualquiera $(x, y) in M times M$. Sea $L in lr([0, 1))$ el nivel de trabajo que alcanza el máximo $r(x, y)$, con consumo $c_0 = q x + F_A (x, L) - y > 0$. Evaluando la utilidad en el par $(h, b)$ con exactamente el *mismo* trabajo $L$, el consumo resultante es $c_1 = q h + F_A (h, L) - b <= C_(max)$. La diferencia exacta de consumo entre $(h, b)$ y $(x, y)$ a igual esfuerzo laboral es:
$ c_1 - c_0 = q(h - x) + [F_A (h, L) - F_A (x, L)] + (y - b). $
Dado que $x < h$ y $F_A (dot, L)$ es no decreciente en el stock de capital para todo $L in [0, 1]$, se cumple que $F_A (h, L) - F_A (x, L) >= 0$. Por consiguiente, *ambos* términos $q(h - x) > 0$ y $(y - b) >= 0$ están presentes simultáneamente en cada arista individual $(x, y) in M times M$. Al descartar $q(h - x)$ en la primera transición y $(z - b)$ en la segunda, la construcción en bloques disjuntos de longitud $N = 2$ pierde prácticamente la mitad de la disipación acumulada a lo largo de trayectorias que permanecen en $M$.

== Construcción de la barrera afín de un paso y reducción del plazo de entrada

El siguiente lema formaliza la cota de pérdida por arista individual y construye una barrera regional afín explícita que satisface la desigualdad de Bellman en un solo paso en todo $M$.

#thm_box("Lema 1 (Cota de pérdida unificada y barrera regional afín en M)")[
  Bajo la caja paramétrica (7.3), toda transición de permanencia $(x, y) in M times M = lr([b, h)) times lr([b, h))$ satisface:
  $ r(x, y) <= r(h, b) - eta / C_(max) [q(h - x) + (y - b)] <= hat(R) - eta / C_(max) [q(h - x) + (y - b)]. $
  En consecuencia, la función afín dependiente del estado definida sobre $M = lr([b, h))$ por:
  $ B_1 (x) = B_* - (eta q (h - x)) / C_(max), quad B_* = (hat(R) - Delta_2) / (1 - beta), $
  es una barrera regional de Bellman acotada en $M$, es decir, satisface $B_1 (x) >= r(x, y) + beta B_1 (y)$ para todo $x, y in M$. Más aún, uniformemente en (7.3):
  $ B_1 (x) <= B_* <= -43.0465116, quad B_1 (b) <= -43.355594, $
  y el margen de calibración frente al testigo factible $W_M (x)$ satisface $W_M (x) - B_1 (x) >= W_M (b) - B_1 (b) > 7.7755$ (y uniformemente $W_M (x) - B_* > 7.4665$).
]

#proof_block[
  Para cualquier $(x, y) in M times M$, sea $L in lr([0, 1))$ el maximizador que define $r(x, y)$ con consumo $c_0 = q x + F_A (x, L) - y > 0$, y sea $c_1 = q h + F_A (h, L) - b <= C_(max)$. Como $(h, b, L)$ es factible en $(h, b)$ y el término de ocio $(1 - eta) log(1 - L)$ se cancela, la concavidad del logaritmo ($log(c_1\/c_0) >= (c_1 - c_0)\/c_1$) y la monotonía $F_A (h, L) >= F_A (x, L)$ implican:
  $ r(h, b) - r(x, y) >= eta log(c_1 / c_0) >= eta (c_1 - c_0) / c_1 >= eta / C_(max) [q(h - x) + (y - b)]. $
  Reemplazando $r(h, b) <= hat(R)$ se obtiene la primera desigualdad del enunciado. Ahora evaluamos $r(x, y) + beta B_1 (y)$ para cualquier par $x, y in M$:
  $ r(x, y) + beta B_1 (y) &<= hat(R) - (eta q (h - x)) / C_(max) - (eta (y - b)) / C_(max) + beta B_* - (eta beta q (h - y)) / C_(max) \
  &= hat(R) + beta B_* - (eta q (h - x)) / C_(max) - eta / C_(max) [(y - b) + beta q (h - y)]. $
  Dado que $y in lr([b, h))$ y $beta q < 1$, la combinación lineal en $y$ cumple:
  $ (y - b) + beta q (h - y) = (1 - beta q)(y - b) + beta q (h - b) >= beta q (h - b). $
  Por lo tanto, el último término está acotado inferiormente por $(eta beta q (h - b))\/C_(max) > Delta_2$. Como $hat(R) - Delta_2 + beta B_* = B_*$ por definición de $B_*$, concluimos que para todo $x, y in M$:
  $ r(x, y) + beta B_1 (y) <= B_* - (eta q (h - x)) / C_(max) = B_1 (x). $
  En la caja (7.3), $hat(R) - Delta_2 = -0.996 - 0.2997 = -1.2957 < 0$ y $beta >= 0.9699$, de modo que $B_* <= -1.2957 \/ 0.0301 = -43.04651162...$ Asimismo, $(eta q)\/C_(max) >= (0.6999 times 0.9199)\/0.37495167 = 1.717123$, lo que arroja $B_1 (b) <= -43.0465116 - 1.717123(0.18) = -43.355594$. Finalmente, dado que el consumo del testigo en el primer paso $c_M (x) = q x + F_A (x, 0.68) - 0.135$ satisface $0 < c_M (x) < C_(max)$ y $F_(A,K) (x, 0.68) > 0$, la derivada del piso del testigo verifica $W'_M (x) = eta [q + F_(A,K) (x, 0.68)] \/ c_M (x) > (eta q)\/C_(max) = B'_1 (x)$ en todo $M$. Por ende, la holgura $W_M (x) - B_1 (x)$ es estrictamente creciente en $x in lr([b, h))$ y alcanza su ínfimo en $x = b$:
  $ inf_(x in M) [W_M (x) - B_1 (x)] = W_M (b) - B_1 (b) > -35.58 - (-43.355594) = 7.775594. $
]

Con el Lema 1 establecido, demostramos nuestra versión reforzada del Teorema 9 de Milei y Reidel (2026), que reduce el límite temporal de entrada de $46$ a $23$ períodos (y a $24$ bajo comparación uniforme no condicionada al estado inicial).

#thm_box("Teorema 9* (Certificado CES reforzado y reducción a la mitad del plazo de entrada)")[
  Bajo la caja paramétrica (7.3), sean $M = lr([0.10, 0.28))$ y $H = lr([0.28, infinity))$.
  1. La barrera regional afín $B_1 (K)$ del Lema 1 y los testigos factibles de la Tabla 4 de Milei y Reidel (2026) conforman un certificado estricto de primer paso (FPBB) con margen de permanencia uniforme mayor a $7.466$ ($7.775$ estado a estado) y margen de salida adversa $> 0.0423$ bajo la partición original (elevado a $> 0.0571$ en la Proposición 1\*\*).
  2. Toda trayectoria óptima que parte de $K_0 in M$ ingresa a la región productiva $H = lr([0.28, infinity))$ a más tardar en la fecha *$tau_H <= 23$* (o $tau_H <= 24$ usando únicamente cotas uniformes independientes de $K_0$) y permanece en $H$ para siempre. Si $K_0 in [0.10, 0.105]$, su fecha de primera entrada satisface:
  $ 3 <= tau_H <= 23. $
]

#proof_block[
  Las comparaciones de salida adversa desde $M$ y $H$ hacia acciones por debajo de $b$ y $h$ dependen únicamente de $W_M, W_H$ y del techo $Psi^sharp$, por lo que bajo la Tabla 5 original conservan margen uniforme $> 0.0423$ (y se mejoran a $> 0.0571$ en la Proposición 1\*\*). Por el Teorema 5 de selección global FPBB, ninguna trayectoria óptima desde $M union H$ realiza jamás una transición adversa ni permanece indefinidamente en $M$.

  Para acotar la fecha máxima de entrada $tau_H$, consideremos cualquier camino factible que permanezca en $M$ durante $T >= 1$ transiciones consecutivas $x_0 -> x_1 -> dots.c -> x_T$ con $x_t in M$ para todo $0 <= t <= T$, seguido de cualquier continuación factible desde $x_T$. Iterando la desigualdad de un paso $r(x_t, x_(t+1)) <= B_1 (x_t) - beta B_1 (x_(t+1))$ para $t = 0, dots, T - 1$ y acotando el valor de continuación en $t = T$ mediante $V(x_T) <= Psi^sharp (x_T) <= Psi(x_T)$, el bienestar total $J_(x_0) (pi)$ de dicho camino verifica:
  $ J_(x_0) (pi) <= B_1 (x_0) + beta^T [Psi^sharp (x_T) - B_1 (x_T)]. $
  En el intervalo $x in lr([0.10, 0.28))$, la derivada de $Psi^sharp (x) = 0.4 x - 5 x^(-1\/2) - 18.5 - 10\/301$ es $(Psi^sharp)'(x) = 0.4 + 2.5 x^(-3\/2) >= 0.4 + 2.5 (0.28)^(-3\/2) = 17.272 > 2 > (eta q)\/C_(max) = B'_1 (x)$. En consecuencia, $Psi^sharp (x_T) - B_1 (x_T)$ es estrictamente creciente en $x_T in lr([b, h))$ y está acotada superiormente por su límite en $x_T arrow.t h$:
  $ sup_(x_T in M) [Psi^sharp (x_T) - B_1 (x_T)] = Psi^sharp (h) - B_* < -27.83 - B_*. $
  *Cota uniforme ($T = 24$):* Utilizando la cota uniforme $B_1 (x_0) <= B_* <= -43.0465116$ y la cota superior conservadora $Psi(h) < -27.83$ de la página 59 de Milei y Reidel (2026), para $T = 24$ períodos obtenemos:
  $ J_(x_0) (pi) <= -43.0465116 + (0.9701)^24 (-27.83 - (-43.0465116)) = -43.0465116 + 7.34400 = -35.70251 < -35.58 <= W_M (x_0). $
  *Cota estado a estado ($T = 23$):* Dado que $W_M (x_0) - B_1 (x_0)$ es estrictamente creciente en $x_0 in lr([b, h))$ por el Lema 1, la ventaja del testigo sobre el camino de $T$ pasos cumple para todo $x_0, x_T in M$:
  $ W_M (x_0) - J_(x_0) (pi) >= [W_M (b) - B_1 (b)] - beta_+^T [Psi(h) - B_*]. $
  Evaluando en $T = 23$ (exactamente la mitad de los $46$ períodos del artículo original):
  $ W_M (x_0) - J_(x_0) (pi) >= 7.775594 - (0.9701)^23 (15.2165116) = 7.775594 - 7.569980 = +0.205614 > 0. $
  (Si además se emplean las cotas exactas $hat(R) = -0.996799$, $Delta_2 = 0.299778$ y $Psi^sharp (0.28) = -27.870334$ ya demostradas en las páginas 57–59 de Milei y Reidel, la holgura resulta positiva incluso en $T = 22$ con $+0.0073$). Por lo tanto, ningún camino óptimo puede permanecer en $M$ durante $23$ períodos, lo que certifica $tau_H <= 23$. La cota inferior $tau_H >= 3$ para $K_0 in [0.10, 0.105]$ se sigue de $Phi(0.105) < 0.16$ y $Phi(0.16) < 0.26 < 0.28$.
]

#figure(
  image("fig1_barrier_es.svg", width: 100%),
  caption: [Comparación entre la construcción por bloques de dos períodos de Milei y Reidel (2026) y nuestra barrera afín de un paso $B_1 (K)$ sobre $M = lr([0.10, 0.28))$. El Panel (a) ilustra la ganancia de calibración de casi $5$ unidades de bienestar; el Panel (b) muestra la reducción del plazo máximo certificado de entrada de $tau_H <= 46$ a $tau_H <= 23$–$24$ períodos.],
)

== Cota explícita de cruce en el tramo previo $M_0 = lr([0.05, 0.10))$

En la Figura 6 (página 21) de Milei y Reidel (2026), el cruce desde $K_0 > S_A$ hasta $0.10$ se garantiza únicamente en tiempo finito ($tau_(.1) < infinity$) sin cota cuantitativa explícita. Aunque ninguna cota uniforme puede llegar hasta $K_0 -> S_A^+$ debido a la desaceleración hiperbólica en el punto de coexistencia $S_A$, sí es posible extender directamente nuestra barrera afín de un paso al intervalo ancla $M_0 = lr([b_0, h_0)) = lr([0.05, 0.10))$, donde el Teorema 8 ya excluye salidas adversas hacia abajo ($G(K) > K$).

#thm_box([Proposición 1\* (Cota explícita de cruce en el tramo previo $M_0 = lr([0.05, 0.10))$)])[
  Bajo la caja paramétrica (7.3), sea $M_0 = lr([0.05, 0.10))$. Toda trayectoria óptima con $K_0 in M_0$ supera el umbral $0.10$ en a lo sumo *$tau_(.1) <= 10$ períodos*, y alcanza la región productiva $H = lr([0.28, infinity))$ en a lo sumo $tau_H <= 33$ períodos totales.
]

#proof_block[
  En $M_0 = lr([b_0, h_0)) = lr([0.05, 0.10))$, la maximización directa sobre $L in lr([0, 1))$ da $r(0.10, 0.05) <= -1.827072 < hat(R)_0 := -1.827$, consumo máximo $C_(max,0) <= q_+(0.10) + F_(A_+) (0.10, 1) - 0.05 = 0.100233$ y pérdida por paso $Delta^(0) := 0.3115 < (eta_- beta_- q_- (0.05))\/C_(max,0) = 0.311503$. Por el Lema 1 aplicado a $M_0$, la barrera $B^(0) (x) = B_*^(0) - (eta q (h_0 - x))\/C_(max,0)$ satisface $B_*^(0) = (hat(R)_0 - Delta^(0))\/(1 - beta) <= -2.1385 \/ 0.0301 = -71.046512$.

  Como testigo factible desde $K_0 in M_0$, anteponemos al testigo $W_M (0.10) > -35.58$ los tres primeros pasos de la progresión geométrica de la página 46 de Milei y Reidel ($0.05 -> 0.065 -> 0.0845 -> 0.100$) con trabajo constante $L = 0.75$. Evaluando en los extremos desfavorables $A_-, q_-$ y $eta_(plus.minus)$, las utilidades de etapa superan $(-3.791, -3.504, -3.197)$, lo que garantiza un piso de bienestar $W_(M_0) (K_0) >= W_(M_0) (0.05) > -43.845$. Como en $h_0 = 0.10$ el techo irrestricto cumple $Psi(0.10) < -34.271388$, en $T_0 = 10$ pasos dentro de $M_0$ se tiene:
  $ B_*^(0) + (0.9701)^10 [Psi(0.10) - B_*^(0)] = -71.046512 + (0.9701)^10 (36.775124) = -43.8980 < -43.845 < W_(M_0) (K_0). $
  Como el orden monótono de sucesores (F.1) excluye transiciones óptimas desde $M_0$ hacia abajo de $0.05$, toda trayectoria óptima desde $M_0$ debe ingresar a $lr([0.10, infinity))$ en $tau_(.1) <= 10$ períodos. Combinado con el Teorema 9\*, entra en $H = lr([0.28, infinity))$ en a lo sumo $10 + 23 = 33$ períodos.
]

#v(0.3em)
#figure(
  text(size: 9.2pt, table(
    columns: (2.2fr, 1.45fr, 1.55fr, 1.5fr),
    align: (left, center, center, center),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [*Métrica certificada en la caja (7.3)*], [*Milei y Reidel (2026)*], [*Este trabajo (Barrera $B_1$)*], [*Mejora obtenida*],
    table.hline(stroke: 0.6pt),
    [Referencia regional en $M = lr([0.10, 0.28))$], [Constante ($N = 2$)], [Afín en $K$ ($N = 1$)], [Retiene $q(h-x)$ y $(y-b)$],
    [Cota superior de $B(K)$ en $M$], [$-38.144176$], [$-43.046512$ \ (a $-43.3556$)], [$-4.90$ a $-5.21$ uds.],
    [Margen de calibración ($W_M - B$)], [$> 2.564$], [$> 7.466$ \ ($> 7.775$ en $b$)], [$times 2.91$ \ (a $times 3.03$)],
    [Plazo máximo $M -> H$ ($tau_H$)], [$<= 46$ períodos], [*$<= 23$ períodos* \ ($24$ unif.)], [*Reducción del $50\%$*],
    [Ventana desde $K_0 in [0.10, 0.105]$], [$3 <= tau_H <= 46$], [*$3 <= tau_H <= 23$*], [Mitad del rango sup.],
    [Cruce desde $lr([0.05, 0.10))$ a $0.10$ ($tau_(.1)$)], [Finito (sin cota)], [*$<= 10$ períodos*], [Elimina brecha abierta],
    [Plazo total desde $K_0 = 0.05$ a $H$], [Finito (sin cota)], [*$<= 33$ períodos*], [$13$ períodos $< 46$],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Síntesis cuantitativa de las mejoras analíticas sobre la Sección 7.2 y el Teorema 9 de Milei y Reidel (2026) bajo exactamente los mismos parámetros (7.3).],
)

== Monotonía estado a estado de las salidas adversas y reducción de la Tabla 5

Al elevar mediante $B_1 (K)$ el margen de calibración de permanencia a $> 7.4665$ ($> 7.7755$ en $b = 0.10$) y el margen del prefijo en $T = 23$ a $+0.2056$, el bloque de permanencia en $M$ deja por completo de ser una restricción activa en el certificado global FPBB. En la Tabla 5 de Milei y Reidel (2026, pág. 23 y Apéndice F.3), las comparaciones de salida adversa sobre las regiones $M = [0.10, 0.28)$ y $H_1 = [0.28, 0.80)$ se verifican dividiendo dichos intervalos en $12$ subintervalos finitos $[k_-, k_+]$ y evaluando $underline(W)_X (k_-)$ en el extremo izquierdo frente a la cota superior $E^+ (k_+, a; l_0) + beta_- Psi^sharp (a)$ en el extremo derecho, lo que arroja un margen mínimo global de $0.0423$ (reportado conservadoramente como $.04$).

La siguiente proposición demuestra que esa discretización por subintervalos es innecesaria: evaluando ambas funciones en el *mismo* estado $K$, la ventaja del testigo frente a la envolvente tangente crece estrictamente con $K$ en todo $M$ y en todo $H_1$, reduciendo las $12$ filas finitas de la Tabla 5 a únicamente dos evaluaciones puntuales en los bordes inferiores $K = 0.10$ y $K = 0.28$.

#thm_box([Proposición 1\*\* (Certificación analítica de monotonía y ampliación del margen global)])[
  Bajo la caja paramétrica (7.3), sean los testigos de la Tabla 4 de Milei y Reidel (2026) definidos por $(l_M, s_M, underline(T)_M, a, l_0) = (0.68, 0.135, -33.103, 0.10, 0.44)$ sobre $M = lr([0.10, 0.28))$ y $(l_H, s_H, underline(T)_H, a, l_0) = (0.72, 0.375, -27.164, 0.28, 0.57)$ sobre $H_1 = lr([0.28, 0.80))$. La ventaja puntual del testigo frente a la envolvente de salida adversa (F.19)–(F.20),
  $ Delta_X (K) := underline(W)_X (K) - [E^+ (K, a; l_0) + beta_- Psi^sharp (a)], $
  es estrictamente creciente en todo punto de ambos intervalos, sin mínimos interiores. Más precisamente:
  1. Un certificado de aritmética de intervalos sobre el cociente $R_X (K) = (S(K) - a)\/c_X (K)$ en $4$ subintervalos de $M$ y $6$ de $H_1$ garantiza uniformemente $Delta'_M (K) >= +0.0722 > 0$ en $M$ y $Delta'_(H_1) (K) >= +0.0094 > 0$ en $H_1$; adicionalmente, las cotas de intervalo de la segunda derivada certifican $Delta''_M (K) <= -0.8564 < 0$ (en $8$ subintervalos) y $Delta''_(H_1) (K) <= -0.0439 < 0$ (en $10$ subintervalos), ubicando el mínimo de $Delta'_X$ en el extremo derecho:
     $ min_(K in M) Delta'_M (K) = Delta'_M (0.28) = +0.502666, quad min_(K in H_1) Delta'_(H_1) (K) = Delta'_(H_1) (0.80) = +0.100489. $
  2. En consecuencia, $inf Delta_X$ se alcanza en el borde izquierdo de cada dominio y las $12$ particiones finitas de la Tabla 5 de Milei y Reidel (2026) se reducen a dos evaluaciones exactas en $K = 0.10$ y $K = 0.28$:
     - En $M = lr([0.10, 0.28))$, el margen mínimo de salida adversa asciende de $> 0.0436$ a *$> 0.0947$* ($+117\%$).
     - En $H_1 = lr([0.28, 0.80))$, el margen mínimo asciende de $> 0.0423$ a $> 0.0561$ (con $l_0 = 0.60$) y a *$> 0.0571$* (con $l_0 = 0.57$), elevando el margen global certificado de todo el Teorema 9 en $M union H$ de $0.0423$ ($.04$) a *$> 0.0571$* ($+35\%$).
]

#proof_block[
  Por la construcción del Apéndice F.3 (ecuaciones F.19–F.20 de Milei y Reidel), para cada región $X in {M, H_1}$ con esfuerzo del testigo $l_X$, sucesor $s_X$, cola $underline(T)_X$, umbral de salida $a$ y punto de tangencia $l_0 >= K\/2$, el consumo mínimo del testigo es $c_X (K) = q_- K + F_(A_-) (K, l_X) - s_X > 0$, la pendiente tangente es $t(K) = partial_L F_(A_+) (K, l_0)$ y el recurso virtual mayorante es $S(K) = q_+ K + F_(A_+) (K, l_0) + (1 - l_0) t(K)$. Para $(K, a, l_0) = (0.28, 0.28, 0.57)$ se cumple $l_0 = 0.57 >= 0.80\/2$ en todo $H_1$ y $beta_- psi'(0.28) = 16.7535 > 4.6539 = 1\/(S(0.28) - 0.28)$, de modo que la envolvente sobre $[0.05, a]$ alcanza su máximo en $s = a$ (la rama en $s = 0$ es inferior por más de $5.37$ unidades en $M$ y $11.77$ en $H_1$).

  *Descomposición exacta de $Delta'_X (K)$ y ausencia de mínimos interiores:* La pendiente tangente satisface las identidades logarítmicas cerradas:
  $ (t'(K)) / (t(K)) = (5 l_0) / (2 K (K + l_0)) > 0, quad ((t'\/t)')(K) = - (5 l_0 (2 K + l_0)) / (2 K^2 (K + l_0)^2) < 0. $
  Diferenciando cada rama de $underline(W)_X$ y de $E^+ (K, a; l_0)$ y definiendo el cociente $R_X (K) := (S(K) - a)\/c_X (K) > 1$ se obtiene la cota inferior exacta en todo punto diferenciable (y para ambas derivadas laterales en eventuales quiebres de $min\/max$):
  $ Delta'_X (K) >= (eta_- c'_X (K) R_X (K) - S'(K)) / (S(K) - a) + (1 - eta_+) (5 l_0) / (2 K (K + l_0)). $
  Para certificar $R'_X (K) < 0$, escribimos $R'_X (K) = Q_X (K) \/ c_X (K)^2$ con Wronskiano $Q_X (K) := S'(K) c_X (K) - c'_X (K)(S(K) - a)$, cuya derivada cancela idénticamente el producto $S' c'$: $Q'_X (K) = S''(K) c_X (K) - c''_X (K)(S(K) - a)$. Como $partial_K F_(A,K)(K, L) prop (L - 4K) K^(-1\/2)(K + L)^(-7\/2)$ y $t''(K) prop (3 l_0\/2 - 2K) K^(1\/2)(K + l_0)^(-9\/2)$, tanto $F_(A,K)$ (pico único en $L\/4$) como $t'$ (pico único en $3 l_0\/4$) carecen de mínimos interiores, mientras $|Q'_X|$ queda acotado en cada subintervalo $[k_L, k_R]$ por las envolventes de extremo de $|F_(A, K K)|$ y $|t''|$. La cota de Lipschitz desde el punto medio $k_m = (k_L + k_R)\/2$, $Q_X (K) <= Q_X (k_m) + (k_R - k_L)|Q'_X|_([k_L, k_R])\/2$, arroja:
  - en los $4$ subintervalos iguales de $M$ (`[0.100, 0.145, 0.190, 0.235, 0.280]`): $Q_M (K) <= -0.06165, -0.05640, -0.04694, -0.03960 < 0$;
  - en los $6$ subintervalos de $H_1$ (`[0.28, 0.36, 0.45, 0.54, 0.63, 0.72, 0.80]`): $Q_(H_1) (K) <= -0.18135, -0.15687, -0.13910, -0.12646, -0.12009, -0.12746 < 0$.
  Así $R_X (K)$ es estrictamente decreciente en todo $M$ y $H_1$, cumpliendo $R_X (K) >= R_X (k_R)$ en cada $[k_L, k_R]$. Reemplazando $c'_X (K) >= min{c'_X (k_L), c'_X (k_R)}$, $S'(K) <= S'_([k_L, k_R], max)$ (por unimodalidad de $F_(A,K)$ y $t'$) y el denominador $S(K) - a$ por el extremo apropiado según el signo del numerador, se obtienen las cotas de intervalo analíticas:
  - en $M$ ($4$ subintervalos): $Delta'_M (K) >= +3.0287, +0.3955, +0.1252, +0.0722 > 0$;
  - en $H_1$ ($6$ subintervalos): $Delta'_(H_1) (K) >= +1.4674, +0.3242, +0.1022, +0.0348, +0.0094, +0.0119 > 0$.
  Esto excluye rigurosamente todo mínimo interior de $Delta_X (K)$ en ambos dominios sin depender de mallas. Además, factorizando la segunda derivada como $Delta''_X (K) <= [(S')^2 - eta_- (c'_X R_X)^2]\/(S-a)^2 + eta_- c''_X\/c_X - S''\/(S-a) + (1 - eta_+)(t'\/t)'(K)$ (empleando el signo exacto $c''_X <= 0$ cuando $k_L >= l_X\/4$), una evaluación de intervalo análoga en $8$ subintervalos iguales de $M$ y $10$ de $H_1$ certifica $Delta''_M (K) <= -0.8564 < 0$ y $Delta''_(H_1) (K) <= -0.0439 < 0$. Por concavidad estricta, $Delta'_X$ decrece monótonamente y alcanza su mínimo único en el borde derecho ($Delta'_M (0.28) = +0.502666$ y $Delta'_(H_1) (0.80) = +0.100489$), mientras $Delta_X$ alcanza su mínimo en el borde izquierdo:
  - En $K = 0.10$: $underline(W)_M (0.10) - [E^+ (0.10, 0.10; 0.44) + beta_- Psi^sharp (0.10)] = 0.094717 > 0.0947$ (y $0.062495 > 0.0624$ usando $Psi$).
  - En $K = 0.28$: con $l_0 = 0.60$, $underline(W)_H (0.28) - [E^+ (0.28, 0.28; 0.60) + beta_- Psi^sharp (0.28)] = 0.056121 > 0.0561$; optimizando $l_0 = 0.57$, se eleva a $0.057148 > 0.0571$ (y $0.024926 > 0.0249$ usando $Psi$).
  Combinado con la cota (F.21) para $H_2 = [0.80, infinity)$ ($> 2.2984$), el mínimo global certificado sobre todo $M union H$ asciende a $> 0.0571$.
]

#v(0.3em)
#figure(
  text(size: 9.2pt, table(
    columns: (1.4fr, 1.85fr, 1.35fr, 1.4fr),
    align: (left, center, center, center),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [*Región y dominio*], [*Método de comparación*], [*Margen usando $Psi$*], [*Margen usando $Psi^sharp$*],
    table.hline(stroke: 0.6pt),
    [$M = lr([0.10, 0.28))$], [Tabla 5 original ($4$ intervalos)], [$> 0.0114$], [$> 0.0436$],
    [$M = lr([0.10, 0.28))$], [*Prop. 1\*\* en $K = 0.10$* \ *($l_0 = 0.44$)*], [*$> 0.0624$*], [*$> 0.0947$*],
    [$H_1 = lr([0.28, 0.80))$], [Tabla 5 original ($8$ intervalos)], [$> 0.01008$], [$> 0.0423$],
    [$H_1 = lr([0.28, 0.80))$], [*Prop. 1\*\* en $K = 0.28$* \ *($l_0 = 0.57$)*], [*$> 0.0249$*], [*$> 0.0571$*],
    [$H_2 = lr([0.80, infinity))$], [Cota global ec. (F.21)], [$> 2.2662$], [$> 2.2984$],
    table.hline(stroke: 0.6pt),
    [*Margen global FPBB*], [*Mínimo sobre $M union H$*], [*$> 0.0249$* \ (vs. $0.01008$)], [*$> 0.0571$* \ (vs. $0.0423$)],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Eliminación de las $12$ particiones finitas de la Tabla 5 de Milei y Reidel (2026) mediante la monotonía estado a estado de la Proposición 1\*\*.],
)

= Equivalencia Asintótica entre Trabajo Endógeno y Trabajo Fijo (Nota al pie 1 y Teorema 3)

En la página 2 de Milei y Reidel (2026), la Nota al pie 1 plantea como problema abierto la comparación entre la frontera de escala mínima viable $S_A$ del modelo con trabajo endógeno y la frontera $S_A^("fix") (overline(L))$ de una economía por lo demás idéntica donde la oferta de trabajo está fija exógenamente en $L_t equiv overline(L) in lr((0, 1])$ (de modo que la utilidad de período es simplemente $eta log C_t$). Asimismo, en la Sección 4.2 (*Teorema 3*, ec. 4.6), los autores demuestran que cuando $A -> infinity$ con $r = theta - 1$ y $c_K = w^(theta\/rho)$:
$ (delta / c_K)^(1/r) <= liminf_(A -> infinity) A^(1/r) S_A <= limsup_(A -> infinity) A^(1/r) S_A <= (D / c_K)^(1/r), quad D = delta + (1 - beta) / beta. $

== Isomorfismo exacto para $A$ finito y equivalencia asintótica cuando $A -> infinity$

Demostramos a continuación que esta pregunta abierta admite una respuesta exacta en el límite asintótico $A -> infinity$ para todo $overline(L) in lr((0, 1])$, junto con una ley de isomorfismo exacto para $A$ finito y la condición estructural precisa de comparación frente a pleno empleo.

#thm_box("Teorema 3* (Isomorfismo de trabajo fijo y convergencia asintótica de fronteras)")[
  Fijemos los seis parámetros primitivos distintos de $A$ en la región paciente $E = D - theta delta < 0$, con $d = -rho > 0$ y $r = theta - 1 in (0, 1)$.
  1. *Régimen de alta productividad ($A -> infinity$) y convergencia de fronteras:* Reescalando en la escala crítica del Teorema 3, $K_t = A^(-1\/r) k_t$ y $C_t = A^(-1\/r) c_t$ con $k_t, c_t = Theta(1)$, a lo largo de toda acción óptima interior la oferta laboral y la razón capital-trabajo obedecen:
  $ L_t = Theta( A^(- d / (r (1 + d))) ) -> 0, quad K_t / L_t = Theta( A^(- 1 / (r (1 + d))) ) -> 0 quad (A -> infinity). $
  En consecuencia, en compactos de $(k, L)$, la pérdida de utilidad por ocio se anula como $(1 - eta)|log(1 - L_t)| = O(A^(-d\/[r(1+d)])) -> 0$ y el producto reescalado converge uniformemente al mismo límite convexo $c_K k^theta$ que con trabajo fijo $overline(L) in lr((0, 1])$. Más aún, dado que la condición de paciencia (2.3) implica necesariamente $beta theta > beta [q + theta delta] > 1$, para todo $overline(L) in lr((0, 1])$ ambas fronteras reescaladas convergen al límite físico común y satisfacen la equivalencia asintótica estricta:
  $ lim_(A -> infinity) A^(1/r) S_A = lim_(A -> infinity) A^(1/r) S_A^("fix") (overline(L)) = ( delta / c_K )^(1/r), quad lim_(A -> infinity) S_A / (S_A^("fix") (overline(L))) = 1. $
  2. *Isomorfismo exacto para $A$ finito y criterio variacional de ordenamiento:* Para todo $A$ finito y todo $overline(L) in lr((0, 1])$, el cambio de escala $tilde(K)_t = K_t \/ overline(L)$ induce un isomorfismo exacto con la economía de capacidad plena ($overline(L) = 1$) a productividad $A overline(L)^r$:
  $ S_A^("fix") (overline(L)) = overline(L) dot S_(A overline(L)^r)^("fix") (1), quad kappa_A^("fix") (overline(L)) = overline(L) dot kappa_(A overline(L)^r) >= kappa_A^("fix") (1) = kappa_A. $
  Frente a la economía con trabajo endógeno, la economía a capacidad plena ($overline(L) = 1$ sin costo de ocio) domina en bienestar ($V_A^("fix") (K; 1) > V_A (K)$ para todo $K > 0$). A la escala crítica $S_A$, sea $Delta W_A^+ := J_A^("fix") (pi^+ |_(L=1)) - V_A (S_A) > 0$ el excedente de aplicar pleno empleo a la trayectoria productiva óptima $pi^+$ desde $S_A$, y sea $Delta W_A^- := sup_(pi^- in cal(O)_(-)^("fix")) [J_A^("fix") (pi^-) - V_A (S_A)]$ la máxima ganancia de cualquier senda extinta bajo trabajo fijo desde $S_A$. Entonces $Delta W_A^- = O(A^(-d\/[r(1+d)]))$ y la desigualdad estricta $S_A^("fix") (1) < S_A$ se cumple en todo $A$ tal que $Delta W_A^+ > Delta W_A^-$.
]

#proof_block[
  *Parte 1 (Escalado de operadores y convergencia de fronteras).* Sea $K = A^(-1\/r) k$ y $C = A^(-1\/r) c$. Usando $1 - theta\/r = -1\/r$ y $rho = -d < 0$:
  $ f_A (k, L) := A^(1/r) F_A (A^(-1\/r) k, L) = c_K k^theta [1 + c_w (k / (A^(1\/r) L))^d]^(-theta/d), quad c_w = (1 - w) / w. $
  Con trabajo fijo $L equiv overline(L) in lr((0, 1])$, $(A^(1\/r) overline(L))^(-d) = O(A^(-d\/r)) -> 0$ y $f_A (k, overline(L)) -> c_K k^theta$. Con trabajo endógeno, multiplicando la condición de primer orden $F_(A,L)(K, L) = nu C\/(1 - L)$ ($nu = (1 - eta)\/eta$) por $A^(1\/r)$:
  $ theta c_K c_w k^(theta + d) A^(-d/r) L^(-1 - d) [1 + c_w (A^(1/r) L / k)^(-d)]^(-1 - theta/d) = nu c / (1 - L), $
  lo que fuerza $L = [theta c_K c_w k^(theta + d)\/(nu c)]^(1\/(1+d)) A^(-d\/[r(1+d)])(1 + o(1)) -> 0$ y $K\/L = Theta(A^(-1\/[r(1+d)])) -> 0$, de modo que $f_A (k, L) = c_K k^theta [1 + O(A^(-d\/[r(1+d)]))]$, $(1 - eta)log(1 - L) = -O(A^(-d\/[r(1+d)]))$ y el operador normalizado converge en compactos al de trabajo fijo.

  Para demostrar la convergencia de las fronteras mismas, nótese primero que para $q in (0, 1)$ y $theta > 1$, $theta - (q + theta delta) = q(theta - 1) > 0$. Por ende, la condición de paciencia (2.3), $beta[q + theta delta] > 1$, implica necesariamente $beta theta > 1$. Fijemos cualquier stock reescalado $k_0 > (delta\/c_K)^(1\/r)$ y sea $K_0 = A^(-1\/r) k_0$. Construimos una expansión factible con trabajo constante $L_0 in (0, 1)$ (en particular $L_0 = 3\/4$, válida tanto en trabajo endógeno como con costo cero en trabajo fijo cuando $overline(L) = 1$, y con el mismo escalado para $overline(L) in (0, 1)$):
  - Elegimos $epsilon_1 in (0, 1)$ tal que $c_K (1 - epsilon_1) k_0^r > delta$ y un umbral macroscópico fijo $K_("esc") > 0$ (independiente de $A$) suficientemente pequeño para que $[1 + c_w (K_("esc")\/L_0)^d]^(-theta\/d) >= 1 - epsilon_1\/2$, de modo que $f_A (k, L_0) >= c_K (1 - epsilon_1\/2) k^theta$ mientras $K_t <= K_("esc")$.
  - *Fase I (escape del cuello de botella):* Consumiendo la mitad del excedente neto sobre $k_t$, se alcanza en $T_1 (k_0) < infinity$ pasos (independientes de $A$) un nivel fijo $k_1$ donde $c_K (1 - epsilon_1\/2) k_1^(theta - tilde(theta)) >= 2$, habiéndose fijado $tilde(theta) in (beta^(-1), theta)$ (factible por $beta theta > 1$).
  - *Fase II (crecimiento superexponencial):* Ahorrando mitad de los recursos ($C_t = K_(t+1) = [q K_t + F_A (K_t, L_0)]\/2$), se cumple $k_(t+1) >= k_t^(tilde(theta))$ mientras $k_t <= A^(1\/r) K_("esc")$, alcanzándose $K_(T_1 + J) >= K_("esc")$ en a lo sumo $J(A) <= (log log A)\/(log tilde(theta)) + O(1)$ períodos.
  - *Fase III (meseta macroscópica):* Desde $t >= T_1 + J$, mantener constante $K_("esc")$ rinde consumo $A f_1 (K_("esc"), L_0) - delta K_("esc") = Omega(A)$, aportando utilidad descontada al menos $beta^(T_1 + J) (eta\/(1 - beta)) log A - O(1)$.

  En contraste, por la cota de recursos del Lema 9 en $(0, K_0]$ (con tasa $G_A (K_0) = q + F_A (K_0, 1)\/K_0 -> q + c_K k_0^r = O(1)$), toda trayectoria confinada en $(0, K_0]$ —incluida cualquier senda óptima extinta desde $K_0$— tiene bienestar acotado superiormente por $-(eta\/[r(1 - beta)]) log A + O(1)$. Sustrayendo ambos términos y usando $beta^(J(A)) >= c_0 (log A)^(-|log beta|\/log tilde(theta))$, el excedente neto de la expansión factible escala al menos como $c_1 (log A)^(1 - |log beta|\/log tilde(theta)) - O(1) -> +infinity$ porque $beta tilde(theta) > 1 => 1 - |log beta|\/log tilde(theta) > 0$. Por contradicción con el Teorema 1, ningún óptimo puede extinguirse desde $K_0 = A^(-1\/r) k_0$ para $A$ grande, luego $limsup_(A -> infinity) A^(1\/r) S_A <= (delta\/c_K)^(1\/r)$ (y análogamente para $S_A^("fix") (overline(L))$). Combinado con la cota física inferior (4.5) del Teorema 3 y (2.4) para $kappa_A^("fix") (overline(L))$, ambos límites coinciden exactamente en $(delta\/c_K)^(1\/r)$ y su cociente converge a $1$.

  *Parte 2 (Isomorfismo finito y condición variacional).* Homogeneidad de grado $theta = 1 + r$ da $F_A (overline(L) tilde(K), overline(L)) = overline(L) F_(A overline(L)^r) (tilde(K), 1)$ y $eta log(overline(L) tilde(C)_t) = eta log tilde(C)_t + eta log overline(L)$, estableciendo el isomorfismo finito exacto. Por el Teorema 1, en $K_0 = S_A$ coexisten un óptimo productivo $pi^+$ y uno extinto que alcanzan $V_A (S_A)$. Evaluar $pi^+$ con $L equiv 1$ (sin desutilidad de ocio) es factible en trabajo fijo y eleva su bienestar en $Delta W_A^+ > 0$, luego $V_A^("fix") (S_A; 1) >= J_A^("fix") (pi^+ |_(L=1)) = V_A (S_A) + Delta W_A^+$. Inversamente, supóngase $S_A^("fix") (1) >= S_A$: existiría entonces un óptimo extinto estrictamente decreciente $pi^- = (C_t^("f"), K_(t+1)^("f"))_(t>=0)$ en trabajo fijo con $K_t^("f") <= S_A <= c_+ A^(-1\/r)$ para todo $t >= 0$. Equipando esta trayectoria de capital con esfuerzo $tilde(L)_t = c_0 A^(-d\/[r(1+d)])$ y consumiendo $tilde(C)_t = C_t^("f") - [F_A (K_t^("f"), 1) - F_A (K_t^("f"), tilde(L)_t)]$, la Proposición 4 aplicada al problema fijo ($C_t^("f") >= chi_p^("fix") K_t^("f")$) garantiza:
  $ (F_A (K_t^("f"), 1) - F_A (K_t^("f"), tilde(L)_t)) / C_t^("f") <= C_1 A (K_t^("f"))^r (K_t^("f") / tilde(L)_t)^d = O(A^(- d / (r(1+d)))), $
  idéntico orden que $(1 - eta)|log(1 - tilde(L)_t)| = O(tilde(L)_t)$. Sumando con descuento $beta$, $V_A (S_A) >= J_A^("endo") (pi^- |_(tilde(L))) >= J_A^("fix") (pi^-) - C_2 A^(-d\/[r(1+d)])$, luego $Delta W_A^- = O(A^(-d\/[r(1+d)]))$. Si $Delta W_A^+ > Delta W_A^-$, $J_A^("fix") (pi^+ |_(L=1)) > sup_(cal(O)_(-)^("fix")) J_A^("fix") (pi^-)$, descartando la extinción óptima en $S_A$ e implicando $S_A^("fix") (1) < S_A$.
]

== Verificación numérica de la condición de primer orden y de fronteras (VFI)

La Figura 2 y la Tabla 3 distinguen explícitamente entre dos niveles complementarios de verificación en el modelo CES armónico ($theta = 3\/2, d = 1, r = 1\/2, beta = 0.97, q = 0.92, eta = 0.70$) para $A in [0.75, 100]$: (i) la evaluación exacta de la condición de primer orden del trabajo $L^*_A$ en el punto de referencia reescalado $(k, c) = (0.002, 0.0001)$, donde $A dot L^*_A$ converge hacia la constante teórica $0.133074$ mientras el costo de ocio y la brecha relativa de producto decaen como $O(A^(-1))$; y (ii) la *resolución directa de la ecuación de Bellman normalizada (VFI)* con interpolación continua sobre una malla de dos zonas de $880$ puntos en $k = A^2 K$, comparando explícitamente las fronteras verdaderas de supervivencia $A^2 S_A^("fix") (1)$ y $A^2 S_A^("endo")$. Se verifica numéricamente en todo el rango $A in [0.75, 100]$ que $S_A^("fix") (1) < S_A^("endo")$ (de acuerdo con el criterio variacional de la Parte 2, donde el excedente productivo VFI permanece en $Delta W_A^+ in [3.20, 9.73]$) y que el cociente de fronteras $S_A^("endo") \/ S_A^("fix") (1)$ converge monótonamente hacia $1$ ($1.02078$ en $A = 0.75$ hasta $1.00198$ en $A = 100$). Nótese además que la aproximación conjunta de $A^2 S_A$ hacia el límite físico $(delta\/c_K)^2 = 0.000800$ se produce a ritmo ultralentamente logarítmico $O(1\/log log A)$ debido al factor $beta theta = 1.455 > 1$, alcanzando $0.000847$ en $A = 10^3$ y $0.000834$ en $A = 10^8$.

#figure(
  image("fig2_scaling_es.svg", width: 100%),
  caption: [Escalamiento asintótico y resolución numérica de fronteras para la Nota al pie 1 ($theta = 3\/2, d = 1, r = 1\/2$). El Panel (a) muestra la banda entre $kappa_A$ y las cotas superiores de $S_A$ ($A^(-2)$); el Panel (b) combina las magnitudes FOC exactas en $(k, c) = (0.002, 0.0001)$ (decaimiento en $A^(-1)$ y $A^(-2)$) con la brecha relativa de fronteras $S_A^("endo")\/S_A^("fix") (1) - 1 -> 0$ calculada directamente por VFI.],
)

#v(0.2em)
#figure(
  text(size: 8.2pt, table(
    columns: (0.55fr, 1.15fr, 0.85fr, 1.15fr, 0.8fr, 0.85fr, 0.95fr, 0.95fr, 1.0fr),
    align: (center, center, center, center, center, center, center, center, center),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [$A$], [$kappa_A$], [$A^2 kappa_A$], [$L^*_A$ \ $(k, c)$], [$A L^*_A$], [Brecha $F_A$], [$A^2 S_A^("fix") (1)$ \ (VFI)], [$A^2 S_A^("endo")$ \ (VFI)], [$S_A^("endo") \/ S_A^("fix") (1)$ \ (VFI)],
    table.hline(stroke: 0.6pt),
    [$0.75$], [$1.428 times 10^(-3)$], [$0.000803$], [$1.583 times 10^(-1)$], [$0.11874$], [$3.276\%$], [$0.000875$], [$0.000893$], [*$1.02078$*],
    [$1.50$], [$3.559 times 10^(-4)$], [$0.000801$], [$8.381 times 10^(-2)$], [$0.12571$], [$1.570\%$], [$0.000867$], [$0.000877$], [*$1.01183$*],
    [$3.00$], [$8.891 times 10^(-5)$], [$0.000800$], [$4.311 times 10^(-2)$], [$0.12934$], [$0.768\%$], [$0.000863$], [$0.000869$], [*$1.00717$*],
    [$10.0$], [$8.000 times 10^(-6)$], [$0.000800$], [$1.319 times 10^(-2)$], [$0.13194$], [$0.227\%$], [$0.000858$], [$0.000861$], [*$1.00371$*],
    [$30.0$], [$8.889 times 10^(-7)$], [$0.000800$], [$4.423 times 10^(-3)$], [$0.13270$], [$0.075\%$], [$0.000855$], [$0.000857$], [*$1.00255$*],
    [$100.0$], [$8.000 times 10^(-8)$], [$0.000800$], [$1.330 times 10^(-3)$], [$0.13296$], [$0.023\%$], [$0.000852$], [$0.000853$], [*$1.00198$*],
    table.hline(stroke: 0.6pt),
    [$-> infinity$], [$-> 0$], [*$0.000800$*], [$-> 0$], [*$0.133074$*], [*$0\%$*], [*$0.000800$*], [*$0.000800$*], [*$1.00000$*],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Verificación numérica combinada del Teorema 3\* en el modelo CES armónico: columnas 2–6 en el punto FOC $(k, c) = (0.002, 0.0001)$ y columnas 7–9 mediante resolución VFI directa de ambas fronteras de supervivencia ($c_K = 2 sqrt(2)$, $(delta\/c_K)^2 = 0.000800$).],
)

= Regulación, Impuestos e Infraestructura Pública: La Curva en U Institucional

== Microfundación Barro–CES y el Teorema 10

En la Sección 4.3 de Milei y Reidel (2026), los autores estudian una pérdida permanente de eficiencia productiva de la forma $A_e = (1 - tau) A$ con $tau in (0, 1)$, probando en la Proposición 2 que el intervalo sostenible $[kappa(A_e), K^+(A_e)]$ se contrae monótonamente con $tau$ y colapsa al conjunto vacío cuando $tau > tau^* := 1 - A_("rep")\/A$. El artículo académico advierte explícitamente en su página 10 que aplicar dicho experimento a impuestos o regulaciones exige contabilizar los recursos devueltos y los beneficios productivos de las instituciones o bienes públicos.

Para cerrar analíticamente esa brecha sin abandonar la tratabilidad exacta del modelo de un sector, incorporemos el canal institucional clásico de Barro (1990) con presupuesto público equilibrado período a período. Supongamos que el Estado recauda una alícuota total $tau = tau_p + tau_u in (0, 1)$ sobre el producto bruto $Y_t$, destinando $G_t = tau_p Y_t$ a infraestructura pública, justicia y protección de derechos de propiedad, mientras que $tau_u Y_t$ representa gasto improductivo o costo regulatorio puro de cumplimiento. Si el flujo de bienes públicos productivos $G_t$ entra en la tecnología agregada con elasticidad $gamma in (0, 1)$ junto con el agregador privado CES de grado $theta_0$:
$ Y_t = tilde(A)_0 G_t^gamma [w K_t^rho + (1 - w) L_t^rho]^(theta_0 / rho), quad G_t = tau_p Y_t, $
al sustituir $G_t = tau_p Y_t$ y despejar $Y_t$, el ingreso privado neto disponible para consumo e inversión $(1 - tau_p - tau_u) Y_t$ toma *exactamente la forma funcional (2.1) de Milei y Reidel (2026)*:
$ Y_t^("priv") = (1 - tau_p - tau_u) Y_t = A_e (tau_p, tau_u) [w K_t^rho + (1 - w) L_t^rho]^(theta / rho), $
donde el exponente de escala efectivo es $theta := theta_0 \/ (1 - gamma)$, la elasticidad institucional inducida es $alpha := gamma \/ (1 - gamma) > 0$, la productividad base es $A_0 := tilde(A)_0^(1\/(1-gamma))$ y la productividad efectiva neta resulta:
$ A_e (tau_p, tau_u) = A_0 tau_p^alpha (1 - tau_p - tau_u) quad ("y en ausencia de peso muerto " tau_u = 0, quad A_e (tau) = A_0 tau^alpha (1 - tau)). $
Notablemente, esta microfundación explica además el origen de los rendimientos crecientes agregados ($theta > 1$): aun cuando la tecnología privada exhiba rendimientos constantes a escala ($theta_0 = 1$), la retroalimentación fiscal de la infraestructura pública ($gamma in (0, 1\/2)$) genera endógenamente $theta = 1\/(1 - gamma) in (1, 2)$.

Dado que $A_e (tau)$ actúa como un escalar multiplicativo puro sobre la tecnología CES (2.1), *todos* los resultados estructurales de Milei y Reidel (2026) —la Proposición 1, el Teorema 1, el Teorema 2 y el Teorema 3— se transfieren de forma exacta componiéndolos con la función unimodal $A_e (tau)$.

#thm_box([Teorema 10 (Curva en U institucional de cotas certificadas, simetría y límite de $S(tau)$)])[
  Sea una economía con productividad efectiva $A_e (tau) = A_0 tau^alpha (1 - tau)$, donde $alpha > 0$ y los seis parámetros restantes cumplen la condición de paciencia (2.3). Defina la carga institucional óptima:
  $ tau^* = alpha / (1 + alpha) in (0, 1), quad A_(max) := A_e (tau^*) = A_0 alpha^alpha / (1 + alpha)^(1 + alpha). $
  1. *Doble umbral de extinción física (Anarquía vs. Hiper-regulación):* Si $A_(max) > A_("rep")$, existen exactamente dos cargas críticas $0 < tau_(min) < tau^* < tau_(max) < 1$, raíces únicas de $tau^alpha (1 - tau) = A_("rep") \/ A_0$, tales que:
     - Para $tau in (0, tau_(min))$ (*trampa de anarquía / déficit institucional*) y para $tau in (tau_(max), 1)$ (*trampa de confiscación / sobre-regulación*), el conjunto físicamente sostenible es vacío ($cal(M)(tau) = emptyset$) y toda historia factible se extingue geométricamente: $K_t <= [q + A_e (tau) H_a]^t K_0 -> 0$.
     - Para $tau in (tau_(min), tau_(max))$, el intervalo sostenible $[kappa(tau), K^+(tau)]$ es no vacío, alcanza su amplitud máxima en $tau = tau^*$, y $kappa(tau)$ describe una curva en U diferenciable exacta con mínimo global único en $tau^*$ ($partial log kappa(tau)\/partial tau < 0$ para $tau < tau^*$ y $> 0$ para $tau > tau^*$).
  2. *Distinción entre la envolvente certificada $overline(S)(tau)$ y la frontera verdadera $S(tau)$:* Si $A_(max) > A_*$, sea $(tau_1, tau_2) subset (tau_(min), tau_(max))$ el intervalo abierto donde $A_e (tau) > A_*$, en el cual existe una única frontera continua $S(tau) > kappa(tau)$. Como advierten Milei y Reidel (2026, págs. 10 y 20), la relación $S_A = Theta(A^(-1\/(theta-1)))$ proporciona cotas de orden pero no implica por sí sola diferenciabilidad ni monotonicidad de $S(tau)$ a $A_0$ finito. Separando ambos niveles:
     - *(a) Curva en U exacta de la cota superior certificada $overline(S)(tau)$:* Toda cota superior escalada de forma $overline(S)(tau) := overline(c)_+ [A_e (tau)]^(-1\/(theta - 1))$ (en particular la envolvente de referencia del Teorema 3 con $overline(c)_+ = (D\/c_K)^(1\/(theta-1))$ tabulada en la Tabla 4, o la cota explícita del Teorema 8 con $overline(c)_+ = (.0014025025)^(1\/2)$ donde $A_e (tau) >= 0.749$) describe una curva diferenciable y estrictamente convexa en U sobre $(tau_1, tau_2)$ con mínimo único en $tau^* = alpha\/(1+alpha)$ y derivada logarítmica cerrada exacta:
       $ partial / (partial tau) log overline(S)(tau) = - 1 / (theta - 1) [ alpha / tau - 1 / (1 - tau) ] = (tau - tau^*) / ((theta - 1)(1 - tau^*) tau (1 - tau)). $
     - *(b) Simetría de conjuntos de nivel de la frontera verdadera $S(tau)$ a todo $A_0$ finito:* Como $S(tau) = S_(A_e (tau))$ depende de $tau$ únicamente mediante el escalar unimodal $A_e (tau)$, todo $tau_- in (tau_1, tau^*)$ posee un único conjugado $tau_+ in (tau^*, tau_2)$ con $A_e (tau_-) = A_e (tau_+)$ donde las fronteras coinciden exactamente ($S(tau_-) = S(tau_+)$), manteniéndose la banda en forma de U $kappa(tau) < S(tau) < 1.798 kappa(tau)$ sobre el dominio del Teorema 8.
     - *(c) Curva en U asintótica exacta de $S(tau)$ ($A_0 -> infinity$):* Por el Teorema 3\* ($lim_(A -> infinity) A^(1\/(theta-1)) S_A = s_infinity^* := (delta\/c_K)^(1\/(theta-1))$), la frontera verdadera reescalada converge uniformemente sobre subconjuntos compactos de $(0, 1)$ al perfil diferenciable exacto:
       $ lim_(A_0 -> infinity) A_0^(1/(theta-1)) S(tau) = s_infinity^* [tau^alpha (1 - tau)]^(-1/(theta-1)), $
       cuyo único mínimo global ocurre exactamente en la tasa óptima de Barro $tau^* = alpha\/(1 + alpha)$.
]

#proof_block[
  La función $g(tau) = tau^alpha (1 - tau)$ es estrictamente log-cóncava sobre $(0, 1)$, con derivada logarítmica $g'(tau)\/g(tau) = alpha\/tau - 1\/(1 - tau) = (tau^* - tau)\/[(1 - tau^*) tau (1 - tau)]$. Por ende, $g(tau)$ crece estrictamente en $(0, tau^*)$, alcanza su único máximo global en $tau^* = alpha\/(1+alpha)$ y decrece estrictamente en $(tau^*, 1)$, anulándose en ambos extremos. Si $A_(max) = A_0 g(tau^*) > A_("rep")$, el teorema del valor intermedio garantiza dos raíces únicas $tau_(min) in (0, tau^*)$ y $tau_(max) in (tau^*, 1)$ de $A_e (tau) = A_("rep")$. Aplicando la Proposición 1 de Milei y Reidel a $A = A_e (tau)$ resulta el punto 1, cuya diferenciación implícita exacta en la ecuación (4.2) original da:
  $ (partial log kappa(tau)) / (partial tau) = - 1 / (theta s(kappa(tau)) - 1) (partial log A_e (tau)) / (partial tau) = (tau - tau^*) / ([theta s(kappa(tau)) - 1](1 - tau^*) tau (1 - tau)), $
  negativa en $(tau_(min), tau^*)$ y positiva en $(tau^*, tau_(max))$ porque $theta s(kappa) - 1 > 0$. Para el punto 2(a), derivar $log overline(S)(tau) = log overline(c)_+ - (theta - 1)^(-1) log A_e (tau)$ entrega inmediatamente la identidad diferencial exacta y estricta log-convexidad en $tau$ (con segunda derivada $> 0$). Para 2(b), la unimodalidad estricta de $A_e (tau)$ garantiza dos preimágenes únicas para cada nivel $A in (A_*, A_(max))$ y transfiere el Teorema 8 cuando $A_e (tau) >= 0.749$. Para 2(c), sustituyendo $A = A_0 tau^alpha (1 - tau)$ en el límite $A^(1\/(theta-1)) S_A -> (delta\/c_K)^(1\/(theta-1))$ probado en el Teorema 3\* se obtiene la convergencia uniforme sobre cualquier compacto $[underline(tau), overline(tau)] subset (0, 1)$ hacia la curva en U asintótica exacta.
]

== Descomposición entre gasto productivo ($tau_p$) y carga improductiva ($tau_u$)

El Teorema 10 reconcilia formalmente la matemática de Milei y Reidel (2026) con el debate de política económica sobre el tamaño óptimo del Estado. Si la carga agregada se descompone en $tau = tau_p + tau_u in (0, 1)$, donde $tau_p > 0$ financia bienes públicos productivos ($tau_p^alpha$) y $tau_u in lr([0, 1 - tau_p))$ representa gasto improductivo o costo regulatorio puro de cumplimiento (burocracia sin contrapartida productiva), la productividad efectiva neta adopta la forma bivariada $A_e (tau_p, tau_u) = A_0 tau_p^alpha (1 - tau_p - tau_u)$, de donde se desprenden dos leyes complementarias:

1. *Monotonía frente a la carga improductiva $tau_u$:* Para cualquier nivel dado de provisión institucional $tau_p$, se verifica $partial A_e \/ partial tau_u = -A_0 tau_p^alpha < 0$, lo que contrae monótonamente el conjunto sostenible ($partial kappa \/ partial tau_u > 0$ y $partial overline(S) \/ partial tau_u > 0$ *en todo punto*, y en el límite $A_0 -> infinity$ también $partial S \/ partial tau_u > 0$), recuperando la Proposición 2 de Milei y Reidel (2026) sobre la dimensión $tau_u$.
2. *Curva en U y efecto desplazamiento (crowding-out) sobre la dimensión productiva $tau_p$:* Para cada $tau_u in lr([0, 1))$ fijo, la alícuota productiva que maximiza $A_e (tau_p, tau_u)$ y minimiza tanto $kappa(tau_p, tau_u)$ como $overline(S)(tau_p, tau_u)$ es $tau_p^* (tau_u) = frac(alpha, 1 + alpha) (1 - tau_u)$, donde la productividad máxima escala como $A_e^* (tau_u) prop (1 - tau_u)^(1 + alpha)$ y la envolvente mínima certificada crece como $overline(S)^* (tau_u) = overline(c)_+ A_e^* (tau_u)^(-1\/(theta - 1)) prop (1 - tau_u)^(-(1+alpha)\/(theta-1))$. Así, recortar burocracia improductiva $tau_u$ o exceso fiscal ($tau_p > tau_p^*$) abate drásticamente las barreras de viabilidad, mientras en la rama izquierda ($tau_p < tau_p^*$) la infraestructura y los derechos de propiedad evitan la trampa de anarquía.

#figure(
  image("fig3_ucurve_es.svg", width: 100%),
  caption: [Extensión institucional de la Sección 4.3 ($A_e (tau) = A_0 tau^alpha (1 - tau)$ con $A_0 = 1.45, alpha = 0.25, tau^* = 0.20, A_("rep") = 0.0735$). El Panel (a) contrasta la productividad neta con infraestructura pública frente a la pérdida lineal pura $A(1-tau)$ y ubica las dos raíces críticas de extinción ($tau_(min) = 6.60 times 10^(-6)$ y $tau_(max) = 0.9486$); el Panel (b) muestra la curva en U exacta resultante para el umbral físico $kappa(tau)$ y la cota superior certificada $overline(S)(tau) = (D\/c_K)^2 A_e (tau)^(-2)$.],
)

#v(0.2em)
#figure(
  table(
    columns: (0.9fr, 1.0fr, 1.0fr, 1.15fr, 1.2fr, 1.7fr),
    align: (center, center, center, center, center, left),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [Carga $tau$], [$A_e (tau)$], [$A_e (tau) \/ A_("rep")$], [$kappa(tau)$], [Cota $overline(S)(tau)$], [Régimen institucional],
    table.hline(stroke: 0.6pt),
    [$5.0 times 10^(-6)$], [$0.0685$], [$0.93$], [—], [—], [Extinción (trampa de anarquía)],
    [$2.0 times 10^(-5)$], [$0.0970$], [$1.32$], [$0.119322$], [$0.163590$], [Borde de anarquía ($tau > tau_(min)$)],
    [$0.02$], [$0.5344$], [$7.27$], [$0.002825$], [$0.005386$], [Rama izquierda (provisión subóptima)],
    [$0.05$], [$0.6514$], [$8.86$], [$0.001896$], [$0.003625$], [Expansión de infraestructura],
    [$0.10$], [$0.7339$], [$9.99$], [$0.001492$], [$0.002856$], [Cercano al óptimo institucional],
    [*$0.20$ ($tau^*$)*], [*$0.7757$*], [*$10.56$*], [*$0.001335$*], [*$0.002556$*], [*Carga óptima única (mínimo de $overline(S), kappa$)*],
    [$0.40$], [$0.6919$], [$9.42$], [$0.001680$], [$0.003213$], [Rama derecha (sobrecarga fiscal)],
    [$0.60$], [$0.5105$], [$6.95$], [$0.003099$], [$0.005903$], [Fuerte contracción sostenible],
    [$0.80$], [$0.2743$], [$3.73$], [$0.010990$], [$0.020448$], [Deterioro severo de viabilidad],
    [$0.90$], [$0.1412$], [$1.92$], [$0.045887$], [$0.077114$], [Antesala de colapso],
    [$0.94$], [$0.0857$], [$1.17$], [$0.178378$], [$0.209599$], [Borde de sobrerregulación ($tau < tau_(max)$)],
    [$0.95$], [$0.0716$], [$0.97$], [—], [—], [Extinción (hiperregulación)],
    table.hline(stroke: 1.1pt),
  ),
  caption: [Cuantificación de los regímenes institucionales del Teorema 10 en el modelo CES armónico ($A_0 = 1.45, alpha = 0.25, A_("rep") = 0.073485, tau_(min) = 6.60 times 10^(-6), tau_(max) = 0.948649$). La columna 5 reporta la envolvente escalada $overline(S)(tau) = (D\/c_K)^2 A_e (tau)^(-2)$ (dominada además por $0.0014025025 thin A_e (tau)^(-2) = 0.002331$ en $tau^*$ donde $A_e >= 0.749$ por el Teorema 8).],
)

= Extensiones Estructurales: Descentralización Empresarial, Crecimiento Sostenido y Barreras Estocásticas

Mientras que las discusiones de política económica en torno a la escala mínima viable enfatizan el rol de las grandes empresas, las leyes antimonopolio, el crecimiento exponencial de largo plazo («palo de hockey») y las crisis macroeconómicas, el modelo matemático base de Milei y Reidel (2026) se formula para un planificador central determinista acotado por un techo estacionario $K_p^+$. Demostramos a continuación cómo incorporar formalmente estas tres dimensiones preservando de manera exacta sus teoremas y certificados.

== Descentralización, poder de mercado y el costo de fragmentar empresas

Con rendimientos crecientes a escala $theta in (1, 2)$, el Teorema de Euler implica $K F_(A,K) + L F_(A,L) = theta F_A (K, L) > F_A (K, L)$, por lo que firmas tomadoras de precios en competencia perfecta sin externalidades incurrirían en pérdidas operativas $(1 - theta) Y_t < 0$. Existen dos descentralizaciones canónicas compatibles con la tecnología CES (2.1): (i) *competencia monopolística u oligopolio simétrico* (Dixit y Stiglitz, 1977) con margen de precios (*markup*) $mu >= theta > 1$, donde cada firma remunera a los factores según $r_t = (1\/mu) F_(A,K)$ y $w_t = (1\/mu) F_(A,L)$ y la fracción restante $(1 - theta\/mu) Y_t >= 0$ cubre costos fijos operativos de intermediación y entrada; o bien (ii) *externalidades agregadas de escala* (Romer, 1986), donde cada firma opera con rendimientos constantes sobre sus insumos privados y productividad externa dada por la escala agregada.

#thm_box("Proposición 2* (Descentralización con escala empresarial, contabilidad factorial y fragmentación)")[
  Bajo la tecnología CES (2.1) con $theta in (1, 2)$ y $r = theta - 1 > 0$:
  1. *Teorema de fragmentación regulatoria o antimonopolio:* Si una regulación o intervención estatal fragmenta los insumos agregados $(K_t, L_t)$ en $M >= 1$ empresas simétricas aisladas ($K_(i,t) = K_t \/ M$, $L_(i,t) = L_t \/ M$), el producto agregado se contrae exactamente como:
  $ Y_t^((M)) = sum_(i=1)^M F_A (K_t / M, L_t / M) = M dot M^(-theta) F_A (K_t, L_t) = F_(A \/ M^r) (K_t, L_t). $
  En consecuencia, fragmentar la escala empresarial en $M$ unidades es *matemáticamente isomorfo* a destruir la productividad total de los factores a $A_("ef") (M) = A \/ M^(theta - 1)$, lo que multiplica la Escala Mínima Viable por un factor $M$ en el régimen asintótico ($S_A (M) = Theta(M dot S_A)$) y provoca la extinción global de la economía ($cal(M)(M) = emptyset$) siempre que $M >= (A \/ A_("rep"))^(1\/(theta - 1))$.
  2. *Contabilidad exacta y brecha de subinversión en el equilibrio descentralizado:* Si las firmas remuneran los factores a $r_t = (1\/mu) F_(A,K)$ y $w_t = (1\/mu) F_(A,L)$ bajo competencia monopolística con margen $mu >= theta > 1$, por el Teorema de Euler el ingreso factorial agregado percibido por los hogares asciende exactamente a:
  $ r_t K_t + w_t L_t = theta / mu F_A (K_t, L_t) = F_(A_("mkt")) (K_t, L_t), quad A_("mkt") := theta / mu A <= A. $
  - *(Cierre con costos fijos operativos / libre entrada):* Cuando la participación residual $(1 - theta\/mu) Y_t >= 0$ cubre costos fijos de operación y entrada (beneficios netos nulos), el problema de acumulación del hogar representativo es exactamente isomorfo al operador de Bellman de Milei y Reidel con productividad efectiva $A_("mkt") = (theta\/mu) A$, induciendo para todo $mu > theta$ la trampa de coordinación descentralizada $lr([S_A, S_((theta\/mu) A)))$.
  - *(Cierre con reembolso de beneficios puros):* Si $(1 - theta\/mu) Y_t$ se distribuye como transferencia de suma fija (*lump-sum*) a los hogares, la restricción de recursos agregados conserva $F_A (K_t, L_t)$, pero las condiciones privadas de Euler e intratemporal de oferta laboral enfrentan precios factoriales reducidos en el factor $1\/mu < 1\/theta$, deprimiendo el retorno privado del ahorro y elevando el umbral de supervivencia por encima de $S_A$.
]

#proof_block[
  Por homogeneidad de grado $theta = 1 + r$ de $F_A (K, L) = A [w K^rho + (1 - w) L^rho]^(theta\/rho)$, se verifica $F_A (K\/M, L\/M) = M^(-theta) F_A (K, L)$. Sumando sobre las $M$ firmas se obtiene $Y_t^((M)) = M^(1-theta) F_A (K, L) = F_(A M^(-r)) (K, L)$. Aplicando la Proposición 1 y el Teorema 3 de Milei y Reidel a $tilde(A) = A M^(-r)$, el conjunto sostenible es vacío si y solo si $A M^(-r) <= A_("rep")$, y el umbral crítico escala como $S_(tilde(A)) = Theta(tilde(A)^(-1\/r)) = M dot Theta(A^(-1\/r))$. Por su parte, la identidad de Euler $K F_(A,K) + L F_(A,L) = theta F_A (K, L)$ garantiza que los pagos factoriales suman $(theta\/mu) F_A (K_t, L_t) = F_((theta\/mu)A) (K_t, L_t)$. Bajo costos fijos operativos que agotan $(1 - theta\/mu) Y_t$, la restricción presupuestaria del hogar coincide exactamente con la del planificador en $A_("mkt") = (theta\/mu) A < A$ siempre que $mu > theta$, generando la brecha $S_((theta\/mu) A) > S_A$; bajo reembolso de suma fija $Pi_t = (1 - theta\/mu) Y_t$, las cuñas marginales $(1\/mu)$ en $r_t$ y $w_t$ distorsionan las decisiones privadas de ahorro y trabajo en la misma dirección subóptima respecto del óptimo social.
]

== Eliminación del techo estacionario $K_p^+$ y el «palo de hockey» del crecimiento sostenido

En el modelo base de Milei y Reidel, la cota laboral $L_t <= 1$ y la complementariedad bruta $rho < 0$ imponen una asíntota horizontal al producto $F_A (K, 1) < A (1 - w)^(theta\/rho)$, generando un techo estacionario $K_p^+ < infinity$. La siguiente proposición muestra que al incorporar progreso técnico aumentador de trabajo a tasa $g > 0$ (o aprendizaje *learning-by-doing* en la región productiva $H$), se elimina el techo $K_p^+$ y se obtiene crecimiento exponencial perpetuo («palo de hockey») *sin modificar una sola prueba ni constante verificada del paper original*.

#thm_box("Proposición 3* (Isomorfismo de crecimiento balanceado y despegue exponencial sin techo)")[
  Sea una economía con progreso técnico aumentador de trabajo $E_t = (1 + g)^t$ ($g > 0$) y tecnología homogénea de grado $1$ en $(K_t, E_t)$:
  $ Y_t = (1 + g)^t F_A ( K_t / (1 + g)^t, L_t ) = A (1 + g)^((1 - theta) t) [w K_t^rho + (1 - w) ((1 + g)^t L_t)^rho]^(theta / rho). $
  Definiendo las variables en unidades de eficiencia $hat(K)_t = K_t \/ (1 + g)^t$ y $tilde(C)_t = C_t \/ (1 + g)^(t+1)$, la ley de acumulación se reduce exactamente a:
  $ tilde(C)_t + hat(K)_(t+1) <= tilde(q) hat(K)_t + F_(tilde(A)) (hat(K)_t, L_t), quad tilde(q) := q / (1 + g), quad tilde(A) := A / (1 + g), $
  mientras que la utilidad de período difiere de $u(tilde(C)_t, L_t)$ únicamente en una constante aditiva $eta [(t + 1) log(1 + g)]$ independiente de la política elegida. En consecuencia:
  1. El problema dinámico en $(hat(K)_t, tilde(C)_t, L_t)$ es *100% idéntico* al modelo de Milei y Reidel con parámetros $(tilde(A), beta, tilde(q), eta, theta, rho, w)$, existiendo una única frontera relativa $hat(S)_p > hat(kappa)_p$.
  2. Si $K_0 < hat(S)_p$, la economía cae en la trampa de liquidación ($hat(K)_t -> 0$). Si $K_0 > hat(S)_p$, $hat(K)_t$ ingresa en tiempo finito (en a lo sumo $tau_H <= 23$ períodos desde $M$ si $(tilde(A), beta, tilde(q), eta)$ pertenece a la caja 7.3) a la banda productiva $hat(H) = lr([hat(h), hat(K)_p^+])$ de $(0, infinity)$, lo que en niveles reales implica que *el capital y el producto crecen exponencialmente sin techo para siempre*:
  $ K_t = (1 + g)^t hat(K)_t >= (1 + g)^t hat(h) -> infinity quad (t -> infinity). $
]

#proof_block[
  Dividiendo la restricción física $C_t + K_(t+1) <= q K_t + (1 + g)^t F_A (K_t \/ (1 + g)^t, L_t)$ por $(1 + g)^(t+1)$ se obtiene de inmediato $tilde(C)_t + hat(K)_(t+1) <= tilde(q) hat(K)_t + F_(tilde(A)) (hat(K)_t, L_t)$. Dado que $sum_(t=0)^infinity beta^t eta (t + 1) log(1 + g) < infinity$ es constante respecto de las decisiones $(hat(K)_(t+1), L_t)$, el conjunto de trayectorias óptimas de $hat(K)_t$ coincide punto por punto con el del modelo estacionario de parámetros $(tilde(A), tilde(q))$.#footnote[De manera alternativa y puramente endógena, si el factor trabajo eficiente es $H_t L_t$ con conocimiento $H_t = 1$ para $K_t < h$ (etapa pre-industrial) y derrame de aprendizaje $H_t = K_t \/ h$ con tecnología linealizada en $H = lr([h, infinity))$ al cruzar el umbral industrial $h$ (Romer, 1986), toda la geometría de la trampa de extinción y del tránsito en $M = lr([b, h))$ permanece inalterada, mientras que el ingreso a $H$ activa un régimen $A K$ de crecimiento endógeno perpetuo.]
]

== Incertidumbre macroeconómica y Barreras de Bellman Estocásticas (Teorema de Doob)

Una ventaja metodológica fundamental de las *Barreras de Bellman de Primer Paso (FPBB)* de la Sección 6 de Milei y Reidel (2026) frente a las pruebas deterministas clásicas de Dechert y Nishimura (1983) es que las desigualdades de barrera se extienden naturalmente a entornos estocásticos mediante la teoría de martingalas y el *Teorema de Parada Opcional de Doob* (Doob, 1953).

#thm_box("Teorema 11 (Barreras de Bellman Estocásticas y probabilidad de supervivencia en tránsito)")[
  Sea $(omega_t)_(t>=0)$ un proceso de shocks macroeconómicos Markovianos sobre un espacio $(Omega, cal(F), bb(P))$ que afecta los parámetros primitivos en cada período, bajo la condición de integrabilidad $sup_(t <= T) bb(E)[ |V(K_(t and tau), omega_(t and tau))| ] < infinity$ para todo horizonte finito $T >= 1$.
  1. *Certificado de Supermartingala (Stochastic FPBB):* Si una función medible y acotada $B : M times Omega -> bb(R)$ sobre la región de tránsito $M = lr([b, h))$ satisface para toda acción de permanencia en $M$:
  $ B(K, omega) >= r(K, omega, a) + beta bb(E) [ B(K', omega') | K, omega, a ], $
  y toda historia de bienestar finito en $M$ satisface $bb(E)[sum_(j=0)^(t-1) beta^j |r_j| ] < infinity$, entonces a lo largo de toda política que permanece en $M$ hasta el tiempo de parada $tau = inf{t >= 0 : K_t in.not M}$, el proceso $Z_t := beta^t B(K_t, omega_t) + sum_(j=0)^(t-1) beta^j r_j$ es una *supermartingala* respecto de la filtración natural $cal(F)_t$. Por el Teorema de Parada Opcional de Doob, para todo horizonte $T >= 1$:
  $ bb(E)_(x_0, omega_0) [J(pi)] <= B(x_0, omega_0) + bb(E)_(x_0, omega_0) [ beta^(T and tau) ( V(K_(T and tau), omega_(T and tau)) - B(K_(T and tau), omega_(T and tau)) ) ]. $
  2. *Exposición al riesgo de régimen durante la transición y el valor de reducir $tau_H$ a la mitad:* Supongamos un núcleo Markoviano híbrido sobre $M = lr([0.10, 0.28))$ tal que en cada período $t$, condicional en $cal(F)_(t-1)$: (i) con probabilidad al menos $1 - p$ ($p in (0, 1)$), la realización $omega_t$ mantiene los parámetros dentro de la caja verificada (7.3) sin salto adverso exógeno de capital, por lo que la barrera afín determinista $B_1 (K)$ y las cotas uniformes de salida adversa de la Proposición 1\*\* rigen estado a estado y garantizan la entrada a $H = lr([0.28, infinity))$ en a lo sumo $T^* = 23$ períodos normales consecutivos; y (ii) con probabilidad a lo sumo $p$ ocurre un shock severo de destrucción de capital que desplaza el estado hacia la trampa de extinción $(0, S_p)$. Entonces la probabilidad de alcanzar con éxito $H$ antes de sufrir una crisis severa verifica:
  $ bb(P) ("Supervivencia hasta " H) >= (1 - p)^(T^*). $
  En particular, reducir mediante $B_1 (K)$ el horizonte crítico de $T^* = 46$ a *$T^* = 23$ períodos* eleva al cuadrado la cota mínima garantizada ($(1 - p)^23$ frente a $(1 - p)^46$), reduciendo casi a la mitad el riesgo acumulado de naufragio en tránsito para tasas de peligro bajas.
]

#proof_block[
  Por la desigualdad de un paso en esperanza condicional y las hipótesis de integrabilidad, $bb(E)[Z_(t+1) - Z_t | cal(F)_t] = beta^t { r(K_t, omega_t, a_t) + beta bb(E)[B(K_(t+1), omega_(t+1)) | cal(F)_t] - B(K_t, omega_t) } <= 0$ sobre ${tau > t}$, demostrando que $(Z_(t and tau))_(t>=0)$ es una supermartingala integrable respecto de $(cal(F)_t)$. Aplicando el Teorema de Parada Opcional de Doob en el tiempo de parada acotado $T and tau$ resulta $bb(E)[Z_(T and tau)] <= Z_0 = B(x_0, omega_0)$, y acotar la continuación desde $T and tau$ por $V(K_(T and tau), omega_(T and tau))$ (integrable por hipótesis) produce el punto 1. En el núcleo híbrido del punto 2, sobre el evento $E_(T^*) := inter.big_(t=1)^(T^*) {omega_t in "caja (7.3) sin shock severo"}$, cada paso pertenece al régimen determinista uniforme cubierto por el Teorema 9\* y la Proposición 1\*\*, por lo cual toda trayectoria óptima ingresa en $H$ dentro de los primeros $T^* = 23$ períodos; como $bb(P)(omega_t in "normal" | cal(F)_(t-1)) >= 1 - p$ para cada $t$, la regla de la cadena condicional da $bb(P)(E_(T^*)) >= (1 - p)^(T^*)$.
]

#figure(
  image("fig4_structural_es.svg", width: 100%),
  caption: [Extensiones estructurales del modelo. El Panel (a) ilustra el despegue exponencial sin techo («palo de hockey», $K_t = (1+g)^t hat(K)_t$) cuando las empresas operan a escala consolidada ($M = 1$) frente al colapso por fragmentación regulatoria ($M = 2$, $A_("ef") = A\/M^(theta-1)$); el Panel (b) muestra el aumento en la probabilidad certificada de supervivencia durante el tránsito en $M$ al reducir $tau_H$ de $46$ a $23$ períodos.],
)

= Conclusión

El trabajo _Minimum Viable Scale: Bellman Barriers and the Economics of Survival_ de Milei y Reidel (2026) introduce una estructura matemática rigurosa y original para analizar trampas de extinción y certificar trayectorias óptimas en modelos no cóncavos con trabajo endógeno. En este documento hemos desarrollado cuatro extensiones y refinamientos analíticos que responden sus preguntas abiertas principales, refuerzan los márgenes cuantitativos del certificado FPBB y amplían su alcance económico:

1. *Afilamiento completo del certificado FPBB (Sección 3):* Sin alterar un solo parámetro ni supuesto de la Sección 7.2, reemplazar la cota por pares disjuntos de la ecuación (7.6) por nuestra *barrera regional afín de un paso* ($B_1 (K)$ en el Lema 1 y el Teorema 9\*) casi triplica el margen de calibración en la región de tránsito ($> 7.4665$) y *reduce exactamente a la mitad el plazo máximo certificado de entrada* a la región productiva (de $46$ a *$23$ períodos*, y a $33$ períodos totales desde $K_0 = 0.05$ vía la Proposición 1\*). Complementariamente, el certificado analítico y de aritmética de intervalos de la Proposición 1\*\* excluye mínimos interiores y colapsa las doce particiones finitas de la Tabla 5 original a dos bordes, elevando el margen de salida adversa en $M$ a $> 0.0947$ y ampliando el margen global certificado del Teorema 9 de $0.0423$ ($0.04$) a *$> 0.0571$* ($+35\%$).
2. *Convergencia asintótica, criterio variacional e isomorfismo laboral (Sección 4):* El análisis en unidades críticas $K = A^(-1\/r) k$ junto con el isomorfismo exacto $S_A^("fix") (overline(L)) = overline(L) S_(A overline(L)^r)^("fix") (1)$ del Teorema 3\* resuelven la pregunta abierta de la Nota al pie 1: probamos bajo la condición de paciencia que ambas fronteras reescaladas convergen al límite físico común $(delta\/c_K)^(1\/r)$ ($S_A \/ S_A^("fix") (overline(L)) -> 1$), establecemos una condición variacional precisa para $S_A^("fix") (1) < S_A$, y verificamos numéricamente dicha convergencia de fronteras mediante VFI.
3. *Curva en U institucional y descomposición fiscal–regulatoria (Sección 5):* La microfundación con gasto público productivo endógeno ($G_t = tau_p Y_t$) y carga improductiva ($tau_u$) en la Sección 4.3 genera el Teorema 10, separando con rigor la curva en U diferenciable exacta del piso físico $kappa(tau)$ y de la envolvente certificada $overline(S)(tau)$ en $tau^* = alpha\/(1+alpha)$, la simetría por pares de la frontera verdadera $S(tau)$ a $A_0$ finito y su perfil asintótico límite cuando $A_0 -> infinity$, además de confirmar que reducir peso muerto $tau_u$ abate incondicionalmente las barreras de viabilidad.
4. *Descentralización, crecimiento perpetuo y barreras estocásticas (Sección 6):* Finalmente, formulamos la descentralización bajo competencia monopolística con contabilidad factorial consistente $(theta\/mu) Y_t$ y externalidades (mostrando que fragmentar empresas en $M$ unidades contrae la TFP como $A\/M^(theta-1)$), eliminamos el techo estacionario $K_p^+$ mediante unidades de eficiencia para generar crecimiento exponencial perpetuo, y extendemos las Barreras de Bellman al caso estocástico bajo condiciones explícitas de integrabilidad y régimen Markoviano mediante el Teorema de Parada Opcional de Doob.

= Referencias

#set par(first-line-indent: 0pt, hanging-indent: 1.5em)
- Acemoglu, D., S. Johnson, y J. A. Robinson (2005): «Institutions as a Fundamental Cause of Long-Run Growth», en P. Aghion y S. N. Durlauf (eds.), _Handbook of Economic Growth_, vol. 1A, cap. 6, pp. 385–472. Amsterdam: Elsevier.
- Akao, K., T. Kamihigashi, y K. Nishimura (2011): «Monotonicity and Continuity of the Critical Capital Stock in the Dechert–Nishimura Model», _Journal of Mathematical Economics_, 47(6), 677–682.
- Akao, K., H. Ishii, T. Kamihigashi, y K. Nishimura (2022): «Existence of an Optimal Path in a Continuous-Time Nonconcave Ramsey Model», _Pure and Applied Functional Analysis_, 7(6), 1939–1952.
- Arrow, K. J., H. B. Chenery, B. S. Minhas, y R. M. Solow (1961): «Capital-Labor Substitution and Economic Efficiency», _The Review of Economics and Statistics_, 43(3), 225–250.
- Azariadis, C., y A. Drazen (1990): «Threshold Externalities in Economic Development», _The Quarterly Journal of Economics_, 105(2), 501–526.
- Barro, R. J. (1990): «Government Spending in a Simple Model of Endogenous Growth», _Journal of Political Economy_, 98(5, Part 2), S103–S125.
- Bellman, R. (1957): _Dynamic Programming_. Princeton, NJ: Princeton University Press.
- Benhabib, J., y R. E. A. Farmer (1994): «Indeterminacy and Increasing Returns», _Journal of Economic Theory_, 63(1), 19–41.
- Bertsekas, D. P. (1972): «Infinite-Time Reachability of State-Space Regions by Using Feedback Control», _IEEE Transactions on Automatic Control_, 17(5), 604–613.
- Dechert, W. D., y K. Nishimura (1983): «A Complete Characterization of Optimal Growth Paths in an Aggregated Model with a Non-Concave Production Function», _Journal of Economic Theory_, 31(2), 332–354.
- de Hek, P. A. (1998): «An Aggregative Model of Capital Accumulation with Leisure-Dependent Utility», _Journal of Economic Dynamics and Control_, 23(2), 255–276.
- Dixit, A. K., y J. E. Stiglitz (1977): «Monopolistic Competition and Optimum Product Diversity», _American Economic Review_, 67(3), 297–308.
- Doob, J. L. (1953): _Stochastic Processes_. New York: John Wiley & Sons.
- Futagami, K., Y. Morita, y A. Shibata (1993): «Dynamic Analysis of an Endogenous Growth Model with Public Capital», _The Scandinavian Journal of Economics_, 95(4), 607–625.
- Gaitsgory, V., A. Parkinson, y I. Shvartsman (2019): «Linear Programming Based Optimality Conditions and Approximate Solution of a Deterministic Infinite Horizon Discounted Optimal Control Problem in Discrete Time», _Discrete and Continuous Dynamical Systems, Series B_, 24(4), 1743–1767.
- Galor, O., y J. Zeira (1993): «Income Distribution and Macroeconomics», _The Review of Economic Studies_, 60(1), 35–52.
- Garicano, L., C. Lelarge, y J. Van Reenen (2016): «Firm Size Distortions and the Productivity Distribution: Evidence from France», _American Economic Review_, 106(11), 3439–3479.
- Geiselhart, R., R. H. Gielen, M. Lazar, y F. R. Wirth (2014): «An Alternative Converse Lyapunov Theorem for Discrete-Time Systems», _Systems & Control Letters_, 70, 49–59.
- Grüne, L., M. A. Müller, C. M. Kellett, y S. R. Weller (2021): «Strict Dissipativity for Discrete Time Discounted Optimal Control Problems», _Mathematical Control and Related Fields_, 11(4), 771–796.
- Haugh, M. B., y L. Kogan (2004): «Pricing American Options: A Duality Approach», _Operations Research_, 52(2), 258–270.
- Hsieh, C.-T., y P. J. Klenow (2009): «Misallocation and Manufacturing TFP in China and India», _The Quarterly Journal of Economics_, 124(4), 1403–1448.
- Kamihigashi, T., y S. Roy (2007): «A Nonsmooth, Nonconvex Model of Optimal Growth», _Journal of Economic Theory_, 132(1), 435–460.
- Klump, R., P. McAdam, y A. Willman (2007): «Factor Substitution and Factor-Augmenting Technical Progress in the United States: A Normalized Supply-Side System Approach», _The Review of Economics and Statistics_, 89(1), 183–192.
- Kraay, A., y D. McKenzie (2014): «Do Poverty Traps Exist? Assessing the Evidence», _Journal of Economic Perspectives_, 28(3), 127–148.
- Majumdar, M., y T. Mitra (1982): «Intertemporal Allocation with a Non-Convex Technology: The Aggregative Framework», _Journal of Economic Theory_, 27(1), 101–136.
- Milei, J., y D. Reidel (2026): _Minimum Viable Scale: Bellman Barriers and the Economics of Survival_, Working Paper, Octubre 2026.
- Milgrom, P., y I. Segal (2002): «Envelope Theorems for Arbitrary Choice Sets», _Econometrica_, 70(2), 583–601.
- Mitra, T., y D. Ray (1984): «Dynamic Optimization on a Non-Convex Feasible Set: Some General Results for Non-Smooth Technologies», _Journal of Economics_ (_Zeitschrift für Nationalökonomie_), 44(2), 151–175.
- Noroozi, N., R. Geiselhart, L. Grüne, y F. R. Wirth (2020): «Control of Discrete-Time Nonlinear Systems via Finite-Step Control Lyapunov Functions», _Systems & Control Letters_, 138, 104631.
- Restuccia, D., y R. Rogerson (2008): «Policy Distortions and Aggregate Productivity with Heterogeneous Establishments», _Review of Economic Dynamics_, 11(4), 707–720.
- Romer, P. M. (1986): «Increasing Returns and Long-Run Growth», _Journal of Political Economy_, 94(5), 1002–1037.
- Skiba, A. K. (1978): «Optimal Growth with a Convex–Concave Production Function», _Econometrica_, 46(3), 527–539.
- Stokey, N. L., y R. E. Lucas, Jr., con E. C. Prescott (1989): _Recursive Methods in Economic Dynamics_. Cambridge, MA: Harvard University Press.
- Trebbi, F., M. B. Zhang, y M. Simkovic (2026): «The Cost of Regulatory Compliance in the United States», _The Review of Financial Studies_, 39(9), 2901–2962.
- Wagener, F. (2020): «Geometrical Methods for Analyzing the Optimal Management of Tipping Point Dynamics», _Natural Resource Modeling_, 33(3), e12258.
