from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import platform
import string
from pathlib import Path
from collections import defaultdict
import mimetypes

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

def get_all_drives():
    """Get all available drives on the system"""
    drives = []
    system = platform.system()
    
    if system == "Windows":
        # Windows: check all drive letters
        import ctypes
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    try:
                        drive_name = f"{letter}: Drive"
                        # Try to get volume name
                        try:
                            import win32api
                            volume_info = win32api.GetVolumeInformation(drive)
                            if volume_info[0]:
                                drive_name = f"{letter}: ({volume_info[0]})"
                        except:
                            pass
                        drives.append({"path": drive, "name": drive_name})
                    except:
                        pass
            bitmask >>= 1
    else:
        # Unix-like systems
        drives.append({"path": "/", "name": "Root (/)"})
        # Check common mount points
        if os.path.exists("/mnt"):
            for mount in os.listdir("/mnt"):
                mount_path = f"/mnt/{mount}"
                if os.path.ismount(mount_path):
                    drives.append({"path": mount_path, "name": f"Mount ({mount})"})
        if os.path.exists("/media"):
            try:
                for user in os.listdir("/media"):
                    user_path = f"/media/{user}"
                    if os.path.isdir(user_path):
                        for mount in os.listdir(user_path):
                            mount_path = f"{user_path}/{mount}"
                            if os.path.ismount(mount_path):
                                drives.append({"path": mount_path, "name": f"Media ({mount})"})
            except:
                pass
    
    return drives

def categorize_file_type(ext):
    """Categorize file extensions into common groups"""
    categories = {
        "PDF": [".pdf"],
        "Excel": [".xlsx", ".xls", ".xlsm", ".xlsb", ".csv"],
        "Word": [".docx", ".doc", ".docm", ".dotx", ".dotm"],
        "PowerPoint": [".pptx", ".ppt", ".pptm"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".tif", ".raw", ".heic"],
        "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg", ".3gp"],
        "Music": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus", ".ape"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
        "Code": [".py", ".js", ".java", ".cpp", ".c", ".cs", ".php", ".html", ".css", ".ts", ".jsx", ".tsx", ".go", ".rs", ".rb", ".swift"],
        "Text": [".txt", ".md", ".rtf", ".log", ".ini", ".cfg", ".conf", ".json", ".xml", ".yaml", ".yml"],
        "Executables": [".exe", ".msi", ".app", ".deb", ".rpm", ".apk", ".dmg"],
        "Databases": [".db", ".sqlite", ".mdb", ".accdb", ".sql"],
    }
    
    ext_lower = ext.lower()
    for category, extensions in categories.items():
        if ext_lower in extensions:
            return category
    
    return "Others"

def scan_filesystem():
    """Scan entire filesystem and gather statistics per drive"""
    drives = get_all_drives()
    drive_results = []
    
    for drive_info in drives:
        drive_path = drive_info["path"]
        drive_name = drive_info["name"]
        
        file_types = defaultdict(int)
        categories = defaultdict(int)
        total_files = 0
        
        try:
            for root, dirs, files in os.walk(drive_path):
                # Skip system and restricted directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['$RECYCLE.BIN', 'System Volume Information', 'Windows', 'Program Files', 'Program Files (x86)']]
                
                for file in files:
                    try:
                        total_files += 1
                        ext = Path(file).suffix.lower()
                        
                        if ext:
                            file_types[ext] += 1
                            category = categorize_file_type(ext)
                            categories[category] += 1
                        else:
                            file_types["[no extension]"] += 1
                            categories["Others"] += 1
                            
                    except Exception:
                        continue
                        
        except (PermissionError, OSError):
            pass
        
        drive_results.append({
            "drive_name": drive_name,
            "drive_path": drive_path,
            "total_files": total_files,
            "categories": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)),
            "file_types": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True))
        })
    
    return {
        "total_drives": len(drive_results),
        "drives": drive_results
    }

def is_text_file(filepath):
    """Check if file is likely a text file"""
    text_extensions = {'.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.md', 
                      '.csv', '.log', '.ini', '.conf', '.yaml', '.yml', '.sh', '.bat',
                      '.c', '.cpp', '.h', '.java', '.php', '.rb', '.go', '.rs', '.sql',
                      '.doc', '.docx', '.rtf'}
    
    ext = Path(filepath).suffix.lower()
    if ext in text_extensions:
        return True
    
    mime_type, _ = mimetypes.guess_type(filepath)
    if mime_type and mime_type.startswith('text'):
        return True
    
    return False

def search_in_files(keyword):
    """Search for keyword in text files across filesystem"""
    results = []
    total_occurrences = 0
    files_scanned = 0
    
    drives = get_all_drives()
    
    for drive_info in drives:
        drive_path = drive_info["path"]
        
        try:
            for root, dirs, files in os.walk(drive_path):
                # Skip system and restricted directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['$RECYCLE.BIN', 'System Volume Information', 'Windows', 'Program Files', 'Program Files (x86)']]
                
                for file in files:
                    filepath = os.path.join(root, file)
                    
                    if not is_text_file(filepath):
                        continue
                    
                    try:
                        files_scanned += 1
                        
                        content = None
                        for encoding in ['utf-8', 'latin-1', 'cp1252']:
                            try:
                                with open(filepath, 'r', encoding=encoding) as f:
                                    content = f.read()
                                break
                            except:
                                continue
                        
                        if content:
                            count = content.lower().count(keyword.lower())
                            if count > 0:
                                results.append({
                                    "filepath": filepath,
                                    "filename": file,
                                    "occurrences": count,
                                    "drive": drive_info["name"]
                                })
                                total_occurrences += count
                                
                    except Exception:
                        continue
                        
        except (PermissionError, OSError):
            continue
    
    return {
        "keyword": keyword,
        "files_scanned": files_scanned,
        "files_found": len(results),
        "total_occurrences": total_occurrences,
        "results": sorted(results, key=lambda x: x['occurrences'], reverse=True)[:100]
    }

@app.route('/scan', methods=['GET'])
def scan():
    """Endpoint to scan filesystem"""
    try:
        result = scan_filesystem()
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    """Endpoint to search for keyword in files"""
    try:
        data = request.get_json()
        keyword = data.get('keyword', '').strip()
        
        if not keyword:
            return jsonify({"success": False, "error": "Keyword is required"}), 400
        
        result = search_in_files(keyword)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "File Scanner API is running"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)