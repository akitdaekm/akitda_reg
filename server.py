"""
AKITDA Event & Member Management Suite - Server
A robust, multi-threaded pure-Python HTTP Server with SQLite REST API,
zero external pip dependencies required.
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import mimetypes
import socket
import sys
from datetime import datetime

import db

PORT = int(os.environ.get("PORT", 5000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class AkitdaRequestHandler(http.server.BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        # Clean logging format
        sys.stderr.write(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]} {args[1]}\n")

    def send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # --- REST API ROUTES ---
        if path == '/api/stats':
            stats = db.get_stats()
            self.send_json(stats)
            return

        elif path == '/api/members':
            q = query.get('q', [''])[0]
            limit = int(query.get('limit', [250])[0])
            members = db.search_members(q, limit)
            self.send_json({'members': members, 'count': len(members)})
            return

        elif path == '/api/registrations':
            search = query.get('q', [''])[0]
            regs = db.get_registrations(search)
            self.send_json({'registrations': regs, 'count': len(regs)})
            return

        elif path == '/api/scans':
            scans = db.get_scans()
            self.send_json({'scans': scans, 'count': len(scans)})
            return

        elif path == '/api/renewals':
            q = query.get('q', [''])[0]
            renewals = db.get_renewals(q)
            self.send_json({'renewals': renewals, 'count': len(renewals)})
            return

        elif path == '/api/users':
            users = db.get_users()
            self.send_json({'users': users, 'count': len(users)})
            return

        elif path == '/api/settings':
            settings = db.get_settings()
            self.send_json({'settings': settings})
            return

        elif path == '/api/export/renewals-csv':
            csv_str = db.export_renewals_csv_string()
            body = csv_str.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="akitda_membership_renewals.csv"')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        elif path == '/api/network-info':
            local_ip = get_local_ip()
            hostname = socket.gethostname()
            self.send_json({
                'local_ip': local_ip,
                'port': PORT,
                'network_url': f"http://{local_ip}:{PORT}",
                'local_url': f"http://localhost:{PORT}",
                'hostname': hostname
            })
            return

        elif path == '/api/export/csv':
            csv_str = db.export_scans_csv_string()
            body = csv_str.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="akitda_attendance.csv"')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        elif path == '/api/export/registrations-csv':
            csv_str = db.export_registrations_csv_string()
            body = csv_str.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="akitda_registered_passes.csv"')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # --- FRIENDLY PAGE ROUTING ---
        route_map = {
            '/': 'portal.html',
            '/portal': 'portal.html',
            '/scan': 'scan.html',
            '/scanner': 'scan.html',
            '/register': 'register.html',
            '/registration': 'register.html',
            '/viewer': 'Data-Viewer.html',
            '/data-viewer': 'Data-Viewer.html',
            '/renewal': 'renewal.html',
            '/members': 'portal.html',
            '/passes': 'view.html',
            '/registered': 'view.html',
            '/view': 'view.html',
            '/view.html': 'view.html'
        }

        if path in route_map:
            file_name = route_map[path]
            file_path = os.path.join(BASE_DIR, file_name)
            self.serve_static_file(file_path)
            return

        # Static files in root or static/
        clean_path = path.lstrip('/')
        # Check in BASE_DIR directly
        target_path = os.path.join(BASE_DIR, clean_path)
        if os.path.isfile(target_path):
            self.serve_static_file(target_path)
            return

        # 404 Not Found
        self.send_error(404, f"File not found: {path}")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else '{}'
        
        try:
            body = json.loads(post_body) if post_body.strip() else {}
        except Exception:
            body = {}

        if path == '/api/register':
            name = body.get('name', '').strip()
            company = body.get('company', '').strip()
            designation = body.get('designation', 'Member').strip()
            district = body.get('district', 'Ernakulam').strip()
            phone = body.get('phone', '').strip()
            email = body.get('email', '').strip()

            if not name or not company or not phone:
                self.send_json({'status': 'error', 'message': 'Name, company, and phone are required.'}, 400)
                return

            reg = db.register_member(name, company, designation, district, phone, email)
            self.send_json({'status': 'success', 'registration': reg})
            return

        elif path == '/api/scan':
            code = body.get('code', '').strip()
            if not code:
                self.send_json({'status': 'error', 'message': 'No code provided.'}, 400)
                return

            result = db.record_scan(code)
            self.send_json(result)
            return

        elif path == '/api/scans/clear':
            db.clear_all_scans()
            self.send_json({'status': 'success', 'message': 'All scans cleared.'})
            return

        elif path == '/api/renew':
            member_name = body.get('member_name', '').strip()
            company_name = body.get('company_name', '').strip()
            phone = body.get('phone', '').strip()
            amount = float(body.get('amount', 1416.00))
            upi_ref = body.get('upi_ref', '').strip()

            if not member_name or not company_name:
                self.send_json({'status': 'error', 'message': 'Member name and company name are required.'}, 400)
                return

            rec = db.add_renewal(member_name, company_name, phone, amount, upi_ref)
            self.send_json({'status': 'success', 'renewal': rec})
            return

        elif path == '/api/auth/login':
            username = body.get('username', '').strip()
            password = body.get('password', '').strip()
            user = db.verify_user(username, password)
            if user:
                self.send_json({'status': 'success', 'user': user, 'message': 'Authentication successful'})
            else:
                self.send_json({'status': 'error', 'message': 'Invalid username or password'}, 401)
            return

        elif path == '/api/auth/change-password':
            username = body.get('username', '').strip()
            old_password = body.get('old_password', '').strip()
            new_password = body.get('new_password', '').strip()
            is_override = bool(body.get('admin_override', False))
            res = db.change_password(username, old_password, new_password, is_override)
            code = 200 if res.get('status') == 'success' else 400
            self.send_json(res, code)
            return

        elif path == '/api/users':
            username = body.get('username', '').strip()
            password = body.get('password', '').strip()
            full_name = body.get('full_name', '').strip()
            role = body.get('role', 'staff').strip()
            res = db.create_user(username, password, full_name, role)
            code = 201 if res.get('status') == 'success' else 400
            self.send_json(res, code)
            return

        elif path == '/api/users/toggle-active':
            user_id = int(body.get('user_id', 0))
            res = db.toggle_user_active(user_id)
            code = 200 if res.get('status') == 'success' else 400
            self.send_json(res, code)
            return

        elif path == '/api/settings':
            updated = db.update_settings(body)
            self.send_json({'status': 'success', 'settings': updated, 'message': 'Settings updated successfully'})
            return

        self.send_error(404, "Endpoint not found")

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith('/api/scans/'):
            try:
                scan_id = int(path.split('/')[-1])
                db.delete_scan(scan_id)
                self.send_json({'status': 'success', 'message': f'Scan {scan_id} deleted.'})
            except Exception as e:
                self.send_json({'status': 'error', 'message': str(e)}, 400)
            return

        elif path.startswith('/api/registrations/'):
            try:
                reg_id = int(path.split('/')[-1])
                db.delete_registration(reg_id)
                self.send_json({'status': 'success', 'message': f'Registration {reg_id} deleted.'})
            except Exception as e:
                self.send_json({'status': 'error', 'message': str(e)}, 400)
            return

        elif path.startswith('/api/renewals/'):
            try:
                ren_id = int(path.split('/')[-1])
                db.delete_renewal(ren_id)
                self.send_json({'status': 'success', 'message': f'Renewal {ren_id} deleted.'})
            except Exception as e:
                self.send_json({'status': 'error', 'message': str(e)}, 400)
            return

        elif path.startswith('/api/users/'):
            try:
                user_id = int(path.split('/')[-1])
                res = db.delete_user(user_id)
                code = 200 if res.get('status') == 'success' else 400
                self.send_json(res, code)
            except Exception as e:
                self.send_json({'status': 'error', 'message': str(e)}, 400)
            return

        self.send_error(404, "Endpoint not found")

    def serve_static_file(self, file_path):
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            self.send_error(404, "File not found")
            return

        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        if file_path.endswith('.js'):
            mime_type = 'application/javascript; charset=utf-8'
        elif file_path.endswith('.css'):
            mime_type = 'text/css; charset=utf-8'
        elif file_path.endswith('.html'):
            mime_type = 'text/html; charset=utf-8'

        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Access-Control-Allow-Origin', '*')
            # Disable caching for active development/refresh
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def start_server(port=None):
    if port is None:
        port = int(os.environ.get("PORT", 5000))
    db.init_db()
    server_address = ('0.0.0.0', port)
    httpd = ThreadedHTTPServer(server_address, AkitdaRequestHandler)
    local_ip = get_local_ip()
    
    print("=" * 65)
    print("  AKITDA Event & Member Management Suite Server Running!  ")
    print("=" * 65)
    print(f"  * Local / Cloud:    http://0.0.0.0:{port}")
    print(f"  * Local Network:    http://{local_ip}:{port}")
    print("=" * 65)
    print("  Available Modules:")
    print(f"  1. Unified Portal:     http://localhost:{port}/")
    print(f"  2. USB Badge Scanner:  http://localhost:{port}/scan")
    print(f"  3. Registration Desk:  http://localhost:{port}/register")
    print(f"  4. Live Attendance:    http://localhost:{port}/viewer")
    print(f"  5. Member Renewal:     http://localhost:{port}/renewal")
    print("=" * 65)
    print("  Press Ctrl+C to stop the server.\n")

    try:
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print("\nStopping server...")
    finally:
        httpd.shutdown()
        httpd.server_close()

if __name__ == '__main__':
    start_server()
