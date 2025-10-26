// HOMEMMO Admin Dashboard - Demo JavaScript

// Global variables
let currentPage = 'dashboard';
let charts = {};
let dataTables = {};

// Mock Data
const MOCK_DATA = {
    stats: {
        totalUsers: 1234,
        totalOrders: 5678,
        totalRevenue: 123456789,
        apiStatus: 'Online'
    },
    recentOrders: [
        { id: 'ORD-001', user_email: 'dungnv933@gmail.com', service_name: 'Tăng Like Facebook', price: 2500, status: 'Completed' },
        { id: 'ORD-002', user_email: 'testuser@gmail.com', service_name: 'Tăng Follow TikTok', price: 50000, status: 'In Progress' },
        { id: 'ORD-003', user_email: 'user123@gmail.com', service_name: 'Tăng View YouTube', price: 25000, status: 'Completed' },
        { id: 'ORD-004', user_email: 'vipuser@gmail.com', service_name: 'Tăng Like Instagram', price: 40000, status: 'Pending' },
        { id: 'ORD-005', user_email: 'newuser@gmail.com', service_name: 'Tăng Comment Facebook', price: 15000, status: 'Failed' }
    ],
    recentUsers: [
        { email: 'dungnv933@gmail.com', balance: 2390000, created_at: '2025-10-20T10:30:00Z' },
        { email: 'testuser@gmail.com', balance: 0, created_at: '2025-10-19T15:45:00Z' },
        { email: 'user123@gmail.com', balance: 150000, created_at: '2025-10-18T09:20:00Z' },
        { email: 'vipuser@gmail.com', balance: 5000000, created_at: '2025-10-15T14:10:00Z' },
        { email: 'newuser@gmail.com', balance: 100000, created_at: '2025-10-26T08:30:00Z' }
    ],
    users: [
        { id: 1, email: 'dungnv933@gmail.com', balance: 2390000, total_spent: 150000, is_active: true, created_at: '2025-10-20T10:30:00Z' },
        { id: 2, email: 'testuser@gmail.com', balance: 0, total_spent: 50000, is_active: true, created_at: '2025-10-19T15:45:00Z' },
        { id: 3, email: 'user123@gmail.com', balance: 150000, total_spent: 25000, is_active: true, created_at: '2025-10-18T09:20:00Z' },
        { id: 4, email: 'vipuser@gmail.com', balance: 5000000, total_spent: 500000, is_active: true, created_at: '2025-10-15T14:10:00Z' },
        { id: 5, email: 'banneduser@gmail.com', balance: 0, total_spent: 0, is_active: false, created_at: '2025-10-10T12:00:00Z' }
    ],
    orders: [
        { id: 1, user_email: 'dungnv933@gmail.com', service_name: 'Tăng Like Facebook', link: 'https://fb.com/post1', quantity: 100, price: 2500, status: 'Completed', created_at: '2025-10-26T10:30:00Z' },
        { id: 2, user_email: 'testuser@gmail.com', service_name: 'Tăng Follow TikTok', link: 'https://tiktok.com/user1', quantity: 500, price: 50000, status: 'In Progress', created_at: '2025-10-26T09:15:00Z' },
        { id: 3, user_email: 'user123@gmail.com', service_name: 'Tăng View YouTube', link: 'https://youtube.com/watch?v=123', quantity: 1000, price: 25000, status: 'Completed', created_at: '2025-10-25T16:45:00Z' },
        { id: 4, user_email: 'vipuser@gmail.com', service_name: 'Tăng Like Instagram', link: 'https://instagram.com/p/abc123', quantity: 200, price: 40000, status: 'Pending', created_at: '2025-10-25T14:20:00Z' },
        { id: 5, user_email: 'newuser@gmail.com', service_name: 'Tăng Comment Facebook', link: 'https://fb.com/post2', quantity: 50, price: 15000, status: 'Failed', created_at: '2025-10-24T11:30:00Z' }
    ],
    services: [
        { id: 1, name: 'Tăng Like Facebook', category: 'Facebook', type: 'Default', rate: 25, min: 100, max: 10000, provider: 'BUMX API', status: 'Active' },
        { id: 2, name: 'Tăng Follow TikTok', category: 'TikTok', type: 'Default', rate: 100, min: 50, max: 5000, provider: 'BUMX API', status: 'Active' },
        { id: 3, name: 'Tăng View YouTube', category: 'YouTube', type: 'Default', rate: 25, min: 100, max: 50000, provider: 'BUMX API', status: 'Active' },
        { id: 4, name: 'Tăng Like Instagram', category: 'Instagram', type: 'Default', rate: 200, min: 50, max: 2000, provider: 'BUMX API', status: 'Active' },
        { id: 5, name: 'Tăng Comment Facebook', category: 'Facebook', type: 'Custom Comments', rate: 300, min: 10, max: 1000, provider: 'BUMX API', status: 'Active' }
    ],
    apiProviders: [
        { id: 1, name: 'BUMX API', url: 'https://bumx-api.com', key: '***', type: 'SMM Panel', status: 'Active', services: 156, last_sync: '2025-10-26T10:30:00Z' },
        { id: 2, name: 'Provider 2', url: 'https://provider2.com', key: '***', type: 'Custom', status: 'Inactive', services: 0, last_sync: '2025-10-20T15:45:00Z' }
    ],
    payments: [
        { id: 1, user_email: 'dungnv933@gmail.com', type: 'Deposit', amount: 1000000, method: 'VNPay', status: 'Completed', created_at: '2025-10-26T10:30:00Z' },
        { id: 2, user_email: 'testuser@gmail.com', type: 'Order', amount: 50000, method: 'Balance', status: 'Completed', created_at: '2025-10-25T15:45:00Z' },
        { id: 3, user_email: 'user123@gmail.com', type: 'Refund', amount: 25000, method: 'Balance', status: 'Pending', created_at: '2025-10-24T09:20:00Z' }
    ],
    promotions: [
        { code: 'WELCOME10', type: 'Percentage', value: 10, min_order: 0, max_uses: 100, used: 25, valid_from: '2025-10-01', valid_to: '2025-12-31', status: 'Active' },
        { code: 'SAVE20', type: 'Percentage', value: 20, min_order: 100000, max_uses: 50, used: 15, valid_from: '2025-10-15', valid_to: '2025-11-15', status: 'Active' }
    ],
    support: [
        { id: 'TICKET-001', user_email: 'dungnv933@gmail.com', subject: 'Order not completed', status: 'Open', priority: 'High', created_at: '2025-10-26T10:30:00Z' },
        { id: 'TICKET-002', user_email: 'testuser@gmail.com', subject: 'Payment issue', status: 'Closed', priority: 'Medium', created_at: '2025-10-25T15:45:00Z' }
    ]
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing HOMEMMO Admin Dashboard...');
    initializeApp();
});

function initializeApp() {
    // Show dashboard by default
    showPage('dashboard');
    
    // Load initial data
    loadDashboardData();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize modals
    initializeModals();
    
    console.log('Admin Dashboard initialized successfully');
}

function initializeModals() {
    // Close modals when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.classList.remove('show');
        }
    });
    
    // Close modals with close button
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.classList.remove('show');
            }
        });
    });
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
        page.style.display = 'none';
    });
    
    // Show selected page
    const targetPage = document.getElementById(`page-${pageName}`);
    if (targetPage) {
        targetPage.classList.add('active');
        targetPage.style.display = 'block';
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
    Swal.fire({
        title: 'Notifications',
        text: 'You have 3 new notifications',
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

function toggleAdminDropdown() {
    const dropdown = document.getElementById('adminDropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

function logout() {
    Swal.fire({
        title: 'Logout',
        text: 'Are you sure you want to logout?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Yes, logout',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            console.log('User logged out');
            // TODO: Implement logout logic
        }
    });
}

// Data loading functions
async function loadDashboardData() {
    try {
        console.log('Loading dashboard data...');
        
        // Use mock data for demo
        const stats = MOCK_DATA.stats;
        const ordersData = { orders: MOCK_DATA.recentOrders };
        const usersData = { users: MOCK_DATA.recentUsers };
        
        // Update stats cards
        updateStatsCards(stats);
        
        // Update tables
        updateRecentOrdersTable(ordersData.orders || []);
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
    const tbody = document.querySelector('#recent-orders');
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
    const tbody = document.querySelector('#recent-users');
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

// Data loading functions for other pages
async function loadUsersData() {
    try {
        console.log('Loading users data...');
        const usersData = { users: MOCK_DATA.users };
        updateUsersTable(usersData.users || []);
        console.log('Users data loaded successfully');
    } catch (error) {
        console.error('Error loading users data:', error);
        showError('Failed to load users data');
    }
}

async function loadOrdersData() {
    try {
        console.log('Loading orders data...');
        const ordersData = { orders: MOCK_DATA.orders };
        updateOrdersTable(ordersData.orders || []);
        console.log('Orders data loaded successfully');
    } catch (error) {
        console.error('Error loading orders data:', error);
        showError('Failed to load orders data');
    }
}

async function loadServicesData() {
    try {
        console.log('Loading services data...');
        const servicesData = { services: MOCK_DATA.services };
        updateServicesTable(servicesData.services || []);
        console.log('Services data loaded successfully');
    } catch (error) {
        console.error('Error loading services data:', error);
        showError('Failed to load services data');
    }
}

// Table update functions
function updateUsersTable(users) {
    const tbody = document.querySelector('#users-table');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No users found</td></tr>';
        return;
    }
    
    users.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.email || 'Unknown'}</td>
            <td>${user.balance?.toLocaleString() || '0'}₫</td>
            <td>${user.total_spent?.toLocaleString() || '0'}₫</td>
            <td><span class="badge badge-${user.is_active ? 'success' : 'danger'}">${user.is_active ? 'Active' : 'Banned'}</span></td>
            <td>${formatDate(user.created_at)}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editUser(${user.id})">Edit</button>
                <button class="btn btn-sm btn-${user.is_active ? 'danger' : 'success'}" onclick="toggleUserStatus(${user.id})">
                    ${user.is_active ? 'Ban' : 'Unban'}
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updateOrdersTable(orders) {
    const tbody = document.querySelector('#orders-table');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (orders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No orders found</td></tr>';
        return;
    }
    
    orders.forEach(order => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${order.id}</td>
            <td>${order.user_email || 'Unknown'}</td>
            <td>${order.service_name || 'Unknown Service'}</td>
            <td><a href="${order.link}" target="_blank" class="text-truncate" style="max-width: 100px; display: inline-block;">${order.link}</a></td>
            <td>${order.quantity || 0}</td>
            <td>${order.price?.toLocaleString() || '0'}₫</td>
            <td><span class="badge badge-${getStatusClass(order.status)}">${order.status || 'Unknown'}</span></td>
            <td>${formatDate(order.created_at)}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="viewOrder(${order.id})">View</button>
                <button class="btn btn-sm btn-${order.status === 'Pending' ? 'success' : 'warning'}" onclick="updateOrderStatus(${order.id})">
                    ${order.status === 'Pending' ? 'Process' : 'Update'}
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updateServicesTable(services) {
    const tbody = document.querySelector('#services-table');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (services.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No services found</td></tr>';
        return;
    }
    
    services.forEach(service => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${service.id}</td>
            <td>${service.name || 'Unknown Service'}</td>
            <td><span class="badge badge-primary">${service.category || 'Unknown'}</span></td>
            <td>${service.type || 'Default'}</td>
            <td>${service.rate?.toLocaleString() || '0'}₫</td>
            <td>${service.min || 0} - ${service.max || 0}</td>
            <td>${service.provider || 'Unknown'}</td>
            <td><span class="badge badge-${service.status === 'Active' ? 'success' : 'danger'}">${service.status || 'Unknown'}</span></td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editService(${service.id})">Edit</button>
                <button class="btn btn-sm btn-${service.status === 'Active' ? 'danger' : 'success'}" onclick="toggleServiceStatus(${service.id})">
                    ${service.status === 'Active' ? 'Deactivate' : 'Activate'}
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Placeholder functions for other pages
async function loadApiProvidersData() {
    try {
        console.log('Loading API providers data...');
        const providersData = { providers: MOCK_DATA.apiProviders };
        updateApiProvidersTable(providersData.providers || []);
        console.log('API providers data loaded successfully');
    } catch (error) {
        console.error('Error loading API providers data:', error);
        showError('Failed to load API providers data');
    }
}

async function loadPaymentsData() {
    try {
        console.log('Loading payments data...');
        const paymentsData = { payments: MOCK_DATA.payments };
        updatePaymentsTable(paymentsData.payments || []);
        console.log('Payments data loaded successfully');
    } catch (error) {
        console.error('Error loading payments data:', error);
        showError('Failed to load payments data');
    }
}

async function loadPromotionsData() {
    try {
        console.log('Loading promotions data...');
        const promotionsData = { promotions: MOCK_DATA.promotions };
        updatePromotionsTable(promotionsData.promotions || []);
        console.log('Promotions data loaded successfully');
    } catch (error) {
        console.error('Error loading promotions data:', error);
        showError('Failed to load promotions data');
    }
}

async function loadSupportData() {
    try {
        console.log('Loading support data...');
        const supportData = { tickets: MOCK_DATA.support };
        updateSupportTable(supportData.tickets || []);
        console.log('Support data loaded successfully');
    } catch (error) {
        console.error('Error loading support data:', error);
        showError('Failed to load support data');
    }
}

async function loadReportsData() {
    try {
        console.log('Loading reports data...');
        // Reports page doesn't need table data, just show success
        console.log('Reports data loaded successfully');
    } catch (error) {
        console.error('Error loading reports data:', error);
        showError('Failed to load reports data');
    }
}

async function loadSettingsData() {
    try {
        console.log('Loading settings data...');
        // Settings page doesn't need table data, just show success
        console.log('Settings data loaded successfully');
    } catch (error) {
        console.error('Error loading settings data:', error);
        showError('Failed to load settings data');
    }
}

// Action functions
function editUser(userId) {
    console.log(`Editing user: ${userId}`);
    Swal.fire({
        title: 'Edit User',
        text: `Edit user ${userId} - Feature coming soon!`,
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

function toggleUserStatus(userId) {
    console.log(`Toggling user status: ${userId}`);
    Swal.fire({
        title: 'Toggle User Status',
        text: `Toggle user status ${userId} - Feature coming soon!`,
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

function viewOrder(orderId) {
    console.log(`Viewing order: ${orderId}`);
    Swal.fire({
        title: 'View Order',
        text: `View order ${orderId} - Feature coming soon!`,
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

function updateOrderStatus(orderId) {
    console.log(`Updating order status: ${orderId}`);
    Swal.fire({
        title: 'Update Order Status',
        text: `Update order status ${orderId} - Feature coming soon!`,
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

function editService(serviceId) {
    console.log(`Editing service: ${serviceId}`);
    Swal.fire({
        title: 'Edit Service',
        text: `Edit service ${serviceId} - Feature coming soon!`,
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

function toggleServiceStatus(serviceId) {
    console.log(`Toggling service status: ${serviceId}`);
    Swal.fire({
        title: 'Toggle Service Status',
        text: `Toggle service status ${serviceId} - Feature coming soon!`,
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

// Modal functions
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
    }
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
    Swal.fire({
        title: 'Error',
        text: message,
        icon: 'error',
        confirmButtonText: 'OK'
    });
}

function showSuccess(message) {
    console.log(message);
    Swal.fire({
        title: 'Success',
        text: message,
        icon: 'success',
        confirmButtonText: 'OK'
    });
}

// Add User functions
function addUser() {
    console.log('Opening Add User modal...');
    showModal('addUserModal');
}

function submitAddUser() {
    const username = document.getElementById('addUsername').value;
    const email = document.getElementById('addUserEmail').value;
    const password = document.getElementById('addUserPassword').value;
    const balance = document.getElementById('addInitialBalance').value;
    
    if (!username || !email || !password) {
        showError('Please fill in all required fields');
        return;
    }
    
    console.log('Adding user:', { username, email, balance });
    
    // Simulate API call
    setTimeout(() => {
        showSuccess('User added successfully!');
        hideModal('addUserModal');
        
        // Clear form
        document.getElementById('addUsername').value = '';
        document.getElementById('addUserEmail').value = '';
        document.getElementById('addUserPassword').value = '';
        document.getElementById('addInitialBalance').value = '0';
        
        // Refresh users table
        loadUsersData();
    }, 1000);
}

function exportUsers() {
    console.log('Exporting users...');
    showSuccess('Exporting users to CSV...');
    // TODO: Implement CSV export
}

function filterUsers() {
    const searchTerm = document.getElementById('user-search')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('user-status-filter')?.value || 'all';
    
    console.log('Filtering users:', { searchTerm, statusFilter });
    
    // Filter users based on search and status
    let filteredUsers = MOCK_DATA.users;
    
    if (searchTerm) {
        filteredUsers = filteredUsers.filter(user => 
            user.email.toLowerCase().includes(searchTerm)
        );
    }
    
    if (statusFilter !== 'all') {
        const isActive = statusFilter === 'active';
        filteredUsers = filteredUsers.filter(user => user.is_active === isActive);
    }
    
    updateUsersTable(filteredUsers);
}

// Add Service functions
function addService() {
    console.log('Opening Add Service modal...');
    showModal('addServiceModal');
}

function submitAddService() {
    const serviceName = document.getElementById('addServiceName').value;
    const serviceCategory = document.getElementById('addServiceCategory').value;
    const serviceType = document.getElementById('addServiceType').value;
    const serviceAPIProvider = document.getElementById('addServiceAPIProvider').value;
    const serviceRate = document.getElementById('addServiceRate').value;
    const serviceMin = document.getElementById('addServiceMin').value;
    const serviceMax = document.getElementById('addServiceMax').value;
    const serviceDescription = document.getElementById('addServiceDescription').value;
    const serviceActive = document.getElementById('addServiceActive').checked;
    
    if (!serviceName || !serviceCategory || !serviceRate || !serviceMin || !serviceMax) {
        showError('Please fill in all required fields');
        return;
    }
    
    console.log('Adding service:', { 
        serviceName, serviceCategory, serviceType, serviceAPIProvider, 
        serviceRate, serviceMin, serviceMax, serviceDescription, serviceActive 
    });
    
    // Simulate API call
    setTimeout(() => {
        showSuccess('Service added successfully!');
        hideModal('addServiceModal');
        
        // Clear form
        document.getElementById('addServiceName').value = '';
        document.getElementById('addServiceCategory').value = '';
        document.getElementById('addServiceType').value = '';
        document.getElementById('addServiceAPIProvider').value = '';
        document.getElementById('addServiceRate').value = '';
        document.getElementById('addServiceMin').value = '';
        document.getElementById('addServiceMax').value = '';
        document.getElementById('addServiceDescription').value = '';
        document.getElementById('addServiceActive').checked = true;
        
        // Refresh services table
        loadServicesData();
    }, 1000);
}

// Other service functions
function showImportModal() {
    console.log('Opening Import Services modal...');
    showModal('importServicesModal');
}

function syncAllServices() {
    console.log('Syncing all services...');
    showSuccess('Syncing all services...');
    // TODO: Implement sync all services
}

function filterServices() {
    const searchTerm = document.getElementById('service-search')?.value.toLowerCase() || '';
    const categoryFilter = document.getElementById('service-category-filter')?.value || 'all';
    
    console.log('Filtering services:', { searchTerm, categoryFilter });
    
    // Filter services based on search and category
    let filteredServices = MOCK_DATA.services;
    
    if (searchTerm) {
        filteredServices = filteredServices.filter(service => 
            service.name.toLowerCase().includes(searchTerm)
        );
    }
    
    if (categoryFilter !== 'all') {
        filteredServices = filteredServices.filter(service => 
            service.category.toLowerCase() === categoryFilter.toLowerCase()
        );
    }
    
    updateServicesTable(filteredServices);
}

// Table update functions for other pages
function updateApiProvidersTable(providers) {
    const tbody = document.querySelector('#providers-table');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (providers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No API providers found</td></tr>';
        return;
    }
    
    providers.forEach(provider => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${provider.id}</td>
            <td>${provider.name || 'Unknown'}</td>
            <td><a href="${provider.url}" target="_blank" class="text-truncate" style="max-width: 150px; display: inline-block;">${provider.url}</a></td>
            <td>${provider.key || '***'}</td>
            <td><span class="badge badge-primary">${provider.type || 'Unknown'}</span></td>
            <td><span class="badge badge-${provider.status === 'Active' ? 'success' : 'danger'}">${provider.status || 'Unknown'}</span></td>
            <td>${provider.services || 0}</td>
            <td>${formatDate(provider.last_sync)}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editProvider(${provider.id})">Edit</button>
                <button class="btn btn-sm btn-${provider.status === 'Active' ? 'danger' : 'success'}" onclick="toggleProviderStatus(${provider.id})">
                    ${provider.status === 'Active' ? 'Deactivate' : 'Activate'}
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updatePaymentsTable(payments) {
    const tbody = document.querySelector('#transactions-table');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (payments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No transactions found</td></tr>';
        return;
    }
    
    payments.forEach(payment => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${payment.id}</td>
            <td>${payment.user_email || 'Unknown'}</td>
            <td><span class="badge badge-${getPaymentTypeClass(payment.type)}">${payment.type || 'Unknown'}</span></td>
            <td>${payment.amount?.toLocaleString() || '0'}₫</td>
            <td>${payment.method || 'Unknown'}</td>
            <td><span class="badge badge-${getStatusClass(payment.status)}">${payment.status || 'Unknown'}</span></td>
            <td>${formatDate(payment.created_at)}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="viewTransaction(${payment.id})">View</button>
                <button class="btn btn-sm btn-${payment.status === 'Pending' ? 'success' : 'warning'}" onclick="updateTransactionStatus(${payment.id})">
                    ${payment.status === 'Pending' ? 'Process' : 'Update'}
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updatePromotionsTable(promotions) {
    const tbody = document.querySelector('#discounts-table');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (promotions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center text-muted">No discount codes found</td></tr>';
        return;
    }
    
    promotions.forEach(promo => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${promo.code || 'Unknown'}</strong></td>
            <td><span class="badge badge-primary">${promo.type || 'Unknown'}</span></td>
            <td>${promo.value || 0}${promo.type === 'Percentage' ? '%' : '₫'}</td>
            <td>${promo.min_order?.toLocaleString() || '0'}₫</td>
            <td>${promo.max_uses || 'Unlimited'}</td>
            <td>${promo.used || 0}</td>
            <td>${formatDate(promo.valid_from)}</td>
            <td>${formatDate(promo.valid_to)}</td>
            <td><span class="badge badge-${promo.status === 'Active' ? 'success' : 'danger'}">${promo.status || 'Unknown'}</span></td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editPromotion('${promo.code}')">Edit</button>
                <button class="btn btn-sm btn-${promo.status === 'Active' ? 'danger' : 'success'}" onclick="togglePromotionStatus('${promo.code}')">
                    ${promo.status === 'Active' ? 'Deactivate' : 'Activate'}
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updateSupportTable(tickets) {
    const tbody = document.querySelector('#supportTicketsTable tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (tickets.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No support tickets found</td></tr>';
        return;
    }
    
    tickets.forEach(ticket => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${ticket.id || 'Unknown'}</td>
            <td>${ticket.user_email || 'Unknown'}</td>
            <td>${ticket.subject || 'No subject'}</td>
            <td><span class="badge badge-${getTicketStatusClass(ticket.status)}">${ticket.status || 'Unknown'}</span></td>
            <td><span class="badge badge-${getPriorityClass(ticket.priority)}">${ticket.priority || 'Unknown'}</span></td>
            <td>${formatDate(ticket.created_at)}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="viewTicket('${ticket.id}')">View</button>
                <button class="btn btn-sm btn-${ticket.status === 'Open' ? 'success' : 'warning'}" onclick="updateTicketStatus('${ticket.id}')">
                    ${ticket.status === 'Open' ? 'Close' : 'Reopen'}
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Helper functions for status classes
function getPaymentTypeClass(type) {
    switch(type?.toLowerCase()) {
        case 'deposit':
            return 'success';
        case 'order':
            return 'primary';
        case 'refund':
            return 'warning';
        default:
            return 'secondary';
    }
}

function getTicketStatusClass(status) {
    switch(status?.toLowerCase()) {
        case 'open':
            return 'warning';
        case 'closed':
            return 'success';
        case 'pending':
            return 'primary';
        default:
            return 'secondary';
    }
}

function getPriorityClass(priority) {
    switch(priority?.toLowerCase()) {
        case 'high':
            return 'danger';
        case 'medium':
            return 'warning';
        case 'low':
            return 'success';
        default:
            return 'secondary';
    }
}

// Export functions for global access
window.showPage = showPage;
window.toggleSidebar = toggleSidebar;
window.showNotifications = showNotifications;
window.toggleAdminDropdown = toggleAdminDropdown;
window.logout = logout;
window.editUser = editUser;
window.toggleUserStatus = toggleUserStatus;
window.viewOrder = viewOrder;
window.updateOrderStatus = updateOrderStatus;
window.editService = editService;
window.toggleServiceStatus = toggleServiceStatus;
window.showModal = showModal;
window.hideModal = hideModal;
window.addUser = addUser;
window.submitAddUser = submitAddUser;
window.exportUsers = exportUsers;
window.filterUsers = filterUsers;
window.addService = addService;
window.submitAddService = submitAddService;
window.showImportModal = showImportModal;
window.syncAllServices = syncAllServices;
window.filterServices = filterServices;

// Action functions for other pages
function addProvider() {
    console.log('Opening Add Provider modal...');
    showModal('addApiProviderModal');
}

function addDiscountCode() {
    console.log('Opening Add Discount Code modal...');
    showModal('addDiscountCodeModal');
}

function editProvider(providerId) {
    console.log(`Editing provider: ${providerId}`);
    Swal.fire({
        title: 'Edit Provider',
        text: `Edit provider ${providerId} - Feature coming soon!`,
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

function toggleProviderStatus(providerId) {
    console.log(`Toggling provider status: ${providerId}`);
    Swal.fire({
        title: 'Toggle Provider Status',
        text: `Toggle provider status ${providerId} - Feature coming soon!`,
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

function viewTransaction(transactionId) {
    console.log(`Viewing transaction: ${transactionId}`);
    Swal.fire({
        title: 'View Transaction',
        text: `View transaction ${transactionId} - Feature coming soon!`,
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

function updateTransactionStatus(transactionId) {
    console.log(`Updating transaction status: ${transactionId}`);
    Swal.fire({
        title: 'Update Transaction Status',
        text: `Update transaction status ${transactionId} - Feature coming soon!`,
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

function editPromotion(promoCode) {
    console.log(`Editing promotion: ${promoCode}`);
    Swal.fire({
        title: 'Edit Promotion',
        text: `Edit promotion ${promoCode} - Feature coming soon!`,
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

function togglePromotionStatus(promoCode) {
    console.log(`Toggling promotion status: ${promoCode}`);
    Swal.fire({
        title: 'Toggle Promotion Status',
        text: `Toggle promotion status ${promoCode} - Feature coming soon!`,
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

function viewTicket(ticketId) {
    console.log(`Viewing ticket: ${ticketId}`);
    Swal.fire({
        title: 'View Ticket',
        text: `View ticket ${ticketId} - Feature coming soon!`,
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

function updateTicketStatus(ticketId) {
    console.log(`Updating ticket status: ${ticketId}`);
    Swal.fire({
        title: 'Update Ticket Status',
        text: `Update ticket status ${ticketId} - Feature coming soon!`,
        icon: 'info',
        confirmButtonText: 'OK'
    });
}

// Export additional functions
window.addProvider = addProvider;
window.addDiscountCode = addDiscountCode;
window.editProvider = editProvider;
window.toggleProviderStatus = toggleProviderStatus;
window.viewTransaction = viewTransaction;
window.updateTransactionStatus = updateTransactionStatus;
window.editPromotion = editPromotion;
window.togglePromotionStatus = togglePromotionStatus;
window.viewTicket = viewTicket;
window.updateTicketStatus = updateTicketStatus;