import os
import subprocess
import tempfile
import re
from flask import Flask, request, jsonify, render_template






app = Flask(__name__, static_url_path='/static', static_folder='static')

class CodeCompiler:
    """Handles compilation and execution of different programming languages"""
    
    SUPPORTED_LANGUAGES = {
        'rust': 'rs',
        'python': 'py',
        'c': 'c',
        'cpp': 'cpp'
    }
    
    EXECUTION_TIMEOUT = 5
    BUILD_TIMEOUT = 30
    
    def __init__(self):
        self.temp_dir = None
    
    def _create_source_file(self, code, language):
        """Create source file in temporary directory"""
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")
        
        file_ext = self.SUPPORTED_LANGUAGES[language]
        source_file_path = os.path.join(self.temp_dir, f"main.{file_ext}")
        
        with open(source_file_path, "w") as source_file:
            source_file.write(code)
        
        return source_file_path
    
    def _execute_python(self, source_file_path, user_input):
        """Execute Python code"""
        try:
            process = subprocess.Popen(
                ["python", source_file_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=user_input, timeout=self.EXECUTION_TIMEOUT)
            
            return {
                "success": True,
                "compile_error": "",
                "output": stdout,
                "runtime_error": stderr
            }
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "success": False,
                "compile_error": "",
                "output": "",
                "runtime_error": f"Program execution timed out (limit: {self.EXECUTION_TIMEOUT} seconds)"
            }
    
    def _needs_cargo(self, code):
        """Check if Rust code needs Cargo for external dependencies"""
        dependencies = []
        extern_crate_pattern = re.compile(r'extern crate (\w+);')
        use_crate_pattern = re.compile(r'use (\w+)::')
        
        for line in code.splitlines():
            extern_match = extern_crate_pattern.search(line)
            if extern_match:
                dependencies.append(extern_match.group(1))
            
            use_match = use_crate_pattern.search(line)
            if use_match and use_match.group(1) not in ['std', 'core', 'alloc']:
                dependencies.append(use_match.group(1))
        
        return len(dependencies) > 0, list(set(dependencies))
    
    def _create_cargo_project(self, code, dependencies):
        """Create Cargo project for Rust code with dependencies"""
        cargo_dir = os.path.join(self.temp_dir, "rust_project")
        os.makedirs(os.path.join(cargo_dir, "src"), exist_ok=True)
        
        # Write main.rs
        with open(os.path.join(cargo_dir, "src", "main.rs"), "w") as f:
            f.write(code)
        
        # Write Cargo.toml
        toml_content = '[package]\nname = "rust_project"\nversion = "0.1.0"\nedition = "2021"\n\n[dependencies]\n'
        for dep in dependencies:
            toml_content += f'{dep} = "*"\n'
        
        with open(os.path.join(cargo_dir, "Cargo.toml"), "w") as f:
            f.write(toml_content)
        
        return cargo_dir
    
    def _execute_cargo_project(self, cargo_dir, user_input):
        """Build and run Cargo project"""
        try:
            # Build project
            build_result = subprocess.run(
                ["cargo", "build", "--release"],
                cwd=cargo_dir,
                capture_output=True,
                text=True,
                timeout=self.BUILD_TIMEOUT
            )
            
            if build_result.returncode != 0:
                return {
                    "success": False,
                    "compile_error": build_result.stderr,
                    "output": ""
                }
            
            # Run project
            run_process = subprocess.Popen(
                ["cargo", "run", "--release"],
                cwd=cargo_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = run_process.communicate(input=user_input, timeout=self.EXECUTION_TIMEOUT)
            
            return {
                "success": True,
                "compile_error": "",
                "output": stdout,
                "runtime_error": stderr
            }
            
        except subprocess.TimeoutExpired as e:
            if 'run_process' in locals():
                run_process.kill()
            return {
                "success": False,
                "compile_error": "",
                "output": "",
                "runtime_error": f"Process timed out: {str(e)}"
            }
    
    def _compile_and_run_executable(self, source_file_path, compiler_cmd, user_input):
        """Compile and run executable for C/C++/Rust"""
        executable_path = os.path.join(self.temp_dir, "main.exe")
        compile_cmd = compiler_cmd + [source_file_path, "-o", executable_path]
        
        # Compile
        compile_result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True
        )
        
        if compile_result.returncode != 0:
            return {
                "success": False,
                "compile_error": compile_result.stderr,
                "output": ""
            }
        
        # Run
        try:
            run_process = subprocess.Popen(
                [executable_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = run_process.communicate(input=user_input, timeout=self.EXECUTION_TIMEOUT)
            
            return {
                "success": True,
                "compile_error": "",
                "output": stdout,
                "runtime_error": stderr
            }
            
        except subprocess.TimeoutExpired:
            run_process.kill()
            return {
                "success": False,
                "compile_error": "",
                "output": "",
                "runtime_error": f"Program execution timed out (limit: {self.EXECUTION_TIMEOUT} seconds)"
            }
    
    def compile_and_execute(self, code, user_input, language, compiler_options):
        """Main method to compile and execute code"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                self.temp_dir = temp_dir
                source_file_path = self._create_source_file(code, language)
                
                if language == 'python':
                    return self._execute_python(source_file_path, user_input)
                
                elif language == 'rust':
                    needs_cargo, dependencies = self._needs_cargo(code)
                    
                    if needs_cargo:
                        cargo_dir = self._create_cargo_project(code, dependencies)
                        return self._execute_cargo_project(cargo_dir, user_input)
                    else:
                        compiler_cmd = ["rustc"] + list(compiler_options)
                        return self._compile_and_run_executable(source_file_path, compiler_cmd, user_input)
                
                elif language == 'c':
                    compiler_cmd = ["gcc"] + list(compiler_options)
                    return self._compile_and_run_executable(source_file_path, compiler_cmd, user_input)
                
                elif language == 'cpp':
                    compiler_cmd = ["g++"] + list(compiler_options)
                    return self._compile_and_run_executable(source_file_path, compiler_cmd, user_input)
                
        except Exception as e:
            return {
                "success": False,
                "compile_error": f"Internal error: {str(e)}",
                "output": "",
                "runtime_error": ""
            }

# Global compiler instance
compiler = CodeCompiler()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile_and_run():
    """Handle code compilation and execution requests"""
    try:
        code = request.form.get('code', '')
        user_input = request.form.get('input', '')
        language = request.form.get('language', 'rust')
        compiler_options = request.form.get('options', '').split()
        
        if not code.strip():
            return jsonify({
                "success": False,
                "compile_error": "No code provided",
                "output": "",
                "runtime_error": ""
            })
        
        result = compiler.compile_and_execute(code, user_input, language, compiler_options)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "compile_error": f"Request processing error: {str(e)}",
            "output": "",
            "runtime_error": ""
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
