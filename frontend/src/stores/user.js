// src/stores/user.js
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    name: '',
    role: '', // 'instructor' o 'aprendiz'
    ficha: null,
    token: null, // Token de Azure
    isAuthenticated: false
  }),
  actions: {
    setUser(userData) {
      this.name = userData.name
      this.role = userData.role
      this.isAuthenticated = true
    },
    logout() {
      this.$reset()
    }
  }
})