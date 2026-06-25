import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import { VueQueryPlugin } from '@tanstack/vue-query'
import App from './App.vue'
import BrowsePage from './pages/BrowsePage.vue'
import ChassisPage from './pages/ChassisPage.vue'
import GearBrowsePage from './pages/GearBrowsePage.vue'
import GearPage from './pages/GearPage.vue'
import SearchPage from './pages/SearchPage.vue'
import StarSystemBrowsePage from './pages/StarSystemBrowsePage.vue'
import StarSystemPage from './pages/StarSystemPage.vue'
import RtoPilotsPage from './pages/RtoPilotsPage.vue'
import './style.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/mechs' },
    { path: '/mechs', component: BrowsePage, props: { mode: 'mech' } },
    { path: '/vehicles', component: BrowsePage, props: { mode: 'vehicle' } },
    { path: '/vtols', component: BrowsePage, props: { mode: 'vtol' } },
    { path: '/battle-armor', component: BrowsePage, props: { mode: 'battle_armor' } },
    { path: '/mechs/:prefabBase', component: ChassisPage },
    { path: '/vehicles/:prefabBase', component: ChassisPage },
    { path: '/vtols/:prefabBase', component: ChassisPage },
    { path: '/battle-armor/:prefabBase', component: ChassisPage },
    { path: '/equipment', component: GearBrowsePage, props: { mode: 'equipment' } },
    { path: '/equipment/:gearId', component: GearPage },
    { path: '/weapons', component: GearBrowsePage, props: { mode: 'weapon' } },
    { path: '/weapons/:gearId', component: GearPage },
    { path: '/quirks', component: GearBrowsePage, props: { mode: 'quirk' } },
    { path: '/quirks/:gearId', component: GearPage },
    { path: '/search', component: SearchPage },
    { path: '/star-systems', component: StarSystemBrowsePage },
    { path: '/star-systems/:systemId', component: StarSystemPage },
    { path: '/rto-pilots', component: RtoPilotsPage },
  ]
})

const app = createApp(App)
app.use(router)
app.use(createPinia())
app.use(VueQueryPlugin)
app.mount('#app')
