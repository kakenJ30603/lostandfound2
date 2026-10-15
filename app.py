
from flask import Flask, request, render_template, redirect
import os
import requests

app = Flask(
    __name__,
    template_folder="templates2",
    static_folder="static2"
)

# Google Apps ScriptのURL
SHEET_API_URL = (
    "https://script.google.com/a/macros/ict.shimanet.ed.jp/s/"
    "AKfycbzT5C1bwpgFxFLxz-n13Ltl6O7LG3raPRI-wICFVP7Trr2wFmQSUK3S5VLW3A0sSBUAVQ/exec"
)


def get_data():
    response = requests.get(
        SHEET_API_URL,
        params={"action": "list"},
        timeout=20
    )
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, list):
        raise RuntimeError("Googleスプレッドシートからデータを取得できません")

    return data


def call_sheet(params):
    response = requests.get(
        SHEET_API_URL,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    result = response.json()

    if not isinstance(result, dict) or result.get("error"):
        raise RuntimeError("スプレッドシートへの保存に失敗しました")

    return result


@app.route("/")
def home():
    return render_template("index2.html")


@app.route("/student")
def student():
    try:
        data_list = get_data()
        data_list.reverse()

        return render_template(
            "student2.html",
            data_list=data_list
        )

    except Exception:
        app.logger.exception("生徒画面のデータ取得エラー")
        return "データを取得できませんでした。設定を確認してください。", 500


@app.route("/admin")
def admin():
    try:
        data_list = get_data()
        data_list.reverse()

        return render_template(
            "admin.html",
            data_list=data_list
        )

    except Exception:
        app.logger.exception("管理画面のデータ取得エラー")
        return "データを取得できませんでした。設定を確認してください。", 500


@app.route("/register", methods=["POST"])
def register():
    place = request.form.get("place", "")
    detail = request.form.get("detail", "")
    date = request.form.get("date", "")
    hour = request.form.get("hour", "")
    minute = request.form.get("minute", "")
    image_url = request.form.get("image_url", "")

    if not all([place, detail, date, hour, minute]):
        return "入力されていない項目があります", 400

    if not image_url:
        return "写真のアップロードに失敗しました", 400

    time = f"{hour}:{minute}"

    try:
        result = call_sheet({
            "action": "register",
            "place": place,
            "detail": detail,
            "date": date,
            "time": time,
            "image": image_url
        })

        if not result.get("success"):
            return "登録に失敗しました", 500

        return redirect("/admin")

    except Exception:
        app.logger.exception("登録エラー")
        return "登録できませんでした。Google Apps Scriptの公開設定を確認してください。", 500


@app.route("/delete/<number>")
def delete(number):
    try:
        call_sheet({
            "action": "delete",
            "number": number
        })

        return redirect("/admin")

    except Exception:
        app.logger.exception("削除エラー")
        return "削除できませんでした。設定を確認してください。", 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
