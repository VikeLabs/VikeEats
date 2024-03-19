// Fetch data from the API endpoint
fetch('/api/food_outlets')
    .then(response => response.json())
    .then(data => {
        // Get the table body element
        const tableBody = document.getElementById('foodOutletTableBody');

        // Loop through the data array and create table rows
        data.forEach(item => {
            const row = document.createElement('tr');

            // Create table data cells for outlet and hours
            const outletCell = document.createElement('td');
            outletCell.textContent = item[0];

            const hoursCell = document.createElement('td');
            hoursCell.textContent = item[1];

            // Append cells to the row
            row.appendChild(outletCell);
            row.appendChild(hoursCell);

            // Append row to the table body
            tableBody.appendChild(row);
        });
    })
    .catch(error => {
        console.error('Error fetching data:', error);
    });
