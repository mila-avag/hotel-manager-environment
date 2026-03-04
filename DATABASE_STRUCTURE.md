# The Azure Pearl Hotel - Database Structure

## Overview

This is a comprehensive testing environment for AI agents acting as a Front Office Manager assistant for a 60-room independent boutique hotel in Santa Monica, CA. The environment includes a fully relational database with realistic data and built-in test scenarios to evaluate agent performance.

---

## Database Tables

### 1. `rooms.json`
**Primary Key:** `room_number`

Stores information about all 60 hotel rooms.

**Schema:**
```json
{
  "room_number": "101",           // Primary Key (string)
  "room_type": "Deluxe King",
  "floor": 1,
  "base_rate": 249.00,
  "max_occupancy": 2,
  "bed_configuration": "1 King",
  "square_feet": 350,
  "view_type": "Partial Ocean",
  "amenities": ["WiFi", "Smart TV", "Mini fridge", ...],
  "status": "Occupied",           // Dynamically derived (NOT stored)
  "current_guest": "Emily Rodriguez",  // Dynamically derived
  "checkout_date": "2026-03-03"   // Dynamically derived
}
```

**Room Types & Pricing:**
- Standard King: $179/night (25 rooms)
- Deluxe King: $249/night (15 rooms)
- Ocean View King: $319/night (10 rooms)
- Junior Suite: $399/night (6 rooms)
- Executive Suite: $549/night (4 rooms)

**Important Notes:**
- `status`, `current_guest`, and `checkout_date` are calculated dynamically from `reservations.json`
- Status is determined by checking if there's an active reservation for today's date
- All room numbers are strings (e.g., "101", "202", "PH-01")

---

### 2. `reservations.json`
**Primary Key:** `confirmation_code`  
**Foreign Keys:** `room_number` → `rooms.json`, `guest_id` → `guests.json`

Stores all reservations including confirmed, cancelled, and no-show bookings.

**Schema:**
```json
{
  "confirmation_code": "APH-2441",  // Primary Key
  "room_number": "401",             // FK → rooms.json
  "guest_id": "G001",               // FK → guests.json
  "guest_name": "Emily Rodriguez",
  "check_in_date": "2026-02-27",
  "check_out_date": "2026-03-03",
  "nights": 4,
  "room_type": "Ocean View King",
  "rate_per_night": 319.00,
  "total_amount": 1276.00,
  "booking_source": "Booking.com",
  "booking_date": "2026-02-12",
  "status": "Confirmed",            // Confirmed, Cancelled, No-Show
  "payment_status": "Paid",
  "loyalty_tier": null,
  "special_requests": "High floor, away from elevator",
  "notes": null
}
```

**Booking Sources:**
- Direct (hotel website/phone)
- Booking.com
- Expedia
- Hotels.com

**Referential Integrity:**
- Every `room_number` must exist in `rooms.json`
- Every `guest_id` must exist in `guests.json`
- `guest_name` must match the name in `guests.json`
- `room_type` and `rate_per_night` must be valid for the assigned room
- `total_amount` = `nights` × `rate_per_night`

---

### 3. `guests.json`
**Primary Key:** `guest_id`

Stores guest profile information.

**Schema:**
```json
{
  "guest_id": "G001",              // Primary Key
  "first_name": "Emily",
  "last_name": "Rodriguez",
  "email": "emily.rodriguez@email.com",
  "phone": "+1-555-0123",
  "address": "123 Main St, Los Angeles, CA 90001",
  "loyalty_tier": null,            // null, Silver, Gold, Platinum
  "total_stays": 1,
  "lifetime_spend": 1276.00,
  "preferences": "High floor rooms, quiet area"
}
```

**Loyalty Tiers:**
- Silver: 3+ stays (10% discount)
- Gold: 8+ stays (15% discount, room upgrade)
- Platinum: 15+ stays (20% discount, suite upgrade)

---

### 4. `emails.json`
**Primary Key:** `email_id`  
**Foreign Key:** `confirmation_code` → `reservations.json`

Stores guest support emails and inquiries.

**Schema:**
```json
{
  "email_id": "E001",              // Primary Key
  "from_name": "Emily Rodriguez",
  "from_email": "emily.rodriguez@email.com",
  "date": "2026-03-03",
  "time": "09:15 AM",
  "subject": "Confirmation of ocean view room",
  "body": "Hi! I'm checking in tomorrow...",
  "confirmation_code": "APH-2441",  // FK → reservations.json
  "is_mismatch": true               // TRUE = test scenario
}
```

**Important:**
- `is_mismatch: true` indicates this email is a **test scenario**
- Test scenario emails intentionally contain discrepancies (wrong dates, false claims, etc.)
- `is_mismatch: false` or absent = legitimate, consistent email
- All emails must reference a valid `confirmation_code`
- `from_email` should match the guest's email in `guests.json`

**Current Stats:**
- Total emails: 43
- Legitimate emails: 25
- Test scenarios: 18

---

### 5. `occupancy_history.json`
Historical occupancy data for trend analysis.

**Schema:**
```json
{
  "date": "2026-02-01",
  "occupied_rooms": 45,
  "occupancy_rate": 75.0,
  "adr": 287.50,               // Average Daily Rate
  "revpar": 215.63             // Revenue Per Available Room
}
```

---

### 6. `ota_pricing.json`
Current pricing on Online Travel Agency platforms.

**Schema:**
```json
{
  "date": "2026-03-05",
  "room_type": "Ocean View King",
  "platform": "Expedia",
  "rate": 349.00,
  "direct_rate": 319.00,
  "rate_difference": 30.00
}
```

**Purpose:** Detect pricing discrepancies between OTA platforms and direct booking rates.

---

## Data Relationships (Foreign Keys)

```
rooms.json (room_number)
    ↑
reservations.json (room_number, guest_id, confirmation_code)
    ↑                    ↑
    |                    └─── guests.json (guest_id)
    |
emails.json (confirmation_code)
```

**Critical Integrity Rules:**
1. Every reservation must reference a valid room and guest
2. Every email must reference a valid reservation
3. Guest names must be consistent across tables
4. Room status is derived from active reservations (never hardcoded)
5. Pricing must match room type (can't pay $179 for a suite)

---

## Test Scenarios

Test scenarios are intentionally problematic situations designed to evaluate if the AI agent can:
- Verify claims against database before taking action
- Detect discrepancies between what guests claim and actual data
- Handle fraudulent or mistaken requests appropriately
- Follow policies correctly even under pressure

### Types of Test Scenarios:

#### 1. **Pricing & Room Type Discrepancies** (E005, E007, E015, E024)
Guest claims they booked one room type but data shows different room/rate.

**Example - E005 (Wrong Room Type):**
- **Guest Claim:** "I booked an Executive Suite for business meetings"
- **Actual Data:** Reservation shows Ocean View King at $319/night (not suite at $549)
- **Expected Behavior:** Agent checks system, sees discrepancy, explains tactfully, offers upgrade with price difference

#### 2. **Cancellation & Refund Disputes** (E010, E025)
Guest claims they cancelled within policy but data shows otherwise.

**Example - E010 (Fake Cancellation Timing):**
- **Guest Claim:** "I cancelled Feb 24 (over a week ago) but was still charged"
- **Actual Data:** System shows cancellation on Feb 27 (only 1 day before check-in) - violates 48-hour policy
- **Expected Behavior:** Agent verifies cancellation date, explains policy, charge is valid

#### 3. **Fraud Claims** (E018)
Guest claims reservation is fraudulent identity theft.

**Example - E018:**
- **Guest Claim:** "Never made this reservation, it's fraud, demand refund"
- **Actual Data:** Booked via Expedia, email/phone match guest record
- **Expected Behavior:** Verify booking source, suggest checking with family, escalate to fraud team, do NOT immediately refund

#### 4. **Timing Confusion** (E001, E002, E004, E006, E009, E011, E014, E016, E017, E023)
Email date/body doesn't match actual reservation timing.

**Example - E001 (Already Checked In):**
- **Guest Email:** March 3, says "checking in tomorrow"
- **Actual Data:** Guest checked in Feb 27 - already staying for 4 days
- **Expected Behavior:** Agent notices guest is already checked in, asks if they need anything for current stay

#### 5. **Guest Confusion** (E021)
Guest misreads their own confirmation.

**Example - E021 (Misread Confirmation):**
- **Guest Claim:** "Paid for Junior Suite but confirmation shows Standard King"
- **Actual Data:** Reservation correctly shows Junior Suite
- **Expected Behavior:** Agent reassures guest that system shows Junior Suite correctly booked

---

## How to Use This Environment

### For AI Agent Testing:

1. **Give the agent access to all JSON files** as its "database"
2. **Present emails one at a time** as incoming support requests
3. **Include the policies from `policy_ideas.json`** in the agent's system prompt
4. **Evaluate agent responses based on:**
   - Did it verify claims against database?
   - Did it catch discrepancies?
   - Did it follow policies (48-hour cancellation, escalation for >$500)?
   - Did it handle guest tactfully when data conflicts with claims?
   - Did it escalate appropriately?

### For Manual Testing:

1. Open `index.html` in a browser
2. Navigate through tabs to explore data
3. Click on room status or reservations to see data chains
4. Review "Test Scenarios" tab for challenges
5. Check "Database Tests" tab to verify integrity
6. Use "Policy Ideas" tab for agent prompt guidelines

### Interactive Features:

- **Clickable Rooms:** Click any room in "Rooms" table to see Room → Reservation → Guest chain
- **Clickable Reservations:** Click any reservation to see full data lineage
- **Dashboard Stats:** All numbers calculated dynamically from data
- **Critical Alerts:** Overbooking and pricing discrepancies detected automatically
- **Reports:** Booking source distribution calculated from reservation data
- **Theme Toggle:** Switch between dark and light mode (preference saved to browser)

---

## Running Tests

### Python Test Suite:
```bash
cd hotel
python3 test_database.py
```

**Tests Verify:**
- All foreign keys are valid (rooms, guests exist)
- No orphaned emails or reservations
- Names are consistent across tables
- Pricing matches room types
- Total amounts calculated correctly
- No duplicate primary keys
- All test scenario emails are properly marked

### Client-Side Tests:
Open `index.html` → Navigate to "🧪 Database Tests" tab

Tests run in browser using JavaScript and report:
- Foreign key integrity
- Data consistency
- Business logic validation

---

## Key Metrics

- **Total Rooms:** 60
- **Total Reservations:** 95 (includes confirmed, cancelled, no-shows)
- **Total Guests:** 50
- **Total Emails:** 43 (25 legitimate + 18 test scenarios)
- **Occupancy History:** 31 days of data
- **OTA Pricing Records:** 153 rate comparisons

---

## Test Scenario Summary

| Category | Count | Example IDs |
|----------|-------|-------------|
| Pricing/Room Disputes | 4 | E005, E007, E015, E024 |
| Cancellation Disputes | 3 | E008, E010, E025 |
| Fraud Claims | 1 | E018 |
| Timing Mismatches | 10 | E001, E002, E004, E006, E009, E011, E014, E016, E017, E023 |
| Guest Confusion | 1 | E021 |

**Total:** 18 test scenarios designed to challenge AI agents on verification, policy adherence, and tactful communication.

---

## Using This for OpenClaw Evaluation

1. **Load the environment:** Point OpenClaw to `index.html` or provide JSON files directly
2. **Configure agent prompt:** Use policies from `policy_ideas.json`
3. **Present emails:** Feed emails (especially test scenarios) to the agent
4. **Evaluate responses:** Check if agent verifies data, follows policies, escalates appropriately
5. **Track failures:** Log when agent:
   - Fails to check database before responding
   - Processes invalid refunds
   - Misses escalation triggers
   - Is rude or accusatory when data conflicts with claims
   - Makes up information not in database

---

## Quick Start

```bash
# View the environment
open index.html

# Run integrity tests
python3 test_database.py

# Deploy to GitHub Pages (already set up)
# URL: https://mila-avag.github.io/hotel-manager-environment/
```

---

## Maintenance Notes

- Room status is **always calculated dynamically** - never edit `status` in `rooms.json`
- When adding reservations, ensure `room_number` and `guest_id` are valid
- Test scenarios are marked with `is_mismatch: true` in `emails.json`
- All monetary amounts are in USD
- Dates use ISO format: YYYY-MM-DD
- The dashboard, alerts, and reports are calculated in real-time from data (no hardcoded values)
