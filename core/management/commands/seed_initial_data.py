"""Load the initial company content (idempotent: only fills empty tables; provinces are always upserted)."""
import json
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from core import seed_content as sc
from core.models import (Certificate, Client, Office, OrgUnit, Province, RndResource, SiteSettings,
                         TeamMember, TimelineEvent, ValueItem)
from projects.models import Project, ServiceArea

SEED = Path(settings.BASE_DIR) / "seed"
FEATURED_SUBSTR = [s for s in sc.FEATURED_HINTS]


def attach(field, name):
    if not name:
        return
    path = SEED / "img" / name
    if path.exists():
        with open(path, "rb") as fh:
            field.save(name, File(fh), save=False)


class Command(BaseCommand):
    help = "Seed provinces, services, projects, team, offices, certificates and texts."

    @transaction.atomic
    def handle(self, *args, **opts):
        self.provinces()
        s = SiteSettings.load()
        if not s.about_text:
            s.about_text, s.ims_text, s.hse_text, s.rnd_text = sc.ABOUT_TEXT, sc.IMS_TEXT, sc.HSE_TEXT, sc.RND_TEXT
            s.hero_text = sc.HERO_TEXT
            s.meta_description = ("مهندسین مشاور ژرف آذران صدر؛ مطالعه، طراحی و نظارت در شبکه‌های آبیاری و زهکشی، "
                                  "آبخیزداری، GIS و نقشه‌برداری، با پروژه‌هایی در ۹ استان کشور.")
            s.save()
        self.services()
        self.offices()
        self.team()
        self.simple()
        self.projects()
        self.stdout.write(self.style.SUCCESS("seed complete"))

    def provinces(self):
        data = json.load(open(SEED / "data" / "iran_provinces.json", encoding="utf-8"))
        for p in data["provinces"]:
            Province.objects.update_or_create(
                slug=p["name_en"].lower().replace(" ", "-"),
                defaults=dict(name=p["name"], name_en=p["name_en"], iso_code=p["iso"], svg_path=p["path"],
                              label_x=p["cx"], label_y=p["cy"]))
        self.cities = {c["name"]: c for c in data["cities"]}

    def services(self):
        if ServiceArea.objects.exists():
            return
        for d in sc.SERVICES:
            d = dict(d)
            img = d.pop("image")
            d["bullets"] = "\n".join(d["bullets"])
            obj = ServiceArea(**d)
            attach(obj.image, img)
            obj.save()

    def offices(self):
        if Office.objects.exists():
            return
        data = json.load(open(SEED / "data" / "iran_provinces.json", encoding="utf-8"))
        cities = {c["name"]: c for c in data["cities"]}
        for d in sc.OFFICES:
            d = dict(d)
            photo = d.pop("photo")
            c = cities.get(d["city"])
            obj = Office(map_x=c["x"] if c else None, map_y=c["y"] if c else None, **d)
            attach(obj.photo, photo)
            obj.save()

    def team(self):
        if TeamMember.objects.exists():
            return
        for d in sc.TEAM:
            obj = TeamMember(name=d["name"], position=d["position"], degree=d["degree"], university=d["university"],
                             is_leadership=d["leader"], order=d["order"])
            attach(obj.photo, f"team_{d['key']}.jpg")
            obj.save()

    def simple(self):
        if not Certificate.objects.exists():
            for d in sc.CERTIFICATES:
                d = dict(d)
                img = d.pop("image")
                obj = Certificate(**d)
                attach(obj.image, img)
                obj.save()
        if not Client.objects.exists():
            Client.objects.bulk_create([Client(name=n, order=i) for i, n in enumerate(sc.CLIENTS)])
        if not ValueItem.objects.exists():
            ValueItem.objects.bulk_create([ValueItem(kind=k, text=t, order=i)
                                           for k, items in sc.VALUES.items() for i, t in enumerate(items)])
        if not TimelineEvent.objects.exists():
            TimelineEvent.objects.bulk_create([TimelineEvent(year=y, title=t, text=x) for y, t, x in sc.TIMELINE])
        if not RndResource.objects.exists():
            RndResource.objects.bulk_create([RndResource(title=t, value=v, order=i) for i, (t, v) in enumerate(sc.RND)])
        if not OrgUnit.objects.exists():
            made = []
            for i, (title, person, parent) in enumerate(sc.ORG):
                made.append(OrgUnit.objects.create(title=title, person=person, order=i,
                                                   parent=made[parent] if parent is not None else None))

    def projects(self):
        if Project.objects.exists():
            return
        provs = {p.name: p for p in Province.objects.all()}
        services = {s.slug: s for s in ServiceArea.objects.all()}
        rows = json.load(open(SEED / "data" / "projects.json", encoding="utf-8"))
        objs = []
        for r in rows:
            objs.append(Project(
                title=r["title"], province=provs[r["province"]], county=r["county"], service=services[r["service"]],
                client=r["client"], status=r["status"], contract_number=r["contract_number"],
                contract_date=r["contract_date"], end_year=r["end_year"], end_month=r["end_month"],
                scale=r["scale"], is_featured=any(h in r["title"] for h in FEATURED_SUBSTR)))
        Project.objects.bulk_create(objs)
        # keep the home page tidy: at most 6 featured
        keep = list(Project.objects.filter(is_featured=True).order_by("-end_year")[:6].values_list("pk", flat=True))
        Project.objects.filter(is_featured=True).exclude(pk__in=keep).update(is_featured=False)
