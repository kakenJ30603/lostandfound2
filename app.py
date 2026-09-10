from flask import Flask, request, render_template, redirect
import os
import cv2

app = Flask(
    __name__,
    template_folder="templates2",
    static_folder="static2"
)

IMAGE_FOLDER = "static2/images"
DATA_FOLDER = "data"

os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

counter_file = "counter.txt"

if not os.path.exists(counter_file):

    with open(counter_file, "w") as f:
        f.write("1")


@app.route('/')
def home():

    return render_template("index2.html")


@app.route('/student')
def student():

    data_list = []

    files = sorted(os.listdir(DATA_FOLDER), reverse=True)

    for file in files:

        with open(os.path.join(DATA_FOLDER, file), "r") as f:

            lines = f.readlines()

            if len(lines) >= 6:

                data = {

                    "number": lines[0].strip(),
                    "place": lines[1].strip(),
                    "detail": lines[2].strip(),
                    "date": lines[3].strip(),
                    "time": lines[4].strip(),
                    "image": lines[5].strip()
                }

                data_list.append(data)

    return render_template("student2.html", data_list=data_list)


@app.route('/admin')
def admin():

    data_list = []

    files = sorted(os.listdir(DATA_FOLDER), reverse=True)

    for file in files:

        with open(os.path.join(DATA_FOLDER, file), "r") as f:

            lines = f.readlines()

            if len(lines) >= 6:

                data = {

                    "number": lines[0].strip(),
                    "place": lines[1].strip(),
                    "detail": lines[2].strip(),
                    "date": lines[3].strip(),
                    "time": lines[4].strip(),
                    "image": lines[5].strip()
                }

                data_list.append(data)

    return render_template("admin.html", data_list=data_list)


@app.route('/register', methods=['POST'])
def register():

    with open(counter_file, "r") as f:

        text = f.read().strip()

        if text == "":
            counter = 1
        else:
            counter = int(text)

    place = request.form['place']
    detail = request.form['detail']
    date = request.form['date']

    hour = request.form['hour']
    minute = request.form['minute']

    time = hour + ":" + minute

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        return "カメラを開けません"

    ret, frame = camera.read()

    image_name = f"{counter}.jpg"

    if ret:

        cv2.imwrite(
            os.path.join(IMAGE_FOLDER, image_name),
            frame
        )

    else:

        camera.release()

        return "撮影失敗"

    camera.release()

    text_name = f"{counter}.txt"

    with open(os.path.join(DATA_FOLDER, text_name), "w") as f:

        f.write(f"{counter}\n")
        f.write(f"{place}\n")
        f.write(f"{detail}\n")
        f.write(f"{date}\n")
        f.write(f"{time}\n")
        f.write(f"{image_name}\n")

    counter += 1

    with open(counter_file, "w") as f:

        f.write(str(counter))

    return render_template("index2.html")


@app.route('/delete/<number>')
def delete(number):

    txt_file = os.path.join(DATA_FOLDER, f"{number}.txt")
    img_file = os.path.join(IMAGE_FOLDER, f"{number}.jpg")

    if os.path.exists(txt_file):
        os.remove(txt_file)

    if os.path.exists(img_file):
        os.remove(img_file)

    return redirect("/admin")


@app.route('/reset_all')
def reset_all():

    for file in os.listdir(DATA_FOLDER):

        file_path = os.path.join(DATA_FOLDER, file)

        if os.path.isfile(file_path):

            os.remove(file_path)

    for file in os.listdir(IMAGE_FOLDER):

        file_path = os.path.join(IMAGE_FOLDER, file)

        if os.path.isfile(file_path):

            os.remove(file_path)

    with open(counter_file, "w") as f:

        f.write("1")

    return redirect("/admin")


app.run(host='0.0.0.0', port=5000)