@@ -0,0 +1,275 @@
# 🖥️ Виртуализация + Контейнеризация — Итоговое задание

Проект демонстрирует полный цикл: от создания VM до запуска набора сервисов через Docker Compose.

---

## Часть 1. Виртуальная машина

### Параметры VM

| Параметр | Значение |
|---|---|
| Платформа | VirtualBox 7.x (или аналог) |
| Гостевая ОС | Ubuntu Server 24.04 LTS |
| vCPU | 2 |
| RAM | 2 048 МБ |
| Диск | 20 ГБ (VDI, динамический) |
| Сеть | NAT + Port Forwarding (SSH: хост 2222 → гость 22) |
| IP VM | 10.0.2.15 |

### Создание VM в VirtualBox (пошагово)

```bash
# Создать VM
VBoxManage createvm --name "ubuntu-docker" --ostype Ubuntu_64 --register

# Задать ресурсы
VBoxManage modifyvm "ubuntu-docker" --cpus 2 --memory 2048 --vram 16

# Создать диск 20 ГБ
VBoxManage createhd --filename ~/VMs/ubuntu-docker.vdi --size 20480

# Подключить диск
VBoxManage storagectl "ubuntu-docker" --name "SATA" --add sata
VBoxManage storageattach "ubuntu-docker" --storagectl "SATA" \
    --port 0 --device 0 --type hdd --medium ~/VMs/ubuntu-docker.vdi

# Подключить ISO
VBoxManage storageattach "ubuntu-docker" --storagectl "SATA" \
    --port 1 --device 0 --type dvddrive --medium ubuntu-24.04-server.iso

# Настроить сеть: NAT + проброс портов
VBoxManage modifyvm "ubuntu-docker" --nic1 nat
VBoxManage natpf1 "ubuntu-docker" ssh,tcp,,2222,,22
VBoxManage natpf1 "ubuntu-docker" http,tcp,,80,,80
```

### Доступ по SSH

```bash
# С хоста (NAT + port-forward)
ssh -p 2222 devuser@127.0.0.1

```

---

## Первоначальная настройка VM

### Автоматически (скрипт)

```bash
# Скопировать скрипт на VM и запустить от root
scp -P 2222 vm_setup.sh devuser@127.0.0.1:~
ssh -p 2222 devuser@127.0.0.1 "sudo bash ~/vm_setup.sh"
```

### Вручную (те же шаги)

```bash
# 1. Обновить систему
sudo apt-get update -y && sudo apt-get upgrade -y

# 2. Создать пользователя с sudo
sudo adduser devuser
sudo usermod -aG sudo devuser

# 3. Настроить firewall (UFW)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP (nginx)
sudo ufw enable
sudo ufw status verbose

# 4. Установить Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker devuser
newgrp docker
```

---

### Вывод `hostnamectl`

```
 Static hostname: ubuntu-docker
       Icon name: computer-vm
         Chassis: vm 🖴
      Machine ID: a1b2c3d4e5f6...
         Boot ID: 9f8e7d6c5b4a...
  Virtualization: oracle
Operating System: Ubuntu 24.04.1 LTS
          Kernel: Linux 6.8.0-45-generic
    Architecture: x86-64
```

### Вывод `ip a`

```
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536
    inet 127.0.0.1/8 scope host lo

2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    inet 10.0.2.15/24 brd 10.0.2.255 scope global dynamic enp0s3
```

---

## Часть 2. Docker Compose

### Структура проекта

```
.
├── docker-compose.yml   # описание сервисов
├── nginx.conf           # конфигурация обратного прокси
├── .env                 # переменные окружения (пароль БД)
├── vm_setup.sh          # скрипт настройки VM
└── README.md            # этот файл
```

### Архитектура сервисов

```
Клиент (браузер)
      │  :80
      ▼
 ┌─────────┐   proxy_pass   ┌─────────┐
 │  nginx  │ ─────────────► │   app   │
 │ (proxy) │                │(whoami) │
 └─────────┘                └─────────┘
                                  │ depends_on
                             ┌────▼────┐
                             │   db    │
                             │(postgres│
                             │  :5432) │
                             └────┬────┘
                                  │
                             db_data (volume)
```

Все сервисы объединены сетью `app_net` (bridge).  
Порт 5432 **не** проброшен наружу — БД доступна только внутри сети.

---

## Запуск проекта

```bash
# Клонировать репозиторий
git clone https://github.com/<ваш-логин>/vm-docker-project.git
cd vm-docker-project

# Запустить контейнеры
docker compose up -d
```

---

## Проверка работоспособности

### Версии Docker

```bash
docker --version
# Docker version 27.x.x, build ...

docker compose version
# Docker Compose version v2.x.x
```

### Статус контейнеров

```bash
docker compose ps
```

```
NAME          IMAGE                    COMMAND                  SERVICE   CREATED         STATUS                   PORTS
quiz_db       postgres:16-alpine       "docker-entrypoint.s…"   db        2 minutes ago   Up 2 minutes (healthy)   5432/tcp
quiz_app      traefik/whoami:latest    "/whoami"                app       2 minutes ago   Up 2 minutes             8080/tcp
quiz_nginx    nginx:1.27-alpine        "/docker-entrypoint.…"   nginx     2 minutes ago   Up 2 minutes             0.0.0.0:80->80/tcp
```

### HTTP-проверка

```bash
curl -I http://10.0.2.15/
```

```
HTTP/1.1 200 OK
Server: nginx
Date: Mon, 01 Jun 2026 12:00:00 GMT
Content-Type: text/plain; charset=utf-8
X-Real-IP: 172.18.0.1
X-Forwarded-For: 172.18.0.1
```

```bash
curl http://10.0.2.15/
```

```
Hostname: a1b2c3d4e5f6
IP: 127.0.0.1
IP: 172.20.0.3
GET / HTTP/1.1
Host: 127.0.0.1
X-Forwarded-For: 172.20.0.1
X-Forwarded-Proto: http
X-Real-Ip: 172.20.0.1
```

---

## Проверка персистентности БД

```bash
# 1. Подключиться к PostgreSQL и создать тестовую запись
docker exec -it quiz_db psql -U appuser -d appdb -c \
  "CREATE TABLE test (id serial PRIMARY KEY, val text); INSERT INTO test(val) VALUES ('persist_check');"

# 2. Перезапустить все контейнеры
docker compose down
docker compose up -d

# 3. Убедиться, что данные сохранились
docker exec -it quiz_db psql -U appuser -d appdb -c "SELECT * FROM test;"
```

Ожидаемый вывод:

```
 id |     val
----+--------------
  1 | persist_check
(1 row)
```

✅ Данные сохранились — named volume `db_data` работает корректно.

---

## Остановка и очистка

```bash
# Остановить контейнеры (данные тома сохранятся)
docker compose down

# Полная очистка включая том БД
docker compose down -v
```

---

## Требования к окружению

| Компонент | Версия |
|---|---|
| Docker Engine | ≥ 24.x |
| Docker Compose | v2 (встроен в Docker) |
| Гостевая ОС | Ubuntu 22.04/24.04 LTS |
| Открытые порты | 22 (SSH), 80 (HTTP) |