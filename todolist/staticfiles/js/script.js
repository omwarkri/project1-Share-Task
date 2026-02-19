function openModal(taskId) {
    const modal = document.getElementById(`shareTaskModal-${taskId}`);
    modal.style.display = 'block';
}

function closeModal(taskId) {
    const modal = document.getElementById(`shareTaskModal-${taskId}`);
    modal.style.display = 'none';
}
