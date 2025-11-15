# -*- coding: utf-8 -*-
"""Mock implementations for demo mode."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
from logging import getLogger
logging.basicConfig(level=logging.INFO)
logger = getLogger(__name__)

# Mock pymongo and bson FIRST (before any imports that might use it)
class MockPyMongoClient:
    def __init__(self, *args, **kwargs):
        pass
    
    def __getitem__(self, key):
        return {}

class MockPyMongo:
    MongoClient = MockPyMongoClient

class MockBSON:
    class ObjectId:
        def __init__(self, oid=None):
            self.oid = oid or "mock_object_id"
        
        def __str__(self):
            return str(self.oid)

# Set up mocks before any pymongo imports
sys.modules['pymongo'] = MockPyMongo
sys.modules['pymongo.collection'] = type('obj', (object,), {'Collection': object})
sys.modules['pymongo.cursor'] = type('obj', (object,), {'Cursor': object})
sys.modules['bson'] = MockBSON

# In-memory storage
_mock_db = {
    "users": {},
    "conversations": {},
    "memories": {}
}

class MockMongoDBBase:
    """Mock MongoDB base class."""
    
    def __init__(self, *args, **kwargs):
        logger.info("Using mock MongoDBBase")
        self.db = _mock_db
    
    def get_collection(self, collection_name: str):
        """Get a mock collection."""
        if collection_name not in _mock_db:
            _mock_db[collection_name] = {}
        return _mock_db[collection_name]
    
    def insert_one(self, collection_name: str, document: dict) -> str:
        """Insert a document."""
        if collection_name not in _mock_db:
            _mock_db[collection_name] = {}
        doc_id = f"mock_id_{len(_mock_db[collection_name])}"
        document["_id"] = doc_id
        _mock_db[collection_name][doc_id] = document
        return doc_id
    
    def find_one(self, collection_name: str, query: dict) -> dict:
        """Find one document."""
        if collection_name not in _mock_db:
            return None
        for doc in _mock_db[collection_name].values():
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None
    
    def find_many(self, collection_name: str, query: dict, limit: int = 0) -> list:
        """Find many documents."""
        if collection_name not in _mock_db:
            return []
        results = []
        for doc in _mock_db[collection_name].values():
            if all(doc.get(k) == v for k, v in query.items()):
                results.append(doc)
        if limit > 0:
            results = results[:limit]
        return results
    
    def update_one(self, collection_name: str, query: dict, update: dict) -> int:
        """Update one document."""
        if collection_name not in _mock_db:
            return 0
        for doc in _mock_db[collection_name].values():
            if all(doc.get(k) == v for k, v in query.items()):
                if "$set" in update:
                    doc.update(update["$set"])
                return 1
        return 0
    
    def upsert_one(self, collection_name: str, query: dict, update: dict) -> str:
        """Upsert one document."""
        if collection_name not in _mock_db:
            _mock_db[collection_name] = {}
        # Try to find existing
        for doc_id, doc in _mock_db[collection_name].items():
            if all(doc.get(k) == v for k, v in query.items()):
                if "$set" in update:
                    doc.update(update["$set"])
                return doc_id
        # Insert new
        doc_id = f"mock_id_{len(_mock_db[collection_name])}"
        new_doc = query.copy()
        if "$set" in update:
            new_doc.update(update["$set"])
        new_doc["_id"] = doc_id
        _mock_db[collection_name][doc_id] = new_doc
        return doc_id

def embedding_by_aliyun(text: str) -> list:
    """Mock embedding function."""
    logger.info(f"Mock embedding_by_aliyun: {text[:50]}...")
    # Return a random 1536-dim vector
    import random
    return [random.random() for _ in range(1536)]

def aliyun_search(query: str, limit: int = 10) -> list:
    """Mock search function."""
    logger.info(f"Mock aliyun_search: {query}")
    return []

class MockUserDAO:
    """Mock User DAO."""
    
    def __init__(self, *args, **kwargs):
        logger.info("Using mock UserDAO")
    
    def get_user_by_id(self, user_id):
        logger.info(f"Mock get_user_by_id: {user_id}")
        return {
            "_id": user_id,
            "name": "Test User",
            "platforms": {
                "wechat": {
                    "id": "wx_test",
                    "nickname": "测试用户"
                }
            }
        }
    
    def find_users(self, query, limit=10):
        logger.info(f"Mock find_users: {query}")
        return [self.get_user_by_id("test_user")]

class MockConversationDAO:
    """Mock Conversation DAO."""
    
    def __init__(self, *args, **kwargs):
        logger.info("Using mock ConversationDAO")
    
    def get_conversation_by_id(self, conversation_id):
        logger.info(f"Mock get_conversation_by_id: {conversation_id}")
        return None
    
    def create_conversation(self, conversation_data):
        logger.info(f"Mock create_conversation")
        return "mock_conversation_id"

# Global mock DB instance
mock_db = MockMongoDBBase()





