/**
 * apiService.js
 * ─────────────
 * Centraliza todas las llamadas HTTP al backend FastAPI de VoltMind.
 * Usa el store de usuario para guardar el perfil después de cargarlo.
 */

import { useUserStore } from '@/stores/user';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export const apiService = {
  async generateUserOTP(email, role) {
    const response = await fetch(`${BASE_URL}/api/auth/generate-otp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, role }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Error ${response.status}: no se pudo generar el PIN`);
    }

    return await response.json();
  },

  async validateTabletOTP(otp) {
    const response = await fetch(`${BASE_URL}/api/auth/verify-otp`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ otp }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Error ${response.status}: PIN inválido o expirado`);
    }

    return await response.json();
  },

  /**
   * Obtiene el perfil del usuario desde FastAPI y lo guarda en el store.
   *
   * @param {string} email      - Email institucional obtenido desde Azure MSAL
   * @param {string} [idToken]  - JWT de Azure para validación en el backend
   * @returns {Promise<Object>} - perfil { name, email, role, ficha, centro }
   */
  async getProfileData(email, idToken = null) {
    const response = await fetch(`${BASE_URL}/api/auth/profile`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Enviamos el token para que FastAPI pueda validarlo con Azure (Fase 2)
        ...(idToken && { Authorization: `Bearer ${idToken}` }),
      },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `Error ${response.status}: no se pudo cargar el perfil`
      );
    }

    const profile = await response.json();

    // Guardar en el store para que toda la app lo consuma
    const userStore = useUserStore();
    userStore.setUser({
      name: profile.name,
      email: profile.email,
      role: profile.role,
      ficha: profile.ficha,
      centro: profile.centro,
      documento: profile.documento,
    });

    return profile;
  },

  async loginByDocument(documento) {
    const response = await fetch(`${BASE_URL}/api/auth/login-document`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ documento }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `Error ${response.status}: no se pudo iniciar sesión por documento`
      );
    }

    const profile = await response.json();
    const userStore = useUserStore();
    userStore.setUser({
      name: profile.name,
      email: profile.email,
      role: profile.role,
      ficha: profile.ficha,
      centro: profile.centro,
      documento: profile.documento,
    });

    return profile;
  }

  ,

  async verifyNfcAndAzure(email, nfcUid, idToken) {
    const response = await fetch(`${BASE_URL}/api/auth/verify-nfc`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(idToken && { Authorization: `Bearer ${idToken}` }),
      },
      body: JSON.stringify({ email, nfc_uid: nfcUid }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Error ${response.status}: no se pudo verificar NFC`);
    }

    return await response.json();
  },

  async validateTabletAccess(nfcUid) {
    const response = await fetch(`${BASE_URL}/api/auth/tablet-access`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ nfc_uid: nfcUid }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Error ${response.status}: acceso denegado`);
    }

    return await response.json();
  }
};