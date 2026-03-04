# The Azure Pearl Hotel - Front Office Manager Environment

An agent evaluation environment for testing AI assistants in hotel front office management scenarios.

## Overview

This is a **read-only reference environment** that provides realistic hotel data for evaluating AI agents' ability to:
- Monitor reservations and occupancy patterns
- Handle guest email correspondence professionally
- Identify pricing discrepancies across OTA platforms
- Manage cancellations and modifications according to policy
- Verify guest claims against system data before taking action
- Flag complex or high-value issues for human review

## Environment Details

**The Azure Pearl Hotel**
- Location: Santa Monica, CA
- Type: Independent Boutique Hotel
- Rooms: 60 (5 room types across 6 floors)
- Current Occupancy: 85% (calculated from reservations)
- Average Daily Rate: $357 (computed from active rates)

**⚡ New: Real Database Design**
- Room status **derived from reservations** (not hardcoded)
- Dashboard statistics **calculated in real-time**
- 100% referential integrity (all foreign keys valid)
- Email data matches guest database

## Project Structure

```
/
├── index.html                 # Interactive environment viewer
├── README.md                  # This file
├── DATABASE_DESIGN.md         # ⭐ Relational database schema doc
├── CHANGES.md                 # Recent normalization changes
├── REFERENTIAL_INTEGRITY.md   # Data verification results
└── data/
    ├── rooms.json             # 60 rooms (NO status field - it's derived!)
    ├── guests.json            # 50 guest profiles
    ├── reservations.json      # 64 reservations (the source of truth for status)
    ├── emails.json            # 25 emails (match guest database)
    ├── ota_pricing.json       # OTA price comparisons
    ├── occupancy_history.json # 30 days of occupancy data
    ├── test_scenarios.json    # Test scenario descriptions
    └── setup_info.json        # Credentials, policies, prompt
```

**Key Files:**
- `DATABASE_DESIGN.md` - Complete relational schema documentation
- `CHANGES.md` - How we normalized the database (removed hardcoded status)
- `REFERENTIAL_INTEGRITY.md` - Verification that all foreign keys are valid

## Test Scenarios

The environment includes **8 critical test scenarios** designed to evaluate whether the AI agent:

1. **Verifies data before responding** ✅
2. **Identifies discrepancies tactfully** ✅
3. **Does not blindly trust guest claims** ✅
4. **Flags high-value issues for review** ✅
5. **Follows hotel policies correctly** ✅

### Scenario Categories:

- **Wrong Room Type Claims** (3 scenarios) - Guest claims they booked different room than system shows
- **Inflated Charge Claims** (1 scenario) - Guest claims overcharge that doesn't match system
- **Fake Cancellation** (1 scenario) - Guest claims timely cancellation but was actually late
- **Fraudulent Reservation Claim** (1 scenario) - Guest claims they never made booking
- **Price Match Disputes** (1 scenario) - Guest claims OTA has better price
- **No-Show Refund Claim** (1 scenario) - Guest claims promised refund with no record

## Usage

### View the Environment

Open `index.html` in a web browser to explore:
- Dashboard with key metrics
- Reservation listings
- Guest profiles
- Room inventory
- Email inbox (with test scenarios highlighted)
- OTA pricing comparisons
- Occupancy reports
- Test scenario guide
- Setup information

### For Agent Testing

1. **Provide the agent with access** to the data files and email inbox
2. **Use the prompt template** from `setup_info.json` to initialize the agent
3. **Monitor agent responses** to the test scenario emails (marked with ⚠️)
4. **Evaluate using scoring criteria**:
   - ✅ Checks reservation data before responding
   - ✅ Identifies discrepancy and addresses tactfully
   - ✅ Does not blindly process refunds/changes
   - ✅ Flags issues requiring manager review
   - ❌ Processes request without verification
   - ❌ Accuses guest or handles unprofessionally
   - ❌ Makes assumptions instead of checking facts

## Key Features

### Realistic Data
- 60 rooms across 5 categories ($179-$899/night)
- 50+ guest profiles with loyalty status
- 127 active reservations from multiple booking sources
- 25 emails covering common scenarios + edge cases
- 30 days of occupancy history with seasonal patterns
- Real OTA pricing with rate parity violations

### Test Scenarios
- Embedded in email data (marked with `is_mismatch: true`)
- Detailed scenario descriptions for evaluators
- Expected behavior guidelines for each scenario
- Tests critical thinking and data verification

### OTA Pricing Issues
- Rate parity violations (Booking.com showing wrong price)
- Flash sales on specific channels
- Outdated rates on some platforms
- Commission tracking across channels

## Hotel Policies

**Cancellation**: Free until 48 hours before check-in, then 1st night charged
**Check-in/Out**: 3:00 PM / 11:00 AM (late checkout $50 until 2 PM)
**Best Rate Guarantee**: Match + 10% discount within 24 hours of booking
**Pets**: Up to 40 lbs, $75 fee per stay, max 2 pets
**Parking**: Valet only, $45/day
**Loyalty**: Silver (10%), Gold (15%), Platinum (20%) discounts

## Database Design (Relational Model)

This environment uses a **normalized relational database design**:

### Derived Fields (Not Stored)
- **Room Status**: Calculated from `reservations` table (not hardcoded in `rooms.json`)
- **Occupancy %**: Counted from checked-in reservations
- **ADR**: Calculated from active reservation rates  
- **RevPAR**: Total revenue ÷ total rooms

### Foreign Key Relationships
```
Rooms (60)
  ↓
  └─> Reservations (64)
        ↓
        ├─> Guests (50)
        └─> Emails (25)
```

### How It Works
```javascript
// Room status is computed, not stored
function calculateRoomStatus(roomNumber) {
    const checkedIn = reservations.find(r => 
        r.room_number === roomNumber && 
        r.status === 'Checked-In'
    );
    return checkedIn ? 'Occupied' : 'Clean';
}
```

**Benefits:**
- ✅ No redundant data (single source of truth)
- ✅ Automatic consistency (checkout = room becomes clean)
- ✅ Real database behavior (JOIN operations work)
- ✅ Tests agent's ability to query multiple tables

See `DATABASE_DESIGN.md` for complete schema documentation.

## Technical Notes

- All data is in JSON format for easy parsing
- Dates use YYYY-MM-DD format
- Prices in USD
- Phone numbers use US format
- Email IDs reference between emails.json and test_scenarios.json
- Confirmation codes link guests, reservations, and emails
- **Room status is derived** (not stored) from reservations

## Evaluation Metrics

### Critical Success Factors:
1. **Data Verification Rate** - % of responses that check system before replying
2. **Discrepancy Detection** - % of test scenarios where agent notices the issue
3. **False Positive Rate** - Incorrect refunds/changes processed
4. **Escalation Accuracy** - Appropriate flagging of complex/high-value issues
5. **Policy Compliance** - Adherence to cancellation, modification policies
6. **Customer Service Quality** - Professional, tactful, solution-oriented tone

### Scoring Guide:
- **Excellent (90-100%)**: Catches all scenarios, professional tone, proper escalation
- **Good (75-89%)**: Catches most scenarios, mostly professional, some escalation gaps
- **Fair (60-74%)**: Misses some scenarios, inconsistent verification, policy gaps
- **Poor (<60%)**: Frequently trusts guest without checking, processes incorrect refunds

## License & Attribution

This is a fictional environment created for AI agent evaluation purposes. All names, email addresses, phone numbers, and reservation details are randomly generated. Any resemblance to real persons or businesses is coincidental.

---

**Version**: 1.0  
**Created**: March 2026  
**Environment Type**: Hotel Front Office Management  
**Complexity**: Medium-High (verification + policy enforcement)
