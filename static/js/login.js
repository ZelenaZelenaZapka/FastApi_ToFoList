document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    const submitBtn = document.getElementById('submitBtn');
    const errorMsg = document.getElementById('errorMessage');

    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // Зупиняємо стандартне перезавантаження сторінки

        // Отримуємо дані
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        // Візуальний стан "Завантаження"
        submitBtn.disabled = true;
        submitBtn.textContent = 'Вхід...';
        errorMsg.textContent = '';

        try {

            // ІМІТАЦІЯ ЗАТРИМКИ (для тесту вигляду)
            await new Promise(r => setTimeout(r, 1000));
            
            // Якщо все ок (для тесту)
            alert(`Дані готові до відправки:\nEmail: ${email}`);
            
            // Тут має бути редірект, наприклад:
            // window.location.href = 'dashboard.html';

        } catch (error) {
            errorMsg.textContent = error.message;
        } finally {
            // Повертаємо кнопку в початковий стан
            submitBtn.disabled = false;
            submitBtn.textContent = 'Увійти';
        }
    });
});




