from flask import Flask, render_template, request
import subprocess, tempfile, os

app = Flask(__name__)

def check_and_run_code(language, code, program_input):
    if language == "java":
        with tempfile.TemporaryDirectory() as tmpdir:
            java_file = os.path.join(tmpdir, "Main.java")
            with open(java_file, "w") as f:
                f.write(code)

            compile_proc = subprocess.run(["javac", java_file],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if compile_proc.returncode != 0:
                return compile_proc.stderr, None

            run_proc = subprocess.run(["java", "-cp", tmpdir, "Main"],
                                      input=program_input,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return "✅ Java code is syntactically correct.", run_proc.stdout if run_proc.stdout else run_proc.stderr

    elif language == "python":
        try:
            compile(code, "<string>", "exec")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmpfile:
                tmpfile.write(code.encode("utf-8"))
                tmpfile_path = tmpfile.name

            run_proc = subprocess.run(["python", tmpfile_path],
                                      input=program_input,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return "✅ Python code is syntactically correct.", run_proc.stdout if run_proc.stdout else run_proc.stderr
        except SyntaxError as e:
            return str(e), None

    elif language == "javascript":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".js") as tmpfile:
            tmpfile.write(code.encode("utf-8"))
            tmpfile_path = tmpfile.name

        run_proc = subprocess.run(["node", tmpfile_path],
                                  input=program_input,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if run_proc.returncode == 0:
            return "✅ JavaScript code is syntactically correct.", run_proc.stdout
        else:
            return run_proc.stderr, None

    elif language == "c":
        with tempfile.TemporaryDirectory() as tmpdir:
            c_file = os.path.join(tmpdir, "program.c")
            exe_file = os.path.join(tmpdir, "program.exe")
            with open(c_file, "w") as f:
                f.write(code)

            compile_proc = subprocess.run(["gcc", c_file, "-o", exe_file],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if compile_proc.returncode != 0:
                return compile_proc.stderr, None

            run_proc = subprocess.run([exe_file],
                                      input=program_input,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return "✅ C code is syntactically correct.", run_proc.stdout if run_proc.stdout else run_proc.stderr

    return "❌ Language not supported", None


@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    output = ""
    code = ""
    program_input = ""
    language = "java"
    if request.method == "POST":
        language = request.form["language"]
        code = request.form["code"]
        program_input = request.form["program_input"]
        result, output = check_and_run_code(language, code, program_input)
    return render_template("index.html", result=result, output=output, code=code, program_input=program_input, language=language)


if __name__ == "__main__":
    app.run(debug=True)
