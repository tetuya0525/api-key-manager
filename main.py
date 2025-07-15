# ==============================================================================
# Memory Library - API Key Manager Service
# main.py
#
# Role:         APIキーの発行、検証、無効化の責務を持つ。
# Version:      1.0
# Author:       心理 (Thinking Partner)
# Last Updated: 2025-07-16
# ==============================================================================
import os
import secrets
import hashlib
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import firestore

# --- 初期化 (Initialization) ---
try:
    firebase_admin.initialize_app()
    db = firestore.client()
except ValueError:
    pass

app = Flask(__name__)

# --- メインロジック ---

@app.route('/generate', methods=['POST'])
def generate_api_key():
    """
    新しいAPIキーを生成し、ハッシュ化してDBに保存後、
    平文のキーを一度だけ返す。
    """
    data = request.get_json()
    user_id = data.get('userId')
    label = data.get('label')

    if not user_id or not label:
        return jsonify({"status": "error", "message": "userIdとlabelは必須です。"}), 400

    try:
        # 1. 安全なAPIキーを生成 (例: sk_ + 48文字のランダム文字列)
        plaintext_key = f"sk_{secrets.token_urlsafe(36)}"

        # 2. キーをハッシュ化 (SHA-256)
        hashed_key = hashlib.sha256(plaintext_key.encode('utf-8')).hexdigest()

        # 3. Firestoreに保存するデータを作成
        key_data = {
            'userId': user_id,
            'label': label,
            'hashedKey': hashed_key,
            'status': 'active',
            'createdAt': firestore.SERVER_TIMESTAMP,
            'lastUsedAt': None
        }

        # 4. Firestoreにドキュメントを追加
        db.collection('api_keys').add(key_data)

        app.logger.info(f"新しいAPIキーを生成しました。 Label: {label}")

        # 5. ★★★【重要】平文のキーを一度だけ返す ★★★
        return jsonify({
            "status": "success",
            "apiKey": plaintext_key,
            "message": "このキーは一度しか表示されません。安全な場所に保管してください。"
        }), 201

    except Exception as e:
        app.logger.error(f"APIキーの生成中にエラーが発生しました: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500


@app.route('/revoke', methods=['POST'])
def revoke_api_key():
    """
    指定されたAPIキー(のドキュメントID)を無効化する。
    """
    data = request.get_json()
    key_id = data.get('keyId') # 無効化対象はFirestoreのドキュメントID
    user_id = data.get('userId')

    if not key_id or not user_id:
        return jsonify({"status": "error", "message": "keyIdとuserIdは必須です。"}), 400

    try:
        key_ref = db.collection('api_keys').document(key_id)
        key_doc = key_ref.get()

        if not key_doc.exists:
            return jsonify({"status": "error", "message": "指定されたキーが見つかりません。"}), 404
        
        # 念のため、発行者本人からのリクエストか確認
        if key_doc.to_dict().get('userId') != user_id:
            return jsonify({"status": "error", "message": "このキーを無効化する権限がありません。"}), 403

        # 2. ステータスを'revoked'に更新
        key_ref.update({'status': 'revoked'})

        app.logger.info(f"APIキーを無効化しました。Key ID: {key_id}")

        return jsonify({"status": "success", "message": "APIキーを無効化しました。"}), 200

    except Exception as e:
        app.logger.error(f"APIキーの無効化中にエラーが発生しました: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500


# Gunicornから直接実行されるためのエントリーポイント
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
