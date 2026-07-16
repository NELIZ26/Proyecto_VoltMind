<template>
  <div class="solicitud-shell" :class="{ 'con-barra': mostrarBarraSofia }">
    <!-- Hero institucional a todo el ancho: cada afiche llena el banner (cover)
         con el foco ajustado por imagen y un zoom lento tipo Ken Burns.
         DESACTIVADO TEMPORALMENTE (jul-2026): el equipo está evaluando si se
         mantiene o se elimina. Para reactivarlo, descomentar este bloque y la
         llamada a reanudarCarrusel() en onMounted. -->
    <!--
    <section
      class="hero-carrusel"
      aria-label="Novedades institucionales del SENA"
      @mouseenter="pausarCarrusel"
      @mouseleave="reanudarCarrusel"
    >
      <div
        v-for="(afiche, i) in AFICHES"
        :key="afiche.src"
        class="hero-lamina"
        :class="{ activa: i === aficheActivo }"
        :aria-hidden="i !== aficheActivo"
      >
        <img
          class="hero-imagen"
          :src="afiche.src"
          :alt="afiche.alt"
          :style="{ objectPosition: afiche.posicion }"
        />
      </div>

      <div class="hero-velo" aria-hidden="true"></div>

      <div class="carrusel-puntos">
        <button
          v-for="(afiche, i) in AFICHES"
          :key="`punto-${i}`"
          type="button"
          class="carrusel-punto"
          :class="{ activo: i === aficheActivo }"
          :aria-label="`Ver afiche ${i + 1} de ${AFICHES.length}`"
          @click="irAAfiche(i)"
        ></button>
      </div>
    </section>
    -->

    <div class="solicitud-contenedor">
      <form class="form-comp" @submit.prevent="enviar">
        <!-- Solicitante -->
        <section id="sec-instructor" class="grupo">
          <header class="grupo-head">
            <span class="grupo-icono"><font-awesome-icon icon="fa-solid fa-user-tie" /></span>
            <div class="grupo-titulos">
              <h3>Información del instructor</h3>
              <p>Datos de contacto de quien presenta la solicitud.</p>
            </div>
            <span v-if="seccionesCompletas.instructor" class="grupo-check" title="Sección completa">
              <font-awesome-icon icon="fa-solid fa-circle-check" />
            </span>
          </header>
          <div class="fila">
            <label class="campo campo-doble">
              <span>Nombre completo *</span>
              <input v-model.trim="form.nombre_instructor" type="text" class="form-input" required minlength="3" placeholder="Ej: Carlos Díaz" />
            </label>
          </div>
          <div class="fila">
            <label class="campo">
              <span>Correo institucional *</span>
              <input v-model.trim="form.correo_instructor" type="email" class="form-input" required placeholder="nombre@sena.edu.co" />
            </label>
            <label class="campo">
              <span>Celular *</span>
              <input v-model.trim="form.celular_instructor" type="tel" class="form-input" required placeholder="3XX XXX XXXX" />
            </label>
          </div>
        </section>

        <!-- Programa -->
        <section id="sec-formacion" class="grupo">
          <header class="grupo-head">
            <span class="grupo-icono"><font-awesome-icon icon="fa-solid fa-graduation-cap" /></span>
            <div class="grupo-titulos">
              <h3>Información de la formación</h3>
              <p>Programa de Sofía Plus que se va a ofertar.</p>
            </div>
            <span v-if="seccionesCompletas.formacion" class="grupo-check" title="Sección completa">
              <font-awesome-icon icon="fa-solid fa-circle-check" />
            </span>
          </header>
          <div class="fila">
            <label class="campo campo-doble">
              <span>Nombre del programa *</span>
              <input v-model.trim="form.nombre_programa" type="text" class="form-input" required minlength="3" placeholder="Ej: Excel Básico para el Registro de Información" />
            </label>
          </div>
          <div class="fila">
            <label class="campo">
              <span>Código (Sofía Plus) *</span>
              <input v-model.trim="form.codigo_programa" type="text" class="form-input" required placeholder="Ej: 12310114" />
            </label>
            <label class="campo">
              <span>Versión</span>
              <input v-model.trim="form.version_programa" type="text" class="form-input" placeholder="1" />
            </label>
            <label class="campo">
              <span>Duración (horas) *</span>
              <input v-model.number="form.duracion_horas" type="number" class="form-input" required min="1" max="880" />
            </label>
          </div>
        </section>

        <!-- Fechas -->
        <section id="sec-fechas" class="grupo">
          <header class="grupo-head">
            <span class="grupo-icono"><font-awesome-icon icon="fa-solid fa-calendar-days" /></span>
            <div class="grupo-titulos">
              <h3>Fechas</h3>
              <p>Ventana de inscripciones y periodo de la formación.</p>
            </div>
            <span v-if="seccionesCompletas.fechas" class="grupo-check" title="Sección completa">
              <font-awesome-icon icon="fa-solid fa-circle-check" />
            </span>
          </header>
          <div class="fila">
            <label class="campo">
              <span>Inicio de inscripciones</span>
              <input v-model="form.fecha_inicio_inscripcion" type="date" class="form-input" />
            </label>
            <label class="campo">
              <span>Cierre de inscripciones</span>
              <input v-model="form.fecha_cierre_inscripcion" type="date" class="form-input" />
            </label>
          </div>
          <div class="fila">
            <label class="campo">
              <span>Inicio de formación</span>
              <input v-model="form.fecha_inicio_formacion" type="date" class="form-input" />
            </label>
            <label class="campo">
              <span>Fin de formación</span>
              <input v-model="form.fecha_fin_formacion" type="date" class="form-input" />
            </label>
          </div>
        </section>

        <!-- Logística -->
        <section id="sec-logistica" class="grupo">
          <header class="grupo-head">
            <span class="grupo-icono"><font-awesome-icon icon="fa-solid fa-location-dot" /></span>
            <div class="grupo-titulos">
              <h3>Logística</h3>
              <p>Dónde y en qué jornada se ejecutará la formación.</p>
            </div>
            <span v-if="seccionesCompletas.logistica" class="grupo-check" title="Sección completa">
              <font-awesome-icon icon="fa-solid fa-circle-check" />
            </span>
          </header>
          <div class="fila">
            <label class="campo">
              <span>Jornada *</span>
              <select v-model="form.jornada" class="form-input" required>
                <option value="" disabled>Seleccione...</option>
                <option v-for="j in JORNADAS" :key="j" :value="j">{{ j }}</option>
              </select>
            </label>
            <label class="campo">
              <span>Municipio *</span>
              <input v-model.trim="form.municipio" type="text" class="form-input" required placeholder="Ej: Puerto Asís" list="municipios-putumayo" />
              <datalist id="municipios-putumayo">
                <option v-for="m in MUNICIPIOS_PUTUMAYO" :key="m" :value="m" />
              </datalist>
            </label>
          </div>
          <div class="fila">
            <label class="campo campo-doble">
              <span>Lugar de ejecución *</span>
              <input v-model.trim="form.lugar_ejecucion" type="text" class="form-input" required placeholder="Ej: Alcaldía de Puerto Asís — Sala de sistemas" />
            </label>
          </div>
        </section>

        <!-- Archivos adjuntos (se almacenan en VoltMind) -->
        <section id="sec-adjuntos" class="grupo">
          <header class="grupo-head">
            <span class="grupo-icono"><font-awesome-icon icon="fa-solid fa-paperclip" /></span>
            <div class="grupo-titulos">
              <h3>Archivos adjuntos</h3>
              <p>
                Arrastre o haga clic para seleccionar (máx. {{ TAMANO_MAXIMO_MB }} MB por archivo).
                La matriz y el archivo plano son obligatorios.
              </p>
            </div>
            <span v-if="seccionesCompletas.adjuntos" class="grupo-check" title="Sección completa">
              <font-awesome-icon icon="fa-solid fa-circle-check" />
            </span>
          </header>

          <div class="zona-adjuntos">
            <div
              v-for="slot in SLOTS_ARCHIVO"
              :key="slot.campo"
              class="dropzone"
              :class="{
                'con-archivo': archivos[slot.campo],
                arrastrando: arrastrando === slot.campo,
                requerido: slot.requerido && !archivos[slot.campo],
              }"
              @dragover.prevent="arrastrando = slot.campo"
              @dragleave.prevent="arrastrando = null"
              @drop.prevent="soltarArchivo(slot, $event)"
              @click="abrirSelector(slot.campo)"
            >
              <input
                :ref="(el) => (inputsArchivo[slot.campo] = el)"
                type="file"
                class="input-oculto"
                :accept="slot.accept"
                @change="seleccionarArchivo(slot, $event)"
              />

              <template v-if="!archivos[slot.campo]">
                <font-awesome-icon icon="fa-solid fa-cloud-arrow-up" class="dropzone-icono" />
                <span class="dropzone-titulo">
                  {{ slot.etiqueta }} <strong v-if="slot.requerido">*</strong>
                </span>
                <span class="dropzone-ayuda">{{ slot.ayuda }}</span>
              </template>

              <template v-else>
                <font-awesome-icon icon="fa-solid fa-circle-check" class="dropzone-icono ok" />
                <span class="dropzone-titulo">{{ slot.etiqueta }}</span>
                <span class="archivo-nombre" :title="archivos[slot.campo].name">{{ archivos[slot.campo].name }}</span>
                <span class="archivo-tamano">{{ formatearTamano(archivos[slot.campo].size) }}</span>
                <div class="archivo-acciones">
                  <button type="button" class="btn-mini" @click.stop="abrirSelector(slot.campo)">
                    <font-awesome-icon icon="fa-solid fa-arrows-rotate" /> Reemplazar
                  </button>
                  <button type="button" class="btn-mini quitar" @click.stop="quitarArchivo(slot.campo)">
                    <font-awesome-icon icon="fa-solid fa-xmark" /> Quitar
                  </button>
                </div>
              </template>
            </div>
          </div>

          <p v-if="faltantes.length" class="aviso-faltantes">
            <font-awesome-icon icon="fa-solid fa-triangle-exclamation" />
            Falta adjuntar: <strong>{{ faltantes.join(' y ') }}</strong>.
          </p>
        </section>

        <footer class="acciones">
          <button type="submit" class="btn-enviar" :disabled="enviando || faltantes.length > 0">
            <font-awesome-icon :icon="enviando ? ['fas', 'circle-notch'] : 'fa-solid fa-paper-plane'" :spin="enviando" />
            {{ enviando ? 'ENVIANDO...' : 'ENVIAR SOLICITUD' }}
          </button>
        </footer>
      </form>

      <!-- Mis solicitudes (solo lectura: el seguimiento lo gestiona el admin) -->
      <section class="module-card mis-solicitudes">
        <header class="grupo-head mis-header">
          <span class="grupo-icono"><font-awesome-icon icon="fa-solid fa-clock-rotate-left" /></span>
          <div class="grupo-titulos">
            <h3>Mis solicitudes</h3>
            <p>Estado y seguimiento de las solicitudes que ha enviado.</p>
          </div>
          <button v-if="correoConsulta" class="btn-mini" :disabled="cargandoMis" @click="cargarMisSolicitudes">
            <font-awesome-icon icon="fa-solid fa-arrows-rotate" :spin="cargandoMis" /> Actualizar
          </button>
        </header>

        <p v-if="!correoConsulta" class="mis-vacio">
          Envíe su primera solicitud para ver aquí su estado.
        </p>
        <p v-else-if="cargandoMis && misSolicitudes.length === 0" class="mis-vacio">
          <font-awesome-icon :icon="['fas', 'circle-notch']" spin /> Consultando sus solicitudes...
        </p>
        <p v-else-if="misSolicitudes.length === 0" class="mis-vacio">
          Aún no tiene solicitudes registradas con el correo {{ correoConsulta }}.
        </p>

        <ul v-else class="mis-lista">
          <li
            v-for="s in misSolicitudes"
            :key="s.id"
            class="mi-solicitud"
            :class="{ resaltada: s.id === solicitudResaltada }"
          >
            <div class="mi-info">
              <span class="mi-programa">{{ s.nombre_programa }}</span>
              <span class="mi-detalle">
                {{ s.codigo_programa }} · Solicitada el {{ s.fecha_creacion || '—' }}
                <template v-if="s.codigo_ficha"> · Ficha {{ s.codigo_ficha }}</template>
              </span>
            </div>
            <div class="mi-derecha">
              <span class="mi-pasos" :title="`Seguimiento del admin: ${pasosCompletados(s)} de 4 pasos`">
                {{ pasosCompletados(s) }}/4 pasos
              </span>
              <span :class="['status-badge', claseEstado(s.estado)]">{{ s.estado }}</span>
              <button
                type="button"
                class="btn-ver-ficha"
                :title="`Ver cómo va quedando la ficha de ${s.nombre_programa} (solo lectura)`"
                @click="abrirFicha(s)"
              >
                <font-awesome-icon icon="fa-solid fa-eye" /> Ver ficha
              </button>
            </div>
          </li>
        </ul>
      </section>

    </div>

    <!-- Campana del instructor: recibe el aviso cuando su ficha queda Publicada -->
    <NotificacionesBell
      v-if="correoConsulta"
      :destinatario="correoConsulta"
      ruta-solicitud="/solicitud-complementaria"
    />

    <!-- Barra fija de acceso rápido a SOFIA Plus (estilo aviso institucional) -->
    <Transition name="barra" appear>
      <div
        v-if="mostrarBarraSofia"
        class="barra-sofia"
        role="region"
        aria-label="Acceso rápido a SOFIA Plus"
      >
        <span class="barra-icono" aria-hidden="true">
          <font-awesome-icon icon="fa-solid fa-bell" />
        </span>
        <p class="barra-texto">
          <strong>Importante:</strong> aquí gestiona sus solicitudes de ficha complementaria.
          La oferta y la inscripción oficial se realizan en SOFIA Plus.
        </p>
        <div class="barra-acciones">
          <a
            class="barra-boton"
            href="https://www.senasofiaplus.edu.co/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Ir a SOFIA Plus
            <font-awesome-icon icon="fa-solid fa-arrow-up-right-from-square" />
          </a>
          <button
            type="button"
            class="barra-cerrar"
            aria-label="Ocultar la barra de SOFIA Plus"
            title="Cerrar"
            @click="mostrarBarraSofia = false"
          >
            <font-awesome-icon icon="fa-solid fa-xmark" />
          </button>
        </div>
      </div>
    </Transition>

    <!-- Bienvenida: popup que aparece cada vez que se carga la vista -->
    <Transition name="bienvenida">
      <div
        v-if="mostrarBienvenida"
        class="bienvenida-fondo"
        role="dialog"
        aria-modal="true"
        aria-labelledby="bienvenida-titulo"
        @click.self="cerrarBienvenida"
      >
        <div class="bienvenida-card">
          <div class="bienvenida-luces" aria-hidden="true">
            <span class="luz luz-a"></span>
            <span class="luz luz-b"></span>
            <span class="luz luz-c"></span>
          </div>

          <button
            type="button"
            class="bienvenida-cerrar"
            aria-label="Cerrar bienvenida"
            title="Cerrar"
            @click="cerrarBienvenida"
          >
            <font-awesome-icon icon="fa-solid fa-xmark" />
          </button>

          <!-- Titular: saludo grande con jerarquía de banner -->
          <div class="bienvenida-encabezado">
            <p class="bienvenida-eyebrow">SENA · Formación Complementaria</p>
            <h2 id="bienvenida-titulo" class="bienvenida-titulo">
              {{ saludo }}, {{ primerNombre }}
            </h2>
            <p class="bienvenida-sub">
              Le damos la bienvenida al módulo de fichas complementarias de VoltMind.
            </p>
          </div>

          <!-- Franja de contraste con el recordatorio -->
          <div class="bienvenida-franja">
            <span class="franja-icono" aria-hidden="true">!</span>
            <p class="franja-texto">
              Recuerde <strong>completar su solicitud de ficha complementaria</strong>:
              son <span class="franja-verde">5 secciones</span> y debe adjuntar la
              <span class="franja-verde">matriz</span> y el
              <span class="franja-verde">archivo plano</span>.
            </p>
          </div>

          <!-- Llamada a la acción + identidad de la sesión -->
          <div class="bienvenida-pie">
            <button ref="botonComenzar" type="button" class="btn-comenzar" @click="cerrarBienvenida">
              Comenzar
            </button>
            <div class="pie-identidad">
              <span class="pie-avatar" aria-hidden="true">{{ inicialesPerfil }}</span>
              <span class="pie-datos">
                <span class="pie-nombre">
                  {{ nombrePerfil }}
                  <font-awesome-icon
                    icon="fa-solid fa-circle-check"
                    class="bienvenida-verificado"
                    title="Instructor de la sesión activa"
                  />
                </span>
                <span class="pie-rol">Instructor · VoltMind Access</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Botón flotante de WhatsApp: contacto directo con el área administrativa -->
    <a
      class="btn-whatsapp"
      :href="ENLACE_WHATSAPP"
      target="_blank"
      rel="noopener noreferrer"
      aria-label="¿Necesitas ayuda? Contáctanos por WhatsApp"
    >
      <span class="whatsapp-tooltip" role="tooltip">
        ¿Necesitas ayuda? Contáctanos por WhatsApp
      </span>
      <svg
        class="whatsapp-icono"
        viewBox="0 0 448 512"
        fill="currentColor"
        aria-hidden="true"
        focusable="false"
      >
        <path d="M380.9 97.1C339 55.1 283.2 32 223.9 32c-122.4 0-222 99.6-222 222 0 39.1 10.2 77.3 29.6 111L0 480l117.7-30.9c32.4 17.7 68.9 27 106.1 27h.1c122.3 0 224.1-99.6 224.1-222 0-59.3-25.2-115-67.1-157zm-157 341.6c-33.2 0-65.7-8.9-94-25.7l-6.7-4-69.8 18.3L72 359.2l-4.4-7c-18.5-29.4-28.2-63.3-28.2-98.2 0-101.7 82.8-184.5 184.6-184.5 49.3 0 95.6 19.2 130.4 54.1 34.8 34.9 56.2 81.2 56.1 130.5 0 101.8-84.9 184.6-186.6 184.6zm101.2-138.2c-5.5-2.8-32.8-16.2-37.9-18-5.1-1.9-8.8-2.8-12.5 2.8-3.7 5.6-14.3 18-17.6 21.8-3.2 3.7-6.5 4.2-12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3 1.8-3.7.9-6.9-.5-9.7-1.4-2.8-12.5-30.1-17.1-41.2-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2-3.7 0-9.7 1.4-14.8 6.9-5.1 5.6-19.4 19-19.4 46.3 0 27.3 19.9 53.7 22.6 57.4 2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9 10.7-1.6 32.8-13.4 37.4-26.4 4.6-13 4.6-24.1 3.2-26.4-1.3-2.5-5-3.9-10.5-6.6z"/>
      </svg>
    </a>

    <!-- Vista previa de la ficha: documento institucional de SOLO LECTURA -->
    <Transition name="ficha">
      <div
        v-if="fichaEnVista"
        class="ficha-fondo"
        role="dialog"
        aria-modal="true"
        aria-labelledby="ficha-titulo"
        @click.self="cerrarFicha"
      >
        <article class="ficha-doc">
          <!-- Membrete institucional -->
          <header class="ficha-membrete">
            <div class="membrete-textos">
              <p class="membrete-entidad">SENA · Servicio Nacional de Aprendizaje</p>
              <p class="membrete-centro">Centro Agroforestal y Acuícola Arapaima — Regional Putumayo</p>
            </div>
            <span class="chip-solo-lectura" title="Vista de consulta: no se puede editar ni descargar">
              <font-awesome-icon icon="fa-solid fa-eye" /> Solo lectura
            </span>
            <button
              type="button"
              class="ficha-cerrar"
              aria-label="Cerrar la vista previa de la ficha"
              title="Cerrar"
              @click="cerrarFicha"
            >
              <font-awesome-icon icon="fa-solid fa-xmark" />
            </button>
          </header>

          <div class="ficha-cuerpo">
            <!-- Título del documento -->
            <div class="ficha-encabezado">
              <p class="ficha-eyebrow">Ficha de formación complementaria</p>
              <h2 id="ficha-titulo" class="ficha-programa">{{ fichaEnVista.nombre_programa }}</h2>
              <p class="ficha-codigos">
                Programa {{ fichaEnVista.codigo_programa }} · v{{ fichaEnVista.version_programa || '1' }}
                · {{ fichaEnVista.duracion_horas }} horas
              </p>
            </div>

            <!-- Estado de la solicitud -->
            <section class="ficha-seccion ficha-estado">
              <h3 class="ficha-seccion-titulo">Estado de la solicitud</h3>
              <div class="estado-fila">
                <span :class="['status-badge', claseEstado(fichaEnVista.estado)]">
                  {{ fichaEnVista.estado }}
                </span>
                <span class="estado-descripcion">{{ descripcionEstado(fichaEnVista.estado) }}</span>
              </div>
              <ul class="estado-pasos">
                <li
                  v-for="paso in PASOS_FICHA"
                  :key="paso.campo"
                  :class="{ hecho: fichaEnVista[paso.campo] }"
                >
                  <span class="paso-punto" aria-hidden="true">
                    <font-awesome-icon v-if="fichaEnVista[paso.campo]" icon="fa-solid fa-check" />
                  </span>
                  {{ paso.etiqueta }}
                </li>
              </ul>
            </section>

            <div class="ficha-grilla">
              <section class="ficha-seccion">
                <h3 class="ficha-seccion-titulo">
                  <font-awesome-icon icon="fa-solid fa-user-tie" /> Instructor
                </h3>
                <dl class="ficha-datos">
                  <div class="ficha-dato"><dt>Nombre</dt><dd>{{ fichaEnVista.nombre_instructor || '—' }}</dd></div>
                  <div class="ficha-dato"><dt>Correo institucional</dt><dd>{{ fichaEnVista.correo_instructor || '—' }}</dd></div>
                  <div class="ficha-dato"><dt>Celular</dt><dd>{{ fichaEnVista.celular_instructor || '—' }}</dd></div>
                </dl>
              </section>

              <section class="ficha-seccion">
                <h3 class="ficha-seccion-titulo">
                  <font-awesome-icon icon="fa-solid fa-graduation-cap" /> Formación
                </h3>
                <dl class="ficha-datos">
                  <div class="ficha-dato">
                    <dt>Código de empresa</dt>
                    <dd>
                      <template v-if="fichaEnVista.codigo_empresa">{{ fichaEnVista.codigo_empresa }}</template>
                      <span v-else class="en-tramite">En trámite por la coordinación</span>
                    </dd>
                  </div>
                  <div class="ficha-dato">
                    <dt>Código de ficha</dt>
                    <dd>
                      <template v-if="fichaEnVista.codigo_ficha">{{ fichaEnVista.codigo_ficha }}</template>
                      <span v-else class="en-tramite">En trámite por la coordinación</span>
                    </dd>
                  </div>
                  <div class="ficha-dato"><dt>Inscritos previstos</dt><dd>{{ fichaEnVista.cantidad_inscritos ?? '—' }}</dd></div>
                </dl>
              </section>

              <section class="ficha-seccion">
                <h3 class="ficha-seccion-titulo">
                  <font-awesome-icon icon="fa-solid fa-calendar-days" /> Fechas
                </h3>
                <dl class="ficha-datos">
                  <div class="ficha-dato">
                    <dt>Inscripciones</dt>
                    <dd class="dato-fechas">{{ rangoFechas(fichaEnVista.fecha_inicio_inscripcion, fichaEnVista.fecha_cierre_inscripcion) }}</dd>
                  </div>
                  <div class="ficha-dato">
                    <dt>Formación</dt>
                    <dd class="dato-fechas">{{ rangoFechas(fichaEnVista.fecha_inicio_formacion, fichaEnVista.fecha_fin_formacion) }}</dd>
                  </div>
                  <div class="ficha-dato"><dt>Solicitud enviada</dt><dd class="dato-fechas">{{ fichaEnVista.fecha_creacion || '—' }}</dd></div>
                </dl>
              </section>

              <section class="ficha-seccion">
                <h3 class="ficha-seccion-titulo">
                  <font-awesome-icon icon="fa-solid fa-location-dot" /> Logística
                </h3>
                <dl class="ficha-datos">
                  <div class="ficha-dato"><dt>Jornada</dt><dd>{{ fichaEnVista.jornada || '—' }}</dd></div>
                  <div class="ficha-dato"><dt>Municipio</dt><dd>{{ fichaEnVista.municipio || '—' }}</dd></div>
                  <div class="ficha-dato"><dt>Lugar de ejecución</dt><dd>{{ fichaEnVista.lugar_ejecucion || '—' }}</dd></div>
                </dl>
              </section>
            </div>

            <!-- Adjuntos entregados (solo el nombre: quedan en custodia de la coordinación) -->
            <section class="ficha-seccion">
              <h3 class="ficha-seccion-titulo">
                <font-awesome-icon icon="fa-solid fa-paperclip" /> Adjuntos entregados
              </h3>
              <ul v-if="adjuntosEntregados.length" class="ficha-adjuntos">
                <li v-for="a in adjuntosEntregados" :key="a.campo">
                  <font-awesome-icon icon="fa-solid fa-paperclip" />
                  <span class="adjunto-tipo">{{ ETIQUETAS_ARCHIVO[a.campo] || a.campo }}:</span>
                  <span class="adjunto-archivo">{{ a.nombre }}</span>
                </li>
              </ul>
              <p v-else class="ficha-sin-adjuntos">Sin archivos registrados en esta solicitud.</p>
              <p class="ficha-nota-adjuntos">
                Los archivos quedan en custodia de la coordinación; esta vista es únicamente de consulta.
              </p>
            </section>

            <!-- Resultados de inscritos: ÚNICO documento descargable por el instructor -->
            <section v-if="archivoResultados" class="ficha-seccion ficha-resultados">
              <h3 class="ficha-seccion-titulo">
                <font-awesome-icon icon="fa-solid fa-user-check" /> Resultados de inscritos
              </h3>
              <div class="resultados-fila">
                <div class="resultados-datos">
                  <span class="resultados-etiqueta">Resultados de aprendices inscritos</span>
                  <span class="resultados-archivo">{{ archivoResultados.nombre }}</span>
                </div>
                <a
                  class="btn-descargar-resultados"
                  :href="urlResultados"
                  :download="archivoResultados.nombre"
                  :title="`Descargar ${archivoResultados.nombre}`"
                >
                  <font-awesome-icon icon="fa-solid fa-download" /> Descargar
                </a>
              </div>
              <p class="ficha-nota-adjuntos">
                Documento publicado por la coordinación al finalizar el proceso;
                es el único archivo disponible para descarga en esta vista.
              </p>
            </section>

            <!-- Observaciones de la coordinación -->
            <section v-if="fichaEnVista.observaciones" class="ficha-seccion">
              <h3 class="ficha-seccion-titulo">
                <font-awesome-icon icon="fa-solid fa-circle-info" /> Observaciones de la coordinación
              </h3>
              <p class="ficha-observaciones">{{ fichaEnVista.observaciones }}</p>
            </section>

            <footer class="ficha-pie">
              <p>Documento de consulta generado por VoltMind Access · {{ fechaGeneracion }}</p>
              <p>Si encuentra un dato incorrecto, comuníquelo al dinamizador: la ficha la gestiona la coordinación.</p>
            </footer>
          </div>
        </article>
      </div>
    </Transition>
  </div>
</template>

<script setup>
// Vista del INSTRUCTOR: solicita la creación de una ficha complementaria con
// sus archivos adjuntos (almacenados en VoltMind) y consulta el estado de sus
// solicitudes. El instructor NO crea la ficha ni gestiona el seguimiento:
// la solicitud nace "Pendiente" y el backend notifica al administrador.
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import Swal from 'sweetalert2';
import { useAuthStore } from '@/stores/auth';
import {
  JORNADAS,
  MUNICIPIOS_PUTUMAYO,
  ETIQUETAS_ARCHIVO,
  claseEstado,
  pasosCompletados,
  formatearRango,
} from '@/stores/complementarias';
import { complementariasService } from '@/services/complementariasService';
import NotificacionesBell from '@/components/admin/NotificacionesBell.vue';
import imagenCampo from '@/image/Campo.png';
import imagenPaz from '@/image/Paz.png';

const TAMANO_MAXIMO_MB = 10; // Debe coincidir con el límite del backend
const CLAVE_CORREO = 'voltmind_correo_instructor';

// Configuración de las tres casillas de carga (mismo contrato del backend)
const SLOTS_ARCHIVO = [
  {
    campo: 'matriz',
    etiqueta: 'Matriz de la ficha',
    requerido: true,
    accept: '.xlsx,.xls,.xlsm,.csv',
    ayuda: 'Excel o CSV',
    extensiones: ['xlsx', 'xls', 'xlsm', 'csv'],
  },
  {
    campo: 'plano',
    etiqueta: 'Archivo plano de aprendices',
    requerido: true,
    accept: '.xlsx,.xls,.pdf',
    ayuda: 'Excel o PDF',
    extensiones: ['xlsx', 'xls', 'pdf'],
  },
  {
    campo: 'adicional',
    etiqueta: 'Documento adicional',
    requerido: false,
    accept: '.pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg',
    ayuda: 'PDF, Office o imagen (opcional)',
    extensiones: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg'],
  },
];

const toast = useToast();
const auth = useAuthStore();
const enviando = ref(false);

// ── Formulario ──
const formVacio = () => ({
  nombre_instructor: '',
  correo_instructor: '',
  celular_instructor: '',
  codigo_programa: '',
  version_programa: '1',
  nombre_programa: '',
  duracion_horas: 40,
  fecha_inicio_inscripcion: '',
  fecha_cierre_inscripcion: '',
  fecha_inicio_formacion: '',
  fecha_fin_formacion: '',
  jornada: '',
  municipio: '',
  lugar_ejecucion: '',
});

const form = ref(formVacio());

// ── Archivos ──
const archivos = ref({ matriz: null, plano: null, adicional: null });
const inputsArchivo = ref({});
const arrastrando = ref(null);

const faltantes = computed(() =>
  SLOTS_ARCHIVO.filter((s) => s.requerido && !archivos.value[s.campo]).map((s) => s.etiqueta)
);

// ── Secciones completas: enciende el check verde de cada tarjeta (solo visual) ──
const seccionesCompletas = computed(() => ({
  instructor: !!(
    form.value.nombre_instructor.trim().length >= 3 &&
    form.value.correo_instructor &&
    form.value.celular_instructor
  ),
  formacion: !!(
    form.value.nombre_programa.trim().length >= 3 &&
    form.value.codigo_programa &&
    form.value.duracion_horas > 0
  ),
  fechas: !!(form.value.fecha_inicio_formacion && form.value.fecha_fin_formacion),
  logistica: !!(form.value.jornada && form.value.municipio && form.value.lugar_ejecucion),
  adjuntos: !!(archivos.value.matriz && archivos.value.plano),
}));

const abrirSelector = (campo) => inputsArchivo.value[campo]?.click();

const validarArchivo = (slot, archivo) => {
  const extension = (archivo.name.split('.').pop() || '').toLowerCase();
  if (!slot.extensiones.includes(extension)) {
    toast.error(
      `El formato ".${extension}" no es válido para ${slot.etiqueta.toLowerCase()}. ` +
        `Formatos permitidos: ${slot.extensiones.map((e) => '.' + e).join(', ')}.`
    );
    return false;
  }
  if (archivo.size > TAMANO_MAXIMO_MB * 1024 * 1024) {
    toast.error(`"${archivo.name}" supera el máximo de ${TAMANO_MAXIMO_MB} MB.`);
    return false;
  }
  if (archivo.size === 0) {
    toast.error(`"${archivo.name}" está vacío.`);
    return false;
  }
  return true;
};

const asignarArchivo = (slot, archivo) => {
  if (!archivo) return;
  if (validarArchivo(slot, archivo)) {
    archivos.value[slot.campo] = archivo;
  }
};

const seleccionarArchivo = (slot, evento) => {
  asignarArchivo(slot, evento.target.files?.[0]);
  evento.target.value = ''; // Permite volver a elegir el mismo archivo
};

const soltarArchivo = (slot, evento) => {
  arrastrando.value = null;
  asignarArchivo(slot, evento.dataTransfer.files?.[0]);
};

const quitarArchivo = (campo) => {
  archivos.value[campo] = null;
};

const formatearTamano = (bytes) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

// ── Mis solicitudes (solo lectura) ──
const misSolicitudes = ref([]);
const cargandoMis = ref(false);
const correoConsulta = ref(
  auth.instructorEmail || localStorage.getItem(CLAVE_CORREO) || ''
);

// ── Hero institucional (carrusel de afiches, solo visual) ──
// "posicion" es el recorte inteligente: qué franja del afiche muestra el banner
const AFICHES = [
  {
    src: imagenCampo,
    alt: 'Afiche del SENA y Fondo Emprender: convocatorias abiertas para emprendedores del campo',
    posicion: 'center 24%',
  },
  {
    src: imagenPaz,
    alt: 'Afiche de la feria de emprendimiento Sembradores de Paz en Puerto Asís, Putumayo',
    posicion: 'center 30%',
  },
];

const aficheActivo = ref(0);
let temporizadorCarrusel = null;

const irAAfiche = (i) => {
  aficheActivo.value = (i + AFICHES.length) % AFICHES.length;
};

const cambiarAfiche = (paso) => irAAfiche(aficheActivo.value + paso);

const pausarCarrusel = () => {
  if (temporizadorCarrusel) {
    clearInterval(temporizadorCarrusel);
    temporizadorCarrusel = null;
  }
};

const reanudarCarrusel = () => {
  // Sin auto-avance si ya corre o si el usuario pidió menos movimiento
  if (temporizadorCarrusel || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  temporizadorCarrusel = setInterval(() => cambiarAfiche(1), 6000);
};

// ── Barra fija de acceso a SOFIA Plus ──
const mostrarBarraSofia = ref(true);

// ── Botón flotante de WhatsApp (contacto con el área administrativa) ──
// ⚠️ Reemplazar por el número real del área administrativa: indicativo del país
// + celular, sin espacios ni signos (Colombia: 57 + 10 dígitos).
const NUMERO_WHATSAPP = '573134625175';
const ENLACE_WHATSAPP = `https://wa.me/${NUMERO_WHATSAPP}?text=${encodeURIComponent(
  'Hola, soy instructor del SENA y tengo una consulta sobre mi solicitud de ficha complementaria.'
)}`;

// ── Modal de bienvenida (se muestra en cada carga de la vista) ──
const mostrarBienvenida = ref(false);
const botonComenzar = ref(null);

const cerrarBienvenida = () => {
  mostrarBienvenida.value = false;
};

// ── Vista previa de la ficha (documento de SOLO LECTURA por solicitud) ──
const fichaEnVista = ref(null);

const PASOS_FICHA = [
  { campo: 'publicacion', etiqueta: 'Publicación de la oferta' },
  { campo: 'asignar_ficha', etiqueta: 'Asignación de ficha' },
  { campo: 'gestion_ficha', etiqueta: 'Gestión de la ficha' },
  { campo: 'proceso_matricula', etiqueta: 'Proceso de matrícula' },
];

const DESCRIPCIONES_ESTADO = {
  Pendiente: 'La coordinación recibió su solicitud y está en revisión.',
  Publicada: 'Su ficha fue publicada; los códigos asignados aparecen en este documento.',
  'En Ejecución': 'La formación se encuentra en ejecución.',
  Cancelada: 'La solicitud fue cancelada por la coordinación.',
};

const abrirFicha = (solicitud) => {
  fichaEnVista.value = solicitud;
};

const cerrarFicha = () => {
  fichaEnVista.value = null;
};

const descripcionEstado = (estado) => DESCRIPCIONES_ESTADO[estado] || '';

// Adjuntos que entregó el propio instructor (los resultados van en su sección)
const adjuntosEntregados = computed(() =>
  (fichaEnVista.value?.archivos || []).filter((a) => a.campo !== 'resultados')
);

// Excel de resultados que adjunta la coordinación: único documento descargable,
// visible solo cuando la ficha ya fue publicada (o está en ejecución)
const archivoResultados = computed(() => {
  const ficha = fichaEnVista.value;
  if (!ficha || !['Publicada', 'En Ejecución'].includes(ficha.estado)) return null;
  return (ficha.archivos || []).find((a) => a.campo === 'resultados') || null;
});

const urlResultados = computed(() =>
  fichaEnVista.value ? complementariasService.urlArchivo(fichaEnVista.value.id, 'resultados') : ''
);

// Mismo helper compartido del módulo, con el texto vacío propio de esta vista
const rangoFechas = (inicio, fin) => formatearRango(inicio, fin, 'Por definir');

const fechaGeneracion = computed(() => {
  if (!fichaEnVista.value) return '';
  return new Date().toLocaleString('es-CO', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
});

const cerrarConEscape = (evento) => {
  if (evento.key !== 'Escape') return;
  if (fichaEnVista.value) {
    cerrarFicha();
    return;
  }
  if (mostrarBienvenida.value) cerrarBienvenida();
};

// Bloquea el desplazamiento del fondo mientras algún popup está abierto
watch([mostrarBienvenida, fichaEnVista], ([bienvenida, ficha]) => {
  document.body.style.overflow = bienvenida || ficha ? 'hidden' : '';
});

// ── Perfil de la bienvenida ──
// Nombre desde la sesión (auth); si no hay sesión, sigue en vivo lo que el
// instructor escribe en el formulario. Solo lectura: no toca la funcionalidad.
const nombrePerfil = computed(
  () => auth.instructorName || form.value.nombre_instructor.trim() || 'Instructor SENA'
);

const inicialesPerfil = computed(() => {
  const partes = nombrePerfil.value.split(/\s+/).filter(Boolean);
  if (!partes.length) return 'IN';
  const primera = partes[0][0] || '';
  const segunda = partes.length > 1 ? partes[1][0] || '' : '';
  return (primera + segunda).toUpperCase();
});

const primerNombre = computed(() => nombrePerfil.value.split(/\s+/)[0]);

const saludo = computed(() => {
  const hora = new Date().getHours();
  if (hora < 12) return 'Buenos días';
  if (hora < 18) return 'Buenas tardes';
  return 'Buenas noches';
});

const cargarMisSolicitudes = async () => {
  if (!correoConsulta.value) return;
  cargandoMis.value = true;
  try {
    const lista = await complementariasService.getSolicitudes({ correo: correoConsulta.value });
    misSolicitudes.value = lista.sort((a, b) =>
      (b.fecha_creacion || '').localeCompare(a.fecha_creacion || '')
    );
  } catch (e) {
    toast.error(e.message);
  } finally {
    cargandoMis.value = false;
  }
};

// claseEstado y pasosCompletados vienen del store del módulo (helpers compartidos)

// ── Aviso abierto desde la campana (?solicitud=<id>) ──
const route = useRoute();
const router = useRouter();
const solicitudResaltada = ref(null);

const resaltarDesdeQuery = async () => {
  const id = route.query.solicitud;
  if (!id) return;
  await cargarMisSolicitudes();
  solicitudResaltada.value = id;
  // Limpiar el query para que recargar la página no repita el resaltado
  router.replace({ query: {} });
};

watch(() => route.query.solicitud, (id) => {
  if (id) resaltarDesdeQuery();
});

// ── Ciclo de vida ──
onMounted(async () => {
  if (auth.instructorName) form.value.nombre_instructor = auth.instructorName;
  if (auth.instructorEmail) form.value.correo_instructor = auth.instructorEmail;

  // La bienvenida aparece siempre al entrar o refrescar la vista
  mostrarBienvenida.value = true;
  nextTick(() => botonComenzar.value?.focus());
  window.addEventListener('keydown', cerrarConEscape);
  // reanudarCarrusel(); // Desactivado junto con el hero-carrusel del template (jul-2026)

  await cargarMisSolicitudes();
  resaltarDesdeQuery();
});

onUnmounted(() => {
  window.removeEventListener('keydown', cerrarConEscape);
  document.body.style.overflow = '';
  pausarCarrusel();
});

// ── Envío ──
const enviar = async () => {
  if (faltantes.value.length) {
    toast.error(`Falta adjuntar: ${faltantes.value.join(' y ')}.`);
    return;
  }

  enviando.value = true;
  try {
    await complementariasService.createSolicitudConArchivos(
      {
        ...form.value,
        duracion_horas: Number(form.value.duracion_horas) || 0,
        estado: 'Pendiente',
      },
      archivos.value
    );

    // Recordar el correo para poder listar "mis solicitudes" en próximas visitas
    correoConsulta.value = form.value.correo_instructor;
    localStorage.setItem(CLAVE_CORREO, correoConsulta.value);

    await Swal.fire({
      title: '¡Solicitud enviada!',
      text: 'Sus archivos quedaron almacenados y el administrador fue notificado. Puede seguir el estado en "Mis solicitudes".',
      icon: 'success',
      confirmButtonColor: '#39A900',
      confirmButtonText: 'Entendido',
    });

    // Limpiar la formación y los archivos, conservando los datos del instructor
    const { nombre_instructor, correo_instructor, celular_instructor } = form.value;
    form.value = { ...formVacio(), nombre_instructor, correo_instructor, celular_instructor };
    archivos.value = { matriz: null, plano: null, adicional: null };
    await cargarMisSolicitudes();
  } catch (e) {
    toast.error(e.message);
  } finally {
    enviando.value = false;
  }
};
</script>

<style scoped>
/* ============================================================================
   Vista del instructor — pulido visual (identidad SENA, filosofía "menos es más")
   Misma estructura y funcionalidad; solo cambia la capa de presentación:
   degradados muy sutiles, sombras en capas, transiciones y profundidad suaves.
   ============================================================================ */
.solicitud-shell {
  min-height: 100vh;
  font-family: var(--fuente-principal);
  color: var(--texto-principal);
  padding: 2rem 1.5rem 3rem;
  box-sizing: border-box;
  /* Fondo con dos brillos institucionales casi imperceptibles sobre el color base */
  background:
    radial-gradient(1100px 500px at 85% -10%, rgba(57, 169, 0, 0.07), transparent 60%),
    radial-gradient(900px 460px at -15% 35%, rgba(0, 50, 77, 0.05), transparent 55%),
    var(--fondo-app);
}

.solicitud-contenedor {
  max-width: 860px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Entrada escalonada de las tres tarjetas al cargar la página */
@keyframes aparece-suave {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

.hero-carrusel { animation: aparece-suave 0.5s cubic-bezier(0.2, 0.7, 0.3, 1) both; }
.mis-solicitudes { animation: aparece-suave 0.6s 0.42s cubic-bezier(0.2, 0.7, 0.3, 1) both; }

/* Cada tarjeta del formulario entra con un pequeño desfase (cascada) */
.form-comp > * { animation: aparece-suave 0.55s cubic-bezier(0.2, 0.7, 0.3, 1) both; }
.form-comp > *:nth-child(1) { animation-delay: 0.08s; }
.form-comp > *:nth-child(2) { animation-delay: 0.13s; }
.form-comp > *:nth-child(3) { animation-delay: 0.18s; }
.form-comp > *:nth-child(4) { animation-delay: 0.23s; }
.form-comp > *:nth-child(5) { animation-delay: 0.28s; }
.form-comp > *:nth-child(6) { animation-delay: 0.33s; }

/* ── Popup de bienvenida: aparece una sola vez por sesión ── */
.bienvenida-fondo {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  box-sizing: border-box;
  /* Velo suave: el formulario sigue visible detrás del anuncio */
  background: rgba(2, 22, 33, 0.28);
  -webkit-backdrop-filter: blur(2.5px);
  backdrop-filter: blur(2.5px);
}

/* Tarjeta ancha tipo banner sobre un degradado institucional vibrante */
.bienvenida-card {
  position: relative;
  width: min(880px, 100%);
  overflow: hidden;
  border-radius: 26px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: linear-gradient(115deg, #00324d 0%, #075a6e 34%, #0b7a33 72%, #39a900 100%);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.12),
    0 34px 90px -30px rgba(0, 20, 30, 0.65);
  color: #fff;
}

/* Luces en movimiento sobre todo el banner (efecto mesh gradient) */
.bienvenida-luces {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.luz {
  position: absolute;
  border-radius: 50%;
  will-change: transform;
}

.luz-a {
  width: 480px;
  height: 480px;
  top: -240px;
  right: -110px;
  background: radial-gradient(closest-side, rgba(222, 255, 154, 0.3), transparent 70%);
  animation: deriva-a 22s ease-in-out infinite alternate;
}

.luz-b {
  width: 440px;
  height: 440px;
  bottom: -260px;
  left: -140px;
  background: radial-gradient(closest-side, rgba(80, 229, 249, 0.22), transparent 70%);
  animation: deriva-b 28s ease-in-out infinite alternate;
}

.luz-c {
  width: 360px;
  height: 360px;
  top: -150px;
  left: 30%;
  background: radial-gradient(closest-side, rgba(255, 255, 255, 0.14), transparent 70%);
  animation: deriva-c 25s ease-in-out infinite alternate;
}

@keyframes deriva-a {
  from { transform: translate(0, 0) scale(1); }
  to { transform: translate(-60px, 40px) scale(1.15); }
}

@keyframes deriva-b {
  from { transform: translate(0, 0) scale(1); }
  to { transform: translate(70px, -35px) scale(1.1); }
}

@keyframes deriva-c {
  from { transform: translate(0, 0) scale(1); }
  to { transform: translate(50px, 25px) scale(0.9); }
}

/* Botón de cierre en vidrio, sobre la portada */
.bienvenida-cerrar {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.14);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  color: #fff;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.25s ease, transform 0.25s ease;
}

.bienvenida-cerrar:hover {
  background: rgba(255, 255, 255, 0.28);
  transform: scale(1.06);
}

.bienvenida-cerrar:focus-visible {
  outline: 2px solid #fff;
  outline-offset: 2px;
}

/* ── Titular del banner ── */
.bienvenida-encabezado {
  position: relative;
  padding: 2.2rem 2.6rem 1.5rem;
  text-align: center;
}

.bienvenida-eyebrow {
  margin: 0;
  font-size: 0.66rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.6);
}

.bienvenida-titulo {
  margin: 10px 0 0;
  font-size: clamp(1.9rem, 4.5vw, 2.7rem);
  font-weight: 800;
  letter-spacing: -0.01em;
  line-height: 1.12;
  color: #fff;
  text-shadow: 0 2px 18px rgba(0, 20, 30, 0.25);
}

/* Degradado sutil en el titular, con blanco como respaldo */
@supports ((-webkit-background-clip: text) or (background-clip: text)) {
  .bienvenida-titulo {
    background: linear-gradient(100deg, #ffffff 55%, #deff9a);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: none;
  }
}

.bienvenida-sub {
  margin: 10px auto 0;
  max-width: 520px;
  font-size: 0.92rem;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.78);
}

/* ── Franja de contraste con el recordatorio (a lo ancho del banner) ── */
.bienvenida-franja {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 1rem 2.6rem;
  background: rgba(255, 255, 255, 0.96);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    0 10px 30px -18px rgba(0, 20, 30, 0.5);
}

.franja-icono {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: linear-gradient(145deg, #43b80a, var(--sena-verde) 60%, #2e8a00);
  box-shadow: 0 8px 18px -8px rgba(57, 169, 0, 0.7);
  color: #fff;
  font-size: 1.25rem;
  font-weight: 800;
  user-select: none;
}

.franja-texto {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
  color: #00324d;
}

.franja-texto strong {
  font-weight: 800;
  color: #00324d;
}

.franja-verde {
  font-weight: 800;
  color: #2e8a00;
}

/* ── Pie del banner: llamada a la acción + identidad de la sesión ── */
.bienvenida-pie {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1.5rem 2.6rem 1.8rem;
}

.btn-comenzar {
  border: none;
  border-radius: 999px;
  padding: 0.85rem 2.6rem;
  background: #fff;
  color: #00324d;
  font-family: inherit;
  font-size: 0.9rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  cursor: pointer;
  box-shadow: 0 14px 30px -14px rgba(0, 20, 30, 0.7);
  transition: transform 0.25s ease, box-shadow 0.25s ease, filter 0.25s ease;
}

.btn-comenzar:hover {
  transform: translateY(-2px);
  filter: brightness(1.03);
  box-shadow: 0 18px 36px -14px rgba(0, 20, 30, 0.75);
}

.btn-comenzar:active {
  transform: translateY(0) scale(0.99);
}

.btn-comenzar:focus-visible {
  outline: 2px solid #fff;
  outline-offset: 3px;
}

.pie-identidad {
  display: flex;
  align-items: center;
  gap: 11px;
  min-width: 0;
}

.pie-avatar {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: linear-gradient(145deg, #43b80a, var(--sena-verde) 60%, #2e8a00);
  border: 2px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 18px -8px rgba(0, 20, 30, 0.6);
  color: #fff;
  font-size: 0.92rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  user-select: none;
}

.pie-datos {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.pie-nombre {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  font-weight: 800;
  line-height: 1.2;
  color: #fff;
}

.bienvenida-verificado {
  color: #deff9a;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.pie-rol {
  font-size: 0.72rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.68);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Entrada y salida del popup (Transition "bienvenida") */
.bienvenida-enter-active { transition: opacity 0.35s ease; }
.bienvenida-leave-active { transition: opacity 0.25s ease; }
.bienvenida-enter-from,
.bienvenida-leave-to { opacity: 0; }

.bienvenida-enter-active .bienvenida-card {
  animation: bienvenida-entra 0.5s cubic-bezier(0.2, 0.7, 0.3, 1) both;
}

.bienvenida-leave-active .bienvenida-card {
  animation: bienvenida-sale 0.25s ease both;
}

@keyframes bienvenida-entra {
  from {
    opacity: 0;
    transform: translateY(22px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

@keyframes bienvenida-sale {
  to {
    opacity: 0;
    transform: translateY(12px) scale(0.97);
  }
}

.module-card {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 20px;
  padding: 1.75rem;
  box-shadow:
    0 1px 2px rgba(0, 48, 64, 0.04),
    0 16px 40px -24px rgba(0, 48, 64, 0.14);
}

/* ── Formulario: pila de tarjetas independientes sobre el fondo ── */
.form-comp {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

/* ── Secciones del formulario como tarjetas ── */
.grupo {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 20px;
  padding: 1.4rem 1.6rem 1.6rem;
  margin: 0;
  box-shadow:
    0 1px 2px rgba(0, 48, 64, 0.04),
    0 16px 40px -24px rgba(0, 48, 64, 0.14);
  transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

/* La tarjeta activa se eleva apenas, sin saltar */
.grupo:focus-within {
  border-color: rgba(57, 169, 0, 0.35);
  transform: translateY(-2px);
  box-shadow:
    0 1px 2px rgba(0, 48, 64, 0.04),
    0 22px 48px -26px rgba(57, 169, 0, 0.4);
}

/* Encabezado de cada sección: icono, título, descripción y check */
.grupo-head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 1.2rem;
}

.grupo-icono {
  flex-shrink: 0;
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(57, 169, 0, 0.1);
  color: var(--sena-verde);
  font-size: 0.95rem;
}

.grupo-titulos {
  flex: 1;
  min-width: 0;
}

.grupo-titulos h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  line-height: 1.3;
}

.grupo-titulos p {
  margin: 3px 0 0;
  font-size: 0.74rem;
  line-height: 1.45;
  color: var(--texto-secundario);
}

/* Check de sección completa: aparece con una entrada suave */
.grupo-check {
  flex-shrink: 0;
  color: var(--sena-verde);
  font-size: 1.05rem;
  margin-top: 2px;
  animation: aparece-suave 0.3s cubic-bezier(0.2, 0.7, 0.3, 1) both;
}

.fila {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.85rem;
  flex-wrap: wrap;
}

.fila:last-child {
  margin-bottom: 0;
}

.campo {
  flex: 1;
  min-width: 160px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.campo-doble {
  flex-basis: 100%;
}

.campo > span {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--texto-secundario);
}

/* Campos rellenos (estilo Notion/Linear): contrastan sobre la tarjeta blanca */
.form-input {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 10px;
  padding: 0.65rem 0.9rem;
  color: var(--texto-principal);
  font-family: inherit;
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
  width: 100%;
  box-sizing: border-box;
}

.form-input:hover {
  border-color: rgba(57, 169, 0, 0.35);
}

.form-input:focus {
  border-color: var(--sena-verde);
  background: var(--fondo-tarjetas);
  box-shadow: 0 0 0 3px rgba(57, 169, 0, 0.14);
}

/* ── Casillas de carga de archivos ── */
.zona-adjuntos {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.dropzone {
  border: 1.5px dashed var(--borde);
  border-radius: 16px;
  background: var(--fondo-app);
  padding: 1.4rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 7px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.25s ease, background 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
}

.dropzone:hover,
.dropzone.arrastrando {
  border-color: var(--sena-verde);
  background: rgba(57, 169, 0, 0.04);
  transform: translateY(-2px);
  box-shadow: 0 12px 28px -18px rgba(57, 169, 0, 0.45);
}

.dropzone.requerido {
  border-color: rgba(253, 195, 0, 0.65);
}

.dropzone.con-archivo {
  border-style: solid;
  border-color: rgba(57, 169, 0, 0.55);
  background: linear-gradient(180deg, rgba(57, 169, 0, 0.05), transparent 70%), var(--fondo-tarjetas);
}

.input-oculto {
  display: none;
}

/* Icono dentro de un círculo suave: acento de color sin recargar */
.dropzone-icono {
  font-size: 1.15rem;
  color: var(--sena-verde);
  background: rgba(57, 169, 0, 0.1);
  border-radius: 999px;
  padding: 0.8rem;
  transition: transform 0.25s ease;
}

.dropzone:hover .dropzone-icono {
  transform: translateY(-2px);
}

.dropzone-icono.ok {
  color: var(--sena-blanco);
  background: var(--sena-verde);
}

.dropzone-titulo {
  font-size: 0.78rem;
  font-weight: 800;
  color: var(--texto-principal);
}

.dropzone-titulo strong {
  color: #e53e3e;
}

.dropzone-ayuda {
  font-size: 0.7rem;
  color: var(--texto-secundario);
}

.archivo-nombre {
  font-size: 0.74rem;
  font-family: monospace;
  color: var(--sena-verde-oscuro);
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.archivo-tamano {
  font-size: 0.68rem;
  color: var(--texto-secundario);
  font-family: monospace;
}

.archivo-acciones {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.btn-mini {
  background: transparent;
  border: 1px solid var(--borde);
  border-radius: 999px;
  padding: 0.32rem 0.75rem;
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--texto-secundario);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  transition: border-color 0.25s ease, color 0.25s ease, background 0.25s ease;
}

.btn-mini:hover {
  border-color: var(--sena-verde);
  color: var(--sena-verde);
  background: rgba(57, 169, 0, 0.06);
}

.btn-mini.quitar:hover {
  border-color: #e53e3e;
  color: #e53e3e;
  background: rgba(229, 62, 62, 0.06);
}

.btn-mini:focus-visible,
.btn-enviar:focus-visible {
  outline: 2px solid var(--sena-verde);
  outline-offset: 2px;
}

.aviso-faltantes {
  margin: 1rem 0 0;
  font-size: 0.75rem;
  color: #8a6d00;
  background: rgba(253, 195, 0, 0.12);
  border: 1px solid rgba(253, 195, 0, 0.35);
  border-radius: 10px;
  padding: 0.65rem 1rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

[data-theme="dark"] .aviso-faltantes {
  color: #fdc300;
}

.acciones {
  display: flex;
  justify-content: flex-end;
}

.btn-enviar {
  background: linear-gradient(180deg, #43b80a, var(--sena-verde));
  color: var(--sena-blanco);
  border: none;
  padding: 0.85rem 2.1rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: transform 0.25s ease, box-shadow 0.25s ease, filter 0.25s ease;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.18),
    0 8px 20px -8px rgba(57, 169, 0, 0.55);
}

.btn-enviar:hover:not(:disabled) {
  transform: translateY(-2px);
  filter: brightness(1.04);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.18),
    0 12px 26px -10px rgba(57, 169, 0, 0.6);
}

.btn-enviar:active:not(:disabled) {
  transform: translateY(0) scale(0.99);
}

.btn-enviar:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

/* ── Mis solicitudes (comparte el encabezado de las tarjetas) ── */
.mis-header {
  flex-wrap: wrap;
}

.mis-header .btn-mini {
  margin-top: 4px;
}

.mis-vacio {
  margin: 0;
  padding: 1.25rem 0.5rem;
  text-align: center;
  color: var(--texto-secundario);
  font-size: 0.82rem;
  font-style: italic;
}

.mis-lista {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mi-solicitud {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 14px;
  padding: 0.9rem 1.2rem;
  flex-wrap: wrap;
  transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.mi-solicitud:hover {
  border-color: rgba(57, 169, 0, 0.35);
  transform: translateY(-1px);
  box-shadow: 0 10px 24px -18px rgba(0, 48, 64, 0.35);
}

/* Solicitud abierta desde un aviso de la campana */
.mi-solicitud.resaltada {
  border-color: var(--sena-verde);
  box-shadow: 0 0 0 3px rgba(57, 169, 0, 0.18);
}

.mi-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 200px;
}

.mi-programa {
  font-size: 0.88rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
}

.mi-detalle {
  font-size: 0.72rem;
  color: var(--texto-secundario);
  font-family: monospace;
}

.mi-derecha {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.mi-pasos {
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--texto-secundario);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.35rem 0.9rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.status-yellow { background: rgba(253, 195, 0, 0.18); color: #8a6d00; }
[data-theme="dark"] .status-yellow { color: #fdc300; }
.status-blue { background: rgba(0, 48, 64, 0.1); color: var(--sena-azul-oscuro); }
[data-theme="dark"] .status-blue { background: rgba(80, 229, 249, 0.12); }
.status-green { background: rgba(57, 169, 0, 0.15); color: var(--sena-verde-oscuro); }
.status-red { background: rgba(244, 67, 54, 0.15); color: #d32f2f; }
.status-gray { background: var(--fondo-app); color: var(--texto-secundario); }

.btn-ver-ficha {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 999px;
  padding: 0.4rem 0.9rem;
  font-family: inherit;
  font-size: 0.74rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-ver-ficha:hover,
.btn-ver-ficha:focus-visible {
  border-color: var(--sena-verde);
  color: var(--sena-verde-oscuro);
  outline: none;
}

/* ── Vista previa de la ficha: documento institucional de solo lectura ── */
.ficha-fondo {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(2, 22, 33, 0.45);
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(3px);
}

.ficha-doc {
  width: min(760px, 100%);
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  border-radius: 18px;
  overflow: hidden;
  background: var(--fondo-tarjetas, #fff);
  box-shadow: 0 30px 80px -20px rgba(0, 20, 30, 0.55);
}

/* Membrete: franja institucional del documento */
.ficha-membrete {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0.9rem 1.4rem;
  background: linear-gradient(100deg, #00324d 0%, #075a6e 55%, #0b7a33 100%);
  color: #fff;
}

.membrete-textos {
  flex: 1;
  min-width: 0;
}

.membrete-entidad {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.membrete-centro {
  margin: 2px 0 0;
  font-size: 0.7rem;
  opacity: 0.85;
}

.chip-solo-lectura {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 999px;
  padding: 0.3rem 0.8rem;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  white-space: nowrap;
}

.ficha-cerrar {
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.14);
  color: #fff;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.2s ease;
}

.ficha-cerrar:hover,
.ficha-cerrar:focus-visible {
  background: rgba(255, 255, 255, 0.28);
  outline: none;
}

.ficha-cuerpo {
  overflow-y: auto;
  padding: 1.4rem 1.6rem 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ficha-encabezado {
  text-align: center;
  padding-bottom: 0.9rem;
  border-bottom: 2px solid var(--sena-verde);
}

.ficha-eyebrow {
  margin: 0;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--texto-secundario);
}

.ficha-programa {
  margin: 0.35rem 0 0.3rem;
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--sena-azul-oscuro);
  line-height: 1.25;
}

.ficha-codigos {
  margin: 0;
  font-size: 0.75rem;
  font-family: monospace;
  color: var(--texto-secundario);
}

.ficha-seccion {
  background: var(--fondo-app);
  border: 1px solid var(--borde);
  border-radius: 12px;
  padding: 0.9rem 1.1rem;
}

.ficha-seccion-titulo {
  margin: 0 0 0.7rem;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--texto-secundario);
  display: flex;
  align-items: center;
  gap: 8px;
}

.ficha-seccion-titulo svg {
  color: var(--sena-verde);
}

/* Estado + seguimiento */
.ficha-estado {
  border-left: 4px solid var(--sena-verde);
}

.estado-fila {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 0.8rem;
}

.estado-descripcion {
  font-size: 0.8rem;
  color: var(--texto-principal);
}

.estado-pasos {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px;
}

.estado-pasos li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.76rem;
  font-weight: 700;
  color: var(--texto-secundario);
}

.estado-pasos li.hecho {
  color: var(--sena-verde-oscuro);
}

.paso-punto {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--borde);
  background: var(--fondo-tarjetas);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6rem;
  flex-shrink: 0;
}

.estado-pasos li.hecho .paso-punto {
  background: var(--sena-verde);
  border-color: var(--sena-verde);
  color: #fff;
}

/* Grilla de secciones del documento */
.ficha-grilla {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.ficha-datos {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.ficha-dato {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
}

.ficha-dato dt {
  font-size: 0.76rem;
  color: var(--texto-secundario);
  flex-shrink: 0;
}

.ficha-dato dd {
  margin: 0;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--texto-principal);
  text-align: right;
  overflow-wrap: anywhere;
}

.dato-fechas {
  font-family: monospace;
}

.en-tramite {
  font-weight: 400;
  font-style: italic;
  font-size: 0.76rem;
  color: var(--texto-secundario);
}

/* Adjuntos: solo el nombre, sin descarga */
.ficha-adjuntos {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ficha-adjuntos li {
  display: flex;
  align-items: baseline;
  gap: 8px;
  font-size: 0.8rem;
  color: var(--texto-principal);
  flex-wrap: wrap;
}

.ficha-adjuntos svg {
  color: var(--sena-verde);
}

.adjunto-tipo {
  font-weight: 800;
}

.adjunto-archivo {
  font-family: monospace;
  font-size: 0.74rem;
  color: var(--texto-secundario);
  overflow-wrap: anywhere;
}

.ficha-sin-adjuntos {
  margin: 0;
  font-size: 0.8rem;
  font-style: italic;
  color: var(--texto-secundario);
}

.ficha-nota-adjuntos {
  margin: 0.7rem 0 0;
  font-size: 0.72rem;
  color: var(--texto-secundario);
  border-top: 1px dashed var(--borde);
  padding-top: 0.6rem;
}

/* Resultados de inscritos: único documento descargable */
.ficha-resultados {
  border-left: 4px solid var(--sena-verde);
}

.resultados-fila {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.resultados-datos {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 160px;
}

.resultados-etiqueta {
  font-size: 0.82rem;
  font-weight: 800;
  color: var(--texto-principal);
}

.resultados-archivo {
  font-family: monospace;
  font-size: 0.74rem;
  color: var(--texto-secundario);
  overflow-wrap: anywhere;
}

.btn-descargar-resultados {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--sena-verde);
  border: none;
  border-radius: 8px;
  padding: 0.55rem 1.1rem;
  font-size: 0.78rem;
  font-weight: 800;
  color: #fff;
  text-decoration: none;
  transition: all 0.2s ease;
}

.btn-descargar-resultados:hover {
  background: var(--sena-verde-oscuro, #2e8500);
  transform: translateY(-1px);
}

.ficha-observaciones {
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.5;
  color: var(--texto-principal);
}

/* Pie del documento */
.ficha-pie {
  text-align: center;
  border-top: 1px solid var(--borde);
  padding-top: 0.8rem;
}

.ficha-pie p {
  margin: 0 0 3px;
  font-size: 0.68rem;
  color: var(--texto-secundario);
}

/* Transición del documento */
.ficha-enter-active,
.ficha-leave-active {
  transition: opacity 0.25s ease;
}

.ficha-enter-from,
.ficha-leave-to {
  opacity: 0;
}

.ficha-enter-active .ficha-doc {
  animation: ficha-sube 0.3s cubic-bezier(0.2, 0.7, 0.3, 1) both;
}

@keyframes ficha-sube {
  from {
    opacity: 0;
    transform: translateY(22px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ── Hero institucional a todo el ancho (borde a borde del área de la vista) ── */
/* Los márgenes negativos cancelan el padding del shell: el banner llega a los bordes */
.hero-carrusel {
  position: relative;
  height: clamp(250px, 32vw, 400px);
  margin: -2rem -1.5rem 2rem;
  border-radius: 0 0 30px 30px;
  overflow: hidden;
  background: linear-gradient(115deg, #00324d 0%, #063f57 55%, #06391f 100%);
  box-shadow:
    inset 0 -1px 0 rgba(255, 255, 255, 0.06),
    0 30px 70px -35px rgba(0, 30, 45, 0.65);
}

.hero-lamina {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 1.1s ease;
}

.hero-lamina.activa {
  opacity: 1;
}

/* La imagen llena TODO el banner sin deformarse; "object-position" fija el foco */
.hero-imagen {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  will-change: transform;
}

/* Ken Burns: zoom lento con una deriva mínima mientras la lámina está visible.
   Las láminas pares derivan al lado contrario para que el ciclo no se sienta repetido. */
.hero-lamina.activa .hero-imagen {
  animation: ken-burns 9s ease-out both;
}

.hero-lamina:nth-child(even).activa .hero-imagen {
  animation-name: ken-burns-inverso;
}

@keyframes ken-burns {
  from { transform: scale(1) translateX(0); }
  to { transform: scale(1.08) translateX(-1.2%); }
}

@keyframes ken-burns-inverso {
  from { transform: scale(1) translateX(0); }
  to { transform: scale(1.08) translateX(1.2%); }
}

/* Velo sutil: da profundidad y legibilidad a los puntos indicadores */
.hero-velo {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  background: linear-gradient(
    180deg,
    rgba(0, 20, 30, 0.18),
    transparent 26%,
    transparent 66%,
    rgba(0, 20, 30, 0.45)
  );
}

.carrusel-puntos {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 12px;
  z-index: 2;
  display: flex;
  justify-content: center;
  gap: 8px;
}

.carrusel-punto {
  width: 9px;
  height: 9px;
  padding: 0;
  border: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.45);
  box-shadow: 0 1px 4px rgba(0, 20, 30, 0.4);
  cursor: pointer;
  transition: background 0.3s ease, width 0.3s ease;
}

.carrusel-punto.activo {
  width: 22px;
  background: #fff;
}

.carrusel-punto:focus-visible {
  outline: 2px solid #fff;
  outline-offset: 2px;
}

/* ── Botón flotante de WhatsApp (contacto con el área administrativa) ── */
.btn-whatsapp {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 910; /* sobre la barra de SOFIA (900), bajo los popups (1000) */
  width: 54px;
  height: 54px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: linear-gradient(180deg, #2fdd72, #1ebe5d);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.25),
    0 4px 10px rgba(0, 20, 30, 0.18),
    0 14px 30px -12px rgba(30, 190, 93, 0.6);
  text-decoration: none;
  animation: aparece-suave 0.5s 0.5s cubic-bezier(0.2, 0.7, 0.3, 1) both;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.btn-whatsapp:hover,
.btn-whatsapp:focus-visible {
  transform: translateY(-3px) scale(1.05);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.25),
    0 6px 14px rgba(0, 20, 30, 0.2),
    0 18px 36px -12px rgba(30, 190, 93, 0.7);
}

.btn-whatsapp:focus-visible {
  outline: 2px solid var(--sena-verde);
  outline-offset: 3px;
}

/* Cuando la barra de SOFIA está visible, el botón sube para no taparla */
.solicitud-shell.con-barra .btn-whatsapp {
  bottom: 92px;
}

.whatsapp-icono {
  width: 28px;
  height: 28px;
}

/* Tooltip institucional a la izquierda del botón */
.whatsapp-tooltip {
  position: absolute;
  right: calc(100% + 14px);
  top: 50%;
  transform: translateY(-50%) translateX(6px);
  background: var(--sena-azul-oscuro, #00324d);
  color: #fff;
  font-size: 0.72rem;
  font-weight: 700;
  line-height: 1.3;
  padding: 0.5rem 0.85rem;
  border-radius: 8px;
  white-space: nowrap;
  box-shadow: 0 8px 20px -8px rgba(0, 20, 30, 0.5);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

/* Flecha del tooltip apuntando al botón */
.whatsapp-tooltip::after {
  content: '';
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  border: 5px solid transparent;
  border-left-color: var(--sena-azul-oscuro, #00324d);
}

.btn-whatsapp:hover .whatsapp-tooltip,
.btn-whatsapp:focus-visible .whatsapp-tooltip {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
}

/* ── Barra fija de acceso a SOFIA Plus ── */
/* Reserva espacio abajo para que la barra nunca tape el final del formulario */
.solicitud-shell.con-barra {
  padding-bottom: 7.5rem;
}

.barra-sofia {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 900;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px 14px;
  padding: 0.8rem 1.5rem;
  background: linear-gradient(90deg, #032838 0%, #00324d 60%, #06391f 100%);
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 -12px 34px -18px rgba(0, 20, 30, 0.6);
  color: #fff;
}

.barra-icono {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(145deg, #43b80a, var(--sena-verde) 60%, #2e8a00);
  box-shadow: 0 6px 14px -6px rgba(57, 169, 0, 0.7);
  color: #fff;
  font-size: 0.85rem;
}

.barra-texto {
  flex: 1;
  min-width: 220px;
  margin: 0;
  font-size: 0.8rem;
  line-height: 1.45;
  color: rgba(255, 255, 255, 0.85);
}

.barra-texto strong {
  color: #fff;
  font-weight: 800;
}

.barra-acciones {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  margin-left: auto;
}

.barra-boton {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0.55rem 1.3rem;
  border-radius: 999px;
  background: #fff;
  color: #00324d;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.3px;
  text-decoration: none;
  white-space: nowrap;
  box-shadow: 0 10px 22px -12px rgba(0, 20, 30, 0.8);
  transition: transform 0.25s ease, box-shadow 0.25s ease, filter 0.25s ease;
}

.barra-boton:hover {
  transform: translateY(-1px);
  filter: brightness(1.03);
}

.barra-boton:focus-visible {
  outline: 2px solid #fff;
  outline-offset: 2px;
}

.barra-cerrar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 0.8rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.25s ease;
}

.barra-cerrar:hover {
  background: rgba(255, 255, 255, 0.22);
}

.barra-cerrar:focus-visible {
  outline: 2px solid #fff;
  outline-offset: 2px;
}

/* La barra entra y sale deslizándose por el borde inferior */
.barra-enter-active {
  transition: transform 0.45s cubic-bezier(0.2, 0.7, 0.3, 1), opacity 0.45s ease;
}

.barra-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.barra-enter-from,
.barra-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

/* Accesibilidad: sin movimiento para quien lo pide (se conservan los spinners) */
@media (prefers-reduced-motion: reduce) {
  .form-comp > *,
  .mis-solicitudes,
  .hero-carrusel,
  .hero-lamina.activa .hero-imagen,
  .luz,
  .grupo-check,
  .bienvenida-enter-active .bienvenida-card,
  .bienvenida-leave-active .bienvenida-card,
  .ficha-enter-active .ficha-doc,
  .btn-whatsapp {
    animation: none;
  }

  .btn-whatsapp:hover,
  .btn-whatsapp:focus-visible,
  .btn-descargar-resultados:hover {
    transform: none;
  }

  .bienvenida-enter-active,
  .bienvenida-leave-active,
  .barra-enter-active,
  .barra-leave-active,
  .ficha-enter-active,
  .ficha-leave-active,
  .hero-lamina {
    transition: none;
  }

  .barra-boton:hover {
    transform: none;
  }

  .grupo:focus-within,
  .dropzone:hover,
  .dropzone:hover .dropzone-icono,
  .btn-enviar:hover:not(:disabled),
  .btn-enviar:active:not(:disabled),
  .btn-comenzar:hover,
  .btn-comenzar:active,
  .bienvenida-cerrar:hover,
  .mi-solicitud:hover {
    transform: none;
  }
}

@media (max-width: 768px) {
  .solicitud-shell {
    padding: 1.25rem 1rem 2rem;
  }

  .bienvenida-fondo {
    padding: 1rem;
  }

  .ficha-fondo {
    padding: 0.75rem;
  }

  .ficha-doc {
    max-height: 92vh;
  }

  .ficha-membrete {
    flex-wrap: wrap;
    padding: 0.8rem 1rem;
  }

  .ficha-cuerpo {
    padding: 1.1rem 1rem 1rem;
  }

  .ficha-dato {
    flex-direction: column;
    gap: 2px;
  }

  .ficha-dato dd {
    text-align: left;
  }

  .mi-derecha {
    width: 100%;
    justify-content: space-between;
  }

  .bienvenida-encabezado {
    padding: 1.8rem 1.3rem 1.2rem;
  }

  .bienvenida-franja {
    padding: 0.9rem 1.3rem;
    text-align: left;
  }

  .bienvenida-pie {
    flex-direction: column-reverse;
    align-items: stretch;
    padding: 1.3rem 1.3rem 1.5rem;
  }

  .btn-comenzar {
    width: 100%;
  }

  .pie-identidad {
    justify-content: center;
  }

  .grupo {
    padding: 1.2rem 1.1rem 1.3rem;
  }

  .hero-carrusel {
    height: 210px;
    margin: -1.25rem -1rem 1.5rem;
    border-radius: 0 0 20px 20px;
  }

  .btn-enviar {
    width: 100%;
    justify-content: center;
  }

  .solicitud-shell.con-barra {
    padding-bottom: 9.5rem;
  }

  .btn-whatsapp {
    right: 16px;
    bottom: 16px;
    width: 50px;
    height: 50px;
  }

  /* Sube por encima de la barra de SOFIA y de la campana (bottom: 84px) */
  .solicitud-shell.con-barra .btn-whatsapp {
    bottom: 144px;
  }

  .whatsapp-tooltip {
    display: none; /* en táctil no hay hover; el aria-label cubre la accesibilidad */
  }

  .barra-sofia {
    padding: 0.7rem 1rem;
  }

  .barra-acciones {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
