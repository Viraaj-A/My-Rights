# Deployment-only gunicorn config (does not modify repo app code).
# Keeps --preload (shares model weights across workers via copy-on-write)
# and fixes inherited-DB-connection corruption: after fork each worker
# disposes the SQLAlchemy pool inherited from the preloaded master, so it
# opens its own fresh Postgres connections (no shared-SSL "bad record mac").
bind = "0.0.0.0:8080"
workers = 2
preload_app = True
timeout = 120

def post_fork(server, worker):
    try:
        from app import app as flask_app, db
        with flask_app.app_context():
            db.engine.dispose()
        worker.log.info("post_fork: disposed inherited DB engine pool")
    except Exception as e:
        worker.log.error(f"post_fork dispose failed: {e}")
