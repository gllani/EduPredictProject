import pandas as pd, urllib.request, json
from pathlib import Path

OUT = Path("data/raw/enrollment_raw.csv")
OUT.parent.mkdir(parents=True, exist_ok=True)

INDICATORS = {
    "SE.PRM.ENRL": "enrollment_primary",
    "SE.SEC.ENRL": "enrollment_secondary",
    "SE.TER.ENRL": "enrollment_tertiary",
    "SP.POP.TOTL": "population_total",
    "NY.GDP.PCAP.CD": "gdp_per_capita_usd",
    "SE.XPD.TOTL.GD.ZS": "gov_edu_expenditure_pct",
    "SE.ADT.LITR.ZS": "literacy_rate",
}

REGIONS = {
    "USA":"North America","CAN":"North America","MEX":"Latin America & Caribbean",
    "BRA":"Latin America & Caribbean","ARG":"Latin America & Caribbean","COL":"Latin America & Caribbean",
    "PER":"Latin America & Caribbean","CHL":"Latin America & Caribbean","VEN":"Latin America & Caribbean",
    "GBR":"Europe & Central Asia","DEU":"Europe & Central Asia","FRA":"Europe & Central Asia",
    "ITA":"Europe & Central Asia","ESP":"Europe & Central Asia","RUS":"Europe & Central Asia",
    "POL":"Europe & Central Asia","NLD":"Europe & Central Asia","BEL":"Europe & Central Asia",
    "SWE":"Europe & Central Asia","NOR":"Europe & Central Asia","CHE":"Europe & Central Asia",
    "TUR":"Europe & Central Asia","UKR":"Europe & Central Asia","KAZ":"Europe & Central Asia",
    "CHN":"East Asia & Pacific","JPN":"East Asia & Pacific","KOR":"East Asia & Pacific",
    "AUS":"East Asia & Pacific","IDN":"East Asia & Pacific","PHL":"East Asia & Pacific",
    "VNM":"East Asia & Pacific","THA":"East Asia & Pacific","MYS":"East Asia & Pacific",
    "IND":"South Asia","PAK":"South Asia","BGD":"South Asia","NPL":"South Asia","LKA":"South Asia",
    "NGA":"Sub-Saharan Africa","ETH":"Sub-Saharan Africa","KEN":"Sub-Saharan Africa",
    "TZA":"Sub-Saharan Africa","ZAF":"Sub-Saharan Africa","GHA":"Sub-Saharan Africa",
    "MOZ":"Sub-Saharan Africa","UGA":"Sub-Saharan Africa","CMR":"Sub-Saharan Africa",
    "EGY":"Middle East & North Africa","IRN":"Middle East & North Africa","SAU":"Middle East & North Africa",
    "MAR":"Middle East & North Africa","DZA":"Middle East & North Africa","TUN":"Middle East & North Africa",
    "IRQ":"Middle East & North Africa","JOR":"Middle East & North Africa","LBN":"Middle East & North Africa",
}

def fetch(code, name):
    print(f"  Fetching {name}...")
    records, page = [], 1
    while True:
        url = f"https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&per_page=1000&page={page}&date=1990:2023"
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                data = json.loads(r.read())
        except Exception as e:
            print(f"    error: {e}"); break
        if not data or len(data) < 2 or not data[1]: break
        for item in data[1]:
            if item.get("value") is not None:
                records.append({"country_code": item["country"]["id"], "country_name": item["country"]["value"], "year": int(item["date"]), name: float(item["value"])})
        if page >= data[0].get("pages", 1): break
        page += 1
    print(f"    {len(records):,} records")
    return pd.DataFrame(records)

dfs = []
for code, name in INDICATORS.items():
    df = fetch(code, name)
    if not df.empty:
        dfs.append(df.set_index(["country_code","country_name","year"]))

combined = dfs[0]
for df in dfs[1:]:
    combined = combined.join(df, how="outer")
combined = combined.reset_index()

cols = [c for c in ["enrollment_primary","enrollment_secondary","enrollment_tertiary"] if c in combined.columns]
combined["enrollment_total"] = combined[cols].sum(axis=1, min_count=1)
combined["region"] = combined["country_code"].map(REGIONS).fillna("Other")
combined["population_school_age"] = combined["population_total"] * 0.28
combined = combined.dropna(subset=["enrollment_total"])
combined.to_csv(OUT, index=False)
print(f"\nDone! {len(combined):,} rows saved to {OUT}")
