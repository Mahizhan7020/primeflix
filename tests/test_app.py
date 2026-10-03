import os
import tempfile
import unittest

from sqlalchemy import URL

from app import Title, User, Watchlist, create_app, db


class PrimeFlixTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": URL.create("sqlite", database=os.path.join(self.temp_dir.name, "test.db")),
            "WTF_CSRF_ENABLED": False,
        })
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()
        self.temp_dir.cleanup()

    def signup(self, email="viewer@example.com", password="correct horse"):
        return self.client.post("/signup", data={
            "name": "Test Viewer",
            "email": email,
            "phone": "1234567890",
            "password": password,
            "confirm_password": password,
        }, follow_redirects=True)

    def login(self, email="viewer@example.com", password="correct horse"):
        return self.client.post("/login", data={"email": email, "password": password}, follow_redirects=True)

    def test_home_and_catalog_are_seeded(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"The Last Horizon", response.data)
        self.assertEqual(self.client.get("/health").json, {"status": "ok", "database": "connected"})

    def test_signup_stores_a_hash_and_rejects_duplicate_email(self):
        response = self.signup(email=" VIEWER@example.com ")
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            user = db.session.scalar(db.select(User).where(User.email == "viewer@example.com"))
            self.assertIsNotNone(user)
            self.assertNotEqual(user.password_hash, "correct horse")
            self.assertTrue(user.password_hash.startswith("scrypt:"))
        duplicate = self.signup()
        self.assertIn(b"already exists", duplicate.data)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(User)), 1)

    def test_signup_validates_password_and_fields(self):
        response = self.client.post("/signup", data={
            "name": "Test", "email": "viewer@example.com", "phone": "123",
            "password": "short", "confirm_password": "short",
        })
        self.assertIn(b"at least 8 characters", response.data)
        self.assertIn(b"Passwords do not match", self.client.post("/signup", data={
            "name": "Test", "email": "viewer@example.com", "phone": "123",
            "password": "correct horse", "confirm_password": "different",
        }).data)

    def test_login_and_logout(self):
        self.signup()
        invalid = self.login(password="wrong password")
        self.assertIn(b"Invalid email or password", invalid.data)
        signed_in = self.login()
        self.assertIn(b"Test Viewer", signed_in.data)
        signed_out = self.client.post("/logout", follow_redirects=True)
        self.assertIn(b"signed out", signed_out.data)
        self.assertEqual(self.client.get("/watchlist").status_code, 302)

    def test_watchlist_add_remove_and_search(self):
        self.signup()
        self.login()
        with self.app.app_context():
            title = db.session.scalar(db.select(Title).where(Title.title == "The Last Horizon"))
            title_id = title.id
        add = self.client.post(f"/watchlist/toggle/{title_id}", follow_redirects=True)
        self.assertIn(b"The Last Horizon", add.data)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(Watchlist)), 1)
        self.assertEqual(len(self.client.get("/api/search?q=horizon").json), 1)
        self.client.post(f"/watchlist/toggle/{title_id}", follow_redirects=True)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(Watchlist)), 0)

    def test_post_forms_require_csrf_token(self):
        self.app.config["WTF_CSRF_ENABLED"] = True
        response = self.client.post("/login", data={"email": "a@example.com", "password": "secret"})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
