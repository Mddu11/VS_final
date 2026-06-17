
set -euo pipefail


NEW_USER="devuser"     
APP_PORT=80                 
SSH_PORT=22                 

echo "=== [1/6] Обновление системы ==="
apt-get update -y
apt-get upgrade -y
apt-get install -y curl wget git ufw

echo "=== [2/6] Создание пользователя '${NEW_USER}' с sudo ==="
if ! id "${NEW_USER}" &>/dev/null; then
    adduser --gecos "" --disabled-password "${NEW_USER}"
    echo "${NEW_USER}:ChangeMe123!" | chpasswd
    usermod -aG sudo "${NEW_USER}"
    echo "Пользователь ${NEW_USER} создан и добавлен в группу sudo"
else
    echo "Пользователь ${NEW_USER} уже существует, пропускаем"
fi

echo "=== [3/6] Настройка SSH-доступа по ключу (опционально) ==="

echo "Шаг пропущен (раскомментируйте блок выше)"

echo "=== [4/6] Настройка UFW (firewall) ==="
ufw default deny incoming
ufw default allow outgoing
ufw allow ${SSH_PORT}/tcp  comment "SSH"
ufw allow ${APP_PORT}/tcp  comment "HTTP приложение"
ufw --force enable
ufw status verbose

echo "=== [5/6] Установка Docker и Docker Compose v2 ==="
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | sh
    usermod -aG docker "${NEW_USER}"
    echo "Docker установлен"
else
    echo "Docker уже установлен: $(docker --version)"
fi

echo "=== [6/6] Проверка версий ==="
docker --version
docker compose version

echo ""
echo "======================================================"
echo "  Настройка завершена!"
echo "  Пользователь : ${NEW_USER}  (пароль: ChangeMe123!)"
echo "  UFW открыты  : SSH (${SSH_PORT}), HTTP (${APP_PORT})"
echo "  Следующий шаг: скопируйте проект на VM и запустите:"
echo "    docker compose up -d"
echo "======================================================"