"""
seed_db.py — Populate the diseases database with realistic records and
plain-language recommendations aimed at smallholder farmers.

Usage:
    python backend/seed_db.py

IMPORTANT: The disease_name values here must exactly match the class names
produced by train_model.py / stored in backend/labels.json.  The names below
match the TensorFlow Datasets 'plant_village' class name strings.
"""

import os
import sys
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_BACKEND_DIR, "diseases.db")

# ── Seed data ─────────────────────────────────────────────────────────────────
# Each entry: (disease_name, crop_type, description, symptoms, recommendations)
# recommendations: list of (category, text)
# Categories must be one of: chemical, biological, cultural, preventive

DISEASES: list[dict] = [
    # ── TOMATO ────────────────────────────────────────────────────────────────
    {
        "disease_name": "Tomato___Early_blight",
        "crop_type": "Tomato",
        "description": (
            "Early blight is a common fungal disease of tomatoes caused by "
            "Alternaria solani. It attacks leaves, stems, and fruit, and spreads "
            "quickly in warm, humid conditions."
        ),
        "symptoms": (
            "Dark brown spots with concentric rings (target-board pattern) on "
            "older, lower leaves. Yellow halo around spots. Leaves turn yellow "
            "and drop early. Fruit may show dark, sunken lesions near the stem."
        ),
        "recommendations": [
            ("chemical",    "Spray with a copper-based fungicide (e.g. Copper Oxychloride) every 7–10 days. Start at first sign of symptoms. Follow label instructions and wear protective gear."),
            ("biological",  "Apply Trichoderma-based bio-fungicide to the soil and foliage. Bacillus subtilis sprays can slow fungal spread. These are safe around bees and livestock."),
            ("cultural",    "Remove and burn affected leaves immediately. Water at the base of the plant — avoid wetting the leaves. Stake or cage plants to improve air circulation."),
            ("preventive",  "Rotate tomatoes with non-related crops (e.g. maize or beans) every season. Use certified disease-free seed or seedlings. Mulch around plants to stop soil splash."),
        ],
    },
    {
        "disease_name": "Tomato___Late_blight",
        "crop_type": "Tomato",
        "description": (
            "Late blight is caused by the water mould Phytophthora infestans — "
            "the same pathogen responsible for the Irish Potato Famine. It spreads "
            "explosively in cool, wet weather and can destroy a crop within days."
        ),
        "symptoms": (
            "Large, irregular, water-soaked dark green or brown patches on leaves, "
            "often with a white mouldy ring on the underside. Infected stems turn "
            "brown and collapse. Fruit develops dark, firm, greasy-looking rot."
        ),
        "recommendations": [
            ("chemical",    "Apply Mancozeb or metalaxyl-based fungicide (e.g. Ridomil Gold) at first sign of symptoms. Spray every 5–7 days in wet weather. Rotate fungicide classes to prevent resistance."),
            ("biological",  "Use phosphonates (potassium phosphite) as a foliar spray to boost the plant's own defences. Apply Bacillus amyloliquefaciens products as a preventive measure."),
            ("cultural",    "Destroy infected plants immediately — do not compost them. Improve field drainage. Avoid overhead irrigation. Harvest early if disease spreads rapidly."),
            ("preventive",  "Plant resistant or tolerant varieties (e.g. Tanya F1, Tengeru 97). Avoid planting tomatoes next to potatoes. Scout fields at least twice a week during cool, rainy periods."),
        ],
    },
    {
        "disease_name": "Tomato___Leaf_Mold",
        "crop_type": "Tomato",
        "description": (
            "Leaf mould is caused by the fungus Passalora fulva. It thrives in "
            "high humidity and poor ventilation, especially under greenhouse or "
            "dense planting conditions."
        ),
        "symptoms": (
            "Pale green or yellow spots on the upper leaf surface. Velvety olive-green "
            "to grey mould growth on the underside of leaves. Infected leaves curl, "
            "wither, and drop. Fruit infection is rare but possible near the stem."
        ),
        "recommendations": [
            ("chemical",    "Spray with chlorothalonil or copper-based fungicide. Apply every 7–10 days during high humidity. Ensure thorough coverage of leaf undersides."),
            ("biological",  "Apply Trichoderma harzianum or Bacillus subtilis-based products as a foliar spray. Increase ventilation to reduce humidity naturally."),
            ("cultural",    "Space plants at least 50–60 cm apart to allow air flow. Remove affected leaves and bury or burn them. Avoid working in the field when plants are wet."),
            ("preventive",  "Use resistant varieties. Reduce humidity in enclosed growing spaces. Drip-irrigate rather than overhead irrigate. Keep the growing area weed-free."),
        ],
    },
    {
        "disease_name": "Tomato___Bacterial_spot",
        "crop_type": "Tomato",
        "description": (
            "Bacterial spot is caused by Xanthomonas species and spreads rapidly "
            "during warm, rainy weather through rain splash, insects, and infected "
            "tools. It affects leaves, stems, and fruit."
        ),
        "symptoms": (
            "Small, water-soaked spots on leaves that turn brown with a yellow "
            "halo. Spots may merge and cause large dead areas. Fruit shows small "
            "raised, scab-like spots that become rough, brown, and cracked. "
            "Severely affected leaves drop early."
        ),
        "recommendations": [
            ("chemical",    "Apply copper-based bactericides (e.g. Copper Oxychloride, Kocide) at 7-day intervals from transplanting. Do not use when temperatures are above 35°C as copper burn can occur."),
            ("biological",  "Seed treatment with Pseudomonas fluorescens before sowing. Foliar sprays of Bacillus amyloliquefaciens can reduce bacterial populations on leaves."),
            ("cultural",    "Remove and destroy infected plants immediately. Disinfect pruning tools with bleach (1 part bleach to 9 parts water) between plants. Avoid overhead watering."),
            ("preventive",  "Use certified disease-free seed or hot-water seed treatment (50°C for 25 minutes). Rotate crops for at least 2 years. Plant in well-drained soil with good air circulation."),
        ],
    },
    {
        "disease_name": "Tomato___healthy",
        "crop_type": "Tomato",
        "description": "This tomato plant appears healthy with no visible signs of disease.",
        "symptoms": "No disease symptoms detected.",
        "recommendations": [
            ("cultural",    "Continue regular scouting (at least twice a week) to catch any early signs of disease."),
            ("preventive",  "Maintain good field hygiene, balanced fertilisation, and consistent irrigation to keep plants vigorous and resistant to disease."),
        ],
    },

    # ── CORN / MAIZE ─────────────────────────────────────────────────────────
    {
        "disease_name": "Corn_(maize)___Common_rust_",
        "crop_type": "Maize",
        "description": (
            "Common rust of maize is caused by Puccinia sorghi. It spreads through "
            "windborne spores and is most severe in cool, moist conditions. It "
            "reduces photosynthesis and can significantly cut yield."
        ),
        "symptoms": (
            "Small, powdery, brick-red to brown pustules (blisters) scattered on "
            "both leaf surfaces. Pustules may merge into large streaks. Heavily "
            "infected leaves turn yellow and die prematurely."
        ),
        "recommendations": [
            ("chemical",    "Apply triazole-based fungicides (e.g. propiconazole, tebuconazole) at early stages of infection. A single well-timed spray can protect the crop for 3–4 weeks."),
            ("biological",  "No commercially available biocontrol is widely used for maize rust. Focus on cultural and preventive measures."),
            ("cultural",    "Scout regularly, especially during cool, wet periods. Remove and destroy heavily infected plants if practical on small plots."),
            ("preventive",  "Plant rust-resistant hybrid varieties whenever available. Plant early in the season to avoid peak spore periods. Avoid dense planting that traps moisture."),
        ],
    },
    {
        "disease_name": "Corn_(maize)___Northern_Leaf_Blight",
        "crop_type": "Maize",
        "description": (
            "Northern leaf blight (NLB) is caused by the fungus Exserohilum turcicum. "
            "It is favoured by moderate temperatures and extended periods of leaf "
            "wetness. Losses can exceed 50% in severe cases."
        ),
        "symptoms": (
            "Long, cigar-shaped grey-green to tan lesions (2.5–15 cm) running "
            "parallel to the leaf veins. Lesions may have dark borders and can "
            "cover entire leaves. Severely infected plants look scorched."
        ),
        "recommendations": [
            ("chemical",    "Apply foliar fungicides (e.g. mancozeb, chlorothalonil, or strobilurins) at tasselling stage if disease is present on the ear leaf or above. Repeat after 14 days if conditions remain favourable."),
            ("biological",  "Trichoderma-based soil applications can improve general plant health. Some Bacillus strains show moderate suppression of foliar pathogens."),
            ("cultural",    "Incorporate crop residues into the soil after harvest to speed up decomposition and reduce spore carry-over. Avoid fields with a history of heavy NLB infection."),
            ("preventive",  "Plant resistant hybrids (check with your local extension officer for varieties rated for NLB resistance). Practise 2-year crop rotation. Plant at the correct spacing to allow good air movement."),
        ],
    },
    {
        "disease_name": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
        "crop_type": "Maize",
        "description": (
            "Grey leaf spot (GLS) is caused by Cercospora zeae-maydis. It is one "
            "of the most economically damaging maize diseases worldwide, especially "
            "in warm, humid regions with frequent dew."
        ),
        "symptoms": (
            "Narrow, rectangular, grey to brown lesions that are limited by leaf "
            "veins. Lesions have a bleached or tan centre with yellow edges. "
            "Under high humidity, a grey mould (spores) may be visible. Whole "
            "leaves can die in severe cases."
        ),
        "recommendations": [
            ("chemical",    "Strobilurin-based fungicides (e.g. azoxystrobin, pyraclostrobin) are most effective against GLS. Apply at early infection and repeat every 14–21 days if warranted. Mix with triazoles for broader spectrum protection."),
            ("biological",  "Bacillus subtilis and Trichoderma products used as foliar sprays show some suppressive effect. Combine with cultural management for best results."),
            ("cultural",    "Plough in or remove maize stover after harvest — the pathogen overwinters in old residue. Avoid continuous maize-on-maize cropping. Improve drainage in waterlogged areas."),
            ("preventive",  "Use GLS-resistant hybrids — this is the most cost-effective control measure. Maintain balanced soil fertility; nitrogen deficiency makes plants more susceptible. Plant at recommended densities."),
        ],
    },
    {
        "disease_name": "Corn_(maize)___healthy",
        "crop_type": "Maize",
        "description": "This maize plant appears healthy with no visible signs of disease.",
        "symptoms": "No disease symptoms detected.",
        "recommendations": [
            ("cultural",    "Continue regular field scouting, especially during and after rainy periods."),
            ("preventive",  "Maintain correct plant spacing, balanced fertilisation, and weed control to keep maize vigorous."),
        ],
    },

    # ── POTATO ───────────────────────────────────────────────────────────────
    {
        "disease_name": "Potato___Early_blight",
        "crop_type": "Potato",
        "description": (
            "Potato early blight is caused by Alternaria solani — the same "
            "pathogen that affects tomatoes. It typically attacks older, "
            "stressed plants and can reduce tuber quality and yield."
        ),
        "symptoms": (
            "Dark brown, circular to oval spots with concentric rings on older "
            "leaves. Yellow tissue surrounds the spots. Stems may also develop "
            "lesions. Severe infections cause defoliation."
        ),
        "recommendations": [
            ("chemical",    "Apply protectant fungicides (e.g. mancozeb, chlorothalonil) every 7–10 days from first symptoms. Copper-based products also work well. Do not wait until the disease is widespread."),
            ("biological",  "Bacillus subtilis-based bio-fungicides can reduce disease severity. Apply as a foliar spray starting at the first sign of infection."),
            ("cultural",    "Remove and destroy infected plant material promptly. Irrigate in the morning so leaves dry before nightfall. Keep plants well-nourished — stressed plants are most vulnerable."),
            ("preventive",  "Use certified disease-free seed tubers. Rotate potatoes with non-solanaceous crops for at least 3 years. Destroy volunteer potato plants that can carry the fungus over."),
        ],
    },
    {
        "disease_name": "Potato___Late_blight",
        "crop_type": "Potato",
        "description": (
            "Potato late blight, caused by Phytophthora infestans, is the most "
            "destructive potato disease in the world. It can destroy an entire "
            "field within 1–2 weeks during cool, wet weather."
        ),
        "symptoms": (
            "Water-soaked, irregular dark green lesions on leaves that quickly "
            "turn brown-black. White mouldy growth on the underside of leaves "
            "in humid conditions. Stems turn brown and collapse. Tubers develop "
            "reddish-brown internal rot with an unpleasant smell."
        ),
        "recommendations": [
            ("chemical",    "Apply systemic fungicides (e.g. metalaxyl + mancozeb, cymoxanil + mancozeb) preventively before disease appears in high-risk weather. Rotate fungicide groups to prevent resistance. Spray every 5–7 days during wet periods."),
            ("biological",  "Copper-based products act as both protectant and mild systemic options. Phosphonates (potassium phosphite) strengthen plant defences. Apply before infection pressure is high."),
            ("cultural",    "Hilling (mounding soil around stems) protects tubers from spores washing down. Destroy infected haulms before harvest. Never store diseased tubers."),
            ("preventive",  "Plant certified, disease-free seed tubers. Choose varieties with late blight resistance (e.g. Sarpo Mira, Victoria). Monitor weather forecasts — spray prophylactically when cool nights and wet days are predicted."),
        ],
    },
    {
        "disease_name": "Potato___healthy",
        "crop_type": "Potato",
        "description": "This potato plant appears healthy with no visible signs of disease.",
        "symptoms": "No disease symptoms detected.",
        "recommendations": [
            ("cultural",    "Continue regular scouting, especially during cool, wet weather when late blight risk is highest."),
            ("preventive",  "Maintain correct earthing-up, balanced fertilisation, and good field sanitation to keep plants vigorous and tubers protected."),
        ],
    },
]


# ── Seeding logic ─────────────────────────────────────────────────────────────

def seed() -> None:
    if not os.path.exists(DB_PATH):
        logger.error(
            "Database not found at %s. "
            "Start the Flask server first (it creates the database automatically).",
            DB_PATH,
        )
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    inserted_diseases = 0
    inserted_recs     = 0
    skipped           = 0

    for entry in DISEASES:
        # Skip if this disease name is already in the database
        cur.execute(
            "SELECT disease_id FROM diseases WHERE disease_name = ?",
            (entry["disease_name"],),
        )
        existing = cur.fetchone()
        if existing:
            logger.info("  [skip] %s (already exists)", entry["disease_name"])
            skipped += 1
            continue

        cur.execute(
            "INSERT INTO diseases (disease_name, crop_type, description, symptoms) "
            "VALUES (?, ?, ?, ?)",
            (entry["disease_name"], entry["crop_type"],
             entry["description"], entry["symptoms"]),
        )
        disease_id = cur.lastrowid
        inserted_diseases += 1

        for category, text in entry["recommendations"]:
            cur.execute(
                "INSERT INTO recommendations (disease_id, category, recommendation_text) "
                "VALUES (?, ?, ?)",
                (disease_id, category, text),
            )
            inserted_recs += 1

        logger.info("  [ok]   %s", entry["disease_name"])

    conn.commit()
    conn.close()

    logger.info(
        "\nSeeding complete: %d diseases inserted, %d skipped (already existed). "
        "%d recommendations inserted.",
        inserted_diseases, skipped, inserted_recs,
    )
    logger.info(
        "\nNOTE: The disease_name values above must match the class names in "
        "backend/labels.json exactly. If you trained with a different dataset "
        "or renamed classes, update the DISEASES list in this file accordingly."
    )


if __name__ == "__main__":
    logger.info("Seeding database at %s …", DB_PATH)
    seed()
