$(document).ready(function () {
    console.log('Document is Ready - scripts.js loaded');

    $('#add-note-form').on('submit', function (e) {
        e.preventDefault();
        console.log('Form submitted (preventDefault called)');

        const formData = $(this).serialize();
        console.log('Form data:', formData);

        $.ajax({
            type: 'POST',
            url: '/notes/ajax-add/',
            data: formData,
            success: function (response) {
                console.log('AJAX success response:', response);
                let newNote;

                if (response.type === 'html') {
                    $('#notes-list').prepend(response.html);
                    $('#add-note-form').trigger('reset');
                    console.log('Note added and form reset.');
                } else {
                    console.error('Received unexpected response type:', response.type);
                    alert('Error: Unexpected response from server.');
                }
            },
            error: function (xhr, status, error) {
                console.error('AJAX error:', status, error);
                alert('Error adding note. Please try again.');
            }
        });
    });

    // --- Folder Creation Logic --- 
    const addFolderForm = $('#add-folder-form');
    const newFolderNameInput = $('#new-folder-name');
    const showAddFolderBtn = $('#show-add-folder-btn');
    const cancelAddFolderBtn = $('#cancel-add-folder');
    const folderListUl = $('.folder-list'); // Assuming this is the UL element

    // Show folder form on button click
    showAddFolderBtn.on('click', function() {
        addFolderForm.css('display', 'flex'); // Use flex to show
        showAddFolderBtn.hide();
        newFolderNameInput.focus();
    });

    // Hide folder form on cancel click
    cancelAddFolderBtn.on('click', function() {
        addFolderForm.hide();
        showAddFolderBtn.show();
        newFolderNameInput.val(''); // Clear input
    });

    // Handle folder form submission
    addFolderForm.on('submit', function(e) {
        e.preventDefault();
        const folderName = newFolderNameInput.val().trim();
        const csrfToken = $('input[name=csrfmiddlewaretoken]').val(); // Get CSRF token

        if (folderName) {
            $.ajax({
                url: '/notes/ajax-add-folder/', // URL for the new view
                method: 'POST',
                data: {
                    'name': folderName,
                    'csrfmiddlewaretoken': csrfToken
                },
                dataType: 'json',
                success: function(response) {
                    if (response.success && response.folder) {
                        // Add the new folder to the list
                        const newFolderHtml = `
                            <li class="">
                                <a href="/notes/?folder=${response.folder.id}">${response.folder.name}</a>
                            </li>
                        `;
                        // Append to the list (maybe remove the 'No folders yet' message first if it exists)
                        folderListUl.find('li:contains("No folders yet.")').remove(); // Remove 'empty' message
                        folderListUl.append(newFolderHtml);

                        // Reset form
                        addFolderForm.hide();
                        showAddFolderBtn.show();
                        newFolderNameInput.val('');
                        console.log('Folder added:', response.folder.name);
                        // Optionally, display a success message to the user
                    } else {
                        console.error('Error adding folder:', response.error);
                        alert('Error: ' + response.error); // Show error to user
                    }
                },
                error: function(xhr, status, error) {
                    console.error('AJAX error:', status, error);
                    alert('An error occurred while adding the folder.');
                }
            });
        }
    });
    // --- End Folder Creation Logic ---
});

/*
function toggleNote(button) {
    const card = button.closest('.note-card');
    const preview = card.querySelector('.note-preview');
    const full = card.querySelector('.note-full');

    if (preview && full) {
        preview.classList.toggle('hidden');
        full.classList.toggle('show');
    }
}
*/







