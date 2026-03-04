# 🏨 Azure Pearl Hotel - Front Office Manager Environment

An AI agent evaluation environment simulating a 60-room independent boutique hotel's front office operations.

## 🎯 Purpose

Test AI agents' ability to:
- Monitor daily occupancy and forecast trends
- Detect OTA pricing discrepancies
- Handle guest inquiries and complaints
- Verify claims against reservation data
- Generate operational reports

## 📊 Dataset

- **60 rooms** across 8 room types (Standard to Presidential Suite)
- **64 reservations** (checked-in, confirmed, past reservations)
- **50 guest profiles** with contact information
- **25 support emails** including 8 challenging test scenarios
- **Historical data**: occupancy trends, OTA pricing logs

## ✨ Key Features

### True Relational Database Design
- **No hardcoded statuses**: Room occupancy derived from active reservations
- **Dynamic calculations**: Occupancy rates, ADR, RevPAR computed in real-time
- **100% referential integrity**: All foreign keys validated and consistent

### Interactive Data Exploration
- Click any room to see the full data chain: Room → Reservation → Guest
- Modal displays show how statuses are derived from underlying data
- Trace emails back to specific reservations and guests

### Automated Verification
- **12 comprehensive tests** validate database integrity
- Tests run in Python (`test_database.py`) and in-browser (Database Tests tab)
- Checks foreign keys, business logic, data quality, and calculations

## 🚀 Quick Start

### View the Environment
```bash
# Open in browser
open index.html
```

The viewer includes:
- **Rooms Grid**: Visual occupancy status
- **Reservations**: Current and upcoming bookings
- **Guest Directory**: Contact information
- **Support Messages**: Inbox with test scenarios
- **Analytics**: Occupancy trends and pricing
- **Database Tests**: Live integrity checks

### Run Test Suite
```bash
# Verify database integrity
python3 test_database.py
```

All 12 tests should pass ✅

## 📁 File Structure

```
├── index.html              # Interactive viewer with modal UI
├── test_database.py        # Automated test suite (12 tests)
├── README.md              # This file
├── DATABASE_DESIGN.md     # Technical documentation
├── CHANGES.md             # Design evolution notes
├── REFERENTIAL_INTEGRITY.md  # Integrity report
└── data/
    ├── rooms.json         # Room inventory (no current_status!)
    ├── reservations.json  # Source of truth for occupancy
    ├── guests.json        # Guest profiles
    ├── emails.json        # Support messages
    ├── occupancy_history.json  # Historical trends
    ├── ota_pricing.json   # Rate comparisons
    └── test_scenarios.json  # Test case descriptions
```

## 🧪 Test Scenarios

The environment includes 8 challenging scenarios:
1. **Wrong room type claim** - Guest claims Queen but booked Standard
2. **Price dispute** - Guest claims lower rate than actual
3. **Fake confirmation** - Non-existent confirmation code
4. **Late checkout** - Guest already checked out
5. **Double booking claim** - False complaint about reservation
6. **Maintenance** - Room 107 issue
7. **OTA discrepancy** - Rate matching request
8. **Cancellation policy** - Non-refundable rate dispute

## 🔄 How It Works

### Dynamic Room Status Calculation
```javascript
// Room status derived from reservations (not stored!)
const status = reservations.find(r => 
    r.room_number === roomNumber && r.status === 'Checked-In'
) ? 'Occupied' : 'Clean';
```

### Dashboard Metrics
All statistics calculated from actual data:
- **Occupancy Rate**: Active reservations / Total rooms
- **ADR** (Average Daily Rate): Total revenue / Occupied rooms
- **RevPAR**: Revenue / Total rooms (occupied + vacant)

## 🎨 Interactive Features

- **Clickable rooms**: See full reservation and guest details
- **Status derivation**: Understand how 'Occupied' is determined
- **Data tracing**: Follow the chain from room to guest
- **Live tests**: Run integrity checks in the browser

## 📚 Documentation

- `DATABASE_DESIGN.md` - Schema and design principles
- `CHANGES.md` - Evolution from hardcoded to dynamic
- `REFERENTIAL_INTEGRITY.md` - Data validation report

## ✅ Verified

- ✅ 100% referential integrity
- ✅ All foreign keys valid
- ✅ No hardcoded derived fields
- ✅ Business logic enforced
- ✅ 12/12 tests passing

---

Built for testing AI customer service agents in realistic hotel management scenarios.
