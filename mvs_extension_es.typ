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
  Este trabajo desarrolla cuatro contribuciones analíticas y extensiones estructurales sobre el modelo de supervivencia óptima con rendimientos crecientes a escala, complementariedad bruta y trabajo endógeno de Milei y Reidel (2026, _Minimum Viable Scale: Bellman Barriers and the Economics of Survival_, versión de octubre de 2026). *Primero*, en el certificado de Barreras de Bellman de Primer Paso (FPBB) de la Sección 7.2, identificamos un término de holgura omitido en la construcción en bloques de dos períodos: al comparar cualquier transición individual $(x, y) in M times M$ con el par $(h, b)$ a igual esfuerzo laboral, la ganancia de consumo retiene simultáneamente el diferencial de capital inicial $q(h - x)$ y el diferencial de ahorro $(y - b)$. Mediante una barrera afín dependiente del estado $B_1 (x)$ de un solo paso, reducimos el techo de la barrera en casi cinco unidades ($-43.0465$ frente a $-38.1442$), *casi triplicamos el margen de calibración de permanencia* (de $2.564$ a $7.4665$ uniforme y $7.7756$ en $b = 0.10$) y *reducimos a la mitad el plazo máximo certificado de entrada* a $H = lr([0.28, infinity))$ (de $46$ a *$23$ períodos*, $24$ uniforme). Extendemos además el certificado a la banda previa $M_0 = lr([0.05, 0.10))$ con cota explícita $tau_(.1) <= 10$ períodos (y $tau_(.1) <= 9$ junto con $tau_H <= 21$–$22$ al unificar un testigo afilado con $W_M^((0))$ y $Psi^((0))$), y certificamos analíticamente mediante descomposición de Wronskiano y aritmética de intervalos que *MR-Tabla 5* de salidas adversas ($12$ subintervalos finitos) colapsa a dos evaluaciones en frontera sin mínimos interiores, elevando el margen de salida en $M$ de $0.0436$ a $> 0.0947$ y el margen global FPBB de $0.0423$ ($0.04$) a *$> 0.0571$* ($+35\%$). *Segundo*, resolvemos asintóticamente ($A -> infinity$) la pregunta abierta de la Nota al pie 1 estableciendo el isomorfismo finito $S_A^("fix") (overline(L)) = overline(L) S_(A overline(L)^r)^("fix") (1)$, formulando un criterio variacional preciso sobre trayectorias extintas óptimas o confinadas en $(0, S_A]$ para $S_A^("fix") (1) < S_A$, y demostrando bajo la condición de paciencia que cuando $A -> infinity$ tanto la frontera con trabajo endógeno como con trabajo fijo convergen a $s_infinity^* = (delta\/c_K)^(1\/r)$ ($S_A \/ S_A^("fix") (overline(L)) -> 1$), respaldado numéricamente por iteración de función de valor (VFI) hasta $A = 10^8$. *Tercero*, microfundamos la Sección 4.3 mediante gasto público productivo tipo Barro (1990) y carga regulatoria improductiva $(tau_p, tau_u)$, separando la envolvente asintótica diferenciable $overline(S)_("asy")(tau)$ (violada cerca del umbral de extinción económica $A_* = A_("SN")$) de la cota certificada a $A$ finito del Teorema 8 ($A_e >= 0.749$), el piso físico $kappa(tau)$, la simetría por pares de $S(tau)$ a $A_0$ finito y su perfil asintótico límite cuando $A_0 -> infinity$. *Cuarto*, formalizamos la descentralización empresarial manteniendo la contabilidad factorial exacta $(theta\/mu) Y_t$ —demostrando que una cuña marginal persistente $1\/mu <= 1\/theta < 1$ impide el isomorfismo de Bellman y abre una trampa descentralizada ya en $mu = theta$, mientras fragmentar empresas en $N_f$ unidades destruye productividad como $A\/N_f^(theta-1)$—, el crecimiento sin techo en unidades de eficiencia (distinguiéndolo del régimen $A K$ endógeno continuo) y certificados estocásticos continuos `log-PWL` de Bellman mediante parada opcional de Doob (*Lema 2* y *Proposición 4\**), derivando el plazo endógeno ajustado por riesgo $T^*(p)$ (frente al plazo determinista miope de $23$ períodos), un sistema acoplado de barreras Markovianas $(B_G, B_B)$ certificado en $32$ subcajas y la dicotomía de política óptima bajo VFI estocástica continua. El Apéndice Técnico A documenta la notación desambiguada y los certificados reproducibles en doble precisión IEEE-754.
  #v(0.65em)
  *Palabras clave.* escala mínima viable; barreras de Bellman de primer paso (FPBB); cotas de tiempo de entrada; oferta laboral endógena; curva en U institucional. \
  *Códigos JEL.* C61, D24, D61, H21, O41.
]

#v(0.7em)

= Introducción

En _Minimum Viable Scale: Bellman Barriers and the Economics of Survival_ (versión de octubre de 2026; toda la numeración de teoremas, constantes y tablas base de este artículo refiere a dicha edición), Milei y Reidel (2026) establecen una teoría unificada de la supervivencia económica cuando la tecnología agregada exhibe rendimientos crecientes a escala ($1 < theta < 2$), complementariedad bruta entre capital y trabajo ($rho = -d < 0$) y oferta laboral endógena con utilidad logarítmica sobre el consumo y el ocio ($L in [0, 1]$). Su resultado central muestra que, bajo una condición de paciencia ($beta[q + theta delta] > 1$) y productividad suficientemente elevada ($A > A_*$), existe una única Escala Mínima Viable $S_p$ estrictamente superior al umbral de reposición física $kappa_p$ (*Teorema 1*). En la banda intermedia $(kappa_p, S_p)$, aunque es físicamente factible sostener el stock de capital indefinidamente con consumo y ocio positivos, todo sendero óptimo decide liquidar gradualmente el capital hacia la extinción porque el retorno neto futuro no compensa el sacrificio de consumo y ocio presentes. En la frontera $S_p$, las trayectorias óptimas de extinción y supervivencia coexisten alcanzando el mismo bienestar total pero generando un quiebre hacia arriba (*upward kink*) en la función de valor (*Teorema 2*). Adicionalmente, dado que las sendas de liquidación diferida aproximan arbitrariamente bien el bienestar inicial óptimo (*Proposición 3*), los autores introducen el método de *Barreras de Bellman de Primer Paso* (*First Passage Bellman Barriers*, FPBB) para certificar analíticamente el ingreso en tiempo finito a una región productiva objetivo $H$ sin resolver la función de valor exacta $V_p (K)$.

Pese al rigor del marco de Milei y Reidel (2026), un análisis detenido de su construcción computacionalmente verificada en la Sección 7 y el Apéndice F, así como de las preguntas abiertas señaladas en el cuerpo del artículo, revela cuatro brechas analíticas susceptibles de cierre preciso sin alterar los axiomas del modelo ni ampliar su caja paramétrica:

1. *Afilamiento simultáneo de la barrera de permanencia y certificación global de las salidas adversas (Sección 3):* En el Teorema 9 de Milei y Reidel (2026), sobre la caja paramétrica (7.3) para la región de tránsito $M = lr([0.10, 0.28))$ y la región objetivo $H = lr([0.28, infinity))$, una barrera constante es imposible porque en el extremo superior $h = 0.28$ la recompensa de liquidar hacia $b = 0.10$ supera el bienestar alcanzable desde $b$. Los autores sortean esta obstrucción construyendo una barrera de bloques de $N = 2$ períodos que arroja $B(K) <= -38.144176$, un margen de permanencia $> 2.564$, un plazo máximo de entrada de $tau_H <= 46$ períodos y un margen global del certificado de $0.04$ (cuyo mínimo en la Tabla 5 de Milei y Reidel (2026), en adelante *MR-Tabla 5*, es $0.0423$, empleando los testigos de su Tabla 4, en adelante *MR-Tabla 4*). Demostramos en el *Lema 1* y el *Teorema 9\** que el agrupamiento en pares de la ecuación (7.6) descarta aproximadamente la mitad de la disipación disponible en cada transición individual $(x, y) in M times M$: una barrera afín de *un solo paso* $B_1 (x)$ retiene ambos términos simultáneamente, mejora la cota superior de la barrera a $-43.046512$, eleva el margen de permanencia a *$> 7.4665$* ($> 7.7755$ en $b = 0.10$) y reduce exactamente a la mitad el plazo máximo de entrada a *$tau_H <= 23$ períodos* ($24$ uniforme). Asimismo, cerramos la brecha sin cota de la Figura 6 en la banda previa $M_0 = lr([0.05, 0.10))$ certificando *$tau_(.1) <= 10$ períodos* (*Proposición 1\**), afilamos dicho testigo en el *Corolario 1* ($tau_(.1) <= 9$ y $tau_H <= 21$–$22$ con el testigo de $25$ pasos $W_M^((0))$ y la cota global continua $Psi^((0))$), y demostramos mediante un certificado de aritmética de intervalos sobre el Wronskiano y la segunda derivada (*Proposición 1\*\**) la ausencia de mínimos interiores en $M$ y $H_1$, reduciendo *MR-Tabla 5* a dos evaluaciones en frontera que elevan el margen de salida en $M$ a $> 0.0947$ y el margen global FPBB a *$> 0.0571$* ($+35\%$).
2. *Resolución asintótica ($A -> infinity$) e isomorfismo finito entre trabajo endógeno y fijo (Sección 4):* En la Nota al pie 1 (página 2), Milei y Reidel (2026) dejan como pregunta abierta la comparación entre la frontera $S_A$ con trabajo endógeno y la frontera $S_A^("fix") (overline(L))$ con trabajo exógenamente fijo. En el *Teorema 3\** probamos el isomorfismo exacto para todo $A$ finito, $S_A^("fix") (overline(L)) = overline(L) S_(A overline(L)^r)^("fix") (1)$, formulamos un criterio variacional preciso sobre trayectorias extintas óptimas o confinadas en $(0, S_A]$ bajo el cual $S_A^("fix") (1) < S_A$, y demostramos que bajo la condición de paciencia (2.3) (la cual fuerza $beta theta > 1$) tanto $A^(1\/r) S_A$ como $A^(1\/r) S_A^("fix") (overline(L))$ convergen al límite físico común $(delta\/c_K)^(1\/r)$, cerrando asintóticamente $S_A \/ S_A^("fix") (overline(L)) -> 1$ cuando $A -> infinity$, junto con una verificación numérica directa de fronteras por VFI hasta $A = 10^8$.
3. *Microfundación institucional y curva en U fiscal–regulatoria (Sección 5):* En la Sección 4.3, los autores modelan distorsiones mediante una pérdida multiplicativa exógena $A_e = (1 - tau) A$, advirtiendo expresamente que su aplicación a impuestos o regulaciones exige contabilizar los beneficios productivos de los ingresos recaudados. Acoplando la tecnología CES con provisión pública equilibrada de infraestructura y derechos de propiedad tipo Barro (1990) junto con carga burocrática improductiva ($tau = tau_p + tau_u$), derivamos el *Teorema 10*: caracterizamos las dos trampas físicas de extinción ($tau < tau_(min)$ y $tau > tau_(max)$), delimitamos las bandas intermedias de extinción económica ($A_e <= A_* = A_("SN")$, donde $cal(M)(tau) != emptyset$ pero $S(tau)$ no existe), establecemos la curva en U diferenciable exacta tanto para el piso físico $kappa(tau)$ como para la envolvente asintótica $overline(S)_("asy")(tau)$ —distinguiéndola rigurosamente de la cota certificada a $A$ finito del Teorema 8 en $A_e >= 0.749$ ($tau in [0.117245, 0.304799]$)— con mínimo único en $tau^* = alpha\/(1+alpha) = gamma$, probamos la simetría de conjuntos de nivel de $S(tau)$ para todo $A_0$ finito y su perfil límite exacto cuando $A_0 -> infinity$, además de la monotonicidad estricta frente a burocracia improductiva $tau_u$.
4. *Descentralización empresarial, crecimiento sostenido y barreras estocásticas (Sección 6):* Finalmente, extendemos el núcleo determinista de planificador central con techo estacionario $K_p^+$ en tres direcciones: (i) descentralización bajo competencia monopolística (Dixit y Stiglitz, 1977) con contabilidad factorial exacta $(theta\/mu) Y_t$ y externalidades (Romer, 1986), probando que fragmentar empresas en $N_f$ unidades equivale a destruir productividad según $A\/N_f^(theta-1)$ (con extinción económica ya en $N_(f,"SN") = 56.79$ frente a $N_(f,"rep") = 104.17$) y que la cuña marginal persistente $1\/mu <= 1\/theta < 1$ impide un isomorfismo de Bellman exacto, abriendo una trampa descentralizada ya en $mu = theta$ (*Proposición 2\**); (ii) crecimiento balanceado aumentador de trabajo a tasa $g > 0$, que elimina el techo $K_p^+$ y genera despegue exponencial perpetuo («palo de hockey») preservando cada certificado en unidades de eficiencia, en contraste con el régimen endógeno $A K$ continuo (*Proposición 3\**); y (iii) extensión probabilística completa de las FPBB mediante el Teorema de Parada Opcional de Doob (*Lema 2*) y certificados continuos `log-PWL` (*Proposición 4\**), reemplazando la cota determinista de $23$ períodos por plazos estocásticos endógenos $T^*(p)$ certificados en todo $(0, infinity)$ (hasta $p_("cert") = 2.0434\%$), barreras acopladas de Markov $(B_G, B_B)$ certificadas en $32$ subcajas sobre $p in [0, 12\%]$, y un experimento VFI estocástico continuo que contrasta la frontera bajo ruina $S^("ruin")(p)$ frente a las fronteras Markovianas $S_G (p), S_B^("kink")(p)$ y $K_B^*(p)$.

El resto del artículo se organiza como sigue. La Sección 2 sitúa nuestras contribuciones en la literatura económica y de control óptimo verificado. La Sección 3 desarrolla las barreras afines de un paso, la cota de cruce previo, su afilamiento y la reducción de *MR-Tabla 5*. La Sección 4 resuelve asintóticamente la Nota al pie 1 y presenta la verificación numérica por VFI. La Sección 5 deriva la curva en U institucional y descompone gasto productivo frente a peso muerto regulatorio. La Sección 6 formaliza la descentralización, el crecimiento sin techo y las barreras estocásticas. La Sección 7 concluye, y el Apéndice Técnico A reúne la notación desambiguada y los certificados reproducibles.

= Literatura Relacionada y Posicionamiento Teórico

Nuestros resultados se articulan en la intersección de cuatro líneas de investigación económica y matemática, cerrando en cada una limitaciones específicas respecto de las pruebas cuantitativas de supervivencia y las implicancias institucionales del modelo de Milei y Reidel (2026).

== Crecimiento óptimo no cóncavo, umbrales de Skiba y trampas de pobreza

Desde las contribuciones pioneras de Skiba (1978), Majumdar y Mitra (1982) y Dechert y Nishimura (1983), la teoría del crecimiento óptimo ha documentado que las tecnologías no convexas o con rendimientos crecientes locales dividen el espacio de estados mediante un umbral crítico de indiferencia donde coexisten trayectorias óptimas convergentes hacia la extinción o hacia un régimen próspero. Posteriormente, Mitra y Ray (1984) generalizaron las condiciones de existencia y monotonicidad a conjuntos factibles no convexos, mientras que Kamihigashi y Roy (2007) y Akao, Kamihigashi y Nishimura (2011) establecieron caracterizaciones globales en tiempo discreto sin diferenciabilidad ni concavidad, extendidas recientemente al tiempo continuo por Akao, Ishii, Kamihigashi y Nishimura (2022). En paralelo, la literatura de desarrollo económico formalizó trampas de pobreza basadas en externalidades de umbral en capital humano (Azariadis y Drazen, 1990) e imperfecciones crediticias con inversiones indivisibles (Galor y Zeira, 1993), mientras que Wagener (2020) caracterizó geométricamente los puntos de inflexión (*tipping points*) mediante variedades de indiferencia y principios de envolvente. No obstante, como señalan Kraay y McKenzie (2014) al evaluar la evidencia empírica, la mayoría de los modelos teóricos clásicos de umbrales operan con trabajo fijo y solo demuestran convergencia asintótica cualitativa, sin acotar cuánto tiempo tarda una economía que supera el umbral crítico en alcanzar un régimen productivo autosostenido. Nuestro *Teorema 9\** y la *Proposición 1\** suplen precisamente esta carencia en el modelo con trabajo endógeno de Milei y Reidel (2026), proporcionando plazos explícitos de entrada garantizada ($tau_(.1) <= 10$ y $tau_H <= 23$ períodos, afilados hasta $tau_(.1) <= 9$ y $tau_H <= 21$–$22$ en el Corolario 1).

== Oferta laboral endógena y complementariedad factorial bajo rendimientos crecientes

La función de producción de elasticidad de sustitución constante (CES) introducida por Arrow, Chenery, Minhas y Solow (1961) desempeña un papel central cuando la elasticidad de sustitución entre capital y trabajo es inferior a la unidad ($rho < 0$), escenario documentado empíricamente por Klump, McAdam y Willman (2007) para economías agregadas. Cuando la tecnología CES se combina con elección endógena de horas trabajadas y utilidad no separable o dependiente del ocio, de Hek (1998) demostró que las preferencias consumo–ocio pueden engendrar multiplicidad de estados estacionarios y trampas de desarrollo incluso bajo tecnologías convexas, mientras que Benhabib y Farmer (1994) exhibieron indeterminación y fluctuaciones endógenas bajo rendimientos crecientes agregados. En el caso de Milei y Reidel (2026), la combinación de rendimientos crecientes ($1 < theta < 2$), complementariedad bruta ($rho = -d < 0$) y desutilidad logarítmica del trabajo impide comparar directamente la frontera $S_A$ frente al modelo canónico de trabajo fijo (Nota al pie 1). Nuestro *Teorema 3\** resuelve esa comparación analítica: establece un isomorfismo exacto para productividad finita $A$ y prueba que, en el límite $A -> infinity$ sobre la escala crítica $A^(-1\/r)$, el trabajo óptimo tiende a cero pero más lentamente que el capital ($K_t\/L_t -> 0$), haciendo que el término de ocio desaparezca algebraicamente y ambos regímenes converjan al mismo problema límite.

== Barreras de Bellman, dualidad y certificados estocásticos de primer paso

El método FPBB de Milei y Reidel (2026) conecta la programación dinámica clásica (Bellman, 1957; Stokey, Lucas y Prescott, 1989) y los teoremas de envolvente sin diferenciabilidad (Milgrom y Segal, 2002) con cuatro tradiciones técnicas: la viabilidad en horizonte finito (Bertsekas, 1972), las funciones de almacenamiento disipativo (Willems, 1972; Grüne, Müller, Kellett y Weller, 2021), los iterados finitos de Lyapunov en control no lineal (Geiselhart, Gielen, Lazar y Wirth, 2014; Noroozi, Geiselhart, Grüne y Wirth, 2020) y la dualidad de programación lineal y valoración de opciones americanas (Haugh y Kogan, 2004; Gaitsgory, Parkinson y Shvartsman, 2019). Sin embargo, la construcción aplicada de la Sección 7.2 de Milei y Reidel (2026) utiliza bloques de dos pasos ($N = 2$) con una función de referencia constante, descartando la mitad de las ganancias de consumo por arista, y discretiza la región $M union H$ en doce intervalos finitos en *MR-Tabla 5* para acotar salidas adversas. Al sustituir la referencia constante por una barrera afín dependiente del estado en un solo paso ($N = 1$) y probar monotonía estricta de las holguras de salida adversa (*Proposición 1\*\**), reducimos a la mitad la cota de tiempo de entrada y elevamos el margen global certificado en un $35\%$. Más aún, mientras el FPBB original es estrictamente determinista, nuestro *Lema 2* y *Proposición 4\** completan el enfoque estocástico vía supermartingalas y parada opcional de Doob (1953), resolviendo certificados analíticos continuos dependientes de la anticipación del riesgo ($T^*(p)$ y barreras acopladas de Markov), complementados por la respuesta óptima de política mediante VFI estocástica continua.

== Bienes públicos productivos, distorsiones regulatorias y estructura de mercado

Finalmente, la Sección 4.3 de Milei y Reidel (2026) se apoya en la literatura moderna de mala asignación factorial y costos regulatorios —donde Restuccia y Rogerson (2008), Hsieh y Klenow (2009), Garicano, Lelarge y Van Reenen (2016) y Trebbi, Zhang y Simkovic (2026) cuantifican cómo cuñas regulatorias dependientes del tamaño empresarial y cargas de cumplimiento deprimen la productividad total de los factores (TFP). Como advierten los propios autores (pág. 10), modelar impuestos o regulaciones únicamente como una pérdida pura $A_e = (1 - tau) A$ ignora el retorno productivo del gasto público y la protección de derechos de propiedad (Barro, 1990; Futagami, Morita y Shibata, 1993; Acemoglu, Johnson y Robinson, 2005). Nuestro *Teorema 10* unifica ambas perspectivas en una fórmula cerrada bivariada $A_e (tau_p, tau_u) = A_0 tau_p^alpha (1 - tau_p - tau_u)$ que reproduce la monotonía anti-burocracia de Milei y Reidel sobre $tau_u$ y genera la curva en U sobre $tau_p$. Asimismo, las extensiones de la Sección 6 muestran cómo descentralizar rendimientos crecientes sin pérdidas operativas mediante competencia monopolística (Dixit y Stiglitz, 1977) o externalidades de escala (Romer, 1986), revelando que fragmentar empresas en $N_f$ unidades replica exactamente un colapso de TFP $A\/N_f^(theta-1)$.

= Barreras de Bellman Afines de Un Paso, Plazo de Entrada y Afilamiento del Certificado Global

== El marco paramétrico y la holgura en la construcción de dos períodos

Siguiendo la Sección 7 de Milei y Reidel (2026), consideramos la tecnología CES armónica con parámetros $(theta, rho, w) = (3\/2, -1, 1\/2)$, donde la función de producción y la utilidad por período son:
$ F_A (K, L) = A ( (2 K L) / (K + L) )^(3/2), quad u(C, L) = eta log C + (1 - eta) log(1 - L), quad C + K' <= q K + F_A (K, L), $
sobre la caja paramétrica (7.3) del artículo original:
$ A in [0.749, 0.751], quad beta in [0.9699, 0.9701], quad q in [0.9199, 0.9201], quad eta in [0.6999, 0.7001]. $
Para la región de tránsito $M = lr([b, h)) = lr([0.10, 0.28))$ y la región objetivo $H = lr([h, infinity)) = lr([0.28, infinity))$, sea $rho.alt(K, s) = max_(0 <= L < 1) {eta log(q K + F_A (K, L) - s) + (1 - eta) log(1 - L)}$ el retorno reducido en un período. Las constantes verificadas racionalmente en las ecuaciones (7.5) y la página 59 de Milei y Reidel (2026) son:
$ hat(R) = -0.996 > rho.alt(h, b), quad Delta_2 = 0.2997 < (eta_- beta_- q_- (h - b)) / (q_+ h + F_(A_+) (h, 1) - b) = 0.2997787, $
con consumo máximo factible $C_(max) = q h + F_A (h, 1) - b <= C_(max)^+ = 0.37495167$, piso del testigo en $M$ dado por $W_M (K) >= W_M (b) > -35.579855 > -35.58$ y techo de continuación irrestricto $Psi^sharp (K) = Psi(K) - 10\/301 >= V(K)$, donde $Psi(h) < -27.83$ (y más precisamente $Psi(0.28) = -27.837112$, $Psi^sharp (0.28) = -27.870334$).

En la página 22 de Milei y Reidel (2026), para una cadena de dos transiciones internas $x -> y -> z$ en $M$, los autores acotan cada arista por separado:
$ rho.alt(x, y) <= rho.alt(h, b) - (eta (y - b)) / C_(max), quad rho.alt(y, z) <= rho.alt(h, b) - (eta q (h - y)) / C_(max), $
sumando ambas para obtener $[hat(R) - rho.alt(x, y)] + beta [hat(R) - rho.alt(y, z)] >= Delta_2$ y definiendo la barrera de dos períodos $B_0 = hat(R)\/(1 - beta) - Delta_2\/(1 - beta^2) <= -38.144176$.

Observemos, sin embargo, qué ocurre en *una única transición* cualquiera $(x, y) in M times M$. Sea $L in lr([0, 1))$ el nivel de trabajo que alcanza el máximo $rho.alt(x, y)$, con consumo $c_0 = q x + F_A (x, L) - y > 0$. Evaluando la utilidad en el par $(h, b)$ con exactamente el *mismo* trabajo $L$, el consumo resultante es $c_1 = q h + F_A (h, L) - b <= C_(max)$. La diferencia exacta de consumo entre $(h, b)$ y $(x, y)$ a igual esfuerzo laboral es:
$ c_1 - c_0 = q(h - x) + [F_A (h, L) - F_A (x, L)] + (y - b). $
Dado que $x < h$ y $F_A (dot, L)$ es no decreciente en el stock de capital para todo $L in [0, 1]$, se cumple que $F_A (h, L) - F_A (x, L) >= 0$. Por consiguiente, *ambos* términos $q(h - x) > 0$ y $(y - b) >= 0$ están presentes simultáneamente en cada arista individual $(x, y) in M times M$. Al descartar $q(h - x)$ en la primera transición y $(z - b)$ en la segunda, la construcción en bloques disjuntos de longitud $N = 2$ pierde prácticamente la mitad de la disipación acumulada a lo largo de trayectorias que permanecen en $M$.

== Construcción de la barrera afín de un paso y reducción del plazo de entrada

El siguiente lema formaliza la cota de pérdida por arista individual y construye una barrera regional afín explícita que satisface la desigualdad de Bellman en un solo paso en todo $M$.

#thm_box("Lema 1 (Cota de pérdida unificada y barrera regional afín en M)")[
  Bajo la caja paramétrica (7.3), toda transición de permanencia $(x, y) in M times M = lr([b, h)) times lr([b, h))$ satisface:
  $ rho.alt(x, y) <= rho.alt(h, b) - eta / C_(max) [q(h - x) + (y - b)] <= hat(R) - eta / C_(max) [q(h - x) + (y - b)]. $
  En consecuencia, la función afín dependiente del estado definida sobre $M = lr([b, h))$ por:
  $ B_1 (x) = B_* - (eta q (h - x)) / C_(max), quad B_* = (hat(R) - Delta_2) / (1 - beta), $
  es una barrera regional de Bellman acotada en $M$, es decir, satisface $B_1 (x) >= rho.alt(x, y) + beta B_1 (y)$ para todo $x, y in M$. Más aún, uniformemente en (7.3):
  $ B_1 (x) <= B_* <= -43.0465116, quad B_1 (b) <= -43.355594, $
  y el margen de calibración frente al testigo factible $W_M (x)$ satisface $W_M (x) - B_1 (x) >= W_M (b) - B_1 (b) > 7.7755$ (y uniformemente $W_M (x) - B_* > 7.4665$).
]

#proof_block[
  Para cualquier $(x, y) in M times M$, sea $L in lr([0, 1))$ el maximizador que define $rho.alt(x, y)$ con consumo $c_0 = q x + F_A (x, L) - y > 0$, y sea $c_1 = q h + F_A (h, L) - b <= C_(max)$. Como $(h, b, L)$ es factible en $(h, b)$ y el término de ocio $(1 - eta) log(1 - L)$ se cancela, la concavidad del logaritmo ($log(c_1\/c_0) >= (c_1 - c_0)\/c_1$) y la monotonía $F_A (h, L) >= F_A (x, L)$ implican:
  $ rho.alt(h, b) - rho.alt(x, y) >= eta log(c_1 / c_0) >= eta (c_1 - c_0) / c_1 >= eta / C_(max) [q(h - x) + (y - b)]. $
  Reemplazando $rho.alt(h, b) <= hat(R)$ se obtiene la primera desigualdad del enunciado. Ahora evaluamos $rho.alt(x, y) + beta B_1 (y)$ para cualquier par $x, y in M$:
  $ rho.alt(x, y) + beta B_1 (y) &<= hat(R) - (eta q (h - x)) / C_(max) - (eta (y - b)) / C_(max) + beta B_* - (eta beta q (h - y)) / C_(max) \
  &= hat(R) + beta B_* - (eta q (h - x)) / C_(max) - eta / C_(max) [(y - b) + beta q (h - y)]. $
  Dado que $y in lr([b, h))$ y $beta q < 1$, la combinación lineal en $y$ cumple:
  $ (y - b) + beta q (h - y) = (1 - beta q)(y - b) + beta q (h - b) >= beta q (h - b). $
  Por lo tanto, el último término está acotado inferiormente por $(eta beta q (h - b))\/C_(max) > Delta_2$. Como $hat(R) - Delta_2 + beta B_* = B_*$ por definición de $B_*$, concluimos que para todo $x, y in M$:
  $ rho.alt(x, y) + beta B_1 (y) <= B_* - (eta q (h - x)) / C_(max) = B_1 (x). $
  En la caja (7.3), $hat(R) - Delta_2 = -0.996 - 0.2997 = -1.2957 < 0$ y $beta >= 0.9699$, de modo que $B_* <= -1.2957 \/ 0.0301 = -43.04651162...$ Asimismo, $(eta q)\/C_(max) >= (0.6999 times 0.9199)\/0.37495167 = 1.717123$, lo que arroja $B_1 (b) <= -43.0465116 - 1.717123(0.18) = -43.355594$. Finalmente, dado que el consumo del testigo en el primer paso $c_M (x) = q x + F_A (x, 0.68) - 0.135$ satisface $0 < c_M (x) < C_(max)$ y $F_(A,K) (x, 0.68) > 0$, la derivada del piso del testigo verifica $W'_M (x) = eta [q + F_(A,K) (x, 0.68)] \/ c_M (x) > (eta q)\/C_(max) = B'_1 (x)$ en todo $M$. Por ende, la holgura $W_M (x) - B_1 (x)$ es estrictamente creciente en $x in lr([b, h))$ y alcanza su ínfimo en $x = b$:
  $ inf_(x in M) [W_M (x) - B_1 (x)] = W_M (b) - B_1 (b) > -35.58 - (-43.355594) = 7.775594. $
]

Con el Lema 1 establecido, demostramos nuestra versión reforzada del Teorema 9 de Milei y Reidel (2026), que reduce el límite temporal de entrada de $46$ a $23$ períodos (y a $24$ bajo comparación uniforme no condicionada al estado inicial).

#thm_box("Teorema 9* (Certificado CES reforzado y reducción a la mitad del plazo de entrada)")[
  Bajo la caja paramétrica (7.3), sean $M = lr([0.10, 0.28))$ y $H = lr([0.28, infinity))$.
  1. La barrera regional afín $B_1 (K)$ del Lema 1 y los testigos factibles de *MR-Tabla 4* conforman un certificado estricto de primer paso (FPBB) con margen de permanencia uniforme mayor a $7.466$ ($7.775$ estado a estado) y margen de salida adversa $> 0.0423$ bajo la partición de *MR-Tabla 5* (elevado a $> 0.0571$ en la Proposición 1\*\*).
  2. Toda trayectoria óptima que parte de $K_0 in M$ ingresa a la región productiva $H = lr([0.28, infinity))$ a más tardar en la fecha *$tau_H <= 23$* (o $tau_H <= 24$ usando únicamente cotas uniformes independientes de $K_0$) y permanece en $H$ para siempre. Si $K_0 in [0.10, 0.105]$, su fecha de primera entrada satisface:
  $ 3 <= tau_H <= 23. $
]

#proof_block[
  Las comparaciones de salida adversa desde $M$ y $H$ hacia acciones por debajo de $b$ y $h$ dependen únicamente de $W_M, W_H$ y del techo $Psi^sharp$, por lo que bajo *MR-Tabla 5* conservan margen uniforme $> 0.0423$ (y se mejoran a $> 0.0571$ en la Proposición 1\*\*). Por el Teorema 5 de selección global FPBB, ninguna trayectoria óptima desde $M union H$ realiza jamás una transición adversa ni permanece indefinidamente en $M$.

  Para acotar la fecha máxima de entrada $tau_H$, consideremos cualquier camino factible que permanezca en $M$ durante $T >= 1$ transiciones consecutivas $x_0 -> x_1 -> dots.c -> x_T$ con $x_t in M$ para todo $0 <= t <= T$, seguido de cualquier continuación factible desde $x_T$. Iterando la desigualdad de un paso $rho.alt(x_t, x_(t+1)) <= B_1 (x_t) - beta B_1 (x_(t+1))$ para $t = 0, dots, T - 1$ y acotando el valor de continuación en $t = T$ mediante $V(x_T) <= Psi^sharp (x_T) <= Psi(x_T)$, el bienestar total $J_(x_0) (pi)$ de dicho camino verifica:
  $ J_(x_0) (pi) <= B_1 (x_0) + beta^T [Psi^sharp (x_T) - B_1 (x_T)]. $
  En el intervalo $x in lr([0.10, 0.28))$, la derivada de $Psi^sharp (x) = 0.4 x - 5 x^(-1\/2) - 18.5 - 10\/301$ es $(Psi^sharp)'(x) = 0.4 + 2.5 x^(-3\/2) >= 0.4 + 2.5 (0.28)^(-3\/2) = 17.272 > 2 > (eta q)\/C_(max) = B'_1 (x)$. En consecuencia, $Psi^sharp (x_T) - B_1 (x_T)$ es estrictamente creciente en $x_T in lr([b, h))$ y está acotada superiormente por su límite en $x_T arrow.t h$:
  $ sup_(x_T in M) [Psi^sharp (x_T) - B_1 (x_T)] = Psi^sharp (h) - B_* < -27.83 - B_*. $
  *Cota uniforme ($T = 24$):* Utilizando la cota uniforme $B_1 (x_0) <= B_* <= -43.0465116$ y la cota superior conservadora $Psi(h) < -27.83$ de la página 59 de Milei y Reidel (2026), para $T = 24$ períodos obtenemos:
  $ J_(x_0) (pi) <= -43.0465116 + (0.9701)^24 (-27.83 - (-43.0465116)) = -43.0465116 + 7.34364 = -35.70287 < -35.58 <= W_M (x_0). $
  *Cota estado a estado ($T = 23$):* Dado que $W_M (x_0) - B_1 (x_0)$ es estrictamente creciente en $x_0 in lr([b, h))$ por el Lema 1, la ventaja del testigo sobre el camino de $T$ pasos cumple para todo $x_0, x_T in M$:
  $ W_M (x_0) - J_(x_0) (pi) >= [W_M (b) - B_1 (b)] - beta_+^T [Psi(h) - B_*]. $
  Evaluando en $T = 23$ (exactamente la mitad de los $46$ períodos del artículo original):
  $ W_M (x_0) - J_(x_0) (pi) >= 7.775594 - (0.9701)^23 (15.2165116) = 7.775594 - 7.569980 = +0.205614 > 0. $
  (Si además se emplean las cotas exactas $hat(R) = -0.996799$, $Delta_2 = 0.299778$ y $Psi^sharp (0.28) = -27.870334$ ya demostradas en las páginas 57–59 de Milei y Reidel, la holgura resulta positiva incluso en $T = 22$ con $+0.0073$). Por lo tanto, ningún camino óptimo puede permanecer en $M$ durante $23$ períodos, lo que certifica $tau_H <= 23$. La cota inferior $tau_H >= 3$ para $K_0 in [0.10, 0.105]$ se sigue de $Phi(0.105) < 0.16$ y $Phi(0.16) < 0.26 < 0.28$.
]

#figure(
  image("fig1_barrier_es.svg", width: 100%),
  caption: [Comparación entre la construcción por bloques de dos períodos de Milei y Reidel (2026) (*MR-Tabla 4* / $Psi^sharp$) y nuestra barrera afín de un paso $B_1 (K)$ sobre $M = lr([0.10, 0.28))$. El Panel (a) ilustra la ganancia de calibración de casi $5$ unidades de bienestar; el Panel (b) muestra la reducción del plazo máximo certificado de entrada de $tau_H <= 46$ a $tau_H <= 23$–$24$ períodos (marcando exactamente los valores evaluados de las curvas de prefijo).],
)

== Cota explícita de cruce en el tramo previo $M_0 = lr([0.05, 0.10))$ y afilamiento unificado

En la Figura 6 (página 21) de Milei y Reidel (2026), el cruce desde $K_0 > S_A$ hasta $0.10$ se garantiza únicamente en tiempo finito ($tau_(.1) < infinity$) sin cota cuantitativa explícita. Aunque ninguna cota uniforme puede llegar hasta $K_0 -> S_A^+$ debido a la desaceleración hiperbólica en el punto de coexistencia $S_A$, sí es posible extender directamente nuestra barrera afín de un paso al intervalo ancla $M_0 = lr([b_0, h_0)) = lr([0.05, 0.10))$, donde el Teorema 8 ya excluye salidas adversas hacia abajo ($G(K) > K$).

#thm_box([Proposición 1\* (Cota explícita de cruce en el tramo previo $M_0 = lr([0.05, 0.10))$)])[
  Bajo la caja paramétrica (7.3), sea $M_0 = lr([0.05, 0.10))$. Toda trayectoria óptima con $K_0 in M_0$ supera el umbral $0.10$ en a lo sumo *$tau_(.1) <= 10$ períodos*, y alcanza la región productiva $H = lr([0.28, infinity))$ en a lo sumo $tau_H <= 33$ períodos totales.
]

#proof_block[
  En $M_0 = lr([b_0, h_0)) = lr([0.05, 0.10))$, la maximización directa sobre $L in lr([0, 1))$ da $rho.alt(0.10, 0.05) <= -1.827072 < hat(R)_0 := -1.827$, consumo máximo $C_(max,0) <= q_+(0.10) + F_(A_+) (0.10, 1) - 0.05 = 0.100233$ y pérdida por paso $Delta^(0) := 0.3115 < (eta_- beta_- q_- (0.05))\/C_(max,0) = 0.311503$. Por el Lema 1 aplicado a $M_0$, la barrera $B^(0) (x) = B_*^(0) - (eta q (h_0 - x))\/C_(max,0)$ satisface $B_*^(0) = (hat(R)_0 - Delta^(0))\/(1 - beta) <= -2.1385 \/ 0.0301 = -71.046512$.

  Como testigo factible para todo $K_0 in M_0$, anteponemos al testigo $W_M (0.10) = -35.579855 > -35.58$ de *MR-Tabla 4* la secuencia de tres pasos $(K_0 -> 0.065 -> 0.0845 -> 0.100)$ con trabajo constante $L = 0.75$ (inspirada en la progresión geométrica desde $0.05$ de la página 46 de Milei y Reidel). Para $K_0 = 0.05$, los consumos resultantes $(0.002495, 0.006286, 0.022068)$ satisfacen $c < 1$, de modo que los extremos desfavorables $(A_-, q_-, eta_+)$ rinden utilidades de etapa exactas $(-4.611772, -3.964892, -3.085659)$ (nótese que en el primer paso incluso $L -> 1$ limita el consumo a $0.003009$ y la utilidad máxima sobre $L$ es $-4.597860 < -4.59$). Descontando con $beta_+ = 0.9701$ y $W_M (0.10) = -35.579855$ se obtiene $W_(M_0) (0.05) = -43.844826 > -43.845$. Más aún, la transición inicial $K_0 -> 0.065 -> 0.0845 -> 0.100$ es factible en todo $M_0$ por liquidación temporal cuando $K_0 >= 0.065$ (ya que la restricción $C + K' <= q K + F_A$ permite elegir $K' < K_0$), con consumo inicial $c_0 (K_0) = q_- K_0 + F_(A_-)(K_0, 0.75) - 0.065 >= c_0 (0.05)$ estrictamente creciente en $K_0$; en consecuencia, $W_(M_0) (K_0) >= W_(M_0) (0.05) = -43.844826 > -43.845$ uniformemente en todo $[0.05, 0.10)$. Como en $h_0 = 0.10$ el techo irrestricto cumple $Psi(0.10) < -34.271388$, en $T_0 = 10$ pasos dentro de $M_0$ se tiene:
  $ B_*^(0) + (0.9701)^10 [Psi(0.10) - B_*^(0)] = -71.046512 + (0.9701)^10 (36.775124) = -43.8997 < -43.845 < W_(M_0) (K_0). $
  Como el orden monótono de sucesores (F.1) excluye transiciones óptimas desde $M_0$ hacia abajo de $0.05$, toda trayectoria óptima desde $M_0$ debe ingresar a $lr([0.10, infinity))$ en $tau_(.1) <= 10$ períodos. Combinado con el Teorema 9\*, entra en $H = lr([0.28, infinity))$ en a lo sumo $10 + 23 = 33$ períodos (Tabla 1).
]

#thm_box([Corolario 1 (Testigo afilado en $M_0$ y unificación de $25$ pasos con $W_M^((0))$ y $Psi^((0))$)])[
  Manteniendo sin cambios las barreras $B^(0)$ y $B_1$ bajo la caja (7.3):
  1. Reemplazando los tres pasos de $M_0$ por la trayectoria afilada $(K_0 -> 0.0595 -> 0.0755 -> 0.100)$ con esfuerzos laborales $(0.45, 0.50, 0.60)$ (factible por liquidación temporal y estrictamente creciente para todo $K_0 in [0.05, 0.10)$), las utilidades mínimas en $(A_-, q_-, eta_+)$ ascienden a $(-3.681867, -3.888538, -3.828711)$, elevando el piso del testigo a $W_(M_0)^("af") (0.05) = -43.540132$ con la cola de *MR-Tabla 4* (y a $-43.500107$ al empalmarse con el testigo factible de $25$ pasos $W_M^((0)) (0.10; beta_+) = -35.536014$ de la Sección 6.3).
  2. Certificando continuamente en todo $(0, infinity)$ la super-barrera paramétrica $Psi^((0)) (K) = 0.45 K - 5 K^(-1\/2) + c_0$ mediante ramificación y acotación tridimensional centrada en $[8 times 10^(-5), 45.0]$ más colas analíticas ($c_(0,"unif") = -18.713835$ uniforme en la caja, $Psi_("unif")^((0)) (0.10) = -34.480223$, $Psi_("unif")^((0)) (0.28) = -28.036947$), se obtiene *$tau_(.1) <= 9$ períodos* uniformemente en $M_0$ (mediante la comparación estado a estado frente a $B^(0)(K_0)$ —evaluada en $B^(0)(0.05) = -71.367682$, pues $W_(M_0)^("af")(K_0) - B^(0)(K_0)$ es estrictamente creciente en $M_0$ al cumplirse $c_0^("af")(K_0) <= 0.0822 < C_(max,0)^+$—, con holgura mínima $+0.0029$) y *$tau_H <= 22$ períodos* en $M$ bajo extremos independientes de la caja (holgura $+0.122408$, o *$tau_H <= 21$ períodos* bajo $beta$ acoplado, total $30$–$31$ períodos desde $K_0 = 0.05$).
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
    [Plazo total desde $K_0 = 0.05$ a $H$], [Finito (sin cota)], [*$<= 33$ períodos*], [Cota nueva (sin cota previa)],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Síntesis cuantitativa de las mejoras analíticas sobre la Sección 7.2 y el Teorema 9 de Milei y Reidel (2026) empleando los testigos base *MR-Tabla 4* / $Psi^sharp$ bajo exactamente los mismos parámetros (7.3). (Bajo el testigo afilado y la unificación continua del Corolario 1, las cotas se reducen adicionalmente a $tau_(.1) <= 9$ y $tau_H <= 21$–$22$, o $30$–$31$ períodos totales.)],
)

*Descomposición exacta de la holgura frente al problema restringido en $M$ (VFI):* Conviene medir cuánta distancia separa la cota certificada de peor caso ($tau_H <= 23$) de la dinámica óptima real. Resolviendo por programación dinámica restringida a $M = [0.10, 0.28)$ bajo exactamente las mismas cotas externas de *MR-Tabla 4* / $Psi^sharp$ (`verify_restricted_M_vfi`), el problema de permanencia restringido $J_T^(*, Psi^sharp)(x_0) - W_M (x_0)$ pasa de $+0.028144$ en $T = 8$ a $-0.556742$ en $T = 9$, idéntico plazo que la barrera regional de punto fijo óptima en $M$, $B_("opt")(x) = max_(y in M) {rho.alt^+ (x, y) + beta_- B_("opt")(y)}$ ($B_("opt")(0.10) = -56.794979$, $B_("opt")(0.28^-) = -52.457990$, holgura $+0.472857$ en $T = 9$ evaluada en la cota uniforme / peor estado inicial $x_0 = 0.28^-$, donde $inf_(M)(W_M - B_("opt")) = 19.1824$ frente a $21.2151$ en $0.10$). Por su parte, en la VFI continua sin restricciones en el centro de la caja ($A = 0.75, beta = 0.97, q = 0.92, eta = 0.70$, donde $V(0.10) = -35.597030$), la política óptima ingresa a $H$ en *$max_(K_0 in M) tau_H^("VFI")(K_0) = 4$ períodos* y el problema restringido verdadero $J_T^(*, "VFI")(x_0) - V(x_0)$ se torna estrictamente negativo ya en $T = 4$ ($-0.173124$, frente a $-0.752234$ en $T = 5$). Así, de los $46$ períodos originales, la barrera afín cerrada $B_1$ elimina $23$ períodos ($46 -> 23$), la linealización afín —al descartar $F_A (h, L) - F_A (x, L)$ y usar $C_("max")$ global— explica los $14$ períodos hasta el óptimo regional ($23 -> 9$), y la brecha externa entre $(W_M, Psi^sharp)$ y $V$ explica los $5$ períodos restantes hasta el peor caso efectivo ($9 -> 4$).

== Monotonía estado a estado de las salidas adversas y reducción de *MR-Tabla 5*

Al elevar mediante $B_1 (K)$ el margen de calibración de permanencia a $> 7.4665$ ($> 7.7755$ en $b = 0.10$) y el margen del prefijo en $T = 23$ a $+0.2056$, el bloque de permanencia en $M$ deja por completo de ser una restricción activa en el certificado global FPBB. En *MR-Tabla 5* (Milei y Reidel, 2026, pág. 23 y Apéndice F.3), las comparaciones de salida adversa sobre las regiones $M = [0.10, 0.28)$ y $H_1 = [0.28, 0.80)$ se verifican dividiendo dichos intervalos en $12$ subintervalos finitos $[k_-, k_+]$ y evaluando $underline(W)_X (k_-)$ en el extremo izquierdo frente a la cota superior $E^+ (k_+, a; l_0) + beta_- Psi^sharp (a)$ en el extremo derecho, lo que arroja un margen mínimo global de $0.0423$ (reportado conservadoramente como $.04$).

La siguiente proposición demuestra que esa discretización por subintervalos es innecesaria: evaluando ambas funciones en el *mismo* estado $K$, la ventaja del testigo frente a la envolvente tangente crece estrictamente con $K$ en todo $M$ y en todo $H_1$, reduciendo las $12$ filas finitas de *MR-Tabla 5* a únicamente dos evaluaciones puntuales en los bordes inferiores $K = 0.10$ y $K = 0.28$.

#thm_box([Proposición 1\*\* (Certificación analítica de monotonía y ampliación del margen global)])[
  Bajo la caja paramétrica (7.3), sean los testigos de *MR-Tabla 4* definidos por $(l_M, s_M, underline(T)_M, a, l_0) = (0.68, 0.135, -33.103, 0.10, 0.44)$ sobre $M = lr([0.10, 0.28))$ y $(l_H, s_H, underline(T)_H, a, l_0) = (0.72, 0.375, -27.164, 0.28, 0.57)$ sobre $H_1 = lr([0.28, 0.80))$. La ventaja puntual del testigo frente a la envolvente de salida adversa (F.19)–(F.20),
  $ Delta_X (K) := underline(W)_X (K) - [E^+ (K, a; l_0) + beta_- Psi^sharp (a)], $
  es estrictamente creciente en todo punto de ambos intervalos, sin mínimos interiores. Más precisamente:
  1. Un certificado analítico de intervalos (evaluado en doble precisión IEEE-754) sobre el cociente $R_X (K) = (cal(S)(K) - a)\/c_X (K)$ en $4$ subintervalos de $M$ y $6$ de $H_1$ basta por sí solo para garantizar uniformemente $Delta'_M (K) >= +0.0723 > 0$ en $M$ y $Delta'_(H_1) (K) >= +0.0095 > 0$ en $H_1$ (excluyendo mínimos interiores); complementariamente, las cotas de intervalo de la segunda derivada certifican concavidad estricta $Delta''_M (K) <= -2.5107 < 0$ (en $8$ subintervalos, empleando $eta_+$ donde $c''_M > 0$) y $Delta''_(H_1) (K) <= -0.1889 < 0$ (en $10$ subintervalos), ubicando además el ínfimo de $Delta'_X$ en el límite lateral derecho:
     $ inf_(K in M) Delta'_M (K) = Delta'_M (0.28^-) = +0.502666, quad inf_(K in H_1) Delta'_(H_1) (K) = Delta'_(H_1) (0.80^-) = +0.100489. $
  2. En consecuencia, $inf Delta_X$ se alcanza en el borde izquierdo de cada dominio y las $12$ particiones finitas de *MR-Tabla 5* se reducen a dos evaluaciones exactas en $K = 0.10$ y $K = 0.28$ (Tabla 2):
     - En $M = lr([0.10, 0.28))$, el margen mínimo de salida adversa asciende de $> 0.0436$ a *$> 0.0947$* ($+117\%$).
     - En $H_1 = lr([0.28, 0.80))$, el margen mínimo asciende de $> 0.0423$ a $> 0.0561$ (con $l_0 = 0.60$) y a *$> 0.0571$* (con $l_0 = 0.57$), elevando el margen global certificado de todo el Teorema 9 en $M union H$ de $0.0423$ ($.04$) a *$> 0.0571$* ($+35\%$).
]

#proof_block[
  Por la construcción del Apéndice F.3 (ecuaciones F.19–F.20 de Milei y Reidel), para cada región $X in {M, H_1}$ con esfuerzo del testigo $l_X$, sucesor $s_X$, cola $underline(T)_X$, umbral de salida $a$ y punto de tangencia $l_0 >= sup(X)\/2$ (condición global de dominancia de la tangente: escribiendo $u = L\/K$ y $g(u) = (u\/(1+u))^(3\/2)$, el intercepto en $u = 0$ de la recta tangente en $u_0 = l_0\/K$ es $g(u_0) - u_0 g'(u_0) = u_0^(3\/2)(1+u_0)^(-5\/2)(u_0 - 1\/2) >= 0$ si y solo si $l_0 >= K\/2$), el consumo mínimo del testigo es $c_X (K) = q_- K + F_(A_-) (K, l_X) - s_X > 0$, la pendiente tangente es $t(K) = partial_L F_(A_+) (K, l_0)$ y el recurso virtual mayorante es $cal(S)(K) = q_+ K + F_(A_+) (K, l_0) + (1 - l_0) t(K)$. Para $(K, a, l_0) = (0.28, 0.28, 0.57)$ se cumple $l_0 = 0.57 >= 0.80\/2$ en todo $H_1$ y $beta_- Psi'(0.28) = beta_- (Psi^sharp)'(0.28) = 16.7535 > 4.6539 = 1\/(cal(S)(0.28) - 0.28)$, de modo que la envolvente sobre $[0.05, a]$ alcanza su máximo en $s = a$ (la rama en $s = 0$ es inferior por más de $5.37$ unidades en $M$ y $11.77$ en $H_1$). Más aún, el multiplicador de ocio $u^*(K) := (1 - eta)(cal(S)(K) - a)\/t(K)$ satisface $u^*(K) in [0.5662, 0.6808] < 1$ en $M$ y $[0.4301, 0.5427] < 1$ en $H_1$ (globalmente $u^*(K) in [0.4301, 0.6808] < 1$), lo que garantiza trabajo óptimo estrictamente interior $L^*(K) = 1 - u^*(K) >= 0.3192 > 0$ en ambos dominios.

  *Descomposición exacta de $Delta'_X (K)$ y ausencia de mínimos interiores:* La pendiente tangente satisface las identidades logarítmicas cerradas:
  $ (t'(K)) / (t(K)) = (5 l_0) / (2 K (K + l_0)) > 0, quad ((t'\/t)')(K) = - (5 l_0 (2 K + l_0)) / (2 K^2 (K + l_0)^2) < 0. $
  Diferenciando cada rama de $underline(W)_X$ y de $E^+ (K, a; l_0)$ y definiendo el cociente $R_X (K) := (cal(S)(K) - a)\/c_X (K) > 1$ se obtiene la cota inferior exacta en todo punto diferenciable (y para ambas derivadas laterales en los quiebres de $min\/max$):
  $ Delta'_X (K) >= (eta_- c'_X (K) R_X (K) - cal(S)'(K)) / (cal(S)(K) - a) + (1 - eta_+) (5 l_0) / (2 K (K + l_0)). $
  Para certificar $R'_X (K) < 0$, escribimos $R'_X (K) = Q_X (K) \/ c_X (K)^2$ con Wronskiano $Q_X (K) := cal(S)'(K) c_X (K) - c'_X (K)(cal(S)(K) - a)$, cuya derivada cancela idénticamente el producto $cal(S)' c'$: $Q'_X (K) = cal(S)''(K) c_X (K) - c''_X (K)(cal(S)(K) - a)$. Como $partial_K F_(A,K)(K, L) prop (L - 4K) K^(-1\/2)(K + L)^(-7\/2)$ y $t''(K) prop (3 l_0\/2 - 2K) K^(1\/2)(K + l_0)^(-9\/2)$, tanto $F_(A,K)$ (pico único en $L\/4$) como $t'$ (pico único en $3 l_0\/4$) carecen de mínimos interiores, mientras $|Q'_X|$ queda acotado en cada subintervalo $[k_L, k_R]$ por las envolventes de extremo y puntos críticos interiores de $|F_(A, K K)|$ y $|t''|$. La cota de Lipschitz desde el punto medio $k_m = (k_L + k_R)\/2$, $Q_X (K) <= Q_X (k_m) + (k_R - k_L)|Q'_X|_([k_L, k_R])\/2$, arroja:
  - en los $4$ subintervalos iguales de $M$ (`[0.100, 0.145, 0.190, 0.235, 0.280]`): $Q_M (K) <= -0.06341, -0.05880, -0.05061, -0.04375 < 0$;
  - en los $6$ subintervalos de $H_1$ (`[0.28, 0.36, 0.45, 0.54, 0.63, 0.72, 0.80]`): $Q_(H_1) (K) <= -0.18976, -0.16941, -0.15171, -0.13844, -0.13124, -0.13540 < 0$.
  Así $R_X (K)$ es estrictamente decreciente en todo $M$ y $H_1$, cumpliendo $R_X (K) >= R_X (k_R)$ en cada $[k_L, k_R]$. Reemplazando $c'_X (K) >= min{c'_X (k_L), c'_X (k_R)}$, $cal(S)'(K) <= cal(S)'_([k_L, k_R], max)$ (por unimodalidad de $F_(A,K)$ y $t'$) y el denominador $cal(S)(K) - a$ por el extremo apropiado según el signo del numerador, se obtienen las cotas de intervalo analíticas:
  - en $M$ ($4$ subintervalos): $Delta'_M (K) >= +3.0288, +0.3955, +0.1252, +0.0723 > 0$;
  - en $H_1$ ($6$ subintervalos): $Delta'_(H_1) (K) >= +1.4675, +0.3243, +0.1022, +0.0348, +0.0095, +0.0119 > 0$.
  Esto excluye rigurosamente todo mínimo interior de $Delta_X (K)$ en ambos dominios sin depender de mallas. Además, en la segunda derivada por intervalos,
  $ Delta''_X (K) <= [(cal(S)')^2 - eta_- (c'_X R_X)^2] / (cal(S) - a)^2 + (eta^* c''_X) / c_X - (cal(S)'') / (cal(S) - a) + (1 - eta_+) (t'\/t)'(K), $
  nótese que en $M$ el punto de inflexión $l_M\/4 = 0.17$ yace dentro del dominio, de modo que $c''_M (K) > 0$ en $[0.10, 0.17)$ y $c''_M (K) <= 0$ en $[0.17, 0.28)$; por consiguiente, el término de signo variable debe evaluarse con $eta^* = eta_+$ cuando $c''_X > 0$ (en $[0.10, 0.17)$) y $eta^* = eta_-$ cuando $c''_X <= 0$ (en $[0.17, 0.28)$ y en todo $H_1$, donde $l_H\/4 = 0.18 < 0.28$). Con dicha regla de signo exacta sobre $8$ subintervalos iguales de $M$ y $10$ de $H_1$ se certifica $Delta''_M (K) <= -2.5107 < 0$ (alcanzando $-421.1331$ en $[0.10, 0.1225]$) y $Delta''_(H_1) (K) <= -0.1889 < 0$. En $H_1$, los dos cambios de régimen donde $c_(H_1) (K)$ cruza $1 - l_H = 0.28$ ($k_W = 0.406819$, donde $W'_(H_1)$ cae de $3.954006$ a $3.952877$) y donde $E^+$ conmuta de $eta_-$ a $eta_+$ ($k_E = 0.573570$, donde $(-E^+)'$ cae de $-1.652310$ a $-1.652744$) constituyen quiebres estrictamente *hacia abajo* en la primera derivada, preservando la concavidad estricta global (Apéndice A.2). Por concavidad estricta, $Delta'_X$ decrece monótonamente y alcanza su ínfimo en el borde derecho ($Delta'_M (0.28^-) = +0.502666$ y $Delta'_(H_1) (0.80^-) = +0.100489$), mientras $Delta_X$ alcanza su mínimo en el borde izquierdo:
  - En $K = 0.10$: $underline(W)_M (0.10) - [E^+ (0.10, 0.10; 0.44) + beta_- Psi^sharp (0.10)] = 0.094717 > 0.0947$ (y $0.062495 > 0.0624$ usando $Psi$).
  - En $K = 0.28$: por el teorema de la envolvente sobre $l_0 > K\/4$, $partial E^+ \/ partial l_0 = (eta\/c^*)(L_("tan")(K; l_0) - l_0) F_(A_+, L L)(K, l_0) = 0 <=> l_0 = L^*(K; l_0)$, cuya solución variacional exacta en $K = 0.28$ es $L^*(0.28) = 0.569743 approx 0.57$ (en $K = 0.10$, $L^*(0.10) = 0.437261$ y $L_("tan")(0.10; 0.44) = 0.433840$, por lo que $l_0 = 0.44$ dista apenas $1.7 times 10^(-5)$ del óptimo). Con $l_0 = 0.60$, $underline(W)_H (0.28) - [E^+ (0.28, 0.28; 0.60) + beta_- Psi^sharp (0.28)] = 0.056121 > 0.0561$; optimizando $l_0 = 0.57$, se eleva a $0.057148 > 0.0571$ (y $0.024926 > 0.0249$ usando $Psi$).
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
    [$M = lr([0.10, 0.28))$], [*MR-Tabla 5* ($4$ intervalos)], [$> 0.0114$], [$> 0.0436$],
    [$M = lr([0.10, 0.28))$], [*Prop. 1\*\* en $K = 0.10$* \ *($l_0 = 0.44$)*], [*$> 0.0624$*], [*$> 0.0947$*],
    [$H_1 = lr([0.28, 0.80))$], [*MR-Tabla 5* ($8$ intervalos)], [$> 0.01008$], [$> 0.0423$],
    [$H_1 = lr([0.28, 0.80))$], [*Prop. 1\*\* en $K = 0.28$* \ *($l_0 = 0.57$)*], [*$> 0.0249$*], [*$> 0.0571$*],
    [$H_2 = lr([0.80, infinity))$], [Cota global ec. (F.21)], [$> 2.2662$], [$> 2.2984$],
    table.hline(stroke: 0.6pt),
    [*Margen global FPBB*], [*Mínimo sobre $M union H$*], [*$> 0.0249$* \ (vs. $0.01008$)], [*$> 0.0571$* \ (vs. $0.0423$)],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Eliminación de las $12$ particiones finitas de *MR-Tabla 5* mediante la monotonía estado a estado de la Proposición 1\*\*.],
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
  Frente a la economía con trabajo endógeno, la economía a capacidad plena ($overline(L) = 1$ sin costo de ocio) domina en bienestar ($V_A^("fix") (K; 1) > V_A (K)$ para todo $K > 0$). A la escala crítica $S_A$, sea $Delta W_A^+ := J_A^("fix") (pi^+ |_(L=1)) - V_A (S_A) > 0$ el excedente de aplicar pleno empleo a la trayectoria productiva óptima $pi^+$ desde $S_A$, y sea $cal(O)_(-)^("fix")$ la clase de trayectorias extintas factibles bajo trabajo fijo confinadas en $(0, S_A]$ que satisfacen el piso uniforme de consumo $C_t >= chi_p^("fix") K_t$ (con $chi_p^("fix") = Omega(1) > 0$ independiente de $A$, clase no vacía que contiene a todo óptimo extinto en $(0, S_A]$ y excluye la liquidación diferida de la Proposición 3 de Milei y Reidel), definiendo $Delta W_A^- := sup_(pi^- in cal(O)_(-)^("fix")) [J_A^("fix") (pi^-) - V_A (S_A)]$. Entonces $Delta W_A^- = O(A^(-d\/[r(1+d)]))$ y la desigualdad estricta $S_A^("fix") (1) < S_A$ se cumple en todo $A$ tal que $Delta W_A^+ > Delta W_A^-$.
]

#proof_block[
  *Parte 1 (Escalado de operadores y convergencia de fronteras).* Sea $K = A^(-1\/r) k$ y $C = A^(-1\/r) c$. Usando $1 - theta\/r = -1\/r$ y $rho = -d < 0$:
  $ f_A (k, L) := A^(1/r) F_A (A^(-1\/r) k, L) = c_K k^theta [1 + c_w (k / (A^(1\/r) L))^d]^(-theta/d), quad c_w = (1 - w) / w. $
  Con trabajo fijo $L equiv overline(L) in lr((0, 1])$, $(A^(1\/r) overline(L))^(-d) = O(A^(-d\/r)) -> 0$ y $f_A (k, overline(L)) -> c_K k^theta$. Con trabajo endógeno, multiplicando la condición de primer orden $F_(A,L)(K, L) = nu C\/(1 - L)$ ($nu = (1 - eta)\/eta$) por $A^(1\/r)$:
  $ theta c_K c_w k^(theta + d) A^(-d/r) L^(-1 - d) [1 + c_w (A^(1/r) L / k)^(-d)]^(-1 - theta/d) = nu c / (1 - L), $
  lo que fuerza $L = [theta c_K c_w k^(theta + d)\/(nu c)]^(1\/(1+d)) A^(-d\/[r(1+d)])(1 + o(1)) -> 0$ y $K\/L = Theta(A^(-1\/[r(1+d)])) -> 0$, de modo que $f_A (k, L) = c_K k^theta [1 + O(A^(-d\/[r(1+d)]))]$, $(1 - eta)log(1 - L) = -O(A^(-d\/[r(1+d)]))$ y el operador normalizado converge en compactos al de trabajo fijo.

  Para demostrar la convergencia de las fronteras mismas, nótese primero que para $q in (0, 1)$ y $theta > 1$, $theta - (q + theta delta) = q(theta - 1) > 0$. Por ende, la condición de paciencia (2.3), $beta[q + theta delta] > 1$, implica necesariamente $beta theta > 1$. Fijemos cualquier stock reescalado $k_0 > (delta\/c_K)^(1\/r)$ y sea $K_0 = A^(-1\/r) k_0$. Construimos una expansión factible con trabajo constante $L_0 in (0, 1]$ (en particular $L_0 = 3\/4$ para trabajo endógeno, o $L_0 = overline(L)$ bajo trabajo fijo —esto es, $L_0 = 1$ cuando $overline(L) = 1$, sin costo de ocio—):
  - Elegimos $epsilon_1 in (0, 1)$ tal que $c_K (1 - epsilon_1) k_0^r > delta$ y un umbral macroscópico fijo $K_("esc") > 0$ (independiente de $A$) suficientemente pequeño para que $[1 + c_w (K_("esc")\/L_0)^d]^(-theta\/d) >= 1 - epsilon_1\/2$, de modo que $f_A (k, L_0) >= c_K (1 - epsilon_1\/2) k^theta$ mientras $K_t <= K_("esc")$.
  - *Fase I (escape del cuello de botella):* Consumiendo la mitad del excedente neto sobre $k_t$, se alcanza en $T_1 (k_0) < infinity$ pasos (independientes de $A$) un nivel fijo $k_1 >= max{2, (2 / [c_K (1 - epsilon_1\/2)])^(1\/(theta - tilde(theta)))}$ (donde la cota $k_1 >= 2$ descarta la rama contractiva $k_1 < 1$ incluso cuando $c_K > 2$), habiéndose fijado $tilde(theta) in (beta^(-1), theta)$ (factible por $beta theta > 1$).
  - *Fase II (crecimiento superexponencial):* Ahorrando mitad de los recursos ($C_t = K_(t+1) = [q K_t + F_A (K_t, L_0)]\/2$), se mantiene $k_t >= k_1 >= 2$ y se cumple $k_(t+1) >= k_t^(tilde(theta))$ mientras $k_t <= A^(1\/r) K_("esc")$, alcanzándose $K_(T_1 + J) >= K_("esc")$ en a lo sumo $J(A) <= (log log A)\/(log tilde(theta)) + O(1)$ períodos (tras lo cual, por monotonía de $F_A (dot, L_0)$, es factible descender en el paso siguiente hasta el nivel $K_("esc")$).
  - *Fase III (meseta macroscópica):* Durante las Fases I y II ($0 <= t < T_1 + J(A)$), $C_t = A^(-1\/r) c_t$ con $c_t = Omega(1)$ aporta utilidad de etapa $u(C_t, L_0) >= -(eta\/r) log A - O(1)$, cuya suma descontada acumula $-(1 - beta^(T_1 + J))(eta\/[r(1 - beta)]) log A - O(1)$ (donde el residuo $-O(1)$ permanece acotado uniformemente cuando $J(A) -> infinity$ porque $sum_(t=0)^infinity beta^t = (1 - beta)^(-1)$). Desde $t >= T_1 + J$, mantener constante $K_("esc")$ rinde consumo $A f_1 (K_("esc"), L_0) - delta K_("esc") = Omega(A)$, aportando utilidad descontada al menos $beta^(T_1 + J) (eta\/(1 - beta)) log A - O(1)$.

  En contraste, por la cota de recursos del Lema 9 en $(0, K_0]$ (con tasa $G_A (K_0) = q + F_A (K_0, 1)\/K_0 -> q + c_K k_0^r = O(1)$), toda trayectoria confinada en $(0, K_0]$ —incluida cualquier senda óptima extinta desde $K_0$— tiene bienestar acotado superiormente por $-(eta\/[r(1 - beta)]) log A + O(1)$. Sumando Fases I–III y sustrayendo la cota de extinción del Lema 9, el término $-(eta\/[r(1 - beta)]) log A$ se cancela idénticamente; usando $1 + 1\/r = theta\/r$ y $beta^(J(A)) >= c_0 (log A)^(-|log beta|\/log tilde(theta))$, el excedente neto de la expansión factible escala al menos como $beta^(T_1 + J(A)) (theta eta\/[r(1 - beta)]) log A - O(1) >= c_1 (log A)^(1 - |log beta|\/log tilde(theta)) - O(1) -> +infinity$ porque $T_1$ es independiente de $A$ y $beta tilde(theta) > 1 => 1 - |log beta|\/log tilde(theta) > 0$. Por contradicción con el Teorema 1, ningún óptimo puede extinguirse desde $K_0 = A^(-1\/r) k_0$ para $A$ grande, luego $limsup_(A -> infinity) A^(1\/r) S_A <= (delta\/c_K)^(1\/r)$ (y análogamente para $S_A^("fix") (overline(L))$). Combinado con la cota física inferior (4.5) del Teorema 3 y (2.4) para $kappa_A^("fix") (overline(L))$, ambos límites coinciden exactamente en $(delta\/c_K)^(1\/r)$ y su cociente converge a $1$.

  *Parte 2 (Isomorfismo finito y condición variacional).* Homogeneidad de grado $theta = 1 + r$ da $F_A (overline(L) tilde(K), overline(L)) = overline(L) F_(A overline(L)^r) (tilde(K), 1)$ y $eta log(overline(L) tilde(C)_t) = eta log tilde(C)_t + eta log overline(L)$, estableciendo el isomorfismo finito exacto. Por el Teorema 1, en $K_0 = S_A$ coexisten un óptimo productivo $pi^+$ y uno extinto que alcanzan $V_A (S_A)$. Evaluar $pi^+$ con $L equiv 1$ (sin desutilidad de ocio) es factible en trabajo fijo y eleva su bienestar en $Delta W_A^+ > 0$, luego $V_A^("fix") (S_A; 1) >= J_A^("fix") (pi^+ |_(L=1)) = V_A (S_A) + Delta W_A^+$. Inversamente, supóngase $S_A^("fix") (1) >= S_A$: existiría entonces un óptimo extinto estrictamente decreciente $pi^- = (C_t^("f"), K_(t+1)^("f"))_(t>=0) in cal(O)_(-)^("fix")$ en trabajo fijo con $K_t^("f") <= S_A <= c_+ A^(-1\/r)$ para todo $t >= 0$. Para establecer el piso uniforme $chi_p^("fix") = Omega(1)$ (uniformemente cuando $A -> infinity$), obsérvese que a lo largo de cualquier óptimo extinto decreciente en $(0, S_A]$, el consumo futuro cumple $C_s^("f") <= G_("max") K_t^("f")$ ($s >= t + 1$) con $G_("max") = q + c_K c_+^r <= beta^(-1) + o(1)$; por consiguiente, $V_A^("fix")(K_t^("f"); 1) <= eta log C_t^("f") + frac(beta eta, 1 - beta) log(G_("max") K_t^("f"))$, mientras que la senda factible de *cake-eating* rinde exactamente $V_("cake")(K_t^("f")) = frac(eta, 1 - beta) log((1 - beta) q K_t^("f")) + frac(beta eta, (1 - beta)^2) log(beta q)$. Comparando $V_A^("fix")(K_t^("f"); 1) >= V_("cake")(K_t^("f"))$ se cancela $log K_t^("f")$ y resulta $C_t^("f")\/K_t^("f") >= chi_p^("fix") := [(1 - beta) q]^(1\/(1 - beta)) (beta q)^(beta\/(1 - beta)^2) G_("max")^(-beta\/(1 - beta)) approx 2.07 times 10^(-106) > 0$ evaluado en $G_("max") = 1\/beta$ (o, acotando la continuación con el problema lineal $A K$ de tasa $G_("max")$ sobre $K_(t+1)^("f") <= K_t^("f")$, $chi_p^("fix") := (1 - beta) q (beta q)^(beta\/(1 - beta)) (q\/G_("max"))^(beta\/(1 - beta)^2) approx 3.60 times 10^(-57) > 0$), ambas constantes estrictamente positivas e independientes de $A$. Equipando toda trayectoria de capital $pi^- in cal(O)_(-)^("fix")$ con esfuerzo $tilde(L)_t = c_0 A^(-d\/[r(1+d)])$ y consumiendo $tilde(C)_t = C_t^("f") - [F_A (K_t^("f"), 1) - F_A (K_t^("f"), tilde(L)_t)] > 0$ (para $A$ suficientemente grande), la cota uniforme $C_t^("f") >= chi_p^("fix") K_t^("f")$ garantiza:
  $ (F_A (K_t^("f"), 1) - F_A (K_t^("f"), tilde(L)_t)) / C_t^("f") <= (theta c_K c_w) / (d chi_p^("fix")) A (K_t^("f"))^r (K_t^("f") / tilde(L)_t)^d = O(A^(- d / (r(1+d)))), $
  idéntico orden que $(1 - eta)|log(1 - tilde(L)_t)| = O(tilde(L)_t)$. Sumando con descuento $beta$, $V_A (S_A) >= J_A^("endo") (pi^- |_(tilde(L))) >= J_A^("fix") (pi^-) - C_2 A^(-d\/[r(1+d)])$, luego $Delta W_A^- = O(A^(-d\/[r(1+d)]))$. Si $Delta W_A^+ > Delta W_A^-$, $J_A^("fix") (pi^+ |_(L=1)) > sup_(pi^- in cal(O)_(-)^("fix")) J_A^("fix") (pi^-)$ descarta toda extinción óptima en $S_A$ bajo trabajo fijo, implicando $S_A^("fix") (1) < S_A$.
]

#thm_box([Corolario 2 (Debilitamiento de la condición de paciencia (2.3) a $beta theta > 1$)])[
  Supóngase únicamente $beta in (0, 1)$ y *$beta theta > 1$*, sin exigir la condición más fuerte (2.3) ($beta[q + theta delta] > 1$). Definidos los umbrales generales de supervivencia y extinción $S_A^- := inf{K_0 > 0 : "algún óptimo desde " K_0 " sobrevive"}$ y $S_A^+ := sup{K_0 > 0 : "algún óptimo desde " K_0 " se extingue"}$ (y análogamente $S_A^("fix", plus.minus) (overline(L))$), se cumple $kappa_A <= S_A^- <= S_A^+$ y ambos convergen asintóticamente al mismo límite físico:
  $ lim_(A -> infinity) A^(1/r) S_A^- = lim_(A -> infinity) A^(1/r) S_A^+ = lim_(A -> infinity) A^(1/r) S_A^("fix", plus.minus) (overline(L)) = (delta / c_K)^(1/r). $
]

#proof_block[
  Con $L_t <= 1$ y $rho < 0$, la tecnología acotada $F_A (K, 1) < A (1 - w)^(theta\/rho)$ confina todo capital factible a un compacto $[0, K_("max")]$ y garantiza la existencia de políticas óptimas para cualquier $beta in (0, 1)$. Por supermodularidad de $rho.alt(x, y)$ (Dechert y Nishimura, 1983; Lema 5 de Milei y Reidel, 2026), cuya validez tampoco depende de (2.3), toda trayectoria óptima $(K_t^*)$ es monótona en el tiempo. En particular, cualquier óptimo que se extingue ($K_t^* -> 0$) desde $K_0$ es monótono no creciente y permanece confinado en $(0, K_0]$, satisfaciendo la cota del Lema 9. Como la construcción de tres fases de la Parte 1 del Teorema 3\* solo emplea $tilde(theta) in (beta^(-1), theta)$ —factible bajo $beta theta > 1$—, para todo $k_0 > (delta\/c_K)^(1\/r)$ y $A$ suficientemente grande la expansión supera a toda senda confinada en $(0, A^(-1\/r) k_0]$, descartando la extinción óptima y probando $limsup_(A -> infinity) A^(1\/r) S_A^+ <= (delta\/c_K)^(1\/r)$. La cota física inferior $liminf_(A -> infinity) A^(1\/r) S_A^- >= lim_(A -> infinity) A^(1\/r) kappa_A = (delta\/c_K)^(1\/r)$ es puramente tecnológica (independiente de $beta$), cerrando el límite común. Además, para $A$ suficientemente grande (o siempre que exista un óptimo sobreviviente sobre $kappa_A$), la supermodularidad estricta de $rho.alt(x, y)$ combinada con el teorema de la envolvente impone $V'_("surv")(x) = rho.alt_x (x, g^+(x)) > rho.alt_x (x, g^-(x)) = V'_("ext")(x)$ en cualquier punto de indiferencia, forzando un único umbral de Skiba $S_A^- = S_A^+$ (tal como verifica la VFI en $beta = 0.90$).
]

== Verificación numérica de la condición de primer orden y de fronteras (VFI)

La Figura 2 y la Tabla 3 distinguen explícitamente entre dos niveles complementarios de verificación en el modelo CES armónico ($theta = 3\/2, d = 1, r = 1\/2, beta = 0.97, q = 0.92, eta = 0.70$) para $A in [0.75, 10^8]$: (i) la evaluación exacta de la condición de primer orden del trabajo $L^*_A$ en el punto de referencia reescalado fijo $(k, c) = (0.002, 10^(-4))$, donde $A dot L^*_A$ converge hacia la constante teórica $0.133074$ mientras el costo de ocio y la brecha relativa de producto decaen como $O(A^(-1))$; y (ii) la *resolución directa de la ecuación de Bellman normalizada (VFI)* con interpolación continua sobre una malla de tres zonas de $880$ puntos en $k = A^2 K$ ($360$ nodos uniformes en $[0.00078, 0.00102]$ con refinamiento local de $25$ puntos en el salto de Skiba), comparando explícitamente las fronteras verdaderas de supervivencia $A^2 S_A^("fix") (1)$ y $A^2 S_A^("endo")$. Se verifica numéricamente en todo el rango $A in [0.75, 10^8]$ que $S_A^("fix") (1) < S_A^("endo")$ (de acuerdo con el criterio variacional de la Parte 2, donde el excedente productivo VFI permanece en $Delta W_A^+ in [0.29, 8.70]$ en todo $[0.75, 10^8]$ y $[0.66, 8.70]$ en $[0.75, 100]$) y que el cociente de fronteras $S_A^("endo") \/ S_A^("fix") (1)$ converge monótonamente hacia $1$ ($1.01997$ en $A = 0.75$, $1.00125$ en $A = 100$ y $1.00039$ en $A = 10^8$; duplicar la malla a $1760$ puntos desplaza dicho cociente en menos de $2.3 times 10^(-5)$ tanto en $A = 100$ como en $A = 10^8$). Nótese además que la aproximación conjunta de $A^2 S_A$ hacia el límite físico $(delta\/c_K)^2 = 0.000800$ se produce a ritmo ultralentamente logarítmico $O(1\/log log A)$ debido al factor $beta theta = 1.455 > 1$, alcanzando $0.000848$ en $A = 10^3$ y $0.000835$ en $A = 10^8$. Asimismo, para corroborar directamente el Corolario 2 cuando la condición (2.3) falla, la VFI con $beta = 0.90$ ($beta[q + theta delta] = 0.936 < 1 < beta theta = 1.35$, donde $(D\/c_K)^2 = 0.004565$) confirma un único umbral de Skiba que desciende hacia $(delta\/c_K)^2 = 0.000800$ mientras el cociente converge a $1$: $(A^2 S_A^("fix")(1), A^2 S_A^("endo"), "cociente")$ pasa de $(0.002038, 0.002153, 1.05642)$ en $A = 1.5$ a $(0.001909, 0.001919, 1.00508)$ en $A = 100$ y $(0.001727, 0.001731, 1.00191)$ en $A = 10^8$.

#figure(
  image("fig2_scaling_es.svg", width: 100%),
  caption: [Escalamiento asintótico y resolución numérica de fronteras para la Nota al pie 1 ($theta = 3\/2, d = 1, r = 1\/2$). El Panel (a) extiende $A in [0.75, 100]$, sombreando la banda certificada a $A$ finito del Teorema 8 ($kappa_A$ a $0.0014025025 A^(-2)$) junto a la asíntota $(D\/c_K)^2 A^(-2)$ y las fronteras VFI $S_A^("fix")(1), S_A^("endo")$; el Panel (b) combina las magnitudes FOC exactas evaluadas en el punto fijo $(k, c) = (0.002, 10^(-4))$ (decaimiento en $A^(-1)$ y $A^(-2)$) con la brecha relativa de fronteras $S_A^("endo")\/S_A^("fix") (1) - 1 -> 0$ calculada directamente por VFI.],
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
    [$0.75$], [$1.428 times 10^(-3)$], [$0.000803$], [$1.583 times 10^(-1)$], [$0.11874$], [$3.276\%$], [$0.000875$], [$0.000893$], [*$1.01997$*],
    [$1.50$], [$3.559 times 10^(-4)$], [$0.000801$], [$8.380 times 10^(-2)$], [$0.12571$], [$1.570\%$], [$0.000868$], [$0.000877$], [*$1.01089$*],
    [$3.00$], [$8.891 times 10^(-5)$], [$0.000800$], [$4.311 times 10^(-2)$], [$0.12934$], [$0.768\%$], [$0.000864$], [$0.000869$], [*$1.00621$*],
    [$10.0$], [$8.000 times 10^(-6)$], [$0.000800$], [$1.319 times 10^(-2)$], [$0.13194$], [$0.227\%$], [$0.000859$], [$0.000862$], [*$1.00279$*],
    [$30.0$], [$8.889 times 10^(-7)$], [$0.000800$], [$4.423 times 10^(-3)$], [$0.13270$], [$0.075\%$], [$0.000856$], [$0.000857$], [*$1.00172$*],
    [$100.0$], [$8.000 times 10^(-8)$], [$0.000800$], [$1.330 times 10^(-3)$], [$0.13296$], [$0.023\%$], [$0.000853$], [$0.000854$], [*$1.00125$*],
    [$1000.0$], [$8.000 times 10^(-10)$], [$0.000800$], [$1.331 times 10^(-4)$], [$0.13306$], [$0.002\%$], [$0.000848$], [$0.000848$], [*$1.00090$*],
    [$10^8$], [$8.000 times 10^(-20)$], [$0.000800$], [$1.331 times 10^(-9)$], [$0.13307$], [$0.000\%$], [$0.000835$], [$0.000835$], [*$1.00039$*],
    table.hline(stroke: 0.6pt),
    [$-> infinity$], [$-> 0$], [*$0.000800$*], [$-> 0$], [*$0.133074$*], [*$0\%$*], [*$0.000800$*], [*$0.000800$*], [*$1.00000$*],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Verificación numérica combinada del Teorema 3\* en el modelo CES armónico: columnas 2–6 en el punto FOC fijo $(k, c) = (0.002, 10^(-4))$ y columnas 7–9 mediante resolución VFI directa de ambas fronteras de supervivencia ($c_K = 2 sqrt(2)$, $(delta\/c_K)^2 = 0.000800$, $Delta W_A^+ in [0.29, 8.70]$).],
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
Notablemente, esta microfundación explica además el origen de los rendimientos crecientes agregados ($theta > 1$): aun cuando la tecnología privada exhiba rendimientos constantes a escala ($theta_0 = 1$), la retroalimentación fiscal de la infraestructura pública ($gamma in (0, 1\/2)$) genera endógenamente $theta = 1\/(1 - gamma) in (1, 2)$, y la alícuota productiva maximizadora del ingreso neto satisface la regla clásica de Barro (1990), $tau^* = alpha\/(1 + alpha) = gamma$. (En la ilustración numérica de la Tabla 4 mantenemos $theta = 3\/2$ para preservar la comparabilidad directa con el modelo armónico de referencia mientras fijamos $gamma = tau^* = 0.20$ y $alpha = 0.25$, lo que corresponde a $theta_0 = theta(1 - gamma) = 1.20$; recíprocamente, $theta_0 = 1$ con $theta = 3\/2$ correspondería a $gamma = 1\/3, alpha = 1\/2$.)

Dado que $A_e (tau)$ actúa como un escalar multiplicativo puro sobre la tecnología CES (2.1) cuando el presupuesto público se internaliza en la programación dinámica agregada (*planificador fiscal*), *todos* los resultados estructurales de Milei y Reidel (2026) —la Proposición 1, el Teorema 1, el Teorema 2 y el Teorema 3— se transfieren de forma exacta componiéndolos con la función unimodal $A_e (tau)$. (Nótese que si, en cambio, hogares y firmas privadas tomaran $G_t$ como una externalidad agregada exógena —como bajo el supuesto privado $theta_0 = 1$—, sus rendimientos marginales privados retendrían una cuña adicional $(1 - gamma) = (1 + alpha)^(-1) < 1$ respecto del planificador fiscal: $tau^* = gamma$ continuaría maximizando el retorno privado, pero el umbral crítico descentralizado superaría a $S_(A_e (tau))$, de modo análogo a la cuña $1\/theta$ de la Proposición 2\*.)

#thm_box([Teorema 10 (Curva en U institucional, extinción económica y límite de $S(tau)$)])[
  Sea una economía con productividad efectiva $A_e (tau) = A_0 tau^alpha (1 - tau)$, donde $alpha = gamma\/(1 - gamma) > 0$ y los seis parámetros restantes cumplen la condición de paciencia (2.3). Defina la carga institucional óptima (regla de Barro):
  $ tau^* = alpha / (1 + alpha) = gamma in (0, 1), quad A_(max) := A_e (tau^*) = A_0 alpha^alpha / (1 + alpha)^(1 + alpha). $
  1. *Doble umbral de extinción física (Anarquía vs. Hiper-regulación):* Si $A_(max) > A_("rep")$, existen exactamente dos cargas críticas $0 < tau_(min) < tau^* < tau_(max) < 1$, raíces únicas de $tau^alpha (1 - tau) = A_("rep") \/ A_0$, tales que:
     - Para $tau in (0, tau_(min))$ (*trampa de anarquía / déficit institucional*) y para $tau in (tau_(max), 1)$ (*trampa de confiscación / sobre-regulación*), el conjunto físicamente sostenible es vacío ($cal(M)(tau) = emptyset$) y toda historia factible se extingue geométricamente: $K_t <= [q + A_e (tau) Lambda_a]^t K_0 -> 0$, donde $Lambda_a := sup_(K > 0) F_1 (K, 1)\/K = delta\/A_("rep")$.
     - Para $tau in (tau_(min), tau_(max))$, el intervalo sostenible $[kappa(tau), K^+(tau)]$ es no vacío, alcanza su amplitud máxima en $tau = tau^*$, y $kappa(tau)$ describe una curva en U diferenciable exacta con mínimo global único en $tau^*$ ($partial log kappa(tau)\/partial tau < 0$ para $tau < tau^*$ y $> 0$ para $tau > tau^*$).
  2. *Extinción económica, envolvente asintótica $overline(S)_("asy")(tau)$ y cota certificada del Teorema 8:* Si $A_(max) > A_*$ (donde $A_* = A_("SN") = 0.0995245$ bajo el modelo armónico de referencia), sea $(tau_1, tau_2) subset (tau_(min), tau_(max))$ el intervalo abierto estricto donde $A_e (tau) > A_*$. En las bandas intermedias $(tau_(min), tau_1]$ y $[tau_2, tau_(max))$, el conjunto físicamente sostenible es no vacío ($cal(M)(tau) != emptyset$), pero toda trayectoria óptima liquida hacia la extinción (*extinción económica*, por lo que $S(tau)$ no existe). Como advierten Milei y Reidel (2026, págs. 10 y 20), la relación $S_A = Theta(A^(-1\/(theta-1)))$ proporciona cotas de orden asintóticas y no implica por sí sola que la cota escalada rija para todo $A$ finito ni la diferenciabilidad de $S(tau)$. Separando ambos niveles sobre $(tau_1, tau_2)$:
     - *(a) Envolvente asintótica $overline(S)_("asy")(tau)$ frente a la cota certificada a $A$ finito del Teorema 8:* La envolvente asintótica del Teorema 3, $overline(S)_("asy")(tau) := (D\/c_K)^(1\/(theta - 1)) [A_e (tau)]^(-1\/(theta - 1))$ (tabulada en la Tabla 4), describe una curva diferenciable y estrictamente convexa en U con mínimo único en $tau^* = alpha\/(1+alpha) = gamma$ y derivada logarítmica cerrada exacta:
       $ partial / (partial tau) log overline(S)_("asy")(tau) = - 1 / (theta - 1) [ alpha / tau - 1 / (1 - tau) ] = (tau - tau^*) / ((theta - 1)(1 - tau^*) tau (1 - tau)). $
       Sin embargo, $overline(S)_("asy")(tau)$ *no* es una cota superior universal a $A$ finito: en el modelo de referencia ($A_0 = 1.45, alpha = 0.25$), la frontera verdadera $S(tau)$ por VFI cruza por encima de $overline(S)_("asy")(tau)$ cuando $A_e (tau) < A_("cross") = 0.110038$ (es decir, fuera de $(tau_(c,1), tau_(c,2)) = (3.3171 times 10^(-5), 0.922567)$), manteniéndose $S(tau) <= overline(S)_("asy")(tau)$ empíricamente para $A_e (tau) >= A_("cross")$. La única *cota superior certificada a $A$ finito* disponible analíticamente es la del Teorema 8, $overline(S)_("cert")(tau) := 0.0014025025 thin [A_e (tau)]^(-2) = (0.03745)^2 [A_e (tau)]^(-2)$, rigurosamente válida sobre el dominio $A_e (tau) >= 0.749$ ($tau in [0.117245, 0.304799]$).
     - *(b) Simetría de conjuntos de nivel de la frontera verdadera $S(tau)$ a todo $A_0$ finito:* Como $S(tau) = S_(A_e (tau))$ depende de $tau$ únicamente mediante el escalar unimodal $A_e (tau)$ en $(tau_1, tau_2)$, todo $tau_- in (tau_1, tau^*)$ posee un único conjugado $tau_+ in (tau^*, tau_2)$ con $A_e (tau_-) = A_e (tau_+)$ donde las fronteras coinciden exactamente ($S(tau_-) = S(tau_+)$), manteniéndose la banda certificada en forma de U $kappa(tau) < S(tau) < 1.75 kappa(tau)$ sobre el dominio $[0.117245, 0.304799]$ del Teorema 8.
     - *(c) Curva en U asintótica exacta de $S(tau)$ ($A_0 -> infinity$):* Por el Teorema 3\* ($lim_(A -> infinity) A^(1\/(theta-1)) S_A = s_infinity^* := (delta\/c_K)^(1\/(theta-1))$), la frontera verdadera reescalada converge uniformemente sobre subconjuntos compactos de $(0, 1)$ al perfil diferenciable exacto:
       $ lim_(A_0 -> infinity) A_0^(1/(theta-1)) S(tau) = s_infinity^* [tau^alpha (1 - tau)]^(-1/(theta-1)), $
       cuyo único mínimo global ocurre exactamente en la tasa óptima de Barro $tau^* = alpha\/(1 + alpha) = gamma$.
]

#proof_block[
  La función $g(tau) = tau^alpha (1 - tau)$ es estrictamente log-cóncava sobre $(0, 1)$, con derivada logarítmica $g'(tau)\/g(tau) = alpha\/tau - 1\/(1 - tau) = (tau^* - tau)\/[(1 - tau^*) tau (1 - tau)]$. Por ende, $g(tau)$ crece estrictamente en $(0, tau^*)$, alcanza su único máximo global en $tau^* = alpha\/(1+alpha) = gamma$ y decrece estrictamente en $(tau^*, 1)$, anulándose en ambos extremos. Si $A_(max) = A_0 g(tau^*) > A_("rep")$, el teorema del valor intermedio garantiza dos raíces únicas $tau_(min) in (0, tau^*)$ y $tau_(max) in (tau^*, 1)$ de $A_e (tau) = A_("rep")$. Aplicando la Proposición 1 de Milei y Reidel a $A = A_e (tau)$ resulta el punto 1, cuya diferenciación implícita exacta en la ecuación (4.2) original da:
  $ (partial log kappa(tau)) / (partial tau) = - 1 / (theta s(kappa(tau)) - 1) (partial log A_e (tau)) / (partial tau) = (tau - tau^*) / ([theta s(kappa(tau)) - 1](1 - tau^*) tau (1 - tau)), $
  negativa en $(tau_(min), tau^*)$ y positiva en $(tau^*, tau_(max))$ porque $theta s(kappa) - 1 > 0$. Para el punto 2(a), derivar $log overline(S)_("asy")(tau) = (theta - 1)^(-1) [log(D\/c_K) - log A_e (tau)]$ entrega la identidad diferencial exacta y estricta log-convexidad en $tau$; no obstante, como el Teorema 3 solo garantiza $limsup_(A -> infinity) A^(1\/r) S_A <= (D\/c_K)^(1\/r)$, conforme $A_e (tau) arrow.b A_* = A_("SN") = 0.0995245$ (cuyas raíces exactas son $tau_1 = 2.2197 times 10^(-5)$ y $tau_2 = 0.930108$) la frontera VFI $S(tau)$ converge al nodo silla interior $K_("SN") approx 0.189$ y supera a $overline(S)_("asy")(tau)$ por debajo de $A_("cross") = 0.110038$ (Apéndice A.4), quedando la certificación a $A$ finito acotada al intervalo $A_e (tau) >= 0.749$ ($tau in [0.117245, 0.304799]$) del Teorema 8. Para 2(b), la unimodalidad estricta de $A_e (tau)$ garantiza dos preimágenes únicas para cada nivel $A in (A_*, A_(max))$ y transfiere el Teorema 8 cuando $A_e (tau) >= 0.749$. Para 2(c), sustituyendo $A = A_0 tau^alpha (1 - tau)$ en el límite $A^(1\/(theta-1)) S_A -> (delta\/c_K)^(1\/(theta-1))$ probado en el Teorema 3\* se obtiene la convergencia uniforme sobre cualquier compacto $[underline(tau), overline(tau)] subset (0, 1)$ hacia la curva en U asintótica exacta.
]

== Descomposición entre gasto productivo ($tau_p$) y carga improductiva ($tau_u$)

El Teorema 10 reconcilia formalmente la matemática de Milei y Reidel (2026) con el debate de política económica sobre el tamaño óptimo del Estado. Si la carga agregada se descompone en $tau = tau_p + tau_u in (0, 1)$, donde $tau_p > 0$ financia bienes públicos productivos ($tau_p^alpha$) y $tau_u in lr([0, 1 - tau_p))$ representa gasto improductivo o costo regulatorio puro de cumplimiento (burocracia sin contrapartida productiva), la productividad efectiva neta adopta la forma bivariada $A_e (tau_p, tau_u) = A_0 tau_p^alpha (1 - tau_p - tau_u)$, de donde se desprenden dos leyes complementarias (Tabla 4):

1. *Monotonía frente a la carga improductiva $tau_u$:* Para cualquier nivel dado de provisión institucional $tau_p$, se verifica $partial A_e \/ partial tau_u = -A_0 tau_p^alpha < 0$, lo que contrae monótonamente el conjunto sostenible ($partial kappa \/ partial tau_u > 0$ y $partial overline(S)_("asy") \/ partial tau_u > 0$ *en todo punto*, y en el límite $A_0 -> infinity$ también $partial S \/ partial tau_u > 0$), recuperando la Proposición 2 de Milei y Reidel (2026) sobre la dimensión $tau_u$.
2. *Curva en U y efecto desplazamiento (crowding-out) sobre la dimensión productiva $tau_p$:* Para cada $tau_u in lr([0, 1))$ fijo, la alícuota productiva que maximiza $A_e (tau_p, tau_u)$ y minimiza tanto $kappa(tau_p, tau_u)$ como $overline(S)_("asy")(tau_p, tau_u)$ es $tau_p^* (tau_u) = frac(alpha, 1 + alpha) (1 - tau_u) = gamma (1 - tau_u)$, donde la productividad máxima escala como $A_e^* (tau_u) prop (1 - tau_u)^(1 + alpha)$ y la envolvente mínima asintótica crece como $overline(S)_("asy")^* (tau_u) = (D\/c_K)^(1\/(theta-1)) A_e^* (tau_u)^(-1\/(theta - 1)) prop (1 - tau_u)^(-(1+alpha)\/(theta-1))$. Así, recortar burocracia improductiva $tau_u$ o exceso fiscal ($tau_p > tau_p^*$) abate drásticamente las barreras de viabilidad, mientras en la rama izquierda ($tau_p < tau_p^*$) la infraestructura y los derechos de propiedad evitan la trampa de anarquía.

#figure(
  image("fig3_ucurve_es.svg", width: 100%),
  caption: [Extensión institucional de la Sección 4.3 ($A_e (tau) = A_0 tau^alpha (1 - tau)$ con $A_0 = 1.45, alpha = 0.25, tau^* = gamma = 0.20, A_("rep") = 0.073485$). El Panel (a) contrasta la productividad neta con infraestructura pública frente a la pérdida lineal pura $A(1-tau)$, delimitando las regiones de extinción física ($[0, tau_(min)]$ y $[tau_(max), 0.98]$ con $tau_(min) = 6.60 times 10^(-6), tau_(max) = 0.9486$), las bandas de extinción económica ($A_e <= A_* = A_("SN") = 0.0995$, $tau_1 = 2.22 times 10^(-5), tau_2 = 0.9301$) y el umbral $A_e = 0.749$; el Panel (b) muestra el umbral físico $kappa(tau)$, la frontera verdadera $S(tau)$ por VFI sobre $(tau_1, tau_2)$, la envolvente asintótica del Teorema 3 $overline(S)_("asy")(tau) = (D\/c_K)^2 A_e (tau)^(-2)$ (superada por $S(tau)$ por debajo de $A_("cross") = 0.1100$, $(tau_(c,1), tau_(c,2)) = (3.32 times 10^(-5), 0.9226)$) y la cota certificada a $A$ finito del Teorema 8 en $[0.117245, 0.304799]$.],
)

#v(0.2em)
#figure(
  table(
    columns: (1.0fr, 0.8fr, 0.85fr, 1.0fr, 1.25fr, 2.05fr),
    align: (center, center, center, center, center, left),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [Carga $tau$], [$A_e (tau)$], [$A_e (tau) \/ A_("rep")$], [$kappa(tau)$], [Env. $overline(S)_("asy")(tau)$], [Régimen institucional],
    table.hline(stroke: 0.6pt),
    [$5.0 times 10^(-6)$], [$0.0686$], [$0.93$], [—], [—], [Extinción física (trampa de anarquía)],
    [$2.0 times 10^(-5)$], [$0.0970$], [$1.32$], [$0.119322$], [— ($0.163590^*$)], [Extinción económica ($cal(M) != emptyset$, $S(tau)$ no existe)],
    [$0.02$], [$0.5344$], [$7.27$], [$0.002825$], [$0.005386$], [Rama izquierda (provisión subóptima)],
    [$0.05$], [$0.6514$], [$8.86$], [$0.001896$], [$0.003625$], [Expansión de infraestructura],
    [$0.10$], [$0.7339$], [$9.99$], [$0.001492$], [$0.002856$], [Cercano al óptimo institucional],
    [*$0.20$ ($tau^*$)*], [*$0.7757$*], [*$10.56$*], [*$0.001335$*], [*$0.002556$*], [*Carga óptima única (Teorema 8: $0.002331$)*],
    [$0.40$], [$0.6919$], [$9.42$], [$0.001680$], [$0.003213$], [Rama derecha (sobrecarga fiscal)],
    [$0.60$], [$0.5105$], [$6.95$], [$0.003099$], [$0.005903$], [Fuerte contracción sostenible],
    [$0.80$], [$0.2743$], [$3.73$], [$0.010990$], [$0.020448$], [Deterioro severo de viabilidad],
    [$0.90$], [$0.1412$], [$1.92$], [$0.045887$], [$0.077114$], [Antesala de colapso ($A_e > A_("cross")$)],
    [$0.94$], [$0.0857$], [$1.17$], [$0.178378$], [— ($0.209599^*$)], [Extinción económica ($cal(M) != emptyset$, $S(tau)$ no existe)],
    [$0.95$], [$0.0716$], [$0.97$], [—], [—], [Extinción física (hiperregulación)],
    table.hline(stroke: 1.1pt),
  ),
  caption: [Cuantificación de los regímenes institucionales del Teorema 10 en el modelo CES armónico ($A_0 = 1.45, alpha = 0.25, A_("rep") = 0.073485, tau_(min) = 6.60 times 10^(-6), tau_(max) = 0.948649, A_* = A_("SN") = 0.0995245, tau_1 = 2.2197 times 10^(-5), tau_2 = 0.930108$). La columna 5 reporta la envolvente asintótica $overline(S)_("asy")(tau) = (D\/c_K)^2 A_e (tau)^(-2)$ (que acota empíricamente a $S(tau)$ para $A_e >= A_("cross") = 0.110038$, y queda dominada por la cota finita certificada del Teorema 8 $0.0014025025 thin A_e (tau)^(-2) = 0.002331$ en $tau^*$ sobre $[0.117245, 0.304799]$ donde $A_e >= 0.749$). \*En $tau = 2.0 times 10^(-5)$ y $tau = 0.94$, $A_e < A_*$ implica extinción económica verificada por VFI ($S(tau)$ no existe), por lo que el valor algebraico entre paréntesis no constituye una cota de frontera.],
)

= Extensiones Estructurales: Descentralización Empresarial, Crecimiento Sostenido y Barreras Estocásticas

Mientras que las discusiones de política económica en torno a la escala mínima viable enfatizan el rol de las grandes empresas, las leyes antimonopolio, el crecimiento exponencial de largo plazo («palo de hockey») y las crisis macroeconómicas, el modelo matemático base de Milei y Reidel (2026) se formula para un planificador central determinista acotado por un techo estacionario $K_p^+$. Demostramos a continuación cómo incorporar formalmente estas tres dimensiones preservando de manera exacta sus teoremas y certificados.

== Descentralización, poder de mercado y el costo de fragmentar empresas

Con rendimientos crecientes a escala $theta in (1, 2)$, el Teorema de Euler implica $K F_(A,K) + L F_(A,L) = theta F_A (K, L) > F_A (K, L)$, por lo que firmas tomadoras de precios en competencia perfecta sin externalidades incurrirían en pérdidas operativas $(1 - theta) Y_t < 0$. Existen dos descentralizaciones canónicas compatibles con la tecnología CES (2.1): (i) *competencia monopolística u oligopolio simétrico* (Dixit y Stiglitz, 1977) con margen de precios (*markup*) $mu >= theta > 1$, donde cada firma remunera a los factores según $R_t^K = (1\/mu) F_(A,K)$ y $w_t = (1\/mu) F_(A,L)$ y la fracción restante $(1 - theta\/mu) Y_t >= 0$ cubre costos fijos operativos de intermediación y entrada; o bien (ii) *externalidades agregadas de escala* (Romer, 1986), donde cada firma opera con rendimientos constantes sobre sus insumos privados y productividad externa dada por la escala agregada.

#thm_box("Proposición 2* (Descentralización con escala empresarial, contabilidad factorial y fragmentación)")[
  Bajo la tecnología CES (2.1) con $theta in (1, 2)$ y $r = theta - 1 > 0$:
  1. *Teorema de fragmentación regulatoria o antimonopolio:* Si una regulación o intervención estatal fragmenta los insumos agregados $(K_t, L_t)$ en $N_f >= 1$ empresas simétricas aisladas ($K_(i,t) = K_t \/ N_f$, $L_(i,t) = L_t \/ N_f$), el producto agregado se contrae exactamente como:
  $ Y_t^((N_f)) = sum_(i=1)^(N_f) F_A (K_t / N_f, L_t / N_f) = N_f dot N_f^(-theta) F_A (K_t, L_t) = F_(A \/ N_f^r) (K_t, L_t). $
  En consecuencia, fragmentar la escala empresarial en $N_f$ unidades es *matemáticamente isomorfo* a destruir la productividad total de los factores a $A_("ef") (N_f) = A \/ N_f^(theta - 1)$, lo que multiplica la Escala Mínima Viable por un factor $N_f$ en el régimen asintótico ($S_A (N_f) = Theta(N_f dot S_A)$), induce extinción económica ($S_A (N_f)$ deja de existir aunque $cal(M)(N_f) != emptyset$) cuando $N_f >= N_(f,"SN") := (A \/ A_*)^(1\/(theta - 1))$ ($N_(f,"SN") = 56.79$ en la parametrización base), y provoca la extinción física global ($cal(M)(N_f) = emptyset$) siempre que $N_f >= N_(f,"rep") := (A \/ A_("rep"))^(1\/(theta - 1))$ ($N_(f,"rep") = 104.17$).
  2. *Contabilidad factorial exacta, ruptura del isomorfismo de Bellman y brecha de subinversión descentralizada:* Si las firmas remuneran los factores a $R_t^K = (1\/mu) F_(A,K)$ y $w_t = (1\/mu) F_(A,L)$ bajo competencia monopolística con margen $mu >= theta > 1$, por el Teorema de Euler el ingreso factorial agregado percibido por los hogares asciende exactamente a:
  $ R_t^K K_t + w_t L_t = theta / mu F_A (K_t, L_t) = F_(A_("mkt")) (K_t, L_t), quad A_("mkt") := theta / mu A <= A. $
  Sin embargo, dado que los hogares tomadores de precios optimizan sobre la restricción presupuestaria lineal $C_t + K_(t+1) <= (q + R_t^K) K_t + w_t L_t + Pi_t$, los precios factoriales percibidos retienen una cuña marginal persistente respecto de la tecnología reescalada $F_(A_("mkt"))$:
  $ R_t^K = 1 / mu F_(A,K) = 1 / theta F_(A_("mkt"),K), quad w_t = 1 / mu F_(A,L) = 1 / theta F_(A_("mkt"),L), quad 1 / mu <= 1 / theta < 1. $
  Por consiguiente, *no existe un isomorfismo de Bellman* con el planificador en $A_("mkt")$:
  - *(Cierre con costos fijos operativos / libre entrada):* Aunque la participación residual $(1 - theta\/mu) Y_t >= 0$ agote los beneficios netos ($Pi_t = 0$) de modo que la restricción presupuestaria agregada iguale a la del planificador en $A_("mkt")$, la cuña marginal $1\/theta < 1$ persiste incluso en el límite $mu = theta$ ($A_("mkt") = A$, al igual que en la descentralización CRS con externalidades de Romer, 1986), deprimiendo el retorno privado del ahorro y abriendo una trampa de coordinación descentralizada $[S_A, S^("eq")(mu))$ con $S^("eq")(mu) > S_(A_("mkt")) >= S_A$ ya en $mu = theta$. Aquí $K_("lo") (mu)$ denota el estado estacionario inestable inferior sobre la variedad estable convergente hacia $K_("hi") (mu)$, de modo que toda trayectoria monótona hacia $K_("hi") (mu)$ exige $K_0 >= K_("lo") (mu)$, fijando $S^("eq")(mu) >= K_("lo") (mu)$ (en el modelo base, $K_("lo") = 0.003039 > S_A = 0.001587$ para $mu = 1.5$).
  - *(Cierre con reembolso de beneficios puros):* Si $(1 - theta\/mu) Y_t > 0$ ($mu > theta$) se distribuye como transferencia exógena de suma fija (*lump-sum*) $Pi_t$ a los hogares ($partial Pi_t \/ partial K_t = 0$), la forma algebraica de la ecuación de Euler y de la condición intratemporal no cambia respecto de $R_t^K, w_t$ (con cuña $1\/mu <= 1\/theta < 1$), pero el efecto riqueza positivo de $Pi_t$ eleva el consumo $C_t$, reduce la oferta laboral $L_t$ y deprime $R_(t+1)^K$, reduciendo el estado estacionario alto $K_("hi")$ y elevando adicionalmente el umbral de trampa $K_("lo")$ respecto del cierre con costos fijos (por ejemplo, de $0.004490$ a $0.004670$ en $mu = 1.8$, y de $0.005644$ a $0.006055$ en $mu = 2.0$).
]

#proof_block[
  Por homogeneidad de grado $theta = 1 + r$ de $F_A (K, L) = A [w K^rho + (1 - w) L^rho]^(theta\/rho)$, se verifica $F_A (K\/N_f, L\/N_f) = N_f^(-theta) F_A (K, L)$. Sumando sobre las $N_f$ firmas se obtiene $Y_t^((N_f)) = N_f^(1-theta) F_A (K, L) = F_(A N_f^(-r)) (K, L)$. Aplicando la Proposición 1, la definición de $A_* = A_("SN") = 0.0995245$ y el Teorema 3 de Milei y Reidel a $tilde(A) = A N_f^(-r)$, el conjunto sostenible es vacío si y solo si $A N_f^(-r) <= A_("rep")$ ($N_(f,"rep") = (0.75\/0.073485)^2 = 104.17$), la extinción económica ocurre cuando $A N_f^(-r) <= A_*$ ($N_(f,"SN") = (0.75\/0.0995245)^2 = 56.79$), y el umbral crítico escala como $S_(tilde(A)) = Theta(tilde(A)^(-1\/r)) = N_f dot Theta(A^(-1\/r))$. Por su parte, la identidad de Euler $K F_(A,K) + L F_(A,L) = theta F_A (K, L)$ garantiza $R_t^K K_t + w_t L_t = (theta\/mu) F_A (K_t, L_t) = F_(A_("mkt")) (K_t, L_t)$. Dado que $F_A$ es lineal en $A$, $F_(A,K) = (A \/ A_("mkt")) F_(A_("mkt"),K) = (mu \/ theta) F_(A_("mkt"),K)$, lo que se traduce en $R_t^K = (1\/mu) F_(A,K) = (1\/theta) F_(A_("mkt"),K)$ y $w_t = (1\/mu) F_(A,L) = (1\/theta) F_(A_("mkt"),L)$, rompiendo la coincidencia con la ecuación de Euler del planificador en $A_("mkt")$ por el factor $1\/theta < 1$. El trazado numérico de la variedad estable hacia $K_("hi")$ desde el estado estacionario inestable $K_("lo")$ (Apéndice A.4) confirma $K_("lo") > S_(A_("mkt"))$ en todos los cierres para $mu in {1.5, 1.8, 2.0}$, y muestra que bajo reembolso $Pi_t = (1 - theta\/mu) Y_t > 0$ el efecto riqueza sobre el ocio contrae $L_t$ (de $0.6755$ a $0.6226$ en $mu = 1.8$), abatiendo $R_(t+1)^K$ y ampliando el umbral $K_("lo")$.
]

== Eliminación del techo estacionario $K_p^+$ y el «palo de hockey» del crecimiento sostenido

En el modelo base de Milei y Reidel, la cota laboral $L_t <= 1$ y la complementariedad bruta $rho < 0$ imponen una asíntota horizontal al producto $F_A (K, 1) < A (1 - w)^(theta\/rho)$, generando un techo estacionario $K_p^+ < infinity$. La siguiente proposición muestra que al incorporar progreso técnico aumentador de trabajo exógeno a tasa $g > 0$, se elimina el techo $K_p^+$ y se obtiene crecimiento exponencial perpetuo («palo de hockey») *preservando intactas las pruebas y constantes verificadas en unidades de eficiencia* —en contraste nítido con los modelos de aprendizaje endógeno *learning-by-doing* al cruzar $H$, cuya modificación del valor de continuación sí exige recalibrar las cotas de la Sección 3 (Nota al pie 2).

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
  Dividiendo la restricción física $C_t + K_(t+1) <= q K_t + (1 + g)^t F_A (K_t \/ (1 + g)^t, L_t)$ por $(1 + g)^(t+1)$ se obtiene de inmediato $tilde(C)_t + hat(K)_(t+1) <= tilde(q) hat(K)_t + F_(tilde(A)) (hat(K)_t, L_t)$. Dado que $sum_(t=0)^infinity beta^t eta (t + 1) log(1 + g) < infinity$ es constante respecto de las decisiones $(hat(K)_(t+1), L_t)$, el conjunto de trayectorias óptimas de $hat(K)_t$ coincide punto por punto con el del modelo estacionario de parámetros $(tilde(A), tilde(q))$.#footnote[Si en lugar de progreso técnico exógeno se intenta modelar crecimiento endógeno mediante externalidades de conocimiento $Gamma_t L_t$ (Romer, 1986) activadas al cruzar $h = 0.28$ ($Gamma_t = 1$ para $K_t < h$ y $Gamma_t = K_t \/ h$ en $H = lr([h, infinity))$), la geometría y las cotas de la Sección 3 *no* permanecen inalteradas. En efecto, sustituir $Gamma_t L_t = (K_t \/ h) L_t$ directamente en la función CES con $theta = 3\/2$ genera producto superlineal $prop K_t^(3\/2)$ que hace diverger el bienestar ($V = +infinity$ pues $beta theta = 1.455 > 1$), mientras que imponer $theta = 1$ en $H$ introduce un salto discontinuo de $+51.2\%$ en $(h, 1)$ ($0.217034 -> 0.328125$). La especificación continua por tramos requiere $Y_t = (K_t \/ h) F_A (h, L_t)$ sobre $H = [h, infinity)$. Aun bajo esta formulación continua, el crecimiento $A K$ perpetuo eleva la función de valor en $h = 0.28$ al menos a $V_("AK")(0.28) >= +240.7598 >> Psi^sharp (0.28) = -27.870334$, invalidando el techo $Psi^sharp >= V$ de la Sección 3 y exigiendo recalibrar tanto la cota superior en $H$ como los certificados de salida adversa.]
]

== Incertidumbre macroeconómica y Barreras de Bellman Estocásticas (Teorema de Doob)

Una ventaja metodológica fundamental de las *Barreras de Bellman de Primer Paso (FPBB)* de la Sección 6 de Milei y Reidel (2026) frente a las pruebas deterministas clásicas de Dechert y Nishimura (1983) es que las desigualdades de barrera se extienden naturalmente a entornos estocásticos mediante la teoría de martingalas y el *Teorema de Parada Opcional de Doob* (Doob, 1953). Sin embargo, limitarse a evaluar una cota ex-post como $(1 - p)^23$ con el horizonte determinista de $p = 0$ supondría implícitamente agentes miopes actuando con $beta = 0.97$ ($p = 0$), ignorando que agentes con expectativas racionales que anticipan probabilidad anual de crisis $p > 0$ modifican ex ante su ahorro $K'^((p)) (K)$, su esfuerzo laboral $L^((p)) (K)$ y su factor efectivo de impaciencia.

Para ordenar con claridad los resultados matemáticos puros, los certificados asistidos por computadora y la evidencia cuantitativa, separamos esta extensión en tres niveles: (1) un resultado analítico general de supermartingala detenida (*Lema 2*); (2) los certificados computacionales continuos `log-PWL` de plazos endógenos $T^*(p)$ bajo riesgo de ruina y el sistema matricial acoplado de Markov $(B_G, B_B)$ en $32$ subcajas (*Proposición 4\**); y (3) un experimento numérico mediante VFI estocástica continua de sección áurea de $880$ puntos (Tabla 5) que caracteriza la dicotomía conductual entre riesgo de ruina y crisis recuperables.

#thm_box("Lema 2 (Certificado estocástico FPBB de supermartingala y parada opcional de Doob)")[
  Sea $(omega_t)_(t>=0)$ un proceso de shocks macroeconómicos Markovianos sobre un espacio $(Omega, cal(F), bb(P))$ que afecta los parámetros primitivos en cada período, bajo la condición de integrabilidad $sup_(t <= T) bb(E)[ |V(K_(t and tau), omega_(t and tau))| ] < infinity$ para todo horizonte finito $T >= 1$. Sea $B : lr([b, infinity)) times Omega -> bb(R)$ una función medible y acotada en $[b, h)$ que satisface la desigualdad de Bellman en un paso para toda acción de permanencia en $M = lr([b, h))$ y toda acción de salida ascendente hacia $H = lr([h, infinity))$:
  $ B(K, omega) >= rho.alt(K, omega, a) + beta bb(E) [ B(K', omega') | K, omega, a ] quad (K in M, K' >= b). $
  Considérese cualquier política que evite salidas por debajo de $b$ (es decir, $K_tau >= b$ casi seguramente en el tiempo de parada $tau = inf{t >= 0 : K_t in.not M}$, donde $[b, infinity)$ pertenece al dominio de $B$) y tal que $bb(E)[sum_(j=0)^((t and tau)-1) beta^j |rho.alt_j| ] < infinity$. Entonces el proceso detenido $Z_(t and tau) := beta^(t and tau) B(K_(t and tau), omega_(t and tau)) + sum_(j=0)^((t and tau)-1) beta^j rho.alt_j$ es una *supermartingala* integrable respecto de la filtración natural $cal(F)_t$. Por el Teorema de Parada Opcional de Doob, para todo horizonte $T >= 1$:
  $ bb(E)_(x_0, omega_0) [J(pi)] <= B(x_0, omega_0) + bb(E)_(x_0, omega_0) [ beta^(T and tau) ( V(K_(T and tau), omega_(T and tau)) - B(K_(T and tau), omega_(T and tau)) ) ]. $
]

#proof_block[
  La desigualdad de Bellman extendida para $K in M$ y $K' >= b$, la condición $K_tau >= b$ c.s. y la integrabilidad dan $bb(E)[Z_((t+1) and tau) - Z_(t and tau) | cal(F)_t] = beta^t bb(1)_(tau > t) { rho.alt(K_t, omega_t, a_t) + beta bb(E)[B(K_(t+1), omega_(t+1)) | cal(F)_t] - B(K_t, omega_t) } <= 0$, de modo que $(Z_(t and tau))$ es una supermartingala integrable y el Teorema de Parada Opcional de Doob en $T and tau$ produce inmediatamente la cota de valor.
]

#thm_box("Proposición 4* (Certificados computacionales de plazos endógenos T*(p) y barreras acopladas de Markov)")[
  Aplicando el Lema 2 sobre la caja paramétrica (7.3) mediante super-barreras continuas `log-PWL` certificadas en $(0, infinity)$:
  1. *Certificado endógeno $T^*(p)$ bajo riesgo anticipado de ruina/colapso ($tilde(beta)_p := beta(1 - p)$):* Supongamos que en cada fecha $t$ (con anticipación ex ante de los agentes), con probabilidad $1 - p$ rige la caja normal (7.3) y con probabilidad $p in (0, 1)$ ocurre un shock catastrófico absorbente con valor de continuación presente de ruina común $U_0 in bb(R)$ para siempre. Sustrayendo el valor constante invariante $frac(beta p U_0, 1 - tilde(beta)_p)$, tanto la optimización dinámica como la supermartingala detenida de Doob se reducen exactamente al problema de descuento efectivo $tilde(beta)_p = beta(1 - p)$. Definiendo la barrera afín estocástica extendida a $[b, infinity)$ como $B_1^((p)) (x) := B_*^((p)) - frac(eta q (h - x)_+, C_(max))$ con $B_*^((p)) = frac(hat(R) - Delta_2 (p), 1 - tilde(beta)_p)$, los testigos explícitos factibles de $25$ pasos $W_X^((p))$ (evaluados en el peor caso de pagos negativos $beta_+ (1 - p)$) y la super-barrera continua `log-PWL` $Psi^((p))$ certificada uniformemente en la caja (7.3) sobre todo $(0, infinity)$ (ya que la familia paramétrica $a_p K - b_p K^(-1\/2) + c_p$ presenta singularidad en $(0, 0.0014)$ por encima de $p_("sing") = 1 - sqrt(q_+)\/beta_+ = 1.1217\%$):
     - En toda la caja (7.3), los márgenes de permanencia, de salida adversa sobre el continuo de $M$ y en $H_1$ (incluyendo el criterio derivativo continuo de no salida $< b$) permanecen estrictamente positivos para todo $p in lr([0, 2.00%])$, con ruptura de certificación de la barrera de un paso en *$p_("cert") = 2.0434\%$* (pese a que la condición local de paciencia en $kappa_A$ quiebra ya en $p_("pat") = 0.8723\%$, $0.8573\%$ en el extremo adverso de la caja, porque los retornos brutos en $M$ alcanzan $1.631$–$1.667$, y hasta $1.831$ en $A_+$);
     - El plazo máximo certificado de entrada antes de una crisis *$T^*(p)$ crece endógenamente con $p$* ($T^*(0) = 22$, $T^*(0.5\%) = 25$, $T^*(1.0\%) = 30$, $T^*(1.5\%) = 40$, $T^*(2.0\%) = 84$), demostrando que la cota inferior certificada válida bajo anticipación racional $bb(P)_p ("Supervivencia hasta " H) >= (1 - p)^(T^*(p))$ cae hasta *$0.1832$* en $p = 2.0\%$, frente a la cota miope $(1 - 0.02)^23 = 0.6283$ obtenida al aplicar el horizonte determinista de $p = 0$ (ambas son cotas de peor caso, por debajo de la supervivencia efectiva a lo largo de la senda testigo de entrada en $4$ períodos).
  2. *Sistema acoplado de barreras Markovianas $(B_G, B_B)$ para recesiones recuperables:* Bajo un proceso de Markov sobre $Omega = {G, B\}$ entre normalidad ($A_G in [0.749, 0.751]$) y recesión severa recuperable ($A_B in [0.349, 0.351]$, donde $kappa(A_B) = 0.0066 < b$), con matriz de transición $P = mat(1 - p, p; p_("rec"), 1 - p_("rec"))$ ($p_("rec") = 1\/3$), el par acoplado extendido $B_omega (x) = B_(*, omega) - m_omega (h - x)_+$ con $m_omega = eta_- q_- \/ C_(max, omega)$ resuelve en forma cerrada el sistema lineal $2 times 2$:
  $ (I - beta_- P) mat(B_(*, G); B_(*, B)) = mat(hat(R)_G; hat(R)_B) - mat(Delta_G (p, p_("rec")); Delta_B (p, p_("rec"))), quad Delta_omega := (h - b) min lr((eta_- / C_(max, omega), beta_- (P bold(m))_omega)). $
  Empalmado con testigos estacionarios factibles sobre malla $(W_G, W_B)$ y super-barreras acopladas continuas `log-PWL` $(Psi_G, Psi_B)$ en $(0, infinity)$ bajo $beta$ acoplado en $\{0.9699, 0.9701\}$ y cobertura de $32$ ($4 times 2 times 2 times 2$) subcajas de la caja (7.3) (con verificación continua de no salida $< b$ sobre todo $M$), el sistema certifica márgenes positivos punto a punto para todo $p in {0\%, 0.5\%, 1.0\%, 1.5\%, 2.0\%, 5.0\%, 8.0\%, 12.0\%}$ ($m_("exit")^(M,G) >= +1.15$, $m_("exit")^(M,B) >= +0.053$ con continuo $>= +0.032$, $m_("exit")^(H,G) >= +0.55$, $m_("exit")^(H,B_("32bx")) >= +0.013$, y raíz extrapolada de permanencia en $B$ hasta $p_("cert")^("Markov") = 15.45\%$), descartando trampas de estancamiento ($bb(P)(tau = infinity) = 0$) y garantizando cotas explícitas de escape probabilístico en $T^*_omega (p)$ períodos.
]

#proof_block[
  En el punto 1, a lo largo de cualquier senda que permanece en $M$ hasta $T and tau$, el flujo acumulado esperado de eventos de ruina más la fracción de continuación $tilde(beta)_p^(T and tau) (beta p U_0)\/(1 - tilde(beta)_p)$ suma idénticamente $frac(beta p U_0, 1 - tilde(beta)_p)$, igual al componente de ruina de $W_X^((p))$, cancelando $U_0$ exactamente. Para transiciones de salida ascendente $x in M, y >= h$, $(h - y)_+ = 0$ da $B_1^((p))(y) = B_*^((p))$ y $c_1 - c_0 >= q(h - x) + (h - b)$, validando la desigualdad de Bellman también en el paso de salida porque $Delta_2 (p) < eta_- (h - b)\/C_(max)$. Como la familia $a_p x - b_p x^(-1\/2) + c_p$ solo satisface $T Psi <= Psi$ en la cola inferior cuando $beta_+ (q_+)^(1\/2) > 1$ (fallando por encima de $p_("sing") = 1 - sqrt(q_+)\/beta_+ = 1.1217\%$ y degradándose ya desde $0.5\%$), sustituimos $Psi^((p))$ por una super-barrera continua `log-PWL` certificada en todo $(0, infinity)$ mediante B&B en $[10^(-8), 90.0]$ más colas analíticas contractivas en $(0, 10^(-8)]$ y $[90.0, infinity)$ uniformemente para $(tilde(beta)_p^-, tilde(beta)_p^+)$. Asimismo, la condición $tilde(beta)_p^- min_((0, b]) d Psi^((p)) \/ d y > eta_+ \/ c_("opt")(b)$ descarta óptimamente toda salida hacia $< b$ (verificado continuamente sobre una cobertura de $M$). Al depender $rho.alt(K, s)$ de $K$ sin intervención de $tilde(beta)_p$, la monotonía de la Proposición 1\*\* se preserva intacta. En el punto 2, para cada $(x, y) in M times M$ y $omega in {G, B\}$, la linealidad en $y$ de $eta y\/C_(max, omega) + beta_- (P bold(m))_omega (h - y)$ fija su mínimo en $y in {b, h}$, validando $rho.alt_omega (x, y) + beta bb(E)[B(y, omega') | omega] <= B(x, omega)$ exactamente cuando $(I - beta_- P) bold(B)_* = hat(bold(R)) - bold(Delta)$ (y verificándose también la arista de salida $y >= h$ porque $Delta_omega <= eta_- (h - b)\/C_(max, omega)$). Dado que $rho(beta_- P) = beta_- < 1$, la inversión es positiva; más aún, como $s_M = 0.135$ es infactible bajo $A_B$ ($c_M^B (0.10) < 0$) y la familia paramétrica $x^(-1\/2)$ no logra certificar $m_("exit")^(M,B) >= 0$, la certificación acoplada `log-PWL` sobre $32$ subcajas junto con el criterio derivativo continuo $< b$ ($beta_- min_((0,b]) d bb(E)_omega [Psi]\/d y > eta_+ \/ c_("opt",omega)(b)$) garantiza $K_tau >= b$ c.s. y $bb(P)(tau > T^*_omega) < 1$. Desde $x_0 = 0.10$ bajo $(A_+, q_+)$, las cotas máximas $K_1 <= 0.150233 < K_2 <= 0.238496 < 0.28 <= K_3 <= 0.398940$ ($y_(max) = 0.474952$) prueban $tau >= 3$, acotando $bb(P)(tau <= T)$ desde abajo (para $T = T^*_G + 4$) vía $[W_omega - B_omega - beta_+^T max(Psi - B_*)]\/[beta_+^3 max(Psi(y_(max)) - B_*) - beta_+^T max(Psi - B_*)] > 0$ (desde $0.120$ en $p = 0\%$ hasta $0.057$ en $p = 12\%$).
]

*Experimento numérico: dicotomía de política óptima anticipatoria (VFI estocástica continua):* Resolviendo ambos modelos estocásticos mediante VFI continua de sección áurea de $880$ puntos acelerada por Howard (coincidiendo exactamente en $p = 0.0\%$), cuando los optimizadores internalizan $p > 0$ cada año la respuesta de política exhibe una dicotomía nítida (Tabla 5 y Figura 4): el riesgo de ruina irreversible ($tilde(beta)_p$) deprime la inversión $K'^((p)) (0.10)$ y el trabajo $L^((p)) (0.10)$ y casi triplica la frontera crítica $S^("ruin")(p)$ ($0.001588 -> 0.004589$ en $p = 8\%$; nótese que $S^("ruin")(p)$ sigue existiendo y siendo único vía el Teorema 1 a $A = 0.75$ incluso por encima de $p_("pat") = 0.8723\%$ porque la condición 2.3 solo gobierna la paciencia local en $kappa_A$ cuando $A -> infinity$, mientras el retorno bruto máximo $q + F_(A,K)(K, 1)$ alcanza $1.8307 >> 1\/tilde(beta)_(0.08) = 1.1206$ y $tilde(beta)_p theta > 1$ rige hasta $p approx 31.3\%$), mientras que una crisis recuperable ($A_G <-> A_B$) activa una *«huida hacia la seguridad»* en la que tanto $K'^((G)) (0.10)$ como $L^((G)) (0.10)$ *aumentan* con $p$ (más intensamente cuanto menor es la tasa de recuperación $p_("rec")$), con $S_G (p)$ y el salto de Skiba $S_B^("kink")(p)$ creciendo suavemente en tanto el punto de inversión neta nula $K_B^*(p)$ desciende.

#v(0.2em)
#figure(
  text(size: 7.2pt, table(
    columns: (0.58fr, 0.58fr, 1.12fr, 1.15fr, 1.75fr, 2.02fr),
    align: (center, center, center, center, center, center),
    stroke: none,
    inset: (x: 2.5pt, y: 3.5pt),
    table.hline(stroke: 1.1pt),
    [Riesgo $p$], [Doob \ $T^*(p)$], [$bb(P)_("Doob") (p)$ vs. \ $(1 - p)^23$], [Markov $2 times 2$ \ $B_G (0.10)$ / $T^*_G$], [VFI Ruina ($tilde(beta)_p$) \ $S^("ruin")(p)$ ; $K'^((p))(0.10)$ ; $L^((p))$], [VFI Markov ($G\/B$) \ $S_G ; S_B^("kink") ; K_B^*$ \ $K'^((G))(0.10) ; L^((G))$],
    table.hline(stroke: 0.6pt),
    [$0.0\%$], [*$22$*], [*$1.0000$* / $1.0000$], [$-43.358$ / $21$], [$0.001588$ ; $0.13364$ ; $0.6626$], [$0.001588$ ; $0.00166$ ; $0.01086$ \ $0.13364$ ; $0.6626$],
    [$0.5\%$], [*$25$*], [*$0.8822$* / $0.8911$], [$-43.508$ / $21$], [$0.001670$ ; $0.13324$ ; $0.6579$], [$0.001603$ ; $0.00168$ ; $0.01062$ \ $0.13373$ ; $0.6638$],
    [$1.0\%$], [*$30$*], [*$0.7397$* / $0.7936$], [$-43.654$ / $22$], [$0.001769$ ; $0.13294$ ; $0.6545$], [$0.001608$ ; $0.00169$ ; $0.01062$ \ $0.13379$ ; $0.6645$],
    [$1.5\%$], [*$40$*], [*$0.5463$* / $0.7064$], [$-43.796$ / $22$], [$0.001884$ ; $0.13254$ ; $0.6502$], [$0.001622$ ; $0.00171$ ; $0.01062$ \ $0.13386$ ; $0.6654$],
    [$2.0\%$], [*$84$*], [*$0.1832$* / $0.6283$], [$-43.935$ / $23$], [$0.002013$ ; $0.13219$ ; $0.6464$], [$0.001636$ ; $0.00172$ ; $0.01062$ \ $0.13392$ ; $0.6660$],
    [$5.0\%$], [$> p_("cert")$], [— / $0.3074$], [$-44.695$ / $25$], [$0.003053$ ; $0.12990$ ; $0.6225$], [$0.001703$ ; $0.00179$ ; $0.01038$ \ $0.13435$ ; $0.6710$],
    [$8.0\%$], [$> p_("cert")$], [— / $0.1471$], [$-45.353$ / $29$], [*$0.004589$* ; *$0.12757$* ; *$0.6008$*], [*$0.001774$* ; *$0.00187$* ; *$0.00991$* \ *$0.13475$* ; *$0.6759$*],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Verificación estocástica conjunta del Lema 2 y Proposición 4\* sobre la caja (7.3): certificado continuo `log-PWL` de Doob bajo anticipación ($p_("cert") = 2.0434\%$), sistema acoplado de Markov de $32$ subcajas ($A_G = 0.75 <-> A_B = 0.35, p_("rec") = 1\/3$, certificado punto a punto hasta $p = 12\%$ donde $B_G = -46.103, T^*_G = 33, T^*_B = 88$), y contraste en VFI continua de sección áurea de $880$ puntos (coincidencia exacta en $p = 0\%$, sensibilidad a $p_("rec")$ en $p = 8\%$: $p_("rec") = 0.20 => S_G = 0.001836, K'^((G)) = 0.13511, L^((G)) = 0.6803$; $p_("rec") = 0.50 => S_G = 0.001735, K'^((G)) = 0.13447, L^((G)) = 0.6726$).],
)

#figure(
  image("fig4_structural_es.svg", width: 100%),
  caption: [Extensiones estructurales del modelo. El Panel (a) muestra trayectorias reales de política VFI desde $K_0 = 0.06$ comparando escala consolidada ($N_f = 1$ con $g = 0$ frente a crecimiento balanceado $g = 0.025$) y duopolio ($N_f = 2$, aún sobreviviente desde $K_0 = 0.06$) frente al colapso hacia la extinción bajo fragmentación regulatoria ($N_f = 60 > N_(f,"SN") = 56.79$, $A_("ef") = A\/N_f^(theta-1)$); el Panel (b) compara la cota inferior certificada válida bajo anticipación del riesgo $(1 - p)^(T^*(p))$ ($tilde(beta)_p = beta(1 - p)$, $T^*(p) = (22, 25, 30, 40, 84)$, ruptura en $p_("cert") = 2.04\%$) frente a las cotas deterministas miopes $(1 - p)^23$ (Teorema 9\* / *MR-Tabla 4*) y $(1 - p)^46$.],
)

= Conclusión

El trabajo _Minimum Viable Scale: Bellman Barriers and the Economics of Survival_ de Milei y Reidel (2026) introduce una estructura matemática rigurosa y original para analizar trampas de extinción y certificar trayectorias óptimas en modelos no cóncavos con trabajo endógeno. En este documento hemos desarrollado cuatro extensiones y refinamientos analíticos que responden sus preguntas abiertas principales, refuerzan los márgenes cuantitativos del certificado FPBB y amplían su alcance económico:

1. *Afilamiento completo del certificado FPBB (Sección 3):* Sin alterar un solo parámetro ni supuesto de la Sección 7.2, reemplazar la cota por pares disjuntos de la ecuación (7.6) por nuestra *barrera regional afín de un paso* ($B_1 (K)$ en el Lema 1 y el Teorema 9\*) casi triplica el margen de calibración en la región de tránsito ($> 7.4665$) y *reduce exactamente a la mitad el plazo máximo certificado de entrada* a la región productiva (de $46$ a *$23$ períodos*, y a $33$ períodos totales desde $K_0 = 0.05$ vía la Proposición 1\*, afilables a $tau_(.1) <= 9$ y $tau_H <= 21$–$22$ en el Corolario 1; el análisis restringido en $M$ muestra además que la barrera óptima regional $B_("opt")$ alcanza $T = 9$ y la VFI libre entra en $<= 4$ períodos). Complementariamente, el certificado analítico y de aritmética de intervalos de la Proposición 1\*\* excluye mínimos interiores y colapsa las doce particiones finitas de *MR-Tabla 5* a dos bordes, elevando el margen de salida adversa en $M$ a $> 0.0947$ y ampliando el margen global certificado del Teorema 9 de $0.0423$ ($0.04$) a *$> 0.0571$* ($+35\%$).
2. *Convergencia asintótica, criterio variacional e isomorfismo laboral (Sección 4):* El análisis en unidades críticas $K = A^(-1\/r) k$ junto con el isomorfismo exacto $S_A^("fix") (overline(L)) = overline(L) S_(A overline(L)^r)^("fix") (1)$ del Teorema 3\* resuelven asintóticamente ($A -> infinity$) la pregunta abierta de la Nota al pie 1: probamos bajo la condición de paciencia que ambas fronteras reescaladas convergen al límite físico común $(delta\/c_K)^(1\/r)$ ($S_A \/ S_A^("fix") (overline(L)) -> 1$), extendemos dicha convergencia asintótica bajo la condición debilitada $beta theta > 1$ (Corolario 2, corroborado por VFI en $beta = 0.90$), establecemos una condición variacional precisa sobre trayectorias extintas óptimas o confinadas en $(0, S_A]$ con piso uniforme $chi_p^("fix") = Omega(1) > 0$ para $S_A^("fix") (1) < S_A$, y verificamos numéricamente la convergencia de fronteras mediante VFI hasta $A = 10^8$ (cociente $1.01997$ a $1.00039$).
3. *Curva en U institucional y descomposición fiscal–regulatoria (Sección 5):* La microfundación con gasto público productivo endógeno ($G_t = tau_p Y_t$) y carga improductiva ($tau_u$) en la Sección 4.3 genera el Teorema 10, delimitando la extinción física ($tau < tau_(min)$, $tau > tau_(max)$) y la extinción económica ($A_e <= A_* = A_("SN") = 0.0995245$), separando la curva en U diferenciable exacta del piso físico $kappa(tau)$ y de la envolvente asintótica $overline(S)_("asy")(tau)$ frente a la cota certificada a $A$ finito del Teorema 8 ($A_e >= 0.749$) en $tau^* = alpha\/(1+alpha) = gamma$, la simetría por pares de la frontera verdadera $S(tau)$ a $A_0$ finito y su perfil asintótico límite cuando $A_0 -> infinity$, además de confirmar que reducir peso muerto $tau_u$ abate incondicionalmente las barreras de viabilidad.
4. *Descentralización, crecimiento perpetuo y barreras estocásticas (Sección 6):* Finalmente, formulamos la descentralización bajo competencia monopolística con contabilidad factorial consistente $(theta\/mu) Y_t$ —demostrando que la cuña marginal $1\/mu <= 1\/theta < 1$ impide el isomorfismo de Bellman y abre una trampa descentralizada ya en $mu = theta$, mientras fragmentar empresas en $N_f$ unidades contrae la TFP como $A\/N_f^(theta-1)$ con extinción económica ya en $N_(f,"SN") = 56.79$ frente a $N_(f,"rep") = 104.17$—, eliminamos el techo estacionario $K_p^+$ mediante unidades de eficiencia para generar crecimiento exponencial perpetuo (contrastándolo con la recalibración requerida bajo un régimen $A K$ continuo), y cerramos la extensión estocástica mediante el Lema 2 de Doob, los certificados computacionales `log-PWL` de la Proposición 4\* ($T^*(p)$, $p_("cert") = 2.0434\%$, barreras acopladas de Markov $(B_G, B_B)$ certificadas en $32$ subcajas sobre $p in [0\%, 12\%]$) y el experimento VFI estocástica continua de sección áurea de $880$ puntos.

#heading(numbering: none)[Referencias]

#[
#set text(size: 9.8pt)
#set par(first-line-indent: 0pt, hanging-indent: 1.5em, leading: 0.54em)
#set list(spacing: 0.34em)
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
- Milei, J., y D. Reidel (2026): _Minimum Viable Scale: Bellman Barriers and the Economics of Survival_, Working Paper, Octubre 2026 (edición de referencia para la numeración de teoremas, constantes y tablas base; posteriormente actualizado como _Extinction and Escape under Increasing Returns_, Noviembre 2026).
- Milgrom, P., y I. Segal (2002): «Envelope Theorems for Arbitrary Choice Sets», _Econometrica_, 70(2), 583–601.
- Mitra, T., y D. Ray (1984): «Dynamic Optimization on a Non-Convex Feasible Set: Some General Results for Non-Smooth Technologies», _Journal of Economics_ (_Zeitschrift für Nationalökonomie_), 44(2), 151–175.
- Noroozi, N., R. Geiselhart, L. Grüne, y F. R. Wirth (2020): «Control of Discrete-Time Nonlinear Systems via Finite-Step Control Lyapunov Functions», _Systems & Control Letters_, 138, 104631.
- Restuccia, D., y R. Rogerson (2008): «Policy Distortions and Aggregate Productivity with Heterogeneous Establishments», _Review of Economic Dynamics_, 11(4), 707–720.
- Romer, P. M. (1986): «Increasing Returns and Long-Run Growth», _Journal of Political Economy_, 94(5), 1002–1037.
- Skiba, A. K. (1978): «Optimal Growth with a Convex–Concave Production Function», _Econometrica_, 46(3), 527–539.
- Stokey, N. L., y R. E. Lucas, Jr., con E. C. Prescott (1989): _Recursive Methods in Economic Dynamics_. Cambridge, MA: Harvard University Press.
- Trebbi, F., M. B. Zhang, y M. Simkovic (2026): «The Cost of Regulatory Compliance in the United States», _The Review of Financial Studies_, 39(9), 2901–2962.
- Wagener, F. (2020): «Geometrical Methods for Analyzing the Optimal Management of Tipping Point Dynamics», _Natural Resource Modeling_, 33(3), e12258.
]

#pagebreak(weak: true)
#set heading(numbering: "A.1")
#counter(heading).update(0)
#counter(figure.where(kind: table)).update(0)
#set figure(numbering: n => "A." + str(n))
= Apéndice Técnico: Testigos Explícitos y Certificados Numéricos de Reproducibilidad

Este apéndice documenta la tabla completa de desambiguación simbólica, los testigos constructivos explícitos, las cotas analíticas por subintervalo y los certificados reproducibles generados por `verify_results.py` (evaluados mediante envolventes analíticas de intervalo en doble precisión IEEE-754 frente a holguras certificadas $>= 2.9 times 10^(-3)$) para las Secciones 3 a 6.

== Desambiguación de notación y convenciones simbólicas

Para evitar toda colisión notacional a lo largo del manuscrito (entre la región de tránsito $M$ y el conteo empresarial, entre las fronteras de supervivencia $S_A$ y el recurso mayorante de salida, entre el exceso de homogeneidad $r$ y las tasas de retorno o recuperación, y entre las tablas del artículo original y las propias), adoptamos de forma uniforme la convención libre de colisiones resumida en la Tabla A.1.

#figure(
  text(size: 8.4pt, table(
    columns: (1.0fr, 1.85fr, 1.5fr, 2.25fr),
    align: (center, left, center, left),
    stroke: none,
    inset: (x: 4pt, y: 3.5pt),
    table.hline(stroke: 1.1pt),
    [*Símbolo previo*], [*Rol conservado sin cambio*], [*Nuevo símbolo*], [*Rol desambiguado y alcance*],
    table.hline(stroke: 0.6pt),
    [$M$], [Región $M = [0.10, 0.28)$ y conjunto sostenible $cal(M)$], [*$N_f$*], [Número de empresas ($N_f >= 1$, $Y_t^((N_f))$, $A_("ef")(N_f)$, $N_(f,"SN")$)],
    [$S$], [Fronteras $S_A, S(tau), overline(S)_("asy")(tau), hat(S)_p$], [*$cal(S)(K)$*], [Recurso virtual mayorante en la Proposición 1\*\*],
    [$S_p$], [Frontera base $S_p, K_p^+, hat(S)_p$ de MR (2026)], [*$S^("ruin")(p)$* \ *$K'^((p)), L^((p))$*], [Frontera VFI bajo riesgo de ruina $p$ (junto con $S_G (p), S_B^("kink")(p)$) y políticas anticipatorias],
    [$r$], [Exceso de homogeneidad $r = theta - 1$], [*$rho.alt(dot)$* / *$R_t^K$* / *$p_("rec")$*], [Retorno reducido en 1 paso ($rho.alt$), renta del capital ($R_t^K$) y prob. de recuperación Markoviana ($p_("rec")$)],
    [$H$], [Región objetivo $H = [0.28, infinity)$, $H_1, H_2, hat(H)$], [*$Lambda_a$* / *$Gamma_t$*], [Factor superior CES $Lambda_a = delta\/A_("rep")$ y derrame de conocimiento $Gamma_t$ en Nota al pie 2],
    [Tabla 4 / 5], [Nuestras Tablas 1–5], [*MR-Tabla 4* / *MR-Tabla 5*], [Tablas 4 y 5 de Milei y Reidel (2026)],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Mapa de desambiguación simbólica libre de colisiones aplicado en todo el artículo.],
)

== Testigos explícitos de la Sección 3 y certificados de intervalos

*1. Testigos en $M_0 = [0.05, 0.10)$ y unificación del Corolario 1:*
- *Progresión base ($L = 0.75$):* $0.05 -> 0.065 -> 0.0845 -> 0.100$ rinde consumos $(0.002495, 0.006286, 0.022068)$ y utilidades en $(A_-, q_-, eta_+)$ iguales a $(-4.611772, -3.964892, -3.085659)$, con $W_(M_0)(0.05) = -43.844826 > -43.845$ (prefijo $T_0 = 10$ igual a $-43.899678$; cota de paso 1 como $L -> 1$: $c <= 0.003009$, $max_L u = -4.597860 < -4.59$).
- *Testigo afilado (Corolario 1):* $0.05 -> 0.0595 -> 0.0755 -> 0.100$ con $L = (0.45, 0.50, 0.60)$ y liquidación temporal en $(0.05, 0.10)$ rinde utilidades $(-3.681867, -3.888538, -3.828711)$, $W_(M_0)^("af")(0.05) = -43.540132$ (cola *MR-Tabla 4*) y $-43.500107$ (cola de $25$ pasos $W_M^((0))(0.10; beta_+) = -35.536014$). Con $Psi^((0))(K) = 0.45 K - 5 K^(-1\/2) + c_0$ certificada continuamente en $(0, infinity)$ ($c_0 (beta_+) = -18.855281$, que da $Psi^((0))(0.28; beta_+) = -28.178393$; $c_(0,"unif") = -18.713835$, discrepancia B&B en $[-0.564473, -0.564273]$, margen de cola superior $1.0433$, $Psi_("unif")^((0))(0.10) = -34.480223$, $Psi_("unif")^((0))(0.28) = -28.036947$), se obtiene $tau_(.1) <= 9$ mediante comparación estado a estado con $B^(0)(0.05) = -71.367682$ ($J(9; 0.05) = -43.543050$, holgura mínima $+0.0029$, pues $W_(M_0)^("af")(K_0) - B^(0)(K_0)$ crece estrictamente en $M_0$), $tau_H <= 22$ independiente en la caja usando $B_* (beta_-) = -43.0465116$ y $B_1 (0.10; beta_-) = -43.355594$ ($+0.122408$, frente a $-0.114831$ en $T = 21$), y $tau_H <= 21$ bajo $beta$ acoplado recalculando consistentemente $B_* (beta)$ y $B_1 (0.10; beta)$ en cada $beta in {0.9699, 0.9700, 0.9701}$ (por ejemplo, $B_* (0.9701) = -43.339148$, $B_1 (0.10; 0.9701) = -43.648230$, holguras $+0.070042$, $+0.083959$ y $+0.097882$).
- *Descomposición de holgura en $M = [0.10, 0.28)$ (`verify_restricted_M_vfi`):* Bajo las cotas de *MR-Tabla 4* / $Psi^sharp$, la DP restringida exacta $J_T^(*, Psi^sharp) - W_M$ alcanza $+0.028144$ ($T = 8$) y $-0.556742$ ($T = 9$); la barrera regional óptima de punto fijo $B_("opt") in [-56.794979, -52.457990]$ da $-0.103800$ ($T = 8$) y $+0.472857$ ($T = 9$) evaluada en el peor estado inicial $x_0 = 0.28^-$ ($inf_M (W_M - B_("opt")) = 19.1824$, frente a $21.2151$ en $x_0 = 0.10$). En el centro de la caja ($V(0.10) = -35.597030$), la VFI libre entra desde todo $M$ en $<= 4$ pasos y la DP restringida verdadera $J_T^(*, "VFI") - V$ cae a $-0.173124$ ($T = 4$) y $-0.752234$ ($T = 5$).

*2. Cotas analíticas por subintervalo y quiebres de la Proposición 1\*\*:*
- *Región $M = [0.10, 0.28)$ ($4$ subintervalos para $Q_M, Delta'_M$ y $8$ iguales para $Delta''_M$, usando $eta_+$ donde $c''_M > 0$ en $[0.10, 0.17)$):* $Q_M <= [-0.06341, -0.05880, -0.05061, -0.04375]$, $Delta'_M >= [3.0288, 0.3955, 0.1252, 0.0723]$, $Delta''_M <= [-421.1331, -107.5343, -42.3434, -21.2734, dots.c, -2.5107]$, $u^*(K) in [0.5662, 0.6808] < 1$ ($L^* >= 0.3192$), $Delta'_M (0.28^-) = +0.502666$, y margen en $K = 0.10$ ($l_0 = 0.44$): $0.094717$ ($Psi^sharp$) y $0.062495$ ($Psi$).
- *Región $H_1 = [0.28, 0.80)$ ($6$ subintervalos para $Q_(H_1), Delta'_(H_1)$ y $10$ iguales para $Delta''_(H_1)$):* $Q_(H_1) <= [-0.18976, -0.16941, -0.15171, -0.13844, -0.13124, -0.13540]$, $Delta'_(H_1) >= [1.4675, 0.3243, 0.1022, 0.0348, 0.0095, 0.0119]$, $Delta''_(H_1) <= [-40.4320, -12.4955, -5.3078, -2.6661, dots.c, -0.1889]$, $u^*(K) in [0.4301, 0.5427] < 1$ ($L^* >= 0.4573$), $Delta'_(H_1)(0.80^-) = +0.100489$. Quiebres hacia abajo en $H_1$: $k_W = 0.406819$ ($W'_(H_1): 3.954006 -> 3.952877$) y $k_E = 0.573570$ ($(-E^+)': -1.652310 -> -1.652744$). Base variacional (U2): $L^*(0.28) = 0.569743$, $L^*(0.10) = 0.437261$, $L_("tan")(0.10; 0.44) in [0.433462, 0.433840]$, margen en $K = 0.28$: $0.056121$ ($l_0 = 0.60$) y $0.057148$ ($l_0 = 0.57$, $Psi^sharp$; $0.024926$ con $Psi$).

== Certificados estocásticos reproducibles del Lema 2 y Proposición 4\*

*Construcción de la malla `log-PWL` y colas analíticas:* La envolvente continua `log-PWL` se define sobre $645$ nodos en $[10^(-8), 90.0]$ mediante interpolación lineal en $log K$ (compuesta por $642$ nodos únicos en $[10^(-8), 60.0]$ repartidos en $11$ sub-mallas log-espaciadas —con $220$ nodos concentrados en la zona de Skiba $[0.0012, 0.0030]$, además de los bordes exactos $0.10, 0.28$— y extendida con los nodos de cola $\{68.0, 78.0, 90.0\}$). Sobre la cola inferior $lr((0, 10^(-8)])$, adopta la forma log-lineal exacta $Psi(x) = Psi(10^(-8)) + s_("tail") log(x \/ 10^(-8))$ con pendiente $s_("tail") = eta_- \/ (1 - b_v)$ (bajo contracción analítica $q_+ + F_(A_+)(10^(-8), 1)\/10^(-8) < 1$); puesto que $log(x \/ 10^(-8)) <= 0$ exige $eta_- - (1 - b) s_("tail") >= 0$, en esta cola $b_v$ toma el extremo inferior ($tilde(beta)_(p,-)$ o $beta_-$). Sobre la cola superior $[90.0, infinity)$, adopta $Psi(x) = Psi(60.0) + D_("hi") log(x \/ 60.0)$ con $D_("hi") >= eta_+ \/ (1 - b_v)$; como $log(x \/ 60.0) > 0$ exige $eta_+ - (1 - b) D_("hi") <= 0$, en esta cola $b_v$ toma el extremo superior ($tilde(beta)_(p,+)$ o $beta_+$), verificándose analíticamente los tres regímenes de sucesor $y in (0, 1]$, $y in [1, 60.0]$ y $y > 60.0$ aprovechando $Y(90.0, 1) < 90.0$.

*1. Super-barreras `log-PWL` bajo riesgo de ruina y testigos de $25$ pasos (5A):* La Tabla A.2 recoge la parametrización `log-PWL` continua en $(0, infinity)$ (desplazamiento $c_("pwl")$, valores en los bordes de $M$ y cola superior $-0.030$) junto con las evaluaciones de $W_M^((p))$ y $W_H^((p))$ en $beta_+ (1 - p)$. Para $p = 0.00\%$, la trayectoria explícita de $25$ pasos desde $K_0 = 0.1000$ inicia con $[(0.1000, 0.6662 -> 0.1338), (0.1338, 0.6854 -> 0.1815), (0.1815, 0.7109 -> 0.2497), (0.2497, 0.7301 -> 0.3434), (0.3434, 0.7556 -> 0.4727), dots.c -> 2.9036]$ con $rho.alt_t in [-3.3968, -0.6205]$; para $p = 2.00\%$, inicia con $[(0.1000, 0.6471 -> 0.1320), (0.1320, 0.6662 -> 0.1765), (0.1765, 0.6982 -> 0.2395), (0.2395, 0.7173 -> 0.3249), (0.3249, 0.7429 -> 0.4440), dots.c -> 2.5619]$ con $rho.alt_t in [-3.3015, -0.6333]$. La familia paramétrica $0.45 x - 5 x^(-1\/2) + c_0$ certifica en $p = 0.00\%$ ($c_0 = -18.7138$, margen de cola $+1.043$), pero sufre explosión en la cola inferior $x -> 0^+$ por encima de $p_("sing") = 1.1217\%$.

#figure(
  text(size: 8.3pt, table(
    columns: (0.7fr, 0.9fr, 1.0fr, 1.0fr, 1.05fr, 1.05fr, 1.25fr),
    align: (center, center, center, center, center, center, center),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [$p$], [$c_("pwl")$], [$Psi^((p))(0.10)$], [$Psi^((p))(0.28)$], [$W_M^((p)) (0.10)$], [$W_H^((p)) (0.28)$], [Permanencia / $T^*(p)$],
    table.hline(stroke: 0.6pt),
    [$0.00\%$], [$0.05025$], [$-35.1934$], [$-28.2088$], [$-35.536014$], [$-28.529814$], [$7.822$ / $22$],
    [$0.50\%$], [$0.06592$], [$-32.0566$], [$-25.2133$], [$-32.361297$], [$-25.497581$], [$4.981$ / $25$],
    [$1.00\%$], [$0.03059$], [$-29.6649$], [$-22.9590$], [$-29.898125$], [$-23.171248$], [$2.894$ / $30$],
    [$1.50\%$], [$0.02625$], [$-27.7135$], [$-21.1402$], [$-27.915233$], [$-21.322296$], [$1.315$ / $40$],
    [$2.00\%$], [$0.03063$], [$-26.0891$], [$-19.6444$], [$-26.273549$], [$-19.809973$], [$0.093$ / $84$],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Certificados continuos `log-PWL` de super-barreras y testigos factibles de $25$ pasos de la Proposición 4\*(1) en $p in [0\%, 2\%]$ (márgenes mínimos de salida: $m_("exit")^M >= +0.927$ en $b$ y $>= +0.839$ continuo en $M$; $m_("exit")^H >= +0.409$; umbral de quiebre $p_("cert") = 2.0434\%$).],
)

*2. Certificados acoplados de Markov en $32$ subcajas (5B):* La Tabla A.3 reporta los desplazamientos `log-PWL` $(c_G, c_B)$ y valores de testigo $(W_G, W_B)$ evaluados en $beta_- = 0.9699$, junto con las holguras mínimas de permanencia, plazos máximos $(T^*_G, T^*_B)$, márgenes de salida adversa sobre las $32$ ($4 times 2 times 2 times 2$) subcajas de la caja (7.3) y cotas inferiores de probabilidad de escape $bb(P)(tau <= T^*_G + 4)$ uniformemente válidos bajo $beta$ acoplado en $\{0.9699, 0.9701\}$ para todo $p in {0\%, dots.c, 12\%}$ (extrapolándose el cruce de permanencia en $B$ hasta $p_("cert")^("Markov") = 15.45\%$).

#figure(
  text(size: 7.5pt, table(
    columns: (0.62fr, 1.15fr, 1.25fr, 1.0fr, 0.8fr, 1.55fr, 1.15fr),
    align: (center, center, center, center, center, center, center),
    stroke: none,
    inset: (x: 2.5pt, y: 3.5pt),
    table.hline(stroke: 1.1pt),
    [$p$], [$(c_G, c_B)$], [$(W_G, W_B)$], [Perm. $(G, B)$], [$(T^*_G, T^*_B)$], [Salidas ($M: G\/B$ ; $H: G\/B_("32bx")$)], [$bb(P)(tau <= T^*_G + 4)$],
    table.hline(stroke: 0.6pt),
    [$0.0\%$], [$(0.0396, 0.0389)$], [$(-35.3952, -40.4501)$], [$(7.963, 3.852)$], [$(21, 45)$], [$+1.152\/+0.053$ ; $+0.553\/+0.013$], [$>= 0.120$ ($tau <= 25$)],
    [$0.5\%$], [$(0.0350, 0.0347)$], [$(-35.7208, -40.7379)$], [$(7.787, 3.701)$], [$(21, 46)$], [$+1.168\/+0.059$ ; $+0.563\/+0.019$], [$>= 0.109$ ($tau <= 25$)],
    [$1.0\%$], [$(0.0322, 0.0322)$], [$(-36.0392, -41.0197)$], [$(7.615, 3.553)$], [$(22, 47)$], [$+1.182\/+0.062$ ; $+0.571\/+0.021$], [$>= 0.117$ ($tau <= 26$)],
    [$1.5\%$], [$(0.0357, 0.0354)$], [$(-36.3512, -41.2963)$], [$(7.445, 3.406)$], [$(22, 48)$], [$+1.190\/+0.059$ ; $+0.573\/+0.023$], [$>= 0.105$ ($tau <= 26$)],
    [$2.0\%$], [$(0.0332, 0.0331)$], [$(-36.6568, -41.5657)$], [$(7.278, 3.264)$], [$(23, 49)$], [$+1.203\/+0.061$ ; $+0.578\/+0.025$], [$>= 0.097$ ($tau <= 27$)],
    [$5.0\%$], [$(0.0358, 0.0356)$], [$(-38.3626, -43.0710)$], [$(6.333, 2.454)$], [$(25, 56)$], [$+1.264\/+0.063$ ; $+0.609\/+0.021$], [$>= 0.082$ ($tau <= 29$)],
    [$8.0\%$], [$(0.0336, 0.0337)$], [$(-39.8733, -44.4031)$], [$(5.480, 1.724)$], [$(29, 66)$], [$+1.334\/+0.073$ ; $+0.648\/+0.022$], [$>= 0.072$ ($tau <= 33$)],
    [$12.0\%$], [$(0.0373, 0.0372)$], [$(-41.6563, -45.9694)$], [$(4.447, 0.844)$], [$(33, 88)$], [$+1.413\/+0.080$ ; $+0.689\/+0.022$], [$>= 0.057$ ($tau <= 37$)],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Certificados acoplados de Markov `log-PWL` de la Proposición 4\*(2) sobre $p in [0\%, 12\%]$ (márgenes continuos en $M$ bajo el estado $B$: $>= +0.032$ en $0\%$ hasta $+0.060$ en $12\%$).],
)

== Curva en U, fronteras VFI y equilibrios descentralizados

*1. Parámetros críticos de la curva en U institucional (Sección 5):* Con $A_0 = 1.45, alpha = 0.25, gamma = tau^* = 0.20$: umbral de reposición $A_("rep") = 0.073485$ con raíces físicas $(tau_(min), tau_(max)) = (6.60 times 10^(-6), 0.948649)$; nodo silla MGR $A_* = A_("SN") = 0.0995245$ con intervalo abierto de viabilidad económica $(tau_1, tau_2) = (2.219660 times 10^(-5), 0.930108)$; punto de cruce donde la frontera VFI $S(tau)$ supera a $overline(S)_("asy")(tau)$ en $A_("cross") = 0.110038$ ($(tau_(c,1), tau_(c,2)) = (3.317089 times 10^(-5), 0.922567)$); dominio finito certificado del Teorema 8 ($A_e >= 0.749$) en $[0.117245, 0.304799]$; umbrales de fragmentación empresarial $N_(f,"SN") = 56.79$ frente a $N_(f,"rep") = 104.17$.

*2. Equilibrios descentralizados de la Proposición 2\*, régimen $A K$ y sensibilidad a $p_("rec")$:* La Tabla A.4 resume los estados estacionarios $(K_("lo"), K_("hi"))$ del equilibrio descentralizado frente a $S(A_("mkt"))$ en la Sección 6.1 (confirmando la trampa $[S_A, K_("lo"))$ ya en $mu = theta = 1.5$ y el desplazamiento hacia arriba de $K_("lo")$ bajo reembolso de suma fija) y la sensibilidad continua VFI respecto de $p_("rec")$ en $p = 8.0\%$ (Sección 6.3). En la Nota al pie 2 (Sección 6.2), la especificación continua $Y_t = (K_t\/h) F_A (h, L_t)$ en $H$ alcanza $V_("AK")(0.28) = +240.7598 >> Psi^sharp (0.28) = -27.870334$.

#figure(
  text(size: 8.2pt, table(
    columns: (1.7fr, 0.95fr, 1.15fr, 1.35fr, 1.35fr),
    align: (left, center, center, center, center),
    stroke: none,
    table.hline(stroke: 1.1pt),
    [*Configuración (Prop. 2\* / VFI 5C)*], [*$A_("mkt")$ / $p_("rec")$*], [*$S(A_("mkt"))$ / $S_G$*], [*$K_("lo")$ ($L_("lo")$) / $S_B^("kink")$*], [*$K_("hi")$ ($L_("hi")$) / $K_B^*; K'^((G)); L^((G))$*],
    table.hline(stroke: 0.6pt),
    [$mu = 1.5$ (costos fijos)], [$0.7500$], [$0.001587$], [$0.003039$ ($0.1423$)], [$1.808955$ ($0.6787$)],
    [$mu = 1.8$ (costos fijos)], [$0.6250$], [$0.002302$], [$0.004490$ ($0.1689$)], [$1.558817$ ($0.6755$)],
    [$mu = 1.8$ (reembolso lump-sum)], [$0.6250$], [$0.002302$], [$0.004670$ ($0.1346$)], [$1.390019$ ($0.6226$)],
    [$mu = 2.0$ (costos fijos)], [$0.5625$], [$0.002856$], [$0.005644$ ($0.1862$)], [$1.423495$ ($0.6734$)],
    [$mu = 2.0$ (reembolso lump-sum)], [$0.5625$], [$0.002856$], [$0.006055$ ($0.1349$)], [$1.171530$ ($0.5872$)],
    table.hline(stroke: 0.6pt),
    [VFI Markov ($p = 8.0\%$)], [$0.2000$], [$0.001836$], [$0.00192$], [$0.00969$ ; $0.13511$ ; $0.6803$],
    [VFI Markov ($p = 8.0\%$)], [$0.3333$], [$0.001774$], [$0.00187$], [$0.00991$ ; $0.13475$ ; $0.6759$],
    [VFI Markov ($p = 8.0\%$)], [$0.5000$], [$0.001735$], [$0.00182$], [$0.01038$ ; $0.13447$ ; $0.6726$],
    table.hline(stroke: 1.1pt),
  )),
  caption: [Estados estacionarios descentralizados de la Proposición 2\* frente al umbral del planificador $S(A_("mkt"))$, y sensibilidad continua en VFI de sección áurea respecto de $p_("rec")$ a $p = 8.0\%$.],
)
