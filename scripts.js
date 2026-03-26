/**
 * Browser-based interactive script simulators.
 * Replaces the Python backend scripts for static GitHub Pages deployment.
 * Each script uses an async/await pattern with a virtual terminal.
 */

// ============================================================
// Virtual Terminal Engine
// ============================================================
class VirtualTerminal {
  constructor(outputEl, inputEl, sendBtn) {
    this.outputEl = outputEl;
    this.inputEl = inputEl;
    this.sendBtn = sendBtn;
    this._resolve = null;
  }

  print(text) {
    const div = document.createElement('div');
    div.textContent = text;
    this.outputEl.appendChild(div);
    this.outputEl.scrollTop = this.outputEl.scrollHeight;
  }

  async input(prompt) {
    if (prompt) this.print(prompt);
    this.inputEl.disabled = false;
    this.sendBtn.disabled = false;
    this.inputEl.focus();
    return new Promise(resolve => { this._resolve = resolve; });
  }

  submit(value) {
    if (!this._resolve) return;
    const div = document.createElement('div');
    div.innerHTML = '<span style="color: var(--accent-warn);">$ ' + escapeHtml(value) + '</span>';
    this.outputEl.appendChild(div);
    this.outputEl.scrollTop = this.outputEl.scrollHeight;
    this.inputEl.disabled = true;
    this.sendBtn.disabled = true;
    const resolve = this._resolve;
    this._resolve = null;
    resolve(value.trim());
  }

  finish() {
    const div = document.createElement('div');
    div.innerHTML = '<span style="color: var(--accent-soft);">[✓] Script finished</span>';
    this.outputEl.appendChild(div);
    this.outputEl.scrollTop = this.outputEl.scrollHeight;
    this.inputEl.disabled = true;
    this.sendBtn.disabled = true;
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ============================================================
// PASSWORD MANAGER
// ============================================================
async function passwordManagerScript(term) {
  const passwords = {};

  function checkStrength(pw) {
    if (pw.length < 6) term.print("Password strength: weak (try making it longer).");
    else if (pw.length < 10) term.print("Password strength: medium (pretty good, but can be stronger).");
    else term.print("Password strength: strong (nice job!).");
  }

  function hasNumber(pw) {
    return /\d/.test(pw);
  }

  while (true) {
    term.print("\n--- Password Manager Menu ---");
    term.print("Note: Passwords must include at least one number (0-9).");
    term.print("1. Add a new password");
    term.print("2. Retrieve a stored password");
    term.print("3. Validate username and password");
    term.print("4. Show how many services are saved");
    term.print("5. Exit");
    const choice = await term.input("Enter your choice (1-5): ");

    if (choice === "1") {
      const service = await term.input("Enter the service name (e.g., email, bank): ");
      const username = await term.input("Enter the username for this service: ");
      const password = await term.input("Enter the password for this service: ");
      if (!service || !username || !password) { term.print("Error: Service, username, and password cannot be empty."); continue; }
      if (!hasNumber(password)) { term.print("Error: Password must contain at least one number (0-9)."); continue; }
      passwords[service] = { username, password };
      term.print("Password added successfully for service: " + service);
      checkStrength(password);
    } else if (choice === "2") {
      const service = await term.input("Enter the service name to retrieve: ");
      if (passwords[service]) {
        term.print("Service: " + service);
        term.print("Username: " + passwords[service].username);
        term.print("Password: " + passwords[service].password);
      } else { term.print("Error: No password found for that service."); }
    } else if (choice === "3") {
      const service = await term.input("Enter the service name to validate: ");
      const username = await term.input("Enter the username: ");
      const password = await term.input("Enter the password: ");
      if (!passwords[service]) { term.print("Credentials are incorrect (service not found)."); continue; }
      if (username === passwords[service].username && password === passwords[service].password) {
        term.print("Credentials are correct.");
      } else { term.print("Credentials are incorrect."); }
    } else if (choice === "4") {
      term.print("You currently have " + Object.keys(passwords).length + " service(s) stored.");
    } else if (choice === "5") {
      const msgs = [
        "Exiting... Your passwords are as safe as they'll ever be. Goodbye!",
        "Until next time! No passwords were harmed in the making of this session.",
        "Connection closed. May your credentials always be strong! 🔐"
      ];
      term.print(msgs[Math.floor(Math.random() * msgs.length)]);
      break;
    } else { term.print("Invalid choice. Please enter a number from 1 to 5."); }
  }
}

// ============================================================
// FILE MANAGER
// ============================================================
async function fileManagerScript(term) {
  const files = {};

  while (true) {
    term.print("\n--- File Manager Menu ---");
    term.print("1. Create a new file");
    term.print("2. View a file");
    term.print("3. List all files");
    term.print("4. Delete a file");
    term.print("5. Rename a file");
    term.print("6. Show how many files are stored");
    term.print("7. Exit");
    const choice = await term.input("Enter your choice (1-7): ");

    if (choice === "1") {
      const name = await term.input("Enter the file name: ");
      if (!name) { term.print("Error: File name cannot be empty."); continue; }
      if (files[name]) { term.print("Error: A file with that name already exists."); continue; }
      const content = await term.input("Enter the file content: ");
      files[name] = content;
      term.print("File created successfully: " + name);
    } else if (choice === "2") {
      const name = await term.input("Enter the file name to view: ");
      if (files[name] !== undefined) {
        term.print("File: " + name);
        term.print("Content: " + files[name]);
      } else { term.print("Error: No file found with that name."); }
    } else if (choice === "3") {
      const names = Object.keys(files);
      if (names.length === 0) { term.print("No files stored yet."); continue; }
      term.print("\n--- Stored Files ---");
      names.forEach((n, i) => term.print((i + 1) + ". " + n));
    } else if (choice === "4") {
      const name = await term.input("Enter the file name to delete: ");
      if (files[name] !== undefined) { delete files[name]; term.print("File deleted successfully: " + name); }
      else { term.print("Error: No file found with that name."); }
    } else if (choice === "5") {
      const oldName = await term.input("Enter the current file name: ");
      if (files[oldName] === undefined) { term.print("Error: No file found with that name."); continue; }
      const newName = await term.input("Enter the new file name: ");
      if (!newName) { term.print("Error: New file name cannot be empty."); continue; }
      if (files[newName] !== undefined) { term.print("Error: A file with that name already exists."); continue; }
      files[newName] = files[oldName];
      delete files[oldName];
      term.print("File renamed from " + oldName + " to " + newName);
    } else if (choice === "6") {
      term.print("You currently have " + Object.keys(files).length + " file(s) stored.");
    } else if (choice === "7") {
      const msgs = [
        "Exiting File Manager... No files were harmed in the making of this session.",
        "Goodbye! May your filesystem always stay organized. 📁",
        "Connection closed. Keep your data safe!"
      ];
      term.print(msgs[Math.floor(Math.random() * msgs.length)]);
      break;
    } else { term.print("Invalid choice. Please enter a number from 1 to 7."); }
  }
}

// ============================================================
// NETWORK DEVICE MANAGER
// ============================================================
async function networkDeviceManagerScript(term) {
  const routers = [];
  const switches = [];

  term.print("========================================");
  term.print("   Network Device Manager");
  term.print("========================================");

  while (true) {
    term.print("\n  1. Add Router");
    term.print("  2. Add Switch");
    term.print("  3. View Routers");
    term.print("  4. View Switches");
    term.print("  5. Exit");
    const choice = await term.input("\n  Choice (1-5): ");

    if (choice === "1") {
      term.print("\n-- Add Router --");
      const location = await term.input("  Location: ");
      const model = await term.input("  Model: ");
      const manufacturer = await term.input("  Manufacturer: ");
      const routeInput = await term.input("  Routes (network/mask/gateway, comma-separated): ");
      const routingTable = [];
      if (routeInput) {
        routeInput.split(",").forEach(entry => {
          const parts = entry.trim().split("/");
          if (parts.length === 3) routingTable.push({ dst: parts[0] + "/" + parts[1], gw: parts[2] });
          else term.print("  [!] Skipped invalid route: '" + entry.trim() + "'");
        });
      }
      routers.push({ location, model, manufacturer, routingTable });
      term.print("  [+] Router '" + model + "' added!");
    } else if (choice === "2") {
      term.print("\n-- Add Switch --");
      const location = await term.input("  Location: ");
      const model = await term.input("  Model: ");
      const manufacturer = await term.input("  Manufacturer: ");
      const vlanInput = await term.input("  VLANs (comma-separated, e.g. 10,20,30): ");
      const vlans = [];
      if (vlanInput) {
        vlanInput.split(",").forEach(v => {
          v = v.trim();
          if (/^\d+$/.test(v)) vlans.push(parseInt(v));
          else term.print("  [!] Skipped invalid VLAN: '" + v + "'");
        });
      }
      switches.push({ location, model, manufacturer, vlans });
      term.print("  [+] Switch '" + model + "' added!");
    } else if (choice === "3") {
      term.print("\n===== All Routers =====");
      if (routers.length === 0) { term.print("  (none added yet)"); }
      routers.forEach((r, i) => {
        term.print("\n  Router #" + (i + 1));
        term.print("[ROUTER]");
        term.print("  Manufacturer: " + r.manufacturer + " | Model: " + r.model + " | Location: " + r.location);
        term.print("  Routes (" + r.routingTable.length + "):");
        if (r.routingTable.length === 0) term.print("    (none)");
        else r.routingTable.forEach(rt => term.print("    " + rt.dst + "  ->  " + rt.gw));
      });
    } else if (choice === "4") {
      term.print("\n===== All Switches =====");
      if (switches.length === 0) { term.print("  (none added yet)"); }
      switches.forEach((s, i) => {
        term.print("\n  Switch #" + (i + 1));
        term.print("[SWITCH]");
        term.print("  Manufacturer: " + s.manufacturer + " | Model: " + s.model + " | Location: " + s.location);
        term.print("  VLANs: " + (s.vlans.length ? s.vlans.join(", ") : "(none)"));
      });
    } else if (choice === "5") {
      const msgs = [
        "Goodbye! May your packets always find their destination.",
        "Exiting... No VLANs were harmed in the making of this program.",
        "Connection closed. Ping me anytime!"
      ];
      term.print("\n" + msgs[Math.floor(Math.random() * msgs.length)]);
      break;
    } else { term.print("  [!] Invalid choice. Enter 1-5."); }
  }
}

// ============================================================
// LOG PARSING ANALYSIS
// ============================================================
async function logParsingAnalysisScript(term) {
  const webTrafficRecords = [
    { source_ip: "192.168.1.1", timestamp: "2024-11-01 12:00:00", method: "GET", resource: "/index.html", status_code: 200 },
    { source_ip: "10.0.0.2", timestamp: "2024-11-01 12:01:00", method: "POST", resource: "/login", status_code: 401 },
    { source_ip: "192.168.1.1", timestamp: "2024-11-01 12:02:00", method: "GET", resource: "/dashboard", status_code: 200 },
    { source_ip: "10.0.0.3", timestamp: "2024-11-01 12:03:00", method: "GET", resource: "/index.html", status_code: 404 },
    { source_ip: "192.168.1.2", timestamp: "2024-11-01 12:04:00", method: "PUT", resource: "/settings", status_code: 200 },
    { source_ip: "192.168.1.1", timestamp: "2024-11-01 12:05:00", method: "GET", resource: "/profile", status_code: 403 },
    { source_ip: "10.0.0.2", timestamp: "2024-11-01 12:06:00", method: "POST", resource: "/login", status_code: 200 },
    { source_ip: "192.168.1.3", timestamp: "2024-11-01 12:07:00", method: "GET", resource: "/home", status_code: 200 },
    { source_ip: "10.0.0.3", timestamp: "2024-11-01 12:08:00", method: "GET", resource: "/help", status_code: 404 },
    { source_ip: "192.168.1.4", timestamp: "2024-11-01 12:09:00", method: "DELETE", resource: "/account", status_code: 500 },
  ];

  const statusMeanings = {
    200: "OK - Everything is awesome!",
    401: "Unauthorized - Invalid credentials detected!",
    403: "Forbidden - Access denied, you shall not pass! 🚫",
    404: "Not Found - File went poof!",
    500: "Internal Server Error - Something exploded!",
  };

  function reqStr(r) { return "[" + r.timestamp + "] " + r.source_ip + ' "' + r.method + " " + r.resource + '" -> ' + r.status_code; }

  function displayRequests(list) {
    if (list.length === 0) { term.print("  No requests found."); return; }
    list.forEach((r, i) => {
      term.print("  " + (i + 1) + ". " + reqStr(r));
      term.print("     " + (statusMeanings[r.status_code] || "Unknown Status"));
    });
  }

  const requests = webTrafficRecords;

  while (true) {
    term.print("\n==================================================");
    term.print("WEB TRAFFIC LOG ANALYZER");
    term.print("==================================================");
    term.print("1. View all captured requests");
    term.print("2. Show error incidents (4xx, 5xx)");
    term.print("3. Response code statistics");
    term.print("4. View unique client IPs");
    term.print("5. Filter by IP address");
    term.print("6. Filter by HTTP method (GET, POST, etc.)");
    term.print("7. Hunt for the suspicious client");
    term.print("8. Exit");
    term.print("==================================================");
    const choice = await term.input("Select an option (1-8): ");

    if (choice === "1") {
      term.print("\nALL CAPTURED REQUESTS:");
      displayRequests(requests);
    } else if (choice === "2") {
      term.print("\nERROR INCIDENTS DETECTED:");
      const incidents = requests.filter(r => r.status_code >= 400);
      if (incidents.length) { term.print("  Found " + incidents.length + " incident(s)!"); displayRequests(incidents); }
      else { term.print("  No incidents found. All good!"); }
    } else if (choice === "3") {
      term.print("\nRESPONSE CODE STATISTICS:");
      const counts = {};
      requests.forEach(r => { counts[r.status_code] = (counts[r.status_code] || 0) + 1; });
      Object.keys(counts).sort().forEach(code => {
        const bar = "█".repeat(counts[code]);
        term.print("  " + code + ": " + bar + " (" + counts[code] + ")");
      });
    } else if (choice === "4") {
      term.print("\nUNIQUE CLIENT IP ADDRESSES:");
      const ips = [...new Set(requests.map(r => r.source_ip))].sort();
      ips.forEach((ip, i) => {
        const count = requests.filter(r => r.source_ip === ip).length;
        term.print("  " + (i + 1) + ". " + ip + " - " + count + " request(s)");
      });
    } else if (choice === "5") {
      const targetIp = await term.input("Enter IP address to filter (e.g., 192.168.1.1): ");
      const filtered = requests.filter(r => r.source_ip === targetIp);
      term.print("\nREQUESTS FROM " + targetIp + ":");
      displayRequests(filtered);
    } else if (choice === "6") {
      const method = (await term.input("Enter HTTP method (GET, POST, PUT, DELETE): ")).toUpperCase();
      const filtered = requests.filter(r => r.method === method);
      term.print("\n" + method + " REQUESTS:");
      displayRequests(filtered);
    } else if (choice === "7") {
      term.print("\nSUSPICIOUS ACTIVITY HUNT...");
      const incidents = requests.filter(r => r.status_code >= 400);
      if (incidents.length) {
        const susIp = incidents[0].source_ip;
        term.print("ALERT: " + susIp + " made multiple failed requests!");
        term.print("Details:");
        displayRequests(requests.filter(r => r.source_ip === susIp));
      } else { term.print("No suspicious activity detected. Nice work!"); }
    } else if (choice === "8") {
      const msgs = [
        "May your logs be clean and your traffic be encrypted!",
        "Keep those firewalls strong!",
        "Happy packet sniffing!",
        "Remember: No logging, no evidence! (Just kidding.)",
        "Keep calm and analyze on!"
      ];
      term.print("\n" + msgs[Math.floor(Math.random() * msgs.length)]);
      break;
    } else { term.print("Invalid choice. Please try again."); }
  }
}

// ============================================================
// Script Registry
// ============================================================
const SCRIPT_REGISTRY = {
  password_manager_enhanced: passwordManagerScript,
  file_manager_enhanced: fileManagerScript,
  network_device_manager_enhanced: networkDeviceManagerScript,
  log_parsing_analysis: logParsingAnalysisScript,
};
