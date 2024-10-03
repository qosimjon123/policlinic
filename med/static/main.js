document.addEventListener('DOMContentLoaded', function() {
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
