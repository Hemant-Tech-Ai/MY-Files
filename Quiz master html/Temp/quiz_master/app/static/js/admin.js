// Admin Dashboard Charts
function initDashboardCharts() {
    // Example chart using Chart.js
    const ctx = document.getElementById('quizAttemptsChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Quiz Attempts',
                data: [12, 19, 3, 5, 2, 3],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        }
    });
}

// Subject Management
function initSubjectManagement() {
    const editSubjectModal = new bootstrap.Modal(document.getElementById('editSubjectModal'));
    
    // Edit Subject Handler
    document.querySelectorAll('.edit-subject').forEach(button => {
        button.addEventListener('click', function() {
            const subjectId = this.dataset.id;
            // Fetch subject details and populate modal
            fetch(`/admin/subjects/${subjectId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('editSubjectId').value = subjectId;
                    document.getElementById('editName').value = data.name;
                    document.getElementById('editDescription').value = data.description;
                    editSubjectModal.show();
                });
        });
    });
}

// Quiz Management
function initQuizManagement() {
    // Date validation for quiz creation
    const dateInput = document.getElementById('date_of_quiz');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
    }

    // Duration validation
    const durationInput = document.getElementById('time_duration');
    if (durationInput) {
        durationInput.addEventListener('input', function() {
            if (this.value < 1) this.value = 1;
            if (this.value > 180) this.value = 180;
        });
    }
}

// Question Management
function initQuestionManagement() {
    // Preview question as it's being created
    const questionPreview = document.getElementById('questionPreview');
    const questionStatement = document.getElementById('question_statement');
    
    if (questionStatement && questionPreview) {
        questionStatement.addEventListener('input', function() {
            questionPreview.textContent = this.value;
        });
    }
}

// Initialize all admin functions
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('quizAttemptsChart')) {
        initDashboardCharts();
    }
    
    if (document.querySelector('.edit-subject')) {
        initSubjectManagement();
    }
    
    if (document.getElementById('date_of_quiz')) {
        initQuizManagement();
    }
    
    if (document.getElementById('question_statement')) {
        initQuestionManagement();
    }
}); 