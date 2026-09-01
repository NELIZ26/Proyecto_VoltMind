<template>
  <nav class="gestor-sidebar">
    <div class="sidebar-header">
      <div class="logo-duo">
        <img src="@/assets/LogoSena.png" alt="SENA" class="logo-sena" />
        <img src="@/assets/VoltMindAccess1.svg" alt="VoltMind" class="logo-volt" />
      </div>
      <div class="brand-text">
        <h1 class="brand-title"><span class="text-volt">Volt</span><span class="text-mind">Mind</span></h1>
        <p class="brand-subtitle">GESTOR FICHAS</p>
      </div>
    </div>

    <ul class="sidebar-menu">
      <li>
        <router-link to="/gestor-fichas" class="menu-link" exact-active-class="active-link">
          <div class="icon-box">
            <font-awesome-icon icon="fa-solid fa-layer-group" fixed-width />
          </div>
          <span class="menu-text">Creación y Catálogo</span>
        </router-link>
      </li>
      <li>
        <router-link to="/gestor-fichas/listado" class="menu-link" active-class="active-link">
          <div class="icon-box">
            <font-awesome-icon icon="fa-solid fa-list-check" fixed-width />
          </div>
          <span class="menu-text">Fichas Creadas</span>
        </router-link>
      </li>
      
      <li class="logout-item">
        <router-link to="/login" class="menu-link logout-link">
          <div class="icon-box logout-icon-box">
            <font-awesome-icon icon="fa-solid fa-right-from-bracket" fixed-width />
          </div>
          <span class="menu-text">Salir</span>
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.gestor-sidebar {
  background: var(--fondo-tarjetas);
  border: 1px solid var(--borde);
  border-radius: 0 16px 16px 0;
  box-shadow: 0 4px 12px var(--sombra-suave);
  width: 280px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  display: flex;
  flex-direction: column;
  padding: 24px 0;
  z-index: 100;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--borde);
}

.logo-duo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}
.logo-sena {
  height: 55px;
  width: auto;
}
.logo-volt {
  height: 60px;
  width: auto;
}

.brand-text {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-title {
  font-size: 1.8rem;
  font-weight: 800;
  margin: 0;
  line-height: 1;
}

.text-volt {
  color: var(--sena-azul-oscuro);
}

.text-mind {
  color: var(--sena-verde);
}

.brand-subtitle {
  font-size: 0.8rem;
  color: var(--texto-secundario);
  letter-spacing: 1.5px;
  margin: 0;
  text-transform: uppercase;
}

.sidebar-menu {
  list-style: none;
  padding: 0 16px;
  margin: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.menu-link {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 12px;
  color: var(--texto-secundario);
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s ease;
}

.icon-box {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--fondo-app);
  margin-right: 16px;
  color: var(--texto-secundario);
  transition: all 0.2s ease;
}

.menu-link:hover {
  background: var(--fondo-app);
  color: var(--texto-principal);
}

.menu-link:hover .icon-box {
  background-color: var(--sena-verde, #39A900);
  color: #fff;
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.25);
}

.active-link {
  background-color: rgba(57, 169, 0, 0.05);
  border-color: rgba(57, 169, 0, 0.2);
  color: var(--texto-principal);
}

.active-link .icon-box {
  background-color: var(--sena-verde, #39A900);
  color: #fff;
  box-shadow: 0 4px 12px rgba(57, 169, 0, 0.25);
}

.logout-item {
  margin-top: auto;
  border-top: 1px solid var(--borde);
  padding-top: 16px;
}

.logout-link {
  color: var(--texto-secundario);
}

.logout-link:hover {
  background: rgba(220, 53, 69, 0.05);
  color: #dc3545;
}

.logout-icon-box {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.logout-link:hover .logout-icon-box {
  background: #dc3545;
  color: white;
}
</style>
