import { createApp } from 'vue'
import App from './App.vue'
import './index.css'

import HomePage from './components/HomePage.vue'
import WelcomePage from './components/WelcomePage.vue'
import ResultsPage from './components/ResultsPage.vue'
import AboutPage from './components/AboutPage.vue'
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {path:"/", redirect:"/welcome"},
    {path:"/welcome", component:WelcomePage},
    {path:"/home", component:HomePage},
    {path:"/results", component:ResultsPage},
    {path:"/about", component:AboutPage},
]
const route = createRouter({
    history:createWebHistory(),
    routes
})

const app = createApp(App)
app.use(route)

app.mount('#app')
