console.log('File cart.js caricato'); // Debug

document.addEventListener('DOMContentLoaded', function() {
    const confirmationPopup = document.getElementById('confirmation-popup');
    const confirmDeleteButton = document.getElementById('confirm-delete');
    const cancelDeleteButton = document.getElementById('cancel-delete');
    const popupMessage = document.getElementById('popup-message');
    let currentForm = null;

    // Gestione del popup di conferma
    document.querySelectorAll('.icon-remove').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Pulsante rimuovi cliccato'); // Debug
            currentForm = this.closest('form');
            console.log('form', currentForm);
            const itemName = currentForm.querySelector('p').textContent || 'Questo articolo';
            popupMessage.textContent = `Sei sicuro di voler rimuovere ${itemName} dal carrello?`;
            confirmationPopup.style.display = 'flex'; // Mostra il popup
        });
    });

    // Conferma rimozione
    confirmDeleteButton.addEventListener('click', function() {
        if (currentForm) {
            currentForm.submit(); // Invia il modulo per rimuovere l'articolo
        }
        confirmationPopup.style.display = 'none'; // Nascondi il popup
    });

    // Annulla rimozione
    cancelDeleteButton.addEventListener('click', function() {
        confirmationPopup.style.display = 'none'; // Nascondi il popup
    });

    // Chiudi il popup se l'utente clicca al di fuori di esso
    confirmationPopup.addEventListener('click', function(e) {
        if (e.target === confirmationPopup) {
            confirmationPopup.style.display = 'none'; // Nascondi il popup
        }
    });

    // Gestione dei pulsanti per modificare la quantità
    const decreaseButtons = document.querySelectorAll('.decrease-quantity');
    const increaseButtons = document.querySelectorAll('.increase-quantity');

    decreaseButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const form = this.closest('form');
            const quantityInput = form.querySelector('.quantity-input');
            let currentQuantity = parseInt(quantityInput.value);

            if (currentQuantity > 1) {
                quantityInput.value = currentQuantity - 1;
                form.submit(); // Invia il modulo con la quantità aggiornata
            } else {
                // Se la quantità è 1, mostra il popup di conferma per la rimozione
                currentForm = form;
                popupMessage.textContent = 'La quantità è già 1. Vuoi rimuovere l\'articolo dal carrello?';
                confirmationPopup.style.display = 'flex'; // Mostra il popup
            }
        });
    });

    increaseButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const form = this.closest('form');
            const quantityInput = form.querySelector('.quantity-input');
            quantityInput.value = parseInt(quantityInput.value) + 1;
            form.submit(); // Invia il modulo con la quantità aggiornata
        });
    });
});
