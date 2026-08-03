# 🚀 Instalación de OpenClaw en Oracle Free Tier

## 📋 Requisitos Previos

**Oracle Free Tier Instance:**
- OS: Ubuntu 22.04 LTS (o superior)
- CPU: 2-4 vCPUs (recomendado)
- RAM: 4+ GB
- Storage: 30+ GB disponibles
- Firewall: Abrir puertos 22 (SSH), 3000, 18789, 11434

## 🔧 Paso 1: Conectar a tu Servidor Oracle

```bash
# Conectar vía SSH (reemplaza con tu IP)
ssh -i ~/tu-key.pem ubuntu@your.oracle.ip.address

# Actualizar el sistema
sudo apt-get update && sudo apt-get upgrade -y
```

## 📥 Paso 2: Descargar el Script Maestro

```bash
# En tu máquina local (macOS):
scp ~/PROMPT_MAESTRO_UNIVERSAL.sh ubuntu@your.oracle.ip:/tmp/

# O en el servidor Oracle:
curl -O https://raw.githubusercontent.com/openclaw/openclaw/main/PROMPT_MAESTRO_UNIVERSAL.sh
# O copiar manualmente el contenido
```

## ⚙️ Paso 3: Ejecutar la Instalación

```bash
# Conectar a tu servidor Oracle
ssh -i ~/tu-key.pem ubuntu@your.oracle.ip

# Dar permisos de ejecución
chmod +x ~/PROMPT_MAESTRO_UNIVERSAL.sh

# Ejecutar (esto tarda 30-45 minutos)
bash ~/PROMPT_MAESTRO_UNIVERSAL.sh
```

La instalación hará todo automáticamente:
- ✅ Instalar Docker, Node.js, Ollama
- ✅ Descargar modelos IA
- ✅ Compilar OpenClaw
- ✅ Configurar Tailscale
- ✅ Crear scripts de inicio/parada

## 🔌 Paso 4: Configurar Firewall Oracle Cloud

En la consola de Oracle Cloud:

1. Ve a **Networking → Virtual Cloud Networks**
2. Selecciona tu subnet
3. Haz clic en tu **Security List**
4. Agrega **Ingress Rules**:

```
Protocol: TCP
Source: 0.0.0.0/0
Dest Port: 3000, 18789, 11434
```

## 🚀 Paso 5: Iniciar el Stack

```bash
# En el servidor Oracle
bash ~/iniciar-stack.sh

# O manualmente:
cd ~/openclaw
node dist/index.js gateway --port 18789 --allow-unconfigured &
```

## 🌐 Paso 6: Acceder Remotamente

### Opción A: IP Pública Directa (NO RECOMENDADO sin VPN)
```bash
http://your.oracle.ip:3000      # Open WebUI
http://your.oracle.ip:18789     # OpenClaw
```

### Opción B: Tailscale (RECOMENDADO - Seguro)

```bash
# En el servidor Oracle
tailscale up

# Sigue el link de autenticación
# Luego habilita Funnel para acceso público

tailscale funnel 18789    # OpenClaw
tailscale funnel 3000     # Open WebUI

# Obtendrás URL como:
https://tu-servidor.ts.net
```

### Opción C: SSH Tunnel (Para desarrollo)
```bash
# Desde tu máquina local
ssh -i ~/tu-key.pem -L 3000:localhost:3000 -L 18789:localhost:18789 ubuntu@your.oracle.ip

# Luego accede a:
http://localhost:3000      # Open WebUI
http://localhost:18789     # OpenClaw
```

## 📊 Monitoreo

```bash
# Ver logs de OpenClaw (en tiempo real)
tail -f /tmp/openclaw.log

# Ver logs de Ollama
tail -f /tmp/ollama.log

# Ver estado de servicios
docker ps
ps aux | grep openclaw
ps aux | grep ollama

# Monitoreo de recursos
watch -n 1 'free -h && echo "---" && df -h'
```

## 🛠️ Troubleshooting

### OpenClaw no inicia
```bash
cd ~/openclaw
node dist/index.js doctor --fix
```

### Ollama no descarga modelos
```bash
# Verificar que el directorio tiene espacio
du -sh ~/.ollama
df -h

# Descargar manualmente
ollama pull mistral-small
```

### Docker sin permisos
```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
newgrp docker

# O usar sudo
sudo docker ps
```

### Memoria insuficiente
```bash
# Usar modelo más pequeño
ollama pull tinyllama  # Solo 4 GB

# O aumentar swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 🔐 Seguridad

**IMPORTANTE: Nunca expongas credenciales públicamente**

```bash
# Tu Gateway Token (guardado en ~/.openclaw/openclaw.json):
GATEWAY_TOKEN=aca30e113a9d745ec3458609c7a06b2261f49c0b91d0759428d4717c0cd7ff9c

# Úsalo para:
curl -H "Authorization: Bearer $GATEWAY_TOKEN" http://tu-servidor:18789
```

## 📈 Optimización para Oracle Free

### Limitar recursos de Ollama
```bash
# Editar ~/.ollama/config.json
{
  "num_parallel": 1,
  "max_loaded_models": 1
}
```

### Usar modelos pequeños
```bash
# Instalar versiones cuantizadas
ollama pull mistral-small:latest    # 14 GB
ollama pull neural-chat:latest      # 4 GB
ollama pull tinyllama:latest        # 2 GB
```

### Autoarranque en caso de reinicio
```bash
# Crear systemd service para OpenClaw
sudo tee /etc/systemd/system/openclaw.service << EOF
[Unit]
Description=OpenClaw AI Gateway
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/openclaw
ExecStart=/usr/bin/node /home/ubuntu/openclaw/dist/index.js gateway --port 18789 --allow-unconfigured
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable openclaw
sudo systemctl start openclaw
```

## 📞 Soporte

- **Documentación OpenClaw:** https://docs.openclaw.ai
- **Issues:** https://github.com/openclaw/openclaw/issues
- **Discord:** https://discord.gg/clawd

## 🎯 Próximos Pasos

1. **Instala el script maestro** en tu servidor Oracle
2. **Ejecuta la instalación automática**
3. **Configura Tailscale** para acceso remoto seguro
4. **Prueba los servicios** desde tu máquina local

¡Tu stack de IA en la nube Oracle está listo! 🚀
