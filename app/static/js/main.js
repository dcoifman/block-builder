// Strength Tracker - main.js

document.addEventListener('DOMContentLoaded', function () {
    // Check if on dashboard page by looking for specific elements
    if (document.getElementById('dashboard-content')) {
        fetchExercisesForDropdown();
        fetchUserMaxes();
        fetchPoliquinTargets();

        const addMaxForm = document.getElementById('add-max-form');
        if (addMaxForm) {
            addMaxForm.addEventListener('submit', handleAddOrUpdateMax);
        }
    }

    // Could add event listeners for other pages here if needed
});

async function fetchExercisesForDropdown() {
    try {
        const response = await fetch('/api/exercises'); // Assumes this endpoint exists
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const exercises = await response.json();
        
        const selectElement = document.getElementById('exercise-select');
        if (selectElement) {
            exercises.forEach(exercise => {
                const option = document.createElement('option');
                option.value = exercise.name; // Or exercise.id if API expects id
                option.textContent = exercise.name;
                selectElement.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error fetching exercises:', error);
        // Optionally display an error message to the user on the page
        const exerciseSection = document.getElementById('user-maxes-section');
        if (exerciseSection) {
            exerciseSection.innerHTML = '<p class="flash error">Could not load exercises for form.</p>';
        }
    }
}

async function fetchUserMaxes() {
    try {
        const response = await fetch('/api/user_maxes');
        if (!response.ok) {
            if (response.status === 401) { // Unauthorized
                window.location.href = '/auth/login'; // Redirect to login
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const maxes = await response.json();
        const maxesList = document.getElementById('user-maxes-list');
        
        if (maxesList) {
            maxesList.innerHTML = ''; // Clear existing
            if (maxes.length === 0) {
                maxesList.innerHTML = '<li>No maxes recorded yet.</li>';
            } else {
                maxes.forEach(max => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${max.exercise_name}: ${max.max_weight} kg (Recorded: ${new Date(max.date_recorded).toLocaleDateString()})`;
                    maxesList.appendChild(listItem);
                });
            }
        }
    } catch (error) {
        console.error('Error fetching user maxes:', error);
        const maxesList = document.getElementById('user-maxes-list');
        if (maxesList) {
            maxesList.innerHTML = '<li><span class="flash error">Error loading your maxes.</span></li>';
        }
    }
}

async function handleAddOrUpdateMax(event) {
    event.preventDefault();
    const exerciseName = document.getElementById('exercise-select').value;
    const maxWeight = document.getElementById('max-weight-input').value;
    const feedbackDiv = document.getElementById('add-max-feedback');

    if (!exerciseName || !maxWeight) {
        feedbackDiv.textContent = 'Please select an exercise and enter a weight.';
        feedbackDiv.className = 'flash error';
        return;
    }

    try {
        const response = await fetch('/api/user_maxes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                exercise_name: exerciseName,
                max_weight: parseFloat(maxWeight)
            }),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || `HTTP error! status: ${response.status}`);
        }
        
        feedbackDiv.textContent = result.message || 'Max saved successfully!';
        feedbackDiv.className = 'flash success';
        fetchUserMaxes(); // Refresh the list of maxes
        document.getElementById('add-max-form').reset(); // Reset form
    } catch (error) {
        console.error('Error saving user max:', error);
        feedbackDiv.textContent = `Error: ${error.message}`;
        feedbackDiv.className = 'flash error';
    }
}

async function fetchPoliquinTargets() {
    try {
        const response = await fetch('/api/poliquin_targets');
        if (!response.ok) {
            if (response.status === 401) { // Unauthorized
                window.location.href = '/auth/login';
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const targets = await response.json();
        const targetsList = document.getElementById('poliquin-targets-list');

        if (targetsList) {
            targetsList.innerHTML = ''; // Clear existing
            if (targets.length === 0) {
                targetsList.innerHTML = '<li>No Poliquin targets available. This might be because you haven\'t set a 1RM for the primary exercises used in ratio calculations.</li>';
            } else {
                targets.forEach(target => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${target.secondary_exercise_name} (Target): ${target.target_weight} kg (Based on ${target.primary_exercise_name_used} 1RM of ${target.primary_exercise_max_used}kg at ${target.ratio_applied * 100}%)`;
                    targetsList.appendChild(listItem);
                });
            }
        }
    } catch (error) {
        console.error('Error fetching Poliquin targets:', error);
        const targetsList = document.getElementById('poliquin-targets-list');
        if (targetsList) {
             targetsList.innerHTML = '<li><span class="flash error">Error loading Poliquin targets.</span></li>';
        }
    }
}

// Utility for flash messages (if needed globally, otherwise keep scoped)
function displayFlashMessage(message, type = 'success') {
    const flashContainer = document.getElementById('flash-messages-container'); // Assuming you have a global container
    if (flashContainer) {
        const flashDiv = document.createElement('div');
        flashDiv.className = `flash ${type}`;
        flashDiv.textContent = message;
        flashContainer.appendChild(flashDiv);
        setTimeout(() => flashDiv.remove(), 5000); // Auto-remove after 5s
    }
}
