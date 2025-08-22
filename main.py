import os
from flask import Flask, request, jsonify
import logging

# --- 初期化 ---
app = Flask(__name__)
# Cloud RunのログにINFOレベルのメッセージも表示されるように設定
logging.basicConfig(level=logging.INFO)

# --- デバッグ用エンドポイント ---

@app.route('/generate', methods=['POST'])
def generate_api_key():
    """
    /generate への呼び出しに対し、ダミーの成功応答を返す。
    """
    app.logger.info("DEBUG: /generate endpoint was called successfully.")
    return jsonify({
        "status": "success_debug",
        "apiKey": "sk_this_is_a_dummy_key_firebase_is_disabled",
        "message": "This is a debug response. The service is running."
    }), 201

@app.route('/revoke', methods=['POST'])
def revoke_api_key():
    """
    /revoke への呼び出しに対し、ダミーの成功応答を返す。
    """
    app.logger.info("DEBUG: /revoke endpoint was called successfully.")
    return jsonify({"status": "success_debug", "message": "Revoke called."}), 200

# Gunicornから直接実行されるためのエントリーポイント
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
