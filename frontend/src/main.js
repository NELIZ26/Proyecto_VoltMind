// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from '@/router' // Mantiene tu importación limpia con alias
import App from '@/App.vue'
import './style.css'

// ── 1. CONFIGURACIÓN DE VUE-TOASTIFICATION ──
import Toast from "vue-toastification"
import "vue-toastification/dist/index.css"

const toastOptions = {
  transition: "Vue-Toastification__bounce",
  maxToasts: 3,
  newestOnTop: true,
  position: "top-right",
  timeout: 3000,
  closeOnClick: true,
  pauseOnFocusLoss: false,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: "button",
  icon: true,
  rtl: false
}

// ── 2. ARQUITECTURA GLOBAL DE FONTAWESOME ──
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

// Recuperamos la totalidad de iconos del ecosistema VoltMind
import { 
  faUser, 
  faPowerOff, 
  faMicrochip, 
  faBolt, 
  faUserCheck, 
  faRss, 
  faIdCard, 
  faIdBadge, 
  faQrcode, 
  faFingerprint, 
  faCompactDisc, 
  faCamera,
  faAddressCard,
  faRightToBracket,
  faArrowRightToBracket,
  faRightFromBracket,
  faShieldHalved,
  faCircleNotch,
  faLock,
  faWifi,
  faClock,
  faCircleCheck,
  faGraduationCap,
  faCalendarCheck,
  faCircleStop,
  faTriangleExclamation,
  faRefresh,
  // --- NUEVOS ICONOS INTEGRADOS PARA EL DASHBOARD Y MODALES ---
  faPlug,
  faUsers,
  faCalendarDays,
  faCircleXmark
} from '@fortawesome/free-solid-svg-icons'

library.add(
  faUser, 
  faPowerOff, 
  faMicrochip, 
  faBolt, 
  faUserCheck, 
  faRss, 
  faIdCard, 
  faIdBadge, 
  faQrcode, 
  faFingerprint, 
  faCompactDisc, 
  faCamera,
  faAddressCard,
  faRightToBracket,
  faArrowRightToBracket,
  faRightFromBracket,
  faShieldHalved,
  faCircleNotch,
  faLock,
  faWifi,
  faClock,
  faCircleCheck,
  faGraduationCap,
  faCalendarCheck,
  faCircleStop,
  faTriangleExclamation,
  faRefresh,
  // --- INYECCIÓN EN LA LIBRERÍA DE VOLTMIND ---
  faPlug,
  faUsers,
  faCalendarDays,
  faCircleXmark
)

// ── 3. INICIALIZACIÓN DE LA INSTANCIA DE VUE ──
const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Toast, toastOptions)

// Registro global del componente de iconos
app.component('font-awesome-icon', FontAwesomeIcon)

app.mount('#app')