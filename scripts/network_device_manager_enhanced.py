import random

routers = []
switches = []


# Parent class — holds info every device shares
class NetworkDevice:
    def __init__(self, location, model, manufacturer):
        self.location = location
        self.model = model
        self.manufacturer = manufacturer

    def display_info(self):
        print(f"  Manufacturer: {self.manufacturer} | Model: {self.model} | Location: {self.location}")


# Router child class — adds a routing table
class Router(NetworkDevice):
    def __init__(self, location, model, manufacturer):
        super().__init__(location, model, manufacturer)
        self.routing_table = []

    # Parses routes entered as network/mask/gateway, comma-separated
    def add_route(self, route_input):
        for entry in route_input.split(","):
            parts = entry.strip().split("/")
            if len(parts) == 3:
                self.routing_table.append({"dst": parts[0] + "/" + parts[1], "gw": parts[2]})
            else:
                print(f"  [!] Skipped invalid route: '{entry.strip()}'")

    # Shows base info plus the routing table
    def display_info(self):
        print("\n[ROUTER]")
        super().display_info()
        print(f"  Routes ({len(self.routing_table)}):")
        for r in self.routing_table:
            print(f"    {r['dst']}  ->  {r['gw']}")
        if not self.routing_table:
            print("    (none)")


# Switch child class — adds VLAN support
class Switch(NetworkDevice):
    def __init__(self, location, model, manufacturer):
        super().__init__(location, model, manufacturer)
        self.vlans = []

    # Parses VLAN IDs entered as comma-separated numbers
    def add_vlans(self, vlan_input):
        for v in vlan_input.split(","):
            v = v.strip()
            if v.isdigit():
                self.vlans.append(int(v))
            else:
                print(f"  [!] Skipped invalid VLAN: '{v}'")

    # Shows base info plus VLANs
    def display_info(self):
        print("\n[SWITCH]")
        super().display_info()
        print(f"  VLANs: {', '.join(str(v) for v in self.vlans) if self.vlans else '(none)'}")


# Collects input and adds a new Router to the global list
def add_router():
    print("\n-- Add Router --")
    r = Router(input("  Location: "), input("  Model: "), input("  Manufacturer: "))
    route_input = input("  Routes (network/mask/gateway, comma-separated): ").strip()
    if route_input:
        r.add_route(route_input)
    routers.append(r)
    print(f"  [+] Router '{r.model}' added!")


# Collects input and adds a new Switch to the global list
def add_switch():
    print("\n-- Add Switch --")
    s = Switch(input("  Location: "), input("  Model: "), input("  Manufacturer: "))
    vlan_input = input("  VLANs (comma-separated, e.g. 10,20,30): ").strip()
    if vlan_input:
        s.add_vlans(vlan_input)
    switches.append(s)
    print(f"  [+] Switch '{s.model}' added!")


# Displays all routers stored in the global list
def view_routers():
    print("\n===== All Routers =====")
    if not routers:
        print("  (none added yet)")
    for i, r in enumerate(routers, 1):
        print(f"\n  Router #{i}")
        r.display_info()


# Displays all switches stored in the global list
def view_switches():
    print("\n===== All Switches =====")
    if not switches:
        print("  (none added yet)")
    for i, s in enumerate(switches, 1):
        print(f"\n  Switch #{i}")
        s.display_info()


# Main menu loop — keeps running until user picks Exit
def main():
    print("=" * 40)
    print("   Network Device Manager")
    print("=" * 40)
    while True:
        print("\n  1. Add Router\n  2. Add Switch\n  3. View Routers\n  4. View Switches\n  5. Exit")
        choice = input("\n  Choice (1-5): ").strip()
        if choice == "1":
            add_router()
        elif choice == "2":
            add_switch()
        elif choice == "3":
            view_routers()
        elif choice == "4":
            view_switches()
        elif choice == "5":
            # Fun tweak: random goodbye message on exit
            print("\n" + random.choice([
                "Goodbye! May your packets always find their destination.",
                "Exiting... No VLANs were harmed in the making of this program.",
                "Connection closed. Ping me anytime!"
            ]))
            break
        else:
            print("  [!] Invalid choice. Enter 1-5.")


if __name__ == "__main__":
    main()
