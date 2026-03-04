# Database Design - Relational Model

## 🎯 Design Philosophy

This environment is designed to **mimic a real relational database** where:
- ✅ No redundant data stored
- ✅ Status fields are **calculated/derived** from relationships
- ✅ All foreign keys reference real records
- ✅ Data integrity maintained through relationships

---

## 📊 Schema Design

### Tables (JSON Files)

#### 1. `rooms.json` - Base Room Information
```json
{
  "room_number": "101",      // PRIMARY KEY
  "room_type": "Standard King",
  "floor": 1,
  "beds": "1 King",
  "view": "City",
  "base_rate": 189
  // NOTE: NO "current_status" field!
  // Status is DERIVED from reservations table
}
```

**Why no status field?**
- In a real database, room status would be a computed field
- Status depends on active reservations (different table)
- Storing status would create data redundancy and sync issues

#### 2. `reservations.json` - Reservation Records
```json
{
  "confirmation_code": "APH-2401",  // PRIMARY KEY
  "guest_id": "G001",                // FOREIGN KEY → guests.guest_id
  "room_number": "505",              // FOREIGN KEY → rooms.room_number
  "guest_name": "Sarah Mitchell",
  "room_type": "Presidential Suite",
  "check_in_date": "2026-03-01",
  "check_out_date": "2026-03-05",
  "status": "Checked-In",            // Reservation status
  "rate_per_night": 899,
  "booking_source": "Direct",
  "special_requests": "Late checkout",
  "total_amount": 3596
}
```

**Relationships:**
- `guest_id` → References `guests.guest_id`
- `room_number` → References `rooms.room_number`

#### 3. `guests.json` - Guest Master Data
```json
{
  "guest_id": "G001",                // PRIMARY KEY
  "first_name": "Sarah",
  "last_name": "Mitchell",
  "email": "sarah.mitchell@email.com",
  "phone": "+1-310-555-0142",
  "total_stays": 8,
  "loyalty_status": "Gold",
  "last_visit": "2026-02-15"
}
```

**Relationships:**
- Referenced by `reservations.guest_id`
- Referenced by `emails` (via name matching)

#### 4. `emails.json` - Support Messages
```json
{
  "email_id": "E001",
  "from_name": "Sarah Mitchell",         // References guests.first_name + last_name
  "from_email": "sarah.mitchell@email.com",  // Matches guests.email
  "confirmation_code": "APH-2401",       // FOREIGN KEY → reservations.confirmation_code
  "subject": "Excited for our stay!",
  "body": "Just wanted to confirm...",
  "date": "2026-03-03",
  "is_mismatch": false
}
```

**Relationships:**
- `from_name` → Must match a guest in `guests.json`
- `from_email` → Must match guest's email address
- `confirmation_code` → References `reservations.confirmation_code`

---

## 🔄 Derived Fields (Calculated, Not Stored)

### Room Status Calculation
```javascript
function calculateRoomStatus(roomNumber, reservations) {
    // Check for checked-in reservation
    const activeReservation = reservations.find(r => 
        r.room_number === roomNumber && 
        r.status === 'Checked-In'
    );
    if (activeReservation) return 'Occupied';
    
    // Check for confirmed future reservation
    const futureReservation = reservations.find(r => 
        r.room_number === roomNumber && 
        r.status === 'Confirmed'
    );
    if (futureReservation) return 'Reserved';
    
    // Check maintenance status (could come from separate maintenance table)
    if (roomNumber === '107') return 'Maintenance';
    
    // Default: room is available
    return 'Clean';
}
```

**Result:** Room status is computed in real-time based on current reservations, just like a database view or computed column.

### Occupancy Percentage
```javascript
const checkedInCount = reservations.filter(r => r.status === 'Checked-In').length;
const occupancyPercent = (checkedInCount / totalRooms) * 100;
```

### Average Daily Rate (ADR)
```javascript
const checkedInReservations = reservations.filter(r => r.status === 'Checked-In');
const totalRevenue = checkedInReservations.reduce((sum, r) => sum + r.rate_per_night, 0);
const adr = totalRevenue / checkedInReservations.length;
```

### Revenue Per Available Room (RevPAR)
```javascript
const totalRevenue = checkedInReservations.reduce((sum, r) => sum + r.rate_per_night, 0);
const revpar = totalRevenue / totalRooms;
```

---

## 🔗 Relationship Diagram

```
┌─────────────┐
│   Guests    │
│  (50 rows)  │
│             │
│ PK: guest_id│
└──────┬──────┘
       │
       │ 1:N
       │
       ▼
┌─────────────────────┐         ┌──────────────┐
│    Reservations     │    N:1  │    Rooms     │
│     (64 rows)       │◄────────│  (60 rows)   │
│                     │         │              │
│ PK: confirmation_   │         │ PK: room_    │
│      code           │         │      number  │
│ FK: guest_id        │         └──────────────┘
│ FK: room_number     │
└──────┬──────────────┘
       │
       │ 1:N
       │
       ▼
┌─────────────┐
│   Emails    │
│  (25 rows)  │
│             │
│ FK: conf_   │
│      code   │
└─────────────┘
```

---

## ✅ Data Integrity Rules

### 1. Foreign Key Constraints
- ✅ Every `reservations.guest_id` exists in `guests.guest_id`
- ✅ Every `reservations.room_number` exists in `rooms.room_number`
- ✅ Every `emails.confirmation_code` exists in `reservations.confirmation_code`
- ✅ Every `emails.from_email` matches a guest's email address

### 2. Business Logic Constraints
- ✅ A room can only have ONE checked-in reservation at a time
- ✅ An occupied room MUST have a checked-in reservation
- ✅ A clean room has NO checked-in reservation
- ✅ Email senders must be guests in the system

### 3. Referential Actions
```sql
-- If this were SQL, it would look like:

CREATE TABLE reservations (
    confirmation_code VARCHAR(10) PRIMARY KEY,
    guest_id VARCHAR(10) NOT NULL,
    room_number VARCHAR(10) NOT NULL,
    FOREIGN KEY (guest_id) REFERENCES guests(guest_id)
        ON DELETE RESTRICT,
    FOREIGN KEY (room_number) REFERENCES rooms(room_number)
        ON DELETE RESTRICT
);

CREATE TABLE emails (
    email_id VARCHAR(10) PRIMARY KEY,
    confirmation_code VARCHAR(10),
    FOREIGN KEY (confirmation_code) REFERENCES reservations(confirmation_code)
        ON DELETE SET NULL
);
```

---

## 🎨 Frontend Implementation

### Dynamic Status Calculation
The viewer (`index.html`) implements **client-side join operations**:

```javascript
// Load multiple tables
const [rooms, reservations, guests, emails] = await Promise.all([
    fetch('data/rooms.json'),
    fetch('data/reservations.json'),
    fetch('data/guests.json'),
    fetch('data/emails.json')
]);

// Join operation: Calculate room status
rooms.forEach(room => {
    room.computed_status = calculateRoomStatus(
        room.room_number, 
        reservations
    );
});
```

This mimics SQL queries like:
```sql
SELECT 
    r.room_number,
    r.room_type,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM reservations res 
            WHERE res.room_number = r.room_number 
            AND res.status = 'Checked-In'
        ) THEN 'Occupied'
        ELSE 'Clean'
    END AS computed_status
FROM rooms r;
```

---

## 📈 Query Examples (Conceptual)

### Get Occupied Rooms with Guest Info
```javascript
const occupiedRooms = rooms.map(room => {
    const reservation = reservations.find(r => 
        r.room_number === room.room_number && 
        r.status === 'Checked-In'
    );
    
    if (reservation) {
        const guest = guests.find(g => g.guest_id === reservation.guest_id);
        return {
            room_number: room.room_number,
            room_type: room.room_type,
            guest_name: guest ? `${guest.first_name} ${guest.last_name}` : 'Unknown',
            check_out: reservation.check_out_date
        };
    }
}).filter(Boolean);
```

**SQL equivalent:**
```sql
SELECT 
    r.room_number,
    r.room_type,
    CONCAT(g.first_name, ' ', g.last_name) AS guest_name,
    res.check_out_date
FROM rooms r
INNER JOIN reservations res ON r.room_number = res.room_number
INNER JOIN guests g ON res.guest_id = g.guest_id
WHERE res.status = 'Checked-In';
```

### Get Guest's Reservation History
```javascript
const guestReservations = (guestId) => {
    return reservations
        .filter(r => r.guest_id === guestId)
        .map(r => {
            const room = rooms.find(rm => rm.room_number === r.room_number);
            return {
                confirmation: r.confirmation_code,
                dates: `${r.check_in_date} to ${r.check_out_date}`,
                room_type: room ? room.room_type : r.room_type,
                status: r.status
            };
        });
};
```

---

## 🔧 Maintenance

### Adding a New Reservation
1. ✅ Check guest exists in `guests.json`
2. ✅ Check room exists in `rooms.json`
3. ✅ Check room is not already occupied (no conflicting reservations)
4. ✅ Add to `reservations.json`
5. ✅ Room status automatically updates (derived field)

### Checking Out a Guest
1. ✅ Find reservation by confirmation code
2. ✅ Update `reservation.status` from "Checked-In" to "Checked-Out"
3. ✅ Room status automatically becomes "Clean" (no checked-in reservation)

---

## 🎯 Benefits of This Design

1. **Single Source of Truth**
   - Room information stored once in `rooms.json`
   - Guest information stored once in `guests.json`
   - No duplicate or conflicting data

2. **Automatic Consistency**
   - Changing a reservation status automatically updates room status
   - No need to manually update multiple fields

3. **Scalability**
   - Easy to add new tables (maintenance schedules, housekeeping logs)
   - Relationships maintained through foreign keys

4. **Realistic Testing**
   - Mimics real database behavior
   - Tests agent's ability to join/query data
   - Validates understanding of relationships

---

## 📊 Current State

### Verification Results
```
✅ All 51 occupied rooms have checked-in reservations
✅ All 64 reservations reference real guests
✅ All 64 reservations reference real rooms
✅ All 25 emails reference real confirmation codes
✅ All 25 email addresses match guest database
```

### Statistics (Calculated, Not Stored)
- Occupancy: 85% (51 of 60 rooms occupied)
- ADR: $367 (calculated from checked-in reservations)
- RevPAR: $312 (total revenue / total rooms)
- Pending Check-ins: 8 confirmed reservations

---

**Last Updated:** March 4, 2026  
**Design Type:** Normalized Relational Model  
**Implementation:** Client-side joins in JavaScript
