import re
from typing import Optional, Tuple

CRIME_KEYWORDS = re.compile(
    r"\b(attack|assault|murder|killed|dead|death|stabbing|chainsaw|rape|fir|police|arrest|custody|firing|encounter|gunman|terrorist|blast|bomb|accident|collision|drowned|kidnap|hijack)\b",
    re.I
)

DISASTER_WEATHER_KEYWORDS = re.compile(
    r"\b(cyclone|earthquake|flood|floods|flooding|rainfall|rain|monsoon|storm|landslide|tsunami|avalanche|cloudburst|heatwave|cold wave|air quality|aqi|smog|pollution|tremor)\b",
    re.I
)

# High-precision word-boundary regex patterns for each category
CATEGORY_PATTERNS = [
    # 1. Odisha Regional Bureau (explicit mentions of Odisha people, places, institutions)
    (
        "odisha",
        re.compile(
            r"\b(odisha|bhubaneswar|cuttack|puri|sambalpur|rourkela|berhampur|balasore|baripada|koraput|naveen patnaik|mohan majhi|jagannath|odia|bjd|utkal|chilika|paradip|subarnarekha|mahanadi|lingaraj)\b",
            re.I
        )
    ),
    # 2. Sports Arena
    (
        "sports",
        re.compile(
            r"\b(cricket|bcci|ipl|rohit sharma|virat kohli|shubman gill|dhoni|hardik pandya|bumrah|rishabh pant|kl rahul|football|fifa|isl|tennis|wimbledon|us open|french open|badminton|pv sindhu|hockey|olympics|paralympics|athletics|tournament|match|trophy|wicket|runs|batting|bowler|batsman|striker|goal|points table|icc|champions trophy|ballon d.or|pro kabaddi|scorecard|centuries|century|sixes|ipl auction|world cup|odi|test match|t20)\b",
            re.I
        )
    ),
    # 3. Arts & Entertainment
    (
        "entertainment",
        re.compile(
            r"\b(bollywood|hollywood|tollywood|kollywood|mollywood|sandallwood|cinema|film|movie|box office|trailer|teaser|actor|actress|filmmaker|director|ott|netflix|prime video|hotstar|celebrity|music video|singer|songs|album|screening|premiere|dia mirza|shah rukh khan|srk|salman khan|aamir khan|deepika|ranbir kapoor|alia bhatt|karan johar|censor board|bigg boss|kangana|rajinikanth|thalapathy vijay|allu arjun|ram charan|jr ntr|prabhas|box-office|bollywood hungama|jackie shroff|sharad kelkar)\b",
            re.I
        )
    ),
    # 4. Business & Economy
    (
        "business",
        re.compile(
            r"\b(sensex|nifty|bse|nse|stock market|stocks|share market|rbi|reserve bank of india|inflation|gdp|rupee|quarterly profit|revenue|earnings|ipo|mutual fund|fintech|banking|tax|gst|monetary policy|bullion|gold price|silver price|crude oil|market rally|dalal street|investor|valuation|acquisition|fdi|trade deficit|export|import|treasury|disinvestment|startup|venture capital|corporate debt|fiscal deficit)\b",
            re.I
        )
    ),
    # 5. Politics & Governance
    (
        "politics",
        re.compile(
            r"\b(election|poll|bjp|congress|inc|aap|tmc|dmk|aiadmk|cpim?|bsp|sp|yuvajana sramika|bjp-led|nda|india bloc|rahul gandhi|narendra modi|amit shah|mamata banerjee|arvind kejriwal|akhilesh yadav|nitish kumar|mk stalin|siddaramaiah|fadnavis|shinde|uddhav|parliament|lok sabha|rajya sabha|assembly|vidhan sabha|mla|mp|minister|cabinet|ordinance|voter|constituency|political rally|chief minister|prime minister|cec gyanesh kumar|election commission of india|eci|poll panel|bypoll|seat-sharing|defection|no-confidence|trump|biden|kamala harris|white house|capitol hill|senate|geopolitics|diplomacy|bilateral talks|summit)\b",
            re.I
        )
    ),
    # 6. Science & Space
    (
        "science",
        re.compile(
            r"\b(isro|nasa|esa|jaxa|space exploration|spacecraft|satellite|rocket launch|chandrayaan|gaganyaan|aditya-l1|mangalyaan|astronomy|telescope|james webb|supernova|black hole|mars rover|quantum computing|particle physics|biotechnology|scientific discovery|genetics|dna research|crispr|meteorology|paleontology|neuroscience|fusion reactor|cern)\b",
            re.I
        )
    ),
    # 7. Technology & AI
    (
        "technology",
        re.compile(
            r"\b(artificial intelligence|generative ai|\bai\b|chatgpt|openai|anthropic|claude|gemini ai|machine learning|deep learning|software|cybersecurity|hacker|malware|ransomware|semiconductor|chipmaker|nvidia|qualcomm|intel|amd|tsmc|smartphone|iphone|android|gadget|technological|algorithms?|cloud computing|big tech|metaverse|cryptocurrency|bitcoin|ethereum|blockchain|fintech app|5g network|6g|server outage|operating system|ios 18|cyber attack)\b",
            re.I
        )
    ),
    # 8. Education & Skills
    (
        "education",
        re.compile(
            r"\b(cbse|icse|ncert|ugc|aicte|neet|jee main|jee advanced|cuet|cat exam|gate exam|upsc|university|college|students?|teachers?|professors?|syllabus|curriculum|exam results?|examination|admissions?|board results?|degree|degrees|higher education|pedagogy|campus placement|scholarship|iit|iim|nit|aiims|vice chancellor)\b",
            re.I
        )
    ),
    # 9. Lifestyle & Health
    (
        "lifestyle",
        re.compile(
            r"\b(wellness|mental health|nutrition|diet|fitness|cancer treatment|cardiology|hospital|disease|vaccine|epidemic|tourism|travel destination|culinary|food festival|fashion week|skincare|ayurveda|meditation|yoga day|diwali celebration|chath puja|durga puja|living style|dermatology|superfood)\b",
            re.I
        )
    ),
    # 10. Regional India
    (
        "regional",
        re.compile(
            r"\b(tamil nadu|kerala|karnataka|andhra pradesh|telangana|maharashtra|gujarat|punjab|haryana|bihar|uttar pradesh|west bengal|assam|rajasthan|madhya pradesh|kashmir|jammu|jharkhand|chhattisgarh|himachal pradesh|uttarakhand|goa|tasmac|bmc|bengaluru|mumbai|chennai|hyderabad|kolkata|lucknow|patna|chandigarh|jaipur|kochi|thiruvananthapuram|amritsar)\b",
            re.I
        )
    ),
]

def classify_news(
    title: str,
    summary: str = "",
    source_type: Optional[str] = None,
    publisher_name: Optional[str] = None
) -> Tuple[str, bool, Optional[str]]:
    """
    High-precision news classifier.
    Returns: (category_slug, is_regional, regional_state)
    """
    combined = f"{title} {summary}".strip()
    is_crime = bool(CRIME_KEYWORDS.search(title))
    is_disaster = bool(DISASTER_WEATHER_KEYWORDS.search(title))

    # 1. Match against high-priority topical patterns
    for cat_slug, regex in CATEGORY_PATTERNS:
        # If crime or weather disaster, don't categorize into education or lifestyle
        if (is_crime or is_disaster) and cat_slug in ("education", "lifestyle"):
            continue
        if regex.search(combined):
            is_reg = cat_slug in ("regional", "odisha")
            reg_state = "Odisha" if cat_slug == "odisha" else None
            return (cat_slug, is_reg, reg_state)

    # 2. Check publisher-based regionality (Odisha outlets)
    if publisher_name and any(k in publisher_name.lower() for k in ["odisha", "otv", "prameya", "dharitri", "sambad", "pragativadi"]):
        return ("odisha", True, "Odisha")

    # 3. Source-based contextual fallback
    if source_type == "business" or (publisher_name and any(k in publisher_name.lower() for k in ["economic times", "mint", "business standard", "financial express", "business line", "business today"])):
        return ("business", False, None)

    if source_type == "regional" or (publisher_name and any(k in publisher_name.lower() for k in ["thanthi", "dinamalar", "eenadu", "sakshi", "lokmat", "sakal", "manorama", "mathrubhumi"])):
        return ("regional", True, None)

    # 4. Default category is national India
    return ("india", False, None)
