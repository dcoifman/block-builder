document.addEventListener('DOMContentLoaded', function () {
    fetchAndDisplayProgram();

    const logWorkoutForm = document.getElementById('log-workout-form');
    if (logWorkoutForm) {
        // Set default date to today for the date input
        const dateInput = document.getElementById('log-date');
        if(dateInput) {
            dateInput.valueAsDate = new Date();
        }
        logWorkoutForm.addEventListener('submit', handleLogWorkoutSubmit);
    }
});

async function fetchAndDisplayProgram() {
    const programContainer = document.getElementById('program-container');
    if (!programContainer) return;

    programContainer.innerHTML = '<p>Loading your program...</p>';

    try {
        const response = await fetch('/api/program/generate_linear');
        if (!response.ok) {
            if (response.status === 401) window.location.href = '/auth/login';
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        const programData = await response.json();

        if (!programData || programData.length === 0) {
            programContainer.innerHTML = '<p class="flash error">Could not load your program. Ensure your 1RMs are set on the dashboard.</p>';
            return;
        }
        renderProgram(programData, programContainer);

    } catch (error) {
        console.error('Error fetching program:', error);
        programContainer.innerHTML = `<p class="flash error">Error fetching program: ${error.message}</p>`;
    }
}

function renderProgram(programData, container) {
    container.innerHTML = ''; // Clear loading message

    // Group exercises by week and then by day
    const programByWeek = programData.reduce((acc, entry) => {
        const week = entry.week;
        const day = entry.day;
        if (!acc[week]) {
            acc[week] = {};
        }
        if (!acc[week][day]) {
            acc[week][day] = {
                workout_name: entry.workout_name,
                exercises: []
            };
        }
        acc[week][day].exercises.push(entry);
        return acc;
    }, {});

    for (const weekNum in programByWeek) {
        const weekSection = document.createElement('section');
        weekSection.className = 'program-week';
        weekSection.innerHTML = `<h3>Week ${weekNum}</h3>`;

        const daysInWeek = programByWeek[weekNum];
        for (const dayNum in daysInWeek) {
            const dayData = daysInWeek[dayNum];
            const dayDiv = document.createElement('div');
            dayDiv.className = 'program-day';
            dayDiv.innerHTML = `<h4>${dayData.workout_name} (Day ${dayNum})</h4>`;
            
            const exerciseTable = document.createElement('table');
            exerciseTable.className = 'exercise-table';
            exerciseTable.innerHTML = `
                <thead>
                    <tr>
                        <th>Exercise</th>
                        <th>Type</th>
                        <th>Sets</th>
                        <th>Reps</th>
                        <th>Target Weight</th>
                        <th>Intensity</th>
                        <th>Notes</th>
                        <th>Action</th>
                    </tr>
                </thead>
            `;
            const tbody = document.createElement('tbody');
            dayData.exercises.forEach(ex => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${ex.exercise_name}</td>
                    <td>${ex.exercise_type}</td>
                    <td>${ex.sets}</td>
                    <td>${ex.reps}</td>
                    <td>${ex.target_weight !== null && ex.target_weight !== undefined ? ex.target_weight : 'N/A'} ${typeof ex.target_weight === 'number' ? 'kg' : ''}</td>
                    <td>${ex.intensity_percent ? ex.intensity_percent.toFixed(0) + '%' : 'N/A'}</td>
                    <td>${ex.notes || ''}</td>
                    <td><button class="btn btn-small log-this-workout-btn" data-exercise='${JSON.stringify(ex)}'>Log This</button></td>
                `;
            });
            exerciseTable.appendChild(tbody);
            dayDiv.appendChild(exerciseTable);
            weekSection.appendChild(dayDiv);
        }
        container.appendChild(weekSection);
    }
    
    // Add event listeners to "Log This" buttons
    document.querySelectorAll('.log-this-workout-btn').forEach(button => {
        button.addEventListener('click', function() {
            const exerciseData = JSON.parse(this.dataset.exercise);
            prefillLogForm(exerciseData);
            document.getElementById('log-workout-section').scrollIntoView({ behavior: 'smooth' });
        });
    });
}

function prefillLogForm(exerciseData) {
    document.getElementById('log-exercise-name').value = exerciseData.exercise_name;
    document.getElementById('log-sets').value = exerciseData.sets;
    document.getElementById('log-reps').value = String(exerciseData.reps).split('-')[0]; // Take first number if range e.g. "10-12"
    
    let weightToLog = exerciseData.target_weight;
    if (typeof exerciseData.target_weight === 'string' && exerciseData.target_weight.toLowerCase().includes('kg')) {
        weightToLog = parseFloat(exerciseData.target_weight);
    } else if (typeof exerciseData.target_weight !== 'number') {
         weightToLog = ''; // Clear if not a numeric value for logging
    }
    document.getElementById('log-weight').value = weightToLog;
    
    // Set date to today by default if not already set
    const dateInput = document.getElementById('log-date');
    if(!dateInput.value) {
        dateInput.valueAsDate = new Date();
    }
}

async function handleLogWorkoutSubmit(event) {
    event.preventDefault();
    const feedbackDiv = document.getElementById('log-workout-feedback');
    feedbackDiv.textContent = '';
    feedbackDiv.className = '';

    const exerciseName = document.getElementById('log-exercise-name').value;
    const sets = document.getElementById('log-sets').value;
    const reps = document.getElementById('log-reps').value;
    const weight = document.getElementById('log-weight').value;
    const dateLogged = document.getElementById('log-date').value; // Format: YYYY-MM-DD

    if (!exerciseName || !sets || !reps || !weight || !dateLogged) {
        feedbackDiv.textContent = 'All fields are required.';
        feedbackDiv.className = 'flash error';
        return;
    }

    const payload = {
        exercise_name: exerciseName,
        sets: parseInt(sets),
        reps: parseInt(reps),
        weight: parseFloat(weight),
        date_logged: dateLogged // API can handle YYYY-MM-DD
    };

    try {
        const response = await fetch('/api/log_workout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || `HTTP error! status: ${response.status}`);
        }
        
        feedbackDiv.textContent = result.message || 'Workout logged successfully!';
        feedbackDiv.className = 'flash success';
        event.target.reset(); // Reset form
        // Optionally, set date back to today after reset
        const dateInput = document.getElementById('log-date');
        if(dateInput) { dateInput.valueAsDate = new Date(); }
        // Could also refresh a "recently logged" list here if one existed
    } catch (error) {
        console.error('Error logging workout:', error);
        feedbackDiv.textContent = `Error: ${error.message}`;
        feedbackDiv.className = 'flash error';
    }
}
