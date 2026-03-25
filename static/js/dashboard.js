document.addEventListener('DOMContentLoaded', () => {
    // --- Елементи DOM ---
    const tasksContainer = document.getElementById('tasksContainer');
    const emptyState = document.getElementById('emptyState');
    const pageTitle = document.getElementById('pageTitle');
    const addTaskBtn = document.getElementById('addTaskBtn');
    const modalOverlay = document.getElementById('modalOverlay');
    const modalClose = document.getElementById('modalClose');
    const modalCancel = document.getElementById('modalCancel');
    const addTaskForm = document.getElementById('addTaskForm');
    const taskTitleInput = document.getElementById('taskTitle');
    const logoutBtn = document.getElementById('logoutBtn');
    const navBtns = document.querySelectorAll('.nav-btn');
    
    // Інформація про користувача
    const userName = document.getElementById('userName');
    const userEmail = document.getElementById('userEmail');
    const userAvatar = document.getElementById('userAvatar');

    // --- Стан додатку ---
    let currentTab = 'tasks'; // 'tasks' або 'history'
    let tasks = [];

    // --- API Конфігурація ---
    const API_BASE = 'http://127.0.0.1:8000'; // Зміни на свій порт
    
    // Отримуємо токен з localStorage
    const getToken = () => localStorage.getItem('access_token');
    const getUser = () => JSON.parse(localStorage.getItem('user') || '{}');

    // --- Перевірка авторизації ---
    function checkAuth() {
        const token = getToken();
        if (!token) {
            window.location.href = '/'; // Редірект на логін
            return false;
        }
        
        const user = getUser();
        userName.textContent = user.username || 'User';
        userEmail.textContent = user.email || '';
        userAvatar.textContent = (user.username || 'U')[0].toUpperCase();
        
        return true;
    }

    // --- Завантаження задач ---
    async function fetchTasks() {
        const token = getToken();
        if (!token) return;

        try {
            const response = await fetch(`${API_BASE}/tasks/`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.status === 401) {
                logout();
                return;
            }

            tasks = await response.json();
            renderTasks();
        } catch (error) {
            console.error('Помилка завантаження:', error);
            tasksContainer.innerHTML = '<p class="error">Помилка завантаження даних</p>';
        }
    }

    // --- Рендеринг задач ---
    function renderTasks() {
        const filteredTasks = currentTab === 'tasks' 
            ? tasks.filter(t => !t.is_done)
            : tasks.filter(t => t.is_done);

        tasksContainer.innerHTML = '';

        if (filteredTasks.length === 0) {
            emptyState.style.display = 'block';
            return;
        }

        emptyState.style.display = 'none';

        filteredTasks.forEach(task => {
            const taskCard = document.createElement('div');
            taskCard.className = 'task-card';
            taskCard.innerHTML = `
                <div class="task-left">
                    <div class="task-checkbox ${task.is_done ? 'checked' : ''}" 
                         data-id="${task.id}" 
                         data-done="${task.is_done}"></div>
                    <span class="task-title ${task.is_done ? 'completed' : ''}">${escapeHtml(task.title)}</span>
                </div>
                <div class="task-actions">
                    <button class="task-btn delete" data-id="${task.id}">🗑️</button>
                </div>
            `;
            tasksContainer.appendChild(taskCard);
        });

        // Додаємо слухачі подій на елементи
        attachTaskListeners();
    }

    // --- Слухачі подій для задач ---
    function attachTaskListeners() {
        // Чекбокси (відмітити як виконане)
        document.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.addEventListener('click', async (e) => {
                const taskId = e.target.dataset.id;
                const isDone = e.target.dataset.done === 'true';
                await toggleTask(taskId, !isDone);
            });
        });

        // Кнопки видалення
        document.querySelectorAll('.task-btn.delete').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const taskId = e.target.dataset.id;
                if (confirm('Ви впевнені, що хочете видалити цю задачу?')) {
                    await deleteTask(taskId);
                }
            });
        });
    }

    // --- API Запити ---
    async function toggleTask(taskId, isDone) {
        const token = getToken();
        try {
            await fetch(`${API_BASE}/tasks/${taskId}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ is_done: isDone })
            });
            fetchTasks();
        } catch (error) {
            console.error('Помилка оновлення:', error);
        }
    }

    async function deleteTask(taskId) {
        const token = getToken();
        try {
            await fetch(`${API_BASE}/tasks/${taskId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            fetchTasks();
        } catch (error) {
            console.error('Помилка видалення:', error);
        }
    }

    async function createTask(title) {
        const token = getToken();
        try {
            await fetch(`${API_BASE}/tasks/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ title: title })
            });
            fetchTasks();
        } catch (error) {
            console.error('Помилка створення:', error);
            alert('Помилка створення задачі');
        }
    }

    // --- Вихід ---
    function logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/';
    }

    // --- Утиліти ---
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // --- Слухачі подій інтерфейсу ---
    
    // Навігація (таби)
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentTab = btn.dataset.tab;
            pageTitle.textContent = currentTab === 'tasks' ? 'Активні завдання' : 'Історія';
            renderTasks();
        });
    });

    // Модальне вікно
    addTaskBtn.addEventListener('click', () => {
        modalOverlay.style.display = 'flex';
        taskTitleInput.focus();
    });

    modalClose.addEventListener('click', () => {
        modalOverlay.style.display = 'none';
        taskTitleInput.value = '';
    });

    modalCancel.addEventListener('click', () => {
        modalOverlay.style.display = 'none';
        taskTitleInput.value = '';
    });

    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            modalOverlay.style.display = 'none';
            taskTitleInput.value = '';
        }
    });

    // Форма додавання задачі
    addTaskForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const title = taskTitleInput.value.trim();
        if (title) {
            createTask(title);
            modalOverlay.style.display = 'none';
            taskTitleInput.value = '';
        }
    });

    // Вихід
    logoutBtn.addEventListener('click', logout);

    // --- Ініціалізація ---
    if (checkAuth()) {
        fetchTasks();
    }
});

