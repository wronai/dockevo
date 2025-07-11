# Demo: Plugin Generator w akcji

## 🎯 **Jak używać Plugin Generator**

### **1. W dockevOS MVP**
```bash
dockevos> generate list
🧩 Available Plugin Templates:

📦 **basic**
   Basic plugin template with simple commands
   Dependencies: None
   Features: commands

📦 **voice-enhanced**
   Enhanced voice control with multiple TTS engines
   Dependencies: pyttsx3, gTTS, pygame
   Features: voice, tts, speech_recognition

📦 **docker-advanced**
   Advanced Docker management with compose support
   Dependencies: docker-compose, pyyaml
   Features: docker, compose, networking

📦 **system-monitor**
   Advanced system monitoring and alerting
   Dependencies: psutil, plotly, schedule
   Features: monitoring, alerts, visualization
```

### **2. Generowanie pluginu voice-enhanced**
```bash
dockevos> generate plugin voice-enhanced advanced-voice "High quality voice control"
✅ Plugin generated successfully!

📁 File: plugins/advanced-voice.py
📦 Template: voice-enhanced
🔧 Features: voice, tts, speech_recognition

📥 Install dependencies: pip install pyttsx3 gtts pygame

🚀 Usage:
  1. Install dependencies (if any)
  2. Reload plugins: reload
  3. Use new commands (check with: help)

🧩 Plugin will be auto-loaded on next restart or reload!
```

### **3. Instalacja zależności i test**
```bash
# Zainstaluj zależności
pip install pyttsx3 gtts pygame

# Przeładuj pluginy
dockevos> reload
🔄 Reloaded 4 plugins

# Test nowych komend
dockevos> voice-engines
🎤 Available Voice Engines:
  • pyttsx3 (current)
  • gtts
  • espeak

dockevos> speak "Hello with enhanced voice" gtts
🔊 Spoke: Hello with enhanced voice (gtts)

dockevos> voice-test
🧪 Testing pyttsx3...
🧪 Testing gtts...
🧪 Testing espeak...
🧪 Voice Engine Test Results:
  pyttsx3: ✅ OK
  gtts: ✅ OK  
  espeak: ✅ OK
```

## 🚀 **Przykłady generowanych pluginów**

### **Voice Enhanced Plugin - funkcje:**

```bash
# Wybór silnika TTS
dockevos> voice-config engine gtts
✅ Set voice.engine = gtts

# Konfiguracja głosu
dockevos> voice-config rate 120
✅ Set voice.rate = 120

dockevos> voice-config language pl
✅ Set voice.language = pl

# Test wszystkich silników
dockevos> voice-test
🧪 Voice Engine Test Results:
  pyttsx3: ✅ OK
  gtts: ✅ OK
  espeak: ✅ OK

# Wyczyść cache
dockevos> voice-clear-cache
🧹 Cleared 15 cached voice files

# Wysokiej jakości synteza
dockevos> speak "Witaj w dockevOS" gtts
🔊 [High quality Google TTS with caching]
```

### **Docker Advanced Plugin - funkcje:**

```bash
# Szczegółowe info o kontenerach
dockevos> docker-ps-detailed
🐳 Docker Containers (Detailed):
NAME               IMAGE              STATUS      PORTS                   CPU/MEM
nginx-1            nginx:alpine       running     80:8080                 2.1%/45MB
redis-cache        redis:7-alpine     running     none                    0.5%/12MB

# Inspekcja kontenera
dockevos> docker-inspect nginx-1
🔍 Container Inspection: nginx-1
==================================================
ID: abc123456
Image: nginx:alpine
Status: running
Created: 2025-01-15T10:30:15

Networks:
  bridge: 172.17.0.2

Port Mappings:
  80/tcp -> 8080

# Zarządzanie sieciami
dockevos> docker-networks
🌐 Docker Networks:
NAME               DRIVER    SCOPE     SUBNET
bridge             bridge    local     172.17.0.0/16
host               host      local     N/A
none               null      local     N/A

# Docker Compose
dockevos> compose up
✅ Compose up successful:
Creating network "app_default" with the default driver
Creating app_web_1 ... done
Creating app_db_1  ... done
```

### **System Monitor Plugin - funkcje:**

```bash
# Status systemu z grafiką
dockevos> monitor
📊 System Status:
┌─────────────────────────────────────────┐
│ CPU Usage:      15.3% │ [██░░░░░░░░]
│ Memory:         67.8% │ [██████▒░░░]
│ Disk Usage:     45.2% │ [████▒░░