import streamlit as st
import pandas as pd
import io
import random
from collections import defaultdict
import math

# --- DEFAULT DATA (PRE-FILLED TSV) ---
# We pre-fill all text_areas with the data you provided
# This makes the app work "out of the box"

DEFAULT_CHAPTERS_TSV = """
Chapter	Chapter Power Required
1	100
2	140
3	155
4	200
5	265
6	290
7	310
8	390
9	450
10	570
11	630
12	890
13	920
14	1380
15	1940.555556
16	2910.833333
17	4366.25
18	6549.375
19	9824.0625
20	14736.09375
21	33156.21094
22	49734.31641
23	74601.47461
24	251779.9768
25	377669.9652
26	566504.9478
27	849757.4217
28	1274636.133
29	1911954.199
30	2867931.298
31	6452845.421
32	9679268.132
33	14518902.2
34	21778353.3
35	32667529.94
36	73501942.38
37	110252913.6
38	165379370.3
39	372103583.3
40	558155374.9
41	837233062.4
42	1255849594
43	1883774390
44	4238492378
45	6357738567
46	9536607851
47	21457367665
48	32186051498
49	244412828559
50	366619242839
"""

DEFAULT_PM_TIERS_TSV = """
Tier	Tier Start	Max Bluestar Count	PM
1	0	15000	1.000693387
2	15000	30000	1.000693387
3	30000	45000	1.000693387
4	45000	60000	1.000693387
5	60000	75000	1.000693387
6	75000	90000	1.000693387
7	90000	105000	1.000693387
8	105000	120000	1.000693387
9	120000	135000	1.000693387
10	135000	150000	1.000693387
11	150000	165000	1.000693387
12	165000	180000	1.000693387
13	180000	195000	1.000693387
14	195000	210000	1.000693387
15	210000	225000	1.000693387
16	225000	240000	1.000693387
17	240000	255000	1.000693387
18	255000	270000	1.000693387
19	270000	285000	1.000693387
20	285000	300000	1.000693387
21	300000	315000	1.000693387
"""

DEFAULT_CARD_BLUE_COMMON_TSV = """
Level	Duplicates Required	Bluestar Reward	CoinsRequired
2	8	16	50
3	10	16	100
4	11	18	150
5	13	18	200
6	14	19	250
7	16	19	300
8	18	21	350
9	19	21	400
10	21	22	450
11	22	22	500
12	24	24	550
13	26	24	600
14	27	26	650
15	29	26	700
16	30	27	750
17	32	27	800
18	34	29	850
19	35	29	900
20	37	30	950
21	38	30	1000
22	40	32	1050
23	42	32	1100
24	43	34	1150
25	45	34	1200
26	46	35	1250
27	48	35	1300
28	50	37	1350
29	51	37	1400
30	53	38	1450
31	54	38	1500
32	56	40	1550
33	58	40	1600
34	59	42	1650
35	61	42	1700
36	62	43	1750
37	64	43	1800
38	66	45	1850
39	67	45	1900
40	69	46	1950
41	70	46	2000
42	72	48	2050
43	74	48	2100
44	75	50	2150
45	77	50	2200
46	78	51	2250
47	80	51	2300
48	82	53	2350
49	83	53	2400
50	85	54	2450
"""

DEFAULT_CARD_GOLD_TSV = """
Level	Duplicates Required	Bluestar Reward	CoinsRequired
2	12	24	50
3	14	24	100
4	17	26	150
5	19	26	200
6	22	29	250
7	24	29	300
8	26	31	350
9	29	31	400
10	31	34	450
11	34	34	500
12	36	36	550
13	38	36	600
14	41	38	650
15	43	38	700
16	46	41	750
17	48	41	800
18	50	43	850
19	53	43	900
20	55	46	950
21	58	46	1000
22	60	48	1050
23	62	48	1100
24	65	50	1150
25	67	50	1200
26	70	53	1250
27	72	53	1300
28	74	55	1350
29	77	55	1400
30	79	58	1450
31	82	58	1500
32	84	60	1550
33	86	60	1600
34	89	62	1650
35	91	62	1700
36	94	65	1750
37	96	65	1800
38	98	67	1850
39	101	67	1900
40	103	70	1950
41	106	70	2000
42	108	72	2050
43	110	72	2100
44	113	74	2150
45	115	74	2200
46	118	77	2250
47	120	77	2300
48	122	79	2350
49	125	79	2400
50	127	82	2450
"""

DEFAULT_CARD_UNIQUE_TSV = """
Level	Duplicates Required	Bluestar Reward	CoinsRequired
2	2	120	250
3	4	168	375
4	8	216	500
5	15	264	625
6	25	312	750
7	40	360	875
8	60	408	1000
9	90	456	1125
10	150	504	1250
"""

DEFAULT_DUPE_GRANT_SHARED_TSV = """
CardLevel	AvrgDupReq
1	0.6
2	0.6
3	0.6
4	0.6
5	0.6
6	0.6
7	0.6
8	0.6
9	0.6
10	0.6
11	0.6
12	0.6
13	0.6
14	0.6
15	0.6
16	0.6
17	0.6
18	0.6
19	0.6
20	0.6
21	0.58
22	0.58
23	0.58
24	0.58
25	0.58
26	0.58
27	0.58
28	0.58
29	0.58
30	0.58
31	0.58
32	0.58
33	0.58
34	0.58
35	0.58
36	0.58
37	0.58
38	0.58
39	0.58
40	0.58
41	0.48
42	0.48
43	0.48
44	0.48
45	0.48
46	0.48
47	0.48
48	0.48
49	0.48
50	0.48
"""

DEFAULT_DUPE_GRANT_UNIQUE_TSV = """
CardLevel	AvrgDupReq
1	0.28
2	0.28
3	0.28
4	0.28
5	0.2
6	0.2
7	0.15
8	0.15
9	0.15
10	0.15
"""

DEFAULT_PACK_EVOLUTION_TSV = """
StartingRarity	StandardPackT1	StandardPackT2	StandardPackT3	StandardPackT4	StandardPackT5
StandardPackT1	0.3164	0.4391	0.201	0.0405	0.003
StandardPackT2	0	0.3336	0.4559	0.2004	0.0101
StandardPackT3	0	0	0.4096	0.5697	0.0207
StandardPackT4	0	0	0	0.96	0.04
StandardPackT5	0	0	0	0	1
"""

DEFAULT_PACK_LOOT_SLOTS_TSV = """
Pack	BonusItemSlot
StandardPackT1	1
StandardPackT2	2
StandardPackT3	3
StandardPackT4	4
StandardPackT5	6
EndOfChapterPack	5
HeroPack	3
PetPack	4
GearPack	3
"""

DEFAULT_PACK_CARD_DRAWS_TSV = """
Pack	Unlocked Card Count	AvrgCardType
StandardPackT1	36	2
StandardPackT1	71	2.5
StandardPackT2	36	2
StandardPackT2	66	2.5
StandardPackT3	36	2.5
StandardPackT3	66	3
StandardPackT4	36	3
StandardPackT4	56	3.5
StandardPackT4	86	4
StandardPackT5	36	4
StandardPackT5	76	4.5
EndOfChapterPack	36	3
EndOfChapterPack	41	2.5
EndOfChapterPack	71	3
EndOfChapterPack	91	3.5
HeroPack	36	2.5
HeroPack	66	3
PetPack	36	2.5
PetPack	66	3
GearPack	36	2.5
GearPack	66	3
"""

DEFAULT_PACK_CARD_BOOSTS_TSV = """
Pack	SharedCardBoost	UniqueCardBoost
StandardPackT1	0
0
StandardPackT2	0.15	0.05
StandardPackT3	0.25	0.15
StandardPackT4	0.3
0.25
StandardPackT5	0.5
0.4
EndOfChapterPack	0.12	0.06
HeroPack	0.25	0.15
PetPack	0.25	0.15
GearPack	0.25	0.15
"""

DEFAULT_PACK_LOOT_PROBS_TSV = """
Pack	HeroUpgradeCards	HeroTokens	PetFood	Spirit Stone	Pet Eggs	Designs	RandomGearPiece	Coins	S-Stone	Ever Stone	Diamonds
StandardPackT1	0	0	0	0	0	0	0	1	0	0	0
StandardPackT2	0	0	0.3	0.3	0.3	0.4	0.4	1	0	0	0
StandardPackT3	0.1	0.1	0.5	0.2	0.2	0.3	0.5	1	0	0	0.15
StandardPackT4	0.2	0.2	1	0.5	0.2	0.5	0.5	1	0.01	0.05	0.25
StandardPackT5	0.5	0.5	1	1	1	1	0.5	1	0.5	0.1	0.5
EndOfChapterPack	0.5	0.5	0.5	0.5	0.5	0.5	0.5	1	0	0	0.1
HeroPack	1	1	0	0	0	0	0	1	0	0	0.1
PetPack	0	0	1	1	1	0	0	1	0	0.02	0.1
GearPack	0	0	0	0	0	1	0.5	1	0.01	0	0.1
"""

DEFAULT_PACK_LOOT_AMOUNTS_TSV = """
Pack	HeroUpgradeCards	HeroTokens	PetFood	Spirit Stone	Pet Eggs	Designs	RandomGearPiece	Coins	S-Stone	Ever Stone	Diamonds
StandardPackT1	0	0	0	0	0	0	0	80	0	0	0
StandardPackT2	0	0	20	30	30	50	2	120	0	0	0
StandardPackT3	15	5	20	200	50	300	3	300	0	0	15
StandardPackT4	30	10	50	400	100	300	2	600	1	1	15
StandardPackT5	200	150	200	500	300	300	2	1500	1	2	15
EndOfChapterPack	40	100	200	80	50	50	1	200	0	0	15
HeroPack	75	250	0	0	0	0	0	300	0	0	15
PetPack	0	0	150	300	150	0	0	300	0	2	15
GearPack	0	0	0	0	0	250	3	300	1	0	15
"""

DEFAULT_PACK_LOOT_VARIANCE_TSV = """
Pack	Bottom	Top
StandardPackT1	0.7	1.2
StandardPackT2	0.7	1.3
StandardPackT3	0.7	1.4
StandardPackT4	0.7	1.5
StandardPackT5	0.7	1.6
EndOfChapterPack	0.7	1.7
HeroPack	0.7	1.4
PetPack	0.7	1.4
GearPack	0.7	1.4
"""

DEFAULT_SEASON_PASS_TSV = """
Step	RequiredPurpleStar	FreeReward_Type	FreeReward_Amount	PaidReward_Type	PaidReward_Amount
1	0	StandardPackT1	1	StandardPackT3	1
2	5	Spirit Stone	100	S-Stone	3
3	10	CommonItem	10	GearPack	1
4	15	Diamond	5	Diamond	25
5	20	Coins	100	Blue Jokers	100
6	25	Coins	50	Coins	150
7	30	PetFood	300	PetPack	1
8	35	Coins	50	Coins	150
9	40	StandardPackT1	1	Gold Jokers	25
10	45	StandardPackT2	1	StandardPackT2	1
11	50	HeroTokens	300	HeroPack	1
12	55	Diamond	5	Diamond	25
13	60	CommonItem	10	GearPack	1
14	65	Coins	50	Coins	150
15	70	PetFood	250	Blue Jokers	100
16	75	Coins	50	Coins	150
17	80	PetFood	300	PetPack	1
18	85	Diamond	5	Diamond	25
19	90	StandardPackT1	1	Gold Jokers	25
20	95	StandardPackT2	1	StandardPackT2	1
21	100	HeroTokens	300	HeroPack	1
22	105	Coins	100	Coins	150
23	110	CommonItem	10	GearPack	1
24	115	Coins	100	Coins	150
25	120	Coins	100	Blue Jokers	100
26	125	Diamond	5	Diamond	25
27	130	PetFood	300	PetPack	1
28	135	Coins	100	Coins	150
29	140	StandardPackT1	1	Gold Jokers	25
30	145	PetPack	1	StandardPackT4	1
31	150	HeroTokens	300	HeroPack	1
32	155	Designs	100	Coins	150
33	160	CommonItem	10	GearPack	1
34	165	Diamond	5	Diamond	25
35	170	Coins	100	Blue Jokers	5
36	175	Coins	100	Coins	150
37	180	PetFood	300	PetPack	1
38	185	Coins	100	Coins	150
39	190	StandardPackT1	1	Gold Jokers	25
40	195	StandardPackT2	1	Hero Unique Jokers	5
41	200	HeroTokens	400	HeroPack	1
42	205	Diamond	10	Diamond	50
43	210	CommonItem	12	GearPack	1
44	215	Coins	150	Coins	250
45	220	Diamond	15	Blue Jokers	100
46	225	Coins	150	Coins	250
47	230	PetFood	500	PetPack	1
48	235	Coins	150	Coins	250
49	240	StandardPackT1	1	Gold Jokers	25
50	245	HeroPack	1	StandardPackT4	1
51	250	HeroTokens	400	HeroPack	1
52	255	Diamond	10	Diamond	50
53	260	CommonItem	12	GearPack	1
54	265	Coins	200	Coins	250
55	270	Diamond	15	Blue Jokers	100
56	275	Coins	200	Coins	250
57	280	PetFood	500	PetPack	1
58	285	Coins	200	Coins	250
59	290	HeroUpgradeCards	25	Gold Jokers	25
60	295	StandardPackT2	1	StandardPackT2	1
61	300	HeroTokens	400	HeroPack	1
62	305	Diamond	10	Diamond	50
63	310	CommonItem	12	GearPack	1
64	315	Coins	200	Coins	250
65	320	Diamond	15	Blue Jokers	100
66	325	Coins	200	Coins	250
67	330	PetFood	500	PetPack	1
68	335	Designs	200	Coins	250
69	340	StandardPackT1	1	Gold Jokers	25
70	345	GearPack	1	Hero Unique Jokers	5
71	350	HeroTokens	500	HeroPack	1
72	355	Diamond	15	Diamond	75
73	360	CommonItem	12	GearPack	1
Am
74	365	Coins	250	Coins	300
75	370	Diamond	15	Blue Jokers	100
76	375	Coins	250	Coins	300
77	380	PetFood	1000	PetPack	1
78	385	Spirit Stone	1000	Coins	300
79	390	StandardPackT1	1	Gold Jokers	25
80	395	StandardPackT3	1	S-Stone	1
81	400	HeroTokens	500	HeroPack	1
82	405	Diamond	15	Diamond	75
83	410	CommonItem	12	GearPack	1
84	415	HeroUpgradeCards	25	Coins	300
85	420	Coins	250	Blue Jokers	100
86	425	Coins	250	Coins	300
87	430	PetFood	1000	PetPack	1
88	435	Designs	200	Gold Jokers	25
89	440	StandardPackT2	1	StandardPackT4	1
90	445	EndOfChapterPack	1	Hero Unique Jokers	5
"""

DEFAULT_PSRACE_TSV = """
Position	RewardType	RewardAmount
1	HeroPack	2
2	HeroPack	1
3	StandardPackT2	1
4	StandardPackT1	1
5	HeroUpgradeCards	50
6	HeroUpgradeCards	50
7	HeroUpgradeCards	50
8	HeroUpgradeCards	50
9	HeroUpgradeCards	50
10	HeroUpgradeCards	50
11	HeroUpgradeCards	50
12	HeroUpgradeCards	40
13	HeroUpgradeCards	40
14	HeroUpgradeCards	40
15	HeroUpgradeCards	40
16	HeroUpgradeCards	40
17	HeroUpgradeCards	40
18	HeroUpgradeCards	40
19	HeroUpgradeCards	40
20	HeroUpgradeCards	40
21	HeroUpgradeCards	30
22	HeroUpgradeCards	30
23	HeroUpgradeCards	30
24	HeroUpgradeCards	30
25	HeroUpgradeCards	30
26	HeroUpgradeCards	30
27	HeroUpgradeCards	30
28	HeroUpgradeCards	30
29	HeroUpgradeCards	30
30	HeroUpgradeCards	30
31	HeroUpgradeCards	20
32	HeroUpgradeCards	20
33	HeroUpgradeCards	20
34	HeroUpgradeCards	20
35	HeroUpgradeCards	20
36	HeroUpgradeCards	20
37	HeroUpgradeCards	20
38	HeroUpgradeCards	20
39	HeroUpgradeCards	20
40	HeroUpgradeCards	15
41	HeroUpgradeCards	15
42	HeroUpgradeCards	15
43	HeroUpgradeCards	15
44	HeroUpgradeCards	15
45	HeroUpgradeCards	15
46	HeroUpgradeCards	15
47	HeroUpgradeCards	15
48	HeroUpgradeCards	15
49	HeroUpgradeCards	15
50	HeroUpgradeCards	15
"""

DEFAULT_BATTLERUSH_TSV = """
Stage	RewardType	RewardAmount
1	Coins	500
2	StandardPackT1	1
3	Coins	700
4	StandardPackT1	1
5	Coins	1000
6	StandardPackT2	1
7	HeroPack	1
"""

DEFAULT_CUPRACE_TSV = """
Position	RewardType1	RewardAmount1	RewardType2	RewardAmount2
1	Designs	350	S-Stone	1
2	Designs	315	GearPack	1
3	Designs	280	GearPack	1
4	Designs	175	GearPack	1
5	Designs	105	GearPack	1
6	Designs	105	GearPack	1
7	Designs	105	GearPack	1
8	Designs	105	GearPack	1
9	Designs	105	GearPack	1
10	Designs	105	GearPack	1
11	Designs	70	StandardPackT2	2
12	Designs	70	StandardPackT2	2
13	Designs	70	StandardPackT2	2
14	Designs	70	StandardPackT2	2
15	Designs	70	StandardPackT2	2
16	Designs	70	StandardPackT2	2
17	Designs	70	StandardPackT2	2
18	Designs	70	StandardPackT2	2
19	Designs	70	StandardPackT2	2
20	Designs	70	StandardPackT2	2
21	Designs	52.5	StandardPackT2	1
22	Designs	52.5	StandardPackT2	1
23	Designs	52.5	StandardPackT2	1
24	Designs	52.5	StandardPackT2	1
25	Designs	52.5	StandardPackT2	1
26	Designs	52.5	StandardPackT2	1
27	Designs	52.5	StandardPackT2	1
28	Designs	52.5	StandardPackT2	1
29	Designs	52.5	StandardPackT2	1
30	Designs	52.5	StandardPackT2	1
31	Designs	35	StandardPackT1	1
32	Designs	35	StandardPackT1	1
33	Designs	35	StandardPackT1	1
34	Designs	35	StandardPackT1	1
35	Designs	35	StandardPackT1	1
36	Designs	35	StandardPackT1	1
37	Designs	35	StandardPackT1	1
38	Designs	35	StandardPackT1	1
39	Designs	35	StandardPackT1	1
40	Designs	35	StandardPackT1	1
41	Designs	17.5	StandardPackT1	0
42	Designs	17.5	StandardPackT1	1
43	Designs	17.5	StandardPackT1	1
44	Designs	17.5	StandardPackT1	1
45	Designs	17.5	StandardPackT1	1
46	Designs	17.5	StandardPackT1	1
47	Designs	17.5	StandardPackT1	1
48	Designs	17.5	StandardPackT1	1
49	Designs	17.5	StandardPackT1	1
50	Designs	17.5	StandardPackT1	1
"""

DEFAULT_COLLECTEMALL_TSV = """
Position	RewardType1	RewardAmount1
1	StandardPackT3	1
2	StandardPackT2	3
3	StandardPackT2	2
4	StandardPackT2	1
5	StandardPackT2	1
6	StandardPackT2	1
7	StandardPackT2	1
8	StandardPackT2	1
9	StandardPackT2	1
10	StandardPackT2	1
11	StandardPackT1	1
12	StandardPackT1	1
13	StandardPackT1	1
14	StandardPackT1	1
15	StandardPackT1	1
16	StandardPackT1	1
17	StandardPackT1	1
18	StandardPackT1	1
19	StandardPackT1	1
20	StandardPackT1	1
"""

DEFAULT_INFINITEWAVES_TSV = """
Wave	Reward Type	Amount
5	PetFood	20
10	PetFood	40
15	PetEgg	10
20	Spirit Stone	20
25	PetFood	30
30	PetEgg	100
35	Everstone	1
40	Spirit Stone	50
45	PetEgg	30
50	PetFood	100
55	Everstone	1
60	PetEgg	100
65	EverStone	2
70	PetEgg	200
75	PetPack	1
80	Spirit Stone	150
85	PetEgg	250
90	PetPack	1
95	Everstone	1
100	PetEgg	300
"""

DEFAULT_INFINITEWAVES_LB_TSV = """
Rank	RewardType	Amount
1	Everstone	1
2	Everstone	1
3	Everstone	1
4	Spirit Stone	1000
5	Spirit Stone	1000
6	Spirit Stone	1000
7	Spirit Stone	1000
8	Spirit Stone	1000
9	Spirit Stone	1000
10	Spirit Stone	1000
11	Spirit Stone	500
12	Spirit Stone	500
13	Spirit Stone	500
14	Spirit Stone	500
15	Spirit Stone	500
16	Spirit Stone	500
17	Spirit Stone	500
18	Spirit Stone	500
19	Spirit Stone	500
20	Spirit Stone	500
"""

DEFAULT_HERO_UNLOCK_TSV = """
Day	New Unique Cards
1	0
10	7
20	7
30	7
40	7
50	7
60	7
70	7
80	7
90	7
100	11
"""


# --- HELPER FUNCTIONS ---

def parse_tsv(tsv_string):
    """Parses a TSV string from st.text_area into a DataFrame."""
    return pd.read_csv(io.StringIO(tsv_string), sep='\t')

@st.cache_data
def load_all_data(data_inputs):
    """Loads all TSV data into a dictionary of DataFrames."""
    data = {}
    try:
        data['chapters'] = parse_tsv(data_inputs['chapters']).set_index('Chapter')
        data['power_multipliers'] = parse_tsv(data_inputs['power_multipliers'])
        
        # Card Upgrade Tables
        data['card_upgrades'] = {
            'blue_common': parse_tsv(data_inputs['card_blue_common']).set_index('Level'),
            'gold': parse_tsv(data_inputs['card_gold']).set_index('Level'),
            'unique': parse_tsv(data_inputs['card_unique']).set_index('Level')
        }
        
        # Card Duplicate Grant Tables
        data['dupe_grant'] = {
            'shared': parse_tsv(data_inputs['dupe_grant_shared']).set_index('CardLevel'),
            'unique': parse_tsv(data_inputs['dupe_grant_unique']).set_index('CardLevel')
        }
        
        # Pack Data
        data['pack_evolution'] = parse_tsv(data_inputs['pack_evolution']).set_index('StartingRarity')
        data['pack_loot_slots'] = parse_tsv(data_inputs['pack_loot_slots']).set_index('Pack')
        
        # Handle the card draw table (it has a multi-level index)
        df_draws = parse_tsv(data_inputs['pack_card_draws'])
        df_draws['Unlocked Card Count'] = df_draws['Unlocked Card Count'].fillna(method='ffill')
        data['pack_card_draws'] = df_draws.set_index(['Pack', 'Unlocked Card Count'])
        
        data['pack_card_boosts'] = parse_tsv(data_inputs['pack_card_boosts']).set_index('Pack')
        data['pack_loot_probs'] = parse_tsv(data_inputs['pack_loot_probs']).set_index('Pack')
        data['pack_loot_amounts'] = parse_tsv(data_inputs['pack_loot_amounts']).set_index('Pack')
        data['pack_loot_variance'] = parse_tsv(data_inputs['pack_loot_variance']).set_index('Pack')
        
        # LiveOps and Season Pass
        data['season_pass'] = parse_tsv(data_inputs['season_pass']).set_index('Step')
        data['psrace'] = parse_tsv(data_inputs['psrace']).set_index('Position')
        data['battlerush'] = parse_tsv(data_inputs['battlerush']).set_index('Stage')
        data['cuprace'] = parse_tsv(data_inputs['cuprace']).set_index('Position')
        data['collectemall'] = parse_tsv(data_inputs['collectemall']).set_index('Position')
        data['infwaves'] = parse_tsv(data_inputs['infwaves']).set_index('Wave')
        data['infwaves_lb'] = parse_tsv(data_inputs['infwaves_lb']).set_index('Rank')
        
        return data
    except Exception as e:
        st.error(f"Error parsing data tables: {e}")
        st.error("Please ensure your TSV data is formatted correctly, especially the headers.")
        return None

# --- THE SIMULATION ENGINE ---

class PlayerState:
    def __init__(self, config, data):
        self.config = config
        self.data = data
        
        # Core State
        self.day = 0
        self.bluestar = 0
        self.base_power = config['starting_base_power']
        self.player_power = self.base_power
        self.current_chapter = 1
        
        # Season Pass
        self.season_pass_progress = 0
        self.season_pass_level = 1
        self.season_pass_rewards_claimed = set()

        # Inventories
        self.inventory = defaultdict(int)
        self.packs_to_open = []
        
        # Card State
        self.card_pool = {
            'blue_common': [f'bc_{i}' for i in range(1, 23)], # 14 blue + 8 common = 22
            'gold': [f'g_{i}' for i in range(1, 11)],     # 10 gold
            'unique': []                                     # Starts empty
        }
        self.unlocked_card_count = 22 + 10
        self.hero_unlock_schedule = config['hero_unlocks'].set_index('Day')
        
        self.card_levels = defaultdict(lambda: 1)
        self.card_duplicates = defaultdict(int)
        
        # Logging
        self.results_log = []

    def run_simulation(self):
        """Runs the full simulation for the specified number of days."""
        for day in range(1, self.config['sim_days'] + 1):
            self.run_day(day)
        
        final_inventory = pd.DataFrame.from_dict(self.inventory, orient='index', columns=['Amount'])
        final_inventory = final_inventory.sort_index()
        return pd.DataFrame(self.results_log), final_inventory

    def run_day(self, day):
        """Simulates a single day."""
        self.day = day
        
        self.grant_daily_rewards()
        self.check_event_schedule(day)
        self.update_season_pass(day)
        self.check_hero_unlocks(day)
        
        self.process_packs()
        self.run_all_upgrades()
        self.update_power()
        self.check_chapter_progression() # This can grant new packs
        
        # Process any packs gained from progression
        if self.packs_to_open:
            self.process_packs()
            self.run_all_upgrades()
            self.update_power()
            # We check one more time in case an upgrade pushed us past another chapter
            self.check_chapter_progression() 
        
        self.log_state()

    def grant_daily_rewards(self):
        self.packs_to_open.append('StandardPackT2')
        self.packs_to_open.extend(['StandardPackT1'] * 3)
        self.season_pass_progress += self.config['daily_purple_stars']

    def check_event_schedule(self, day):
        # Weekly events
        if (day - 1) % 7 == 0:
            self.grant_liveops_reward('psrace', self.config['ps_rank'])
            self.grant_liveops_reward('cuprace', self.config['cup_rank'])
            self.grant_liveops_reward('collectemall', self.config['collect_rank'])
        
        # Bi-weekly (every 14 days)
        if (day - 1) % 14 == 0:
            # BattleRush: Grant all rewards *up to* the selected stage
            for stage in range(1, self.config['battlerush_stage'] + 1):
                self.grant_liveops_reward('battlerush', stage)
        
        # Every 2 days
        if (day - 1) % 2 == 0:
            # Infinite Waves: Grant all wave rewards *up to* selected wave
            for wave in self.data['infwaves'].index:
                if wave <= self.config['infwaves_wave']:
                    self.grant_liveops_reward('infwaves', wave)
            # Grant leaderboard reward
            self.grant_liveops_reward('infwaves_lb', self.config['infwaves_rank'])

    def grant_liveops_reward(self, table_name, key):
        """Grants a reward from a LiveOps table."""
        try:
            reward_data = self.data[table_name].loc[key]
            
            # Handle tables with one reward (PSRace, BattleRush, InfWaves)
            if 'RewardType' in reward_data:
                self.add_to_inventory(reward_data['RewardType'], reward_data['RewardAmount'])
            
            # Handle tables with two rewards (CupRace)
            if 'RewardType1' in reward_data:
                self.add_to_inventory(reward_data['RewardType1'], reward_data['RewardAmount1'])
            if 'RewardType2' in reward_data and pd.notna(reward_data['RewardType2']):
                self.add_to_inventory(reward_data['RewardType2'], reward_data['RewardAmount2'])
                
        except KeyError:
            pass # No reward for this rank/stage
        except Exception as e:
            st.warning(f"Error granting reward {table_name} for key {key}: {e}")

    def update_season_pass(self, day):
        if (day - 1) % 28 == 0 and day > 1:
            self.season_pass_progress = self.config['daily_purple_stars'] # Reset but include today's stars
            self.season_pass_rewards_claimed.clear()
            self.season_pass_level = 1

        pass_table = self.data['season_pass']
        
        # Check all levels player might have achieved
        unlocked_levels = pass_table[pass_table['RequiredPurpleStar'] <= self.season_pass_progress]
        
        for step, row in unlocked_levels.iterrows():
            if step not in self.season_pass_rewards_claimed:
                # Grant Free Reward
                self.add_to_inventory(row['FreeReward_Type'], row['FreeReward_Amount'])
                
                # Grant Paid Reward
                if self.config['is_paid_player']:
                    self.add_to_inventory(row['PaidReward_Type'], row['PaidReward_Amount'])
                
                self.season_pass_rewards_claimed.add(step)
                self.season_pass_level = max(self.season_pass_level, step)

    def check_hero_unlocks(self, day):
        if day in self.hero_unlock_schedule.index:
            new_cards = self.hero_unlock_schedule.loc[day, 'New Unique Cards']
            current_max = len(self.card_pool['unique'])
            for i in range(1, new_cards + 1):
                self.card_pool['unique'].append(f'u_{current_max + i}')
            self.unlocked_card_count += new_cards

    def process_packs(self):
        """Opens all packs in the queue."""
        packs_to_process = self.packs_to_open[:]
        self.packs_to_open = []
        
        for pack_name in packs_to_process:
            if "StandardPack" in pack_name:
                pack_name = self.get_pack_evolution(pack_name)
            self.open_pack(pack_name)

    def get_pack_evolution(self, pack_name):
        """Rolls for pack evolution."""
        if pack_name not in self.data['pack_evolution'].index:
            return pack_name
            
        row = self.data['pack_evolution'].loc[pack_name]
        tiers = row.index
        probs = row.values
        return random.choices(tiers, weights=probs, k=1)[0]

    def open_pack(self, pack_name):
        """Opens a single pack and grants cards and items."""
        if pack_name not in self.data['pack_loot_slots'].index:
            st.warning(f"Unknown pack type: {pack_name}")
            return

        # 1. Grant Card Piles
        self.grant_card_piles(pack_name)
        
        # 2. Grant Bonus Items
        num_bonus_slots = self.data['pack_loot_slots'].loc[pack_name, 'BonusItemSlot']
        loot_probs = self.data['pack_loot_probs'].loc[pack_name]
        loot_amounts = self.data['pack_loot_amounts'].loc[pack_name]
        variance = self.data['pack_loot_variance'].loc[pack_name]
        
        # Handle 100% prob items (like Coins) - they drop first and use a slot
        guaranteed_items = loot_probs[loot_probs == 1].index
        for item in guaranteed_items:
            if num_bonus_slots > 0:
                self.grant_bonus_item(item, loot_amounts, variance)
                num_bonus_slots -= 1
        
        # Roll for remaining slots from non-guaranteed items
        remaining_items = loot_probs[loot_probs < 1]
        
        for _ in range(num_bonus_slots):
            # Roll for an item
            item_probs = remaining_items.values
            item_names = remaining_items.index
            
            # Normalize probabilities (they may not sum to 1)
            total_prob = sum(item_probs)
            if total_prob > 0:
                normalized_probs = [p / total_prob for p in item_probs]
                
                # Check if we get any of these items at all
                if random.random() < total_prob: # This simulates the chance of getting "nothing"
                    chosen_item = random.choices(item_names, weights=normalized_probs, k=1)[0]
                    self.grant_bonus_item(chosen_item, loot_amounts, variance)

    def grant_card_piles(self, pack_name):
        """Grants the card piles from a pack."""
        # Find the correct row for AvrgCardType based on unlocked_card_count
        draw_rules = self.data['pack_card_draws'].loc[pack_name]
        correct_rule = draw_rules[draw_rules.index <= self.unlocked_card_count].iloc[-1]
        num_card_types = int(round(correct_rule['AvrgCardType']))

        for _ in range(num_card_types):
            card_name, card_type = self.pick_random_card()
            if card_name is None:
                continue # No cards of this type unlocked
                
            current_level = self.card_levels[card_name]
            
            # Get upgrade info for NEXT level
            upgrade_table_name = 'unique' if card_type == 'unique' else 'blue_common' if card_type == 'blue_common' else 'gold'
            dupe_grant_table_name = 'unique' if card_type == 'unique' else 'shared'

            try:
                upgrade_info = self.data['card_upgrades'][upgrade_table_name].loc[current_level + 1]
                dupes_required = upgrade_info['Duplicates Required']
                
                # Get base grant %
                grant_info = self.data['dupe_grant'][dupe_grant_table_name]
                base_grant_perc = grant_info[grant_info.index <= current_level].iloc[-1]['AvrgDupReq']
                
                # Get pack boost
                boosts = self.data['pack_card_boosts'].loc[pack_name]
                boost_perc = boosts['UniqueCardBoost'] if card_type == 'unique' else boosts['SharedCardBoost']
                
                # Calculate final duplicates
                total_dupes = math.ceil(dupes_required * (base_grant_perc + boost_perc))
                self.card_duplicates[card_name] += total_dupes
                
            except KeyError:
                pass # Card is max level

    def pick_random_card(self):
        """Picks a random card from the available pool."""
        pool_weights = [len(self.card_pool['blue_common']), len(self.card_pool['gold']), len(self.card_pool['unique'])]
        if sum(pool_weights) == 0:
            return None, None
            
        card_type = random.choices(['blue_common', 'gold', 'unique'], weights=pool_weights, k=1)[0]
        
        if not self.card_pool[card_type]:
            return None, None # No cards of this type unlocked
            
        card_name = random.choice(self.card_pool[card_type])
        return card_name, card_type

    def grant_bonus_item(self, item, amounts, variance):
        """Helper to add a non-card item to inventory with variance."""
        base_amount = amounts[item]
        min_mult = variance['Bottom']
        max_mult = variance['Top']
        
        amount = math.ceil(base_amount * random.uniform(min_mult, max_mult))
        self.add_to_inventory(item, amount)

    def add_to_inventory(self, item_type, amount):
        """Adds an item or pack to the correct inventory/queue."""
        if pd.isna(item_type) or amount == 0:
            return
            
        amount = int(amount)
        if "Pack" in item_type:
            self.packs_to_open.extend([item_type] * amount)
        else:
            self.inventory[item_type] += amount

    def run_all_upgrades(self):
        """Attempts to upgrade all cards."""
        upgraded_something = True
        while upgraded_something:
            upgraded_something = False
            for card_name, current_level in self.card_levels.items():
                card_type = 'unique' if 'u_' in card_name else 'gold' if 'g_' in card_name else 'blue_common'
                upgrade_table = self.data['card_upgrades'][card_type]
                
                next_level = current_level + 1
                if next_level in upgrade_table.index:
                    costs = upgrade_table.loc[next_level]
                    dupe_cost = costs['Duplicates Required']
                    coin_cost = costs['CoinsRequired']
                    
                    if self.card_duplicates[card_name] >= dupe_cost and self.inventory['Coins'] >= coin_cost:
                        # Perform upgrade
                        self.card_duplicates[card_name] -= dupe_cost
                        self.inventory['Coins'] -= coin_cost
                        self.card_levels[card_name] = next_level
                        
                        bluestar_reward = costs['Bluestar Reward']
                        self.bluestar += bluestar_reward
                        
                        upgraded_something = True # We changed state, so loop again

    def update_power(self):
        """Recalculates player power based on bluestar count."""
        pm_table = self.data['power_multipliers']
        # Find the correct tier
        tier = pm_table[pm_table['Tier Start'] <= self.bluestar].iloc[-1]
        pm = tier['PM']
        
        self.player_power = self.base_power * (pm ** self.bluestar)

    def check_chapter_progression(self):
        """Checks if the player can beat the current chapter."""
        try:
            chapter_req = self.data['chapters'].loc[self.current_chapter, 'Chapter Power Required']
            
            while self.player_power > chapter_req:
                # Beat chapter
                self.add_to_inventory('EndOfChapterPack', 1)
                self.current_chapter += 1
                
                # Check next chapter
                if self.current_chapter in self.data['chapters'].index:
                    chapter_req = self.data['chapters'].loc[self.current_chapter, 'Chapter Power Required']
                else:
                    break # Beat all chapters
        except KeyError:
            pass # No more chapters defined

    def log_state(self):
        """Logs the current player state for charts."""
        chapter_req = 0
        if self.current_chapter in self.data['chapters'].index:
            chapter_req = self.data['chapters'].loc[self.current_chapter, 'Chapter Power Required']
            
        self.results_log.append({
            'Day': self.day,
            'Bluestar': self.bluestar,
            'PlayerPower': self.player_power,
            'Chapter': self.current_chapter,
            'ChapterPowerRequirement': chapter_req,
            'Coins': self.inventory['Coins'],
            'UnlockedCards': self.unlocked_card_count
        })

# --- STREAMLIT UI ---

def main_app():
    st.set_page_config(layout="wide")
    st.title("📈 Roguelike Economy Simulator")

    # --- SIDEBAR (Inputs) ---
    with st.sidebar:
        st.header("Simulation Config")
        
        if st.button("Run Simulation", type="primary"):
            # 1. Collate all config
            config = {
                'sim_days': st.session_state.sim_days,
                'is_paid_player': st.session_state.is_paid_player,
                'starting_base_power': st.session_state.starting_base_power,
                'daily_purple_stars': st.session_state.daily_purple_stars,
                'hero_unlocks': st.session_state.hero_unlocks,
                'ps_rank': st.session_state.ps_rank,
                'cup_rank': st.session_state.cup_rank,
                'collect_rank': st.session_state.collect_rank,
                'battlerush_stage': st.session_state.battlerush_stage,
                'infwaves_wave': st.session_state.infwaves_wave,
                'infwaves_rank': st.session_state.infwaves_rank
            }
            
            # 2. Collate all data
            data_inputs = {
                'chapters': st.session_state.chapters_tsv,
                'power_multipliers': st.session_state.pm_tiers_tsv,
                'card_blue_common': st.session_state.card_blue_common_tsv,
                'card_gold': st.session_state.card_gold_tsv,
                'card_unique': st.session_state.card_unique_tsv,
                'dupe_grant_shared': st.session_state.dupe_grant_shared_tsv,
                'dupe_grant_unique': st.session_state.dupe_grant_unique_tsv,
                'pack_evolution': st.session_state.pack_evolution_tsv,
                'pack_loot_slots': st.session_state.pack_loot_slots_tsv,
                'pack_card_draws': st.session_state.pack_card_draws_tsv,
                'pack_card_boosts': st.session_state.pack_card_boosts_tsv,
                'pack_loot_probs': st.session_state.pack_loot_probs_tsv,
                'pack_loot_amounts': st.session_state.pack_loot_amounts_tsv,
                'pack_loot_variance': st.session_state.pack_loot_variance_tsv,
                'season_pass': st.session_state.season_pass_tsv,
                'psrace': st.session_state.psrace_tsv,
                'battlerush': st.session_state.battlerush_tsv,
                'cuprace': st.session_state.cuprace_tsv,
                'collectemall': st.session_state.collectemall_tsv,
                'infwaves': st.session_state.infwaves_tsv,
                'infwaves_lb': st.session_state.infwaves_lb_tsv
            }
            
            # 3. Load data and run sim
            with st.spinner("Loading data..."):
                all_data = load_all_data(data_inputs)
            
            if all_data:
                with st.spinner(f"Running simulation for {config['sim_days']} days..."):
                    player = PlayerState(config, all_data)
                    results_log, final_inventory = player.run_simulation()
                    
                    # 4. Save to session state
                    st.session_state.results = results_log
                    st.session_state.inventory = final_inventory
                st.success("Simulation Complete!")
        
        st.subheader("General Settings")
        st.number_input("Simulation Days", 1, 1000, 365, key="sim_days")
        st.toggle("Paid Season Pass Player?", value=True, key="is_paid_player")
        
        st.subheader("Core Assumptions")
        st.number_input("Starting Base Power", value=100.0, format="%.1f", key="starting_base_power")
        st.number_input("Daily Purple Stars", value=12, key="daily_purple_stars")
        
        st.subheader("Hero Unlock Schedule")
        st.data_editor(
            parse_tsv(DEFAULT_HERO_UNLOCK_TSV),
            num_rows="dynamic",
            key="hero_unlocks"
        )

        st.subheader("LiveOps Ranks / Progress")
        st.slider("PSRace Rank (Weekly)", 1, 50, 5, key="ps_rank")
        st.slider("Cup Race Rank (Weekly)", 1, 50, 10, key="cup_rank")
        st.slider("Collect 'em All Rank (Weekly)", 1, 20, 10, key="collect_rank")
        st.slider("BattleRush Stage (Bi-Weekly)", 1, 7, 7, key="battlerush_stage")
        st.slider("Infinite Waves Reached (Every 2 Days)", 0, 100, 50, key="infwaves_wave")
        st.slider("Infinite Waves Rank (Every 2 Days)", 1, 20, 10, key="infwaves_rank")
        
        # --- Data Tables ---
        with st.expander("Edit All Economy Data (TSV)"):
            st.text_area("Chapters Table", DEFAULT_CHAPTERS_TSV, height=200, key="chapters_tsv")
            st.text_area("Bluestar Power Tiers", DEFAULT_PM_TIERS_TSV, height=200, key="pm_tiers_tsv")
            st.text_area("Blue/Common Card Upgrades", DEFAULT_CARD_BLUE_COMMON_TSV, height=200, key="card_blue_common_tsv")
            st.text_area("Gold Card Upgrades", DEFAULT_CARD_GOLD_TSV, height=200, key="card_gold_tsv")
            st.text_area("Unique Card Upgrades", DEFAULT_CARD_UNIQUE_TSV, height=200, key="card_unique_tsv")
            st.text_area("Shared Dupe Grant %", DEFAULT_DUPE_GRANT_SHARED_TSV, height=200, key="dupe_grant_shared_tsv")
            st.text_area("Unique Dupe Grant %", DEFAULT_DUPE_GRANT_UNIQUE_TSV, height=200, key="dupe_grant_unique_tsv")
            st.text_area("Pack Evolution", DEFAULT_PACK_EVOLUTION_TSV, height=200, key="pack_evolution_tsv")
            st.text_area("Pack Loot Slots", DEFAULT_PACK_LOOT_SLOTS_TSV, height=200, key="pack_loot_slots_tsv")
            st.text_area("Pack Card Draws", DEFAULT_PACK_CARD_DRAWS_TSV, height=200, key="pack_card_draws_tsv")
            st.text_area("Pack Card Boosts", DEFAULT_PACK_CARD_BOOSTS_TSV, height=200, key="pack_card_boosts_tsv")
            st.text_area("Pack Loot Probabilities", DEFAULT_PACK_LOOT_PROBS_TSV, height=200, key="pack_loot_probs_tsv")
            st.text_area("Pack Loot Amounts", DEFAULT_PACK_LOOT_AMOUNTS_TSV, height=200, key="pack_loot_amounts_tsv")
            st.text_area("Pack Loot Variance", DEFAULT_PACK_LOOT_VARIANCE_TSV, height=200, key="pack_loot_variance_tsv")
            st.text_area("Season Pass", DEFAULT_SEASON_PASS_TSV, height=200, key="season_pass_tsv")
            st.text_area("PSRace Rewards", DEFAULT_PSRACE_TSV, height=200, key="psrace_tsv")
            st.text_area("BattleRush Rewards", DEFAULT_BATTLERUSH_TSV, height=200, key="battlerush_tsv")
            st.text_area("CupRace Rewards", DEFAULT_CUPRACE_TSV, height=200, key="cuprace_tsv")
            st.text_area("CollectEmAll Rewards", DEFAULT_COLLECTEMALL_TSV, height=200, key="collectemall_tsv")
            st.text_area("InfWaves Rewards", DEFAULT_INFINITEWAVES_TSV, height=200, key="infwaves_tsv")
            st.text_area("InfWaves LB Rewards", DEFAULT_INFINITEWAVES_LB_TSV, height=200, key="infwaves_lb_tsv")


    # --- MAIN PAGE (Outputs) ---
    if "results" not in st.session_state:
        st.info("Configure your inputs in the sidebar and press 'Run Simulation'.")
    else:
        results = st.session_state.results
        inventory = st.session_state.inventory
        
        st.header("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        final_bluestar = results.iloc[-1]['Bluestar']
        final_power = results.iloc[-1]['PlayerPower']
        final_chapter = results.iloc[-1]['Chapter']
        final_coins = results.iloc[-1]['Coins']
        
        col1.metric("Final Bluestar", f"{final_bluestar:,.0f}")
        col2.metric("Final Player Power", f"{final_power:.2e}")
        col3.metric("Final Chapter", f"{final_chapter}")
        col4.metric("Final Coins", f"{final_coins:,.0f}")
        
        st.header("Player Progression")
        st.subheader("Player Power vs. Chapter Requirement")
        st.line_chart(results, x="Day", y=["PlayerPower", "ChapterPowerRequirement"], log_y=True)
        
        st.subheader("Bluestar Growth")
        st.line_chart(results, x="Day", y="Bluestar")
        
        with st.expander("Final Inventory"):
            st.dataframe(inventory)
            
        with st.expander("Daily Simulation Log"):
            st.dataframe(results)

if __name__ == "__main__":
    main_app()