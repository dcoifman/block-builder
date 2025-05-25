document.addEventListener('DOMContentLoaded', function () {
    const filterForm = document.getElementById('filter-history-form');
    const exerciseSelect = document.getElementById('filter-exercise-name');
    const dateFromInput = document.getElementById('filter-date-from');
    const dateToInput = document.getElementById('filter-date-to');
    const historyTbody = document.getElementById('workout-history-tbody');
    const noHistoryMessage = document.getElementById('no-history-message');
    const resetFiltersBtn = document.getElementById('reset-filters-btn');

    // Fetch exercises for the filter dropdown
    async function populateExerciseFilter() {
        try {
            const response = await fetch('/api/exercises'); // Assumes this endpoint is under api_bp
            if (!response.ok) {
                if (response.status === 401) window.location.href = '/auth/login';
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const exercises = await response.json();
            exercises.forEach(exercise => {
                const option = document.createElement('option');
                option.value = exercise.name;
                option.textContent = exercise.name;
                exerciseSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching exercises for filter:', error);
            // Optionally display an error message
        }
    }

    // Fetch and display workout history
    async function fetchWorkoutHistory(filters = {}) {
        historyTbody.innerHTML = '<tr><td colspan="5">Loading history...</td></tr>';
        noHistoryMessage.style.display = 'none';

        let queryParams = new URLSearchParams();
        if (filters.exercise_name) {
            queryParams.append('exercise_name', filters.exercise_name);
        }
        if (filters.date_from) {
            queryParams.append('date_from', filters.date_from);
        }
        if (filters.date_to) {
            queryParams.append('date_to', filters.date_to);
        }

        try {
            const response = await fetch(`/api/workout_history?${queryParams.toString()}`);
            if (!response.ok) {
                if (response.status === 401) window.location.href = '/auth/login';
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            const historyLogs = await response.json();

            historyTbody.innerHTML = ''; // Clear loading message
            if (historyLogs.length === 0) {
                noHistoryMessage.style.display = 'block';
            } else {
                historyLogs.forEach(log => {
                    const row = historyTbody.insertRow();
                    row.insertCell().textContent = new Date(log.date_logged).toLocaleDateString();
                    row.insertCell().textContent = log.exercise_name;
                    row.insertCell().textContent = log.sets;
                    row.insertCell().textContent = log.reps;
                    row.insertCell().textContent = log.weight;
                });
            }
        } catch (error) {
            console.error('Error fetching workout history:', error);
            historyTbody.innerHTML = `<tr><td colspan="5" class="flash error">Error fetching history: ${error.message}</td></tr>`;
            noHistoryMessage.style.display = 'none';
        }
    }

    // Event listener for filter form submission
    filterForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const filters = {
            exercise_name: exerciseSelect.value,
            date_from: dateFromInput.value,
            date_to: dateToInput.value
        };
        fetchWorkoutHistory(filters);
    });

    // Event listener for reset filters button
    if(resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', function() {
            filterForm.reset();
            // After resetting, select the "All Exercises" option explicitly if it's the first one
            if(exerciseSelect.options.length > 0) {
                 exerciseSelect.value = ""; // Assuming the "All Exercises" option has an empty value
            }
            fetchWorkoutHistory(); // Fetch all history
        });
    }

    // Initial load
    populateExerciseFilter();
    fetchWorkoutHistory(); 
});
