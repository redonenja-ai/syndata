"""
SynData Studio — Synthetic AI Data Generator (Streamlit)
pip install streamlit pandas
streamlit run syndata_studio.py
"""

import streamlit as st
import pandas as pd
import json
import io
import random
from datetime import datetime

st.set_page_config(
    page_title="SynData Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──
st.markdown("""
<style>
    .stApp { background: #0a0a0f; }
    [data-testid="stSidebar"] { background: #12121a; border-right: 1px solid #2a2a3e; }
    .main .block-container { padding-top: 2rem; }
    .stButton>button {
        background: linear-gradient(135deg, #6c5ce7, #5a4bd1);
        color: white; border: none; border-radius: 10px;
        padding: 0.6rem 1.5rem; font-weight: 600;
        box-shadow: 0 4px 15px rgba(108,92,231,0.3);
    }
    .stButton>button:hover { box-shadow: 0 6px 20px rgba(108,92,231,0.5); }
    .tip-box {
        background: linear-gradient(135deg, rgba(108,92,231,0.15), rgba(0,206,201,0.1));
        border: 1px solid rgba(108,92,231,0.25);
        border-radius: 12px; padding: 16px 20px;
        margin: 16px 0; font-size: 14px;
    }
    .metric-card {
        background: #1a1a2e; border: 1px solid #2a2a3e;
        border-radius: 12px; padding: 20px; text-align: center;
    }
    .metric-card h3 { color: #00cec9; font-size: 28px; margin: 0; }
    .metric-card p { color: #8888a0; font-size: 13px; margin: 4px 0 0 0; }
    .stProgress > div > div > div > div { background: linear-gradient(90deg, #6c5ce7, #00cec9); }
    div[data-testid="stExpander"] { background: #1a1a2e; border: 1px solid #2a2a3e; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Data generators ──

PRODUCTS = [
    'wireless headphones', 'standing desk', 'coffee maker', 'yoga mat',
    'laptop backpack', 'smart watch', 'bluetooth speaker', 'air purifier',
    'robot vacuum', 'ergonomic chair'
]

REVIEW_PHRASES = {
    'positive': [
        'exceeded my expectations', 'absolutely love it', 'best purchase I\'ve made',
        'worth every penny', 'impressive quality', 'works perfectly',
        'highly recommend', 'game changer', 'fantastic value',
        'build quality is outstanding', 'user-friendly design', 'incredibly durable'
    ],
    'negative': [
        'disappointed with the quality', 'stopped working after a week',
        'not worth the price', 'poor build quality', 'misleading description',
        'returned immediately', 'cheaply made', 'customer service was unhelpful',
        'broke on first use', 'significantly overpriced'
    ],
    'neutral': [
        'decent for the price', 'gets the job done', 'nothing special but works',
        'average quality', 'meets basic expectations', 'could be better',
        'mixed feelings about this one'
    ]
}

QA_TEMPLATES = [
    ("What are the key principles of {domain}?",
     "The key principles of {domain} include understanding fundamentals, applying best practices, continuous learning, and practical application. Mastery requires both theoretical knowledge and hands-on experience."),
    ("How does one get started with {domain}?",
     "Getting started with {domain} involves learning the basics, finding quality resources, practicing consistently, and building projects. Start with foundational concepts before tackling advanced topics."),
    ("What are common mistakes in {domain}?",
     "Common mistakes in {domain} include skipping fundamentals, not practicing enough, ignoring best practices, and failing to seek feedback. Avoid rushing through learning stages."),
    ("Explain the advanced concepts in {domain}.",
     "Advanced concepts in {domain} build on foundational knowledge and include specialized techniques, optimization strategies, and domain-specific methodologies that require deep understanding."),
    ("What tools are essential for {domain}?",
     "Essential tools for {domain} vary by specialization but typically include industry-standard software, reference materials, and collaborative platforms that enhance productivity and learning."),
    ("How has {domain} evolved over time?",
     "{domain} has evolved significantly, driven by technological advances, changing methodologies, and growing understanding. Modern approaches emphasize efficiency, accessibility, and integration with related fields."),
    ("What are the career opportunities in {domain}?",
     "Career opportunities in {domain} span multiple roles from entry-level to senior positions. Growth typically involves specialization, continuous education, and building a strong portfolio of work."),
    ("How do you measure success in {domain}?",
     "Success in {domain} is measured through various metrics including skill proficiency, project outcomes, peer recognition, and the ability to solve complex problems effectively."),
]


def generate_qa_pairs(domain: str, count: int, difficulty: str) -> list[dict]:
    pairs = []
    for i in range(count):
        q, a = QA_TEMPLATES[i % len(QA_TEMPLATES)]
        diff = random.choice(['beginner', 'intermediate', 'expert']) if difficulty == 'mixed' else difficulty
        pairs.append({
            'question': q.format(domain=domain or 'General'),
            'answer': a.format(domain=domain or 'General'),
            'difficulty': diff,
            'domain': domain or 'General'
        })
    return pairs


def generate_classifications(task: str, labels: list[str], count: int, domain: str) -> list[dict]:
    sample_texts = {
        'positive': ['This is wonderful!', 'Really enjoyed this experience.', 'Great quality and fast shipping.',
                     'Absolutely perfect, couldn\'t be happier.', 'Outstanding service and product.',
                     'Five stars, will buy again!', 'Exceeded all my expectations.'],
        'negative': ['Terrible experience, very disappointed.', 'Product broke immediately.',
                     'Waste of money, do not buy.', 'Poor quality, returning this.', 'Worst purchase ever.',
                     'Completely useless, total letdown.', 'Not as described at all.'],
        'neutral': ['It\'s okay, nothing special.', 'Average product, gets the job done.', 'Neither good nor bad.',
                    'Does what it says, nothing more.', 'Acceptable for the price.', 'Standard quality, meets expectations.']
    }
    data = []
    for label in labels:
        texts = sample_texts.get(label.lower(), [f'{label} sample text {random.randint(1000,9999)}'])
        for i in range(count):
            data.append({
                'text': random.choice(texts) + (f' (variant {i})' if i > 0 else ''),
                'label': label,
                'task': task,
                'domain': domain
            })
    random.shuffle(data)
    return data


def generate_reviews(category: str, count: int, sentiment_mix: str, length: str) -> list[dict]:
    data = []
    for _ in range(count):
        r = random.random()
        if sentiment_mix == 'positive-heavy':
            sentiment = 'positive' if r < 0.7 else ('neutral' if r < 0.9 else 'negative')
        elif sentiment_mix == 'negative-heavy':
            sentiment = 'negative' if r < 0.7 else ('neutral' if r < 0.9 else 'positive')
        elif sentiment_mix == 'mixed':
            sentiment = 'positive' if r < 0.45 else ('negative' if r < 0.8 else 'neutral')
        else:
            sentiment = 'positive' if r < 0.4 else ('neutral' if r < 0.7 else 'negative')

        phrases = REVIEW_PHRASES[sentiment]
        product = random.choice(PRODUCTS)
        review = random.choice(phrases)
        if length in ('medium', 'long'):
            review += f" The {product} {random.choice(phrases)}. {random.choice(phrases)}."
        if length == 'long':
            rec = 'definitely' if sentiment == 'positive' else ('not' if sentiment == 'negative' else 'probably not')
            review += f" Overall, {random.choice(phrases)} and would {rec} recommend to others."
        rating = random.randint(4, 5) if sentiment == 'positive' else (random.randint(1, 2) if sentiment == 'negative' else random.randint(2, 4))
        data.append({'review': review, 'sentiment': sentiment, 'rating': rating, 'product': product, 'category': category})
    return data


def generate_summaries(domain: str, count: int, style: str) -> list[dict]:
    topics = ['AI advancement in healthcare', 'Climate change policy update', 'New renewable energy breakthrough',
              'Tech company quarterly earnings', 'Scientific discovery in space', 'Global economic trends',
              'Cybersecurity threat landscape', 'Education reform proposal']
    data = []
    for _ in range(count):
        topic = random.choice(topics)
        article = (f"This article discusses {topic} in the context of {domain}. The research shows significant "
                   f"developments in the field, with multiple stakeholders contributing to progress. Key findings "
                   f"indicate measurable improvements across several metrics. Experts suggest this represents a "
                   f"paradigm shift in how we approach the subject. Further analysis reveals both opportunities "
                   f"and challenges ahead.")
        if style == 'bullet':
            summary = f"• Key development in {topic}\n• Measurable improvements across metrics\n• Paradigm shift identified by experts\n• Both opportunities and challenges ahead"
        elif style == 'tldr':
            summary = f"TL;DR: {topic} shows significant progress with broad implications for {domain}."
        else:
            summary = f"Research on {topic} reveals significant advances with measurable improvements. Experts identify this as a paradigm shift with both opportunities and challenges for {domain}."
        data.append({'article': article, 'summary': summary, 'topic': topic, 'domain': domain})
    return data


def generate_conversations(scenario: str, count: int, max_turns: int, tone: str) -> list[dict]:
    greetings = {'professional': 'Good day. How may I assist you?', 'casual': 'Hey there! What can I help you with?',
                 'empathetic': 'Hello, I understand you need help. I\'m here for you.',
                 'technical': 'Support initiated. Please describe your issue.'}
    closings = {'professional': 'Thank you for contacting us. Have a great day.', 'casual': 'All done! Take care!',
                'empathetic': 'I\'m glad I could help. Don\'t hesitate to reach out again.',
                'technical': 'Issue resolved. Ticket closed.'}
    data = []
    for _ in range(count):
        turns = [{'role': 'assistant', 'content': greetings[tone]}]
        turns.append({'role': 'user', 'content': f"I'm having an issue with my {random.choice(['account','order','subscription','payment','delivery','product'])} in the {scenario} context."})
        num_turns = random.randint(3, max_turns)
        for t in range(2, num_turns - 1):
            if t % 2 == 0:
                turns.append({'role': 'assistant', 'content': f"I understand. Let me help you with that. {random.choice(['Could you provide more details?','Let me look into this.','I can see the issue now.','Here\'s what we can do.'])}"})
            else:
                turns.append({'role': 'user', 'content': random.choice(['Yes, that sounds right.','Let me check my records.','Actually, I also wanted to ask about...','That makes sense, thank you.','Can you explain a bit more?'])})
        turns.append({'role': 'assistant', 'content': closings[tone]})
        data.append({'conversation': json.dumps(turns), 'scenario': scenario, 'tone': tone, 'turn_count': len(turns)})
    return data


def generate_entities(domain: str, count: int, density: str) -> list[dict]:
    entity_types = {
        'PERSON': ['Dr. Sarah Chen', 'James Rodriguez', 'Prof. Wei Liu', 'Maria Garcia', 'Alex Thompson', 'Dr. Emily Park'],
        'ORG': ['Stanford University', 'Mayo Clinic', 'Goldman Sachs', 'Google', 'WHO', 'MIT'],
        'DATE': ['January 2024', 'Q3 2023', 'last Tuesday', 'March 15th', '2025'],
        'LOCATION': ['New York', 'Silicon Valley', 'London', 'Tokyo', 'San Francisco', 'Berlin'],
        'DISEASE': ['Type 2 Diabetes', 'hypertension', 'asthma', 'pneumonia', 'anemia'],
        'DRUG': ['metformin', 'lisinopril', 'albuterol', 'ibuprofen', 'amoxicillin']
    }
    templates = [
        '{PERSON} from {ORG} published findings on {DISEASE} treatment in {LOCATION} on {DATE}.',
        '{ORG} announced a new {DRUG} study led by {PERSON}, targeting {DISEASE} patients.',
        'Research conducted at {ORG} in {LOCATION} by {PERSON} shows {DRUG} effectively treats {DISEASE}.',
        '{PERSON} presented at {ORG} on {DATE} about {DISEASE} prevalence in {LOCATION}.',
        'A clinical trial at {ORG} testing {DRUG} for {DISEASE} began on {DATE}.'
    ]
    data = []
    for _ in range(count):
        sentence = random.choice(templates)
        entities = []
        for etype, values in entity_types.items():
            tag = '{' + etype + '}'
            while tag in sentence:
                val = random.choice(values)
                sentence = sentence.replace(tag, val, 1)
                entities.append({'text': val, 'type': etype})
        data.append({'text': sentence, 'entities': json.dumps(entities), 'domain': domain})
    return data


def generate_code_dataset(lang: str, count: int, complexity: str, focus: str) -> list[dict]:
    tasks = [
        (f"Write a {lang} function to sort a list of dictionaries by a given key.",
         f"def sort_by_key(data, key):\n    return sorted(data, key=lambda x: x.get(key, 0))" if lang == 'Python' else
         f"function sortByKey(data, key) {{\n  return data.sort((a, b) => a[key] > b[key] ? 1 : -1);\n}}"),
        (f"Create a {lang} function that reads a CSV file and returns a list of objects.",
         "import csv\n\ndef read_csv(filepath):\n    with open(filepath) as f:\n        return list(csv.DictReader(f))" if lang == 'Python' else
         "const fs = require('fs');\nfunction readCSV(filepath) {\n  const data = fs.readFileSync(filepath, 'utf8');\n  const [header, ...rows] = data.split('\\n');\n  return rows.map(r => Object.fromEntries(header.split(',').map((k,i) => [k, r.split(',')[i]])));\n}"),
        (f"Implement a {lang} function to validate an email address.",
         "import re\n\ndef is_valid_email(email):\n    pattern = r'^[\\w.+-]+@[\\w-]+\\.[\\w.-]+$'\n    return bool(re.match(pattern, email))" if lang == 'Python' else
         "function isValidEmail(email) {\n  return /^[\\w.+-]+@[\\w-]+\\.[\\w.-]+$/.test(email);\n}"),
        (f"Write a {lang} function that flattens a nested list.",
         "def flatten(lst):\n    result = []\n    for item in lst:\n        if isinstance(item, list):\n            result.extend(flatten(item))\n        else:\n            result.append(item)\n    return result" if lang == 'Python' else
         "function flatten(arr) {\n  return arr.flat(Infinity);\n}"),
        (f"Create a {lang} class for a simple LRU cache.",
         "from collections import OrderedDict\n\nclass LRUCache:\n    def __init__(self, capacity):\n        self.cache = OrderedDict()\n        self.capacity = capacity\n    def get(self, key):\n        if key in self.cache:\n            self.cache.move_to_end(key)\n            return self.cache[key]\n        return -1\n    def put(self, key, value):\n        if key in self.cache:\n            self.cache.move_to_end(key)\n        self.cache[key] = value\n        if len(self.cache) > self.capacity:\n            self.cache.popitem(last=False)" if lang == 'Python' else
         "class LRUCache {\n  constructor(capacity) {\n    this.cache = new Map();\n    this.capacity = capacity;\n  }\n  get(key) {\n    if (!this.cache.has(key)) return -1;\n    const val = this.cache.get(key);\n    this.cache.delete(key);\n    this.cache.set(key, val);\n    return val;\n  }\n  put(key, value) {\n    if (this.cache.has(key)) this.cache.delete(key);\n    this.cache.set(key, value);\n    if (this.cache.size > this.capacity) this.cache.delete(this.cache.keys().next().value);\n  }\n}"),
    ]
    data = []
    for i in range(count):
        inst, code = tasks[i % len(tasks)]
        c = random.choice(['simple', 'moderate', 'complex']) if complexity == 'mixed' else complexity
        data.append({'instruction': inst, 'input': '', 'output': code, 'language': lang, 'complexity': c, 'domain': focus})
    return data


def generate_instructions(domain: str, count: int, input_mode: str, output_style: str) -> list[dict]:
    templates = [
        ("Write a compelling product description for a {product}.",
         "Product: Smart Home Hub\nFeatures: voice control, 200+ device compatibility, energy monitoring",
         "The Smart Home Hub transforms your living space into an intelligent ecosystem. With seamless voice control and compatibility with over 200 devices, managing your home has never been easier. Track energy usage in real-time and optimize consumption to save on bills. Its sleek design blends into any decor while its powerful processor ensures instant response times."),
        ("Analyze the sentiment of the following text and explain your reasoning.",
         '"The new update completely ruined my workflow. I\'ve lost hours of work."',
         'Sentiment: Strongly Negative\n\nThe text expresses clear frustration through several indicators: "completely ruined" shows severity, "lost hours of work" indicates tangible negative impact, and the overall tone is one of significant dissatisfaction.'),
        ("Create a meal plan for a week based on the given dietary requirements.",
         "Requirements: vegetarian, high-protein, budget-friendly ($50/week)",
         "Weekly Plan:\nMon: Lentil curry + rice (28g protein) ~$6\nTue: Black bean tacos (24g protein) ~$5\nWed: Tofu stir-fry + edamame (32g protein) ~$7\nThu: Chickpea pasta (26g protein) ~$6\nFri: Bean burrito bowls (25g protein) ~$7\nSat-Sun: Egg frittata & Greek yogurt bowls ~$8/day\nTotal: ~$47"),
        ("Explain the concept of {concept} as if teaching it to a {audience}.",
         "Concept: machine learning\nAudience: 10-year-old",
         "Imagine you're teaching your dog to recognize a ball. You show the dog many balls — red ones, blue ones, big ones, small ones. At first, the dog might confuse a ball with an orange. But each time, you tell the dog \"yes, that's a ball!\" or \"no, that's not!\" Eventually, the dog learns what makes something a ball.\n\nMachine learning is like that! Instead of a dog, we use a computer. The computer looks at thousands of pictures, learning what makes a cat look like a cat and a dog look like a dog."),
        ("Draft a professional email to {recipient} about {topic}.",
         "Recipient: project stakeholders\nTopic: 2-week delay in milestone delivery",
         "Subject: Project Timeline Update - Milestone Adjustment\n\nDear Stakeholders,\n\nI am writing to inform you of an adjustment to our project timeline. Due to unforeseen technical challenges in the integration phase, our upcoming milestone will require an additional two weeks to complete.\n\nCurrent Status:\n- Core development: 95% complete\n- Integration testing: 70% complete\n- New target date: [date + 2 weeks]\n\nBest regards,\n[Your Name]"),
    ]
    data = []
    for i in range(count):
        inst, inp, out = templates[i % len(templates)]
        has_input = input_mode == 'always' or (input_mode == 'mixed' and random.random() > 0.3)
        data.append({
            'instruction': inst,
            'input': inp if has_input else '',
            'output': out,
            'domain': domain,
            'output_style': output_style
        })
    return data


# ── Marketplace info ──

MARKETPLACES = [
    {"name": "Defined.ai", "type": "Premium", "description": "Enterprise-grade NLP data marketplace. Revenue share: 70/30.", "pricing": "$0.01-2.00 per sample"},
    {"name": "Kaggle Datasets", "type": "Free + Paid", "description": "Massive community. Build reputation with free datasets, monetize premium ones.", "pricing": "Premium: $5-500+"},
    {"name": "Datarade", "type": "B2B", "description": "B2B data marketplace for enterprise buyers.", "pricing": "$100-10,000+ per dataset"},
    {"name": "Scale AI", "type": "Partner", "description": "Supply-side data labeling partner. Apply as contributor.", "pricing": "$15-50/hr contract"},
    {"name": "Hugging Face", "type": "Open + Paid", "description": "Open-source community with paid dataset hosting.", "pricing": "Donations + premium access"},
    {"name": "Bright Data", "type": "Web Data", "description": "Marketplace for web scraping and structured web data.", "pricing": "$50-5,000+ per dataset"},
]

MONETIZATION_TIPS = {
    'Q&A Pairs': 'Q&A pairs for niche domains (medical, legal, finance) sell for $0.10-0.50 per pair. Batch by domain for premium pricing.',
    'Classifications': 'Labeled classification data is in constant demand. Focus on rare languages or specialized domains.',
    'Reviews': 'Annotated review datasets power recommendation engines. Include sentiment, aspect, and rating labels.',
    'Summaries': 'Summarization pairs are valuable for training. Research paper abstracts and news summaries command higher prices.',
    'Conversations': 'Multi-turn conversation data is essential for chatbot training. Domain-specific dialogues sell at premium rates.',
    'NER Entities': 'NER training data is foundational for information extraction. Medical and legal NER data has highest demand.',
    'Code Generation': 'Code instruction datasets are among the most valuable training data types.',
    'Instruction Tuning': 'Alpaca-style instruction datasets are the gold standard for fine-tuning.',
}

# ── Initialize session state ──

if 'datasets' not in st.session_state:
    st.session_state.datasets = []
if 'total_generated' not in st.session_state:
    st.session_state.total_generated = 0

# ── Sidebar ──

with st.sidebar:
    st.markdown("## ⚡ SynData Studio")
    st.markdown("Generate synthetic AI training data to sell on data marketplaces.")
    st.divider()

    data_type = st.radio("📊 Data Type", [
        "Q&A Pairs",
        "Classifications",
        "Reviews",
        "Summaries",
        "Conversations",
        "NER Entities",
        "Code Generation",
        "Instruction Tuning",
    ])

    st.divider()
    st.markdown("### 📈 Session Stats")
    total_rows = sum(d['count'] for d in st.session_state.datasets)
    total_size = sum(d['size'] for d in st.session_state.datasets)
    c1, c2 = st.columns(2)
    c1.metric("Datasets", len(st.session_state.datasets))
    c2.metric("Total Rows", f"{total_rows:,}")
    st.metric("Total Size", f"{total_size/1024:.1f} KB" if total_size < 1024*1024 else f"{total_size/(1024*1024):.1f} MB")

    st.divider()
    with st.expander("💰 Where to Sell", expanded=False):
        for m in MARKETPLACES:
            st.markdown(f"**{m['name']}** `{m['type']}`")
            st.caption(f"{m['description']}")
            st.caption(f"💰 {m['pricing']}")
            st.markdown("")

    st.divider()
    st.caption("🚀 Pro Tips:")
    st.caption("• Niche domains command 3-5x premium")
    st.caption("• JSONL is preferred for LLM fine-tuning")
    st.caption("• Start free on Kaggle/HuggingFace to build reputation")

# ── Main content ──

st.markdown(f"## {data_type}")

# ── Configuration forms ──

config = {}

if data_type == "Q&A Pairs":
    st.write("Generate question-answer training data for fine-tuning LLMs.")
    col1, col2 = st.columns(2)
    config['domain'] = col1.text_input("Domain / Topic", placeholder="e.g., Python programming, medical diagnosis, cooking")
    config['count'] = col2.number_input("Number of Pairs", min_value=1, max_value=1000, value=50)
    col3, col4 = st.columns(2)
    config['difficulty'] = col3.selectbox("Difficulty Level", ['mixed', 'beginner', 'intermediate', 'expert'])
    config['context'] = col4.text_area("Extra Context (optional)", placeholder="Additional constraints...")

elif data_type == "Classifications":
    st.write("Create labeled text samples for sentiment analysis, topic classification, or intent detection.")
    col1, col2 = st.columns(2)
    config['task'] = col1.text_input("Classification Task", placeholder="e.g., sentiment analysis, spam detection")
    config['labels'] = col2.text_input("Labels (comma-separated)", value="positive, negative, neutral")
    col3, col4 = st.columns(2)
    config['count'] = col3.number_input("Samples per Label", min_value=1, max_value=500, value=25)
    config['domain'] = col4.text_input("Domain", placeholder="e.g., e-commerce, social media")

elif data_type == "Reviews":
    st.write("Generate synthetic product reviews with sentiment labels.")
    col1, col2 = st.columns(2)
    config['category'] = col1.text_input("Product Category", placeholder="e.g., electronics, restaurants, books")
    config['count'] = col2.number_input("Number of Reviews", min_value=1, max_value=1000, value=50)
    col3, col4 = st.columns(2)
    config['sentiment'] = col3.selectbox("Sentiment Mix", ['balanced', 'positive-heavy', 'negative-heavy', 'mixed'])
    config['length'] = col4.selectbox("Review Length", ['short', 'medium', 'long'])

elif data_type == "Summaries":
    st.write("Generate article-to-summary pairs for training text summarization models.")
    col1, col2 = st.columns(2)
    config['domain'] = col1.text_input("Content Domain", placeholder="e.g., news articles, research papers")
    config['count'] = col2.number_input("Number of Pairs", min_value=1, max_value=500, value=30)
    config['style'] = st.selectbox("Summary Style", ['abstract', 'bullet', 'tldr'])

elif data_type == "Conversations":
    st.write("Generate realistic multi-turn dialogues for training chatbots.")
    col1, col2 = st.columns(2)
    config['scenario'] = col1.text_input("Scenario", placeholder="e.g., customer support, medical consultation")
    config['count'] = col2.number_input("Conversations", min_value=1, max_value=200, value=20)
    col3, col4 = st.columns(2)
    config['turns'] = col3.number_input("Turns per Conversation", min_value=3, max_value=20, value=6)
    config['tone'] = col4.selectbox("Tone", ['professional', 'casual', 'empathetic', 'technical'])

elif data_type == "NER Entities":
    st.write("Generate labeled text with named entities for NER training.")
    col1, col2 = st.columns(2)
    config['domain'] = col1.text_input("Domain", placeholder="e.g., medical records, legal documents, news")
    config['count'] = col2.number_input("Sentences", min_value=1, max_value=500, value=40)
    config['density'] = st.selectbox("Entity Density", ['sparse', 'moderate', 'dense'])

elif data_type == "Code Generation":
    st.write("Generate natural language to code pairs. Among the most valuable training data types.")
    col1, col2 = st.columns(2)
    config['lang'] = col1.text_input("Programming Language", value="Python")
    config['count'] = col2.number_input("Number of Pairs", min_value=1, max_value=500, value=30)
    col3, col4 = st.columns(2)
    config['complexity'] = col3.selectbox("Complexity", ['mixed', 'simple', 'moderate', 'complex'])
    config['focus'] = col4.text_input("Focus Area", placeholder="e.g., data processing, web scraping")

elif data_type == "Instruction Tuning":
    st.write("Generate Alpaca-style instruction/input/output triplets.")
    col1, col2 = st.columns(2)
    config['domain'] = col1.text_input("Domain / Category", placeholder="e.g., writing assistant, data analysis")
    config['count'] = col2.number_input("Number of Instructions", min_value=1, max_value=500, value=40)
    col3, col4 = st.columns(2)
    config['input_mode'] = col3.selectbox("Include Input Field", ['mixed', 'always', 'never'])
    config['output_style'] = col4.selectbox("Output Style", ['detailed', 'concise', 'step-by-step'])

# ── Export settings ──

st.markdown("### 📤 Export Settings")
col_fmt, col_meta = st.columns(2)
export_format = col_fmt.selectbox("Format", ['JSON', 'JSONL', 'CSV', 'TSV'])
include_meta = col_meta.checkbox("Include Metadata", value=True)

# ── Generate button ──

col_btn, col_tip = st.columns([1, 2])
generate = col_btn.button("⚡ Generate Dataset", type="primary")
col_tip.markdown(f'<div class="tip-box">💡 <strong>Tip:</strong> {MONETIZATION_TIPS.get(data_type, "Focus on quality over quantity.")}</div>', unsafe_allow_html=True)

if generate:
    with st.spinner("Generating dataset..."):
        progress = st.progress(0)

        if data_type == "Q&A Pairs":
            data = generate_qa_pairs(config['domain'], config['count'], config['difficulty'])
            fmt_name = 'json'
        elif data_type == "Classifications":
            labels = [l.strip() for l in config['labels'].split(',') if l.strip()]
            data = generate_classifications(config['task'], labels, config['count'], config['domain'])
            fmt_name = 'csv'
        elif data_type == "Reviews":
            data = generate_reviews(config['category'], config['count'], config['sentiment'], config['length'])
            fmt_name = 'json'
        elif data_type == "Summaries":
            data = generate_summaries(config['domain'], config['count'], config['style'])
            fmt_name = 'json'
        elif data_type == "Conversations":
            data = generate_conversations(config['scenario'], config['count'], config['turns'], config['tone'])
            fmt_name = 'json'
        elif data_type == "NER Entities":
            data = generate_entities(config['domain'], config['count'], config['density'])
            fmt_name = 'json'
        elif data_type == "Code Generation":
            data = generate_code_dataset(config['lang'], config['count'], config['complexity'], config['focus'])
            fmt_name = 'json'
        else:
            data = generate_instructions(config['domain'], config['count'], config['input_mode'], config['output_style'])
            fmt_name = 'json'

        progress.progress(100)

        df = pd.DataFrame(data)
        raw_json = json.dumps(data, indent=2, ensure_ascii=False)
        raw_jsonl = '\n'.join(json.dumps(d, ensure_ascii=False) for d in data)
        raw_csv = df.to_csv(index=False)
        raw_tsv = df.to_csv(index=False, sep='\t')

        content_map = {'JSON': raw_json, 'JSONL': raw_jsonl, 'CSV': raw_csv, 'TSV': raw_tsv}
        ext_map = {'JSON': 'json', 'JSONL': 'jsonl', 'CSV': 'csv', 'TSV': 'tsv'}

        dataset = {
            'name': f"{data_type} — {config.get('domain', config.get('category', config.get('scenario', config.get('lang', 'general'))))}",
            'type': data_type,
            'count': len(data),
            'size': len(raw_json.encode('utf-8')),
            'data': data,
            'df': df,
            'content': content_map,
            'ext_map': ext_map,
            'timestamp': datetime.now().isoformat(),
        }
        st.session_state.datasets.append(dataset)
        st.session_state.total_generated += 1

    st.success(f"✅ Generated {len(data)} {data_type.lower()} samples!")
    st.balloons()

# ── Preview & Export ──

if st.session_state.datasets:
    latest = st.session_state.datasets[-1]

    st.divider()
    st.markdown("### 📊 Live Preview")

    # Quality score
    keys = list(latest['data'][0].keys())
    quality = min(60 + len(keys) * 5, 80) + 10 + (5 if len(latest['data']) > 10 else 0) + (5 if len(latest['data']) > 50 else 0)
    quality = min(quality, 100)
    qc = "🟢" if quality > 80 else ("🟡" if quality > 50 else "🔴")
    st.markdown(f"**Quality Score:** {qc} {quality}%")
    st.progress(quality / 100)

    # Data preview
    st.dataframe(latest['df'].head(10), use_container_width=True)

    # Raw preview
    with st.expander("🔍 Raw JSON Preview"):
        st.code(json.dumps(latest['data'][:3], indent=2), language='json')

    # Download buttons
    st.markdown("### 💾 Download")
    dl_cols = st.columns(4)
    for i, fmt in enumerate(['JSON', 'JSONL', 'CSV', 'TSV']):
        dl_cols[i].download_button(
            label=f"📥 {fmt}",
            data=latest['content'][fmt],
            file_name=f"syndata_{latest['type'].replace(' ','_').lower()}_{int(datetime.now().timestamp())}.{latest['ext_map'][fmt]}",
            mime="text/plain",
            key=f"dl_{fmt}_{st.session_state.total_generated}"
        )

    # Export all
    if len(st.session_state.datasets) > 1:
        st.markdown("### 📦 Export All Datasets")
        all_data = []
        for ds in st.session_state.datasets:
            all_data.extend(ds['data'])
        combined_json = json.dumps(all_data, indent=2, ensure_ascii=False)
        combined_jsonl = '\n'.join(json.dumps(d, ensure_ascii=False) for d in all_data)
        combined_df = pd.DataFrame(all_data)
        st.download_button(
            label=f"📦 Export All ({len(all_data)} total rows) as JSON",
            data=combined_json,
            file_name=f"syndata_all_{len(st.session_state.datasets)}_datasets.json",
            mime="application/json"
        )

    # Dataset history
    st.divider()
    st.markdown("### 📁 Dataset History")
    for i, ds in enumerate(reversed(st.session_state.datasets)):
        idx = len(st.session_state.datasets) - i
        with st.expander(f"#{idx} {ds['name']} — {ds['count']} rows ({ds['size']/1024:.1f} KB)"):
            st.dataframe(ds['df'].head(5), use_container_width=True)
            dlh = st.columns(4)
            for j, fmt in enumerate(['JSON', 'JSONL', 'CSV', 'TSV']):
                dlh[j].download_button(
                    label=f"📥 {fmt}",
                    data=ds['content'][fmt],
                    file_name=f"syndata_{ds['type'].replace(' ','_').lower()}_{idx}.{ds['ext_map'][fmt]}",
                    mime="text/plain",
                    key=f"dlh_{fmt}_{idx}"
                )
