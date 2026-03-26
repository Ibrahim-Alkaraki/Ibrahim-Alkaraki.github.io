import random

# ---------------------------------
# 1. Web Traffic Records Dataset
# ---------------------------------
web_traffic_records = [
    {
        "source_ip": "192.168.1.1",
        "timestamp": "2024-11-01 12:00:00",
        "method": "GET",
        "resource": "/index.html",
        "status_code": 200,
    },
    {
        "source_ip": "10.0.0.2",
        "timestamp": "2024-11-01 12:01:00",
        "method": "POST",
        "resource": "/login",
        "status_code": 401,
    },
    {
        "source_ip": "192.168.1.1",
        "timestamp": "2024-11-01 12:02:00",
        "method": "GET",
        "resource": "/dashboard",
        "status_code": 200,
    },
    {
        "source_ip": "10.0.0.3",
        "timestamp": "2024-11-01 12:03:00",
        "method": "GET",
        "resource": "/index.html",
        "status_code": 404,
    },
    {
        "source_ip": "192.168.1.2",
        "timestamp": "2024-11-01 12:04:00",
        "method": "PUT",
        "resource": "/settings",
        "status_code": 200,
    },
    {
        "source_ip": "192.168.1.1",
        "timestamp": "2024-11-01 12:05:00",
        "method": "GET",
        "resource": "/profile",
        "status_code": 403,
    },
    {
        "source_ip": "10.0.0.2",
        "timestamp": "2024-11-01 12:06:00",
        "method": "POST",
        "resource": "/login",
        "status_code": 200,
    },
    {
        "source_ip": "192.168.1.3",
        "timestamp": "2024-11-01 12:07:00",
        "method": "GET",
        "resource": "/home",
        "status_code": 200,
    },
    {
        "source_ip": "10.0.0.3",
        "timestamp": "2024-11-01 12:08:00",
        "method": "GET",
        "resource": "/help",
        "status_code": 404,
    },
    {
        "source_ip": "192.168.1.4",
        "timestamp": "2024-11-01 12:09:00",
        "method": "DELETE",
        "resource": "/account",
        "status_code": 500,
    },
]

# Fun status code meanings
status_meanings = {
    200: "OK - Everything is awesome!",
    401: "Unauthorized - Invalid credentials detected!",
    403: "Forbidden - Access denied, you shall not pass! 🚫",
    404: "Not Found - File went poof!",
    500: "Internal Server Error - Something exploded!",
}


# -----------------------------
# 2. TrafficRequest class definition
# -----------------------------------------------
class TrafficRequest:
    # Represents a single HTTP request captured from web server logs

    def __init__(self, log_dict):
        # Initialize from a dictionary with log data
        # Use dict.get so that missing keys fall back to safe defaults.
        self.source_ip = log_dict.get("source_ip", "unknown")
        self.timestamp = log_dict.get("timestamp", "unknown")
        self.method = log_dict.get("method", "UNKNOWN")
        self.resource = log_dict.get("resource", "unknown")
        self.status_code = log_dict.get("status_code", 0)

    def to_string(self):
        # Return a readable string representation
        return (
            f"[{self.timestamp}] {self.source_ip} "
            f'"{self.method} {self.resource}" -> {self.status_code}'
        )

    def __str__(self):
        # Return readable format when printed
        return self.to_string()

# --------------------------------------
# 3. Helper functions (outside the class)
# --------------------------------------
def parse_web_requests(raw_log_list):
    # Convert raw log dictionaries into TrafficRequest objects
    entries = []

    # Convert each log dictionary into a TrafficRequest object.
    for log_dict in raw_log_list:
        entry = TrafficRequest(log_dict)
        entries.append(entry)

    return entries


def analyze_response_codes(requests):
    # Count how many times each response code appears
    counts = {}

    # Count occurrences of each response code.
    for request in requests:
        code = request.status_code

        if code not in counts:
            counts[code] = 0

        counts[code] += 1

    return counts


def identify_client_addresses(requests):
    # Extract all unique client IP addresses
    ips = set()

    # Extract unique client IPs automatically via set.
    for request in requests:
        ips.add(request.source_ip)

    return ips


def print_traffic_summary(response_breakdown, client_ips):
    # Display the web traffic analysis report
    print("=== Web Traffic Analysis Report ===")

    # Display response code patterns.
    print("Response Code Statistics:")
    for code in sorted(response_breakdown.keys()):
        print(f"  {code}: {response_breakdown[code]} request(s)")

    print("\nClient IP Addresses:")
    for ip in sorted(client_ips):
        print(f"  {ip}")


# Additional helper functions
def get_error_incidents(requests):
    """Find all requests with error status codes (4xx, 5xx)"""
    incidents = []
    for req in requests:
        if req.status_code >= 400:
            incidents.append(req)
    return incidents

def filter_by_ip(requests, target_ip):
    """Filter requests from a specific IP address"""
    return [req for req in requests if req.source_ip == target_ip]

def filter_by_method(requests, target_method):
    """Filter requests by HTTP method"""
    return [req for req in requests if req.method == target_method.upper()]

def display_requests(requests):
    """Pretty print a list of requests"""
    if not requests:
        print("  No requests found.")
        return
    for i, req in enumerate(requests, 1):
        meaning = status_meanings.get(req.status_code, "Unknown Status")
        print(f"  {i}. {req}")
        print(f"     {meaning}")

def show_menu():
    """Interactive menu system"""
    requests = parse_web_requests(web_traffic_records)
    
    while True:
        print("\n" + "="*50)
        print("WEB TRAFFIC LOG ANALYZER")
        print("="*50)
        print("1. View all captured requests")
        print("2. Show error incidents (4xx, 5xx)")
        print("3. Response code statistics")
        print("4. View unique client IPs")
        print("5. Filter by IP address")
        print("6. Filter by HTTP method (GET, POST, etc.)")
        print("7. Hunt for the suspicious client")
        print("8. Exit")
        print("="*50)
        
        choice = input("Select an option (1-8): ").strip()
        
        if choice == "1":
            print("\nALL CAPTURED REQUESTS:")
            display_requests(requests)
            
        elif choice == "2":
            print("\nERROR INCIDENTS DETECTED:")
            incidents = get_error_incidents(requests)
            if incidents:
                print(f"  Found {len(incidents)} incident(s)!")
                display_requests(incidents)
            else:
                print("  No incidents found. All good!")
                
        elif choice == "3":
            print("\nRESPONSE CODE STATISTICS:")
            response_breakdown = analyze_response_codes(requests)
            for code in sorted(response_breakdown.keys()):
                count = response_breakdown[code]
                meaning = status_meanings.get(code, "Unknown")
                bar = "█" * count
                print(f"  {code}: {bar} ({count})")
                
        elif choice == "4":
            print("\nUNIQUE CLIENT IP ADDRESSES:")
            client_ips = identify_client_addresses(requests)
            for i, ip in enumerate(sorted(client_ips), 1):
                req_count = len(filter_by_ip(requests, ip))
                print(f"  {i}. {ip} - {req_count} request(s)")
                
        elif choice == "5":
            target_ip = input("Enter IP address to filter (e.g., 192.168.1.1): ").strip()
            filtered = filter_by_ip(requests, target_ip)
            print(f"\nREQUESTS FROM {target_ip}:")
            display_requests(filtered)
            
        elif choice == "6":
            method = input("Enter HTTP method (GET, POST, PUT, DELETE): ").strip().upper()
            filtered = filter_by_method(requests, method)
            print(f"\n{method} REQUESTS:")
            display_requests(filtered)
            
        elif choice == "7":
            print("\nSUSPICIOUS ACTIVITY HUNT...")
            incidents = get_error_incidents(requests)
            if incidents:
                sus_ip = incidents[0].source_ip
                print(f"ALERT: {sus_ip} made multiple failed requests!")
                print("Details:")
                display_requests(filter_by_ip(requests, sus_ip))
            else:
                print("No suspicious activity detected. Nice work!")
                
        elif choice == "8":
            farewells = [
                "May your logs be clean and your traffic be encrypted!",
                "Keep those firewalls strong!",
                "Happy packet sniffing!",
                "Remember: No logging, no evidence! (Just kidding.)",
                "Keep calm and analyze on!"
            ]
            print("\n" + random.choice(farewells))
            break
        else:
            print("Invalid choice. Please try again.")


# Run the menu if this file is executed directly.
if __name__ == "__main__":
    show_menu()