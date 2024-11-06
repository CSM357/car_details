// Show image preview when a file is selected
document.getElementById('lp_image').addEventListener('change', function (event) {
    const file = event.target.files[0];
    const preview = document.getElementById('lp_image_preview');
    const detectedLicensePlateDiv = document.getElementById('detected_license_plate');
    const showLpDetailsButton = document.getElementById('showLpDetails');

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            preview.style.backgroundImage = `url(${e.target.result})`;
            preview.style.display = 'block';
            detectedLicensePlateDiv.innerHTML = '';
            showLpDetailsButton.style.display = 'none';
        };
        reader.readAsDataURL(file);
    } else {
        preview.style.backgroundImage = 'none';
        preview.style.display = 'none';
        detectedLicensePlateDiv.innerHTML = '';
        showLpDetailsButton.style.display = 'none';
    }
});

// Detect license plate number
document.getElementById('detectLicensePlate').addEventListener('click', async () => {
    const lpImage = document.getElementById('lp_image').files[0];
    const detectedLicensePlateDiv = document.getElementById('detected_license_plate');
    const showLpDetailsButton = document.getElementById('showLpDetails');

    if (!lpImage) {
        alert('Please upload a license plate image.');
        return;
    }

    const formData = new FormData();
    formData.append('lp_image', lpImage);
    
    detectedLicensePlateDiv.innerHTML = '<p>Detecting license plate...</p>';

    try {
        const response = await fetch('/recognize_lp', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) throw new Error(`Error: ${response.statusText}`);

        const result = await response.json();

        detectedLicensePlateDiv.innerHTML = `<h2>Detected License Plate:</h2><p>${result.license_plate}</p>`;
        showLpDetailsButton.style.display = 'inline-block';
        showLpDetailsButton.dataset.licensePlate = result.license_plate;

    } catch (error) {
        console.error('Error:', error);
        detectedLicensePlateDiv.innerHTML = '<h2>Error:</h2><p>An error occurred while detecting the license plate. Please try again.</p>';
        showLpDetailsButton.style.display = 'none';
    }
});

// Show vehicle details based on detected license plate
// Show vehicle details based on detected license plate
document.getElementById('showLpDetails').addEventListener('click', async () => {
    const licensePlate = document.getElementById('showLpDetails').dataset.licensePlate;
    const lpDetailsDiv = document.getElementById('lp_details');

    if (!licensePlate) {
        alert('No license plate detected.');
        return;
    }

    lpDetailsDiv.innerHTML = '<p>Fetching vehicle details...</p>';

    try {
        const response = await fetch('/get-vehicle-details', {
            method: 'GET',
        });

        if (!response.ok) throw new Error(`Error fetching JSON: ${response.statusText}`);

        const vehicleData = await response.json();

        // Parse the JSON data within the `success` field
        const vehicleInfo = JSON.parse(vehicleData.success).data;

        // Check if the detected license plate matches the registration number
        if (vehicleInfo.registration_no === licensePlate) {
            // Generate HTML for vehicle information
            const vehicleInfoHTML = Object.entries(vehicleInfo)
                .filter(([_, value]) => value !== null && value !== undefined)
                .map(([key, value]) => `<li><strong>${key.replace(/_/g, ' ')}:</strong> ${value}</li>`)
                .join('');
                
            lpDetailsDiv.innerHTML = `<h2>Vehicle Information:</h2><ul>${vehicleInfoHTML}</ul>`;
        } else {
            lpDetailsDiv.innerHTML = '<h2>Error:</h2><p>No matching vehicle information found for the detected license plate.</p>';
        }
    } catch (error) {
        console.error('Error:', error);
        lpDetailsDiv.innerHTML = '<h2>Error:</h2><p>An error occurred while fetching vehicle details. Please try again.</p>';
    }
});
