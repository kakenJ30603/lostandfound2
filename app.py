
from flask import Flask, request, render_template, redirect, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(
    __name__,
    template_folder="templates2",
    static_folder="static2"
)

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URLが設定されていません")
    return psycopg2.connect(DATABASE_URL)


def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS lost_items (
                number SERIAL PRIMARY KEY,
                place TEXT NOT NULL,
                detail TEXT NOT NULL,
                found_date TEXT NOT NULL,
                found_time TEXT NOT NULL,
                image TEXT NOT NULL
            )
        """)


def get_data():
    conn = get_connection()
    try:
        with conn:
            create_table(conn)
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        number,
                        place,
                        detail,
                        found_date AS date,
                        found_time AS time,
                        image
                    FROM lost_items
                    ORDER BY number DESC
                """)
                return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


@app.route("/")
def home():
    return render_template("index2.html")


@app.route("/student")
def student():
    try:
        data_list = get_data()
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
        return jsonify({
            "success": False,
            "message": "入力されていない項目があります。"
        }), 400

    if not image_url:
        return jsonify({
            "success": False,
            "message": "写真のアップロードに失敗しました。"
        }), 400

    time = f"{hour}:{minute}"

    conn = None
    try:
        conn = get_connection()
        with conn:
            create_table(conn)
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO lost_items
                        (place, detail, found_date, found_time, image)
                    VALUES (%s, %s, %s, %s, %s)
                """, (place, detail, date, time, image_url))

        # 登録画面にとどまるため、JSONで成功を返す
        return jsonify({
            "success": True,
            "message": "登録ありがとうございます！"
        })

    except Exception:
        app.logger.exception("登録エラー")
        return jsonify({
            "success": False,
            "message": "登録できませんでした。設定を確認してください。"
        }), 500

    finally:
        if conn is not None:
            conn.close()


@app.route("/reset_all", methods=["POST"])
def reset_all():
    conn = None
    try:
        conn = get_connection()
        with conn:
            create_table(conn)
            with conn.cursor() as cur:
                cur.execute(
                    "TRUNCATE TABLE lost_items RESTART IDENTITY"
                )

        return redirect("/admin")

    except Exception:
        app.logger.exception("リセットエラー")
        return "リセットできませんでした。設定を確認してください。", 500

    finally:
        if conn is not None:
            conn.close()


@app.route("/delete/<number>", methods=["POST"])
def delete(number):
    conn = None
    try:
        conn = get_connection()
        with conn:
            create_table(conn)
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM lost_items WHERE number = %s",
                    (number,)
                )
        return redirect("/admin")

    except Exception:
        app.logger.exception("削除エラー")
        return "削除できませんでした。設定を確認してください。", 500

    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
