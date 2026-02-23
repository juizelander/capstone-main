# home/tests/test_media.py

"""Tests for media handling and program image URLs."""

import os
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from home.models import Program

class MediaAPITest(TestCase):
    def setUp(self):
        img_content = b"fake-image-content"
        img = SimpleUploadedFile("test.jpg", img_content, content_type="image/jpeg")
        self.program = Program.objects.create(program_name="Test Program", program_image=img)
        self.client = Client()
        session = self.client.session
        session["user_id"] = 1
        session.save()

    def test_program_image_url(self):
        response = self.client.get("/home/programs/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        prog = next(p for p in data["programs"] if p["program_name"] == "Test Program")
        self.assertTrue(prog["program_image"].endswith("test.jpg"))
        self.assertTrue(prog["program_image"].startswith("/media/") or prog["program_image"].startswith("http"))
