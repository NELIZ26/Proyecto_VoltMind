Aquí tienes el contenido completo y organizado para tu archivo `README.md`. Este documento es la "Biblia" del proyecto para tu equipo; si lo siguen al pie de la letra, no deberían tener ningún error de compilación.

Copia y pega lo siguiente en un archivo llamado `README.md` dentro de la carpeta `frontend`:

---

# ⚡ VoltMind Access - Frontend (Vue.js + Capacitor)

Este repositorio contiene la interfaz profesional de **VoltMind Access**, diseñada para la gestión de energía y control de asistencia mediante NFC en los ambientes de formación del SENA.

## 🛠️ Requisitos del Sistema

* **Node.js**: v18.0 o superior.
* **NPM**: v9.0 o superior.
* **Editor**: VS Code (Recomendado: Extensión *Material Icon Theme* para ver iconos en las carpetas).

---

## 📦 Instalación del Proyecto (Cero Errores)

Si acabas de clonar el repositorio o estás iniciando en una máquina nueva, ejecuta estos comandos en orden dentro de la carpeta `frontend`:

### 1. Instalación de dependencias base

```bash
# Instala todas las librerías registradas en el package.json
npm install

```

### 2. Librerías específicas instaladas (Resumen)

En caso de que necesites reinstalar algo manualmente, estos son los paquetes que estamos usando:

* **Navegación y Estado:** `npm install vue-router@4 pinia`
* **Iconografía:** `npm install @fortawesome/fontawesome-svg-core @fortawesome/free-solid-svg-icons @fortawesome/vue-fontawesome@latest-3`
* **Móvil (Capacitor):** `npm install @capacitor/core @capacitor/cli`
* **Hardware (NFC):** `npm install phonegap-nfc @awesome-cordova-plugins/nfc`
* **Desarrollo (DevTools):** `npm install @types/node @vitejs/plugin-vue -D`

---

## 🏗️ Estructura de Navegación Inteligente

El sistema detecta automáticamente el dispositivo y redirige según el rol:

1. **Login SENA (`/`)**: Pantalla de entrada obligatoria.
2. **Si es Tablet/PC (`/select-ficha`)**: Selección de ficha de formación.
3. **Dashboard Instructor (`/tablet-dashboard`)**: Control de Relé (Energía) y monitoreo de Watts.
4. **Si es Móvil/App (`/mobile-card`)**: Carnet Digital del aprendiz listo para lectura NFC.

### Organización de Carpetas (Vista `src/views/`)

* 📂 `display/`: Vistas optimizadas para pantallas grandes (Dashboard, Selección de Ficha). *Icono de monitor.*
* 📂 `mobile/`: Vistas optimizadas para celulares (Carnet Digital). *Icono de celular.*

---

## ⚙️ Configuraciones Críticas

Para que el alias `@` (rutas relativas limpias) funcione, se han configurado dos archivos:

### `vite.config.js`

Permite importar archivos usando `@/` en lugar de `../../`.

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue()
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})

```

### `jsconfig.json`

Evita que VS Code marque errores de "archivo no encontrado" al usar el arroba.

```json
{
  "compilerOptions": {
    "ignoreDeprecations": "5.0",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}

```

---

## 🎨 Identidad Visual (SENA)

Se utilizan variables globales de CSS para mantener la coherencia:

* **Principal:** `--sena-verde` (#39A900)
* **Acento:** `--sena-verde-claro` (#deff9a)
* **Contraste:** `--sena-azul` (#00324D)
* **Fondo:** `--sena-gris-fondo` (#f4f7f6)

---

## 🚀 Comandos de Ejecución

* **Modo Desarrollo:** `npm run dev`
* **Compilar para Producción:** `npm run build`
* **Sincronizar con Android:** `npx cap sync android`

---

> **⚠️ IMPORTANTE:** Nunca subas la carpeta `node_modules/` ni archivos `.env` al repositorio. Asegúrate de tener el archivo `.gitignore` configurado.

---