# 🦞 Aplicación OpenClaw Services HTML

## 🎯 ¿Qué es?

Una aplicación web interactiva moderna que funciona como **panel de control** para acceder rápidamente a todos tus servicios OpenClaw.

**Características:**
- ✅ Agregar/eliminar servicios sobre la marcha
- ✅ Verificar estado de servicios (online/offline)
- ✅ Copiar token con un clic
- ✅ Exportar/importar configuración
- ✅ Almacenamiento local (funciona sin internet)
- ✅ Diseño moderno y responsive
- ✅ Atajos de teclado

---

## 📂 Archivo

**Ubicación:** `~/openclaw-services.html`

---

## 🚀 Cómo Usar

### Opción 1: Abrir en Navegador (Más Rápido)

```bash
# macOS
open ~/openclaw-services.html

# Linux
xdg-open ~/openclaw-services.html

# O simplemente arrastra el archivo a tu navegador
```

### Opción 2: Guardarlo como Acceso Directo

**macOS - Crear Acceso Directo en Dock:**

1. Abre el archivo HTML en Safari
2. Presiona Cmd + Shift + D (añadir a inicio)
3. Ahora está en tu Dock

**macOS - Crear Alias:**

```bash
# Crear acceso directo en el Desktop
ln -s ~/openclaw-services.html ~/Desktop/OpenClaw\ Services.html

# Luego haz doble clic en el Desktop
```

---

## 🎮 Características Principales

### 🔍 Verificar Estado de Servicios

Haz clic en el botón **"🔍 Verificar Todos"** para comprobar qué servicios están activos:

- ✅ **En línea** (verde) - Servicio funcionando
- ❌ **Desconectado** (rojo) - Servicio caído
- 🔄 **Verificando** (amarillo) - Comprobando estado

### ➕ Agregar Nuevo Servicio

1. Haz clic en **"➕ Agregar"** o en el área punteada
2. Rellena:
   - **Nombre:** ej. "Mi API Custom"
   - **URL:** ej. "http://localhost:5000"
   - **Descripción:** ej. "API personalizada"
   - **Icono:** ej. "📡"
3. Haz clic en **"💾 Guardar"**

Ejemplo:
```
Nombre: Grafana
URL: http://localhost:3000
Descripción: Monitoreo en tiempo real
Icono: 📊
```

### 🗑️ Eliminar Servicio

Haz clic en la **"×"** en la esquina superior derecha del servicio.

### 🔐 Copiar Token

Haz clic en **"📋 Copiar Token"** para copiar el token de autenticación al portapapeles.

---

## 💾 Exportar/Importar

### Exportar Servicios

Haz clic en **"📥 Exportar"** en la parte inferior para descargar un archivo JSON con tus servicios.

**Uso:** Guardar configuración como backup o compartir.

### Importar Servicios

Haz clic en **"📤 Importar"** y selecciona un archivo JSON previamente exportado.

**Uso:** Restaurar configuración o importar desde otra máquina.

---

## ⌨️ Atajos de Teclado

| Atajo | Acción |
|-------|--------|
| `ESC` | Cerrar modal (si está abierto) |
| Click en servicio | Abrir en nueva pestaña |
| Click en "×" | Eliminar servicio |

---

## 📦 Servicios Predefinidos

La app viene con estos servicios ya configurados:

1. **Open WebUI** (💬)
   - URL: http://localhost:3000
   - Interfaz de chat

2. **OpenClaw Control UI** (🦞)
   - URL: http://localhost:18789
   - Panel de control

3. **Ollama API** (🤖)
   - URL: http://localhost:11434
   - API de IA

4. **WebChat** (💭)
   - URL: http://localhost:18789/web
   - Chat en OpenClaw

Puedes modificar o eliminar cualquiera.

---

## 🎨 Personalización

### Cambiar Tema

Para crear un tema oscuro, puedes usar una extensión de navegador o modificar el CSS:

1. Abre el archivo HTML con un editor de texto
2. Busca la sección `<style>`
3. Cambia los colores (ej. `#667eea` por otro color)

### Agregar Tus Propios Servicios

La app guarda todos los cambios automáticamente en el **localStorage del navegador**.

Ejemplo de servicios útiles para agregar:

```
Nombre: Prometheus
URL: http://localhost:9090
Icono: 📈

Nombre: Jenkins
URL: http://localhost:8080
Icono: ⚙️

Nombre: Portainer
URL: http://localhost:9000
Icono: 🐳
```

---

## 🔒 Seguridad

- **Token visible:** Se muestra en la interfaz para copiar
- **Almacenamiento:** Guardado en localStorage (local, no enviado a servidores)
- **Cookies:** No se usan cookies
- **Datos:** Todo se guarda localmente en tu navegador

---

## 🛠️ Troubleshooting

### "No puedo copiar el token"

**Solución:** 
- Permite acceso al portapapeles en tu navegador
- O copia manualmente desde el campo

### "Los servicios no se guardan"

**Solución:**
- Verifica que el navegador permite localStorage
- Intenta con otro navegador
- Usa Exportar/Importar como backup

### "¿Dónde se guardan los servicios?"

Los servicios se guardan en:
- **localStorage:** `window.localStorage.getItem('openclaw-services')`
- **Ubicación:** Dentro de tu navegador (no en archivos)

Para ver la configuración:
```javascript
// En la consola del navegador (F12)
console.log(JSON.parse(localStorage.getItem('openclaw-services')))
```

---

## 📱 Uso en Móvil

La app es **responsive** y funciona en móviles:

1. Abre en navegador móvil: `file:///Users/davidnows/openclaw-services.html`
2. O copia el archivo HTML a tu teléfono
3. Todas las funciones funcionan igual

---

## 🔄 Sincronizar Entre Máquinas

### Opción 1: Exportar/Importar

1. En macOS: Haz clic en **"📥 Exportar"**
2. Sube el JSON a Dropbox/Google Drive/etc.
3. En otra máquina: Descarga y haz clic en **"📤 Importar"**

### Opción 2: Copiar Archivo

```bash
# En macOS
scp ~/openclaw-services.html usuario@otra-maquina:~/

# Luego abre en esa máquina
```

---

## 💡 Tips & Tricks

### Crear un Bookmark (Marcador)

Guarda en tus marcadores:
```
Nombre: OpenClaw Services
URL: file:///Users/davidnows/openclaw-services.html
```

Así puedes acceder rápidamente sin memorizar la ruta.

### Abrir Siempre en el Mismo Navegador

macOS:
```bash
# Crear AppleScript para Safari
open -a Safari ~/openclaw-services.html
```

### Crear Carpeta de Aplicaciones

```bash
# Crear carpeta
mkdir -p ~/Applications/OpenClaw

# Mover archivo
cp ~/openclaw-services.html ~/Applications/OpenClaw/Services.html

# Crear alias
ln -s ~/Applications/OpenClaw/Services.html ~/Desktop/OpenClaw\ Services
```

---

## 🎯 Casos de Uso

### 1. Dashboard Personal

Guarda todos tus servicios locales en un solo lugar.

### 2. Monitoreo Rápido

Verifica el estado de servicios cada 30 segundos automáticamente.

### 3. Compartir con el Equipo

Exporta la configuración y comparte el JSON con tu equipo.

### 4. Desarrollo Multi-Proyectos

Crea diferentes configuraciones para diferentes proyectos.

---

## 📖 Referencia Rápida

```
🦞 OpenClaw Services

├─ 🚀 Servicios Principales
│  ├─ 🔍 Verificar Todos
│  ├─ ➕ Agregar Servicio
│  └─ [Tarjetas de Servicios]
│     ├─ Estado (✅/❌/🔄)
│     ├─ Click para abrir
│     └─ × para eliminar
│
├─ 🔐 Autenticación
│  ├─ Token (copiable)
│  ├─ ℹ️ Info del Sistema
│  └─ ⌨️ Comandos Útiles
│
└─ Pie
   ├─ 📥 Exportar
   └─ 📤 Importar
```

---

## 🚀 Próximos Pasos

1. Abre el archivo HTML
2. Verifica que los servicios estén disponibles
3. Añade tus propios servicios según necesites
4. Guarda en marcadores para acceso rápido
5. ¡Usa el panel en tu día a día!

---

**Última actualización:** 2026-03-09
**Versión:** 1.0
**Compatibilidad:** Todos los navegadores modernos (Chrome, Safari, Firefox, Edge)
