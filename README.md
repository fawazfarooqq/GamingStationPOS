# GamingStation POS

GamingStation POS is a full-stack Point of Sale and business management system I built for my uncle's gaming center located at Podium Mall, Tolichowki, Hyderabad.

The system is designed to be used as the shop's day-to-day operational software rather than as a simple demonstration project. It centralizes gaming-session management, automated billing, customer records, inventory, product sales, payments, expenses, and business reporting into a single dashboard.

## What It Handles

- Gaming station management
- Real-time gaming session tracking
- Automatic session billing
- Customer registration and CRM
- Food and beverage/product sales
- Shopping cart and POS checkout
- Cash, UPI and card payment recording
- Inventory and stock management
- Low-stock alerts
- Expense tracking
- Revenue and business analytics
- Session and sales history
- CSV transaction exports
- Configurable station pricing
- Persistent SQLite database
- REST API backend
- Responsive management dashboard

## Purpose

The goal of GamingStation POS is to replace manual tracking and separate spreadsheets with a centralized system that can be used by the gaming center to manage its daily operations.

I designed and developed the system around the actual workflow of the business, including timed gaming sessions, station availability, customer information, automatic billing, product sales and operational reporting.

## Technology

- Python
- Flask
- SQLite
- REST API
- JavaScript
- Tailwind CSS
- Chart.js
- Docker
- Pytest

## Architecture

The application uses a Flask backend with SQLite for persistent business data and a JavaScript-based web dashboard for the POS and management interface.

```text
GamingStation POS
│
├── POS Dashboard
│   ├── Gaming Sessions
│   ├── Product Sales
│   └── Checkout
│
├── Business Management
│   ├── Customers
│   ├── Inventory
│   ├── Expenses
│   └── Reports
│
├── Backend
│   ├── REST API
│   ├── Billing Logic
│   └── Database Layer
│
└── Database
    ├── Sessions
    ├── Customers
    ├── Products
    ├── Sales
    └── Expenses
