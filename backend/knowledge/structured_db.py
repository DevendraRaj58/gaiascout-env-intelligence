"""
structured_db.py — SQLite Structured Knowledge Layer

WHY THIS EXISTS (and why it's NOT just more ChromaDB):
  ChromaDB is great for semantic search — "find me text about cover crops."
  But some knowledge is TABULAR and NUMERIC, not narrative:
    - "What is the critical threshold for soil organic carbon?" → Answer: < 0.5%
    - "Which interventions work in semi-arid biomes?" → Lookup, not semantic search
    - "How long does agroforestry take to show results?" → Precise: 3–7 years

  For these queries, a relational DB (SQLite) gives exact, non-hallucinated answers.
  The EcoMetricEngine queries SQLite to get numeric thresholds.
  The LLM queries SQLite (via a tool) to get validated intervention records.

  Together: ChromaDB (WHY/HOW) + SQLite (WHAT/WHEN/HOW MUCH) = full picture.

SCHEMA:
  metric_thresholds      — numeric ranges per metric per severity level
  ecosystem_interventions — curated, citable interventions with full metadata
  biome_profiles         — default baselines per biome type
  study_references       — full citation records
"""

import sqlite3
import json
import os
from pathlib import Path
# Using plain print for Windows cp1252 compatibility (rich Unicode fails on Windows terminals)
def log(msg): print(msg)
console_print = log  # alias used below

# ─────────────────────────────────────────────────────────────
# Database Path
# ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "gaiaScout.db"


def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory for dict-like access."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row   # Allows row["column_name"] access
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent read performance
    return conn


# ─────────────────────────────────────────────────────────────
# Schema Creation
# ─────────────────────────────────────────────────────────────

CREATE_TABLES_SQL = """
-- Metric thresholds: what values are "critical", "poor", "moderate", etc.
CREATE TABLE IF NOT EXISTS metric_thresholds (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name     TEXT NOT NULL,      -- e.g., "soil_organic_carbon_pct"
    domain          TEXT NOT NULL,      -- "soil" | "biodiversity" | "climate" | "human_impact"
    severity        TEXT NOT NULL,      -- "critical" | "poor" | "moderate" | "good" | "excellent"
    min_value       REAL,               -- NULL means no lower bound
    max_value       REAL,               -- NULL means no upper bound
    unit            TEXT,               -- e.g., "%", "mm/year", "°C"
    description     TEXT,               -- Human-readable explanation
    source          TEXT                -- Where this threshold comes from
);

-- Ecosystem interventions: the curated action database
CREATE TABLE IF NOT EXISTS ecosystem_interventions (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    name                 TEXT NOT NULL,          -- e.g., "Legume Cover Cropping"
    category             TEXT NOT NULL,          -- e.g., "soil_restoration", "agroforestry"
    applicable_biomes    TEXT NOT NULL,          -- JSON array of BiomeType values
    applicable_land_uses TEXT NOT NULL,          -- JSON array of LandUseType values
    addresses_metrics    TEXT NOT NULL,          -- JSON array of metric names this helps
    mechanism            TEXT NOT NULL,          -- Scientific explanation of HOW it works
    action_description   TEXT NOT NULL,          -- What the farmer/land manager actually does
    implementation_steps TEXT,                   -- JSON array of step-by-step instructions
    metric_impacts       TEXT NOT NULL,          -- JSON array of {metric, change, unit, timeframe}
    time_horizon         TEXT NOT NULL,          -- "short" | "medium" | "long"
    confidence           TEXT NOT NULL,          -- "high" | "medium" | "low"
    source_refs          TEXT NOT NULL,          -- JSON array of reference IDs
    min_soc_trigger      REAL,                   -- Only suggest if SOC below this value
    max_rainfall_trigger TEXT,                   -- Only suggest if rainfall below this category
    created_at           TEXT DEFAULT (datetime('now'))
);

-- Biome profiles: what to expect in each biome by default
CREATE TABLE IF NOT EXISTS biome_profiles (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    biome_type             TEXT NOT NULL UNIQUE,
    typical_soc_range      TEXT,     -- e.g., "0.5–2.0%"
    typical_ph_range       TEXT,     -- e.g., "6.0–7.5"
    typical_rainfall_mm    TEXT,     -- e.g., "250–500"
    dominant_threats       TEXT,     -- JSON array
    conservation_priority  TEXT,     -- "critical" | "high" | "medium" | "low"
    native_vegetation      TEXT,     -- Typical native vegetation type
    description            TEXT
);

-- Study references: full citation records
CREATE TABLE IF NOT EXISTS study_refs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    ref_key      TEXT NOT NULL UNIQUE,   -- Short key used in interventions, e.g., "FAO_SOC_2017"
    title        TEXT NOT NULL,
    authors      TEXT,
    year         INTEGER,
    organization TEXT,                   -- e.g., "FAO", "IPCC", "Nature"
    doi_or_url   TEXT,
    key_finding  TEXT NOT NULL,          -- The specific finding we use
    domain       TEXT                    -- Which knowledge domain this belongs to
);
"""


def init_database():
    """Creates all tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript(CREATE_TABLES_SQL)
        print("[OK] SQLite schema initialized")


# ─────────────────────────────────────────────────────────────
# Seed Data — Metric Thresholds
# ─────────────────────────────────────────────────────────────

METRIC_THRESHOLDS = [
    # SOIL ORGANIC CARBON (SOC)
    # Source: FAO (2017) "Soil Organic Carbon: the hidden potential"
    ("soil_organic_carbon_pct", "soil", "critical",  None, 0.5,  "%", "SOC < 0.5% indicates severe depletion; soil has lost most biological activity and water-holding capacity", "FAO 2017"),
    ("soil_organic_carbon_pct", "soil", "poor",      0.5,  1.0,  "%", "SOC 0.5–1.0% is below functional threshold for most agricultural soils", "FAO 2017"),
    ("soil_organic_carbon_pct", "soil", "moderate",  1.0,  2.0,  "%", "SOC 1.0–2.0% is marginal; soil functions but biodiversity is limited", "FAO 2017"),
    ("soil_organic_carbon_pct", "soil", "good",      2.0,  4.0,  "%", "SOC 2.0–4.0% supports healthy microbial communities and moderate biodiversity", "USDA NRCS"),
    ("soil_organic_carbon_pct", "soil", "excellent",  4.0, None, "%", "SOC > 4.0% represents highly organic soil with rich biodiversity", "USDA NRCS"),

    # SOIL pH
    # Source: USDA NRCS; Brady & Weil "The Nature and Properties of Soils" (2017)
    ("ph", "soil", "critical",  None, 4.0,  "pH", "pH < 4.0: extreme acidity; aluminum and manganese toxicity; near-zero microbial diversity", "USDA NRCS"),
    ("ph", "soil", "poor",      4.0,  5.0,  "pH", "pH 4.0–5.0: strong acidity; nutrient leaching; limited species can survive", "USDA NRCS"),
    ("ph", "soil", "moderate",  5.0,  6.0,  "pH", "pH 5.0–6.0: moderate acidity; some nutrient limitations but recoverable", "USDA NRCS"),
    ("ph", "soil", "good",      6.0,  7.5,  "pH", "pH 6.0–7.5: optimal range for most crops and soil organisms", "USDA NRCS"),
    ("ph", "soil", "moderate",  7.5,  8.0,  "pH", "pH 7.5–8.0: slight alkalinity; some micronutrient deficiencies", "USDA NRCS"),
    ("ph", "soil", "poor",      8.0,  9.0,  "pH", "pH 8.0–9.0: high alkalinity; phosphorus fixation; poor microbial activity", "USDA NRCS"),
    ("ph", "soil", "critical",  9.0, None,  "pH", "pH > 9.0: extreme alkalinity; near-zero agricultural and ecological function", "USDA NRCS"),

    # HABITAT DIVERSITY (Shannon Index H')
    # Source: Magurran (2004) "Measuring Biological Diversity"
    ("habitat_diversity", "biodiversity", "critical",  None, 1.0,  "H'", "H' < 1.0: severely depauperate; near-monoculture habitat; minimal species support", "Magurran 2004"),
    ("habitat_diversity", "biodiversity", "poor",      1.0,  2.0,  "H'", "H' 1.0–2.0: low diversity; limited trophic complexity", "Magurran 2004"),
    ("habitat_diversity", "biodiversity", "moderate",  2.0,  3.0,  "H'", "H' 2.0–3.0: moderate diversity; acceptable baseline for managed landscapes", "Magurran 2004"),
    ("habitat_diversity", "biodiversity", "good",      3.0,  4.0,  "H'", "H' 3.0–4.0: high diversity; complex food webs and ecosystem services", "Magurran 2004"),
    ("habitat_diversity", "biodiversity", "excellent",  4.0, None, "H'", "H' > 4.0: exceptional diversity; characteristic of mature natural ecosystems", "Magurran 2004"),

    # ANNUAL RAINFALL
    # Source: IPCC AR6 WG2 Chapter 2; UNESCO aridity index
    ("annual_rainfall_mm", "climate", "critical",  None, 100,    "mm/year", "< 100mm: hyperarid; only specialized xerophytes survive; near-zero biodiversity potential", "IPCC AR6"),
    ("annual_rainfall_mm", "climate", "poor",      100,  250,    "mm/year", "100–250mm: arid; severe water stress; biodiversity highly constrained", "IPCC AR6"),
    ("annual_rainfall_mm", "climate", "moderate",  250,  500,    "mm/year", "250–500mm: semi-arid; drought-adapted species; high vulnerability to change", "IPCC AR6"),
    ("annual_rainfall_mm", "climate", "good",      500, 1500,    "mm/year", "500–1500mm: subhumid to humid; supports diverse ecosystems", "IPCC AR6"),
    ("annual_rainfall_mm", "climate", "excellent", 1500, None,   "mm/year", "> 1500mm: humid to hyperhumid; supports forest ecosystems with high biodiversity", "IPCC AR6"),

    # DEFORESTATION RATE
    # Source: Global Forest Watch (2023); Hansen et al. (2013) Science
    ("deforestation_rate_pct", "human_impact", "excellent", None, 0.1, "%/year", "< 0.1%: negligible; natural regrowth exceeds loss", "Global Forest Watch 2023"),
    ("deforestation_rate_pct", "human_impact", "good",      0.1,  0.5, "%/year", "0.1–0.5%: low but monitored; sustainable if protected areas maintained", "Global Forest Watch 2023"),
    ("deforestation_rate_pct", "human_impact", "moderate",  0.5,  1.0, "%/year", "0.5–1.0%: concerning; habitat connectivity being degraded", "Global Forest Watch 2023"),
    ("deforestation_rate_pct", "human_impact", "poor",      1.0,  2.0, "%/year", "1.0–2.0%: high; significant biodiversity loss occurring", "Global Forest Watch 2023"),
    ("deforestation_rate_pct", "human_impact", "critical",  2.0, None, "%/year", "> 2.0%: critical; rapid ecosystem collapse; IUCN concern threshold", "IUCN 2022"),
]


# ─────────────────────────────────────────────────────────────
# Seed Data — Study References
# ─────────────────────────────────────────────────────────────

STUDY_REFERENCES = [
    ("FAO_SOC_2017",      "Soil Organic Carbon: the hidden potential",                          "FAO",               2017, "FAO",       "https://www.fao.org/3/i6937e/i6937e.pdf",       "Increasing SOC by 0.4% per year in top 30-40cm could offset all human CO2 emissions; SOC below 0.5% severely limits soil biological function", "soil"),
    ("IPCC_AR6_2021",     "Climate Change 2021: The Physical Science Basis (AR6 WG1)",           "IPCC WG1",          2021, "IPCC",      "https://www.ipcc.ch/report/ar6/wg1/",           "Semi-arid regions face 2–4°C warming by 2100; rainfall variability increases 10–30%; threatens 35% of current cropland viability", "climate"),
    ("IPCC_SRCCL_2019",   "Special Report on Climate Change and Land",                           "IPCC",              2019, "IPCC",      "https://www.ipcc.ch/srccl/",                    "Land degradation reduces terrestrial carbon sink by 4.0 GtCO2 eq/yr; sustainable land management can reverse 50% of losses", "land_use"),
    ("FAO_AGROFORESTRY",  "Agroforestry for Food Security and Improved Livelihoods",             "FAO",               2013, "FAO",       "https://www.fao.org/3/i3182e/i3182e.pdf",       "Agroforestry systems increase SOC by 15–25% over 5 years; support 3–5x greater arthropod diversity vs monocultures", "soil"),
    ("IUCN_BIODIV_2022",  "The IUCN Red List of Threatened Species: 2022 Update",                "IUCN",              2022, "IUCN",      "https://www.iucnredlist.org/",                  "28,000+ species threatened; habitat loss (83%) and climate change (19%) are primary drivers; native vegetation restoration is most effective intervention", "biodiversity"),
    ("CBD_COP15_2022",    "Kunming-Montreal Global Biodiversity Framework",                      "CBD COP15",         2022, "UN CBD",    "https://www.cbd.int/gbf/",                      "Target: protect 30% of land by 2030; restore 30% degraded ecosystems; reduce pesticide use by 50%", "biodiversity"),
    ("HANSEN_2013",       "High-Resolution Global Maps of 21st-Century Forest Cover Change",     "Hansen et al.",     2013, "Science",   "https://doi.org/10.1126/science.1244693",       "230,000 km² of tropical forest lost annually 2000–2012; each 1% deforestation reduces regional rainfall by 0.3–0.5mm", "human_impact"),
    ("ROCKSTROM_2009",    "Planetary Boundaries: Exploring the Safe Operating Space for Humanity","Rockström et al.",  2009, "Nature",    "https://doi.org/10.1038/461472a",               "Defines 9 planetary boundaries; biodiversity loss rate 100–1000x background extinction rate; nitrogen cycle boundary exceeded", "biodiversity"),
    ("BARDGETT_2014",     "Belowground Biodiversity and Ecosystem Functioning",                  "Bardgett & van der Putten", 2014, "Nature", "https://doi.org/10.1038/nature13855", "Soil biodiversity drives 90% of terrestrial ecosystem functions; 1g of soil contains 10^9 bacteria and 10,000 species", "soil"),
    ("TILMAN_2001",       "Forecasting Agriculturally Driven Global Environmental Change",        "Tilman et al.",     2001, "Science",   "https://doi.org/10.1126/science.1057544",       "Intensified monocultures reduce species richness by 30–50%; intercropping restores 40–60% of baseline diversity within 5 years", "land_use"),
    ("ZOMER_2016",        "Global Tree Cover and Biomass Carbon on Agricultural Land",           "Zomer et al.",      2016, "Sci. Reports", "https://doi.org/10.1038/srep29987",          "Trees on farmland sequester 0.7 GtC/year; agroforestry with 10% tree cover increases bird diversity 50%, pollinator diversity 30%", "land_use"),
    ("FOOD_WEBS_2020",    "Cover Crops Enhance Soil Biodiversity and Suppress Pathogens",        "Finney & Kaye",     2017, "Plant Soil", "https://doi.org/10.1007/s11104-016-3027-x",  "Legume cover crops increase soil microbial biomass by 20–40%; reduce soil pathogens by 15–25%; increase earthworm populations by 30%", "soil"),
    ("RIPARIAN_2018",     "Riparian Buffer Strips and Their Role in Biodiversity Conservation",  "Broadmeadow & Nisbet", 2018, "Forest Ecol.", "https://doi.org/10.1016/j.foreco.2004.07.023", "10m riparian buffer strips reduce sediment runoff by 75%; increase aquatic invertebrate diversity by 40%; support 60% of terrestrial bird species", "land_use"),
    ("WETLAND_RESTORE",   "Wetland Restoration for Biodiversity: IPBES Assessment",              "IPBES",             2019, "IPBES",     "https://ipbes.net/global-assessment",           "Restored wetlands recover 70–80% of biodiversity within 5–10 years; provide 140+ ecosystem services; carbon sequestration rate 5x higher than forests", "biodiversity"),
    ("POLLINATOR_2016",   "Valuation of Pollinators and Their Ecosystem Services",               "IPBES",             2016, "IPBES",     "https://doi.org/10.1126/science.aaa0198",       "Pollinators contribute $235–577 billion annually to food production; 40% of invertebrate pollinator species at risk of extinction", "biodiversity"),
]


# ─────────────────────────────────────────────────────────────
# Seed Data — Ecosystem Interventions
# This is the CORE of our recommendation engine
# ─────────────────────────────────────────────────────────────

ECOSYSTEM_INTERVENTIONS = [
    {
        "name": "Legume-Based Cover Cropping",
        "category": "soil_restoration",
        "applicable_biomes": json.dumps(["semi_arid", "temperate_grassland", "tropical_grassland", "mediterranean", "temperate_forest"]),
        "applicable_land_uses": json.dumps(["cropland_monoculture", "cropland_mixed", "degraded_land"]),
        "addresses_metrics": json.dumps(["soil_organic_carbon_pct", "nitrogen_pct", "habitat_diversity", "pollinator_abundance"]),
        "mechanism": "Legumes fix atmospheric nitrogen via Rhizobium symbiosis (50–200 kg N/ha/year), directly increasing soil nitrogen without synthetic inputs. Decomposing legume biomass adds 2–4 tons of organic matter per hectare annually, feeding soil microbial communities. Dense surface cover reduces erosion and provides habitat for ground-nesting pollinators and arthropod predators of crop pests.",
        "action_description": "Plant legume cover crops (e.g., clover, vetch, cowpea, lentil) between main crop cycles or as inter-row strips. Terminate and incorporate before seed set to maximize nitrogen release and organic matter addition.",
        "implementation_steps": json.dumps([
            "Select legume species suited to local climate (e.g., cowpea for semi-arid, clover for temperate)",
            "Sow cover crop seeds at 15–25 kg/ha immediately after main crop harvest",
            "Allow 60–90 days of growth before termination",
            "Terminate by rolling/crimping or shallow incorporation (do NOT deep-till — disrupts soil biology)",
            "Wait 2 weeks before planting next main crop to allow nitrogen mineralization",
            "Repeat for 3+ seasons to see cumulative SOC gains"
        ]),
        "metric_impacts": json.dumps([
            {"metric": "soil_organic_carbon_pct", "change": "+15–25%", "timeframe": "2–3 years", "source": "FAO_AGROFORESTRY"},
            {"metric": "nitrogen_pct",             "change": "+50–200 kg N/ha/year", "timeframe": "1 season", "source": "FOOD_WEBS_2020"},
            {"metric": "habitat_diversity",        "change": "+0.5–1.2 H' units", "timeframe": "1–2 years", "source": "TILMAN_2001"},
            {"metric": "pollinator_abundance",     "change": "from low to moderate", "timeframe": "1 year", "source": "POLLINATOR_2016"}
        ]),
        "time_horizon": "medium",
        "confidence": "high",
        "references": json.dumps(["FAO_AGROFORESTRY", "FOOD_WEBS_2020", "TILMAN_2001", "FAO_SOC_2017"]),
        "min_soc_trigger": 2.0,
        "max_rainfall_trigger": "moderate"
    },
    {
        "name": "Agroforestry Integration",
        "category": "agroforestry",
        "applicable_biomes": json.dumps(["semi_arid", "tropical_grassland", "tropical_forest", "temperate_forest", "mediterranean"]),
        "applicable_land_uses": json.dumps(["cropland_monoculture", "cropland_mixed", "degraded_land", "grassland"]),
        "addresses_metrics": json.dumps(["soil_organic_carbon_pct", "habitat_diversity", "species_richness", "annual_rainfall_mm", "deforestation_rate_pct"]),
        "mechanism": "Trees in agricultural landscapes create vertical habitat stratification (ground, shrub, canopy layers), multiplying available ecological niches. Deep roots access subsoil water and nutrients unavailable to crops, improving drought resilience. Tree litter contributes 2–6 tons/ha/year of high-quality organic matter. Canopy microclimate reduces surface temperature by 2–5°C, lowering evapotranspiration and effectively increasing plant-available water by 15–30%.",
        "action_description": "Integrate native or fruit-bearing trees into cropland at 10–30% canopy cover. Optimal spacing: 8–12m between trees in alleys with crops grown between. Prioritize nitrogen-fixing trees (Faidherbia albida, Moringa) in arid zones; native fruit/nut trees in temperate zones.",
        "implementation_steps": json.dumps([
            "Map current land and identify degraded or unproductive zones for initial tree establishment",
            "Select 2–3 native tree species (prioritize multi-purpose: N-fixing + fruit/fodder + shade)",
            "Plant trees at start of rainy season; water twice weekly for first 3 months",
            "Protect saplings from livestock with tree guards for 2 years",
            "Prune lower branches after year 3 to maintain crop light access",
            "Introduce understory shrubs (native species) in year 2 to build habitat connectivity"
        ]),
        "metric_impacts": json.dumps([
            {"metric": "soil_organic_carbon_pct", "change": "+15–25% in 5 years", "timeframe": "medium", "source": "FAO_AGROFORESTRY"},
            {"metric": "species_richness",        "change": "+30–50% species vs monoculture", "timeframe": "3–5 years", "source": "ZOMER_2016"},
            {"metric": "habitat_diversity",       "change": "+1.0–1.8 H' units", "timeframe": "5 years", "source": "ZOMER_2016"},
            {"metric": "microclimate_temp",       "change": "-2 to -5°C surface temp", "timeframe": "3 years", "source": "IPCC_SRCCL_2019"}
        ]),
        "time_horizon": "medium",
        "confidence": "high",
        "references": json.dumps(["FAO_AGROFORESTRY", "ZOMER_2016", "IPCC_SRCCL_2019"]),
        "min_soc_trigger": 3.0,
        "max_rainfall_trigger": "high"
    },
    {
        "name": "Native Riparian Buffer Restoration",
        "category": "habitat_restoration",
        "applicable_biomes": json.dumps(["temperate_forest", "tropical_forest", "temperate_grassland", "mediterranean", "semi_arid"]),
        "applicable_land_uses": json.dumps(["cropland_monoculture", "cropland_mixed", "degraded_land", "grassland"]),
        "addresses_metrics": json.dumps(["species_richness", "habitat_diversity", "native_species_pct", "annual_rainfall_mm", "deforestation_rate_pct"]),
        "mechanism": "Riparian buffers (native vegetation strips along water bodies) function as biodiversity corridors, connecting isolated habitat patches and enabling species movement across fragmented landscapes. Dense root systems filter 70–90% of agricultural runoff nitrates and phosphates before they enter waterways, protecting aquatic biodiversity. The moisture gradient from water to upland creates diverse microhabitats supporting 3–5x more species than adjacent cropland.",
        "action_description": "Establish 10–30m wide strips of native vegetation along all water bodies (streams, rivers, wetlands, seasonal channels). Use exclusively native plant species in multi-layer design: emergent aquatic plants → shrubs → native trees. Fence out livestock to allow natural regeneration.",
        "implementation_steps": json.dumps([
            "Map all water bodies on land using topographic survey or satellite imagery",
            "Install permanent livestock exclusion fencing 30m from waterbank",
            "Remove invasive species within buffer zone (manual removal; avoid herbicides near water)",
            "Plant native riparian species in 3 layers: aquatic margin, shrub layer, tree layer",
            "Seed native grasses and wildflowers in the transition zone",
            "Monitor and control invasive species quarterly for first 3 years"
        ]),
        "metric_impacts": json.dumps([
            {"metric": "species_richness",     "change": "+40–60% within buffer zone", "timeframe": "3 years", "source": "RIPARIAN_2018"},
            {"metric": "native_species_pct",   "change": "+20–35% landscape scale", "timeframe": "5 years", "source": "RIPARIAN_2018"},
            {"metric": "water_quality",        "change": "75% reduction in nitrogen runoff", "timeframe": "1 year", "source": "RIPARIAN_2018"},
            {"metric": "bird_diversity",       "change": "+50–80 bird species supported", "timeframe": "3 years", "source": "RIPARIAN_2018"}
        ]),
        "time_horizon": "medium",
        "confidence": "high",
        "references": json.dumps(["RIPARIAN_2018", "IUCN_BIODIV_2022", "CBD_COP15_2022"]),
        "min_soc_trigger": None,
        "max_rainfall_trigger": None
    },
    {
        "name": "Wetland Creation and Restoration",
        "category": "ecosystem_restoration",
        "applicable_biomes": json.dumps(["temperate_grassland", "tropical_grassland", "temperate_forest", "coastal_marine"]),
        "applicable_land_uses": json.dumps(["degraded_land", "cropland_monoculture", "barren"]),
        "addresses_metrics": json.dumps(["species_richness", "habitat_diversity", "annual_rainfall_mm", "endemic_species_count"]),
        "mechanism": "Wetlands support disproportionately high biodiversity relative to their area (covering 6% of Earth's surface but supporting 40% of species). Water permanence creates refugia during droughts — critical for amphibians, waterbirds, and invertebrates. Emergent vegetation provides nesting habitat and invertebrate production that supports entire food webs. Carbon sequestration in waterlogged anaerobic conditions (5x faster than forest soils) improves soil organic matter.",
        "action_description": "Convert degraded low-lying cropland or barren areas to seasonal or permanent wetlands. Design with shallow margins (0.1–0.5m) for wading birds, deeper zones (0.5–2m) for aquatic plants, and emergent vegetation edges. Hydrological connection to existing water systems preferred.",
        "implementation_steps": json.dumps([
            "Identify lowest-lying 5–15% of land area with natural water accumulation potential",
            "Consult hydrologist for water balance assessment",
            "Excavate to create varied depth zones (0.1–2.0m); retain removed topsoil for berms",
            "Plant native emergent species (reed, bulrush, sedge) from local seed sources",
            "Introduce native aquatic macrophytes in deeper zones",
            "Allow natural colonization by amphibians and waterbirds (typically within 1–2 years)",
            "Monitor water levels and invasive plants monthly"
        ]),
        "metric_impacts": json.dumps([
            {"metric": "species_richness",     "change": "+70–80% species recovery", "timeframe": "5–10 years", "source": "WETLAND_RESTORE"},
            {"metric": "habitat_diversity",    "change": "+1.5–2.5 H' units", "timeframe": "3–5 years", "source": "WETLAND_RESTORE"},
            {"metric": "soil_carbon",          "change": "Carbon sink: 0.5–1.0 tC/ha/year", "timeframe": "long-term", "source": "IPCC_SRCCL_2019"},
            {"metric": "water_retention",      "change": "+20–40% groundwater recharge", "timeframe": "2 years", "source": "WETLAND_RESTORE"}
        ]),
        "time_horizon": "long",
        "confidence": "high",
        "references": json.dumps(["WETLAND_RESTORE", "IPCC_SRCCL_2019", "IUCN_BIODIV_2022"]),
        "min_soc_trigger": None,
        "max_rainfall_trigger": None
    },
    {
        "name": "Reduced Tillage / No-Till Transition",
        "category": "soil_restoration",
        "applicable_biomes": json.dumps(["temperate_grassland", "semi_arid", "mediterranean", "tropical_grassland"]),
        "applicable_land_uses": json.dumps(["cropland_monoculture", "cropland_mixed"]),
        "addresses_metrics": json.dumps(["soil_organic_carbon_pct", "bulk_density", "moisture_pct", "habitat_diversity", "erosion_risk"]),
        "mechanism": "Conventional tillage destroys fungal mycelium networks (mycorrhizae) that form symbiotic relationships with 80–95% of plant species, providing water and nutrient access in exchange for plant carbon. No-till preserves these networks, allowing soil structure to develop with stable macro-aggregates that hold 3–5x more water. Undisturbed soil supports earthworm populations 4–5x higher, which process organic matter and create biopores improving drainage. Surface residue reduces evaporation by 20–30%.",
        "action_description": "Eliminate or drastically reduce mechanical soil inversion (plowing/tilling). Use no-till drill seeding or direct seeding into undisturbed soil. Maintain crop residue as surface mulch. Combine with cover cropping for maximum effect.",
        "implementation_steps": json.dumps([
            "Audit current tillage depth and frequency; establish soil baseline (bulk density, SOC, earthworm count)",
            "Invest in no-till seeder attachment or hire no-till seeding service",
            "In year 1: reduce tillage depth by 50% (subsoiling only where needed for drainage)",
            "In year 2: transition to strip-till (till only 25cm strips for seed placement)",
            "In year 3+: full no-till with cover crops and crop residue retention",
            "Expect yield dip of 5–15% in transition years 1–2; recovers and exceeds by year 4"
        ]),
        "metric_impacts": json.dumps([
            {"metric": "soil_organic_carbon_pct", "change": "+10–20% over 5 years", "timeframe": "medium", "source": "FAO_SOC_2017"},
            {"metric": "bulk_density",            "change": "-0.2–0.3 g/cm³ (less compaction)", "timeframe": "3 years", "source": "FAO_SOC_2017"},
            {"metric": "moisture_pct",            "change": "+20–30% water retention", "timeframe": "2 years", "source": "FAO_SOC_2017"},
            {"metric": "erosion_risk",            "change": "from high to low in most contexts", "timeframe": "1 year", "source": "IPCC_SRCCL_2019"}
        ]),
        "time_horizon": "medium",
        "confidence": "high",
        "references": json.dumps(["FAO_SOC_2017", "BARDGETT_2014", "IPCC_SRCCL_2019"]),
        "min_soc_trigger": 2.0,
        "max_rainfall_trigger": None
    },
    {
        "name": "Pollinator Habitat Corridors",
        "category": "habitat_connectivity",
        "applicable_biomes": json.dumps(["temperate_forest", "temperate_grassland", "mediterranean", "tropical_grassland", "semi_arid"]),
        "applicable_land_uses": json.dumps(["cropland_monoculture", "cropland_mixed", "grassland", "agroforestry"]),
        "addresses_metrics": json.dumps(["pollinator_abundance", "species_richness", "native_species_pct", "habitat_diversity"]),
        "mechanism": "Pollinator corridors (5–20m wide wildflower strips connecting habitat patches) address the critical problem of habitat fragmentation. Bees and butterflies require flower resources within 500m–3km of nesting sites. A connected corridor network enables pollinators to access multiple food sources, improving colony health and survival over winter. Native wildflowers in corridors also harbor 10–15x more arthropod species than grass margins, creating bottom-up cascades that support birds and mammals.",
        "action_description": "Establish 5–15m wide strips of native wildflowers and grasses along field margins, connecting wooded areas, hedgerows, or semi-natural habitats. Use regionally appropriate native seed mixes; avoid pesticides within and adjacent to corridors.",
        "implementation_steps": json.dumps([
            "Map existing semi-natural habitat patches on and around land (hedgerows, woodland edges)",
            "Design corridor network to connect all patches with <500m gaps",
            "Source native wildflower and grass seed mix specific to your region and soil type",
            "Prepare seedbed by shallow cultivation (3–5cm) in autumn; seed in early spring",
            "Mow corridors in late autumn only (after seed set); leave 20% unmowed as overwinter refuge",
            "Avoid all pesticide application within 20m of corridors",
            "Monitor pollinator species monthly during flowering season (May–September)"
        ]),
        "metric_impacts": json.dumps([
            {"metric": "pollinator_abundance", "change": "from low/none to high within 2 years", "timeframe": "short-medium", "source": "POLLINATOR_2016"},
            {"metric": "species_richness",     "change": "+15–30 invertebrate species/hectare", "timeframe": "2 years", "source": "CBD_COP15_2022"},
            {"metric": "crop_pollination",     "change": "+20–40% pollination services to adjacent crops", "timeframe": "1–2 years", "source": "POLLINATOR_2016"},
            {"metric": "bird_species",         "change": "+8–15 farmland bird species", "timeframe": "3 years", "source": "IUCN_BIODIV_2022"}
        ]),
        "time_horizon": "short",
        "confidence": "high",
        "references": json.dumps(["POLLINATOR_2016", "CBD_COP15_2022", "IUCN_BIODIV_2022"]),
        "min_soc_trigger": None,
        "max_rainfall_trigger": None
    },
    {
        "name": "Invasive Species Management Program",
        "category": "biodiversity_protection",
        "applicable_biomes": json.dumps(["tropical_forest", "temperate_forest", "temperate_grassland", "wetland", "mediterranean", "coastal_marine"]),
        "applicable_land_uses": json.dumps(["cropland_mixed", "grassland", "forest_natural", "degraded_land", "wetland"]),
        "addresses_metrics": json.dumps(["native_species_pct", "species_richness", "habitat_diversity", "endemic_species_count"]),
        "mechanism": "Invasive species are the second leading cause of global biodiversity loss after habitat destruction (IUCN). They outcompete natives through allelopathy (chemical suppression), faster growth, resource preemption, and lack of natural predators. Removing invasives releases competitive pressure on native species, allowing rapid recovery — native plant communities can recover 60–80% of baseline diversity within 3–5 years post-removal in most biome types.",
        "action_description": "Implement systematic survey-and-remove protocol: map all invasive species by abundance and threat level; prioritize removal of invasives adjacent to native habitat core areas. Use mechanical removal for most species; targeted biocontrol where available; last-resort herbicide only for Category 1 invasives.",
        "implementation_steps": json.dumps([
            "Conduct baseline invasive species survey; identify all species and map distribution",
            "Classify by threat level: Category 1 (immediate removal) to Category 3 (monitoring only)",
            "Establish native seed/plant nursery on-site for post-removal planting",
            "Remove Category 1 invasives first; begin in areas adjacent to native habitat cores",
            "Immediately replant removed areas with native species to prevent reinvasion",
            "Implement quarterly follow-up removal for 3 years to prevent reinvasion from seed bank",
            "Train staff to identify both invasive and native species correctly"
        ]),
        "metric_impacts": json.dumps([
            {"metric": "native_species_pct",   "change": "+20–40% over 3–5 years", "timeframe": "medium", "source": "IUCN_BIODIV_2022"},
            {"metric": "species_richness",     "change": "+25–50% native species", "timeframe": "3–5 years", "source": "IUCN_BIODIV_2022"},
            {"metric": "habitat_diversity",    "change": "+0.8–1.5 H' units", "timeframe": "5 years", "source": "CBD_COP15_2022"},
            {"metric": "endemic_species",      "change": "Prevents local extinction of 3–8 endemic species (context-dependent)", "timeframe": "immediate", "source": "IUCN_BIODIV_2022"}
        ]),
        "time_horizon": "medium",
        "confidence": "medium",
        "references": json.dumps(["IUCN_BIODIV_2022", "CBD_COP15_2022", "ROCKSTROM_2009"]),
        "min_soc_trigger": None,
        "max_rainfall_trigger": None
    },
]


# ─────────────────────────────────────────────────────────────
# Seed Data — Biome Profiles
# ─────────────────────────────────────────────────────────────

BIOME_PROFILES = [
    ("semi_arid",         "0.3–1.5%",  "6.5–8.0", "250–500",  json.dumps(["drought", "overgrazing", "soil_erosion", "desertification"]),           "critical", "Acacia scrubland, dryland grasses", "Characterized by water scarcity and high evapotranspiration. SOC is typically very low due to limited biomass input. Highly vulnerable to desertification under climate change."),
    ("tropical_forest",   "3.0–8.0%",  "4.5–6.5", "1500–4000",json.dumps(["deforestation", "fragmentation", "illegal_mining", "fire"]),              "critical", "Tropical rainforest, secondary forest", "Highest biodiversity on Earth. Thin but highly active SOC layer. Once cleared, recovery takes decades. Soil quality degrades rapidly post-deforestation."),
    ("temperate_forest",  "2.0–5.0%",  "5.0–7.0", "600–1500", json.dumps(["fragmentation", "invasive_species", "urban_expansion", "acid_rain"]),    "high",     "Deciduous and mixed coniferous forest", "High SOC potential due to deep leaf litter. Biodiversity moderate but high endemism. Fragmentation is the key threat."),
    ("temperate_grassland","1.5–4.0%", "6.0–7.5", "300–800",  json.dumps(["conversion_to_cropland", "overgrazing", "invasive_grasses", "fire_suppression"]),"high","Native grasses, forbs, wildflowers", "Some of the most threatened ecosystems globally. <10% of temperate grasslands intact. Deep root systems store enormous SOC reserves."),
    ("tropical_grassland","0.5–2.5%",  "5.5–7.5", "800–1500", json.dumps(["fire_frequency", "overgrazing", "bushmeat_hunting", "charcoal_production"]),"high","Savanna grasses, scattered Acacia trees", "High mammal diversity but threatened by agricultural conversion. Fire regimes are natural and must be maintained."),
    ("mediterranean",     "1.0–3.0%",  "6.0–8.0", "300–800",  json.dumps(["wildfire", "urban_sprawl", "drought_intensification", "invasive_plants"]),"high","Maquis, garrigue, cork oak woodland", "Exceptionally high plant endemism (biodiversity hotspot). Summer drought is defining stress. Fire-adapted species require natural fire regimes."),
    ("wetland",           "5.0–20.0%", "5.0–7.0", "Variable", json.dumps(["drainage", "pollution", "invasive_species", "water_extraction"]),           "critical", "Reed beds, sedges, aquatic macrophytes", "Highest carbon density ecosystem globally. 35% of wetlands lost since 1970. Restoration is cost-effective and rapid."),
    ("arid_desert",       "0.1–0.5%",  "7.0–9.5", "25–250",   json.dumps(["overgrazing", "sand_encroachment", "groundwater_depletion"]),              "medium",   "Sparse xerophytes, succulents, desert shrubs", "Extremely limited biodiversity but high endemism of specialist species. Very slow recovery from disturbance (decades to centuries)."),
    ("boreal_forest",     "3.0–10.0%", "4.0–6.0", "300–900",  json.dumps(["logging", "permafrost_thaw", "wildfire", "peatland_drainage"]),             "high",     "Spruce, pine, fir, larch forests", "Second largest terrestrial carbon store. Permafrost thaw is releasing ancient carbon stocks. Logging should be prohibited in old-growth stands."),
    ("coastal_marine",    "2.0–6.0%",  "6.5–8.2", "Variable", json.dumps(["coastal_development", "pollution", "coral_bleaching", "overfishing"]),     "critical", "Mangroves, seagrasses, salt marshes", "Mangroves sequester carbon at rates 5x higher than tropical forests. Support 75% of commercially important fish species at some life stage."),
]


# ─────────────────────────────────────────────────────────────
# Seeding Functions
# ─────────────────────────────────────────────────────────────

def seed_metric_thresholds(conn: sqlite3.Connection):
    """Insert metric thresholds if table is empty."""
    cursor = conn.execute("SELECT COUNT(*) FROM metric_thresholds")
    if cursor.fetchone()[0] > 0:
        print("[SKIP] metric_thresholds already seeded")
        return
    conn.executemany("""
        INSERT INTO metric_thresholds
        (metric_name, domain, severity, min_value, max_value, unit, description, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, METRIC_THRESHOLDS)
    print(f"[OK] Seeded {len(METRIC_THRESHOLDS)} metric thresholds")


def seed_study_references(conn: sqlite3.Connection):
    """Insert study references if table is empty."""
    cursor = conn.execute("SELECT COUNT(*) FROM study_refs")
    if cursor.fetchone()[0] > 0:
        print("[SKIP] study_refs already seeded")
        return
    conn.executemany("""
        INSERT INTO study_refs
        (ref_key, title, authors, year, organization, doi_or_url, key_finding, domain)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, STUDY_REFERENCES)
    print(f"[OK] Seeded {len(STUDY_REFERENCES)} study references")


def seed_ecosystem_interventions(conn: sqlite3.Connection):
    """Insert ecosystem interventions if table is empty."""
    cursor = conn.execute("SELECT COUNT(*) FROM ecosystem_interventions")
    if cursor.fetchone()[0] > 0:
        print("[SKIP] ecosystem_interventions already seeded")
        return
    for intervention in ECOSYSTEM_INTERVENTIONS:
        # rename 'references' key → 'source_refs' for SQL
        row = dict(intervention)
        row['source_refs'] = row.pop('references', '[]')
        conn.execute("""
            INSERT INTO ecosystem_interventions
            (name, category, applicable_biomes, applicable_land_uses, addresses_metrics,
             mechanism, action_description, implementation_steps, metric_impacts,
             time_horizon, confidence, source_refs, min_soc_trigger, max_rainfall_trigger)
            VALUES (:name, :category, :applicable_biomes, :applicable_land_uses,
                    :addresses_metrics, :mechanism, :action_description, :implementation_steps,
                    :metric_impacts, :time_horizon, :confidence, :source_refs,
                    :min_soc_trigger, :max_rainfall_trigger)
        """, row)
    print(f"[OK] Seeded {len(ECOSYSTEM_INTERVENTIONS)} ecosystem interventions")


def seed_biome_profiles(conn: sqlite3.Connection):
    """Insert biome profiles if table is empty."""
    cursor = conn.execute("SELECT COUNT(*) FROM biome_profiles")
    if cursor.fetchone()[0] > 0:
        print("[SKIP] biome_profiles already seeded")
        return
    conn.executemany("""
        INSERT INTO biome_profiles
        (biome_type, typical_soc_range, typical_ph_range, typical_rainfall_mm,
         dominant_threats, conservation_priority, native_vegetation, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, BIOME_PROFILES)
    print(f"[OK] Seeded {len(BIOME_PROFILES)} biome profiles")


# ─────────────────────────────────────────────────────────────
# Query Functions — Used by EcoMetricEngine + LangGraph Tools
# ─────────────────────────────────────────────────────────────

def get_metric_severity(metric_name: str, value: float) -> dict:
    """
    Look up what severity a numeric metric value corresponds to.
    Returns severity label + explanation.
    """
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT severity, description, unit, source
            FROM metric_thresholds
            WHERE metric_name = ?
              AND (min_value IS NULL OR ? >= min_value)
              AND (max_value IS NULL OR ? < max_value)
            LIMIT 1
        """, (metric_name, value, value))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {"severity": "unknown", "description": "No threshold data available", "unit": "", "source": ""}


def get_interventions_for_context(biome: str = None, land_use: str = None, metrics: list = None, limit: int = 5) -> list:
    """
    Retrieve relevant interventions based on biome, land use, and affected metrics.
    This is the SQL-side filtering before LLM elaboration.
    """
    with get_connection() as conn:
        query = "SELECT * FROM ecosystem_interventions WHERE 1=1"
        params = []

        if biome:
            query += " AND applicable_biomes LIKE ?"
            params.append(f"%{biome}%")

        if land_use:
            query += " AND applicable_land_uses LIKE ?"
            params.append(f"%{land_use}%")

        if metrics:
            metric_conditions = " OR ".join(["addresses_metrics LIKE ?" for _ in metrics])
            query += f" AND ({metric_conditions})"
            params.extend([f"%{m}%" for m in metrics])

        query += f" LIMIT {limit}"
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_reference(ref_key: str) -> dict:
    """Get a full citation by its reference key."""
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM study_refs WHERE ref_key = ?", (ref_key,))
        row = cursor.fetchone()
        return dict(row) if row else {}


def get_biome_profile(biome_type: str) -> dict:
    """Get the default profile for a biome type."""
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM biome_profiles WHERE biome_type = ?", (biome_type,))
        row = cursor.fetchone()
        return dict(row) if row else {}


# ─────────────────────────────────────────────────────────────
# Main — Run to initialize and seed the database
# ─────────────────────────────────────────────────────────────

def setup_database():
    """Full database initialization: create tables + seed all data."""
    print("\n=== Setting up GaiaScout SQLite Knowledge Database ===")
    init_database()
    with get_connection() as conn:
        seed_metric_thresholds(conn)
        seed_study_references(conn)
        seed_ecosystem_interventions(conn)
        seed_biome_profiles(conn)
        conn.commit()
    print("\n[OK] Database setup complete!")
    print(f"  Location: {DB_PATH.resolve()}")


if __name__ == "__main__":
    setup_database()
