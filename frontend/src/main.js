import { createApp } from 'vue'
import { createPinia } from 'pinia' // Importar Pinia
import router from '@/router'      // Importar Router
import App from '@/App.vue'
import './style.css'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

import { faBolt, faUserCheck, faMicrochip, faPowerOff, faIdCard } from '@fortawesome/free-solid-svg-icons'

/* Añadirlos a la librería */
library.add(faBolt, faUserCheck, faMicrochip, faPowerOff, faIdCard)

const app = createApp(App)

app.component('font-awesome-icon', FontAwesomeIcon)
app.use(createPinia()) // Usar Pinia
app.use(router)        // Usar Router

app.mount('#app')