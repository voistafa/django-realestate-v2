from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.agents.models import Agent
from apps.locations.models import City, Region
from apps.projects.models import DevelopmentProject, ProjectFeature
from apps.properties.models import Feature, PropertyType


CITY_DATA = {
    "name": "کلاردشت",
    "slug": "kelardasht",
}


REGIONS = [
    ("گَویتر", "goytar"),
    ("بنفشه ده", "banafsheh-deh"),
    ("کَلِنو", "kaleno"),
    ("کُلُمه", "kolomeh"),
    ("کُردیچال", "kordichal"),
    ("اِسپندکُلا", "espandkola"),
    ("پِی قلعه", "pey-ghaleh"),
    ("طَبرسو", "tabarsu"),
    ("لاهو", "lahoo"),
    ("وَلِبال", "valbal"),
    ("لَشِسَر", "lashesar"),
    ("حسنکیف", "hasankif"),
    ("مَکارود", "makarud"),
    ("اُجابیت", "ojabit"),
    ("چِلاجور", "chelajur"),
    ("والِت", "valet"),
    ("گَرَکپَس", "garakpas"),
    ("رودبارک", "rudbarak"),
    ("واحه/واحد", "vahe-vahed"),
    ("طائبکلا", "taebkola"),
    ("بازارسر", "bazarsar"),
    ("پِیَمبور", "peyambur"),
    ("پیشَنبور", "pishanbur"),
    ("مِجِل", "mejel"),
    ("لَرگان", "largan"),
    ("سَرکا", "sarka"),
    ("سَما", "sama"),
    ("دیمو", "dimo"),
    ("شَکَرکوه", "shakarkuh"),
    ("کوهپر", "kuhpar"),
    ("طویدره", "tuidareh"),
]


PROPERTY_TYPES = [
    ("ویلا", "villa", 10),
    ("زمین", "land", 20),
    ("آپارتمان", "apartment", 30),
    ("خانه", "house", 40),
    ("باغ و باغ‌ویلا", "garden-villa", 50),
    ("تجاری", "commercial", 60),
    ("اداری", "office", 70),
]


PROPERTY_FEATURES = [
    ("پارکینگ", "parking", 10),
    ("انباری", "storage", 20),
    ("آسانسور", "elevator", 30),
    ("بالکن یا تراس", "balcony", 40),
    ("حیاط", "yard", 50),
    ("استخر", "pool", 60),
    ("سونا", "sauna", 70),
    ("جکوزی", "jacuzzi", 80),
    ("شومینه", "fireplace", 90),
    ("گرمایش از کف", "floor-heating", 100),
    ("سیستم امنیتی", "security", 110),
    ("دوربین مداربسته", "cctv", 120),
    ("چشم‌انداز کوهستان", "mountain-view", 130),
    ("چشم‌انداز جنگل", "forest-view", 140),
    ("دسترسی آسفالت", "asphalt-access", 150),
    ("آب", "water", 160),
    ("برق", "electricity", 170),
    ("گاز", "gas", 180),
    ("سند آماده انتقال", "ready-deed", 190),
]


PROJECT_FEATURES = [
    ("پارکینگ اختصاصی", "parking", 10),
    ("آسانسور", "elevator", 20),
    ("لابی", "lobby", 30),
    ("نگهبانی", "security", 40),
    ("دوربین مداربسته", "cctv", 50),
    ("فضای سبز", "green-space", 60),
    ("محوطه‌سازی", "landscaping", 70),
    ("استخر", "pool", 80),
    ("سالن ورزشی", "gym", 90),
    ("سیستم گرمایش مرکزی", "central-heating", 100),
    ("چشم‌انداز کوهستان", "mountain-view", 110),
    ("چشم‌انداز جنگل", "forest-view", 120),
]


AGENTS = [
    {
        "full_name": "ترنم بیگی",
        "slug": "taranom-beigi",
        "job_title": "مشاور ارشد املاک",
        "specialties": "خرید و فروش ویلا، سرمایه‌گذاری ملکی",
        "short_bio": (
            "مشاور املاک با تمرکز بر فایل‌های منتخب "
            "و فرصت‌های سرمایه‌گذاری در کلاردشت."
        ),
        "experience_years": 11,
        "is_featured": True,
        "display_order": 10,
    },
    {
        "full_name": "سارا همجوار",
        "slug": "sara-hamjavar",
        "job_title": "کارشناس فروش و سرمایه‌گذاری",
        "specialties": "ویلا، زمین، فایل‌های سرمایه‌گذاری",
        "short_bio": (
            "فعال در ارزیابی و معرفی فایل‌های مسکونی "
            "و زمین‌های مناسب سرمایه‌گذاری."
        ),
        "experience_years": 8,
        "is_featured": True,
        "display_order": 20,
    },
    {
        "full_name": "نیلوفر محمودی",
        "slug": "niloufar-mahmoudi",
        "job_title": "مشاور پروژه‌های ساختمانی",
        "specialties": "پروژه ساختمانی، پیش‌فروش، آپارتمان",
        "short_bio": (
            "متخصص معرفی پروژه‌های ساختمانی، "
            "پیش‌فروش و واحدهای در حال ساخت."
        ),
        "experience_years": 9,
        "is_featured": True,
        "display_order": 30,
    },
    {
        "full_name": "شقایق خرسند",
        "slug": "shaghayegh-khorsand",
        "job_title": "مشاور املاک مسکونی",
        "specialties": "ویلا، خانه، اجاره و رهن",
        "short_bio": (
            "مشاور فایل‌های مسکونی با تمرکز بر "
            "انتخاب متناسب با بودجه و نیاز خریدار."
        ),
        "experience_years": 6,
        "is_featured": True,
        "display_order": 40,
    },
    {
        "full_name": "نازنین سوادکوهی",
        "slug": "nazanin-savadkouhi",
        "job_title": "کارشناس زمین و املاک سرمایه‌ای",
        "specialties": "زمین، باغ، املاک سرمایه‌ای",
        "short_bio": (
            "فعال در حوزه زمین، باغ و فرصت‌های "
            "سرمایه‌گذاری بلندمدت ملکی."
        ),
        "experience_years": 10,
        "is_featured": True,
        "display_order": 50,
    },
]


PROJECTS = [
    {
        "reference_code": "DEMO-PROJ-001",
        "title": "مجموعه ویلایی رودبارک",
        "slug": "rudbarak-villa-residence",
        "region_slug": "rudbarak",
        "agent_slug": "taranom-beigi",
        "construction_status": "under_construction",
        "completion_percentage": 45,
        "developer_name": "گروه توسعه کلارخانه",
        "short_description": (
            "مجموعه‌ای ویلایی با طراحی معاصر و دسترسی مناسب "
            "به طبیعت رودبارک."
        ),
        "description": (
            "مجموعه ویلایی رودبارک یک پروژه نمایشی مسکونی "
            "با تمرکز بر معماری معاصر، فضای سبز و دسترسی "
            "مناسب به طبیعت منطقه است. این پروژه برای نمایش "
            "قابلیت‌های معرفی و مدیریت پروژه‌های ساختمانی "
            "در سامانه کلارخانه طراحی شده است."
        ),
        "public_location": "رودبارک، کلاردشت",
        "total_units": 12,
        "available_units": 7,
        "price_on_request": False,
        "starting_price": 8_900_000_000,
        "is_featured": True,
        "start_offset": -260,
        "completion_offset": 320,
        "features": [
            "پارکینگ اختصاصی",
            "نگهبانی",
            "فضای سبز",
            "محوطه‌سازی",
            "چشم‌انداز کوهستان",
        ],
    },
    {
        "reference_code": "DEMO-PROJ-002",
        "title": "رزیدنس مرکزی حسنکیف",
        "slug": "hasankif-central-residence",
        "region_slug": "hasankif",
        "agent_slug": "niloufar-mahmoudi",
        "construction_status": "under_construction",
        "completion_percentage": 68,
        "developer_name": "گروه توسعه کلارخانه",
        "short_description": (
            "مجتمع مسکونی شهری در حسنکیف با واحدهای مدرن "
            "و دسترسی مناسب به خدمات روزمره."
        ),
        "description": (
            "رزیدنس مرکزی حسنکیف یک پروژه نمایشی مسکونی "
            "با تمرکز بر زندگی شهری، دسترسی مناسب و امکانات "
            "مشترک ساختمان است. اطلاعات این پروژه برای نمایش "
            "قابلیت‌های نسخه دمو سامانه کلارخانه ارائه می‌شود."
        ),
        "public_location": "حسنکیف، مرکز کلاردشت",
        "total_units": 24,
        "available_units": 9,
        "price_on_request": False,
        "starting_price": 6_800_000_000,
        "is_featured": True,
        "start_offset": -420,
        "completion_offset": 190,
        "features": [
            "پارکینگ اختصاصی",
            "آسانسور",
            "لابی",
            "نگهبانی",
            "دوربین مداربسته",
            "سیستم گرمایش مرکزی",
        ],
    },
    {
        "reference_code": "DEMO-PROJ-003",
        "title": "برج‌باغ حسنکیف",
        "slug": "hasankif-garden-residence",
        "region_slug": "hasankif",
        "agent_slug": "sara-hamjavar",
        "construction_status": "planning",
        "completion_percentage": 0,
        "developer_name": "گروه سرمایه‌گذاری کلارخانه",
        "short_description": (
            "پروژه مسکونی کم‌تراکم با فضای سبز و طراحی "
            "متناسب با اقلیم کلاردشت."
        ),
        "description": (
            "برج‌باغ حسنکیف یک پروژه نمایشی در مرحله "
            "برنامه‌ریزی است که برای نمایش فرآیند معرفی "
            "پروژه‌های پیش‌فروش، امکانات، زمان‌بندی و وضعیت "
            "پیشرفت پروژه در سامانه طراحی شده است."
        ),
        "public_location": "حسنکیف، کلاردشت",
        "total_units": 18,
        "available_units": 18,
        "price_on_request": True,
        "starting_price": None,
        "is_featured": False,
        "start_offset": 60,
        "completion_offset": 720,
        "features": [
            "پارکینگ اختصاصی",
            "آسانسور",
            "فضای سبز",
            "محوطه‌سازی",
            "سالن ورزشی",
        ],
    },
    {
        "reference_code": "DEMO-PROJ-004",
        "title": "مجتمع تجاری مسکونی حسنکیف",
        "slug": "hasankif-mixed-use-complex",
        "region_slug": "hasankif",
        "agent_slug": "niloufar-mahmoudi",
        "construction_status": "completed",
        "completion_percentage": 100,
        "developer_name": "توسعه شهری کلارخانه",
        "short_description": (
            "مجتمع تکمیل‌شده با کاربری ترکیبی در محدوده "
            "مرکزی حسنکیف."
        ),
        "description": (
            "مجتمع تجاری مسکونی حسنکیف نمونه‌ای نمایشی از "
            "پروژه‌های تکمیل‌شده با کاربری ترکیبی است. این "
            "پروژه برای نمایش واحدهای آماده بهره‌برداری، "
            "امکانات مشترک و وضعیت موجودی در سامانه طراحی شده است."
        ),
        "public_location": "حسنکیف، کلاردشت",
        "total_units": 30,
        "available_units": 4,
        "price_on_request": False,
        "starting_price": 5_900_000_000,
        "is_featured": True,
        "start_offset": -920,
        "completion_offset": -80,
        "features": [
            "پارکینگ اختصاصی",
            "آسانسور",
            "لابی",
            "نگهبانی",
            "دوربین مداربسته",
        ],
    },
    {
        "reference_code": "DEMO-PROJ-005",
        "title": "مجموعه ویلایی جنگلی کُردیچال",
        "slug": "kordichal-forest-villas",
        "region_slug": "kordichal",
        "agent_slug": "shaghayegh-khorsand",
        "construction_status": "under_construction",
        "completion_percentage": 55,
        "developer_name": "گروه معماری کلارخانه",
        "short_description": (
            "مجموعه ویلایی کم‌تراکم با تأکید بر چشم‌انداز "
            "طبیعی و فضای سبز."
        ),
        "description": (
            "مجموعه ویلایی جنگلی کُردیچال یک پروژه نمایشی "
            "برای معرفی مجموعه‌های ویلایی کم‌تراکم با "
            "محوطه‌سازی، فضای سبز و دسترسی مناسب به طبیعت است."
        ),
        "public_location": "کُردیچال، کلاردشت",
        "total_units": 8,
        "available_units": 5,
        "price_on_request": True,
        "starting_price": None,
        "is_featured": False,
        "start_offset": -310,
        "completion_offset": 260,
        "features": [
            "پارکینگ اختصاصی",
            "فضای سبز",
            "محوطه‌سازی",
            "چشم‌انداز جنگل",
            "چشم‌انداز کوهستان",
        ],
    },
    {
        "reference_code": "DEMO-PROJ-006",
        "title": "مجموعه اقامتی مَکارود",
        "slug": "makarud-residential-retreat",
        "region_slug": "makarud",
        "agent_slug": "sara-hamjavar",
        "construction_status": "planning",
        "completion_percentage": 0,
        "developer_name": "گروه سرمایه‌گذاری کلارخانه",
        "short_description": (
            "پروژه‌ای در مرحله برنامه‌ریزی با تمرکز بر "
            "اقامت و سرمایه‌گذاری در محیط طبیعی."
        ),
        "description": (
            "مجموعه اقامتی مَکارود به‌صورت یک پروژه نمایشی "
            "برای معرفی فرصت‌های سرمایه‌گذاری و پروژه‌های "
            "در مرحله برنامه‌ریزی در سامانه ایجاد شده است."
        ),
        "public_location": "مَکارود، کلاردشت",
        "total_units": 16,
        "available_units": 16,
        "price_on_request": True,
        "starting_price": None,
        "is_featured": False,
        "start_offset": 120,
        "completion_offset": 820,
        "features": [
            "پارکینگ اختصاصی",
            "نگهبانی",
            "فضای سبز",
            "محوطه‌سازی",
            "چشم‌انداز جنگل",
        ],
    },
    {
        "reference_code": "DEMO-PROJ-007",
        "title": "رزیدنس لاهو",
        "slug": "lahoo-residence",
        "region_slug": "lahoo",
        "agent_slug": "taranom-beigi",
        "construction_status": "completed",
        "completion_percentage": 100,
        "developer_name": "گروه توسعه کلارخانه",
        "short_description": (
            "مجتمع مسکونی تکمیل‌شده با تعداد محدود واحد "
            "و طراحی متناسب با بافت منطقه."
        ),
        "description": (
            "رزیدنس لاهو نمونه‌ای از پروژه‌های تکمیل‌شده "
            "در نسخه دمو است که برای نمایش وضعیت موجودی "
            "واحدها، مشخصات پروژه و امکانات مشترک طراحی شده است."
        ),
        "public_location": "لاهو، کلاردشت",
        "total_units": 10,
        "available_units": 2,
        "price_on_request": False,
        "starting_price": 7_400_000_000,
        "is_featured": False,
        "start_offset": -760,
        "completion_offset": -45,
        "features": [
            "پارکینگ اختصاصی",
            "آسانسور",
            "فضای سبز",
            "سیستم گرمایش مرکزی",
        ],
    },
    {
        "reference_code": "DEMO-PROJ-008",
        "title": "مجتمع مسکونی چِلاجور",
        "slug": "chelajur-residential-complex",
        "region_slug": "chelajur",
        "agent_slug": "nazanin-savadkouhi",
        "construction_status": "under_construction",
        "completion_percentage": 74,
        "developer_name": "توسعه‌سازان کلارخانه",
        "short_description": (
            "مجتمع مسکونی در حال ساخت با واحدهای محدود "
            "و فضای مشاع استاندارد."
        ),
        "description": (
            "مجتمع مسکونی چِلاجور یک پروژه نمایشی برای "
            "نمایش پروژه‌های در حال ساخت با پیشرفت بالا، "
            "تعداد واحد مشخص و امکانات مشترک در سامانه است."
        ),
        "public_location": "چِلاجور، کلاردشت",
        "total_units": 14,
        "available_units": 5,
        "price_on_request": False,
        "starting_price": 6_200_000_000,
        "is_featured": True,
        "start_offset": -470,
        "completion_offset": 130,
        "features": [
            "پارکینگ اختصاصی",
            "آسانسور",
            "نگهبانی",
            "دوربین مداربسته",
            "محوطه‌سازی",
        ],
    },
]


class Command(BaseCommand):
    help = (
        "Create or update reusable demo data "
        "for the real-estate showcase."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        city = self.seed_city_and_regions()
        self.seed_property_types()
        self.seed_property_features()
        self.seed_project_features()
        self.seed_agents()

        seeded_project_codes = self.seed_projects(city)

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Demo data seeded successfully."
            )
        )

        self.print_summary(
            city=city,
            seeded_project_codes=seeded_project_codes,
        )

    def seed_city_and_regions(self):
        city, _ = City.objects.update_or_create(
            slug=CITY_DATA["slug"],
            defaults={
                "name": CITY_DATA["name"],
                "is_active": True,
            },
        )

        for name, slug in REGIONS:
            Region.objects.update_or_create(
                city=city,
                slug=slug,
                defaults={
                    "name": name,
                    "is_active": True,
                },
            )

        return city

    def seed_property_types(self):
        for name, slug, display_order in PROPERTY_TYPES:
            PropertyType.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "is_active": True,
                    "display_order": display_order,
                },
            )

    def seed_property_features(self):
        for name, icon, display_order in PROPERTY_FEATURES:
            Feature.objects.update_or_create(
                name=name,
                defaults={
                    "icon": icon,
                    "is_active": True,
                    "display_order": display_order,
                },
            )

    def seed_project_features(self):
        for name, icon, display_order in PROJECT_FEATURES:
            ProjectFeature.objects.update_or_create(
                name=name,
                defaults={
                    "icon": icon,
                    "is_active": True,
                    "display_order": display_order,
                },
            )

    def seed_agents(self):
        for agent_data in AGENTS:
            slug = agent_data["slug"]

            defaults = {
                key: value
                for key, value in agent_data.items()
                if key != "slug"
            }

            defaults["is_active"] = True

            agent, created = Agent.objects.get_or_create(
                slug=slug,
                defaults=defaults,
            )

            if created:
                self.stdout.write(
                    f"Agent {slug} created."
                )
            else:
                self.stdout.write(
                    f"Agent {slug} already exists; skipped."
                )

    def seed_projects(self, city):
        today = timezone.localdate()
        seeded_project_codes = []

        for project_data in PROJECTS:
            reference_code = project_data["reference_code"]

            existing_project = DevelopmentProject.objects.filter(
                reference_code=reference_code,
            ).first()

            if existing_project is not None:
                seeded_project_codes.append(reference_code)

                self.stdout.write(
                    f"Project {reference_code} already exists; skipped."
                )

                continue

            region = Region.objects.get(
                city=city,
                slug=project_data["region_slug"],
            )

            agent = Agent.objects.get(
                slug=project_data["agent_slug"],
            )

            project = DevelopmentProject(
                reference_code=reference_code,
                publication_status=(
                    DevelopmentProject.PublicationStatus.DRAFT
                ),
                published_at=None,
            )

            project.title = project_data["title"]
            project.slug = project_data["slug"]
            project.region = region
            project.agent = agent

            project.construction_status = (
                project_data["construction_status"]
            )

            project.short_description = (
                project_data["short_description"]
            )

            project.description = (
                project_data["description"]
            )

            project.public_location = (
                project_data["public_location"]
            )

            project.private_address = ""

            project.developer_name = (
                project_data["developer_name"]
            )

            project.starting_price = (
                project_data["starting_price"]
            )

            project.currency_code = "IRT"

            project.price_on_request = (
                project_data["price_on_request"]
            )

            project.total_units = (
                project_data["total_units"]
            )

            project.available_units = (
                project_data["available_units"]
            )

            project.completion_percentage = (
                project_data["completion_percentage"]
            )

            project.start_date = (
                today
                + timedelta(
                    days=project_data["start_offset"],
                )
            )

            project.expected_completion_date = (
                today
                + timedelta(
                    days=project_data["completion_offset"],
                )
            )

            project.latitude = None
            project.longitude = None
            project.is_exact_location_public = False

            project.is_featured = (
                project_data["is_featured"]
            )

            project.full_clean()
            project.save()

            features = ProjectFeature.objects.filter(
                name__in=project_data["features"],
                is_active=True,
            )

            project.features.set(features)

            seeded_project_codes.append(
                reference_code
            )

        return seeded_project_codes

    def print_summary(
        self,
        city,
        seeded_project_codes,
    ):
        region_count = Region.objects.filter(
            city=city,
        ).count()

        property_type_slugs = [
            item[1]
            for item in PROPERTY_TYPES
        ]

        property_type_count = PropertyType.objects.filter(
            slug__in=property_type_slugs,
        ).count()

        property_feature_names = [
            item[0]
            for item in PROPERTY_FEATURES
        ]

        property_feature_count = Feature.objects.filter(
            name__in=property_feature_names,
        ).count()

        project_feature_names = [
            item[0]
            for item in PROJECT_FEATURES
        ]

        project_feature_count = ProjectFeature.objects.filter(
            name__in=project_feature_names,
        ).count()

        agent_slugs = [
            item["slug"]
            for item in AGENTS
        ]

        agent_count = Agent.objects.filter(
            slug__in=agent_slugs,
        ).count()

        seeded_projects_count = DevelopmentProject.objects.filter(
            reference_code__in=seeded_project_codes,
        ).count()

        self.stdout.write("")

        self.stdout.write(
            f"Cities: "
            f"{City.objects.filter(slug=CITY_DATA['slug']).count()}"
        )

        self.stdout.write(
            f"Regions: {region_count}"
        )

        self.stdout.write(
            f"Property types: {property_type_count}"
        )

        self.stdout.write(
            f"Property features: {property_feature_count}"
        )

        self.stdout.write(
            f"Project features: {project_feature_count}"
        )

        self.stdout.write(
            f"Agents: {agent_count}"
        )

        self.stdout.write(
            f"Seeded projects: {seeded_projects_count}"
        )