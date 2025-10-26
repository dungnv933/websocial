# SMM Panel Backend API

A complete FastAPI backend for Social Media Marketing Panel with tier system, referral program, and BUMX API integration.

## Features

- **User Management**: Registration, authentication, tier system
- **Tier System**: 4 levels with automatic discount calculation
- **Referral Program**: 5% commission for referrals
- **Order Management**: Create orders with BUMX API integration
- **Payment System**: Deposit handling with Sepay webhook
- **Admin Panel**: Complete admin API for management
- **Telegram Notifications**: Real-time notifications
- **Background Tasks**: Order status synchronization

## Tech Stack

- **Python 3.6.8** (CentOS 7 compatible)
- **FastAPI 0.68.0**
- **SQLAlchemy 1.3.24** (ORM)
- **PostgreSQL** (Database)
- **JWT Authentication**
- **Pydantic** (Data validation)

## Installation

1. **Clone repository**
```bash
cd /home/homemmo/websocial/backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment**
```bash
cp env.example .env
# Edit .env with your configuration
```

4. **Setup database**
```bash
# Create PostgreSQL database
createdb smmpanel

# Run migrations (if using Alembic)
alembic upgrade head
```

5. **Run application**
```bash
python -m app.main
# or
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost/smmpanel
SECRET_KEY=your-secret-key-here
BUMX_API_KEY=your-bumx-api-key
BUMX_API_URL=https://bumx.vn/api/v1
SEPAY_SECRET=your-sepay-secret
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-chat-id
DEBUG=True
CORS_ORIGINS=http://localhost:3000,https://social.homemmo.store
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info

### User
- `GET /api/user/tier` - Get tier information
- `GET /api/user/balance` - Get balance
- `GET /api/user/referrals` - Get referrals
- `GET /api/user/orders` - Get user orders
- `GET /api/user/transactions` - Get transactions

### Services
- `GET /api/services` - Get available services
- `GET /api/services/{id}` - Get specific service

### Orders
- `POST /api/orders` - Create new order
- `GET /api/orders/{id}` - Get specific order
- `GET /api/orders` - Get user orders

### Payment
- `POST /api/payment/deposit` - Create deposit request
- `POST /api/payment/sepay/webhook` - Sepay webhook

### Admin
- `GET /api/admin/users` - Get all users
- `PUT /api/admin/users/{id}/balance` - Update user balance
- `PUT /api/admin/users/{id}/ban` - Ban/unban user
- `GET /api/admin/orders` - Get all orders
- `PUT /api/admin/orders/{id}/status` - Update order status
- `GET /api/admin/services` - Get all services
- `POST /api/admin/services` - Create service
- `PUT /api/admin/services/{id}` - Update service
- `GET /api/admin/deposits` - Get all deposits
- `PUT /api/admin/deposits/{id}/approve` - Approve deposit

## Tier System

| Tier | Name | Total Spent | Discount |
|------|------|-------------|----------|
| 1 | Cấp 1 | < 5,000,000 VND | 0% |
| 2 | Cấp 2 | 5M - 20M VND | 3% |
| 3 | Cấp 3 | 20M - 50M VND | 5% |
| 4 | VIP | ≥ 50M VND | 10% |

## Referral System

- Users get unique referral codes
- 5% commission on referred user spending
- Automatic balance updates

## Database Models

### User
- Basic user information
- Balance and spending tracking
- Tier system fields
- Referral system fields

### Service
- Service details and pricing
- Provider integration
- Category classification

### Order
- Order details and status
- BUMX API integration
- User and service relationships

### Transaction
- All financial transactions
- Balance tracking
- Transaction history

### Deposit
- Deposit requests
- Bank transfer handling
- Status tracking

## External Integrations

### BUMX API
- Order creation
- Status synchronization
- Service management

### Sepay
- Payment processing
- Webhook handling
- Bank transfer integration

### Telegram Bot
- Order notifications
- Deposit confirmations
- Status updates

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
isort app/
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## Production Deployment

1. **Setup PostgreSQL**
2. **Configure environment variables**
3. **Run database migrations**
4. **Start with Gunicorn**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## License

Private - All rights reserved

