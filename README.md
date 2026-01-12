# 💰 Money Tracker - Personal Finance Management System

A modern, responsive web application built with Django for tracking personal income and expenses with beautiful analytics and insights.

## 🚀 Features

### Core Functionality
- **User Authentication**: Secure login/logout system
- **Transaction Management**: Add, view, and filter income/expense transactions
- **Real-time Dashboard**: Overview of financial status with summary cards
- **Advanced Analytics**: Monthly trends, category breakdowns, and interactive charts
- **Responsive Design**: Optimized for mobile, tablet, and desktop devices

### Key Highlights
- **Modern UI/UX**: Clean, professional interface with glassmorphism effects
- **Interactive Charts**: Daily trends, monthly comparisons, and category distributions
- **Smart Filtering**: Date-based transaction filtering with pagination
- **Mobile-First**: Touch-friendly design with responsive layouts
- **Data Visualization**: Chart.js integration for beautiful financial insights

## 🏗️ Project Structure

```
money_log/
├── money_log/                 # Main project directory
│   ├── settings.py           # Django settings and configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI configuration
├── accounts/                 # User management app
│   ├── models.py            # Custom User and UserProfile models
│   ├── admin.py             # Admin interface configuration
│   └── views.py             # Authentication views
├── dashboard/                # Main dashboard app
│   ├── views.py             # Dashboard and analytics views
│   ├── urls.py              # Dashboard URL patterns
│   └── templates/           # Dashboard templates
├── ledger/                   # Transaction management app
│   ├── models.py            # Transaction model
│   ├── forms.py             # Transaction forms
│   ├── views.py             # Transaction CRUD views
│   ├── admin.py             # Transaction admin interface
│   └── templates/           # Transaction templates
└── templates/                # Global templates
    ├── accounts/            # Authentication templates
    ├── dashboard/           # Dashboard templates
    └── ledger/              # Transaction templates
```

## 🔧 Technology Stack

### Backend
- **Django 5.2.10**: Web framework
- **SQLite**: Database (development)
- **Python 3.x**: Programming language

### Frontend
- **HTML5/CSS3**: Structure and styling
- **JavaScript**: Interactive functionality
- **Chart.js**: Data visualization
- **Inter Font**: Modern typography

### Key Libraries
- **django.contrib.humanize**: Number formatting with commas
- **python-dotenv**: Environment variable management

## 📊 Database Schema

### User Model (Custom)
```python
class User(AbstractUser):
    # Extends Django's built-in User model
    # Fields: username, email, password, first_name, last_name, etc.
```

### Transaction Model
```python
class Transaction(models.Model):
    user = ForeignKey(User)                    # Transaction owner
    transaction_type = CharField               # 'INCOME' or 'EXPENSE'
    amount = DecimalField(max_digits=12)       # Transaction amount
    category = CharField(max_length=50)        # Transaction category
    description = CharField(max_length=200)    # Optional description
    date = DateField()                         # Transaction date
    created_at = DateTimeField(auto_now_add=True)  # Creation timestamp
```

### UserProfile Model
```python
class UserProfile(models.Model):
    user = OneToOneField(User)
    phone_plain = CharField                    # Phone number
    address_plain = TextField                  # Address
    # Includes encrypted fields for sensitive data
```

## 🔄 Application Workflow

### 1. User Authentication Flow
```
User Registration/Login → Authentication → Dashboard Access
```

### 2. Transaction Management Flow
```
Add Transaction → Form Validation → Database Storage → Dashboard Update
```

### 3. Analytics Generation Flow
```
Transaction Data → Date Filtering → Aggregation → Chart Generation → Display
```

### 4. Dashboard Data Flow
```
User Login → Fetch Transactions → Calculate Summaries → Render Dashboard
```

## 🎯 Core Features Breakdown

### Dashboard (`dashboard/views.py`)
- **Summary Cards**: Total income, expenses, and balance
- **Transaction Filtering**: Date-based filtering with pagination
- **Recent Transactions**: Paginated transaction list
- **AJAX Pagination**: Smooth page transitions

### Analytics (`dashboard/views.py - analytics`)
- **Month Navigation**: Previous/next month browsing
- **Daily Trends**: Line charts showing daily income/expense patterns
- **Monthly Overview**: Bar charts for yearly monthly comparison
- **Category Analysis**: Pie charts for income/expense distribution
- **Data Aggregation**: Complex database queries for insights

### Transaction Management (`ledger/views.py`)
- **Add Transactions**: Form-based transaction creation
- **Form Validation**: Server-side validation and error handling
- **User Association**: Automatic user linking for transactions

## 🎨 UI/UX Design Philosophy

### Design Principles
- **Mobile-First**: Responsive design starting from mobile
- **Modern Aesthetics**: Clean, professional appearance
- **User-Friendly**: Intuitive navigation and interactions
- **Accessibility**: Proper labels, focus states, and semantic HTML

### Color Scheme
- **Primary**: Blue gradient (#4facfe to #00f2fe)
- **Success**: Green (#2ecc71) for income
- **Danger**: Red (#e74c3c) for expenses
- **Neutral**: Gray tones for text and backgrounds

### Responsive Breakpoints
- **Mobile**: ≤ 480px (Ultra-compact layout)
- **Tablet**: ≤ 768px (Compact layout)
- **Desktop**: ≥ 1024px (Spacious layout)
- **Large Desktop**: ≥ 1440px (Ultra-wide support)

## 📱 Mobile Optimization

### Key Mobile Features
- **Touch-Friendly**: Large buttons and input fields
- **iOS Compatibility**: 16px font size prevents zoom
- **Horizontal Scrolling**: Tables scroll smoothly on mobile
- **Stacked Layouts**: Forms and navigation stack vertically
- **Optimized Charts**: Responsive chart sizing

## 📈 Analytics Features

### Chart Types
1. **Daily Trend Chart**: Line chart showing daily income/expense
2. **Monthly Bar Chart**: Yearly overview with monthly comparisons
3. **Category Pie Charts**: Separate charts for income/expense categories

### Data Insights
- **Financial Summaries**: Overall and monthly totals
- **Category Breakdowns**: Spending patterns by category
- **Trend Analysis**: Daily and monthly financial trends
- **Balance Tracking**: Real-time balance calculations

## 🔐 Security Features

### Authentication
- **Login Required**: All views protected with `@login_required`
- **User Isolation**: Users only see their own transactions
- **CSRF Protection**: Forms protected against CSRF attacks

### Data Protection
- **Encrypted Fields**: Sensitive user data encryption support
- **Secure Sessions**: Django's built-in session security
- **SQL Injection Prevention**: ORM-based database queries

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Django 5.2.10
- SQLite (included with Python)

### Installation Steps
```bash
# Clone the repository
git clone <repository-url>
cd money_log

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install django python-dotenv

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Environment Variables
Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
ENABLE_ENCRYPTION=false
```

## 🔧 Configuration

### Django Settings
- **DEBUG**: Set to `False` in production
- **ALLOWED_HOSTS**: Configure for production domain
- **DATABASES**: Switch to PostgreSQL/MySQL for production
- **STATIC_FILES**: Configure static file serving

### Admin Interface
Access Django admin at `/admin/` to:
- Manage users and transactions
- View database records
- Perform administrative tasks

## 📊 Usage Examples

### Adding a Transaction
1. Navigate to "Add Transaction"
2. Select Income or Expense
3. Enter amount, category, description
4. Choose date
5. Save transaction

### Viewing Analytics
1. Click "Analytics" from dashboard
2. Use month navigation to browse different periods
3. View charts and category breakdowns
4. Analyze spending patterns

### Filtering Transactions
1. Use date filters on dashboard
2. Set start and end dates
3. Click "Filter" to apply
4. Use "Reset" to clear filters

## 🔮 Future Enhancements

### Planned Features
- **SMS Integration**: Auto-parse bank SMS notifications
- **Receipt Scanning**: OCR-based expense entry
- **Recurring Transactions**: Automated monthly bills
- **Budget Planning**: Set and track budgets
- **Export Features**: PDF/Excel export capabilities
- **Multi-currency Support**: Handle different currencies
- **Bank API Integration**: Direct bank account connection

### Technical Improvements
- **API Development**: REST API for mobile apps
- **Real-time Updates**: WebSocket integration
- **Advanced Analytics**: Machine learning insights
- **Performance Optimization**: Database indexing and caching

## 🤝 Contributing

### Development Guidelines
1. Follow Django best practices
2. Maintain responsive design principles
3. Write clean, documented code
4. Test on multiple devices
5. Ensure security best practices

### Code Style
- Use Django conventions
- Follow PEP 8 for Python code
- Use semantic HTML and CSS
- Comment complex logic

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

Developed with ❤️ for personal finance management.

---

**Money Tracker** - Take control of your finances with beautiful, insightful analytics! 💰📊