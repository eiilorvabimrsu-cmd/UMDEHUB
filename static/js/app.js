const navToggle = document.querySelector('[data-nav-toggle]');
const navMenu = document.querySelector('[data-nav-menu]');

if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
        navMenu.classList.toggle('is-open');
    });
}

const timerElement = document.getElementById('quiz-timer');
if (timerElement && window.quizDurationSeconds) {
    let remainingSeconds = Number(window.quizDurationSeconds);
    const form = document.getElementById('quiz-form');

    const renderTimer = () => {
        const minutes = Math.floor(remainingSeconds / 60).toString().padStart(2, '0');
        const seconds = (remainingSeconds % 60).toString().padStart(2, '0');
        timerElement.textContent = `${minutes}:${seconds}`;
    };

    renderTimer();
    const interval = setInterval(() => {
        remainingSeconds -= 1;
        renderTimer();
        if (remainingSeconds <= 0) {
            clearInterval(interval);
            if (form) {
                form.submit();
            }
        }
    }, 1000);
}
