import requests
from bs4 import BeautifulSoup
import json
import os
import time
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import threading
import collections # Para collections.deque
from concurrent.futures import ThreadPoolExecutor, as_completed # Adicionado

# --- Constantes e Globais para Headers ---
BASE_URL_CAMBRIDGE = "https://dictionary.cambridge.org"
REQUEST_BASE_URL_DICTIONARY = "https://dictionary.cambridge.org/dictionary/english/"
DATA_FILE = "cambridge_dictionary_data.json"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
    # Safari no macOS (versão mais recente do OS/Safari)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    
    # Microsoft Edge no Windows 10 (baseado no Chromium)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.2535.51", # Versão do Edge pode variar
    
    # Chrome no Android (Mobile - Exemplo com Pixel)
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    
    # Safari no iPhone (iOS)
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    
    # Firefox no Linux (Ubuntu)
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
    
    # Opera no Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 OPR/110.0.0.0", # Versão do Opera (OPR) pode variar

    # Chrome no Windows 11 (versão ligeiramente mais nova do Chrome)
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",

    # Firefox no Android (Mobile)
    "Mozilla/5.0 (Android 13; Mobile; rv:126.0) Gecko/126.0 Firefox/126.0",
    
    # Chrome no ChromeOS
    "Mozilla/5.0 (X11; CrOS x86_64 15662.76.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36", # Versão do ChromeOS pode variar

    # Chrome no macOS (versão mais recente do OS e Chrome ligeiramente mais novo)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
]

# Para usar em conjunto com os seus, você pode concatenar as listas:
# TODOS_USER_AGENTS = USER_AGENTS + USER_AGENTS_ADICIONAIS
# print(TODOS_USER_AGENTS)

current_user_agent_index = 0 # Índice do User-Agent atual
ua_lock = threading.Lock() # Lock para proteger o acesso ao User-Agent e contador de erro

REQUEST_HEADERS = { # Estes são os headers base, o User-Agent será atualizado dinamicamente
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

MAX_CONSECUTIVE_FETCH_ERRORS_BEFORE_UA_SWITCH = 3
shared_fetch_error_counter = [0] # Lista para ser mutável

list_initial_words = [
"riga",
"be-able",
"non-fiction",
"doctor",
"justi",
"stuffed-toy",
"next",
"declaration",
"try",
"newspaper",
"neck-brace",
"leal",
"trimaran",
"cynical",
"fennel",
"nachos",
"package",
"order",
"pounds",
"satellite",
"rely-on",
"bedrooms",
"acrylic-paint",
"effects",
"shaving-foam",
"stand",
"plans",
"ona",
"exams",
"guava-tree",
"apple-tree",
"leasure",
"orgal",
"-watt",
"meto",
"cake",
"lights",
"to-survive",
"portugal",
"to-make-a-mistake",
"gra",
"read",
"engagement",
"rice",
"ninety",
"sixty-seven",
"smoothie",
"pincers",
"shou",
"deck's",
"to-give",
"robot",
"roly-poly",
"pressures",
"to-illuminate",
"started",
"parenis",
"listen",
"browsing",
"wind's",
"laman",
"fourteen",
"occultism",
"melody",
"beach-umbrella",
"sea's",
"cardiologist",
"ethnomusic",
"come",
"round-trip",
"smirnov",
"daughter-in-law",
"well-known",
"tall",
"cookery",
"software",
"to-define",
"gyrfalcon",
"battery's",
"tulip",
"xperienced",
"good",
"steakhouse",
"check-up",
"potentially",
"exclamation",
"ina",
"vacuum-cleaner",
"internet's",
"been",
"banon",
"pasta",
"flirt",
"sharpener",
"vhat",
"ten-minute",
"to-cry",
"dustpan",
"mother's",
"bread",
"two",
"exchan",
"hard-working",
"kilogram",
"indirect",
"pediatrician",
"ticket-office",
"dance",
"one-bedroom",
"services",
"to-turn-on",
"hairspray",
"to-sterilize",
"apology",
"fifty-fir",
"t-shirts",
"hina",
"unusual",
"waders",
"seventy-seven",
"screen's",
"phonetics",
"buenos",
"agriculturist",
"sometime",
"color",
"fishmonger's",
"right-on-time",
"pass",
"eighty-six",
"doesnt",
"dry-clean",
"garcia",
"waterskiing",
"understood",
"deaf-mute",
"enough",
"make-up",
"what-whatever-says-goes",
"assist",
"statement",
"number",
"one",
"alter",
"sugar",
"chocolate-bar",
"frank",
"kmh",
"to-educate",
"e-ticket",
"sun's",
"where's",
"not-the-done-thing",
"solid-shape",
"four-year-old",
"subtitles",
"job",
"plough-through",
"to-joke",
"half-hour",
"duty-free",
"ticke",
"sloth",
"insecticide",
"e-mail",
"fits",
"wang",
"put-a-pin-in",
"tone",
"daniel's",
"old-fashioned",
"slippers",
"firefighter",
"yes",
"room-key",
"feijo",
"make-waves",
"eighty-five",
"asted",
"child's",
"palm-oil",
"ementary",
"wolves",
"leisure-time",
"remote-control",
"painkiller",
"sush",
"frenc",
"migraine",
"card",
"majo",
"children",
"olive-tree",
"irrency",
"details",
"sixty",
"sucking-diesel",
"click",
"heisina",
"moment",
"perfumery",
"checking",
"roller-coaster",
"to-insult",
"horses",
"to-penalise",
"holiday-brochure",
"eee",
"go-out-like-a-light",
"self-confidence",
"foreleg",
"nail-polish-remover",
"bug",
"seventy-two",
"eighteen",
"valentine",
"here's",
"night",
"alr",
"thirty-three",
"vhen",
"camellia",
"ninety-three",
"alist",
"stati",
"french",
"to-salt",
"agouti",
"user-friendly",
"pistachio-tree",
"forty-five",
"to-suggest",
"wi-fri",
"directions",
"expenses",
"seu",
"sto",
"mais",
"tottenham",
"consist",
"fishing-reel",
"ten",
"press",
"apricot-tree",
"jhat",
"koi-carp",
"museum's",
"red-eye",
"jectic",
"tens",
"pomegranate-tree",
"car's",
"plastic-bag",
"didnt",
"lector",
"breakfast's",
"edical",
"smith",
"lights-switch",
"juice",
"carry-on",
"stamps",
"charing",
"traffic-sign",
"rooms",
"compartment",
"butter",
"december",
"filip",
"laptop's",
"fligil",
"pleasant",
"cardigan-sweater",
"good-looking",
"nushrooms",
"wouldn-t-know-if-fell-over-one-it",
"dental-implant",
"hereis",
"maid-service",
"merry-go-round",
"so-so",
"forty-seven",
"sixty-eight",
"four-ber",
"renta",
"self-portrait",
"mutism",
"all-day",
"results",
"facilities",
"thirty-two",
"envelope",
"convenient",
"could-use",
"npeti",
"five-minute",
"eighty-one",
"eyesight's",
"three-dimensional",
"twenty",
"stories",
"seventy-sixth",
"coat",
"pay",
"tastes",
"unstable",
"two-door",
"costs",
"firestarter",
"lufthansa",
"textile",
"lucy",
"ally",
"ninety-nine",
"them-and-us",
"upermarket",
"anna",
"forty-two",
"great-granddaught-er",
"mass-media",
"director",
"stamp-collecting",
"equator",
"heavens-open",
"thongs",
"eighty-four",
"herring",
"flock-of-sheep",
"rise-to-the-occasion-challenge",
"ineed",
"cleaning",
"half-year",
"great-grandfather",
"beard",
"computer-literate",
"to-wash",
"straightforwarc",
"theme-park",
"even-number",
"days",
"perm",
"twenty-six",
"god",
"peach-tree",
"be-green-with-envy",
"building's",
"cost",
"on-the-dot",
"schc",
"moonstone",
"oss-couni-skiing",
"fty-four",
"spanish",
"pressure",
"mango-tree",
"to-slip",
"criss-cross-applesauce",
"to-rot",
"to-hospitalize",
"toa",
"forty-four",
"packa",
"wider",
"tour-bus",
"position's",
"to-relax",
"teeter-totter",
"triple-decker",
"sarah",
"dill",
"worth",
"hind-leg",
"tell",
"sheepherder",
"worry",
"makeup-remover",
"party",
"cashew-tree",
"steps",
"octopus",
"bad",
"second-hand-shop",
"self-employed",
"japanese",
"today's",
"twenty-three",
"pass-out",
"wi-fi",
"read-my-lips",
"ninety-six",
"from-a-to-b",
"intere",
"lemon-tree",
"you",
"routine",
"produced",
"quince-tree",
"wings",
"weather",
"misérables’",
"druggist",
"eighty-two",
"roses",
"likes",
"your-guess-is-as-good-as-mine",
"thyroid-gland",
"month's",
"clerk",
"fitness",
"eighty-eight",
"avocado-tree",
"honest",
"carry-on-baggage",
"wednesday",
"hotel",
"seat",
"four",
"tropical-fruit",
"nothing",
"obedience",
"bar-counter",
"eight",
"jia",
"fast-moving",
"emma",
"beef",
"cooked",
"flower-shop",
"cherry-tree",
"rates",
"week-after-week",
"suitcases",
"forty-third",
"fall-asleep",
"baskets",
"to-regret",
"passport",
"vhich",
"beena",
"buildin",
"death",
"ninety-five",
"epistolary-novel",
"change",
"store-window",
"pear-tree",
"car-rental",
"fty-one",
"young",
"attention",
"manicure",
"police-sketch",
"tax-free",
"reality",
"not-be-beyond-the-wit-of-man",
"ardon",
"best",
"contacts",
"forest",
"tonometer",
"careful",
"jidn'tt",
"volleyballer",
"checkbook",
"ant-colony",
"onian-ukrainian",
"again",
"cauliflow",
"madam",
"rthrit",
"short",
"to-curl",
"key",
"street-light",
"pedestrian-zone",
"dishwashing",
"lessons",
"cuckoo",
"emily",
"grapes",
"hebrew-speaking",
"to-misspell",
"battery",
"ninety-seven",
"kuala",
"sale",
"kangaroo",
"discussion",
"exas",
"tide",
"non-alcoholic",
"drinks",
"herd-of-horses",
"furniture-polish",
"blackberry",
"hyacinth",
"processado",
"to-replant",
"oclock",
"tou",
"things-that-go-bump-in-the-night",
"character",
"dominoes",
"stamp",
"non-human",
"regards",
"conveniently",
"cough",
"nameexample",
"opinion",
"longer",
"program",
"fearful",
"custom-made",
"to-diagnose",
"understal",
"yet",
"adoptive-parents",
"slip-away",
"dishwashing-liquid",
"marmalade",
"today",
"three",
"stop",
"turn-upside-down",
"mumble",
"eaglet",
"croissant",
"oakwood",
"comedy",
"pianist",
"possível",
"long-term",
"reading",
"xylophone",
"to-scroll",
"muscles",
"stop",
"lipstick",
"feel",
"deepest",
"to-impose",
"curiosity-killed-the-cat",
"stand-out",
"distant",
"nail-clippers",
"there",
"ticket",
"accepts",
"refusal",
"ilizat",
"argentina",
"psoriasis",
"filled",
"coffee",
"point",
"year",
"aracl",
"excessively",
"insuran",
"pectoral",
"rely",
"clearly",
"ould",
"concern",
"right",
"seventy-eight",
"money",
"seventy-four",
"leal",
"seventy-one",
"fifty-six",
"greatest",
"jualifications",
"helpful",
"casserole-dish",
"boiled",
"to-eat",
"somewhere-along-the-line",
"hailstone",
"lili",
"thirty-eight",
"emails",
"moonrise",
"eighty-seven",
"sixty-nine",
"thirty-six",
"gel",
"twenty-first",
"reefs",
"team",
"pressure's",
"literary-genre",
"locks",
"pluto",
"private-jet",
"tui",
"oranges",
"golf",
"to-attach",
"two-story",
"to-clean",
"offe",
"hundredth",
"credit-card",
"to-milk",
"suffice-it-to-say",
"dry-milk",
"horseback",
"swallow's",
"to-go-down",
"therapy",
"to-make",
"appetizers",
"pull-off",
"organized",
"part-time",
"out-of-sight",
"night-time",
"to-tell",
"wor",
"wake-up",
"disobedience",
"eyeshadow",
"addict",
"cold-blooded",
"amethyst",
"askir",
"chicken-coop",
"blac",
"close-enough-for-government-work",
"club",
"two-bedroom",
"embarrass",
"flock-of-birds",
"witch",
"science-fiction-film",
"to-apologize",
"twenty-eight",
"temperatur",
"thirty-five",
"control",
"mino",
"fine",
"menu",
"arthquak",
"twenty-seven",
"mother-in-law",
"igag",
"twenty-nine",
"great-granddaught",
"to-lock",
"mascara",
"learned",
"digestion",
"forty-nine",
"multilateral",
"lik",
"sister-in-law",
"baku",
"arnica",
"triplets",
"possibility",
"to-save",
"channel",
"chips",
"grapefruit-tree",
"shop",
"naked",
"builder",
"path",
"to-satisfy",
"previously",
"to-install",
"duc",
"extraordinary",
"seventy-nine",
"dumb-bell",
"theater-program",
"questions",
"strong",
"maced",
"ve'd",
"child-seat",
"sit-up",
"champignon",
"that-will-do",
"boomerang",
"push-up",
"representative",
"reading-room",
"dani",
"corporation",
"hockey-player",
"orward",
"fried-egg",
"home",
"belt",
"following",
"north",
"slow-moving",
"vegetarian",
"ver",
"ground's",
"tend-to",
"thirty-second",
"hot-air-balloon",
"stoplights",
"hot-air",
"to-bathe",
"points",
"doctors",
"devices",
"tv-show",
"pictures",
"to-travel",
"to-retire",
"room-for-improvement",
"plums",
"long-lived",
"coloured-pencil",
"rambla",
"plants",
"races",
"june",
"neil",
"to-snore",
"double-decker",
"gravy",
"fifty-four",
"lines",
"fifty-tw",
"sixty-fifth",
"crying",
"fishing-permit",
"bed",
"communicat",
"lond",
"second-hand",
"forty-one",
"asia",
"cab's",
"to-test",
"to-discover",
"envelopes",
"porch-light",
"employee",
"icelandic",
"laura",
"defenseless",
"to-fall-in-love",
"ninety-eighth",
"knock-spots-off",
"when's",
"known",
"straighten",
"daughter",
"kick-against-the-pricks",
"sixty-five",
"thirty-four",
"goodnight",
"rubber-ring",
"view",
"louder",
"time",
"phone",
"eighty",
"iistoric",
"co-workers",
"isured",
"tea",
"seventy-five",
"slices",
"thigh",
"for",
"yens",
"signed",
"crabs",
"seventy-three",
"to-recover",
"copier's",
"courses",
"prompily",
"rápido",
"touch-base",
"sights",
"to-light-a-fire",
"e-mail-address",
"lhave",
"ice-cold",
"be-in-one-of-moods",
"billfo",
"personally",
"lukas",
"balance",
"seven",
"stars",
"ninety-eight",
"like",
"epartment",
"place",
"to-pitch-a-tent",
"nightclubs",
"asitate",
"colour-outside-the-lines",
"chal",
"repellent",
"light-the-lamp",
"father-in-law",
"jhat's",
"eyebrow-pencil",
"to-be-born",
"oceanographer",
"cheese",
"hallucination",
"touristic-attractions",
"pack-of-wolves",
"tube",
"cotton-pad",
"approve",
"truffle",
"yours",
"younger",
"epic-poem",
"hinese-speakir",
"hand-woven",
"fifty-eight",
"twin-room",
"all-inclusive",
"hat's",
"can",
"israel",
"seventy",
"speakers",
"fifteen",
"name",
"eighty-three",
"years",
"sandwich",
"headband",
"to-pasture",
"great-grandson",
"wishes",
"nhat",
"start-a-new-life",
"six",
"seventy-six",
"like-a-boss",
"insect-repellent",
"urgent",
"powder",
"sent",
"medical-condition",
"trackless-trolley",
"panties",
"gearbox",
"permission",
"time's",
"time's-up",
"same",
"dry-cleaned",
"son-in-law",
"drive-off",
"x-ray",
"customer-service",
"to-go-up",
"states",
"nine",
"waters",
"appy",
"served",
"fluorite",
"trial",
"words",
"president",
"ebbly",
"mile-off",
"milk",
"this",
"forty-three",
"orange-tree",
"les",
"rhinoceros",
"context",
"cords",
"ice-climbing",
"almond-tree",
"check-in",
"sixty-six",
"yeah",
"le'd",
"unpotable",
"middle-aged",
"train's",
"hair",
"to-select",
"eighty-nine",
"thanks",
"blow-dry",
"wedding",
"together",
"volume",
"fifty-three",
"soup",
"ninety-one",
"salt",
"one-hundred-thousand",
"cockroach",
"please",
"fat-free",
"here",
"t-shirt",
"later",
"igo",
"more",
"make-scarce",
"pedido",
"lumpur",
"sixty-one",
"tamarind-tree",
"quarter-final",
"correct",
"canlusea",
"to-give-up",
"ten-thousand",
"dessert",
"time-is-ripe",
"smoking-room",
"sundial",
"mailbox",
"seventeen",
"nountaineerin",
"ightseeing",
"tuesday",
"fifty-fourth",
"dishes",
"calzone",
"september",
"warc",
"thinking",
"bakeshop",
"omething",
"creel",
"sixty-two",
"jaggage",
"bell-the-cat",
"shave",
"five-year-old",
"odd-number",
"down",
"hardware-store",
"persimmon-tree",
"forty-six",
"salespeople",
"sport-car",
"proaching",
"twenty-two",
"water",
"kettle's",
"section",
"little",
"condensed-milk",
"orgot",
"skis",
"t-intersection",
"at-short-notice",
"trigu",
"forget-me-not",
"anda",
"full-time",
"thirty-seven",
"plate's",
"weight-training",
"self-confident",
"vests",
"to-sneeze",
"onderful",
"weather's",
"sixty-four",
"to-embarrass",
"index",
"ice",
"havea",
"be-an-actor-cook-etc-in-the-making",
"scales",
"sixty-three",
"highest",
"toy-store",
"treated",
"sheets",
"sense-of-humor",
"coatroom",
"chestnut-tree",
"wrong",
"sheepfold",
"meal",
"exceptionally",
"wrist",
"shortly",
"vehicle-audio",
"to-rake",
"fillings",
"eleven",
"to-bake",
"cookies",
"radio-station",
"well",
"byte",
"to-contact",
"test",
"to-sip",
"you'd",
"rcoo",
"forty-eight",
"mouth",
"first-aid-box",
"bills",
"plus-sign",
"to-take-care",
"electronic",
"baggage",
"thi",
"twenty-one",
"march",
"mustache",
"tic-tac-toe",
"rule-ok",
"anyway",
"water-polo",
"café",
"rikin«",
"pedicure",
"self-service",
"to-knot",
"dinner's",
"all-night",
"caveman",
"tickets",
"linguagem",
"tennis-player",
"one-way",
"ake",
"peter's",
"separately",
"thirty-nine",
"schedule",
"articles",
"twenty-four",
"platform-shoes",
"buttons",
"sunlounger",
"payment",
"itch",
"rare",
"tailor's",
"to-pour",
"black-and-white",
"bag",
"wasn't",
"still-water",
"jeweller's",
"yo-yo",
"ninety-two",
"ninety-four",
"imni",
"timio",
"korean",
"visa",
"inexistent",
"fifteer",
"be-like-sheep",
"bend-back",
"jhere's",
"room-number",
"thirty-one",
"replant",
"koi",
"weevil",
"flatbread",
"to-graduate",
"eighty-seventh",
"great-grandmother",
"clock's",
"ndig",
"love",
"ties",
"hazelnut-tree",
"medical-history",
"room's",
"table",
"thirty",
"short-term",
"oss-couni",
"back",
"these",
"iistoric-buildin",
"twelve",
"check",
"dont",
"to-consist-of",
"cactus",
"vhy",
"wholll",
"looks",
"can't",
"he's",
"devoted",
"how's",
"music's",
"beans",
"to-sponsor",
"seea",
"basketball-player",
"cab",
"all",
"different",
"o-communicat",
"forty",
"co-pilot",
"actually",
"buy",
"ads",
"stick-nose-into",
"eye-test",
"sorry",
"twenty-five",
"gift-wrap",
"seeir",
"ountry",
"mid-december",
"map",
"macadamia-nut-tree",
"whipped-cream",
"brother-in-law",
"usinesswomai",
"to-concern",
"anything",
"home-made",
"state-frame-of-mind",
"ela",
]

# REQUEST_DELAY_SECONDS não será mais usado no loop principal da thread de scraping,
# pois o controle de taxa com paralelismo é mais complexo.
# A "gentileza" com o servidor agora é principalmente controlada por MAX_WORKERS.
# Se um delay for estritamente necessário POR request, ele deveria ser dentro do fetch_word_html
# ou gerenciado por um rate limiter mais sofisticado.

MAX_WORKERS = 15 # Número de threads paralelas para requisições. Ajuste com cuidado!

# --- Funções Auxiliares de Parsing (sem alteração) ---
def safe_get_text(element, default=""):
    """Extrai o texto de um elemento BeautifulSoup de forma segura."""
    return element.get_text() if element else default

def safe_get_attr(element, attr, default=""):
    """Extrai um atributo de um elemento BeautifulSoup de forma segura."""
    return element.get(attr, default) if element else default

# --- Funções de Persistência de Dados (sem alteração significativa) ---
def load_existing_data(filepath, gui_app_instance=None):
    """Carrega dados de um arquivo JSON, se existir."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            if gui_app_instance: gui_app_instance.log_message(f"Aviso: Arquivo '{filepath}' corrompido. Iniciando com dados vazios.")
            return {}
        except Exception as e:
            if gui_app_instance: gui_app_instance.log_message(f"Aviso: Não foi possível ler '{filepath}'. Erro: {e}. Iniciando com dados vazios.")
            return {}
    return {}

def save_data(data, filepath, gui_app_instance=None):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        if gui_app_instance: gui_app_instance.log_message(f"Erro Crítico: Não foi possível salvar dados em '{filepath}'. Erro: {e}")

# --- Função de Requisição HTTP (Modificada para Thread Safety) ---
def fetch_word_html(word_to_search, gui_app):
    global current_user_agent_index, shared_fetch_error_counter # Note: REQUEST_HEADERS não é global aqui, é construído localmente

    local_request_headers = REQUEST_HEADERS.copy() # Copia os headers base

    with ua_lock: # Garante acesso exclusivo para ler/modificar o índice e contador de erro do UA
        active_user_agent = USER_AGENTS[current_user_agent_index]
        local_request_headers["User-Agent"] = active_user_agent
    
    url = f"{REQUEST_BASE_URL_DICTIONARY}{word_to_search.lower()}"
    gui_app.log_message(f"Tentando: {word_to_search} (UA: ...{active_user_agent[-40:]})")

    try:
        response = requests.get(url, headers=local_request_headers, timeout=20) # Timeout um pouco maior
        response.raise_for_status()
        gui_app.log_message(f"Sucesso ({response.status_code}) para: {word_to_search}")
        with ua_lock: # Protege a modificação do contador de erros
            shared_fetch_error_counter[0] = 0 
        return response.text
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError) as e:
        error_message = f"Erro fetch para '{word_to_search}': {type(e).__name__}"
        if hasattr(e, 'response') and e.response is not None:
            error_message += f" (Status: {e.response.status_code})"
        else:
            error_message += f" ({e})"
        gui_app.log_message(error_message)

        with ua_lock: # Protege a lógica de troca de UA
            shared_fetch_error_counter[0] += 1
            if shared_fetch_error_counter[0] >= MAX_CONSECUTIVE_FETCH_ERRORS_BEFORE_UA_SWITCH:
                old_ua_index = current_user_agent_index
                current_user_agent_index = (current_user_agent_index + 1) % len(USER_AGENTS)
                # O User-Agent efetivo será pego na próxima chamada a fetch_word_html
                gui_app.log_message(f"MUITOS ERROS! Trocando UA de ...{USER_AGENTS[old_ua_index][-40:]} para ...{USER_AGENTS[current_user_agent_index][-40:]} (próxima requisição usará o novo).")
                shared_fetch_error_counter[0] = 0
    except requests.exceptions.RequestException as e:
        gui_app.log_message(f"Erro na requisição para '{word_to_search}': {type(e).__name__} - {e}")
    except Exception as e:
        gui_app.log_message(f"Erro inesperado no fetch para '{word_to_search}': {type(e).__name__} - {e}")
    return None

# --- Função Principal de Parsing (Coloque sua função parse_cambridge_entry completa aqui) ---
def parse_cambridge_entry(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    entry_data = {
        "word": "", "part_of_speech": "", "grammar": "",
        "pronunciations": {"uk": {}, "us": {}},
        "senses": [],
        "smart_vocabulary": {"topic": {}, "related_words": []}
    }
    entry_body = soup.find('div', class_='pr entry-body__el')
    if not entry_body: return entry_data # Retorna vazio se o corpo principal não for encontrado

    pos_header = entry_body.find('div', class_='pos-header')
    if pos_header:
        headword_span = pos_header.find('span', class_='hw dhw')
        entry_data['word'] = safe_get_text(headword_span)
        pos_span = pos_header.find('span', class_='pos dpos')
        entry_data['part_of_speech'] = safe_get_text(pos_span)
        gram_span = pos_header.find('span', class_='gram dgram')
        entry_data['grammar'] = safe_get_text(gram_span)

        uk_pron_span = pos_header.find('span', class_='uk dpron-i')
        if uk_pron_span:
            uk_audio_src = safe_get_attr(uk_pron_span.find('source', type='audio/mpeg'), 'src')

            # Tentativa de encontrar o span do IPA
            ipa_element = uk_pron_span.find('span', class_='ipa dipa')
            
            # Log para depuração:
            # print(f"Elemento IPA com 'ipa dipa': {ipa_element}")

            if not ipa_element:
                # Se não encontrou com 'ipa dipa', tente apenas com 'ipa'
                # Isso é mais robusto se a classe 'dipa' nem sempre estiver presente ou variar
                ipa_element = uk_pron_span.find('span', class_='ipa')
                # Log para depuração:
                # print(f"Elemento IPA apenas com 'ipa': {ipa_element}")
            
            ipa_text = safe_get_text(ipa_element)
            # Se o ipa_text ainda estiver vindo com as barras, ex: "/ˈstɔː.ri/", você pode limpá-las:
            if ipa_text.startswith('/') and ipa_text.endswith('/'):
               ipa_text = ipa_text.strip('/')
            # No entanto, com o seletor correto para o span interno, isso não deve ser necessário.

            entry_data['pronunciations']['uk'] = {
                'ipa': ipa_text,
                'audio': BASE_URL_CAMBRIDGE + uk_audio_src if uk_audio_src else ""
            }

        us_pron_span = pos_header.find('span', class_='us dpron-i')
        if us_pron_span:
            us_audio_src = safe_get_attr(us_pron_span.find('source', type='audio/mpeg'), 'src')
            
            ipa_element_us = us_pron_span.find('span', class_='ipa dipa')
            if not ipa_element_us:
                ipa_element_us = us_pron_span.find('span', class_='ipa')
            
            ipa_text_us = safe_get_text(ipa_element_us)

            if ipa_text_us.startswith('/') and ipa_text_us.endswith('/'):
               ipa_text_us = ipa_text_us.strip('/')

            entry_data['pronunciations']['us'] = {
                'ipa': ipa_text_us,
                'audio': BASE_URL_CAMBRIDGE + us_audio_src if us_audio_src else ""
            }
    else: # Fallback para a palavra se o cabeçalho não for encontrado
        headword_fallback = entry_body.find('span', class_='hw dhw')
        if headword_fallback: entry_data['word'] = safe_get_text(headword_fallback)

    pos_body = entry_body.find('div', class_='pos-body')
    if pos_body:
        for def_block in pos_body.find_all('div', class_='def-block ddef_block'):
            current_sense = {}
            ddef_h = def_block.find('div', class_='ddef_h')
            if ddef_h:
                epp_xref = ddef_h.find('span', class_='epp-xref')
                current_sense['cefr_level'] = safe_get_text(epp_xref)
            current_sense['definition'] = safe_get_text(def_block.find('div', class_='def ddef_d db'))
            
            examples, more_examples, see_also_terms = [], [], []
            def_body_ddef_b = def_block.find('div', class_='def-body ddef_b')
            if def_body_ddef_b:
                for ex_div in def_body_ddef_b.find_all('div', class_='examp dexamp', recursive=False):
                    examples.append(safe_get_text(ex_div.find('span', class_='eg deg')))
                
                see_xref_div = def_body_ddef_b.find('div', class_='xref see hax dxref-w')
                if see_xref_div:
                    for item_div in see_xref_div.find_all('div', class_='item lc'):
                        term_url = safe_get_attr(item_div.find('a'), 'href')
                        see_also_terms.append({
                            "term": safe_get_text(item_div.find('span', class_='x-h dx-h')),
                            "url": BASE_URL_CAMBRIDGE + term_url if term_url and not term_url.startswith('http') else term_url
                        })
            current_sense['examples'] = [ex for ex in examples if ex] # Remove exemplos vazios
            
            daccord_more_examples = def_block.find('div', class_='daccord')
            if daccord_more_examples and safe_get_text(daccord_more_examples.find('span', class_='showmore')) == "More examples":
                for li_tag in daccord_more_examples.find_all('li', class_='eg dexamp hax'):
                    more_examples.append(safe_get_text(li_tag))
            current_sense['more_examples'] = [ex for ex in more_examples if ex] # Remove exemplos vazios
            current_sense['see_also'] = see_also_terms
            
            if current_sense.get('definition') or current_sense.get('examples'):
                entry_data['senses'].append(current_sense)

    smart_vocab_div = entry_body.find('div', class_='smartt daccord')
    if smart_vocab_div:
        topic_anchor = smart_vocab_div.find('div', class_='daccord_lt').find('a') if smart_vocab_div.find('div', class_='daccord_lt') else None
        if topic_anchor:
            entry_data['smart_vocabulary']['topic'] = {
                "name": safe_get_text(topic_anchor), "url": safe_get_attr(topic_anchor, 'href')
            }
        related_words_list = smart_vocab_div.find('ul', class_='hul-u')
        if related_words_list:
            for li_tag in related_words_list.find_all('li', class_='lc'):
                word_link_tag = li_tag.find('a')
                if word_link_tag:
                    word_text = ""
                    base_span = word_link_tag.find('span', class_='base')
                    if base_span:
                        text_parts = [s.get_text() for s in base_span.find_all(True, recursive=False) if s.get_text()]
                        word_text = ' '.join(text_parts) if text_parts else safe_get_text(base_span)
                    else:
                        results_span = word_link_tag.find('span', class_='results')
                        word_text = safe_get_text(results_span) if results_span else safe_get_text(word_link_tag)
                    
                    if word_text:
                        entry_data['smart_vocabulary']['related_words'].append({
                            "word": word_text, "url": safe_get_attr(word_link_tag, 'href')
                        })
    return entry_data


# --- Função Worker para o ThreadPoolExecutor ---
def worker_fetch_and_parse(word_key, gui_app):
    """Busca e analisa HTML para uma única palavra."""
    html_content = fetch_word_html(word_key, gui_app)
    if html_content:
        parsed_data = parse_cambridge_entry(html_content)
        if parsed_data and parsed_data.get("word"):
            return word_key, parsed_data, None  # Sucesso: (palavra, dados, None)
        else:
            error_detail = {"error": "Falha no parsing ou palavra não encontrada na página.",
                            "original_query": word_key, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
            return word_key, None, error_detail  # Erro de Parse: (palavra, None, erro)
    else:
        error_detail = {"error": "Falha ao buscar o conteúdo HTML.",
                        "original_query": word_key, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
        return word_key, None, error_detail  # Erro de Fetch: (palavra, None, erro)

# --- Lógica de Scraping (Modificada para Paralelismo) ---
def scraping_logic_thread(gui_app, initial_words, stop_event):
    all_words_data = load_existing_data(DATA_FILE, gui_app)
    processed_or_in_queue_set = set(all_words_data.keys())
    
    word_processing_queue = collections.deque()
    for word in initial_words:
        normalized_word = word.lower().strip()
        if normalized_word:
            word_processing_queue.append(normalized_word)
            # Adiciona ao set aqui também, para que se estiver na lista inicial mas já processado,
            # não seja adicionado à fila de processamento real abaixo se já existir em all_words_data.
            # A lógica de pular abaixo cuidará disso, mas é bom ter o set consistente.
            processed_or_in_queue_set.add(normalized_word)


    gui_app.log_message(f"--- Iniciando Coleta Paralela (Max Workers: {MAX_WORKERS}) ---")
    gui_app.log_message(f"Carregados {len(all_words_data)} registros de '{DATA_FILE}'.")
    gui_app.log_message(f"Fila inicial com {len(word_processing_queue)} palavras.")

    words_newly_collected_this_session = 0
    words_skipped_this_session = 0
    words_failed_this_session = 0
    
    # Usar um lock para salvar o arquivo, para o caso de querermos salvar mais frequentemente de dentro do loop as_completed
    save_data_lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        active_futures = {} # Mapeia future -> normalized_key

        while (word_processing_queue or active_futures) and not stop_event.is_set():
            # Submeter novas tarefas se houver palavras na fila e capacidade no executor
            # Limitar o número de futures submetidos de uma vez para evitar sobrecarregar a memória se o processamento de resultados for lento
            # Ou, como aqui, submeter enquanto a fila tiver itens e houver "espaço mental" para gerenciar futures
            while word_processing_queue and len(active_futures) < MAX_WORKERS * 2 and not stop_event.is_set() : # Ex: não mais que o dobro de workers em voo
                current_word_to_process = word_processing_queue.popleft()
                normalized_key = current_word_to_process.lower().strip() # Normalização já feita ao adicionar

                if not normalized_key: continue

                # Atualiza estatísticas antes de checar se pula (para refletir a fila diminuindo)
                gui_app.update_stats(
                    len(all_words_data) - words_failed_this_session,
                    words_skipped_this_session,
                    words_failed_this_session,
                    len(word_processing_queue) + len(active_futures) + 1 # +1 para o que está prestes a ser submetido/pulado
                )

                if normalized_key in all_words_data and all_words_data[normalized_key].get("word"):
                    # gui_app.log_message(f"'{normalized_key}' já processada. Pulando submissão.")
                    words_skipped_this_session += 1
                    continue
                elif normalized_key in all_words_data and "error" in all_words_data[normalized_key]:
                    # gui_app.log_message(f"'{normalized_key}' erro anterior. Pulando submissão.")
                    words_skipped_this_session += 1
                    continue
                
                # Se a palavra já foi adicionada ao processed_or_in_queue_set mas não está em all_words_data
                # (significa que está na fila mas ainda não foi submetida, ou foi submetida e está em active_futures)
                # A checagem `normalized_key in all_words_data` acima lida com o caso de já ter sido persistida.
                # Para evitar submeter a mesma palavra múltiplas vezes se ela for adicionada à fila várias vezes rapidamente:
                # O `processed_or_in_queue_set` já deveria conter `normalized_key` se ela foi pega da fila.
                # Se ela foi pulada acima, está OK. Se não, será submetida.
                
                gui_app.log_message(f"Submetendo: '{normalized_key}'...")
                future = executor.submit(worker_fetch_and_parse, normalized_key, gui_app)
                active_futures[future] = normalized_key

            if not active_futures and not word_processing_queue and not stop_event.is_set(): # Fila e workers ociosos
                gui_app.log_message("Fila de processamento vazia e nenhum worker ativo.")
                # Opcional: adicionar uma pequena pausa aqui se for esperado que a fila seja repopulada
                # time.sleep(0.5) # Se não houver mais futures, o loop as_completed abaixo não bloqueará
                # break # Ou sair se a intenção é terminar quando a fila inicial se esgota e nada mais é adicionado

            # Processar resultados dos futures que completaram
            # O timeout em as_completed permite que o loop verifique stop_event e submeta novas tasks
            # se o processamento de futures for lento.
            results_processed_in_batch = 0
            for future in as_completed(list(active_futures.keys())): # timeout pequeno para responsividade
                if stop_event.is_set(): break

                normalized_key_completed = active_futures.pop(future)
                results_processed_in_batch +=1
                
                try:
                    _word_key_returned, parsed_data_result, error_detail_result = future.result()
                    # _word_key_returned deve ser igual a normalized_key_completed

                    if parsed_data_result:
                        all_words_data[normalized_key_completed] = parsed_data_result
                        gui_app.log_message(f"Resultado OK para: '{normalized_key_completed}'.")
                        words_newly_collected_this_session += 1

                        # Adicionar palavras do SMART Vocabulary à fila
                        if parsed_data_result.get("smart_vocabulary", {}).get("related_words"):
                            new_smart_count = 0
                            for dict_word_info in parsed_data_result["smart_vocabulary"]["related_words"]:
                                url_smart = dict_word_info.get("url")
                                if url_smart:
                                    # Use sua função _extract_keyword_from_url aqui
                                    # Lembre-se que _extract_keyword_from_url precisa de REQUEST_BASE_URL_DICTIONARY
                                    potential_new_key = _extract_keyword_from_url(url_smart, REQUEST_BASE_URL_DICTIONARY)
                                    if potential_new_key and potential_new_key not in processed_or_in_queue_set:
                                        processed_or_in_queue_set.add(potential_new_key)
                                        word_processing_queue.append(potential_new_key)
                                        new_smart_count += 1
                            if new_smart_count > 0:
                                gui_app.log_message(f"+{new_smart_count} palavras do SMART Vocab para '{normalized_key_completed}' adicionadas à fila.")
                    
                    elif error_detail_result:
                        all_words_data[normalized_key_completed] = error_detail_result
                        gui_app.log_message(f"Resultado com ERRO para '{normalized_key_completed}': {error_detail_result.get('error')}")
                        
                        words_failed_this_session += 1
                    
                except Exception as exc: # Erro ao obter resultado do future (ex: exceção no worker não capturada)
                    gui_app.log_message(f"Exceção no worker para '{normalized_key_completed}': {exc}")
                    all_words_data[normalized_key_completed] = {
                        "error": f"Exceção no worker: {str(exc)}",
                        "original_query": normalized_key_completed, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    words_failed_this_session += 1
                finally:
                    # Salvar após cada resultado processado, protegido por lock
                    with save_data_lock:
                        save_data(all_words_data, DATA_FILE, gui_app)
                    # O log de "Arquivo atualizado" pode ser muito frequente aqui, talvez logar a cada N salvamentos.

            if results_processed_in_batch > 0:
                 gui_app.log_message(f"Lote de {results_processed_in_batch} resultados processado. Arquivo salvo.")


            if stop_event.is_set():
                gui_app.log_message("Sinal de parada detectado, finalizando submissão e processamento de resultados.")
                # Limpar futures restantes se necessário, ou apenas deixar o 'with executor' lidar com o shutdown
                for future in list(active_futures.keys()): # Tenta cancelar futures que não iniciaram (melhor esforço)
                    future.cancel()
                break
            
            # Se não há mais palavras na fila e nenhuma tarefa ativa, o trabalho terminou.
            if not word_processing_queue and not active_futures:
                gui_app.log_message("Fila de processamento e tarefas ativas concluídas.")
                break
            
            # Pequena pausa para o loop principal não consumir 100% CPU se estiver apenas esperando por as_completed com timeout
            # time.sleep(0.1) # O timeout do as_completed já faz isso.

    # Fim do 'with ThreadPoolExecutor'
    if stop_event.is_set():
        gui_app.log_message("Coleta interrompida (final do executor).")
    
    gui_app.log_message("\n--- Coleta Finalizada (Sessão) ---")
    gui_app.log_message(f"Palavras novas coletadas: {words_newly_collected_this_session}")
    gui_app.log_message(f"Palavras puladas: {words_skipped_this_session}")
    gui_app.log_message(f"Falhas na coleta: {words_failed_this_session}")
    gui_app.log_message(f"Total de registros em '{DATA_FILE}': {len(all_words_data)}")
    gui_app.enable_start_button()

# --- Funções _extract_keyword_from_url e find_new_related_keywords (COPIE AS SUAS VERSÕES COMPLETAS AQUI) ---
def _extract_keyword_from_url(url_string: str | None, base_url: str) -> str | None:
    # ... (Sua implementação completa) ...
    if not url_string: 
        return None
    url_string = url_string.strip()
    if url_string.startswith(base_url):
        path_after_base = url_string[len(base_url):]
        keyword = path_after_base.split('?')[0]
        return keyword if keyword else None
    return None


def find_new_related_keywords(
    data_store: dict[str, dict], 
    dictionary_base_url: str = REQUEST_BASE_URL_DICTIONARY
) -> set[str]:
    """
    Scans a data store of word entries, extracts related keywords from their
    'smart_vocabulary' URLs, and returns a set of unique related keywords
    that are not already present as top-level keys in the data_store.

    Args:
        data_store (dict[str, dict]): The main dictionary where keys are existing words
                                      (keywords) and values are their detailed data.
                                      It's expected that entry values are dictionaries
                                      which might contain a 'smart_vocabulary' key,
                                      which in turn might contain a 'related_words' list.
        dictionary_base_url (str): The base URL prefix for dictionary entries,
                                   used to extract keywords from related word URLs.

    Returns:
        set[str]: A set of unique related keywords (strings) found from the URLs,
                  which are not already keys in the input data_store.
                  Keywords are in the format like 'anecdote', 'be-another-story'.
    """
    all_extracted_related_keywords = set()
    
    # Iterate through the values (word data entries) in the data store
    for entry_data in data_store.values():
        # Ensure the entry_data itself is a dictionary to safely use .get()
        if not isinstance(entry_data, dict):
            continue 
            
        # Safely navigate to the 'related_words' list
        smart_vocabulary_data = entry_data.get("smart_vocabulary", {})
        if not isinstance(smart_vocabulary_data, dict): # Ensure smart_vocabulary_data is a dict
            continue
            
        related_word_info_list = smart_vocabulary_data.get("related_words", [])
        if not isinstance(related_word_info_list, list): # Ensure related_word_info_list is a list
            continue

        for related_info_item in related_word_info_list:
            # Ensure the item within 'related_words' is a dictionary
            if not isinstance(related_info_item, dict):
                continue

            url = related_info_item.get("url")
            extracted_keyword = _extract_keyword_from_url(url, dictionary_base_url)
            
            if extracted_keyword:
                all_extracted_related_keywords.add(extracted_keyword)
    
    # Get the set of keywords already present in the data_store
    existing_keywords_in_store = set(data_store.keys())
    
    # Find which of the extracted related keywords are new
    # (i.e., not already in the data_store keys)
    newly_discovered_keywords = all_extracted_related_keywords.difference(existing_keywords_in_store)
    
    return newly_discovered_keywords


def read_json(path_json):
    try:
        with open(path_json, "r", encoding="utf-8") as file:
            json_data = json.load(file)
        return json_data
    except FileNotFoundError:
        print(f"Erro: O arquivo '{DATA_FILE}' não foi encontrado.")
        return {}
    except json.JSONDecodeError:
        print(f"Erro: O arquivo '{DATA_FILE}' não contém um JSON válido ou está corrompido.")
        return {}
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao ler o arquivo: {e}")
        return {}

# --- Classe da Interface Gráfica Tkinter ---
class ScraperAppGUI:
    def __init__(self, master_root):
        self.master = master_root
        master_root.title("Cambridge Dictionary Scraper")
        master_root.geometry("700x550")

        self.stop_event = threading.Event()
        self.scraper_thread = None

        # Frame para controles
        control_frame = ttk.Frame(master_root, padding="10")
        control_frame.pack(fill=tk.X)

        ttk.Label(control_frame, text="Palavras Iniciais (separadas por vírgula):").pack(side=tk.LEFT, padx=(0, 5))
        self.words_entry = ttk.Entry(control_frame, width=40)
        self.words_entry.insert(0, "story, have, elegance, ubiquitous, nonexistentwordxyz")
        self.words_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.start_button = ttk.Button(control_frame, text="Iniciar Coleta", command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(control_frame, text="Parar", command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)

        # Área de Log
        log_frame = ttk.LabelFrame(master_root, text="Log de Atividades", padding="10")
        log_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        
        self.log_text_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15, state=tk.DISABLED)
        self.log_text_area.pack(expand=True, fill=tk.BOTH)

        # Frame para Estatísticas
        stats_frame = ttk.LabelFrame(master_root, text="Estatísticas", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=(0,10))

        self.stats_label = ttk.Label(stats_frame, text="Coletadas: 0 | Puladas: 0 | Falhas: 0 | Fila: 0")
        self.stats_label.pack()
        
        master_root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log_message(self, message):
        if hasattr(self, 'log_text_area') and self.log_text_area.winfo_exists():
            self.log_text_area.config(state=tk.NORMAL)
            self.log_text_area.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
            self.log_text_area.see(tk.END)
            self.log_text_area.config(state=tk.DISABLED)
            self.master.update_idletasks() # Força atualização da UI

    def update_stats(self, collected, skipped, failed, queue_size):
        if hasattr(self, 'stats_label') and self.stats_label.winfo_exists():
            self.stats_label.config(text=f"Coletadas (total): {collected} | Puladas (sessão): {skipped} | Falhas (sessão): {failed} | Fila: {queue_size}")
            self.master.update_idletasks()

    def start_scraping(self):
        initial_words_str = self.words_entry.get()

        if not initial_words_str.strip():
            messagebox.showwarning("Entrada Inválida", "Por favor, insira algumas palavras iniciais.")
            return
            
        initial_words = [word.strip() for word in initial_words_str.split(',') if word.strip()]

        initial_words.extend(
            list_initial_words
        )

        json_data = read_json(path_json=DATA_FILE)

        new_keywords_to_fetch = find_new_related_keywords(json_data)


        initial_words.extend(new_keywords_to_fetch)
        
        if not initial_words:
            messagebox.showwarning("Entrada Inválida", "Nenhuma palavra válida para processar após limpeza.")
            return

        self.log_text_area.config(state=tk.NORMAL)
        self.log_text_area.delete('1.0', tk.END) # Limpa log anterior
        self.log_text_area.config(state=tk.DISABLED)

        self.stop_event.clear()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.words_entry.config(state=tk.DISABLED)
        
        self.log_message(f"Iniciando coleta para: {', '.join(initial_words)}")
        
        # Passa a instância da GUI e o evento de parada para a thread
        self.scraper_thread = threading.Thread(target=scraping_logic_thread, args=(self, initial_words, self.stop_event))
        self.scraper_thread.daemon = True 
        self.scraper_thread.start()
        
        # Não é mais necessário, pois a thread chama enable_start_button() no final
        # self.master.after(100, self.check_thread_status)

    def stop_scraping(self):
        if self.scraper_thread and self.scraper_thread.is_alive():
            self.stop_event.set()
            self.log_message("Sinal de parada enviado à thread de coleta...")
        self.stop_button.config(state=tk.DISABLED) # Desabilita imediatamente

    def enable_start_button(self):
        """Chamado pela thread de scraping quando ela termina."""
        if self.master.winfo_exists(): # Verifica se a janela ainda existe
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.words_entry.config(state=tk.NORMAL)
            self.log_message("Pronto para nova coleta ou fechar.")
            
    def on_closing(self):
        if self.scraper_thread and self.scraper_thread.is_alive():
            self.log_message("Tentando parar a coleta antes de fechar...")
            self.stop_event.set()
            # Poderia esperar um pouco pela thread aqui, ou apenas avisar
            if messagebox.askokcancel("Sair", "A coleta de dados está em andamento. Deseja realmente sair? O progresso atual foi salvo."):
                self.master.destroy()
            else:
                return # Não fecha
        else:
            self.master.destroy()

# --- Ponto de Entrada Principal ---
if __name__ == "__main__":
    # Validação crucial: assegure que parse_cambridge_entry não é um placeholder.
    # Esta é uma verificação simples baseada em docstring, ajuste se necessário.
    root = tk.Tk()
    app = ScraperAppGUI(root)
    root.mainloop()