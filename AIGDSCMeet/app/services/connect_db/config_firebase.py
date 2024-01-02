import firebase_admin
from firebase_admin import credentials, firestore


class ConfigFirebase:
    # source: string, keyword[]
    def __init__(self, file_path):
        cred = credentials.Certificate(file_path)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.collection = 'data'

    def create_document(self, source, keywords):
        keywords_map = {}
        for index, value in enumerate(keywords):
            keywords_map[str(index)] = value

        try:
            _, doc_ref = self.db.collection(self.collection).add({
                'keywords': keywords_map,
                'source': source
            })
            return doc_ref.id
        except Exception as e:
            return f"Error creating document: {e}"

    def update_document(self, index, keyword, did):
        doc_ref = self.db.collection(self.collection).document(did)
        try:
            doc_ref.update({
                f"keywords.{index}": keyword
            })
            return "Update successful"
        except Exception as e:
            return f"Update failed: {e}"

    def get_document_by_id(self, document_id):
        doc_ref = self.db.collection(self.collection).document(document_id)
        doc = doc_ref.get()
        result = {}

        if doc.exists:
            result = {
                "source": doc.to_dict().get("source"),
                "keywords": [value for _, value in sorted(doc.to_dict().get("keywords", {}).items())]
            }
        else:
            return "No such document!"

        return result

    def get_all_document(self):
        result = []
        docs = self.db.collection(self.collection).stream()
        for doc in docs:
            result.append({
                "doc_id": doc.id,
                "data": doc.to_dict()
            })
        return result

    def remove_keyword(self, document_id, index):
        data = self.get_document_by_id(document_id)
        if data == "No such document!":
            return "No such document!"
        else:
            if 0 <= index < len(data['keywords']):
                keywords_map = {}
                data['keywords'].pop(index)
                for index, value in enumerate(data['keywords']):
                    keywords_map[str(index)] = value
                updated_data = self.update_document_keywords(document_id, keywords_map)
                return keywords_map

    def update_document_keywords(self, document_id, new_keywords):
        updated_data = self.db.collection(self.collection).document(document_id).update({
            'keywords':new_keywords
        })
        if updated_data:
            return "Update successful"
        else:
            return "Update failed!"











