# Health Monitor Application

A comprehensive web application for tracking and visualizing personal health metrics over time.

![Health Monitor Dashboard](docs/images/dashboard.png)

## Features

- **User Authentication**: Secure registration and login system
- **Health Data Tracking**: Record various health metrics including:
  - Weight
  - Blood pressure
  - Heart rate
  - Steps
  - Sleep duration
  - Water intake
  - Calorie intake
  - Stress levels
- **Data Visualization**: Interactive charts and graphs to monitor trends
- **History View**: Paginated history of all recorded health data
- **User Profiles**: Customizable user profiles with personal information
- **Personalized Settings**: Customize units (metric/imperial) and application preferences

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- SQLite (included with Python)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/health-monitor-app.git
   cd health-monitor-app
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Initialize the database:
   ```bash
   cd health_monitor_app
   python init_db.py
   ```

## Running the Application

1. Start the Flask development server:
   ```bash
   python -m flask run
   ```

2. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Development Setup

### Creating a Test User

For testing purposes, you can create a default test user:

```bash
python create_test_user.py
```

This will create a user with the following credentials:
- Username: testuser
- Password: password123

### Adding Sample Data

To populate the database with sample health data:

```bash
python add_dummy_data.py
```

## Project Structure

```
health_monitor_app/
├── app/                    # Main application package
│   ├── auth/               # Authentication blueprint
│   ├── health_data/        # Health data blueprint
│   ├── main/               # Main routes blueprint
│   ├── static/             # Static assets (CSS, JS, images)
│   ├── templates/          # HTML templates
│   ├── __init__.py         # Application factory
│   ├── extensions.py       # Flask extensions
│   ├── forms.py            # Form definitions
│   ├── models.py           # Database models
│   └── routes.py           # Main routes
├── instance/               # Instance-specific data (DB file)
├── logs/                   # Application logs
├── add_dummy_data.py       # Script to add sample data
├── create_test_user.py     # Script to create test user
├── init_db.py              # Database initialization script
└── requirements.txt        # Application dependencies
```

## API Documentation

The application provides the following main routes:

- **Authentication**:
  - `/auth/login` - User login
  - `/auth/register` - New user registration
  - `/auth/logout` - User logout

- **Dashboard**:
  - `/dashboard` - Main dashboard with health summary

- **Health Data**:
  - `/history` - View health data history
  - `/add` - Add new health data
  - `/edit/<id>` - Edit existing health data
  - `/delete/<id>` - Delete health data record
  - `/graph/<parameter>` - View graphs for specific health metrics

- **User Management**:
  - `/profile` - User profile page
  - `/settings` - User settings page

## Technologies Used

- **Backend**: Flask, SQLAlchemy, WTForms
- **Frontend**: Bootstrap 5, Chart.js
- **Database**: SQLite
- **Data Visualization**: Matplotlib, Pandas
- **Authentication**: Flask-Login

## Security Features

- Password hashing
- Form CSRF protection
- Input validation and sanitization
- User data isolation
- Authentication requirements for sensitive routes

## Screenshots

Place screenshots of the application in the `docs/images/` directory:

1. **Dashboard** - `docs/images/dashboard.png`
2. **Health Data History** - `docs/images/history.png`
3. **Data Entry Form** - `docs/images/add_data.png`
4. **Data Visualization** - `docs/images/graphs.png`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgements

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Chart.js Documentation](https://www.chartjs.org/docs/) 