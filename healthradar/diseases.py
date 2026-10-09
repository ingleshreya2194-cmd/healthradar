"""
diseases.py
-----------
Awareness content for each disease. Written as general public-health
information in line with WHO and CDC fact sheets. It is NOT medical advice
and does not diagnose or cure anything.

To update the text, edit the lists below. The pages read this file directly.
"""

DISCLAIMER = ("This app gives general information only and is not medical advice. "
              "Consult a doctor for diagnosis and treatment.")

HOME_CARE_NOTE = ("These are comfort measures that may help you feel better while you recover. "
                  "They are not cures and do not replace medical care. "
                  "Honey must not be given to children under 1 year old.")

DISEASE_INFO = {
    "Dengue": {
        "slug": "dengue",
        "title": "Dengue",
        "tagline": "A mosquito-borne viral illness common in tropical and sub-tropical areas.",
        "overview": ("Dengue is caused by a virus spread by Aedes mosquitoes. Many people have mild "
                     "or no symptoms, but some develop severe dengue, which can be life-threatening "
                     "and needs urgent medical care."),
        "symptoms": [
            "Sudden high fever",
            "Severe headache and pain behind the eyes",
            "Muscle, bone and joint pain",
            "Nausea and vomiting",
            "Skin rash and swollen glands",
            "Symptoms usually begin 4-10 days after a bite and last about 2-7 days",
        ],
        "spread": [
            "Through the bite of an infected Aedes mosquito (mainly Aedes aegypti)",
            "These mosquitoes bite mostly during the day and breed in clean standing water, such as buckets, coolers, tyres and flower pots",
            "It does not spread by casual contact, but a sick person can pass the virus to mosquitoes that bite them",
        ],
        "prevention": [
            "Use mosquito repellent and wear long sleeves and trousers, also during the day",
            "Use window and door screens or mosquito nets",
            "Empty, cover or clean containers that hold water at least once a week",
            "Join community clean-up efforts to remove mosquito breeding places",
            "In some countries a dengue vaccine is approved for certain age groups. Ask a doctor or your local health authority if it is recommended for you",
            "If you have dengue, stay under a mosquito net so mosquitoes do not bite you and spread it further",
        ],
        "medical": [
            "There is no specific antiviral medicine for dengue",
            "Doctors usually advise rest and plenty of fluids, and may order blood tests to monitor the illness",
            "Paracetamol (acetaminophen) may be used for fever and pain only as advised by a doctor",
            "Avoid aspirin and ibuprofen-type painkillers (NSAIDs) unless a doctor says so, because they can increase the risk of bleeding",
            "Severe dengue needs hospital care, for example fluids given through a drip and close monitoring",
        ],
        "home_care": [
            "Rest as much as you can",
            "Drink plenty of fluids: water, oral rehydration solution (ORS), clear soups, fruit juices",
            "Eat light, easy-to-digest food",
            "Stay under a mosquito net or in a screened room",
            "Do not rely on unproven remedies, and do not delay seeing a doctor",
        ],
        "warning_signs_intro": ("Warning signs often appear 1-2 days after the fever goes down. "
                                "Go to a hospital or emergency care immediately if you notice:"),
        "warning_signs": [
            "Severe stomach (abdominal) pain",
            "Repeated or persistent vomiting",
            "Bleeding from the nose or gums, blood in vomit or stool, or easy bruising",
            "Extreme tiredness, restlessness or drowsiness",
            "Difficulty breathing or fast breathing",
            "Cold, clammy or pale skin",
        ],
        "sources": ["WHO: Dengue and severe dengue fact sheet", "CDC: Dengue - Symptoms and Treatment"],
    },
    "Influenza": {
        "slug": "influenza",
        "title": "Influenza (Flu)",
        "tagline": "A contagious respiratory illness that is more common in the cold or rainy season.",
        "overview": ("Influenza is a viral infection of the nose, throat and lungs. Most people recover "
                     "in a week or two, but flu can be serious for young children, older adults, "
                     "pregnant women and people with long-term health conditions."),
        "symptoms": [
            "Fever or chills",
            "Cough and sore throat",
            "Runny or blocked nose",
            "Body aches and headache",
            "Tiredness",
            "Vomiting and diarrhoea can occur, more often in children",
        ],
        "spread": [
            "Through tiny droplets when an infected person coughs, sneezes or talks",
            "By touching surfaces with the virus and then touching your eyes, nose or mouth",
            "Most contagious in the first few days of illness",
        ],
        "prevention": [
            "Get a seasonal flu vaccine every year, especially if you are in a higher-risk group",
            "Wash hands often with soap and water, or use an alcohol-based hand rub",
            "Cover coughs and sneezes with a tissue or your elbow",
            "Wear a mask in crowded or poorly ventilated places, especially during flu season",
            "Avoid close contact with people who are sick, and stay home when you are sick",
            "Keep rooms well ventilated",
        ],
        "medical": [
            "Most healthy people recover with rest and fluids",
            "A doctor may prescribe an antiviral medicine in some cases, for example for people at higher risk or with severe illness. Antivirals work best when started early",
            "Antibiotics do not work against flu viruses. A doctor will decide if they are needed for a separate bacterial infection",
            "Do not give aspirin to children or teenagers with flu-like illness",
            "Use fever or pain medicine only as advised by a doctor or as directed on the label",
        ],
        "home_care": [
            "Rest and stay home to avoid spreading the illness",
            "Drink plenty of fluids, including water and oral rehydration solution if you have vomiting or diarrhoea",
            "Warm fluids such as soup or warm water can soothe the throat",
            "A warm salt-water gargle may ease a sore throat",
            "A warm ginger-honey drink may be comforting (not for children under 1 year)",
            "Eat light food as your appetite allows",
        ],
        "warning_signs_intro": "Seek urgent medical care immediately if you or your child have:",
        "warning_signs": [
            "Difficulty breathing or shortness of breath",
            "Chest pain or pressure that does not go away",
            "Confusion, severe dizziness or difficulty waking up",
            "Seizures (fits)",
            "Very little or no urine, or signs of dehydration",
            "Symptoms that improve and then come back with fever and worse cough",
            "In children: fast breathing, bluish lips or face, not drinking enough, or being unusually hard to wake",
        ],
        "sources": ["WHO: Influenza (seasonal) fact sheet", "CDC: Flu - Symptoms and Treatment"],
    },
    "COVID-19": {
        "slug": "covid-19",
        "title": "COVID-19",
        "tagline": "A respiratory illness caused by the SARS-CoV-2 virus, which still causes waves of infection.",
        "overview": ("COVID-19 can cause anything from no symptoms to severe illness. Older adults, "
                     "people with long-term conditions and those who are not vaccinated have a higher "
                     "chance of becoming seriously ill."),
        "symptoms": [
            "Fever or chills",
            "Cough and sore throat",
            "Tiredness and body aches",
            "Headache",
            "Loss of taste or smell",
            "Shortness of breath in some people",
        ],
        "spread": [
            "Through droplets and tiny airborne particles when an infected person breathes, talks, coughs or sneezes",
            "Spreads more easily in crowded, closed or poorly ventilated places",
            "Less often, by touching contaminated surfaces and then your face",
            "A person can spread the virus even before symptoms appear",
        ],
        "prevention": [
            "Stay up to date with COVID-19 vaccination as recommended in your country",
            "Wear a well-fitting mask in crowded or poorly ventilated places",
            "Improve ventilation: open windows and doors when possible",
            "Wash hands often with soap and water, or use an alcohol-based hand rub",
            "Test if you have symptoms, and stay home and isolate while you are sick",
            "Avoid close contact with people who are unwell",
        ],
        "medical": [
            "Testing helps confirm the illness. Follow your local health authority's advice on testing",
            "Most people recover at home with rest and fluids",
            "A doctor may prescribe antiviral medicine in some cases, usually for people at higher risk of severe illness, and it works best when started early",
            "Severe illness may need hospital care, such as oxygen support",
            "Use fever or pain medicine only as advised by a doctor or as directed on the label",
        ],
        "home_care": [
            "Rest and isolate while you are sick, as advised by local health guidance",
            "Drink plenty of fluids, including water and oral rehydration solution if needed",
            "Warm fluids such as soup or warm water can soothe the throat",
            "A warm salt-water gargle may ease a sore throat",
            "A warm ginger-honey drink may be comforting (not for children under 1 year)",
            "Eat light food, keep the room ventilated and watch how your symptoms change",
        ],
        "warning_signs_intro": "Get emergency medical help immediately if you or someone else has:",
        "warning_signs": [
            "Trouble breathing or shortness of breath at rest",
            "Chest pain or pressure that does not go away",
            "New confusion or inability to stay awake",
            "Pale, grey or blue-coloured lips, skin or nails",
            "Symptoms that quickly get worse",
        ],
        "sources": ["WHO: Coronavirus disease (COVID-19) fact sheet and advice for the public",
                    "CDC: COVID-19 - Symptoms and Treatment"],
    },
}


def get_disease_by_name(name):
    """Find a disease by name or slug (case-insensitive). Returns None if not found."""
    key = name.strip().lower()
    key = {"flu": "influenza", "covid": "covid-19", "covid19": "covid-19"}.get(key, key)
    for d, info in DISEASE_INFO.items():
        if key in (d.lower(), info["slug"]):
            return d, info
    return None
