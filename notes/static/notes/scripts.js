$(document).ready(function () {
    $('#add-note-form').on('submit', function (e) {
        e.preventDefault(); // зупиняємо стандартну відправку форми

        const formData = $(this).serialize();

        $.ajax({
            type: 'POST',
            url: '/notes/ajax-add/',
            data: formData,
            success: function (response) {
                // Випадкове рішення — JSON чи HTML
                if (response.type === 'json') {
                    const note = response.note;
                    const newNote = `
                        <div class="note-card">
                            <h2>${note.title}</h2>
                            <p>${note.content}</p>
                        </div>`;
                    $('#notes-list').prepend(newNote);
                } else if (response.type === 'html') {
                    $('#notes-list').prepend(response.html);
                }

                // Очищаємо форму
                $('#add-note-form').trigger('reset');
            },
            error: function () {
                alert('Error adding note');
            }
        });
    });
});