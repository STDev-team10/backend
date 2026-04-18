from typing import TypedDict


class CompoundMeta(TypedDict):
    name_ko: str
    name_en: str
    formula: str
    pubchem_cid: int | None
    has_3d: bool


COMPOUND_MAP: dict[str, CompoundMeta] = {
    "water":                {"name_ko": "물",               "name_en": "Water",               "formula": "H2O",           "pubchem_cid": 962,      "has_3d": True},
    "sodium-chloride":      {"name_ko": "염화나트륨",        "name_en": "Sodium chloride",      "formula": "NaCl",          "pubchem_cid": 5234,     "has_3d": True},
    "carbon-dioxide":       {"name_ko": "이산화탄소",         "name_en": "Carbon dioxide",       "formula": "CO2",           "pubchem_cid": 280,      "has_3d": True},
    "oxygen":               {"name_ko": "산소",              "name_en": "Oxygen",               "formula": "O2",            "pubchem_cid": 977,      "has_3d": True},
    "nitrogen":             {"name_ko": "질소",              "name_en": "Nitrogen",             "formula": "N2",            "pubchem_cid": 947,      "has_3d": True},
    "hydrogen":             {"name_ko": "수소",              "name_en": "Hydrogen",             "formula": "H2",            "pubchem_cid": 783,      "has_3d": True},
    "ammonia":              {"name_ko": "암모니아",           "name_en": "Ammonia",              "formula": "NH3",           "pubchem_cid": 222,      "has_3d": True},
    "methane":              {"name_ko": "메테인",             "name_en": "Methane",              "formula": "CH4",           "pubchem_cid": 297,      "has_3d": True},
    "hydrogen-chloride":    {"name_ko": "염화수소",           "name_en": "Hydrogen chloride",    "formula": "HCl",           "pubchem_cid": 313,      "has_3d": True},
    "carbon-monoxide":      {"name_ko": "일산화탄소",         "name_en": "Carbon monoxide",      "formula": "CO",            "pubchem_cid": 281,      "has_3d": True},
    "calcium-carbonate":    {"name_ko": "탄산칼슘",           "name_en": "Calcium carbonate",    "formula": "CaCO3",         "pubchem_cid": 10112,    "has_3d": True},
    "sodium-bicarbonate":   {"name_ko": "탄산수소나트륨",      "name_en": "Sodium bicarbonate",   "formula": "NaHCO3",        "pubchem_cid": 516892,   "has_3d": True},
    "hydrogen-peroxide":    {"name_ko": "과산화수소",          "name_en": "Hydrogen peroxide",    "formula": "H2O2",          "pubchem_cid": 784,      "has_3d": True},
    "ethanol":              {"name_ko": "에탄올",             "name_en": "Ethanol",              "formula": "C2H5OH",        "pubchem_cid": 702,      "has_3d": True},
    "sodium-hydroxide":     {"name_ko": "수산화나트륨",        "name_en": "Sodium hydroxide",     "formula": "NaOH",          "pubchem_cid": 14798,    "has_3d": True},
    "potassium-chloride":   {"name_ko": "염화칼륨",           "name_en": "Potassium chloride",   "formula": "KCl",           "pubchem_cid": 4873,     "has_3d": True},
    "calcium-oxide":        {"name_ko": "산화칼슘",           "name_en": "Calcium oxide",        "formula": "CaO",           "pubchem_cid": 14778,    "has_3d": True},
    "magnesium-oxide":      {"name_ko": "산화마그네슘",        "name_en": "Magnesium oxide",      "formula": "MgO",           "pubchem_cid": 14792,    "has_3d": True},
    "sulfur-dioxide":       {"name_ko": "이산화황",           "name_en": "Sulfur dioxide",       "formula": "SO2",           "pubchem_cid": 1119,     "has_3d": True},
    "sulfur-trioxide":      {"name_ko": "삼산화황",           "name_en": "Sulfur trioxide",      "formula": "SO3",           "pubchem_cid": 24682,    "has_3d": True},
    "nitrogen-dioxide":     {"name_ko": "이산화질소",          "name_en": "Nitrogen dioxide",     "formula": "NO2",           "pubchem_cid": 3032552,  "has_3d": True},
    "nitric-oxide":         {"name_ko": "일산화질소",          "name_en": "Nitric oxide",         "formula": "NO",            "pubchem_cid": 145068,   "has_3d": True},
    "nitrous-oxide":        {"name_ko": "아산화질소",          "name_en": "Nitrous oxide",        "formula": "N2O",           "pubchem_cid": 948,      "has_3d": True},
    "sodium-carbonate":     {"name_ko": "탄산나트륨",          "name_en": "Sodium carbonate",     "formula": "Na2CO3",        "pubchem_cid": 10340,    "has_3d": True},
    "calcium-chloride":     {"name_ko": "염화칼슘",           "name_en": "Calcium chloride",     "formula": "CaCl2",         "pubchem_cid": 24854,    "has_3d": True},
    "magnesium-chloride":   {"name_ko": "염화마그네슘",        "name_en": "Magnesium chloride",   "formula": "MgCl2",         "pubchem_cid": 24584,    "has_3d": True},
    "potassium-hydroxide":  {"name_ko": "수산화칼륨",          "name_en": "Potassium hydroxide",  "formula": "KOH",           "pubchem_cid": 14797,    "has_3d": True},
    "sodium-oxide":         {"name_ko": "산화나트륨",          "name_en": "Sodium oxide",         "formula": "Na2O",          "pubchem_cid": 73971,    "has_3d": True},
    "potassium-oxide":      {"name_ko": "산화칼륨",           "name_en": "Potassium oxide",      "formula": "K2O",           "pubchem_cid": 14800,    "has_3d": True},
    "magnesium-hydroxide":  {"name_ko": "수산화마그네슘",       "name_en": "Magnesium hydroxide",  "formula": "Mg(OH)2",       "pubchem_cid": 73981,    "has_3d": True},
    "calcium-hydroxide":    {"name_ko": "수산화칼슘",          "name_en": "Calcium hydroxide",    "formula": "Ca(OH)2",       "pubchem_cid": 12616,    "has_3d": True},
    "nitric-acid":          {"name_ko": "질산",              "name_en": "Nitric acid",          "formula": "HNO3",          "pubchem_cid": 944,      "has_3d": True},
    "sulfuric-acid":        {"name_ko": "황산",              "name_en": "Sulfuric acid",        "formula": "H2SO4",         "pubchem_cid": 1118,     "has_3d": True},
    "sulfurous-acid":       {"name_ko": "아황산",             "name_en": "Sulfurous acid",       "formula": "H2SO3",         "pubchem_cid": 1100,     "has_3d": True},
    "carbonic-acid":        {"name_ko": "탄산",              "name_en": "Carbonic acid",        "formula": "H2CO3",         "pubchem_cid": 767,      "has_3d": True},
    "glucose":              {"name_ko": "포도당",             "name_en": "Glucose",              "formula": "C6H12O6",       "pubchem_cid": 5793,     "has_3d": True},
    "sucrose":              {"name_ko": "자당",              "name_en": "Sucrose",              "formula": "C12H22O11",     "pubchem_cid": 5988,     "has_3d": True},
    "benzene":              {"name_ko": "벤젠",              "name_en": "Benzene",              "formula": "C6H6",          "pubchem_cid": 241,      "has_3d": True},
    "ethylene":             {"name_ko": "에틸렌",             "name_en": "Ethylene",             "formula": "C2H4",          "pubchem_cid": 6325,     "has_3d": True},
    "acetylene":            {"name_ko": "아세틸렌",           "name_en": "Acetylene",            "formula": "C2H2",          "pubchem_cid": 6326,     "has_3d": True},
    "propane":              {"name_ko": "프로페인",           "name_en": "Propane",              "formula": "C3H8",          "pubchem_cid": 6334,     "has_3d": True},
    "butane":               {"name_ko": "부테인",             "name_en": "Butane",               "formula": "C4H10",         "pubchem_cid": 7843,     "has_3d": True},
    "methanol":             {"name_ko": "메탄올",             "name_en": "Methanol",             "formula": "CH3OH",         "pubchem_cid": 887,      "has_3d": True},
    "sodium-fluoride":      {"name_ko": "플루오르화나트륨",     "name_en": "Sodium fluoride",      "formula": "NaF",           "pubchem_cid": 5235,     "has_3d": True},
    "hydrogen-fluoride":    {"name_ko": "플루오르화수소",       "name_en": "Hydrogen fluoride",    "formula": "HF",            "pubchem_cid": 16211014, "has_3d": True},
    "sodium-bromide":       {"name_ko": "브로민화나트륨",       "name_en": "Sodium bromide",       "formula": "NaBr",          "pubchem_cid": 253881,   "has_3d": True},
    "potassium-iodide":     {"name_ko": "아이오딘화칼륨",       "name_en": "Potassium iodide",     "formula": "KI",            "pubchem_cid": 4875,     "has_3d": True},
    "iron3-oxide":          {"name_ko": "산화철(III)",        "name_en": "Iron(III) oxide",      "formula": "Fe2O3",         "pubchem_cid": 518696,   "has_3d": True},
    "iron2-oxide":          {"name_ko": "산화철(II)",         "name_en": "Iron(II) oxide",       "formula": "FeO",           "pubchem_cid": 14945,    "has_3d": True},
    "aluminum-oxide":       {"name_ko": "산화알루미늄",        "name_en": "Aluminum oxide",       "formula": "Al2O3",         "pubchem_cid": 9989226,  "has_3d": True},
    "silicon-dioxide":      {"name_ko": "이산화규소",          "name_en": "Silicon dioxide",      "formula": "SiO2",          "pubchem_cid": 24261,    "has_3d": True},
    "ammonium-chloride":    {"name_ko": "염화암모늄",          "name_en": "Ammonium chloride",    "formula": "NH4Cl",         "pubchem_cid": 25517,    "has_3d": True},
    "ammonium-nitrate":     {"name_ko": "질산암모늄",          "name_en": "Ammonium nitrate",     "formula": "NH4NO3",        "pubchem_cid": 22985,    "has_3d": True},
    "ammonium-hydroxide":   {"name_ko": "수산화암모늄",        "name_en": "Ammonium hydroxide",   "formula": "NH4OH",         "pubchem_cid": 14923,    "has_3d": True},
    "sodium-nitrate":       {"name_ko": "질산나트륨",          "name_en": "Sodium nitrate",       "formula": "NaNO3",         "pubchem_cid": 24268,    "has_3d": True},
    "potassium-nitrate":    {"name_ko": "질산칼륨",           "name_en": "Potassium nitrate",    "formula": "KNO3",          "pubchem_cid": 516920,   "has_3d": True},
    # 새로 추가된 특수 항목
    "gold":                 {"name_ko": "금(귀금속)",         "name_en": "Gold",                 "formula": "Au",            "pubchem_cid": 23985,    "has_3d": False},
    "nitroglycerin":        {"name_ko": "다이너마이트(니트로글리세린)", "name_en": "Nitroglycerin",   "formula": "C3H5N3O9",      "pubchem_cid": 11477,    "has_3d": True},
    "radium":               {"name_ko": "라듐",              "name_en": "Radium",               "formula": "Ra",            "pubchem_cid": 6328144,  "has_3d": False},
    "sodium-hypochlorite":  {"name_ko": "락스(차아염소산나트륨)", "name_en": "Sodium hypochlorite", "formula": "NaClO",         "pubchem_cid": 23665760, "has_3d": True},
    "arsenic":              {"name_ko": "비소",              "name_en": "Arsenic",              "formula": "As",            "pubchem_cid": 5359596,  "has_3d": False},
    "ddt":                  {"name_ko": "살충제(DDT)",        "name_en": "DDT",                  "formula": "C14H9Cl5",      "pubchem_cid": 3036,     "has_3d": True},
    "chrysotile":           {"name_ko": "석면(크리소타일)",     "name_en": "Chrysotile",           "formula": "Mg3Si2O5(OH)4", "pubchem_cid": 16211697, "has_3d": True},
    "alcohol":              {"name_ko": "알콜(에탄올)",        "name_en": "Alcohol (Ethanol)",    "formula": "C2H5OH",        "pubchem_cid": 702,      "has_3d": True},
    "mercury":              {"name_ko": "수은",              "name_en": "Mercury",              "formula": "Hg",            "pubchem_cid": 23931,    "has_3d": False},
    "haber-ammonia":        {"name_ko": "하버(암모니아)",       "name_en": "Haber-Bosch Ammonia",  "formula": "NH3",           "pubchem_cid": 222,      "has_3d": True},
}

# 한글명 → id 역방향 검색용
_KO_INDEX: dict[str, str] = {v["name_ko"]: k for k, v in COMPOUND_MAP.items()}


def lookup(compound_id: str) -> CompoundMeta | None:
    return COMPOUND_MAP.get(compound_id)


def lookup_by_name_ko(name_ko: str) -> CompoundMeta | None:
    cid = _KO_INDEX.get(name_ko)
    return COMPOUND_MAP.get(cid) if cid else None
