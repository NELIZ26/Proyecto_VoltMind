/**
 * authService.js
 * ──────────────
 * Maneja toda la autenticación con Microsoft Azure AD usando MSAL.
 * Instalación previa requerida:
 *   npm install @azure/msal-browser
 */

import { PublicClientApplication, InteractionRequiredAuthError } from '@azure/msal-browser';

// ── Configuración MSAL ────────────────────────────────────────────────────────
const msalConfig = {
  auth: {
    clientId: 'd5c704a2-4bd3-4675-9822-7bdf35edfec6',
    authority: 'https://login.microsoftonline.com/1e2fcfd3-cad9-457b-b7f2-d53e52ca7047',
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
};

const loginRequest = {
  scopes: ['openid', 'profile', 'email', 'User.Read'],
};

// ── Singleton con inicialización lazy ─────────────────────────────────────────
// NO usamos await en top-level: eso causa interaction_in_progress en hot-reload.
// En su lugar, inicializamos una sola vez la primera vez que se llama loginWithAzure.
let _msalInstance = null;

const getMsal = async () => {
  if (_msalInstance) return _msalInstance;

  _msalInstance = new PublicClientApplication(msalConfig);
  await _msalInstance.initialize();

  return _msalInstance;
};

// ── API pública ───────────────────────────────────────────────────────────────

/**
 * Inicia el login redirigiendo al portal de Microsoft.
 * Al volver, handleRedirectPromise() en getMsal() captura el resultado.
 * Usamos redirect en lugar de popup para evitar bloqueos del navegador.
 */
export const loginWithAzure = async () => {
  const msal = await getMsal();
  await msal.loginRedirect(loginRequest);
  // La ejecución se detiene aquí — el navegador redirige a Microsoft.
  // El resultado se procesa en getRedirectResult() al volver.
};

/**
 * Procesa el resultado de vuelta de Microsoft y devuelve el objeto completo del usuario.
 * Llama a esto en onMounted() del LoginView para capturar el redirect.
 * @returns {Promise<{email, name, idToken, localAccountId}|null>}
 */
export const getRedirectResult = async () => {
  const msal = await getMsal();
  const response = await msal.handleRedirectPromise();
  const account = response?.account || msal.getAllAccounts()[0];

  if (account) {
    return {
      email: account.username,
      name: account.name,
      idToken: response?.idToken || null,
      localAccountId: account.localAccountId,
    };
  }
  return null;
};

/**
 * Cierra la sesión redirigiendo a Microsoft.
 */
export const logoutAzure = async () => {
  const msal = await getMsal();
  await msal.logoutRedirect();
};

/**
 * Devuelve el email del usuario actualmente autenticado,
 * o null si no hay sesión activa.
 * @returns {Promise<string|null>}
 */
export const getCurrentEmail = async () => {
  const msal = await getMsal();
  const accounts = msal.getAllAccounts();
  return accounts.length > 0 ? accounts[0].username : null;
};