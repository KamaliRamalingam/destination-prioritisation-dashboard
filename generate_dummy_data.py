"""Generate synthetic input data for the destination prioritisation analysis.

Creates the same six CSV files, with the same columns and row counts, as the
original (confidential) dataset. All values are random and fictional.

    python generate_dummy_data.py   ->   data/*.csv
"""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
OUT = Path("data"); OUT.mkdir(exist_ok=True)

N_BOOKINGS, N_FACT_ROWS = 19_665, 150_631
N_TRANSPORT, N_ACCOMMODATION, N_PRODUCT_GROUPS = 6_130, 325, 50

# ---------------------------------------------------------------- dim_market (14 x 3)
countries = [("Sweden", "SEK"), ("Norway", "NOK"), ("Denmark", "DKK"),
             ("Finland", "EUR"), ("Iceland", "ISK"), ("United Kingdom", "GBP")]
market_country = [0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5]
mk = pd.DataFrame({"market_id": range(1, 15),
                   "sell_country": [countries[i][0] for i in market_country],
                   "sell_currency": [countries[i][1] for i in market_country]})
FX = {"SEK": 1.0, "NOK": 0.98, "DKK": 1.52, "EUR": 11.3, "ISK": 0.077, "GBP": 13.2}

# ---------------------------------------------------------------- dim_product_group (50 x 4)
groups = [("Flyg", "Flight"), ("Hotell", "Hotel"), ("Transfer", "Transfer"), ("Hyrbil", "Car rental"),
          ("Aktivitet", "Activity"), ("Försäkring", "Insurance"), ("Avbokningsskydd", "Cancellation cover"),
          ("Utflykt", "Excursion"), ("Bagage", "Luggage"), ("Måltider", "Meals"), ("Spa", "Spa"),
          ("Utrustning", "Equipment"), ("Kurs", "Course"), ("Avgift", "Fee"), ("Rabatt", "Discount"),
          ("Presentkort", "Gift card")]
pg = pd.DataFrame({"product_group_id": range(1, N_PRODUCT_GROUPS + 1),
                   "product_group_code": rng.choice(np.arange(100, 999), N_PRODUCT_GROUPS, replace=False)})
pick = [groups[i % len(groups)] for i in range(N_PRODUCT_GROUPS)]
pg["description_swedish"] = [f"{s} {i // len(groups) + 1}" if i >= len(groups) else s for i, (s, _) in enumerate(pick)]
pg["description_english"] = [f"{e} {i // len(groups) + 1}" if i >= len(groups) else e for i, (_, e) in enumerate(pick)]
pg.loc[rng.choice(N_PRODUCT_GROUPS, 13, replace=False), ["description_swedish", "description_english"]] = np.nan

# ---------------------------------------------------------------- dim_transport (6,130 x 7)
home = [("ARN", "Stockholm"), ("GOT", "Gothenburg"), ("MMX", "Malmö"), ("CPH", "Copenhagen"), ("BLL", "Billund"),
        ("AAL", "Aalborg"), ("OSL", "Oslo"), ("BGO", "Bergen"), ("TRD", "Trondheim"), ("SVG", "Stavanger"),
        ("HEL", "Helsinki"), ("TMP", "Tampere"), ("OUL", "Oulu"), ("KEF", "Reykjavik"), ("LHR", "London"),
        ("MAN", "Manchester"), ("LPI", "Linköping"), ("NRK", "Norrköping"), ("UME", "Umeå"), ("LLA", "Luleå"),
        ("VXO", "Växjö"), ("KRS", "Kristiansand"), ("TOS", "Tromsø"), ("TKU", "Turku")]
dest = [("FAO", "Faro"), ("AGP", "Malaga"), ("ALC", "Alicante"), ("PMI", "Palma"), ("AYT", "Antalya"),
        ("LIS", "Lisbon"), ("TFS", "Tenerife"), ("RAK", "Marrakesh"), ("LCA", "Larnaca"), ("NCE", "Nice"),
        ("VLC", "Valencia"), ("FNC", "Funchal"), ("AGA", "Agadir"), ("PFO", "Paphos"), ("OPO", "Porto"),
        ("SVQ", "Seville"), ("LPA", "Gran Canaria"), ("FCO", "Rome"), ("DBV", "Dubrovnik"), ("BCN", "Barcelona"),
        ("ACE", "Lanzarote"), ("FUE", "Fuerteventura"), ("MLA", "Malta"), ("CTA", "Catania"), ("ATH", "Athens"),
        ("HER", "Crete"), ("RHO", "Rhodes"), ("SPU", "Split"), ("BJV", "Bodrum"), ("DLM", "Dalaman"),
        ("PSA", "Pisa"), ("OLB", "Sardinia"), ("BOD", "Bordeaux"), ("MRS", "Marseille"), ("MAD", "Madrid"),
        ("DXB", "Dubai"), ("BKK", "Bangkok"), ("HKT", "Phuket"), ("CUN", "Cancun"), ("MRU", "Mauritius")]
w = np.linspace(3, 0.15, len(dest)); w /= w.sum()
d_idx = rng.choice(len(dest), N_TRANSPORT, p=w)
h_idx = rng.choice(len(home), N_TRANSPORT, p=np.linspace(4, 0.2, len(home)) / np.linspace(4, 0.2, len(home)).sum())
tr = pd.DataFrame({"transport_id": range(1, N_TRANSPORT + 1),
                   "departure_airport_code": [home[i][0] for i in h_idx],
                   "departure_city": [home[i][1] for i in h_idx],
                   "arrival_airport_code": [dest[i][0] for i in d_idx],
                   "arrival_city": [dest[i][1] for i in d_idx],
                   "outbound_airline_code": rng.choice([f"X{i:02d}" for i in range(49)], N_TRANSPORT),
                   "nr_of_flight_legs": rng.choice([1, 2, 2, 2, 3, 4, 5, 6, 7, 8], N_TRANSPORT).astype(float)})
tr.loc[rng.choice(N_TRANSPORT, 18, replace=False), ["departure_airport_code", "departure_city"]] = np.nan
tr.loc[rng.choice(N_TRANSPORT, 13, replace=False), ["arrival_airport_code", "arrival_city"]] = np.nan
tr.loc[rng.choice(N_TRANSPORT, 232, replace=False), "outbound_airline_code"] = np.nan
tr.loc[rng.choice(N_TRANSPORT, 120, replace=False), "nr_of_flight_legs"] = np.nan
transport_by_city = tr.dropna(subset=["arrival_city"]).groupby("arrival_city").transport_id.apply(np.array).to_dict()

# Each destination has its own cost level and cancellation tendency, so results differ
CITY_COST = {c: rng.uniform(0.70, 0.90) for _, c in dest}
CITY_CANCEL = {c: rng.uniform(0.6, 1.4) for _, c in dest}
YEAR_CANCEL = {2020: 0.62, 2021: 0.45, 2022: 0.16}          # pandemic years cancel far more

# ---------------------------------------------------------------- dim_booking, dim_passenger
brands = ["Sunward Travel", "Blue Horizon", "Coastline Holidays", "Northern Escapes", "Island Hopper", "Active Breaks"]
bk = pd.DataFrame({"booking_id": range(1, N_BOOKINGS + 1),
                   "sales_platform": rng.choice(["Online", "Offline"], N_BOOKINGS, p=[0.72, 0.28]),
                   "brand": rng.choice(brands, N_BOOKINGS, p=[0.34, 0.24, 0.16, 0.12, 0.09, 0.05])})
agents = ["EDI", "WEB"] + [f"AGENT_{i:02d}" for i in range(1, 47)]
bk["created_by"] = np.where(bk.sales_platform == "Online", rng.choice(["EDI", "WEB"], N_BOOKINGS, p=[0.6, 0.4]),
                            rng.choice(agents[2:], N_BOOKINGS))
bk.loc[rng.choice(N_BOOKINGS, 16, replace=False), "brand"] = np.nan

pax_values = list(range(1, 21)) + [22, 24, 25, 26, 28, 30, 32, 34, 36, 38, 40, 44, 48, 52, 56, 60]
pax_p = np.r_[np.array([12, 50, 9, 14, 3, 5, 1.5, 2.5, 1, 1.2, 0.6, 0.8, .3, .3, .3, .3, .2, .2, .2, .3]),
              np.full(16, 0.05)]
pax = pd.DataFrame({"passenger_id": rng.permutation(np.arange(1, N_BOOKINGS + 1)),
                    "pax": rng.choice(pax_values, N_BOOKINGS, p=pax_p / pax_p.sum())})
booking_passenger = pax.passenger_id.to_numpy()          # booking i -> passenger booking_passenger[i-1]

# ---------------------------------------------------------------- fact_sales_and_costs (150,631 x 14)
rows_per_booking = 1 + rng.poisson(6.66, N_BOOKINGS)
diff = N_FACT_ROWS - rows_per_booking.sum()              # adjust to the exact row count
adj = rng.choice(N_BOOKINGS, abs(diff), replace=abs(diff) > N_BOOKINGS)
np.add.at(rows_per_booking, adj, np.sign(diff))
rows_per_booking = np.maximum(rows_per_booking, 1)
rows_per_booking[0] += N_FACT_ROWS - rows_per_booking.sum()

cities = list(transport_by_city)
city_p = np.array([len(transport_by_city[c]) for c in cities], float); city_p /= city_p.sum()
status = np.empty(N_BOOKINGS, dtype=object)
cols = {k: [] for k in ["booking_id", "passenger_id", "market_id", "accommodation_id", "transport_id",
                        "product_group_id", "booking_date", "cancellation_date", "first_departure_date",
                        "last_return_date", "sales_local", "sales_global", "cost_local", "cost_global"]}
MARKET_P = np.r_[[0.22, 0.14, 0.1, 0.06], [0.06] * 3, [0.05] * 3, [0.04, 0.03], 0.02, 0.01]
MARKET_P = MARKET_P / MARKET_P.sum()
dep_days = (pd.Timestamp("2022-12-31") - pd.Timestamp("2020-01-01")).days
for i in range(N_BOOKINGS):
    n = int(rows_per_booking[i])
    dep = pd.Timestamp("2020-01-01") + pd.Timedelta(days=int(rng.integers(0, dep_days + 1)))
    book = dep - pd.Timedelta(days=int(rng.gamma(2.2, 45)) + 1)
    if rng.random() < 0.01:                                 # a few data entry errors
        book = dep + pd.Timedelta(days=int(rng.integers(1, 30)))
    ret = dep + pd.Timedelta(days=int(rng.choice([4, 5, 7, 7, 7, 8, 10, 14])))
    city = rng.choice(cities, p=city_p)
    p_canc = min(0.9, YEAR_CANCEL[dep.year] * CITY_CANCEL[city])
    st = rng.choice(["Booking", "Cancellation", "Preliminary"], p=[0.97 - p_canc, p_canc, 0.03])
    status[i] = st
    canc = (min(book + pd.Timedelta(days=int(rng.integers(1, 120))), dep - pd.Timedelta(days=1))
            if st == "Cancellation" else pd.NaT)
    market = int(rng.choice(mk.market_id, p=MARKET_P))
    currency = mk.sell_currency[market - 1]
    main_tr = int(rng.choice(transport_by_city[city]))
    acc = int(rng.integers(1, N_ACCOMMODATION + 1))
    split_market = rng.random() < 0.015
    base = float(rng.lognormal(8.2, 0.6))
    for line in range(n):
        if st == "Cancellation":                             # reversal only, sometimes a small fee
            sales = -round(base * rng.uniform(0.05, 0.4), 2) if line == 0 else 0.0
        else:
            sales = round(base * rng.uniform(0.3, 1.5), 2) if rng.random() > 0.15 else 0.0
        cost = round(sales * (CITY_COST[city] + rng.normal(0, 0.05) if rng.random() > 0.03 else rng.uniform(1.0, 1.3)), 2)
        cols["booking_id"].append(i + 1)
        cols["passenger_id"].append(int(booking_passenger[i]))
        cols["market_id"].append((market % 14) + 1 if split_market and line == 1 else market)
        cols["accommodation_id"].append(acc)
        cols["transport_id"].append(main_tr if line < max(2, n // 2) else int(rng.integers(1, N_TRANSPORT + 1)))
        cols["product_group_id"].append(int(rng.integers(1, N_PRODUCT_GROUPS + 1)))
        cols["booking_date"].append(book.date())
        cols["cancellation_date"].append(canc.date() if pd.notna(canc) else None)
        cols["first_departure_date"].append(dep.date())
        cols["last_return_date"].append(ret.date())
        cols["sales_global"].append(sales)
        cols["sales_local"].append(round(sales / FX[currency], 2))
        cols["cost_global"].append(cost)
        cols["cost_local"].append(round(cost / FX[currency], 2))

fact = pd.DataFrame(cols)
nan_rows = rng.choice(len(fact), 1355, replace=False); fact.loc[nan_rows, "last_return_date"] = None
fact.loc[rng.choice(len(fact), 447, replace=False), ["cost_local", "cost_global"]] = np.nan
fact.loc[rng.choice(len(fact), 1), "sales_global"] = np.nan
bk.insert(1, "booking_status", status)

for name, df in [("fact_sales_and_costs", fact), ("dim_booking", bk), ("dim_passenger", pax),
                 ("dim_transport", tr), ("dim_market", mk), ("dim_product_group", pg)]:
    df.to_csv(OUT / f"{name}.csv", index=False)
    print(f"{name:22} {len(df):>8,} rows x {df.shape[1]} columns")
