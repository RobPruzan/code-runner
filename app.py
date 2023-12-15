import json
import sys
from flask import Flask, request, jsonify, make_response
import subprocess
import shlex
import uuid
import os

app = Flask(__name__)
parse_var = "\P"

error_var = "\E"


def parse_output(out: str):
    pre = [""]
    post = [""]
    err = False
    for idx in range(len(out)):
        if idx == len(out):
            return
        if out[idx : idx + 2] == error_var:
            err = True
            pre[0] = out[:idx]
            post[0] = out[idx + 2 :]
            return pre[0], post[0], err
        if out[idx : idx + 2] == parse_var:
            pre[0] = out[:idx]
            post[0] = out[idx + 2 :]
            return pre[0], post[0], err
    return pre[0], post[0], err


python_executable = sys.executable
languages = {
    "python": {
        "interpreter": python_executable,
        "extension": ".py",
    },
    "java": {
        "interpreter": "javac",
        "extension": ".java",
        # java doesn't work need to parse in the env var
        "env_code": "",
    },
    "rust": {
        "interpreter": "rustc",
        "extension": ".rs",
        "env_code": "",  # Parsing JSON in Rust is non-trivial and would require a library like serde_json.
    },
    "go": {
        "interpreter": "go",
        "extension": ".go",
    },
}


@app.after_request
def add_cors_headers(response):
    print("got response")
    response.headers.add("Access-Control-Allow-Origin", "*")
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Methods"] = "POST"
        headers = request.headers.get("Access-Control-Request-Headers")  # type:ignore

        if headers:
            response.headers["Access-Control-Allow-Headers"] = headers
    return response


@app.route("/execute", methods=["POST", "OPTIONS"])
def execute_code():
    print("oy")
    if request.method == "OPTIONS":
        return make_response(("Allowed", 204))
    data = request.get_json()  # type: ignore
    print(f"{data=}")
    code = data.get("code")
    interpreter = languages["python"]["interpreter"]

    filename = "/tmp/code" + str(uuid.uuid4()) + languages["python"]["extension"]
    with open(filename, "w") as file:
        file.write(code)
    run_command = f"{interpreter} {filename}"
    result = subprocess.run(
        shlex.split(run_command),
        timeout=1,
        capture_output=True,
    )

    stdout = result.stdout.decode()
    stderr = result.stderr.decode()

    return {"stdout": stdout, "stderr": stderr}


@app.route("/run", methods=["POST", "OPTIONS"])
def graph_runner():
    if request.method == "OPTIONS":
        return make_response(("Allowed", 204))
    data = request.get_json()  # type: ignore
    lang = data.get("lang")
    code = data.get("code")
    code = code.replace(": NodeID", "") if lang != "typescript" else code
    env = data.get("env")
    # print("env res", env)

    if lang not in languages:
        return jsonify({"error": "Unsupported language"}), 400

    filename = "/tmp/code" + str(uuid.uuid4()) + languages[lang]["extension"]
    setup_code_name = f"exec_{lang}" + languages[lang]["extension"]

    with open(setup_code_name, "r") as file:
        full_code = str(code + "\n" + file.read())

    with open(filename, "w") as file:
        file.write(full_code)
    stderr = ""
    stdout = ""
    try:
        interpreter = languages[lang]["interpreter"]
        # if lang in ["c", "c++", "rust"]:
        #     compile_command = f"{interpreter} {filename} -o {filename}.out"
        #     subprocess.run(shlex.split(compile_command), check=True)
        #     run_command = f"./{filename}.out"
        # elif lang == "java":
        #     # Java needs special treatment because of the way javac works
        #     compile_command = f"{interpreter} {filename}"
        #     subprocess.run(shlex.split(compile_command), check=True)
        #     run_command = (
        #         f"java -cp /tmp {os.path.splitext(os.path.basename(filename))[0]}"
        #     )
        # else:
        run_command = f"{interpreter} {filename}"

        result = subprocess.run(
            shlex.split(run_command),
            timeout=1,
            capture_output=True,
            env=env,
        )

        stdout = result.stdout.decode()

        stderr = result.stderr.decode()

        output = stdout if not stderr else stderr
    except Exception as e:
        output = str(e)
    print("caught exception:", output)
    logs, out, err = parse_output(output)  # type:ignore
    if stderr:
        return jsonify({"type": "error", "logs": [stderr]})
    out = json.loads(out)
    out = out if out is not None else []

    logs = logs if logs else ""

    return {"output": out, "logs": logs}


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
