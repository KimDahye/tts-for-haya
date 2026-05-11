from dataclasses import dataclass


@dataclass(frozen=True)
class Book:
    code: str
    num: int
    esv: str
    kor_full: str
    kor_short: str


BOOKS: list[Book] = [
    Book("gen",  1, "Genesis",         "창세기",     "창"),
    Book("exo",  2, "Exodus",          "출애굽기",   "출"),
    Book("lev",  3, "Leviticus",       "레위기",     "레"),
    Book("num",  4, "Numbers",         "민수기",     "민"),
    Book("deu",  5, "Deuteronomy",     "신명기",     "신"),
    Book("jos",  6, "Joshua",          "여호수아",   "수"),
    Book("jdg",  7, "Judges",          "사사기",     "삿"),
    Book("rut",  8, "Ruth",            "룻기",       "룻"),
    Book("1sa",  9, "1 Samuel",        "사무엘상",   "삼상"),
    Book("2sa", 10, "2 Samuel",        "사무엘하",   "삼하"),
    Book("1ki", 11, "1 Kings",         "열왕기상",   "왕상"),
    Book("2ki", 12, "2 Kings",         "열왕기하",   "왕하"),
    Book("1ch", 13, "1 Chronicles",    "역대상",     "대상"),
    Book("2ch", 14, "2 Chronicles",    "역대하",     "대하"),
    Book("ezr", 15, "Ezra",            "에스라",     "스"),
    Book("neh", 16, "Nehemiah",        "느헤미야",   "느"),
    Book("est", 17, "Esther",          "에스더",     "에"),
    Book("job", 18, "Job",             "욥기",       "욥"),
    Book("psa", 19, "Psalms",          "시편",       "시"),
    Book("pro", 20, "Proverbs",        "잠언",       "잠"),
    Book("ecc", 21, "Ecclesiastes",    "전도서",     "전"),
    Book("sng", 22, "Song of Solomon", "아가",       "아"),
    Book("isa", 23, "Isaiah",          "이사야",     "사"),
    Book("jer", 24, "Jeremiah",        "예레미야",   "렘"),
    Book("lam", 25, "Lamentations",    "예레미야애가", "애"),
    Book("ezk", 26, "Ezekiel",         "에스겔",     "겔"),
    Book("dan", 27, "Daniel",          "다니엘",     "단"),
    Book("hos", 28, "Hosea",           "호세아",     "호"),
    Book("jol", 29, "Joel",            "요엘",       "욜"),
    Book("amo", 30, "Amos",            "아모스",     "암"),
    Book("oba", 31, "Obadiah",         "오바댜",     "옵"),
    Book("jon", 32, "Jonah",           "요나",       "욘"),
    Book("mic", 33, "Micah",           "미가",       "미"),
    Book("nam", 34, "Nahum",           "나훔",       "나"),
    Book("hab", 35, "Habakkuk",        "하박국",     "합"),
    Book("zep", 36, "Zephaniah",       "스바냐",     "습"),
    Book("hag", 37, "Haggai",          "학개",       "학"),
    Book("zec", 38, "Zechariah",       "스가랴",     "슥"),
    Book("mal", 39, "Malachi",         "말라기",     "말"),
    Book("mat", 40, "Matthew",         "마태복음",   "마"),
    Book("mrk", 41, "Mark",            "마가복음",   "막"),
    Book("luk", 42, "Luke",            "누가복음",   "눅"),
    Book("jhn", 43, "John",            "요한복음",   "요"),
    Book("act", 44, "Acts",            "사도행전",   "행"),
    Book("rom", 45, "Romans",          "로마서",     "롬"),
    Book("1co", 46, "1 Corinthians",   "고린도전서", "고전"),
    Book("2co", 47, "2 Corinthians",   "고린도후서", "고후"),
    Book("gal", 48, "Galatians",       "갈라디아서", "갈"),
    Book("eph", 49, "Ephesians",       "에베소서",   "엡"),
    Book("php", 50, "Philippians",     "빌립보서",   "빌"),
    Book("col", 51, "Colossians",      "골로새서",   "골"),
    Book("1th", 52, "1 Thessalonians", "데살로니가전서", "살전"),
    Book("2th", 53, "2 Thessalonians", "데살로니가후서", "살후"),
    Book("1ti", 54, "1 Timothy",       "디모데전서", "딤전"),
    Book("2ti", 55, "2 Timothy",       "디모데후서", "딤후"),
    Book("tit", 56, "Titus",           "디도서",     "딛"),
    Book("phm", 57, "Philemon",        "빌레몬서",   "몬"),
    Book("heb", 58, "Hebrews",         "히브리서",   "히"),
    Book("jas", 59, "James",           "야고보서",   "약"),
    Book("1pe", 60, "1 Peter",         "베드로전서", "벧전"),
    Book("2pe", 61, "2 Peter",         "베드로후서", "벧후"),
    Book("1jn", 62, "1 John",          "요한일서",   "요일"),
    Book("2jn", 63, "2 John",          "요한이서",   "요이"),
    Book("3jn", 64, "3 John",          "요한삼서",   "요삼"),
    Book("jud", 65, "Jude",            "유다서",     "유"),
    Book("rev", 66, "Revelation",      "요한계시록", "계"),
]

BY_CODE: dict[str, Book] = {b.code: b for b in BOOKS}


_EXTRA_ALIASES: dict[str, list[str]] = {
    "gen": ["ge"],
    "exo": ["ex", "exod"],
    "lev": ["lv"],
    "num": ["nm", "nu"],
    "deu": ["dt", "deut"],
    "jos": ["josh", "jsh"],
    "jdg": ["jg", "judg"],
    "rut": ["ru", "ruth"],
    "1sa": ["1s", "1sam", "i sam", "1 sam"],
    "2sa": ["2s", "2sam", "ii sam", "2 sam"],
    "1ki": ["1k", "1kgs", "1 kgs", "1 kings"],
    "2ki": ["2k", "2kgs", "2 kgs", "2 kings"],
    "1ch": ["1chr", "1 chr", "1 chron"],
    "2ch": ["2chr", "2 chr", "2 chron"],
    "ezr": ["ezra"],
    "neh": ["nehemiah"],
    "est": ["esth", "esther"],
    "job": ["jb"],
    "psa": ["ps", "psalm", "psalms"],
    "pro": ["pr", "prov"],
    "ecc": ["ec", "eccl", "qoh"],
    "sng": ["sg", "song", "ss", "song of songs", "song of sol", "canticles"],
    "isa": ["is"],
    "jer": ["jr"],
    "lam": ["la"],
    "ezk": ["ezek", "eze"],
    "dan": ["dn"],
    "hos": ["ho"],
    "jol": ["joel"],
    "amo": ["am", "amos"],
    "oba": ["ob", "obad"],
    "jon": ["jonah", "jnh"],
    "mic": ["mi", "micah"],
    "nam": ["na", "nahum", "nah"],
    "hab": ["hb", "habakkuk"],
    "zep": ["zp", "zeph", "zph"],
    "hag": ["hg"],
    "zec": ["zc", "zech"],
    "mal": ["ml"],
    "mat": ["mt", "matt"],
    "mrk": ["mk", "mark"],
    "luk": ["lk", "luke"],
    "jhn": ["jn", "john"],
    "act": ["ac", "acts"],
    "rom": ["ro"],
    "1co": ["1cor", "1 cor"],
    "2co": ["2cor", "2 cor"],
    "gal": ["ga"],
    "eph": ["ephes"],
    "php": ["phil", "philip"],
    "col": ["colossians"],
    "1th": ["1thess", "1 thess"],
    "2th": ["2thess", "2 thess"],
    "1ti": ["1tim", "1 tim"],
    "2ti": ["2tim", "2 tim"],
    "tit": ["ti", "titus"],
    "phm": ["phlm", "philem"],
    "heb": ["he"],
    "jas": ["jm", "james"],
    "1pe": ["1pet", "1 pet"],
    "2pe": ["2pet", "2 pet"],
    "1jn": ["1jo", "1jhn", "1 jn", "1 john"],
    "2jn": ["2jo", "2jhn", "2 jn", "2 john"],
    "3jn": ["3jo", "3jhn", "3 jn", "3 john"],
    "jud": ["jude"],
    "rev": ["re", "rv", "apoc", "apocalypse"],
}


def _build_alias_table() -> dict[str, str]:
    table: dict[str, str] = {}

    def add(key: str, code: str) -> None:
        norm = key.strip().lower().replace(" ", "")
        if norm:
            table[norm] = code

    for b in BOOKS:
        add(b.code, b.code)
        add(b.esv, b.code)
        add(b.kor_full, b.code)
        add(b.kor_short, b.code)
        add(str(b.num), b.code)
        for alias in _EXTRA_ALIASES.get(b.code, []):
            add(alias, b.code)
    return table


_ALIAS_TABLE: dict[str, str] = _build_alias_table()


def resolve_book(user_input: str) -> Book:
    key = user_input.strip().lower().replace(" ", "")
    code = _ALIAS_TABLE.get(key)
    if code is None:
        raise ValueError(f"알 수 없는 책 이름입니다: {user_input!r}")
    return BY_CODE[code]
