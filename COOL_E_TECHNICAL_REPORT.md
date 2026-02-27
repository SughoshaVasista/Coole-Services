# COOL-E: Technical Specification & Architecture Report
**Project Name:** Cool-E (Urban Service Marketplace)
**Developed for:** Final Judges Review
**Date:** February 14, 2026

---

## 📋 1. Executive Summary
Cool-E is a high-performance, on-demand service marketplace designed to automate the connection between skilled service providers (Partners) and end-customers. The platform emphasizes a "Frictionless Economy" by providing real-time availability tracking, transparent commission-based transactions, and a robust UPI-first payment ecosystem.

---

## 🛠 2. Core Technology Stack

### 🔹 Backend (The Brain)
- **Framework:** Django 6.0.2 (Advanced MVT Architecture)
- **Language:** Python 3.12+
- **Security:** CSRF Protection, Password Hashing (PBKDF2), and SQL Injection prevention via Django ORM.

### 🔹 Database (The Heart)
- **Type:** Relational Database Management System (RDBMS)
- **Choice:** **MySQL**
- **Capabilities:** Managed via PyMySQL; handles complex relations between User Profiles, Service Providers, Bookings, and Financial Transactions.

### 🔹 Frontend (The Face)
- **Design Philosophy:** **Glassmorphism** (Modern UI with frosted glass effects and vibrant gradients).
- **Core Tech:** HTML5, CSS3 (Vanilla), and ES6+ JavaScript.
- **Typography:** Google Fonts (Outfit & Inter) for a premium, mobile-first aesthetic.

---

## 📂 3. Modular Application Structure
The codebase is divided into specialized Django apps for maximum scalability:

1.  **`home` Module:**
    *   Authentication (Login/Signup/Logout).
    *   Dynamic Landing Page & Service Discovery.
    *   Phone-based Password Recovery System.
2.  **`services` Module (Core Logic):**
    *   Service Category Management.
    *   Service Provider Registry & Advanced Search.
    *   **Availability State Machine:** Manages `Available`, `Busy`, `Verifying`, and `Offline` states.
3.  **`orders` Module:**
    *   User Order History & Tracking.
    *   Automated PDF-ready Digital Receipt Generation.
4.  **`profiles` Module:**
    *   Extended User Profiles (Phone, Address, Verification Status).
    *   Automatic Profile Creation via Django Signals.

---

## 📚 4. Libraries & Dependencies
| Library | Version/Source | Purpose |
| :--- | :--- | :--- |
| **Django** | 6.0.2 | Main Web Framework |
| **PyMySQL** | 1.0.2+ | Interface for MySQL Database |
| **Pillow** | 12.1.0 | Image processing (Profile Pics/Receipts) |
| **Razorpay** | Official SDK | Credit Card & Netbanking Payments |
| **PyTZ** | Latest | Timezone-aware scheduling |
| **Gunicorn** | Production | WSGI HTTP Server for high concurrency |
| **python-dateutil** | Latest | Complex date manipulations for bookings |

---

## 🔌 5. External APIs & Third-Party Integrations
- **Razorpay API:** Secure payment gateway integration for diversified payment methods.
- **Custom UPI Engine:** Integration with dynamic QR code generation for mobile-first Indian market.
- **OpenStreetMap (Nominatim):** Geolocation API used for live location detection of service providers.
- **Google Fonts API:** Provides a curated high-end visual experience.

---

## 💡 6. Unique Selling Points (USPs) & Logic Modules
- **Mutual Exclusion Availability:** Prevents double-booking of a single provider at any time index.
- **Secure Start OTP:** A dual-verification system where the partner must enter a 6-digit code provided by the customer to officially "start" the work, ensuring safety and arrival accuracy.
- **Automated Settlement Engine:** Instantly calculates and distributes a **20% Platform Fee** and **80% Partner Salary** per transaction.
- **UTR verification system:** A manual verification loop ensuring that UPI payments are confirmed by the partner before the service cycle ends.
- **Rebooking Logic:** Intelligent rebooking system that remembers user preferences, locations, and previous notes.

---

## 👨‍💻 7. Final System Status
- **Service Providers Tracked:** 94+ (Automated Population)
- **Service Categories:** 6 Standardized Units
- **Payment Verification:** Operational (UPI & Razorpay)
- **Environment:** Production-ready with `.bat` orchestration for multi-port simulation.

---
**Cool-E Technical Report | Created by Antigravity AI**
