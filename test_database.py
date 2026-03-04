#!/usr/bin/env python3
"""
Database Integrity Test Suite for Azure Pearl Hotel
Tests all relationships, foreign keys, and business logic constraints
"""

import json
import sys
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def load_data():
    """Load all JSON data files"""
    with open('data/rooms.json', 'r') as f:
        rooms = json.load(f)
    with open('data/reservations.json', 'r') as f:
        reservations = json.load(f)
    with open('data/guests.json', 'r') as f:
        guests = json.load(f)
    with open('data/emails.json', 'r') as f:
        emails = json.load(f)
    
    return rooms, reservations, guests, emails

def print_test(name, passed, message, details=None):
    """Print formatted test result"""
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"{status} | {Colors.BOLD}{name}{Colors.END}")
    print(f"       {message}")
    if details:
        for detail in details:
            print(f"       → {detail}")
    print()

def test_no_hardcoded_status(rooms):
    """Test 1: Room status should NOT be stored in rooms.json"""
    has_status = any('current_status' in room for room in rooms)
    return (
        not has_status,
        "Room status must be derived from reservations, not hardcoded",
        [f"Found 'current_status' in {sum(1 for r in rooms if 'current_status' in r)} rooms"] if has_status else None
    )

def test_foreign_key_guests(reservations, guests):
    """Test 2: All reservations must reference real guests"""
    guest_ids = {g['guest_id'] for g in guests}
    invalid = [r['confirmation_code'] for r in reservations if r['guest_id'] not in guest_ids]
    return (
        len(invalid) == 0,
        f"All {len(reservations)} reservations reference valid guests",
        [f"Invalid guest references: {', '.join(invalid)}"] if invalid else None
    )

def test_foreign_key_rooms(reservations, rooms):
    """Test 3: All reservations must reference real rooms"""
    room_numbers = {r['room_number'] for r in rooms}
    invalid = [r['confirmation_code'] for r in reservations 
               if r['room_number'] and r['room_number'] not in room_numbers]
    return (
        len(invalid) == 0,
        f"All reservations reference valid room numbers",
        [f"Invalid room references: {', '.join(invalid)}"] if invalid else None
    )

def test_foreign_key_emails(emails, reservations):
    """Test 4: All emails must reference real confirmation codes"""
    conf_codes = {r['confirmation_code'] for r in reservations}
    invalid = [e['email_id'] for e in emails 
               if e.get('confirmation_code') and e['confirmation_code'] not in conf_codes]
    return (
        len(invalid) == 0,
        f"All {len(emails)} emails reference valid confirmation codes",
        [f"Invalid confirmation references: {', '.join(invalid)}"] if invalid else None
    )

def test_email_addresses_match_guests(emails, guests):
    """Test 5: Email addresses must match guest database"""
    guest_map = {f"{g['first_name']} {g['last_name']}": g for g in guests}
    mismatches = []
    for email in emails:
        guest = guest_map.get(email['from_name'])
        if guest and guest['email'] != email['from_email']:
            mismatches.append(f"{email['from_name']}: {email['from_email']} != {guest['email']}")
    
    return (
        len(mismatches) == 0,
        "All email addresses match guest database",
        mismatches if mismatches else None
    )

def test_email_senders_are_guests(emails, guests):
    """Test 6: All email senders must exist in guest database"""
    guest_names = {f"{g['first_name']} {g['last_name']}" for g in guests}
    unknown = [e['from_name'] for e in emails if e['from_name'] not in guest_names]
    return (
        len(unknown) == 0,
        "All email senders are registered guests",
        [f"Unknown senders: {', '.join(unknown)}"] if unknown else None
    )

def test_no_double_bookings(reservations):
    """Test 7: No room should have multiple checked-in reservations"""
    checked_in = [r for r in reservations if r['status'] == 'Checked-In']
    room_counts = {}
    for res in checked_in:
        room = res['room_number']
        room_counts[room] = room_counts.get(room, 0) + 1
    
    double_booked = [(room, count) for room, count in room_counts.items() if count > 1]
    return (
        len(double_booked) == 0,
        "No rooms have multiple active check-ins",
        [f"Room {room} has {count} checked-in reservations" for room, count in double_booked] if double_booked else None
    )

def test_unique_primary_keys(rooms, reservations, guests, emails):
    """Test 8: All primary keys must be unique"""
    results = []
    
    # Check room numbers
    room_nums = [r['room_number'] for r in rooms]
    dup_rooms = [num for num in set(room_nums) if room_nums.count(num) > 1]
    if dup_rooms:
        results.append(f"Duplicate room numbers: {', '.join(dup_rooms)}")
    
    # Check guest IDs
    guest_ids = [g['guest_id'] for g in guests]
    dup_guests = [id for id in set(guest_ids) if guest_ids.count(id) > 1]
    if dup_guests:
        results.append(f"Duplicate guest IDs: {', '.join(dup_guests)}")
    
    # Check confirmation codes
    conf_codes = [r['confirmation_code'] for r in reservations]
    dup_confs = [code for code in set(conf_codes) if conf_codes.count(code) > 1]
    if dup_confs:
        results.append(f"Duplicate confirmation codes: {', '.join(dup_confs)}")
    
    # Check email IDs
    email_ids = [e['email_id'] for e in emails]
    dup_emails = [id for id in set(email_ids) if email_ids.count(id) > 1]
    if dup_emails:
        results.append(f"Duplicate email IDs: {', '.join(dup_emails)}")
    
    return (
        len(results) == 0,
        "All primary keys are unique",
        results if results else None
    )

def test_rate_consistency(reservations, rooms):
    """Test 9: Reservation rates should be reasonable compared to base rates"""
    room_base_rates = {r['room_number']: r['base_rate'] for r in rooms}
    issues = []
    
    for res in reservations:
        if res['room_number']:
            base_rate = room_base_rates.get(res['room_number'])
            if base_rate:
                # Allow up to 100% markup (seasonal pricing) but flag > 200%
                if res['rate_per_night'] > base_rate * 3:
                    issues.append(f"{res['confirmation_code']}: ${res['rate_per_night']} vs base ${base_rate}")
                # Also flag rates below 50% of base (too cheap)
                elif res['rate_per_night'] < base_rate * 0.5:
                    issues.append(f"{res['confirmation_code']}: ${res['rate_per_night']} vs base ${base_rate} (too low)")
    
    return (
        len(issues) == 0,
        "All reservation rates are within reasonable range of base rates",
        issues if issues else None
    )

def test_valid_dates(reservations):
    """Test 10: Check-in must be before check-out"""
    invalid = []
    for res in reservations:
        try:
            check_in = datetime.strptime(res['check_in_date'], '%Y-%m-%d')
            check_out = datetime.strptime(res['check_out_date'], '%Y-%m-%d')
            if check_in >= check_out:
                invalid.append(f"{res['confirmation_code']}: {res['check_in_date']} to {res['check_out_date']}")
        except Exception as e:
            invalid.append(f"{res['confirmation_code']}: Invalid date format")
    
    return (
        len(invalid) == 0,
        "All reservations have valid date ranges",
        invalid if invalid else None
    )

def test_total_amount_calculation(reservations):
    """Test 11: Total amount should equal rate × nights"""
    errors = []
    for res in reservations:
        try:
            check_in = datetime.strptime(res['check_in_date'], '%Y-%m-%d')
            check_out = datetime.strptime(res['check_out_date'], '%Y-%m-%d')
            nights = (check_out - check_in).days
            expected_total = res['rate_per_night'] * nights
            
            if res['total_amount'] != expected_total:
                errors.append(f"{res['confirmation_code']}: ${res['total_amount']} != ${expected_total} ({nights} nights × ${res['rate_per_night']})")
        except Exception:
            pass
    
    return (
        len(errors) == 0,
        "All total amounts calculated correctly",
        errors if errors else None
    )

def test_status_values(reservations):
    """Test 12: Reservation status must be valid enum values"""
    valid_statuses = {'Checked-In', 'Confirmed', 'Checked-Out', 'Cancelled', 'No-Show'}
    invalid = [f"{r['confirmation_code']}: '{r['status']}'" 
               for r in reservations if r['status'] not in valid_statuses]
    return (
        len(invalid) == 0,
        f"All reservation statuses are valid ({', '.join(valid_statuses)})",
        invalid if invalid else None
    )

def run_all_tests():
    """Run all database integrity tests"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}🧪 Azure Pearl Hotel - Database Integrity Test Suite{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    try:
        rooms, reservations, guests, emails = load_data()
        print(f"📊 Loaded data: {len(rooms)} rooms, {len(reservations)} reservations, {len(guests)} guests, {len(emails)} emails\n")
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to load data files: {e}{Colors.END}")
        return False
    
    tests = [
        ("Schema Design", test_no_hardcoded_status, [rooms]),
        ("Foreign Key: Reservations → Guests", test_foreign_key_guests, [reservations, guests]),
        ("Foreign Key: Reservations → Rooms", test_foreign_key_rooms, [reservations, rooms]),
        ("Foreign Key: Emails → Reservations", test_foreign_key_emails, [emails, reservations]),
        ("Data Matching: Email Addresses", test_email_addresses_match_guests, [emails, guests]),
        ("Data Matching: Email Senders", test_email_senders_are_guests, [emails, guests]),
        ("Business Logic: No Double Bookings", test_no_double_bookings, [reservations]),
        ("Data Quality: Unique Primary Keys", test_unique_primary_keys, [rooms, reservations, guests, emails]),
        ("Data Quality: Rate Consistency", test_rate_consistency, [reservations, rooms]),
        ("Data Quality: Valid Date Ranges", test_valid_dates, [reservations]),
        ("Data Quality: Total Amount Calculation", test_total_amount_calculation, [reservations]),
        ("Data Quality: Valid Status Values", test_status_values, [reservations])
    ]
    
    results = []
    for test_name, test_func, args in tests:
        try:
            passed, message, details = test_func(*args)
            print_test(test_name, passed, message, details)
            results.append(passed)
        except Exception as e:
            print_test(test_name, False, f"Test error: {str(e)}", None)
            results.append(False)
    
    # Summary
    passed_count = sum(results)
    total_count = len(results)
    pass_rate = (passed_count / total_count) * 100
    
    print(f"{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}📊 Test Summary: {passed_count}/{total_count} Passed ({pass_rate:.0f}%){Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    if passed_count == total_count:
        print(f"{Colors.GREEN}{Colors.BOLD}✅✅✅ ALL TESTS PASSED - DATABASE IS VALID! ✅✅✅{Colors.END}")
        print(f"{Colors.GREEN}The database has perfect referential integrity and data quality.{Colors.END}\n")
        return True
    else:
        failed_count = total_count - passed_count
        print(f"{Colors.RED}{Colors.BOLD}❌ {failed_count} TEST(S) FAILED{Colors.END}")
        print(f"{Colors.RED}Please fix the issues above before using this environment.{Colors.END}\n")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
