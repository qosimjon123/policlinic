document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');

    cards.forEach(card => {
        card.addEventListener('click', () => {
            if (card.classList.contains('enlarged')) {
                card.classList.remove('enlarged');
            } else {
                // Убираем класс 'enlarged' у всех других карточек
                cards.forEach(c => c.classList.remove('enlarged'));
                card.classList.add('enlarged');
            }
        });
    });
    document.querySelector('.clickbind').addEventListener('click', () => {

    window.print();



});
    const deleteButtons = document.querySelectorAll('.delete-btn');

    const modalBody = document.querySelector('.msg-for_del');
    const deleteForm = document.querySelector('.form-for-del');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const patientId = e.target.getAttribute('patientId');
            const patientName = e.target.closest('tr').querySelector('.patient-name').textContent;

            // Обновите сообщение в модальном окне
            modalBody.textContent = patientName;

            // Обновите URL формы удаления
            deleteForm.setAttribute('action', `/delete_patient/${patientId}`);
        });
    });
});