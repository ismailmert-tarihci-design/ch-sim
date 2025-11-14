import streamlit as st
import pandas as pd
import io
import random
from collections import defaultdict
import math
from streamlit_gsheets import GSheetsConnection  # New import

# --- NO MORE DEFAULT DATA! ---
# All data will be loaded from Google Sheets

# --- HELPER FUNCTIONS ---

@st.cache_data(ttl=600)  # Cache data for 10 minutes
def load_all_data():
    """Loads all data from the Google Sheet."""
    try:
        # Create connection
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Define all the worksheet names
        worksheet_names = [
            'Chapters', 'PowerTiers', 'CardBlueCommon', 'CardGold', 'CardUnique',
            'DupeGrantShared', 'DupeGrantUnique', 'PackEvolution', 'PackLootSlots',
            'PackCardDraws', 'PackCardBoosts', 'PackLootProbs', 'PackLootAmounts',
            'PackLootVariance', 'SeasonPass', 'PSRace', 'BattleRush', 'CupRace',
            'CollectEmAll', 'InfWaves', 'InfWavesLB', 'HeroUnlocks'
        ]
        
        # Read all worksheets into a dictionary of DataFrames
        df_dict = conn.read_all(worksheet_names=worksheet_names)
        
        # --- Process and structure the data ---
        data = {}
        
        data['chapters'] = df_dict['Chapters'].set_index('Chapter')
        data['power_multipliers'] = df_dict['PowerTiers']
        
        # Card Upgrade Tables
        data['card_upgrades'] = {
            'blue_common': df_dict['CardBlueCommon'].set_index('Level'),
            'gold': df_dict['CardGold'].set_index('Level'),
            'unique': df_dict['CardUnique'].set_index('Level')
        }
        
        # Card Duplicate Grant Tables
        data['dupe_grant'] = {
            'shared': df_dict['DupeGrantShared'].set_index('CardLevel'),
            'unique': df_dict['DupeGrantUnique'].set_index('CardLevel')
        }
        
        # Pack Data
        data['pack_evolution'] = df_dict['PackEvolution'].set_index('StartingRarity')
        data['pack_loot_slots'] = df_dict['PackLootSlots'].set_index('Pack')
        
        # Handle the card draw table (it has a multi-level index)
        df_draws = df_dict['PackCardDraws']
        df_draws['Unlocked Card Count'] = df_draws['Unlocked Card Count'].fillna(method='ffill')
        data['pack_card_draws'] = df_draws.set_index(['Pack', 'Unlocked Card Count'])
        
        data['pack_card_boosts'] = df_dict['PackCardBoosts'].set_index('Pack')
        data['pack_loot_probs'] = df_dict['PackLootProbs'].set_index('Pack')
        data['pack_loot_amounts'] = df_dict['PackLootAmounts'].set_index('Pack')
        data['pack_loot_variance'] = df_dict['PackLootVariance'].set_index('Pack')
        
        # LiveOps and Season Pass
        data['season_pass'] = df_dict['SeasonPass'].set_index('Step')
        data['psrace'] = df_dict['PSRace'].set_index('Position')
        data['battlerush'] = df_dict['BattleRush'].set_index('Stage')
        data['cuprace'] = df_dict['CupRace'].set_index('Position')
        data['collectemall'] = df_dict['CollectEmAll'].set_index('Position')
        data['infwaves'] = df_dict['InfWaves'].set_index('Wave')
        data['infwaves_lb'] = df_dict['InfWavesLB'].set_index('Rank')
        
        # This will be used by the config, not the data dict
        data['hero_unlocks'] = df_dict['HeroUnlocks'] 
        
        return data
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        st.error("Please check your Google Sheet sharing settings and tab names.")
        return None

# --- THE SIMULATION ENGINE ---

class PlayerState:
    # --- THIS IS THE BUG FIX ---
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
        
        # Convert hero_unlocks from config to a DataFrame
        hero_unlock_df = pd.DataFrame(config['hero_unlocks'])
        if not hero_unlock_df.empty:
            # If it's not empty, set the index
            self.hero_unlock_schedule = hero_unlock_df.set_index('Day')
        else:
            # If it is empty, create an empty schedule so the app doesn't crash
            empty_index = pd.Index([], name='Day')
            self.hero_unlock_schedule = pd.DataFrame(columns=['New Unique Cards'], index=empty_index)

        self.card_levels = defaultdict(lambda: 1)
        self.card_duplicates = defaultdict(int)
        
        # Logging
        self.results_log = []
    
    # ... (Rest of the PlayerState class from the previous answer) ...
    # ... (run_simulation, run_day, grant_daily_rewards, etc... ALL THE SAME) ...
    
    # (Paste the entire rest of the PlayerState class here)
    # (from run_simulation() all the way to log_state())

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
            # Handle potential multiple entries for the same day
            new_cards_entries = self.hero_unlock_schedule.loc[day]
            if isinstance(new_cards_entries, pd.Series):
                new_cards = new_cards_entries['New Unique Cards']
            else:
                new_cards = new_cards_entries['New Unique Cards'].sum()

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
            
        amount = int(round(float(amount))) # Ensure amount is a rounded integer
        if "Pack" in str(item_type):
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
    
    # Load all data from GSheets at the start
    all_data = load_all_data()

    # --- SIDEBAR (Inputs) ---
    with st.sidebar:
        st.header("Simulation Config")
        
        if 'all_data' not in st.session_state:
            if all_data:
                st.session_state.all_data = all_data
            else:
                st.error("Failed to load data. App cannot run.")
                return

        if st.button("Run Simulation", type="primary"):
            # 1. Collate all config
            config = {
                'sim_days': st.session_state.sim_days,
                'is_paid_player': st.session_state.is_paid_player,
                'starting_base_power': st.session_state.starting_base_power,
                'daily_purple_stars': st.session_state.daily_purple_stars,
                'hero_unlocks': st.session_state.all_data['hero_unlocks'], # Get from loaded data
                'ps_rank': st.session_state.ps_rank,
                'cup_rank': st.session_state.cup_rank,
                'collect_rank': st.session_state.collect_rank,
                'battlerush_stage': st.session_state.battlerush_stage,
                'infwaves_wave': st.session_state.infwaves_wave,
                'infwaves_rank': st.session_state.infwaves_rank
            }
            
            # 2. Run sim
            with st.spinner(f"Running simulation for {config['sim_days']} days..."):
                player = PlayerState(config, st.session_state.all_data)
                results_log, final_inventory = player.run_simulation()
                
                # 3. Save to session state
                st.session_state.results = results_log
                st.session_state.inventory = final_inventory
            st.success("Simulation Complete!")
        
        st.subheader("General Settings")
        st.number_input("Simulation Days", 1, 1000, 365, key="sim_days")
        st.toggle("Paid Season Pass Player?", value=True, key="is_paid_player")
        
        st.subheader("Core Assumptions")
        st.number_input("Starting Base Power", value=100.0, format="%.1f", key="starting_base_power")
        st.number_input("Daily Purple Stars", value=12, key="daily_purple_stars")

        st.subheader("LiveOps Ranks / Progress")
        st.slider("PSRace Rank (Weekly)", 1, 50, 5, key="ps_rank")
        st.slider("Cup Race Rank (Weekly)", 1, 50, 10, key="cup_rank")
        st.slider("Collect 'em All Rank (Weekly)", 1, 20, 10, key="collect_rank")
        st.slider("BattleRush Stage (Bi-Weekly)", 1, 7, 7, key="battlerush_stage")
        st.slider("Infinite Waves Reached (Every 2 Days)", 0, 100, 50, key="infwaves_wave")
        st.slider("Infinite Waves Rank (Every 2 Days)", 1, 20, 10, key="infwaves_rank")
        
        st.caption("All economy data (packs, cards, etc.) is loaded from the connected Google Sheet. Edit the sheet to see changes here.")


    # --- MAIN PAGE (Outputs) ---
    if "results" not in st.session_state:
        st.info("Configure your inputs in the sidebar and press 'Run Simulation'.")
        st.info("Data is loaded live from your connected Google Sheet.")
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