import os
import subprocess
import tempfile
from flask import Flask, request, render_template, jsonify, send_from_directory, abort
from sqlalchemy.orm import Session # For type hinting
import database # Import the database module

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Database session management for Flask routes
@app.before_request
def before_request():
    # This makes a new session available for each request
    # and closes it when the request context ends.
    # However, for Flask, it's often better to manage sessions per request explicitly
    # or use a Flask extension like Flask-SQLAlchemy for more robust session handling.
    # For this simple case, we'll get a session from database.py when needed.
    pass

@app.teardown_appcontext
def shutdown_session(exception=None):
    # This would be used if we attached a session to g.
    # database.SessionLocal.remove() # If using scoped_session
    pass


@app.route('/', methods=['GET'])
def index():
    # Ensure database tables are created if they don't exist when app starts
    # This is a good place if not running database.py directly earlier
    # Moved to app.py or a startup script for PySide6 app to avoid issues with multiple initializations
    # database.create_db_tables()
    return render_template('index.html')

# --- API Routes for Code History ---

@app.route('/api/save_code', methods=['POST'])
def save_code_route():
    data = request.get_json()
    if not data or 'language' not in data or 'code' not in data:
        return jsonify({"success": False, "error": "Missing language or code"}), 400

    language = data['language']
    code = data['code']
    title = data.get('title') # Optional title from frontend

    db_session = next(database.get_db())
    try:
        entry = database.add_code_history(db_session, language, code, title)
        return jsonify({"success": True, "id": entry.id, "title": entry.title, "message": "Code saved successfully."})
    except Exception as e:
        db_session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db_session.close()

@app.route('/api/history', methods=['GET'])
def get_history_route():
    db_session = next(database.get_db())
    try:
        history_entries = database.get_all_code_history(db_session)
        # Convert SQLAlchemy objects to dictionaries for JSON serialization
        history_list = [
            {
                "id": entry.id,
                "language": entry.language,
                "code": entry.code, # Consider if sending full code always is okay, or just snippet/title
                "title": entry.title,
                "timestamp": entry.timestamp.isoformat()
            } for entry in history_entries
        ]
        return jsonify({"success": True, "history": history_list})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db_session.close()

@app.route('/api/history/<int:entry_id>', methods=['GET'])
def get_history_entry_route(entry_id):
    db_session = next(database.get_db())
    try:
        entry = database.get_code_history_by_id(db_session, entry_id)
        if entry:
            return jsonify({
                "success": True,
                "id": entry.id,
                "language": entry.language,
                "code": entry.code,
                "title": entry.title,
                "timestamp": entry.timestamp.isoformat()
            })
        else:
            return jsonify({"success": False, "error": "Entry not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db_session.close()


@app.route('/api/history/<int:entry_id>', methods=['DELETE'])
def delete_history_entry_route(entry_id):
    db_session = next(database.get_db())
    try:
        success = database.delete_code_history_by_id(db_session, entry_id)
        if success:
            return jsonify({"success": True, "message": "Entry deleted successfully."})
        else:
            return jsonify({"success": False, "error": "Entry not found or could not be deleted."}), 404
    except Exception as e:
        db_session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db_session.close()


@app.route('/compile', methods=['POST'])
def compile_and_run():
    code = request.form.get('code', '')
    user_input = request.form.get('input', '')
    language = request.form.get('language', 'rust')
    compiler_options = request.form.get('options', '').split()
    
    # Create temporary directory for the code and compiled output
    with tempfile.TemporaryDirectory() as temp_dir:
        # File extension and command settings based on language
        file_extensions = {
            'rust': 'rs',
            'python': 'py',
            'c': 'c',
            'cpp': 'cpp'
        }
        
        if language not in file_extensions:
            return jsonify({
                "success": False,
                "compile_error": f"Unsupported language: {language}",
                "output": ""
            })
        
        file_ext = file_extensions[language]
        source_file_path = os.path.join(temp_dir, f"main.{file_ext}")
        
        # Write code to the source file
        with open(source_file_path, "w") as source_file:
            source_file.write(code)
        
        # Execute based on language
        if language == 'python':
            # Python is interpreted, no compilation needed
            try:
                run_process = subprocess.Popen(
                    ["python", source_file_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = run_process.communicate(input=user_input, timeout=5)
                
                return jsonify({
                    "success": True,
                    "compile_error": "",
                    "output": stdout,
                    "runtime_error": stderr
                })
            except subprocess.TimeoutExpired:
                run_process.kill()
                return jsonify({
                    "success": False,
                    "compile_error": "",
                    "output": "",
                    "runtime_error": "Program execution timed out (limit: 5 seconds)"
                })
                
        elif language == 'rust':
            # Compile Rust code
            executable_path = os.path.join(temp_dir, "main.exe")
            
            # Prepare rustc command with user-provided options
            rustc_cmd = ["rustc", source_file_path, "-o", executable_path]
            # Add any additional compiler options
            if compiler_options:
                rustc_cmd.extend(compiler_options)
            
            # Compile the Rust code
            compile_result = subprocess.run(
                rustc_cmd,
                capture_output=True,
                text=True
            )
            
            if compile_result.returncode != 0:
                return jsonify({
                    "success": False,
                    "compile_error": compile_result.stderr,
                    "output": ""
                })
            
        elif language == 'c':
            # Compile C code
            executable_path = os.path.join(temp_dir, "main.exe")
            
            # Prepare gcc command with user-provided options
            gcc_cmd = ["gcc", source_file_path, "-o", executable_path]
            # Add any additional compiler options
            if compiler_options:
                gcc_cmd.extend(compiler_options)
            
            # Compile the C code
            compile_result = subprocess.run(
                gcc_cmd,
                capture_output=True,
                text=True
            )
            
            if compile_result.returncode != 0:
                return jsonify({
                    "success": False,
                    "compile_error": compile_result.stderr,
                    "output": ""
                })
                
        elif language == 'cpp':
            # Compile C++ code
            executable_path = os.path.join(temp_dir, "main.exe")
            
            # Prepare g++ command with user-provided options
            gpp_cmd = ["g++", source_file_path, "-o", executable_path]
            # Add any additional compiler options
            if compiler_options:
                gpp_cmd.extend(compiler_options)
            
            # Compile the C++ code
            compile_result = subprocess.run(
                gpp_cmd,
                capture_output=True,
                text=True
            )
            
            if compile_result.returncode != 0:
                return jsonify({
                    "success": False,
                    "compile_error": compile_result.stderr,
                    "output": ""
                })
        
        # Run the compiled program for compiled languages
        if language in ['rust', 'c', 'cpp']:
            try:
                run_process = subprocess.Popen(
                    [executable_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = run_process.communicate(input=user_input, timeout=5)
                
                return jsonify({
                    "success": True,
                    "compile_error": "",
                    "output": stdout,
                    "runtime_error": stderr
                })
            except subprocess.TimeoutExpired:
                run_process.kill()
                return jsonify({
                    "success": False,
                    "compile_error": "",
                    "output": "",
                    "runtime_error": "Program execution timed out (limit: 5 seconds)"
                })

# The Flask app instance
# To run the app, use the command: flask run

# To run with debug mode and specific host/port:
# flask run --debug --host=0.0.0.0 --port=5000

# The following block is commented out to prevent auto-run when imported
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
