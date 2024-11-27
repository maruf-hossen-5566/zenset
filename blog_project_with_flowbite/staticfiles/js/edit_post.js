// --- Inner Html ---
window.addEventListener("load",
    function () {
        try {
            // Access the data from window.POST_DATA
            const postContent = window.POST_DATA.content;
            const postId = window.POST_DATA.id;

            console.log("postContent:", postContent);
            console.log("postId:", postId);

            const contentElement = document.querySelector('#wysiwyg-example').firstElementChild;
            if (contentElement) {
                contentElement.innerHTML = postContent;
            }
        } catch (error) {
            console.error("Error loading post data:", error);
        }
    }
)

// --- Create Post submit button ---
document.addEventListener('DOMContentLoaded', function () {
    const submitButton = document.querySelector('.create_form_submit_button');

    submitButton.addEventListener('click', function (e) {
        e.preventDefault();

        const contentElement = document.querySelector('#wysiwyg-example').firstElementChild;
        const form = document.querySelector('form');

        // --- Function to remove empty paragraphs
        function removeEmptyParagraphs(html) {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;

            const paragraphs = tempDiv.querySelectorAll('p');
            paragraphs.forEach(p => {
                if (!p.textContent.trim() && !p.querySelector('img')) {
                    p.remove();
                }
            });

            return tempDiv.innerHTML;
        }

        // Clean the content
        let cleanedContent = removeEmptyParagraphs(contentElement.innerHTML);

        // --- Check if the cleaned content is empty
        const isEmpty = !cleanedContent.trim() || cleanedContent === '<br class="ProseMirror-trailingBreak">';

        if (isEmpty) {
            // If content is empty, set an empty string
            form.content.value = '';
        } else {
            // Otherwise, use the cleaned content
            form.content.value = cleanedContent;
        }

        form.submit();
    });
});
