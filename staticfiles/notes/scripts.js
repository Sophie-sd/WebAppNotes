$(document).ready(function () {
    $('#add-note-form').on('submit', function (e) {
        e.preventDefault();

        const formData = $(this).serialize();

        $.ajax({
            type: 'POST',
            url: $('#urls').data('add-url'),
            data: formData,
            success: function (response) {
                let newNote;

                if (response.type === 'json') {
                    const note = response.note;
                    newNote = $(`
                        <div class="note-card fade-in">
                            <h2>${note.title}</h2>
                            <p class="note-preview">${note.content.substring(0, 100)}...</p>
                            <div class="note-full">${note.content}</div>
                            <div class="note-actions">
                                <a href="${$('#urls').data('edit-url').replace('0', note.id)}" class="icon-btn edit-btn" title="Edit">✏️</a>
                                <a href="${$('#urls').data('delete-url').replace('0', note.id)}" class="icon-btn delete-btn" title="Delete">🗑️</a>
                                <button onclick="toggleNote(this)" class="icon-btn view-btn" title="View full note">📖</button>
                            </div>
                        </div>
                    `);
                } else if (response.type === 'html') {
                    newNote = $(response.html).addClass('fade-in');
                }

                $('#notes-list').prepend(newNote);
                $('#add-note-form').trigger('reset');
            },
            error: function () {
                alert('Error adding note');
            }
        });
    });
});

function toggleNote(button) {
    const card = button.closest('.note-card');
    const preview = card.querySelector('.note-preview');
    const full = card.querySelector('.note-full');

    if (preview && full) {
        preview.classList.toggle('hidden');
        full.classList.toggle('show');
    }
}







