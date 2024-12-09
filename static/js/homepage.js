document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', () => {
        // Remove active class from all menu items
        document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));

        // Add active class to the clicked item
        item.classList.add('active');

        // Change the content dynamically
        const contentArea = document.getElementById('content-area');
        if (item.id === 'my-events') {
            contentArea.innerHTML = `
                <h1>My Events</h1>
                <div class="events-container">
                    <div class="event-card">
                        <h2>Event Name</h2>
                        <p>Date: 2024-01-01</p>
                        <p>Location: Online</p>
                    </div>
                </div>
            `;
        } else if (item.id === 'my-tickets') {
            contentArea.innerHTML = `
                <h1>My Tickets</h1>
                <p>Here you will see your purchased tickets.</p>
            `;
        } else if (item.id === 'browse-events') {
            contentArea.innerHTML = `
                <h1>Browse Events</h1>
                <p>Discover upcoming events here.</p>
            `;
        }
    });
});