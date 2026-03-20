"""
Synthetic Data Generator for Engineering Change Impact Copilot

Generates realistic engineering data including:
- Parts (50-100)
- Assemblies (10-20)
- BOMs
- Documents (30-50)
- Change Requests (20)
- Specifications (20)
- Test Reports (10)
"""

import json
import random
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy import text

# Import models
import sys
sys.path.insert(0, str(__file__).replace("scripts/generate_data.py", ""))
from app.models.database import (
    Part, Assembly, BOMEntry, Document, ChangeRequest,
    Specification, TestReport, DocumentChunk, DocumentPartLink,
    PartStatus, DocumentStatus, ChangeRequestStatus
)
from app.core.config import settings

# Materials database
MATERIALS = [
    ("Edelstahl 1.4404", "316L stainless steel, corrosion resistant"),
    ("Edelstahl 1.4301", "304 stainless steel, general purpose"),
    ("Aluminium 6061", "Aluminum alloy, good machinability"),
    ("Titan Grade 5", "Ti-6Al-4V, high strength"),
    ("Hastelloy C-276", "Nickel alloy, extreme corrosion resistance"),
    ("Inconel 625", "Nickel-chromium alloy, high temperature"),
    ("PTFE", "Polytetrafluoroethylene, chemical resistant"),
    ("NBR", "Nitrile rubber, oil resistant"),
    ("EPDM", "Ethylene propylene rubber, weather resistant"),
    ("Bronze CuSn12", "Tin bronze, bearing applications"),
]

# Part categories
PART_CATEGORIES = [
    ("Ventil", ["Sicherheitsventil", "Regelventil", "Absperrventil", "Rückschlagventil", "Drosselventil"]),
    ("Pumpe", ["Kreiselpumpe", "Kolbenpumpe", "Zahnradpumpe", "Membranpumpe"]),
    ("Dichtung", ["O-Ring", "Flachdichtung", "Wellendichtring", "Lippendichtung"]),
    ("Flansch", ["Vorschweißflansch", "Blindflansch", "Losflansch", "Gewindeflansch"]),
    ("Rohr", ["Druckrohr", "Saugrohr", "Bypassrohr", "Messrohr"]),
    ("Sensor", ["Drucksensor", "Temperatursensor", "Durchflusssensor", "Füllstandsensor"]),
    ("Gehäuse", ["Pumpengehäuse", "Ventilgehäuse", "Sensorgehäuse", "Steuergehäuse"]),
    ("Welle", ["Antriebswelle", "Pumpenwelle", "Abtriebswelle"]),
    ("Lager", ["Kugellager", "Rollenlager", "Gleitlager", "Axiallager"]),
    ("Schraube", ["Sechskantschraube", "Zylinderschraube", "Stiftschraube"]),
]

# Assembly types
ASSEMBLY_TYPES = [
    "Pumpeneinheit",
    "Ventilblock",
    "Antriebsmodul",
    "Steuereinheit",
    "Filtermodul",
    "Druckbehälter",
    "Wärmetauscher",
    "Messstation",
    "Absperrgruppe",
    "Sicherheitsgruppe",
]


def random_date(start_days_ago=365, end_days_ago=0):
    """Generate a random date in the past."""
    days_ago = random.randint(end_days_ago, start_days_ago)
    return datetime.now() - timedelta(days=days_ago)


def generate_parts(session: Session, count: int = 75):
    """Generate synthetic parts."""
    parts = []

    # First, create the key parts from PLAN.md
    key_parts = [
        ("V-202", "Sicherheitsventil DN50", "Sicherheitsventil für Überdruckschutz, Ansprechdruck 16 bar", "Edelstahl 1.4404", 3.5),
        ("V-203", "Regelventil DN80", "Pneumatisch gesteuertes Regelventil für Durchflussregelung", "Edelstahl 1.4301", 8.2),
        ("V-204", "Absperrventil DN100", "Handbetätigtes Absperrventil für Wartungszwecke", "Edelstahl 1.4404", 12.5),
        ("P-101", "Kreiselpumpe 15kW", "Horizontale Kreiselpumpe für Prozessmedien", "Hastelloy C-276", 85.0),
        ("P-102", "Dosierpumpe", "Membran-Dosierpumpe für chemische Zusätze", "PTFE", 12.0),
        ("S-301", "Drucksensor 0-25bar", "Keramischer Drucktransmitter mit 4-20mA Ausgang", "Edelstahl 1.4404", 0.5),
        ("S-302", "Temperatursensor PT100", "Widerstandsthermometer für Prozesstemperaturmessung", "Edelstahl 1.4301", 0.3),
        ("F-101", "Vorschweißflansch DN100", "Flansch nach DIN EN 1092-1, PN16", "Edelstahl 1.4404", 4.8),
        ("D-101", "O-Ring DN50", "Dichtring aus EPDM für Ventilgehäuse", "EPDM", 0.05),
        ("D-102", "Flachdichtung DN100", "Grafitdichtung für Flanschverbindungen", "Graphit", 0.1),
    ]

    for part_num, name, desc, material, weight in key_parts:
        part = Part(
            part_number=part_num,
            name=name,
            description=desc,
            material=material,
            weight_kg=weight,
            status=PartStatus.ACTIVE,
            revision=random.choice(["A", "B", "C"]),
            created_at=random_date(365, 30),
            updated_at=random_date(30, 0)
        )
        session.add(part)
        parts.append(part)

    # Generate additional random parts
    for i in range(count - len(key_parts)):
        category, subtypes = random.choice(PART_CATEGORIES)
        subtype = random.choice(subtypes)
        material_name, _ = random.choice(MATERIALS)

        part_prefix = category[0].upper()
        part_num = f"{part_prefix}-{random.randint(100, 999)}"

        part = Part(
            part_number=part_num,
            name=f"{subtype} {random.choice(['DN25', 'DN50', 'DN80', 'DN100', 'DN150'])}",
            description=f"{subtype} für industrielle Anwendungen. Material: {material_name}",
            material=material_name,
            weight_kg=round(random.uniform(0.1, 50.0), 2),
            status=random.choice([PartStatus.ACTIVE, PartStatus.ACTIVE, PartStatus.ACTIVE, PartStatus.DRAFT]),
            revision=random.choice(["A", "B", "C", "D"]),
            created_at=random_date(365, 30),
            updated_at=random_date(30, 0)
        )
        session.add(part)
        parts.append(part)

    session.commit()
    print(f"Created {len(parts)} parts")
    return parts


def generate_assemblies(session: Session, count: int = 15):
    """Generate synthetic assemblies."""
    assemblies = []

    # Key assemblies from PLAN.md
    key_assemblies = [
        ("BG-240", "Pumpeneinheit Hauptprozess", "Komplette Pumpeneinheit mit Motor, Kupplung und Grundrahmen"),
        ("BG-241", "Ventilblock Einlass", "Ventilgruppe für Einlassregelung mit Sicherheitsventil"),
        ("BG-242", "Filtermodul Primär", "Primärfilter mit Bypassventil und Differenzdruckanzeige"),
        ("BG-243", "Messstation Prozess", "Integrierte Messstation für Druck, Temperatur und Durchfluss"),
        ("BG-244", "Sicherheitsgruppe", "Sicherheitsrelevante Komponenten inkl. Überdruckventil und Notabschaltung"),
    ]

    for asm_num, name, desc in key_assemblies:
        assembly = Assembly(
            assembly_number=asm_num,
            name=name,
            description=desc,
            status=PartStatus.ACTIVE,
            revision=random.choice(["A", "B"]),
            created_at=random_date(365, 60),
            updated_at=random_date(60, 0)
        )
        session.add(assembly)
        assemblies.append(assembly)

    # Generate additional assemblies
    for i in range(count - len(key_assemblies)):
        asm_type = random.choice(ASSEMBLY_TYPES)
        asm_num = f"BG-{random.randint(100, 999)}"

        assembly = Assembly(
            assembly_number=asm_num,
            name=f"{asm_type} {random.choice(['A', 'B', 'Standard', 'Spezial'])}",
            description=f"{asm_type} für Prozessanlagen. Konfiguration nach Kundenanforderung.",
            status=random.choice([PartStatus.ACTIVE, PartStatus.ACTIVE, PartStatus.DRAFT]),
            revision=random.choice(["A", "B", "C"]),
            created_at=random_date(365, 60),
            updated_at=random_date(60, 0)
        )
        session.add(assembly)
        assemblies.append(assembly)

    session.commit()
    print(f"Created {len(assemblies)} assemblies")
    return assemblies


def generate_bom(session: Session, parts: list, assemblies: list):
    """Generate bill of materials entries."""
    bom_entries = []

    for assembly in assemblies:
        # Each assembly gets 3-8 parts
        num_parts = random.randint(3, 8)
        selected_parts = random.sample(parts, min(num_parts, len(parts)))

        for i, part in enumerate(selected_parts):
            entry = BOMEntry(
                assembly_id=assembly.id,
                part_id=part.id,
                quantity=random.randint(1, 4),
                position=f"Pos. {(i+1)*10}"
            )
            session.add(entry)
            bom_entries.append(entry)

        # Some assemblies contain sub-assemblies
        if random.random() > 0.6:
            other_assemblies = [a for a in assemblies if a.id != assembly.id]
            if other_assemblies:
                child = random.choice(other_assemblies)
                entry = BOMEntry(
                    assembly_id=assembly.id,
                    child_assembly_id=child.id,
                    quantity=1,
                    position=f"Pos. {(len(selected_parts)+1)*10}"
                )
                session.add(entry)
                bom_entries.append(entry)

    session.commit()
    print(f"Created {len(bom_entries)} BOM entries")
    return bom_entries


def generate_documents(session: Session, parts: list, assemblies: list, count: int = 40):
    """Generate synthetic documents."""
    documents = []

    # Document templates
    doc_templates = [
        ("SPEC", "Spezifikation", [
            ("Druckbeständigkeit", "Anforderungen an die Druckbeständigkeit der Komponenten. Maximaler Betriebsdruck: {pressure} bar. Testdruck: {test_pressure} bar. Materialanforderungen gemäß DIN EN 10216."),
            ("Korrosionsbeständigkeit", "Spezifikation der Korrosionsbeständigkeit. Einsatzmedium: Prozesswasser mit pH {ph}. Chloridgehalt max. {chloride} ppm."),
            ("Temperaturbereich", "Zulässiger Temperaturbereich: {temp_min}°C bis {temp_max}°C. Thermische Ausdehnung gemäß EN 13480."),
            ("Oberflächengüte", "Oberflächenrauheit Ra max. {ra} µm. Schweißnähte gemäß DIN EN ISO 5817, Bewertungsgruppe B."),
        ]),
        ("TEST", "Prüfbericht", [
            ("Druckprüfung", "Hydrostatische Druckprüfung durchgeführt am {date}. Prüfdruck: {pressure} bar. Haltezeit: 30 Minuten. Ergebnis: {result}."),
            ("Korrosionstest", "Salzsprühnebeltest nach DIN EN ISO 9227. Testdauer: {hours} Stunden. Korrosionsgrad: {grade}. Ergebnis: {result}."),
            ("Funktionstest", "Funktionsprüfung der Komponente unter Betriebsbedingungen. Durchfluss: {flow} m³/h. Druckabfall: {dp} bar. Ergebnis: {result}."),
            ("Dichtigkeitsprüfung", "Leckagetest mit Helium-Massenspektrometer. Leckagerate: {leak} mbar·l/s. Grenzwert: 1×10⁻⁸ mbar·l/s. Ergebnis: {result}."),
        ]),
        ("DWG", "Zeichnung", [
            ("Einzelteilzeichnung", "Technische Zeichnung {part}. Maßstab 1:{scale}. Toleranzen nach ISO 2768-mK."),
            ("Baugruppe", "Zusammenbauzeichnung {assembly}. Stückliste und Positionsnummern nach DIN 6789."),
            ("Explosionszeichnung", "Explosionsdarstellung zur Montage. Alle Einzelteile nummeriert."),
        ]),
        ("MANUAL", "Handbuch", [
            ("Betriebsanleitung", "Anleitung für Inbetriebnahme und Betrieb. Sicherheitshinweise gemäß Maschinenrichtlinie 2006/42/EG."),
            ("Wartungsanleitung", "Wartungsintervalle und -arbeiten. Empfohlene Ersatzteile. Schmierplan."),
            ("Montageanleiung", "Schrittweise Montageanleitung mit Drehmomentangaben. Erforderliches Werkzeug."),
        ]),
    ]

    # Key documents from PLAN.md
    key_docs = [
        ("SPEC-014", "Spezifikation Druckbeständigkeit", "SPEC",
         """Spezifikation für druckführende Komponenten

1. Geltungsbereich
Diese Spezifikation gilt für alle druckführenden Teile der Baugruppen BG-240, BG-241 und BG-244.

2. Druckanforderungen
- Maximaler Betriebsdruck (PS): 16 bar
- Prüfdruck: 24 bar (1.5 × PS)
- Maximale Temperatur: 150°C

3. Materialanforderungen
- Werkstoff: Edelstahl 1.4404 (AISI 316L)
- Mindeststreckgrenze Rp0.2: 220 MPa
- Mindestbruchdehnung A5: 40%

4. Prüfung
Jede Komponente muss einer hydrostatischen Druckprüfung unterzogen werden.
Haltezeit: 30 Minuten bei Prüfdruck.

5. Dokumentation
Prüfzertifikat 3.1 nach EN 10204 erforderlich.

Referenzierte Teile: V-202, V-203, P-101, F-101"""),

        ("TEST-009", "Korrosionstest 1.4404", "TEST",
         """Prüfbericht Korrosionsbeständigkeit

Prüfobjekt: Material 1.4404 (Edelstahl)
Prüfdatum: 15.01.2024
Prüfer: Dr. M. Schmidt

1. Prüfverfahren
Salzsprühnebeltest nach DIN EN ISO 9227
Testmedium: 5% NaCl-Lösung
Temperatur: 35°C ± 2°C
Dauer: 720 Stunden

2. Prüflinge
- 3 Proben V-202 Ventilgehäuse
- 3 Proben F-101 Flansch
- 3 Proben P-101 Pumpengehäuse

3. Ergebnisse
Alle Proben zeigen keine sichtbare Korrosion nach Testende.
Bewertung nach EN ISO 10289: Schutzstufe 10 (keine Korrosion)

4. Bewertung
BESTANDEN

Der Werkstoff 1.4404 erfüllt die Korrosionsanforderungen für den Einsatz
in Prozesswasseranwendungen mit Chloridgehalt bis 200 ppm.

Betroffene Teile: V-202, F-101, P-101, BG-240"""),

        ("DWG-1102", "Explosionszeichnung BG-240", "DWG",
         """Technische Dokumentation

Zeichnungsnummer: DWG-1102
Titel: Explosionszeichnung Pumpeneinheit BG-240
Revision: C
Datum: 10.02.2024

Enthaltene Komponenten:
Pos. 10 - Pumpengehäuse P-101
Pos. 20 - Sicherheitsventil V-202
Pos. 30 - Flansch F-101 (2x)
Pos. 40 - O-Ring D-101 (4x)
Pos. 50 - Drucksensor S-301
Pos. 60 - Temperatursensor S-302

Montageanweisungen:
1. Grundrahmen positionieren
2. Pumpe P-101 montieren (M12 Schrauben, Drehmoment 80 Nm)
3. Einlassflansch mit Dichtung montieren
4. Auslassflansch mit Dichtung montieren
5. Ventil V-202 installieren
6. Sensoren S-301 und S-302 anschließen
7. Elektrische Verbindungen herstellen

Referenzierte Baugruppe: BG-240
Referenzierte Teile: P-101, V-202, F-101, D-101, S-301, S-302"""),

        ("SPEC-015", "Spezifikation Material M-17", "SPEC",
         """Materialspezifikation M-17

Material: Edelstahl 1.4404 (X2CrNiMo17-12-2)

1. Chemische Zusammensetzung (in %)
- C: max. 0.030
- Cr: 16.5 - 18.5
- Ni: 10.0 - 13.0
- Mo: 2.0 - 2.5
- Mn: max. 2.0
- Si: max. 1.0
- P: max. 0.045
- S: max. 0.030

2. Mechanische Eigenschaften
- Zugfestigkeit Rm: 520 - 670 MPa
- Streckgrenze Rp0.2: min. 220 MPa
- Bruchdehnung A5: min. 40%
- Härte: max. 215 HB

3. Anwendungsbereich
- Chemische Industrie
- Lebensmittelindustrie
- Pharmazeutische Industrie
- Meerwasseranwendungen

4. Prüfanforderungen
- Werkszeugnis 3.1 nach EN 10204
- Positive Materialidentifikation (PMI)
- Intergranulare Korrosionsprüfung nach ASTM A262

Verwendung in: V-202, V-203, P-101, F-101, S-301"""),
    ]

    for doc_num, title, doc_type, content in key_docs:
        doc = Document(
            document_number=doc_num,
            title=title,
            document_type=doc_type,
            description=title,
            content=content,
            version="1.0",
            status=DocumentStatus.RELEASED,
            created_at=random_date(180, 30),
            updated_at=random_date(30, 0)
        )
        session.add(doc)
        documents.append(doc)

    # Generate additional documents
    doc_counter = 100
    for _ in range(count - len(key_docs)):
        doc_type, type_name, templates = random.choice(doc_templates)
        template_name, template_content = random.choice(templates)

        doc_num = f"{doc_type}-{doc_counter:03d}"
        doc_counter += 1

        # Fill template with random values
        content = template_content.format(
            pressure=random.randint(10, 40),
            test_pressure=random.randint(15, 60),
            ph=round(random.uniform(6.0, 8.5), 1),
            chloride=random.randint(50, 500),
            temp_min=random.randint(-20, 20),
            temp_max=random.randint(80, 200),
            ra=round(random.uniform(0.8, 6.3), 1),
            date=random_date(90, 1).strftime("%d.%m.%Y"),
            result=random.choice(["BESTANDEN", "BESTANDEN", "BESTANDEN", "BEDINGT BESTANDEN"]),
            hours=random.choice([240, 480, 720, 1000]),
            grade=random.choice(["Ra 0", "Ra 1", "Ra 2"]),
            flow=random.randint(10, 200),
            dp=round(random.uniform(0.1, 2.0), 2),
            leak=f"{random.randint(1, 9)}×10⁻{random.randint(8, 10)}",
            part=random.choice(parts).part_number if parts else "P-001",
            assembly=random.choice(assemblies).assembly_number if assemblies else "BG-001",
            scale=random.choice([1, 2, 5, 10]),
        )

        doc = Document(
            document_number=doc_num,
            title=f"{type_name} {template_name}",
            document_type=doc_type,
            description=f"{type_name}: {template_name}",
            content=content,
            version=f"{random.randint(1, 3)}.{random.randint(0, 5)}",
            status=random.choice([DocumentStatus.RELEASED, DocumentStatus.RELEASED, DocumentStatus.APPROVED, DocumentStatus.DRAFT]),
            created_at=random_date(365, 30),
            updated_at=random_date(30, 0)
        )
        session.add(doc)
        documents.append(doc)

    session.commit()
    print(f"Created {len(documents)} documents")
    return documents


def generate_change_requests(session: Session, parts: list, assemblies: list, count: int = 20):
    """Generate synthetic change requests."""
    change_requests = []

    cr_templates = [
        ("Materialänderung", "Änderung des Materials von {old_mat} auf {new_mat} wegen {reason}."),
        ("Designänderung", "Anpassung der Geometrie zur {reason}."),
        ("Lieferantenänderung", "Wechsel des Lieferanten für {part} wegen {reason}."),
        ("Normänderung", "Anpassung an neue Norm {norm}. Betrifft {scope}."),
        ("Kostenoptimierung", "Kostenreduzierung durch {method}. Erwartete Einsparung: {savings}%."),
        ("Qualitätsverbesserung", "Qualitätssteigerung durch {method}. Ziel: {target}."),
    ]

    reasons = [
        "Lieferengpass",
        "Kosteneinsparung",
        "verbesserte Korrosionsbeständigkeit",
        "erhöhte Druckfestigkeit",
        "Kundenanforderung",
        "Normänderung",
        "Fertigungsoptimierung",
        "Qualitätsprobleme beim Vorgänger",
    ]

    # Key CRs from PLAN.md
    key_crs = [
        ("CR-031", "Materialänderung V-202", "high",
         "Änderung des Ventilgehäusematerials von 1.4301 auf 1.4404 wegen erhöhter Korrosionsanforderungen.",
         "Kunde fordert erhöhte Korrosionsbeständigkeit für Chloridhaltige Medien. Bisheriges Material 1.4301 nicht geeignet.",
         ["V-202"], ["BG-240", "BG-241"]),
        ("CR-032", "Druckerhöhung BG-240", "critical",
         "Erhöhung des maximalen Betriebsdrucks von 16 bar auf 25 bar.",
         "Prozessänderung beim Kunden erfordert höheren Betriebsdruck. Alle druckführenden Teile betroffen.",
         ["V-202", "P-101", "F-101"], ["BG-240"]),
        ("CR-033", "Lieferantenwechsel Dichtungen", "medium",
         "Wechsel des Dichtungslieferanten für alle EPDM-Dichtungen.",
         "Aktueller Lieferant kann Liefertermine nicht einhalten. Qualifikation neuer Lieferant erforderlich.",
         ["D-101", "D-102"], []),
    ]

    for cr_num, title, priority, desc, reason, affected_p, affected_a in key_crs:
        cr = ChangeRequest(
            cr_number=cr_num,
            title=title,
            description=desc,
            reason=reason,
            priority=priority,
            status=random.choice([ChangeRequestStatus.OPEN, ChangeRequestStatus.IN_PROGRESS, ChangeRequestStatus.REVIEW]),
            requestor=random.choice(["M. Müller", "S. Schmidt", "K. Weber", "A. Fischer"]),
            affected_parts=json.dumps(affected_p),
            affected_assemblies=json.dumps(affected_a),
            created_at=random_date(90, 10),
            updated_at=random_date(10, 0),
            target_date=datetime.now() + timedelta(days=random.randint(30, 180))
        )
        session.add(cr)
        change_requests.append(cr)

    # Generate additional CRs
    cr_counter = 40
    for _ in range(count - len(key_crs)):
        cr_type, template = random.choice(cr_templates)

        cr_num = f"CR-{cr_counter:03d}"
        cr_counter += 1

        affected_p = random.sample([p.part_number for p in parts], min(random.randint(1, 4), len(parts)))
        affected_a = random.sample([a.assembly_number for a in assemblies], min(random.randint(0, 2), len(assemblies)))

        desc = template.format(
            old_mat=random.choice(MATERIALS)[0],
            new_mat=random.choice(MATERIALS)[0],
            reason=random.choice(reasons),
            part=affected_p[0] if affected_p else "unbekannt",
            norm=random.choice(["DIN EN 1092-1:2024", "ISO 9001:2024", "PED 2014/68/EU"]),
            scope="Flanschverbindungen" if random.random() > 0.5 else "Druckbehälter",
            method=random.choice(["alternative Fertigung", "Materialsubstitution", "Designvereinfachung"]),
            savings=random.randint(5, 25),
            target=random.choice(["Reduzierung Ausschussrate um 50%", "MTBF +20%", "Null-Fehler-Strategie"]),
        )

        cr = ChangeRequest(
            cr_number=cr_num,
            title=f"{cr_type} - {affected_p[0] if affected_p else 'Allgemein'}",
            description=desc,
            reason=random.choice(reasons),
            priority=random.choice(["low", "medium", "medium", "high", "critical"]),
            status=random.choice(list(ChangeRequestStatus)),
            requestor=random.choice(["M. Müller", "S. Schmidt", "K. Weber", "A. Fischer", "J. Bauer", "L. Hoffmann"]),
            affected_parts=json.dumps(affected_p),
            affected_assemblies=json.dumps(affected_a),
            created_at=random_date(180, 10),
            updated_at=random_date(10, 0),
            target_date=datetime.now() + timedelta(days=random.randint(30, 365))
        )
        session.add(cr)
        change_requests.append(cr)

    session.commit()
    print(f"Created {len(change_requests)} change requests")
    return change_requests


def generate_specifications(session: Session, count: int = 20):
    """Generate synthetic specifications."""
    specifications = []

    spec_categories = [
        ("pressure", "Druckbeständigkeit"),
        ("temperature", "Temperaturbeständigkeit"),
        ("material", "Materialanforderungen"),
        ("corrosion", "Korrosionsbeständigkeit"),
        ("dimensions", "Maßtoleranzen"),
        ("surface", "Oberflächengüte"),
    ]

    for i in range(count):
        category, category_name = random.choice(spec_categories)

        spec = Specification(
            spec_number=f"SPEC-{i+100:03d}",
            title=f"{category_name} Spezifikation",
            description=f"Anforderungsspezifikation für {category_name}",
            category=category,
            requirements=f"Detaillierte Anforderungen für {category_name}. "
                        f"Prüfverfahren nach DIN EN {random.randint(1000, 9999)}. "
                        f"Akzeptanzkriterien definiert.",
            version=f"{random.randint(1, 3)}.{random.randint(0, 9)}",
            status=random.choice([DocumentStatus.RELEASED, DocumentStatus.APPROVED]),
            created_at=random_date(365, 60),
            updated_at=random_date(60, 0)
        )
        session.add(spec)
        specifications.append(spec)

    session.commit()
    print(f"Created {len(specifications)} specifications")
    return specifications


def generate_test_reports(session: Session, specifications: list, count: int = 15):
    """Generate synthetic test reports."""
    test_reports = []

    test_types = [
        ("corrosion", "Korrosionstest"),
        ("pressure", "Druckprüfung"),
        ("fatigue", "Ermüdungstest"),
        ("leak", "Dichtigkeitsprüfung"),
        ("function", "Funktionstest"),
        ("dimensional", "Maßprüfung"),
    ]

    testers = ["Dr. M. Schmidt", "Dipl.-Ing. K. Weber", "B.Eng. S. Müller", "M.Sc. A. Fischer"]

    for i in range(count):
        test_type, test_name = random.choice(test_types)
        result = random.choice(["passed", "passed", "passed", "passed", "conditional", "failed"])

        findings = None
        if result == "conditional":
            findings = "Geringfügige Abweichung festgestellt. Nacharbeit empfohlen."
        elif result == "failed":
            findings = "Grenzwertüberschreitung. Ursachenanalyse erforderlich."

        report = TestReport(
            test_number=f"TEST-{i+100:03d}",
            title=f"{test_name} Bericht",
            description=f"Durchführung und Dokumentation {test_name}",
            test_type=test_type,
            result=result,
            test_date=random_date(180, 1),
            tester=random.choice(testers),
            findings=findings,
            related_spec_id=random.choice(specifications).id if specifications and random.random() > 0.3 else None,
            created_at=random_date(180, 1)
        )
        session.add(report)
        test_reports.append(report)

    session.commit()
    print(f"Created {len(test_reports)} test reports")
    return test_reports


def generate_document_links(session: Session, documents: list, parts: list, assemblies: list):
    """Generate links between documents and parts/assemblies."""
    links = []

    for doc in documents:
        # Link to random parts
        num_parts = random.randint(1, 5)
        selected_parts = random.sample(parts, min(num_parts, len(parts)))

        for part in selected_parts:
            link = DocumentPartLink(
                document_id=doc.id,
                part_id=part.id,
                link_type=random.choice(["reference", "defines", "tests", "specifies"])
            )
            session.add(link)
            links.append(link)

        # Link to random assemblies
        if random.random() > 0.5:
            num_assemblies = random.randint(1, 3)
            selected_assemblies = random.sample(assemblies, min(num_assemblies, len(assemblies)))

            for assembly in selected_assemblies:
                link = DocumentPartLink(
                    document_id=doc.id,
                    assembly_id=assembly.id,
                    link_type=random.choice(["reference", "defines", "assembly_drawing"])
                )
                session.add(link)
                links.append(link)

    session.commit()
    print(f"Created {len(links)} document links")
    return links


def main():
    """Main function to generate all synthetic data."""
    print("=" * 50)
    print("Engineering Change Impact Copilot - Data Generator")
    print("=" * 50)

    # Create database engine
    engine = create_engine(settings.DATABASE_URL, echo=False)

    # Create extension and tables
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Generate data
        parts = generate_parts(session)
        assemblies = generate_assemblies(session)
        generate_bom(session, parts, assemblies)
        documents = generate_documents(session, parts, assemblies)
        generate_change_requests(session, parts, assemblies)
        specifications = generate_specifications(session)
        generate_test_reports(session, specifications)
        generate_document_links(session, documents, parts, assemblies)

    print("=" * 50)
    print("Data generation complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
