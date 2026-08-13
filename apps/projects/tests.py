import shutil
import tempfile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.locations.models import City, Region

from .models import DevelopmentProject, ProjectImage


class DevelopmentProjectPublicationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls._temporary_media_root = tempfile.mkdtemp()
        cls._media_override = override_settings(
            MEDIA_ROOT=cls._temporary_media_root,
        )
        cls._media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._media_override.disable()

        shutil.rmtree(
            cls._temporary_media_root,
            ignore_errors=True,
        )

        super().tearDownClass()

    def setUp(self):
        self.city = City.objects.create(
            name="کلاردشت",
            slug="kelardasht-test",
        )

        self.region = Region.objects.create(
            city=self.city,
            name="رودبارک",
            slug="rudbarak-test",
        )

        self.project = DevelopmentProject.objects.create(
            title="پروژه تست انتشار",
            slug="publication-test-project",
            reference_code="TEST-PROJ-001",
            region=self.region,
            description="توضیحات پروژه برای تست منطق انتشار.",
            price_on_request=True,
            is_featured=True,
        )

    def create_cover_image(self):
        image_content = (
            b"GIF89a"
            b"\x01\x00\x01\x00"
            b"\x80\x00\x00"
            b"\x00\x00\x00"
            b"\xff\xff\xff"
            b"!\xf9\x04\x01\x00\x00\x00\x00"
            b",\x00\x00\x00\x00\x01\x00\x01\x00\x00"
            b"\x02\x02D\x01\x00;"
        )

        return ProjectImage.objects.create(
            project=self.project,
            image=SimpleUploadedFile(
                "cover.gif",
                image_content,
                content_type="image/gif",
            ),
            alt_text="تصویر کاور تست",
            is_cover=True,
        )

    def test_draft_project_is_not_public(self):
        list_response = self.client.get(
            reverse("projects:list"),
        )

        self.assertEqual(
            list_response.status_code,
            200,
        )

        self.assertNotContains(
            list_response,
            self.project.title,
        )

        detail_response = self.client.get(
            reverse(
                "projects:detail",
                kwargs={
                    "slug": self.project.slug,
                },
            ),
        )

        self.assertEqual(
            detail_response.status_code,
            404,
        )

    def test_project_cannot_publish_without_cover(self):
        with self.assertRaises(ValidationError):
            self.project.publish()

        self.project.refresh_from_db()

        self.assertEqual(
            self.project.publication_status,
            DevelopmentProject.PublicationStatus.DRAFT,
        )

        self.assertIsNone(
            self.project.published_at,
        )

    def test_project_with_cover_can_be_published(self):
        self.create_cover_image()

        self.project.publish()
        self.project.refresh_from_db()

        self.assertEqual(
            self.project.publication_status,
            DevelopmentProject.PublicationStatus.PUBLISHED,
        )

        self.assertIsNotNone(
            self.project.published_at,
        )

        list_response = self.client.get(
            reverse("projects:list"),
        )

        self.assertContains(
            list_response,
            self.project.title,
        )

        detail_response = self.client.get(
            reverse(
                "projects:detail",
                kwargs={
                    "slug": self.project.slug,
                },
            ),
        )

        self.assertEqual(
            detail_response.status_code,
            200,
        )

        self.assertContains(
            detail_response,
            self.project.title,
        )

    def test_move_to_draft_hides_published_project(self):
        self.create_cover_image()

        self.project.publish()
        self.project.move_to_draft()
        self.project.refresh_from_db()

        self.assertEqual(
            self.project.publication_status,
            DevelopmentProject.PublicationStatus.DRAFT,
        )

        self.assertIsNone(
            self.project.published_at,
        )

        list_response = self.client.get(
            reverse("projects:list"),
        )

        self.assertNotContains(
            list_response,
            self.project.title,
        )

        detail_response = self.client.get(
            reverse(
                "projects:detail",
                kwargs={
                    "slug": self.project.slug,
                },
            ),
        )

        self.assertEqual(
            detail_response.status_code,
            404,
        )

    def test_featured_project_appears_on_home_only_when_published(self):
        home_url = reverse("core:home")

        draft_response = self.client.get(
            home_url,
        )

        self.assertNotContains(
            draft_response,
            self.project.title,
        )

        self.create_cover_image()
        self.project.publish()

        published_response = self.client.get(
            home_url,
        )

        self.assertContains(
            published_response,
            self.project.title,
        )