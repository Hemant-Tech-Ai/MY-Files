<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Reports Management</h1>
      <div>
        <router-link to="/admin" class="btn btn-outline-secondary me-2">
          <i class="bi bi-arrow-left"></i> Back to Dashboard
        </router-link>
      </div>
    </div>
    
    <!-- Statistics Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card text-center p-3">
          <div class="display-4 mb-2">{{ stats.userCount || 0 }}</div>
          <div class="text-muted text-uppercase small">TOTAL USERS</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center p-3">
          <div class="display-4 mb-2">{{ stats.quizCount || 0 }}</div>
          <div class="text-muted text-uppercase small">TOTAL QUIZZES</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center p-3">
          <div class="display-4 mb-2">{{ stats.scoresLastMonth || 0 }}</div>
          <div class="text-muted text-uppercase small">SCORES LAST MONTH</div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-center p-3">
          <div class="display-4 mb-2">{{ reportsSent }}</div>
          <div class="text-muted text-uppercase small">REPORTS SENT</div>
        </div>
      </div>
    </div>
    
    <!-- Report Preview Section (Consolidated) -->
    <div v-if="previewData" class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Report Preview</h5>
            <button class="btn btn-sm btn-light" @click="previewData = null">
              <i class="bi bi-x"></i> Close
            </button>
          </div>
          <div class="card-body">
            <div v-if="!previewData.has_data" class="alert alert-warning">
              No activity found for this user in the selected month.
            </div>
            <div v-else>
              <div class="mb-4">
                <h3>Monthly Activity Report - {{ previewData.report_data.month }}</h3>
                <p class="lead">For: {{ previewData.user.full_name }} ({{ previewData.user.email }})</p>
              </div>
              
              <div class="row mb-4">
                <div class="col-md-6">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h5>Quizzes Completed</h5>
                      <div class="display-4">{{ previewData.report_data.total_quizzes }}</div>
                    </div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h5>Average Score</h5>
                      <div class="display-4">{{ previewData.report_data.average_score }}%</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <h4>Quiz Details</h4>
              <div class="table-responsive">
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Subject</th>
                      <th>Chapter</th>
                      <th>Quiz</th>
                      <th>Date</th>
                      <th>Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(quiz, index) in previewData.report_data.quiz_details" :key="index">
                      <td>{{ quiz.subject }}</td>
                      <td>{{ quiz.chapter }}</td>
                      <td>{{ quiz.quiz }}</td>
                      <td>{{ quiz.date }}</td>
                      <td>{{ quiz.score }} ({{ quiz.percentage }}%)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div class="mt-4 text-center">
                <button class="btn btn-primary" @click="sendReportForCurrentPreview" :disabled="isSending">
                  <span v-if="isSending" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  Generate and Send Report
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <!-- Monthly Report Generator -->
      <div class="col-md-6 mb-4">
        <div class="card">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Generate Monthly Reports</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="previewReport">
              <div class="mb-3">
                <label for="month-select" class="form-label">Month</label>
                <select v-model="reportForm.month" class="form-select" id="month-select" required>
                  <option value="">Select a month</option>
                  <option v-for="month in reportOptions.months" :key="month.value" :value="month">
                    {{ month.label }}
                  </option>
                </select>
              </div>
              <div class="mb-3">
                <label for="user-select" class="form-label">User</label>
                <select v-model="reportForm.userId" class="form-select" id="user-select" required>
                  <option value="">Select a user</option>
                  <option v-for="user in reportOptions.users" :key="user.id" :value="user.id">
                    {{ user.name }} ({{ user.email }})
                  </option>
                </select>
              </div>
              <div class="d-flex gap-2">
                <button type="submit" class="btn btn-info" :disabled="isLoading || !reportForm.month || !reportForm.userId">
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  Preview Report
                </button>
                <button type="button" class="btn btn-primary" @click="generateReport" :disabled="isLoading || !reportForm.month">
                  <span v-if="isSending" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  Generate and Send Report
                </button>
              </div>
            </form>
            <div v-if="successMessage" class="alert alert-success mt-3">
              {{ successMessage }}
            </div>
            <div v-if="errorMessage" class="alert alert-danger mt-3">
              {{ errorMessage }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Export Data -->
      <div class="col-md-6 mb-4">
        <div class="card">
          <div class="card-header bg-info text-white">
            <h5 class="mb-0">Export Data</h5>
          </div>
          <div class="card-body">
            <div class="mb-4">
              <h6>Export User Data</h6>
              <p class="small text-muted">Export all user performance data as CSV file</p>
              <button class="btn btn-outline-primary" @click="exportUsers" :disabled="isExporting">
                <span v-if="isExporting" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i class="bi bi-file-earmark-excel me-2"></i> Export User Data
              </button>
            </div>
            
            <hr>
            
            <!-- Export Status -->
            <div v-if="jobInfo.id" class="mt-4">
              <h6>Export Status</h6>
              <div class="alert" :class="getStatusAlertClass(jobInfo.status)">
                <div class="d-flex align-items-center">
                  <div class="flex-grow-1">
                    <strong>{{ getStatusLabel(jobInfo.status) }}</strong><br>
                    <small>{{ formatStatusMessage(jobInfo.message) }}</small>
                  </div>
                </div>
                <div v-if="jobInfo.status === 'running'" class="progress mt-2" style="height: 5px;">
                  <div class="progress-bar progress-bar-striped progress-bar-animated" 
                       :style="`width: ${jobInfo.progress}%`"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Quiz Assignments -->
    <div class="row mt-2">
      <div class="col-12">
        <div class="card">
          <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Quiz Assignments</h5>
            <button class="btn btn-sm btn-light" @click="fetchQuizAssignments">
              <i class="bi bi-arrow-clockwise"></i> Refresh
            </button>
          </div>
          <div class="card-body">
            <div v-if="loading.assignments" class="text-center py-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="error.assignments" class="alert alert-danger">
              {{ error.assignments }}
            </div>
            <div v-else-if="quizAssignments.length === 0" class="text-center py-3">
              <p class="text-muted">No quiz assignments found</p>
            </div>
            <div v-else>
              <div class="input-group mb-3">
                <input 
                  type="text" 
                  class="form-control" 
                  placeholder="Search assignments..." 
                  v-model="assignmentSearchTerm"
                  @input="filterAssignments">
                <button class="btn btn-outline-secondary" type="button">
                  <i class="bi bi-search"></i>
                </button>
              </div>
              
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Quiz</th>
                      <th>Student</th>
                      <th>Date</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="assignment in filteredAssignments" :key="`${assignment.quiz_id}-${assignment.user_id}`">
                      <td><strong>{{ assignment.subject_name || '' }} - {{ assignment.chapter_name || '' }}</strong></td>
                      <td>{{ assignment.student_name }}</td>
                      <td>{{ formatDate(assignment.date_of_quiz) }}</td>
                      <td>
                        <span v-if="assignment.completed" class="badge bg-success">Completed</span>
                        <span v-else class="badge bg-warning">Pending</span>
                      </td>
                      <td>
                        <button 
                          class="btn btn-primary" 
                          @click="prepareReportForUser(assignment.user_id)"
                          title="Generate report for this user">
                          <i class="bi bi-file-earmark-text me-1"></i> Generate Report
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'ReportsManagement',
  data() {
    return {
      stats: {
        userCount: 0,
        quizCount: 0,
        scoresLastMonth: 0,
        topUsers: []
      },
      reportOptions: {
        months: [],
        users: []
      },
      reportForm: {
        month: '',
        userId: ''
      },
      successMessage: '',
      errorMessage: '',
      isLoading: false,
      isSending: false,
      isExporting: false,
      reportsSent: 0,
      jobInfo: {
        id: null,
        status: '',
        progress: 0,
        message: '',
        downloadUrl: null
      },
      jobCheckInterval: null,
      previewData: null,
      // Quiz assignments data
      quizAssignments: [],
      filteredAssignments: [],
      assignmentSearchTerm: '',
      loading: {
        stats: true,
        assignments: true
      },
      error: {
        stats: null,
        assignments: null
      }
    };
  },
  mounted() {
    this.fetchReportOptions();
    this.fetchReportStats();
    this.fetchQuizAssignments();
  },
  beforeUnmount() {
    if (this.jobCheckInterval) {
      clearInterval(this.jobCheckInterval);
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    
    async fetchReportOptions() {
      try {
        const response = await api.getReportOptions();
        this.reportOptions = response.data;
      } catch (error) {
        console.error('Error fetching report options:', error);
        this.errorMessage = 'Failed to load report options. Please try again.';
      }
    },
    
    async fetchReportStats() {
      this.loading.stats = true;
      this.error.stats = null;
      
      try {
        const response = await api.getReportStats();
        console.log('Report stats retrieved:', response.data);
        this.stats = {
          userCount: response.data.user_count || 0,
          quizCount: response.data.quiz_count || 0,
          scoresLastMonth: response.data.scores_last_month || 0,
          topUsers: response.data.top_users || []
        };
        console.log('Stats set to:', this.stats);
      } catch (error) {
        console.error('Error fetching report stats:', error);
        this.error.stats = 'Failed to load report statistics';
      } finally {
        this.loading.stats = false;
      }
    },
    
    async fetchQuizAssignments() {
      this.loading.assignments = true;
      this.error.assignments = null;
      
      try {
        const response = await api.getQuizAssignments();
        this.quizAssignments = response.data;
        this.filteredAssignments = response.data;
        
        // For debugging - log the assignments data
        console.log("Quiz assignments fetched:", this.quizAssignments);
        
        if (this.quizAssignments.length === 0) {
          console.log("No assignments found");
        } else {
          // Check for required fields
          const sampleAssignment = this.quizAssignments[0];
          console.log("Sample assignment:", sampleAssignment);
        }
      } catch (error) {
        console.error('Error fetching quiz assignments:', error);
        this.error.assignments = 'Failed to load quiz assignments';
      } finally {
        this.loading.assignments = false;
      }
    },
    
    async previewReport() {
      if (!this.reportForm.month || !this.reportForm.userId) {
        this.errorMessage = 'Please select a month and user';
        return;
      }
      
      this.isLoading = true;
      this.errorMessage = '';
      this.successMessage = '';
      
      try {
        const payload = {
          month: this.reportForm.month.month,
          year: this.reportForm.month.year,
          user_id: this.reportForm.userId
        };
        
        const response = await api.previewMonthlyReport(payload);
        this.previewData = response.data;
        
        // Check if there's actually data in the preview
        if (this.previewData && !this.previewData.has_data) {
          // If no data, show a user-friendly message
          const userName = this.reportOptions.users.find(u => u.id === this.reportForm.userId)?.name || 'selected user';
          const monthName = this.reportForm.month.label;
          this.errorMessage = `No quiz activity found for ${userName} in ${monthName}. Please select a different month or user.`;
        }
        
        // Scroll to top to show the preview at the top of the page
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        // Clear success message when showing preview
        this.successMessage = '';
      } catch (error) {
        console.error('Error previewing report:', error);
        this.errorMessage = error.response?.data?.error || 'Failed to preview report';
      } finally {
        this.isLoading = false;
      }
    },
    
    async generateReport() {
      if (!this.reportForm.month) {
        this.errorMessage = 'Please select a month';
        return;
      }
      
      this.isSending = true;
      this.errorMessage = '';
      this.successMessage = '';
      
      try {
        const payload = {
          month: this.reportForm.month.month,
          year: this.reportForm.month.year
        };
        
        if (this.reportForm.userId) {
          payload.user_id = this.reportForm.userId;
        }
        
        const response = await api.triggerMonthlyReport(payload);
        this.successMessage = response.data.message;
        this.reportsSent++;
      } catch (error) {
        console.error('Error generating report:', error);
        this.errorMessage = error.response?.data?.error || 'Failed to generate report';
      } finally {
        this.isSending = false;
      }
    },
    
    async sendReportForCurrentPreview() {
      if (!this.previewData || !this.previewData.has_data) {
        return;
      }
      
      this.isSending = true;
      this.errorMessage = '';
      this.successMessage = '';
      
      try {
        const payload = {
          month: this.reportForm.month.month,
          year: this.reportForm.month.year,
          user_id: this.previewData.user.id
        };
        
        const response = await api.triggerMonthlyReport(payload);
        this.successMessage = response.data.message;
        this.reportsSent++;
        
        // Close the preview after sending
        setTimeout(() => {
          this.previewData = null;
        }, 2000); // Close after 2 seconds so user can see success message
      } catch (error) {
        console.error('Error sending report:', error);
        this.errorMessage = error.response?.data?.error || 'Failed to send report';
      } finally {
        this.isSending = false;
      }
    },
    
    async prepareReportForUser(userId) {
      // Find the user in the options
      const user = this.reportOptions.users.find(u => u.id === userId);
      
      if (!user) {
        console.error(`User with ID ${userId} not found in options`);
        this.errorMessage = 'User not found in available options';
        return;
      }
      
      console.log(`Preparing report for user: ${user.name} (ID: ${userId})`);
      this.reportForm.userId = userId;
      
      // If a month is already selected, preview the report
      if (this.reportForm.month) {
        await this.previewReport();
        // Scroll to the top where the preview is displayed
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        // If no month is selected, try to select the current month
        const currentDate = new Date();
        const currentMonthYear = {
          month: currentDate.getMonth() + 1, // JS months are 0-indexed
          year: currentDate.getFullYear(),
          label: new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(currentDate)
        };
        
        // Find the closest month in the options
        const availableMonth = this.reportOptions.months.find(m => 
          m.month === currentMonthYear.month && m.year === currentMonthYear.year
        ) || this.reportOptions.months[0]; // fallback to first month if current not available
        
        if (availableMonth) {
          this.reportForm.month = availableMonth;
          await this.previewReport();
          // Scroll to the top where the preview is displayed
          window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
          // Scroll to the top where the form is
          window.scrollTo({ top: 0, behavior: 'smooth' });
          this.errorMessage = 'Please select a month to generate a report';
          
          // Focus the month dropdown
          setTimeout(() => {
            const monthSelect = document.getElementById('month-select');
            if (monthSelect) {
              monthSelect.focus();
            }
          }, 500);
        }
      }
    },
    
    async generateReportForUser(userId) {
      if (!this.reportForm.month) {
        this.errorMessage = 'Please select a month first';
        return;
      }
      
      this.isSending = true;
      this.errorMessage = '';
      this.successMessage = '';
      
      try {
        const payload = {
          month: this.reportForm.month.month,
          year: this.reportForm.month.year,
          user_id: userId
        };
        
        const response = await api.triggerMonthlyReport(payload);
        this.successMessage = response.data.message;
        this.reportsSent++;
      } catch (error) {
        console.error('Error generating report for user:', error);
        this.errorMessage = error.response?.data?.error || 'Failed to generate report';
      } finally {
        this.isSending = false;
      }
    },
    
    async exportUsers() {
      this.isExporting = true;
      this.jobInfo = {
        id: null,
        status: '',
        progress: 0,
        message: '',
        downloadUrl: null
      };
      
      try {
        const response = await api.exportUsers();
        const jobId = response.data.job_id;
        
        this.jobInfo.id = jobId;
        this.jobInfo.status = 'running';
        this.jobInfo.message = 'Export job started';
        
        // Start checking job status
        this.checkJobStatus(jobId);
      } catch (error) {
        console.error('Error starting export:', error);
        this.errorMessage = error.response?.data?.error || 'Failed to start export';
        this.isExporting = false;
      }
    },
    
    checkJobStatus(jobId) {
      // Clear any existing interval
      if (this.jobCheckInterval) {
        clearInterval(this.jobCheckInterval);
      }
      
      // Set up new interval
      this.jobCheckInterval = setInterval(async () => {
        try {
          const response = await api.getJobStatus(jobId);
          const job = response.data;
          
          this.jobInfo.status = job.status;
          this.jobInfo.progress = job.progress;
          this.jobInfo.message = job.message;
          
          if (job.download_url) {
            this.jobInfo.downloadUrl = api.getDownloadUrl(job.download_url.split('/').pop());
          }
          
          // If job is completed or failed, stop checking
          if (job.status === 'completed' || job.status === 'failed') {
            clearInterval(this.jobCheckInterval);
            this.isExporting = false;
          }
        } catch (error) {
          console.error('Error checking job status:', error);
          clearInterval(this.jobCheckInterval);
          this.isExporting = false;
        }
      }, 2000); // Check every 2 seconds
    },
    
    getStatusAlertClass(status) {
      switch (status) {
        case 'completed': return 'alert-success';
        case 'failed': return 'alert-danger';
        case 'running': return 'alert-info';
        default: return 'alert-secondary';
      }
    },
    
    getStatusLabel(status) {
      switch (status) {
        case 'completed': return 'Export Completed';
        case 'failed': return 'Export Failed';
        case 'running': return 'Export in Progress';
        default: return 'Unknown Status';
      }
    },
    
    formatStatusMessage(message) {
      // If there's no message, return a default message
      if (!message) {
        return 'No status information available';
      }
      
      // Check if message contains DNS resolution errors
      if (message && message.includes('getaddrinfo failed')) {
        return 'Export completed successfully. Email notification could not be sent due to email server configuration.';
      }
      
      // Check for SMTP connection errors
      if (message && (message.includes('Failed to connect to SMTP server') || message.includes('Connection refused'))) {
        return 'Export completed successfully. Email notification could not be sent due to SMTP server connection issues.';
      }
      
      // Check for authentication errors
      if (message && message.includes('Authentication failed')) {
        return 'Export completed successfully. Email notification failed due to email authentication issues.';
      }
      
      // Check for any notification failure
      if (message && message.includes('Failed to send notification')) {
        return 'Export completed successfully, but email notification could not be sent.';
      }
      
      // Handle successful completions clearly
      if (message && message.includes('Export completed successfully')) {
        return message;
      }
      
      return message;
    },
    
    async sendReportForSpecificUser(userId) {
      if (!this.reportForm.month) {
        this.errorMessage = 'Please select a month first';
        return;
      }
      
      this.isSending = true;
      this.errorMessage = '';
      this.successMessage = '';
      
      try {
        const payload = {
          month: this.reportForm.month.month,
          year: this.reportForm.month.year,
          user_id: userId
        };
        
        const response = await api.triggerMonthlyReport(payload);
        this.successMessage = response.data.message;
        this.reportsSent++;
      } catch (error) {
        console.error('Error sending report:', error);
        this.errorMessage = error.response?.data?.error || 'Failed to send report';
      } finally {
        this.isSending = false;
      }
    },
    
    filterAssignments() {
      if (!this.assignmentSearchTerm) {
        this.filteredAssignments = this.quizAssignments;
        return;
      }
      
      this.filteredAssignments = this.quizAssignments.filter(assignment => {
        const searchTerm = this.assignmentSearchTerm.toLowerCase();
        return (
          assignment.subject_name && assignment.subject_name.toLowerCase().includes(searchTerm) ||
          assignment.chapter_name && assignment.chapter_name.toLowerCase().includes(searchTerm) ||
          assignment.student_name && assignment.student_name.toLowerCase().includes(searchTerm)
        );
      });
    }
  }
};
</script>

<style scoped>
.card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}
.card-header {
  border-radius: 8px 8px 0 0;
  font-weight: bold;
}
</style> 