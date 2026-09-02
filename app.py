import os
import sys
import uuid
import shutil
import subprocess

from flask import Flask, render_template, request, jsonify, send_file


# ============================================================
# APP
# ============================================================

app = Flask(__name__)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CODEFORMER_DIR = os.path.join(
    BASE_DIR,
    "CodeFormer"
)

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "uploads"
)

RESULT_DIR = os.path.join(
    BASE_DIR,
    "results"
)


os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# FIND FINAL CODEFORMER IMAGE
# ============================================================

def find_final_result(job_output_dir):

    # CodeFormer ka FULL result yahan hota hai
    final_results_dir = os.path.join(
        job_output_dir,
        "final_results"
    )

    print()
    print("SEARCHING FINAL RESULT:")
    print(final_results_dir)


    if not os.path.isdir(
        final_results_dir
    ):

        print(
            "final_results folder NOT FOUND"
        )

        return None


    for filename in os.listdir(
        final_results_dir
    ):

        if filename.lower().endswith(
            (
                ".png",
                ".jpg",
                ".jpeg",
                ".webp"
            )
        ):

            result_path = os.path.join(
                final_results_dir,
                filename
            )

            if os.path.isfile(
                result_path
            ):

                return result_path


    return None


# ============================================================
# ENHANCE
# ============================================================

@app.route(
    "/enhance",
    methods=["POST"]
)
def enhance():

    # --------------------------------------------------------
    # CHECK IMAGE
    # --------------------------------------------------------

    if "image" not in request.files:

        return jsonify({
            "success": False,
            "error": "Please select a photo"
        }), 400


    file = request.files["image"]


    if not file.filename:

        return jsonify({
            "success": False,
            "error": "Please select a photo"
        }), 400


    # --------------------------------------------------------
    # JOB ID
    # --------------------------------------------------------

    job_id = uuid.uuid4().hex


    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    input_filename = (
        job_id +
        "_input.jpg"
    )


    input_path = os.path.join(
        UPLOAD_DIR,
        input_filename
    )


    file.save(
        input_path
    )


    # --------------------------------------------------------
    # JOB OUTPUT DIRECTORY
    # --------------------------------------------------------

    job_output_dir = os.path.join(
        RESULT_DIR,
        job_id
    )


    os.makedirs(
        job_output_dir,
        exist_ok=True
    )


    # --------------------------------------------------------
    # LOG
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("CODEFORMER STARTED")
    print("=" * 60)

    print(
        "JOB     :",
        job_id
    )

    print(
        "INPUT   :",
        input_path
    )

    print(
        "WEIGHT  : 0.7"
    )

    print(
        "SCALE   : 1"
    )

    print(
        "OUTPUT  :",
        job_output_dir
    )

    print("=" * 60)


    # --------------------------------------------------------
    # CODEFORMER COMMAND
    # --------------------------------------------------------

    codeformer_script = os.path.join(
        CODEFORMER_DIR,
        "inference_codeformer.py"
    )


    command = [

        sys.executable,

        codeformer_script,

        "-w",
        "0.7",

        "-s",
        "1",

        "-i",
        input_path,

        "-o",
        job_output_dir
    ]


    print()
    print("COMMAND:")
    print(
        " ".join(command)
    )
    print()


    # --------------------------------------------------------
    # RUN CODEFORMER
    # --------------------------------------------------------

    env = os.environ.copy()

    env["PYTHONPATH"] = (
        CODEFORMER_DIR
        + os.pathsep
        + env.get("PYTHONPATH", "")
    )

    process = subprocess.run(
        command,
        cwd=CODEFORMER_DIR,
        env=env,
        capture_output=True,
        text=True
    )


    # --------------------------------------------------------
    # CODEFORMER OUTPUT
    # --------------------------------------------------------

    if process.stdout:

        print(
            process.stdout
        )


    if process.stderr:

        print(
            process.stderr
        )


    # --------------------------------------------------------
    # CHECK PROCESS
    # --------------------------------------------------------

    if process.returncode != 0:

        print()
        print(
            "CODEFORMER FAILED"
        )

        return jsonify({

            "success": False,

            "error":
                "CodeFormer failed",

            "details":
                process.stderr[-5000:]

        }), 500


    # --------------------------------------------------------
    # FIND FULL FINAL IMAGE
    # --------------------------------------------------------

    result_file = find_final_result(
        job_output_dir
    )


    # --------------------------------------------------------
    # RESULT NOT FOUND
    # --------------------------------------------------------

    if result_file is None:

        print()
        print(
            "FINAL RESULT NOT FOUND"
        )

        return jsonify({

            "success": False,

            "error":
                "CodeFormer final result not found"

        }), 500


    # --------------------------------------------------------
    # IMPORTANT
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("FULL FINAL CODEFORMER RESULT")
    print("=" * 60)

    print(
        result_file
    )

    print("=" * 60)


    # --------------------------------------------------------
    # COPY FINAL IMAGE
    # --------------------------------------------------------

    final_name = (
        job_id +
        ".png"
    )


    final_path = os.path.join(
        RESULT_DIR,
        final_name
    )


    shutil.copy2(
        result_file,
        final_path
    )


    print()
    print(
        "FINAL BROWSER IMAGE:"
    )

    print(
        final_path
    )


    # --------------------------------------------------------
    # RETURN TO BROWSER
    # --------------------------------------------------------

    return jsonify({

        "success": True,

        "before":
            "/result/" +
            input_filename,

        "after":
            "/result/" +
            final_name,

        "image":
            "/result/" +
            final_name

    })


# ============================================================
# SERVE RESULT / UPLOAD
# ============================================================

@app.route(
    "/result/<filename>"
)
def result(filename):

    # Security
    filename = os.path.basename(
        filename
    )


    # --------------------------------------------------------
    # RESULT IMAGE
    # --------------------------------------------------------

    result_path = os.path.join(
        RESULT_DIR,
        filename
    )


    if os.path.isfile(
        result_path
    ):

        return send_file(
            result_path
        )


    # --------------------------------------------------------
    # ORIGINAL IMAGE
    # --------------------------------------------------------

    upload_path = os.path.join(
        UPLOAD_DIR,
        filename
    )


    if os.path.isfile(
        upload_path
    ):

        return send_file(
            upload_path
        )


    # --------------------------------------------------------
    # NOT FOUND
    # --------------------------------------------------------

    return (
        "Image not found",
        404
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("FACE ENHANCER")
    print("MODEL  : CodeFormer 0.7")
    print("RESULT : FULL FINAL RESULT")
    print("FILTER : None")
    print("DEVICE : CPU")
    print("URL    : http://127.0.0.1:5000")
    print("=" * 60)
    print()


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
