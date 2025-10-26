// SMM Panel User Frontend - JavaScript

// API Configuration
const API_CONFIG = {
    baseURL: 'https://social.homemmo.store/api',
    timeout: 10000
};

// Mock Data
const MOCK_USER = {
  username: "dungnv933",
  email: null,
  phone: "0374349033",
  balance: 2.3906,
  total_spent: 48000.0004,
  tier: "Thành viên Cấp 3",
  tier_badge: "3 sao"
};

const SERVICES_DATA = [
  {
    id: 'fb-like',
    name: 'Tăng Like bài viết FB',
    icon: '👍',
    description: 'Sử dụng tốt',
    category: 'Facebook',
    rate: 500,  // Updated to match price
    min: 100,
    max: 10000
  },
  {
    id: 'fb-share',
    name: 'Tăng Share bài viết FB',
    icon: '📊',
    description: 'Sử dụng tốt',
    category: 'Facebook',
    rate: 800,  // Updated to match price
    min: 50,
    max: 5000
  },
  {
    id: 'fb-comment',
    name: 'Tăng Comment FB',
    icon: '💬',
    description: 'Sử dụng tốt',
    category: 'Facebook',
    rate: 1000,
    min: 10,
    max: 1000
  },
  {
    id: 'fb-like-comment',
    name: 'Tăng Like cho Bình luận',
    icon: '👍',
    description: 'Sử dụng tốt',
    category: 'Facebook',
    rate: 400,
    min: 10,
    max: 500
  },
  {
    id: 'fb-livestream',
    name: 'Tăng mắt LiveStream',
    icon: '👁️',
    description: 'Sử dụng tốt',
    category: 'Facebook',
    rate: 100,
    min: 100,
    max: 10000
  },
  {
    id: 'fb-follow',
    name: 'Tăng Follow FB có nhận',
    icon: '➕',
    description: 'Sử dụng tốt',
    category: 'Facebook',
    rate: 1000,
    min: 100,
    max: 5000
  },
  {
    id: 'fb-fanpage',
    name: 'Tăng Like, follow Fanpage',
    icon: '📱',
    description: 'Sử dụng tốt',
    category: 'Facebook',
    rate: 5000,
    min: 100,
    max: 10000
  },
  {
    id: 'fb-group',
    name: 'Tăng member Group',
    icon: '👥',
    description: 'Sử dụng tốt',
    category: 'Facebook',
    rate: 3000,
    min: 100,
    max: 10000
  },
  {
    id: 'fb-video',
    name: 'Tăng view Video FB',
    icon: '🎥',
    description: 'Sử dụng tốt',
    category: 'Facebook',
    rate: 300,
    min: 100,
    max: 10000
  },
  {
    id: 'fb-rating',
    name: 'Tăng đánh giá Fanpage',
    icon: '⭐',
    description: 'Sử dụng tốt',
    category: 'Facebook',
    rate: 2000,
    min: 5,
    max: 500
  },
  {
    id: 'fb-viplike',
    name: 'VipLike - Like thẳng',
    icon: '💎',
    description: 'Sử dụng tốt',
    category: 'Facebook',
    rate: 1000,
    min: 100,
    max: 5000
  },
  {
    id: 'tt-like',
    name: 'Tăng Like, tim TikTok',
    icon: '🎵',
    description: 'Sử dụng tốt',
    category: 'TikTok',
    rate: 1.5,
    min: 100,
    max: 20000
  },
  {
    id: 'tt-follow',
    name: 'Tăng Follow TikTok',
    icon: '➕',
    description: 'Sử dụng tốt',
    category: 'TikTok',
    rate: 100,
    min: 100,
    max: 5000
  },
  {
    id: 'ig-follow',
    name: 'Tăng Follow Instagram',
    icon: '📷',
    description: 'Sử dụng tốt',
    category: 'Instagram',
    rate: 80,
    min: 100,
    max: 20000
  },
  {
    id: 'yt-premium',
    name: 'Youtube Premium',
    icon: '💎',
    description: 'Có thể báo trí',
    category: 'YouTube',
    rate: 50,
    min: 1,
    max: 100
  },
  {
    id: 'yt-view',
    name: 'Tăng view, giờ xem YT',
    icon: '📺',
    description: 'Sử dụng tốt',
    category: 'YouTube',
    rate: 5,
    min: 1000,
    max: 100000
  },
  {
    id: 'shopee-like',
    name: 'Tăng Like Shopee',
    icon: '🏪',
    description: 'Sử dụng tốt',
    category: 'Shopee',
    rate: 2,
    min: 100,
    max: 10000
  }
];

// Global State
let currentBalance = MOCK_USER.balance;
let selectedService = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
  initializeApp();
});

function initializeApp() {
  // Initialize sidebar sections (first section open by default)
  const firstSection = document.querySelector('.nav-section');
  if (firstSection) {
    firstSection.classList.add('active');
  }
  
  // Setup form handlers
  setupFormHandlers();
  setupOrderForm();
  
  // Show order form by default
  showOrderForm();
}

function setupOrderForm() {
  // Setup order quantity change listener for main form
  const quantityInput = document.getElementById('order-quantity-main');
  if (quantityInput) {
    quantityInput.addEventListener('input', calculateMainOrderPrice);
  }
  
  const serviceSelect = document.getElementById('order-service-main');
  if (serviceSelect) {
    serviceSelect.addEventListener('change', function() {
      updateQuantityLimits();
      calculateMainOrderPrice();
    });
  }
  
  // Setup form submission
  const orderForm = document.getElementById('order-form-main');
  if (orderForm) {
    orderForm.addEventListener('submit', function(e) {
      e.preventDefault();
      submitMainOrder();
    });
  }
  
  // Update balance display
  updateBalanceDisplay();
}

// Sidebar Functions
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.classList.toggle('active');
}

function toggleSection(sectionId) {
  const section = document.querySelector(`#section-${sectionId}`).parentElement;
  section.classList.toggle('active');
}

function selectService(serviceId) {
  const service = SERVICES_DATA.find(s => s.id === serviceId);
  if (service) {
    selectedService = service;
    showOrderForm();
    loadServiceIntoForm(service);
  }
}

function showOrderForm() {
  document.getElementById('order-form-section').style.display = 'flex';
  document.getElementById('profile-section').style.display = 'none';
}

function closeOrderForm() {
  // Do nothing, keep form visible
}

function loadServiceIntoForm(service) {
  const serviceSelect = document.getElementById('order-service-main');
  
  // Try to find matching option
  for (let option of serviceSelect.options) {
    if (option.value === service.id) {
      serviceSelect.value = option.value;
      updateQuantityLimits();
      calculateMainOrderPrice();
      return;
    }
  }
}

// Tab Functions
function switchTab(tabName) {
  // Hide all tab panes
  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.style.display = 'none';
  });
  
  // Show selected tab pane
  document.getElementById(`${tabName}-content`).style.display = 'block';
  
  // Update active nav link
  document.querySelectorAll('.card-header-tabs .nav-link').forEach(link => {
    link.classList.remove('active');
  });
  event.target.classList.add('active');
}

function showProfileTab() {
  document.getElementById('order-form-section').style.display = 'none';
  document.getElementById('profile-section').style.display = 'flex';
  switchTab('info');
}

function showOrdersTab() {
  document.getElementById('order-form-section').style.display = 'none';
  document.getElementById('profile-section').style.display = 'flex';
  switchTab('orders');
}

function showTransactionsTab() {
  document.getElementById('order-form-section').style.display = 'none';
  document.getElementById('profile-section').style.display = 'flex';
  switchTab('transactions');
}

// Main Order Form Functions
function updateQuantityLimits() {
  const serviceSelect = document.getElementById('order-service-main');
  const selectedOption = serviceSelect.options[serviceSelect.selectedIndex];
  
  if (selectedOption && selectedOption.value) {
    const min = selectedOption.getAttribute('data-min');
    const max = selectedOption.getAttribute('data-max');
    const quantityInput = document.getElementById('order-quantity-main');
    const quantityInfo = document.getElementById('quantity-info-main');
    
    quantityInput.min = min;
    quantityInput.max = max;
    quantityInfo.innerHTML = `Số lượng tối thiểu: <strong>${parseInt(min).toLocaleString()}</strong>, tối đa: <strong>${parseInt(max).toLocaleString()}</strong>`;
  }
}

function calculateMainOrderPrice() {
  const serviceSelect = document.getElementById('order-service-main');
  const quantityInput = document.getElementById('order-quantity-main');
  const priceDisplay = document.getElementById('order-price-main');
  
  if (!serviceSelect.value || !quantityInput.value) {
    priceDisplay.textContent = '0đ';
    return;
  }
  
  const selectedOption = serviceSelect.options[serviceSelect.selectedIndex];
  const rate = parseFloat(selectedOption.getAttribute('data-rate'));
  const quantity = parseInt(quantityInput.value);
  const total = quantity * rate;
  
  priceDisplay.textContent = formatCurrency(total);
}

function submitMainOrder() {
  const serviceSelect = document.getElementById('order-service-main');
  const link = document.getElementById('order-link-main').value;
  const quantity = document.getElementById('order-quantity-main').value;
  const note = document.getElementById('order-note-main').value;
  
  if (!serviceSelect.value || !link || !quantity) {
    showToast('error', 'Vui lòng điền đầy đủ thông tin');
    return;
  }
  
  const selectedOption = serviceSelect.options[serviceSelect.selectedIndex];
  const rate = parseFloat(selectedOption.getAttribute('data-rate'));
  const total = parseInt(quantity) * rate;
  
  // Check balance
  if (total > currentBalance) {
    showToast('error', 'Số dư không đủ. Vui lòng nạp thêm tiền!');
    return;
  }
  
  // Simulate order creation
  showToast('info', 'Đang tạo đơn hàng...');
  
  setTimeout(() => {
    currentBalance -= total;
    updateBalanceDisplay();
    
    showToast('success', `Tạo đơn thành công! ID: ORD-${Math.floor(Math.random() * 10000)}`);
    
    // Reset form
    document.getElementById('order-form-main').reset();
    document.getElementById('order-price-main').textContent = '0đ';
  }, 1500);
}

function updateBalanceDisplay() {
  document.getElementById('user-balance').textContent = formatCurrency(currentBalance);
  const balanceDisplay = document.getElementById('balance-display-main');
  if (balanceDisplay) {
    balanceDisplay.textContent = formatCurrency(currentBalance);
  }
}

// Modal Functions
function showOrderModal(service) {
  if (service) {
    selectedService = service;
    
    // Set service in dropdown
    const serviceSelect = document.getElementById('order-service');
    const option = Array.from(serviceSelect.options).find(opt => 
      opt.text.includes(service.name.substring(0, 15))
    );
    if (option) {
      serviceSelect.value = option.value;
    }
    
    // Update min/max in placeholder
    const quantityInput = document.getElementById('order-quantity');
    quantityInput.placeholder = `Min: ${service.min} - Max: ${service.max.toLocaleString()}`;
    quantityInput.min = service.min;
    quantityInput.max = service.max;
  }
  
  // Update balance display
  document.getElementById('current-balance').textContent = formatCurrency(currentBalance);
  
  $('#orderModal').modal('show');
}

function showDepositModal() {
  $('#depositModal').modal('show');
}

function showPriceList() {
  showToast('info', 'Đang tải bảng giá...');
}

function showFindId() {
  showToast('info', 'Công cụ tìm ID Facebook đang được phát triển');
}

function showNotifications() {
  showToast('info', 'Bạn không có thông báo mới');
}

function showContact() {
  showToast('info', 'Vui lòng liên hệ qua Fanpage hoặc Admin');
}

// Order Functions
function calculateOrderPrice() {
  const serviceSelect = document.getElementById('order-service');
  const quantityInput = document.getElementById('order-quantity');
  const priceDisplay = document.getElementById('order-price');
  
  if (!serviceSelect.value || !quantityInput.value) {
    priceDisplay.textContent = '0đ';
    return;
  }
  
  // Get rate from mock data
  let rate = 2.5;
  if (serviceSelect.value === '1') rate = 2.5;
  if (serviceSelect.value === '2') rate = 100;
  
  const quantity = parseInt(quantityInput.value);
  const total = quantity * rate;
  
  priceDisplay.textContent = formatCurrency(total);
}

function submitOrder() {
  const serviceSelect = document.getElementById('order-service');
  const link = document.getElementById('order-link').value;
  const quantity = document.getElementById('order-quantity').value;
  const note = document.getElementById('order-note').value;
  
  if (!serviceSelect.value || !link || !quantity) {
    showToast('error', 'Vui lòng điền đầy đủ thông tin');
    return;
  }
  
  // Calculate price
  let rate = serviceSelect.value === '1' ? 2.5 : 100;
  const total = parseInt(quantity) * rate;
  
  // Check balance
  if (total > currentBalance) {
    showToast('error', 'Số dư không đủ. Vui lòng nạp thêm tiền!');
    return;
  }
  
  // Simulate order creation
  showToast('info', 'Đang tạo đơn hàng...');
  
  setTimeout(() => {
    currentBalance -= total;
    document.getElementById('user-balance').textContent = formatCurrency(currentBalance);
    
    $('#orderModal').modal('hide');
    showToast('success', `Tạo đơn thành công! ID: ORD-${Math.floor(Math.random() * 10000)}`);
    
    // Reset form
    document.getElementById('order-form').reset();
    document.getElementById('order-price').textContent = '0đ';
  }, 1500);
}

// Deposit Functions
function setAmount(amount) {
  document.getElementById('deposit-amount').value = amount;
}

function submitDeposit() {
  const method = document.getElementById('payment-method').value;
  const amount = document.getElementById('deposit-amount').value;
  
  if (!method || !amount) {
    showToast('error', 'Vui lòng chọn phương thức và nhập số tiền');
    return;
  }
  
  if (parseInt(amount) < 10000) {
    showToast('error', 'Số tiền tối thiểu là 10,000đ');
    return;
  }
  
  showToast('info', 'Đang xử lý yêu cầu nạp tiền...');
  
  setTimeout(() => {
    $('#depositModal').modal('hide');
    
    let methodName = '';
    if (method === 'vnpay') methodName = 'VNPay';
    else if (method === 'momo') methodName = 'Momo';
    else methodName = 'Chuyển khoản';
    
    showToast('success', `Yêu cầu nạp ${formatCurrency(amount)} qua ${methodName} đã được tạo. Vui lòng hoàn tất thanh toán!`);
    
    // Reset form
    document.getElementById('deposit-form').reset();
  }, 1500);
}

// Profile Functions
function setupFormHandlers() {
  const profileForm = document.getElementById('profile-form');
  if (profileForm) {
    profileForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const email = document.getElementById('user-email').value;
      const phone = document.getElementById('user-phone').value;
      const newPassword = document.getElementById('new-password').value;
      const confirmPassword = document.getElementById('confirm-password').value;
      
      if (newPassword && newPassword !== confirmPassword) {
        showToast('error', 'Mật khẩu không khớp');
        return;
      }
      
      showToast('info', 'Đang cập nhật thông tin...');
      
      setTimeout(() => {
        showToast('success', 'Cập nhật thông tin thành công!');
        
        // Update email warning if email is provided
        if (email) {
          const alertBanner = document.querySelector('.alert-banner');
          if (alertBanner) {
            alertBanner.style.display = 'none';
          }
        }
      }, 1000);
    });
  }
}

// Utility Functions
function formatCurrency(amount) {
  return new Intl.NumberFormat('vi-VN', { 
    style: 'decimal',
    minimumFractionDigits: 0,
    maximumFractionDigits: 4
  }).format(amount) + 'đ';
}

function showToast(type, message) {
  let bgClass = 'bg-info';
  let icon = 'fa-info-circle';
  
  if (type === 'success') {
    bgClass = 'bg-success';
    icon = 'fa-check-circle';
  } else if (type === 'error') {
    bgClass = 'bg-danger';
    icon = 'fa-exclamation-circle';
  } else if (type === 'warning') {
    bgClass = 'bg-warning';
    icon = 'fa-exclamation-triangle';
  }
  
  // Create toast element
  const toastId = 'toast-' + Date.now();
  const toastHTML = `
    <div class="toast ${bgClass} text-white" id="${toastId}" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
      <div class="toast-header ${bgClass} text-white">
        <i class="fas ${icon} mr-2"></i>
        <strong class="mr-auto">Thông báo</strong>
        <button type="button" class="ml-2 mb-1 close text-white" onclick="document.getElementById('${toastId}').remove()">
          <span>&times;</span>
        </button>
      </div>
      <div class="toast-body">
        ${message}
      </div>
    </div>
  `;
  
  document.body.insertAdjacentHTML('beforeend', toastHTML);
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    const toastEl = document.getElementById(toastId);
    if (toastEl) toastEl.remove();
  }, 5000);
}

function openChat() {
  showToast('info', 'Chat hỗ trợ đang được phát triển. Vui lòng liên hệ qua Fanpage!');
}

function logout() {
  if (confirm('Bạn có chắc chắn muốn đăng xuất?')) {
    showToast('info', 'Đang đăng xuất...');
    setTimeout(() => {
      showToast('success', 'Đã đăng xuất thành công!');
      // In real app, redirect to login page
    }, 1000);
  }
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function(event) {
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.querySelector('.sidebar-toggle');
  
  if (window.innerWidth <= 768 && sidebar.classList.contains('active')) {
    if (!sidebar.contains(event.target) && !toggleBtn.contains(event.target)) {
      sidebar.classList.remove('active');
    }
  }
});