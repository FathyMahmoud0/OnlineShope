from celery import shared_task
from .ai import AISearchEngine

@shared_task(name="rebuild_ai_index") 
def rebuild_ai_index_task():
    print("⏳ Celery: Starting AI Index Rebuild...")
    try:
        engine = AISearchEngine()
        engine.build_index()
        print("✅ Celery: AI Index Rebuilt Successfully.")
    except Exception as e:
        print(f"❌ Celery Error: {e}")