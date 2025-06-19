import os
import subprocess
import tempfile
from flask import Flask, request, render_template, jsonify, send_from_directory

app = Flask(__name__, static_url_path='/static', static_folder='static')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
