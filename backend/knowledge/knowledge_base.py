"""
knowledge_base.py — Scientific Text Corpus for ChromaDB Ingestion

WHY THIS FILE EXISTS:
  ChromaDB needs TEXT to embed and search semantically.
  This file contains curated, chunked scientific knowledge written as
  dense, information-rich paragraphs — one idea per chunk.

  WHY NOT JUST USE PDFs?
    - PDFs require parsing (messy, slow, format-dependent)
    - Research papers have boilerplate (abstracts, references, author lists)
      that pollutes embeddings
    - We want DENSE, RELEVANT chunks — not 500-word sections of methodology

  EACH CHUNK IS:
    - ~150-300 words (optimal for sentence-transformer embedding quality)
    - Focused on ONE specific mechanism or finding
    - Tagged with metadata: domain, topic, source, year

  DOMAINS (5 ChromaDB collections):
    1. soil_healthh
    2. land_use
    3. biodiversity_indicators
    4. climate_factors
    5. human_impact
"""

from typing import List, Dict, Any

# ─────────────────────────────────────────────────────────────
# Type alias for a knowledge chunk
# ─────────────────────────────────────────────────────────────
KnowledgeChunk = Dict[str, Any]
# Fields: text, domain, topic, source, year, source_url


# ─────────────────────────────────────────────────────────────
# DOMAIN 1: SOIL HEALTH
# ─────────────────────────────────────────────────────────────

SOIL_HEALTH_CHUNKS: List[KnowledgeChunk] = [
    {
        "text": """Soil organic carbon (SOC) is the single most important indicator of soil health and biological productivity.
        The FAO (2017) defines soils with less than 0.5percent SOC as critically depleted, having lost most functional biological
        activity including microbial decomposition, nitrogen cycling, and water retention capacity. At 0.5-1.0percent SOC, soils
        are functionally impaired but can be restored. The global average agricultural SOC is 1.3percent, far below the 2.0-3.5percent
        range that supports high biodiversity and stable crop yields. Soils below 1percent SOC hold 40percent less plant-available water
        per unit volume compared to soils at 3percent SOC, directly linking carbon depletion to drought vulnerability.
        The French '4 per 1000' initiative demonstrated that increasing SOC by just 0.4percent per year globally could offset
        all annual human CO2 emissions, illustrating SOC's dual role in biodiversity and climate mitigation.""",
        "domain": "soil_health",
        "topic": "soil_organic_carbon",
        "source": "FAO Soil Organic Carbon Report",
        "year": 2017,
        "source_url": "https://www.fao.org/3/i6937e/i6937e.pdf"
    },
    {
        "text": """Soil microbial diversity is the hidden engine of terrestrial ecosystem function. Research by Bardgett and
        van der Putten (2014, Nature) established that one gram of healthy soil contains approximately one billion bacteria
        representing up to 10,000 species, and a single teaspoon of forest soil may contain several miles of fungal hyphae.
        This microbial community performs 90percent of all terrestrial ecosystem functions including decomposition, nitrogen
        fixation, phosphorus solubilization, disease suppression, and aggregation. When SOC falls below 1percent, microbial
        biomass declines by 60-80percent, triggering cascading failures across these functions. Mycorrhizal fungi — which form
        symbiotic associations with 80-95percent of all terrestrial plant species — are particularly sensitive to soil disturbance
        and low carbon, with populations declining 90percent under conventional tillage. Restoration of mycorrhizal networks
        requires minimum 3-5 years of no-till with organic matter addition.""",
        "domain": "soil_health",
        "topic": "soil_microbial_diversity",
        "source": "Bardgett & van der Putten, Nature",
        "year": 2014,
        "source_url": "https://doi.org/10.1038/nature13855"
    },
    {
        "text": """Soil pH is the master variable governing nutrient availability and microbial community composition.
        At pH below 5.0, aluminum and manganese become soluble and toxic, eliminating sensitive species and reducing
        microbial diversity by up to 80percent compared to neutral soils (Brady & Weil, 2017). Phosphorus availability
        is maximum at pH 6.0-7.5 and drops sharply outside this range — at pH 5.0, phosphorus availability is
        only 30percent of maximum. Nitrogen-fixing bacteria (Rhizobium, Azospirillum) are most active at pH 6.0-7.5.
        Soil acidification — driven by nitrogen fertilizer overuse, acid rain, and monoculture — is advancing
        globally, with 30percent of world agricultural soils now below pH 6.0. Liming with agricultural limestone or
        dolomite is the primary corrective intervention, raising pH by 0.5-1.0 units per ton applied per hectare.
        However, in severely acidic soils (pH < 4.5), biotic recovery takes 10-20 years even after pH correction
        because native microbial and seed banks are depleted.""",
        "domain": "soil_health",
        "topic": "soil_ph",
        "source": "Brady & Weil - The Nature and Properties of Soils",
        "year": 2017,
        "source_url": "https://www.pearson.com/en-us/subject-catalog/p/nature-and-properties-of-soils-the/P200000006993"
    },
    {
        "text": """Earthworm populations are a key indicator and driver of soil health. Healthy temperate agricultural
        soils support 200-400 earthworms per square meter, processing 10-100 tons of soil per hectare annually.
        Earthworm bioturbation creates macropores that improve water infiltration by 50-200percent, reduces surface runoff,
        and prevents compaction. Their castings are 5-7x richer in available nutrients than surrounding soil.
        Earthworm populations are devastated by: (1) tillage — reduces populations by 70-90percent per tillage event;
        (2) pesticides — insecticides reduce populations 40-60percent; (3) low organic matter — populations collapse
        below SOC 1.0percent. Recovery from zero to functional populations takes 3-10 years under no-till with organic
        inputs. A single metric: earthworm count per square meter (target >150) is a reliable proxy for overall
        soil biological health and future yield potential without synthetic inputs. (Source: FAO, 2020,
        'State of Knowledge of Soil Biodiversity')""",
        "domain": "soil_health",
        "topic": "soil_fauna_earthworms",
        "source": "FAO State of Knowledge of Soil Biodiversity",
        "year": 2020,
        "source_url": "https://www.fao.org/documents/card/en/c/cb1928en"
    },
    {
        "text": """Soil erosion is a permanent loss of soil capital operating at timescales far exceeding human recovery
        capacity. It takes approximately 500 years to form 2.5 cm of topsoil under natural conditions, yet erosion
        can remove this depth in a single intense rainfall event on sloped, bare soil. The IPCC (2019, SRCCL) found
        that soil erosion on croplands globally averages 20-30 Mg/ha/year — 100x the natural soil formation rate.
        Each millimeter of topsoil lost reduces crop yield by 0.4percent, and eroded soils contain 10-50x more organic
        carbon and nutrients than subsoil. Regions with erosion rates above 10 Mg/ha/year face irreversible
        productivity loss within 50-100 years without intervention. Erosion also moves 1.5 billion tons of carbon
        annually from terrestrial to aquatic systems, reducing soil biological activity and contributing to
        waterway eutrophication. Critical interventions: contour farming (reduces erosion 50-75percent), cover crops
        year-round (reduces erosion 90percent on slopes), and vegetative buffer strips.""",
        "domain": "soil_health",
        "topic": "soil_erosion",
        "source": "IPCC Special Report on Climate Change and Land (SRCCL)",
        "year": 2019,
        "source_url": "https://www.ipcc.ch/srccl/"
    },
    {
        "text": """The concept of soil bulk density directly measures soil compaction and is a critical indicator of
        biological health. Ideal bulk density for loam soil is 1.0-1.3 g/cm³. At 1.4 g/cm³, root penetration
        becomes restricted; at 1.6 g/cm³ most plant roots cannot penetrate and oxygen diffusion is limited.
        Compaction reduces pore space and kills or expels soil fauna. Heavy agricultural machinery causes
        compaction to depths of 40-60 cm that cannot be alleviated by surface biological recovery — deep
        subsoiling at >40 cm depth is then required, at a cost of €200-400/ha. Compaction is a major hidden
        driver of biodiversity loss: it eliminates burrowing mammals, ground-nesting insects, and soil
        macrofauna. Prevention (controlled traffic farming, reduced axle loads, maintaining vegetative cover)
        is far cheaper than remediation. Biological remediation via deep-rooted plants (chicory, daikon radish,
        subsoil clovers) can reduce compaction by 15-25percent within 2-3 years. (USDA NRCS Technical Note 2016)""",
        "domain": "soil_health",
        "topic": "soil_compaction",
        "source": "USDA NRCS Technical Note",
        "year": 2016,
        "source_url": "https://www.nrcs.usda.gov/resources/guides-and-instructions/soil-health-technical-notes"
    },
    {
        "text": """Legume cover crops represent one of the highest-leverage interventions for simultaneous soil health
        and biodiversity restoration. Legumes fix atmospheric nitrogen at rates of 50-300 kg N/ha/year via
        Rhizobium bacteria in root nodules, making nitrogen available to subsequent crops without synthetic
        fertilizers. Their dense surface biomass (2-6 t/ha dry matter) feeds soil microbiota upon incorporation.
        Finney & Kaye (2017, Plant and Soil) demonstrated that legume cover crop systems increase soil microbial
        biomass carbon by 20-40percent, reduce soil-borne pathogens by 15-25percent, and increase earthworm populations
        by 25-35percent within two seasons. The diversity benefit extends above ground: flowering legumes
        (clover, vetch, crimson clover) provide critical early-season nectar for bumblebees and solitary bees
        that are critical crop pollinators. A 5-year study in semi-arid Mediterranean conditions showed SOC
        increased from 0.8percent to 1.2percent under continuous legume cover crop rotation — a 50percent increase that moved
        soils from 'poor' to 'moderate' functional status.""",
        "domain": "soil_health",
        "topic": "cover_crops_legumes",
        "source": "Finney & Kaye, Plant and Soil",
        "year": 2017,
        "source_url": "https://doi.org/10.1007/s11104-016-3027-x"
    },
    {
        "text": """No-till agriculture preserves soil structure by eliminating mechanical inversion that destroys fungal
        hyphal networks, kills macrofauna, and exposes soil carbon to rapid oxidation. A meta-analysis of 78
        long-term trials (Poeplau & Don, 2015, Agriculture, Ecosystems and Environment) found that no-till
        systems accumulate 0.1-0.5 t C/ha/year in the top 30 cm, with the greatest gains in warm, moist climates.
        The soil water retention improvement under no-till is critical in semi-arid systems: surface residue
        mulch reduces evaporation by 20-35percent, equivalent to 40-70 additional mm of effective rainfall per year.
        This effectively extends the viable growing window by 2-4 weeks in marginal rainfall zones. Biological
        activity in no-till soils is 2-4x higher than conventional tillage across all organism groups.
        The transition period (years 1-3) typically shows 5-15percent yield decline as soils adjust; most farmers
        who persist past year 3 report yield parity or improvement by year 5, with significantly reduced
        input costs (fuel, fertilizer, labor).""",
        "domain": "soil_health",
        "topic": "no_till_conservation_agriculture",
        "source": "Poeplau & Don, Agriculture Ecosystems and Environment",
        "year": 2015,
        "source_url": "https://doi.org/10.1016/j.agee.2014.11.023"
    },
]


# ─────────────────────────────────────────────────────────────
# DOMAIN 2: LAND USE / LAND COVER
# ─────────────────────────────────────────────────────────────

LAND_USE_CHUNKS: List[KnowledgeChunk] = [
    {
        "text": """Habitat fragmentation is the primary mechanism by which land use change destroys biodiversity,
        even when total habitat area is only moderately reduced. The species-area relationship (MacArthur & Wilson,
        1967) predicts that halving habitat area reduces species richness by 10-20percent, but fragmentation into
        isolated patches imposes additional losses of 15-40percent through edge effects, reduced immigration rates,
        and genetic erosion. A landscape with 40percent forest but fragmented into patches smaller than 100 ha
        supports far fewer species than the same 40percent in connected blocks. Critical threshold: below 30percent habitat
        cover in a landscape, species loss accelerates nonlinearly — this is the fragmentation threshold
        identified by Andrén (1994) and confirmed in tropical, temperate, and boreal systems. Corridors as
        narrow as 100-300m connecting patches can restore 60-80percent of movement for most terrestrial species.
        The Kunming-Montreal Global Biodiversity Framework (2022) sets a target of protecting 30percent of land
        in connected networks by 2030 specifically to address this threshold effect.""",
        "domain": "land_use",
        "topic": "habitat_fragmentation",
        "source": "MacArthur & Wilson, Kunming-Montreal GBF",
        "year": 2022,
        "source_url": "https://www.cbd.int/gbf/"
    },
    {
        "text": """Agroforestry systems integrate trees into cropland or pasture, creating multi-strata habitats that
        dramatically increase biodiversity compared to monocultures. Zomer et al. (2016, Scientific Reports)
        analyzed satellite and field data globally and found that farms with ≥10percent tree cover support 50percent more
        bird species, 30percent more pollinator species, and 2-3x more arthropod species than treeless farms.
        The mechanism is vertical habitat stratification: trees create canopy, sub-canopy, shrub, and ground
        layers that each support distinct species guilds. In semi-arid systems, the Faidherbia albida tree
        (African acacia) is particularly valuable: it sheds leaves in the rainy season (maximizing crop light)
        and retains them in the dry season (providing shade and leaf litter), while fixing 30-80 kg N/ha/year.
        Carbon sequestration in agroforestry systems ranges from 1.5-15 tC/ha/year depending on tree density,
        species, and climate — compared to 0-0.3 tC/ha/year in annual monocultures. The FAO (2013) reports
        SOC increases of 15-25percent within 5 years in agroforestry transitions.""",
        "domain": "land_use",
        "topic": "agroforestry_biodiversity",
        "source": "Zomer et al., Scientific Reports; FAO 2013",
        "year": 2016,
        "source_url": "https://doi.org/10.1038/srep29987"
    },
    {
        "text": """Land use change from natural ecosystems to agriculture is the leading driver of global biodiversity
        loss. Tilman et al. (2001, Science) projected that if global food demand were met through continued
        land conversion (business-as-usual), 1 billion additional hectares of natural habitat would be
        converted by 2050, causing extinction of 10-15percent of the world's species. Monoculture agriculture
        covers 70percent of all cropland globally and supports approximately 1-3 generalist species per hectare,
        compared to 20-200 species in diverse natural habitats. The biodiversity gradient from conventional
        monoculture to organic diversified agriculture to natural habitat follows: monoculture (1x baseline
        diversity) → organic diversified (2-3x) → hedgerows/field margins (5-8x) → semi-natural grassland
        (10-15x) → natural forest/grassland (20-50x). Intercropping — growing two or more crops simultaneously
        — restores 40-60percent of baseline invertebrate diversity compared to monoculture on the same area within
        2-5 years.""",
        "domain": "land_use",
        "topic": "land_conversion_biodiversity_loss",
        "source": "Tilman et al., Science",
        "year": 2001,
        "source_url": "https://doi.org/10.1126/science.1057544"
    },
    {
        "text": """Riparian buffer strips — native vegetation maintained along stream, river, and wetland margins —
        are among the most cost-effective biodiversity investments available to land managers. Broadmeadow &
        Nisbet (2004, Forest Ecology and Management) demonstrated that 10-meter buffers reduce sediment
        runoff entering waterways by 60-75percent, nitrogen by 70-80percent, and phosphorus by 50-70percent. These inputs
        are major drivers of aquatic biodiversity loss through eutrophication. The buffers themselves support
        exceptional biodiversity: the moisture gradient from water margin to upland creates microhabitats
        supporting 3-5x more species than adjacent farmland. Sixty percent of terrestrial bird species use
        riparian habitats for nesting, foraging, or migration stopover. Amphibians — globally the most
        threatened vertebrate class with 41percent of species threatened — depend on riparian connectivity between
        aquatic breeding habitat and terrestrial summer habitat. A 30-meter buffer provides connectivity
        sufficient for most amphibian species to complete their lifecycle. The economics are favorable:
        taking 2-5percent of farmland area for riparian buffers typically costs less than the fertilizer savings
        from reduced runoff capture alone.""",
        "domain": "land_use",
        "topic": "riparian_buffers",
        "source": "Broadmeadow & Nisbet, Forest Ecology and Management",
        "year": 2004,
        "source_url": "https://doi.org/10.1016/j.foreco.2004.07.023"
    },
    {
        "text": """Wetland ecosystems occupy only 6percent of Earth's land surface but support approximately 40percent of all
        species and provide ecosystem services valued at $47 trillion per year — 3x the value of all tropical
        forests combined. The IPBES Global Assessment (2019) reported that 35percent of world wetlands were lost
        between 1970 and 2015, a rate 3x faster than forest loss. Wetlands act as critical biodiversity
        refugia during drought: as surrounding upland habitats dry out, species concentrate in wetlands,
        requiring that wetland quality be maintained for drought resilience. Carbon sequestration in waterlogged
        organic soils (peatlands, freshwater marshes) occurs at rates of 0.5-5.0 tC/ha/year — the highest
        of any ecosystem. Wetland restoration on degraded agricultural land recovers 70-80percent of original
        biodiversity within 5-10 years, and 90percent within 20 years — faster recovery than forest or grassland
        restoration. Investment: $2,000-10,000/ha for restoration vs. $200,000-1,000,000/ha for alternative
        water infrastructure providing equivalent services.""",
        "domain": "land_use",
        "topic": "wetland_conservation_restoration",
        "source": "IPBES Global Assessment",
        "year": 2019,
        "source_url": "https://ipbes.net/global-assessment"
    },
    {
        "text": """Grassland ecosystems are among the most threatened and least protected globally. Less than 10percent of
        temperate grasslands and less than 20percent of tropical savannas are formally protected, making them more
        threatened than tropical forests on a percentage basis. The deep root systems of native grassland
        species (some reaching 3-5 meters deep) store 60-80percent of their biomass below ground, making them
        highly efficient carbon sinks that are invisible from satellite imagery. Conversion of temperate
        grassland to cropland releases 40-70percent of the stored soil carbon within 5-10 years through oxidation.
        Native grassland species richness can reach 50-80 plant species per 100 square meters in intact
        conditions, supporting 1,000+ invertebrate species. Restoration of native grassland from cropland
        requires 10-30 years to recover species richness and 50-100 years to recover soil carbon to original
        levels. The most effective technique: direct seeding with local-provenance native seed mixes,
        combined with appropriate fire or grazing regimes to prevent woody encroachment. (CBD, 2020)""",
        "domain": "land_use",
        "topic": "grassland_conservation",
        "source": "CBD Status of Grasslands Report",
        "year": 2020,
        "source_url": "https://www.cbd.int/gbo/"
    },
]


# ─────────────────────────────────────────────────────────────
# DOMAIN 3: BIODIVERSITY INDICATORS
# ─────────────────────────────────────────────────────────────

BIODIVERSITY_CHUNKS: List[KnowledgeChunk] = [
    {
        "text": """The Shannon Diversity Index (H') is the standard measure of ecological community diversity,
        integrating both species richness (number of species) and evenness (relative abundance). H' = 0
        represents a single-species monoculture; values of 1-2 indicate low diversity; 2-3 moderate;
        3-4 high; and >4 exceptional (characteristic of old-growth forests or pristine coral reefs).
        In managed agricultural landscapes, H' < 1.5 signals functionally depauperate conditions where
        pest-predator balance, pollination services, and nutrient cycling are compromised. The 'diversity
        paradox' of modern agriculture is that most monoculture systems operate at H' 0-0.3, providing
        food but requiring massive synthetic inputs to compensate for lost ecosystem services valued at
        $2.5 trillion/year globally (Costanza et al., 2014). Increasing on-farm plant diversity to
        achieve H' > 2.5 through polycultures, cover crops, and wildflower margins correlates with
        40-60percent reduction in pesticide requirement as natural enemy populations recover. (Magurran, 2004)""",
        "domain": "biodiversity_indicators",
        "topic": "shannon_diversity_index",
        "source": "Magurran - Measuring Biological Diversity",
        "year": 2004,
        "source_url": "https://www.wiley.com/en-us/Measuring+Biological+Diversity-p-9780632056330"
    },
    {
        "text": """Pollinator biodiversity is a direct service provider to food security. The IPBES Assessment
        on Pollinators (2016) estimated that 75percent of the world's food crops depend at least partially on
        animal pollination, with a market value of $235-577 billion per year. Bee diversity is the
        primary driver of this service: diverse bee communities pollinate more efficiently than single
        species due to complementarity in flower type, foraging time, and weather tolerance. Studies show
        that each additional wild bee species in an agricultural landscape increases crop yield by 1-5percent
        independent of managed honeybee presence. Globally, 40percent of invertebrate pollinator species —
        including 16percent of butterflies and 9percent of bees — are at elevated risk of extinction. The primary
        drivers are: pesticide use (especially systemic neonicotinoids), habitat loss reducing floral
        resources, and loss of nesting habitat (bare soil for ground-nesting bees, hollow stems for
        cavity-nesters). Restoration strategy: providing 10percent semi-natural habitat within 1km of crops
        increases wild bee abundance by 50percent and reduces yield gaps by 15-20percent.""",
        "domain": "biodiversity_indicators",
        "topic": "pollinator_biodiversity",
        "source": "IPBES Assessment on Pollinators, Pollinators and Food Production",
        "year": 2016,
        "source_url": "https://doi.org/10.1126/science.aaa0198"
    },
    {
        "text": """Species richness on its own is insufficient as a biodiversity metric — the trophic structure
        and functional diversity of a community determines its stability and service provision. The
        Rockström et al. (2009) planetary boundaries framework defined a 'biodiversity boundary' based
        on extinction rate: the safe operating space is ≤10 extinctions per million species-years.
        Current rates are estimated at 100-1,000 per million species-years — 10-100x the boundary.
        This represents not just species loss but collapse of the ecological networks that species form.
        Functional diversity — measuring the range of biological roles (nutrient cycling, predation,
        pollination, seed dispersal) — is a better predictor of ecosystem stability than species richness
        alone. Communities with high functional diversity maintain services under stress (drought, invasion)
        where species-rich but functionally redundant communities do not. Restoration programs that
        maximize functional diversity achieve service recovery at 30-50percent lower species counts than
        random restoration.""",
        "domain": "biodiversity_indicators",
        "topic": "functional_biodiversity_trophic_structure",
        "source": "Rockström et al., Nature - Planetary Boundaries",
        "year": 2009,
        "source_url": "https://doi.org/10.1038/461472a"
    },
    {
        "text": """Native species percentage is a key metric for distinguishing 'recovered' from 'invaded'
        ecosystems. Many landscapes show high species richness but low ecological function because species
        composition is dominated by cosmopolitan invasive species (Lantana camara, water hyacinth,
        Prosopis juliflora) rather than native specialists. The IUCN (2022) recognizes invasive species
        as the second leading cause of global species extinction after habitat loss, responsible for 37percent
        of all extinctions for which cause is known. The problem is particularly severe on islands (60percent
        of extinctions) and in freshwater systems (39percent of threatened fish species affected). Invasive
        plant dominance reduces soil invertebrate diversity by 40-60percent and bird diversity by 30-50percent
        because they produce fewer, lower-quality arthropods as food compared to native plants. The
        most effective control is early detection and rapid response — eradicating a new invasion costs
        10-100x less than controlling an established one. Biological control (natural enemies from the
        invasive's home range) is the only cost-effective option for landscape-scale control of
        established invasives.""",
        "domain": "biodiversity_indicators",
        "topic": "native_species_invasive_management",
        "source": "IUCN Red List 2022 Update",
        "year": 2022,
        "source_url": "https://www.iucnredlist.org/"
    },
    {
        "text": """Bird diversity is widely used as a surrogate indicator for overall biodiversity because birds
        are sensitive, easily monitored, and occupy all trophic levels. The State of the World's Birds
        (BirdLife International, 2022) reports that 49percent of all bird species are in population decline,
        with farmland birds declining by 55percent since 1970 across Europe and North America — the steepest
        decline of any habitat group. Farmland bird collapse is driven by: (1) loss of winter seed food
        (clean harvesting practices removing food sources); (2) insecticide use eliminating the arthropod
        food base for chick-rearing; (3) loss of nesting habitat (hedgerows, field margins, unimproved
        grassland). Each 10percent increase in semi-natural habitat on a farm is associated with 35-50percent more
        farmland bird species. Birds provide significant pest control services: a single barn owl pair
        consumes 1,000-1,500 small rodents per year; swallow pairs consume 50,000-100,000 flying insects
        per season. Loss of bird diversity directly increases pest pressure and crop losses.""",
        "domain": "biodiversity_indicators",
        "topic": "bird_diversity_farmland",
        "source": "BirdLife International State of World Birds",
        "year": 2022,
        "source_url": "https://www.birdlife.org/projects/state-of-worlds-birds/"
    },
]


# ─────────────────────────────────────────────────────────────
# DOMAIN 4: CLIMATE FACTORS
# ─────────────────────────────────────────────────────────────

CLIMATE_CHUNKS: List[KnowledgeChunk] = [
    {
        "text": """The IPCC Sixth Assessment Report (AR6, 2021) presents the most comprehensive assessment of
        climate-biodiversity interactions. In semi-arid and arid regions — covering 40percent of Earth's land
        surface — mean temperatures are projected to increase 2-4°C above pre-industrial levels by 2100
        under moderate emissions scenarios, with rainfall variability increasing 20-40percent. This combination
        is particularly lethal for biodiversity: higher temperatures increase evapotranspiration demand
        even without rainfall change, and extreme rainfall variability (longer dry periods punctuated by
        intense events) makes soil conservation critical because erosion risk spikes during intense events
        while drought risk increases in dry periods. The IPCC identified 16 'climate change hotspots' —
        regions of compounding risk — including the Sahel, Indian subcontinent, Central America, and
        Mediterranean Basin. Biodiversity in these regions faces 'double jeopardy': existing habitat
        degradation plus accelerating climate change.""",
        "domain": "climate_factors",
        "topic": "climate_change_biodiversity_impact",
        "source": "IPCC AR6 WG1 & WG2",
        "year": 2021,
        "source_url": "https://www.ipcc.ch/report/ar6/wg1/"
    },
    {
        "text": """Rainfall seasonality and predictability are more important for biodiversity than annual total
        alone. A biome receiving 600mm annually concentrated in a 2-month monsoon supports different —
        and often less diverse — communities than one receiving 600mm spread across 8 months. Pulse-reserve
        dynamics in semi-arid systems mean that biodiversity is structured around rainfall events:
        seed banks remain dormant until threshold rainfall triggers synchronized germination. Climate change
        is disrupting these seasonal cues, causing phenological mismatches between plants and their
        pollinators. Studies in the Sahel show a 10-day shift in rainfall onset over 30 years has caused
        15-25percent decline in pollination success for native plants. Drought frequency and duration matter
        more than mean annual rainfall for soil biological communities: IPCC data show that periods of
        >60 consecutive days without rainfall reduce soil microbial activity by 40-80percent, and if repeated
        annually, cause permanent community shifts toward drought-tolerant but functionally impoverished
        communities. Maintaining soil moisture via mulch, cover crops, and agroforestry is therefore
        a climate adaptation strategy for biodiversity.""",
        "domain": "climate_factors",
        "topic": "rainfall_patterns_biodiversity",
        "source": "IPCC SRCCL; Sahel Biodiversity Study",
        "year": 2019,
        "source_url": "https://www.ipcc.ch/srccl/"
    },
    {
        "text": """Temperature increase affects species through three mechanisms: direct thermal stress, phenological
        disruption, and habitat shift. Most ectothermic species (insects, reptiles, amphibians) have narrow
        thermal tolerance ranges (5-10°C) and are particularly vulnerable. A warming of 1.5°C is projected
        to threaten 6percent of insects, 4percent of vertebrates, and 8percent of plants with local extinction (Warren et al.,
        2018, Science). At 2°C, these figures rise to 18percent, 8percent, and 16percent respectively — illustrating the
        nonlinear response to warming. For agricultural biodiversity, warming above 30°C daily maximum
        reduces pollination efficiency by 30-50percent because bee flight activity declines and pollen viability
        decreases. In areas where maximum daily temperatures regularly exceed 35°C, crop pollination failures
        cause yield losses of 10-30percent even with adequate soil moisture. Agroforestry (canopy shade reducing
        ground temperatures by 2-5°C) and riparian vegetation (cooling via evapotranspiration) are the
        most effective local-scale temperature mitigation strategies for biodiversity.""",
        "domain": "climate_factors",
        "topic": "temperature_species_vulnerability",
        "source": "Warren et al., Science; IPCC AR6",
        "year": 2018,
        "source_url": "https://doi.org/10.1126/science.aar3646"
    },
    {
        "text": """Drought-adapted ecosystems have evolved complex mechanisms to survive water scarcity, but these
        adaptations have limits and are being exceeded. In semi-arid biomes, the most biodiverse period
        is typically the 2-4 weeks following the first rains — when dormant seeds and soil organisms
        simultaneously activate. This flush of activity supports specialist species found nowhere else.
        Climate change is compressing this window and making it less predictable, directly threatening
        semi-arid biodiversity. Soil crusts (cryptobiotic crusts composed of cyanobacteria, mosses,
        and lichens) are a critical but invisible biodiversity layer in semi-arid systems, stabilizing
        soil against erosion, fixing nitrogen, and retaining moisture. They are destroyed by a single
        livestock trampling event and take 50-250 years to recover. Protection of soil crusts through
        rotational grazing and livestock exclusion is a high-priority, low-cost intervention in
        semi-arid landscapes. (USGS Biological Soil Crusts Report; IPCC AR6 Chapter 5)""",
        "domain": "climate_factors",
        "topic": "drought_semi_arid_biodiversity",
        "source": "USGS Biological Soil Crusts Report; IPCC AR6",
        "year": 2021,
        "source_url": "https://pubs.usgs.gov/bul/1597/report.pdf"
    },
]


# ─────────────────────────────────────────────────────────────
# DOMAIN 5: HUMAN IMPACT
# ─────────────────────────────────────────────────────────────

HUMAN_IMPACT_CHUNKS: List[KnowledgeChunk] = [
    {
        "text": """Deforestation is the single largest driver of terrestrial biodiversity loss globally. Hansen
        et al. (2013, Science) used Landsat satellite data to document 2.3 million km² of forest loss
        between 2000 and 2012 — an area equivalent to the United States east of the Mississippi. Each 1percent
        loss of forest cover in a watershed reduces average streamflow by 0.5-2percent and increases water
        temperature by 0.3-0.8°C, directly threatening aquatic biodiversity. Tropical forests contain
        50-80percent of all terrestrial species on 7percent of Earth's land area — meaning their loss has outsized
        biodiversity consequences. The 'extinction debt' concept (Tilman et al., 1994) explains why species
        loss continues for decades after habitat loss stops: species with small populations persist for
        years before stochastic extinction. A forest patch that loses 70percent of its area will eventually
        lose 50percent of its species even if no further loss occurs. Secondary forest regrowth (after
        deforestation) recovers 80percent of species richness within 20 years but only 30-50percent of species
        composition, as forest specialists remain absent.""",
        "domain": "human_impact",
        "topic": "deforestation_impact",
        "source": "Hansen et al., Science; Tilman et al.",
        "year": 2013,
        "source_url": "https://doi.org/10.1126/science.1244693"
    },
    {
        "text": """Agricultural pesticide use is the most pervasive chemical pollutant affecting biodiversity globally.
        The WHO and UNEP estimate that 3.5 million tons of pesticides are applied annually worldwide,
        of which only 0.1-1percent contacts the target pest organism — the rest enters soil, water, and air.
        Neonicotinoid insecticides, now the world's most used insecticide class, are systemic (taken up
        by all plant tissue including pollen and nectar) and persistent in soil (half-life 200-1,000 days).
        Field-realistic neonicotinoid exposures reduce bumblebee queen production by 85percent, disrupt honey bee
        navigation, and reduce solitary bee reproduction by 35-40percent (Woodcock et al., 2017, Science).
        Glyphosate herbicide — the most widely used herbicide globally — does not directly kill
        pollinators but eliminates the broadleaf 'weed' species (dandelions, clover, plantain) that are
        primary food sources for pollinators in agricultural landscapes. A 50percent reduction in pesticide use —
        the CBD COP15 (2022) target — is achievable through Integrated Pest Management (IPM) while
        maintaining yields, as demonstrated in 20+ country programs.""",
        "domain": "human_impact",
        "topic": "pesticide_impact_biodiversity",
        "source": "Woodcock et al., Science; WHO-UNEP Pesticide Report",
        "year": 2017,
        "source_url": "https://doi.org/10.1126/science.aan2776"
    },
    {
        "text": """Nitrogen pollution is an invisible but globally significant driver of biodiversity loss.
        The reactive nitrogen produced annually by human activities (fertilizers, combustion) now exceeds
        natural nitrogen fixation — a Planetary Boundary that has been exceeded (Rockström et al., 2009).
        Nitrogen deposition from air pollution reduces plant diversity by favoring fast-growing grasses
        that outcompete slow-growing native wildflowers. In European semi-natural grasslands, nitrogen
        deposition is the leading cause of 70percent of sites failing to meet biodiversity targets. For every
        1 kg of excess nitrogen deposited per hectare per year, plant species richness declines by 0.5-1
        species over 20 years. This is the 'eutrophication' effect, which is as damaging in terrestrial
        systems as in aquatic ones. Buffer strips and hedgerows reduce nitrogen deposition reaching
        sensitive habitats by 40-70percent. At field scale, precision fertilizer application (right rate, right
        time, right place) can reduce nitrogen surplus by 30-50percent without yield loss, directly reducing
        the biodiversity impact of agricultural production. (European Nitrogen Assessment, 2011)""",
        "domain": "human_impact",
        "topic": "nitrogen_pollution_biodiversity",
        "source": "European Nitrogen Assessment; Rockström et al.",
        "year": 2011,
        "source_url": "https://www.nine-esf.org/ENA"
    },
    {
        "text": """Plastic pollution has emerged as a novel threat to soil biodiversity with poorly understood
        long-term consequences. Microplastics (particles <5mm) are now found in virtually all
        agricultural soils globally, with concentrations 4-23x higher in agricultural than natural
        soils due to plastic mulch films, sewage sludge application, and atmospheric deposition.
        Laboratory studies show that microplastic concentrations typical of many agricultural soils
        reduce earthworm reproduction by 23percent, alter soil microbial community composition, and reduce
        plant biomass by 3-5percent. The mechanism appears to be physical interference with soil structure
        (microplastics reduce aggregate stability and aeration) and chemical leaching of plasticizers
        and additives that are toxic to soil organisms. Nanoplastics (<1 μm) penetrate plant root
        cells and have been shown to reduce crop yield by up to 20percent in controlled experiments.
        Prevention is far preferable to remediation: biodegradable mulch films (lignin-based or
        starch-based) eliminate the problem at source. (UNEP, 2021; Rillig et al., 2019, Science)""",
        "domain": "human_impact",
        "topic": "plastic_pollution_soil",
        "source": "UNEP Plastic Pollution Report; Rillig et al., Science",
        "year": 2021,
        "source_url": "https://doi.org/10.1126/science.aax8665"
    },
    {
        "text": """Light pollution disrupts nocturnal biodiversity in ways that are severely underappreciated.
        Artificial light at night (ALAN) affects 83percent of the world's population and 23percent of land surface.
        Nocturnal insects — which include most moth species, a major component of food webs — show 50percent
        reduction in abundance near artificial lights due to fatal attraction and disrupted navigation.
        Moths are critical nighttime pollinators for many native plant species not pollinated by daytime
        bees. Bat foraging activity is suppressed around lights; bats consume 3,000-8,000 insects per
        night and are critical for agricultural pest control. Light pollution disrupts animal migration
        (birds, marine turtles), breeding cycles triggered by photoperiod (amphibians, fireflies, deer),
        and plant dormancy cycles. Simple mitigation: shielded, downward-directed LEDs; amber-spectrum
        lighting (3000K) with reduced UV emission; timer controls reducing output 11pm-4am by 70percent.
        These measures reduce biodiversity impacts by 60-80percent at minimal infrastructure cost. (UNEP/CMS)""",
        "domain": "human_impact",
        "topic": "light_pollution_nocturnal_biodiversity",
        "source": "UNEP/CMS Guidelines on Light Pollution",
        "year": 2020,
        "source_url": "https://www.cms.int/en/publication/artificial-light-night-its-impact-wildlife"
    },
]


# ─────────────────────────────────────────────────────────────
# Master registry — all chunks organized by domain
# ─────────────────────────────────────────────────────────────

ALL_CHUNKS: Dict[str, List[KnowledgeChunk]] = {
    "soil_health":            SOIL_HEALTH_CHUNKS,
    "land_use":               LAND_USE_CHUNKS,
    "biodiversity_indicators": BIODIVERSITY_CHUNKS,
    "climate_factors":        CLIMATE_CHUNKS,
    "human_impact":           HUMAN_IMPACT_CHUNKS,
}


def get_all_chunks() -> List[KnowledgeChunk]:
    """Returns all chunks across all domains as a flat list."""
    all_chunks = []
    for domain, chunks in ALL_CHUNKS.items():
        all_chunks.extend(chunks)
    return all_chunks


def get_chunks_by_domain(domain: str) -> List[KnowledgeChunk]:
    """Returns chunks for a specific domain."""
    return ALL_CHUNKS.get(domain, [])


def get_total_chunk_count() -> int:
    return sum(len(chunks) for chunks in ALL_CHUNKS.values())
