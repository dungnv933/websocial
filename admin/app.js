// HOMEMMO Admin Dashboard JavaScript

// Global variables
let currentPage = 'dashboard';
let charts = {};
let dataTables = {};

// API Configuration
const API_CONFIG = {
    baseURL: '/api',
    timeout: 10000
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    console.log('Initializing HOMEMMO Admin Dashboard...');
    
    // Show dashboard by default
    showPage('dashboard');
    
    // Load initial data
    loadDashboardData();
    
    // Setup event listeners
    setupEventListeners();
    
    console.log('Admin Dashboard initialized successfully');
}

function setupEventListeners() {
    // Sidebar toggle
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    // Notification click
    const notificationIcon = document.querySelector('.notification-icon');
    if (notificationIcon) {
        notificationIcon.addEventListener('click', showNotifications);
    }
    
    // Admin dropdown
    const adminDropdown = document.querySelector('.btn-admin-dropdown');
    if (adminDropdown) {
        adminDropdown.addEventListener('click', toggleAdminDropdown);
    }
}

// Navigation functions
function showPage(pageName) {
    console.log(`Switching to page: ${pageName}`);
    
    // Hide all pages
    document.querySelectorAll('.page-content').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show selected page
    const targetPage = document.getElementById(`page-${pageName}`);
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const activeNavItem = document.querySelector(`[onclick*="showPage('${pageName}')"]`);
    if (activeNavItem) {
        activeNavItem.classList.add('active');
    }
    
    currentPage = pageName;
    
    // Load page-specific data
    switch(pageName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'users':
            loadUsersData();
            break;
        case 'orders':
            loadOrdersData();
            break;
        case 'services':
            loadServicesData();
            break;
        case 'api-providers':
            loadApiProvidersData();
            break;
        case 'payments':
            loadPaymentsData();
            break;
        case 'promotions':
            loadPromotionsData();
            break;
        case 'support':
            loadSupportData();
            break;
        case 'reports':
            loadReportsData();
            break;
        case 'settings':
            loadSettingsData();
            break;
    }
}

// Sidebar functions
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebar && mainContent) {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('sidebar-collapsed');
    }
}

// Header functions
function showNotifications() {
    console.log('Showing notifications...');
    // TODO: Implement notifications modal
    alert('Notifications feature coming soon!');
}

function toggleAdminDropdown() {
    console.log('Toggling admin dropdown...');
    // TODO: Implement admin dropdown
}

// Data loading functions
async function loadDashboardData() {
    try {
        console.log('Loading dashboard data...');
        
        // Load stats
        const statsResponse = await fetch(`${API_CONFIG.baseURL}/admin/stats`);
        const stats = await statsResponse.json();
        
        // Update stats cards
        updateStatsCards(stats);
        
        // Load recent orders
        const ordersResponse = await fetch(`${API_CONFIG.baseURL}/admin/orders?limit=5`);
        const ordersData = await ordersResponse.json();
        updateRecentOrdersTable(ordersData.orders || []);
        
        // Load recent users
        const usersResponse = await fetch(`${API_CONFIG.baseURL}/admin/users?limit=5`);
        const usersData = await usersResponse.json();
        updateRecentUsersTable(usersData.users || []);
        
        // Initialize charts
        initializeCharts(stats);
        
        console.log('Dashboard data loaded successfully');
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Failed to load dashboard data');
    }
}

function updateStatsCards(stats) {
    // Update Total Users
    const totalUsersElement = document.querySelector('.stat-card.stat-blue .stat-number');
    if (totalUsersElement) {
        totalUsersElement.textContent = stats.totalUsers?.toLocaleString() || '0';
    }
    
    // Update Total Orders
    const totalOrdersElement = document.querySelector('.stat-card.stat-green .stat-number');
    if (totalOrdersElement) {
        totalOrdersElement.textContent = stats.totalOrders?.toLocaleString() || '0';
    }
    
    // Update Total Revenue
    const totalRevenueElement = document.querySelector('.stat-card.stat-yellow .stat-number');
    if (totalRevenueElement) {
        totalRevenueElement.textContent = `${stats.totalRevenue?.toLocaleString() || '0'}₫`;
    }
    
    // Update API Status
    const apiStatusElement = document.querySelector('.stat-card.stat-purple .stat-number');
    if (apiStatusElement) {
        apiStatusElement.textContent = stats.apiStatus || 'Offline';
    }
}

function updateRecentOrdersTable(orders) {
    const tbody = document.querySelector('#recentOrdersTable tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (orders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No recent orders</td></tr>';
        return;
    }
    
    orders.forEach(order => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${order.id}</td>
            <td>${order.user_email || 'Unknown'}</td>
            <td>${order.service_name || 'Unknown Service'}</td>
            <td>${order.price?.toLocaleString() || '0'}₫</td>
            <td><span class="badge badge-${getStatusClass(order.status)}">${order.status || 'Unknown'}</span></td>
        `;
        tbody.appendChild(row);
    });
}

function updateRecentUsersTable(users) {
    const tbody = document.querySelector('#recentUsersTable tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No recent users</td></tr>';
        return;
    }
    
    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.email || 'Unknown'}</td>
            <td>${user.email || 'Unknown'}</td>
            <td>${user.balance?.toLocaleString() || '0'}₫</td>
            <td>${formatDate(user.created_at)}</td>
        `;
        tbody.appendChild(row);
    });
}

// Chart functions
function initializeCharts(stats) {
    try {
        console.log('Initializing charts...');
        
        // Check if Chart.js is loaded
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not loaded');
            return;
        }
        
        // Revenue Chart
        const revenueCtx = document.getElementById('revenueChart');
        if (revenueCtx) {
            charts.revenue = new Chart(revenueCtx, {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                    datasets: [{
                        label: 'Revenue (VNĐ)',
                        data: [12000000, 19000000, 15000000, 25000000],
                        borderColor: 'rgb(79, 70, 229)',
                        backgroundColor: 'rgba(79, 70, 229, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value.toLocaleString() + '₫';
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // Order Status Chart
        const orderStatusCtx = document.getElementById('orderStatusChart');
        if (orderStatusCtx) {
            charts.orderStatus = new Chart(orderStatusCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Completed', 'In Progress', 'Pending', 'Failed'],
                    datasets: [{
                        data: [45, 25, 20, 10],
                        backgroundColor: [
                            'rgb(16, 185, 129)',
                            'rgb(79, 70, 229)',
                            'rgb(245, 158, 11)',
                            'rgb(239, 68, 68)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
        
        console.log('Charts initialized successfully');
    } catch (error) {
        console.error('Error initializing charts:', error);
    }
}

// Placeholder functions for other pages
async function loadUsersData() {
    console.log('Loading users data...');
    // TODO: Implement users data loading
}

async function loadOrdersData() {
    console.log('Loading orders data...');
    // TODO: Implement orders data loading
}

async function loadServicesData() {
    console.log('Loading services data...');
    // TODO: Implement services data loading
}

async function loadApiProvidersData() {
    console.log('Loading API providers data...');
    // TODO: Implement API providers data loading
}

async function loadPaymentsData() {
    console.log('Loading payments data...');
    // TODO: Implement payments data loading
}

async function loadPromotionsData() {
    console.log('Loading promotions data...');
    // TODO: Implement promotions data loading
}

async function loadSupportData() {
    console.log('Loading support data...');
    // TODO: Implement support data loading
}

async function loadReportsData() {
    console.log('Loading reports data...');
    // TODO: Implement reports data loading
}

async function loadSettingsData() {
    console.log('Loading settings data...');
    // TODO: Implement settings data loading
}

// Utility functions
function getStatusClass(status) {
    switch(status?.toLowerCase()) {
        case 'completed':
            return 'success';
        case 'in progress':
        case 'processing':
            return 'primary';
        case 'pending':
            return 'warning';
        case 'failed':
        case 'cancelled':
            return 'danger';
        default:
            return 'secondary';
    }
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('vi-VN');
    } catch (error) {
        return 'Invalid Date';
    }
}

function showError(message) {
    console.error(message);
    // TODO: Implement error notification system
    alert(`Error: ${message}`);
}

function showSuccess(message) {
    console.log(message);
    // TODO: Implement success notification system
    alert(`Success: ${message}`);
}

// Export functions for global access
window.showPage = showPage;
window.toggleSidebar = toggleSidebar;
window.showNotifications = showNotifications;
window.toggleAdminDropdown = toggleAdminDropdown;
