# import random
# from pypokerengine.players import BasePokerPlayer

# # Notes
# # All cards follow this format: Suit + Rank : 4 of Hearts = 4H, 10 of Spades = ST [2,3,4,5,6,7,8,9,T,J,Q,K,A] [S,C,D,H]

# def setup_ai():
#     return MyBot()

# class MyBot(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

#     #  we define the logic to make an action through this method. (so this method would be the core of your AI)
#     def declare_action(self, valid_actions, hole_card, round_state):
#         # For your convenience:
#         community_card = round_state['community_card']                  # array, starting from [] to [] of 5 elems
#         street = round_state['street']                                  # preflop, flop, turn, river
#         pot = round_state['pot']                                        # dict : {'main': {'amount': int}, 'side': {'amount': int}}
#         dealer_btn = round_state['dealer_btn']                          # int : user id of the player acting as the dealer
#         next_player = round_state['next_player']                        # int : user id of next player
#         small_blind_pos = round_state['small_blind_pos']                # int : user id of player with small blind (next player is big blind)
#         big_blind_pos = round_state['big_blind_pos']                    # int : user id of player with big blind
#         round_count = round_state['round_count']                        # int : round number
#         small_blind_amount = round_state['small_blind_amount']          # int : amount of starting small blind
#         seats = round_state['seats']                                    # {'name' : the AI name, 'uuid': their user id, 'stack': their stack/remaining money, 'state': participating/folded}
#                                                                         # we recommend if you're going to try to find your own user id, name your own class name and ai name the same
#         action_histories = round_state['action_histories']              # {'preflop': [{'action': 'SMALLBLIND', 'amount': 10, 'add_amount': 10, 'uuid': '1'}, {'action': 'BIGBLIND', 'amount': 20, 'add_amount': 10, 'uuid': '2'},
#                                                                         #   {'action': 'CALL', 'amount': 20, 'paid': 20, 'uuid': '3'}, {'action': 'CALL', 'amount': 20, 'paid': 20, 'uuid': '0'}, 
#                                                                         #   {'action': 'CALL', 'amount': 20, 'paid': 10, 'uuid': '1'}, {'action': 'FOLD', 'uuid': '2'}]}   -- sample action history for preflop
#                                                                         # {'flop': [{'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': '1'}]}  -- sample for flop

#         # Minimum and maximum raise values (max raise ==> all in)
#         min_raise = valid_actions[2]['amount']['min']
#         max_raise = valid_actions[2]['amount']['max']


#         # --------------------------------------------------------------------------------------------------------#
        
#         # Sample code: feel free to rewrite
#         action = random.choice(valid_actions)["action"]
#         if action == "raise":
#             action_info = valid_actions[2]
#             amount = random.randint(action_info["amount"]["min"], action_info["amount"]["max"])
#             if amount == -1: action = "call"
#         if action == "call":
#             return self.do_call(valid_actions)
#         if action == "fold":
#             return self.do_fold(valid_actions)
#         return self.do_raise(valid_actions, amount)   # action returned here is sent to the poker engine
    
#         # -------------------------------------------------------------------------------------------------------#
#         # Make sure that you call one of the actions (self.do_fold, self.do_call, self.do_raise, self.do_all_in)
#         # All in is defined as raise using all of your remaining stack (chips)



#     def receive_game_start_message(self, game_info):
#         # Predefined variables for various game information --  feel free to use them however you like
#         player_num = game_info["player_num"]
#         max_round = game_info["rule"]["max_round"]
#         small_blind_amount = game_info["rule"]["small_blind_amount"]
#         ante_amount = game_info["rule"]["ante"]
#         blind_structure = game_info["rule"]["blind_structure"]

#     def receive_round_start_message(self, round_count, hole_card, seats):
#         pass

#     def receive_street_start_message(self, street, round_state):
#         pass

#     def receive_game_update_message(self, action, round_state):
#         pass

#     def receive_round_result_message(self, winners, hand_info, round_state):
#         pass


#     # Helper functions  -- call these in the declare_action function to declare your move
#     def do_fold(self, valid_actions):
#         action_info = valid_actions[0]
#         amount = action_info["amount"]
#         return action_info['action'], amount

#     def do_call(self, valid_actions):
#         action_info = valid_actions[1]
#         amount = action_info["amount"]
#         return action_info['action'], amount
    
#     def do_raise(self,  valid_actions, raise_amount):
#         action_info = valid_actions[2]
#         amount = max(action_info['amount']['min'], raise_amount)
#         return action_info['action'], amount
    
#     def do_all_in(self,  valid_actions):
#         action_info = valid_actions[2]
#         amount = action_info['amount']['max']
#         return action_info['action'], amount


# FIRST ATTEMPT ------------------------------------------------------------

import random
from pypokerengine.players import BasePokerPlayer
from collections import defaultdict

class MillionDollarBot(BasePokerPlayer):
    def __init__(self):
        super().__init__()
        self.opponent_stats = defaultdict(lambda: {
            'vpip': 0,  # Voluntarily put $ in pot
            'pfr': 0,   # Pre-flop raise
            'aggression': 0,
            'fold_to_raise': 0,
            'actions': 0
        })
        self.hand_strength_cache = {}
        self.position = None
        self.current_street = None
        self.hole_cards = None

    def declare_action(self, valid_actions, hole_card, round_state):
        self.hole_cards = hole_card
        self.current_street = round_state['street']
        self.update_position(round_state)
        self.update_opponent_stats(round_state)
        
        # Calculate hand strength and potential
        hand_strength = self.calculate_hand_strength(hole_card, round_state['community_card'])
        hand_potential = self.calculate_hand_potential(hole_card, round_state['community_card'])
        
        # Get opponent tendencies
        opponent_tightness = self.get_opponent_tightness(round_state)
        opponent_aggression = self.get_opponent_aggression(round_state)
        
        # Calculate pot odds
        pot_odds = self.calculate_pot_odds(valid_actions, round_state['pot'])
        
        # Implement mixed strategy with GTO principles
        action = self.determine_optimal_action(
            hand_strength,
            hand_potential,
            pot_odds,
            opponent_tightness,
            opponent_aggression,
            valid_actions,
            round_state
        )
        
        return action

    # ------------------- Core Calculation Methods ------------------- #

    def calculate_hand_strength(self, hole_cards, community_cards):
        """Evaluate hand strength from 0 (weakest) to 1 (strongest)"""
        if len(community_cards) == 0:  # Pre-flop
            return self._preflop_strength(hole_cards)
        return self._postflop_strength(hole_cards, community_cards)

    def _preflop_strength(self, hole_cards):
        # Premium hands
        ranks = sorted([card[1] for card in hole_cards], reverse=True)
        suited = hole_cards[0][0] == hole_cards[1][0]
        
        # Pocket pairs
        if ranks[0] == ranks[1]:
            pair_rank = ranks[0]
            if pair_rank in ['A', 'K', 'Q', 'J', 'T']:
                return 0.9 + (['A', 'K', 'Q', 'J', 'T'].index(pair_rank) * 0.02)
            return 0.7 + (int(pair_rank)/14)
        
        # Suited connectors
        if suited and abs('23456789TJQKA'.index(ranks[0]) - '23456789TJQKA'.index(ranks[1])) == 1:
            if ranks[0] in ['A', 'K', 'Q']:
                return 0.65
            return 0.55
        
        # High cards
        high_card_strength = sum(['AKQJT'.index(c) for c in ranks if c in 'AKQJT']) / 10
        return high_card_strength if suited else high_card_strength * 0.8

    def _postflop_strength(self, hole_cards, community_cards):
        # Simplified hand evaluation - in practice you'd use a proper hand evaluator library
        all_cards = hole_cards + community_cards
        ranks = [card[1] for card in all_cards]
        suits = [card[0] for card in all_cards]
        
        # Check for flush
        flush = any(suits.count(suit) >= 5 for suit in set(suits))
        
        # Check for straight
        rank_values = sorted(['23456789TJQKA'.index(r) for r in set(ranks)])
        straight = False
        for i in range(len(rank_values) - 4):
            if rank_values[i+4] - rank_values[i] == 4:
                straight = True
                break
        
        # Pair/three of a kind/four of a kind
        rank_counts = {r: ranks.count(r) for r in set(ranks)}
        max_count = max(rank_counts.values())
        
        if flush and straight:
            return 1.0  # Straight flush
        elif max_count == 4:
            return 0.95  # Four of a kind
        elif max_count == 3 and len([v for v in rank_counts.values() if v == 2]) >= 1:
            return 0.9  # Full house
        elif flush:
            return 0.85
        elif straight:
            return 0.8
        elif max_count == 3:
            return 0.7
        elif len([v for v in rank_counts.values() if v == 2]) >= 2:
            return 0.6  # Two pair
        elif max_count == 2:
            return 0.4  # One pair
        return 0.2  # High card

    # ------------------- Strategic Components ------------------- #

    def determine_optimal_action(self, hand_strength, hand_potential, pot_odds, 
                               opponent_tightness, opponent_aggression, valid_actions, round_state):
        street = round_state['street']
        min_raise = valid_actions[2]['amount']['min']
        max_raise = valid_actions[2]['amount']['max']
        call_amount = valid_actions[1]['amount']
        
        # Position adjustment
        position_factor = 1.0
        if self.position == 'early':
            position_factor = 0.8
        elif self.position == 'late':
            position_factor = 1.2
            
        # Adjusted hand strength
        adjusted_strength = hand_strength * position_factor
        
        # Implement GTO mixed strategy
        if street == 'preflop':
            return self._preflop_strategy(adjusted_strength, valid_actions, opponent_tightness)
        else:
            return self._postflop_strategy(adjusted_strength, hand_potential, pot_odds, 
                                         valid_actions, opponent_aggression, street)

    def _preflop_strategy(self, hand_strength, valid_actions, opponent_tightness):
        # Tight-aggressive preflop strategy
        if hand_strength > 0.8:
            # Premium hands - raise big
            raise_amount = min(valid_actions[2]['amount']['max'],
                              max(valid_actions[2]['amount']['min'], 
                              int(3 * valid_actions[1]['amount'])))
            return self.do_raise(valid_actions, raise_amount)
        elif hand_strength > 0.6:
            # Strong hands - standard raise
            return self.do_raise(valid_actions, valid_actions[2]['amount']['min'])
        elif hand_strength > 0.4 and opponent_tightness < 0.5:
            # Speculative hands against loose opponents
            return self.do_call(valid_actions)
        else:
            # Fold weak hands
            return self.do_fold(valid_actions)

    def _postflop_strategy(self, hand_strength, hand_potential, pot_odds, 
                          valid_actions, opponent_aggression, street):
        # Implement street-specific strategies
        if hand_strength > 0.9:
            # Nut hands - value bet aggressively
            bet_size = min(valid_actions[2]['amount']['max'],
                          max(valid_actions[2]['amount']['min'], 
                          int(0.75 * valid_actions[1]['amount'])))
            return self.do_raise(valid_actions, bet_size)
        elif hand_strength > 0.7:
            # Strong hands - standard bet
            return self.do_raise(valid_actions, valid_actions[2]['amount']['min'])
        elif hand_strength > 0.5 and pot_odds > 0.3:
            # Medium strength with good pot odds
            return self.do_call(valid_actions)
        elif hand_potential > 0.6 and pot_odds < 0.25:
            # Drawing hands with good potential
            return self.do_call(valid_actions)
        else:
            # Fold weak hands or bad odds
            return self.do_fold(valid_actions)

    # ------------------- Helper Methods ------------------- #

    def update_position(self, round_state):
        positions = ['early', 'middle', 'late', 'button', 'small blind', 'big blind']
        btn_pos = round_state['dealer_btn']
        my_pos = next(i for i, seat in enumerate(round_state['seats']) if seat['uuid'] == self.uuid)
        relative_pos = (my_pos - btn_pos) % len(round_state['seats'])
        
        if relative_pos <= 1:
            self.position = 'early'
        elif relative_pos <= 3:
            self.position = 'middle'
        else:
            self.position = 'late'

    def calculate_pot_odds(self, valid_actions, pot):
        call_amount = valid_actions[1]['amount']
        pot_size = pot['main']['amount']
        return call_amount / (pot_size + call_amount) if call_amount > 0 else 0

    def update_opponent_stats(self, round_state):
        if 'action_histories' not in round_state:
            return
            
        for street, actions in round_state['action_histories'].items():
            for action in actions:
                uuid = action['uuid']
                if uuid == self.uuid:
                    continue
                    
                self.opponent_stats[uuid]['actions'] += 1
                
                if action['action'] != 'FOLD':
                    self.opponent_stats[uuid]['vpip'] += 1
                
                if action['action'] == 'RAISE':
                    self.opponent_stats[uuid]['pfr'] += 1
                    self.opponent_stats[uuid]['aggression'] += 1
                elif action['action'] == 'CALL':
                    self.opponent_stats[uuid]['aggression'] -= 0.5

    def get_opponent_tightness(self, round_state):
        if not self.opponent_stats:
            return 0.5
        vpips = [stats['vpip']/stats['actions'] for stats in self.opponent_stats.values() if stats['actions'] > 0]
        return 1 - (sum(vpips)/len(vpips)) if vpips else 0.5

    def get_opponent_aggression(self, round_state):
        if not self.opponent_stats:
            return 0.5
        aggs = [stats['aggression']/stats['actions'] for stats in self.opponent_stats.values() if stats['actions'] > 0]
        return (sum(aggs)/len(aggs)) if aggs else 0.5

    # ------------------- Standard Methods ------------------- #
    def receive_game_start_message(self, game_info):
        self.uuid = game_info['seats'][0]['uuid']  # Assuming we're first in the list

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.hole_cards = hole_card
        self.current_street = 'preflop'

    def receive_street_start_message(self, street, round_state):
        self.current_street = street

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

def setup_ai():
    return MillionDollarBot()

# import random
# import numpy as np
# from collections import defaultdict, deque
# from pypokerengine.players import BasePokerPlayer
# from sklearn.linear_model import LogisticRegression

# class MillionDollarBot(BasePokerPlayer):
#     def __init__(self):
#         super().__init__()
#         # Advanced tracking
#         self.opponent_models = defaultdict(lambda: {
#             'action_sequence': deque(maxlen=20),
#             'hand_range': [0.5]*169,  # All possible starting hands
#             'aggression_factor': 0.5,
#             'fold_to_raise': 0.5,
#             'tendencies': {
#                 'preflop': {'raise': 0.2, 'call': 0.3, 'fold': 0.5},
#                 'postflop': {'bluff': 0.1, 'value_bet': 0.3}
#             }
#         })
        
#         # Neural net components (simplified for this example)
#         self.hand_evaluator = self.build_hand_evaluator()
#         self.range_calculator = LogisticRegression()
        
#         # Game state memory
#         self.hand_history = []
#         self.current_pot_odds = 0
#         self.effective_stack = 100
        
#         # GTO baseline strategy
#         self.gto_ranges = self.load_gtoranges()
        
#         # Dynamic adjustment factors
#         self.exploitation_factor = 0.7  # 0=GTO, 1=Max Exploitation
#         self.risk_tolerance = 0.6

#     def declare_action(self, valid_actions, hole_card, round_state):
#         self.update_game_state(round_state)
#         hand_strength = self.calculate_hand_strength(hole_card, round_state['community_card'])
        
#         # Advanced opponent modeling
#         opponent_ranges = self.predict_opponent_ranges(round_state)
#         equity = self.calculate_equity_against_ranges(hole_card, opponent_ranges)
        
#         # Bayesian probability adjustment
#         bayesian_adjustment = self.calculate_bayesian_adjustment(round_state)
        
#         # Optimal action calculation
#         action = self.game_tree_solver(
#             hand_strength,
#             equity,
#             valid_actions,
#             round_state,
#             bayesian_adjustment
#         )
        
#         # Add randomization to prevent pattern recognition
#         if random.random() < 0.05:  # 5% chance to randomize
#             action = self.randomized_action(action, valid_actions)
            
#         return action

#     # --------------- CORE STRATEGY COMPONENTS --------------- #
    
#     def game_tree_solver(self, hand_strength, equity, valid_actions, round_state, bayesian_adjustment):
#         street = round_state['street']
#         pot_odds = self.calculate_pot_odds(valid_actions, round_state['pot'])
        
#         # Combine GTO and exploitative strategies
#         gto_action = self.gto_strategy(street, hand_strength, equity, pot_odds)
#         exploitative_action = self.exploitative_strategy(round_state)
        
#         # Weighted decision
#         if random.random() < self.exploitation_factor:
#             optimal_action = exploitative_action
#         else:
#             optimal_action = gto_action
            
#         # Pot control logic
#         if street in ['flop', 'turn'] and hand_strength > 0.6 and hand_strength < 0.8:
#             if optimal_action[0] == 'raise':
#                 return self.do_call(valid_actions)  # Pot control with medium strength
        
#         return optimal_action

#     def gto_strategy(self, street, hand_strength, equity, pot_odds):
#         # Implement simplified GTO ranges
#         if street == 'preflop':
#             if hand_strength > 0.85:
#                 return 'raise', min(3, self.effective_stack/2)
#             elif hand_strength > 0.7:
#                 return 'raise', 2.5
#             elif hand_strength > 0.5 and pot_odds < 0.3:
#                 return 'call'
#             else:
#                 return 'fold'
        
#         # Postflop GTO
#         if equity > 0.65:
#             return 'raise', min(3, self.effective_stack/2)
#         elif equity > pot_odds + 0.1:
#             return 'call'
#         elif equity > pot_odds - 0.15 and random.random() < 0.3:  # Bluff
#             return 'raise', min(2, self.effective_stack/3)
#         else:
#             return 'fold'

#     def exploitative_strategy(self, round_state):
#         # Identify weakest opponent
#         weakest_uuid = min(self.opponent_models.items(), 
#                           key=lambda x: x[1]['aggression_factor'])[0]
        
#         # Overbet against tight players
#         if self.opponent_models[weakest_uuid]['fold_to_raise'] > 0.6:
#             return 'raise', min(4, self.effective_stack)
        
#         # Trap aggressive players
#         most_agg_uuid = max(self.opponent_models.items(), 
#                            key=lambda x: x[1]['aggression_factor'])[0]
#         if self.opponent_models[most_agg_uuid]['aggression_factor'] > 0.8:
#             return 'call'
            
#         # Default to value bet
#         return 'raise', 2

#     # --------------- ADVANCED CALCULATIONS --------------- #
    
#     def predict_opponent_ranges(self, round_state):
#         # Uses action history to predict opponent hand ranges
#         ranges = {}
#         for uuid, model in self.opponent_models.items():
#             # Update based on recent actions
#             last_action = model['action_sequence'][-1] if model['action_sequence'] else None
#             if last_action == 'FOLD':
#                 model['hand_range'] = [p*0.5 for p in model['hand_range']]  # Fold weak hands
#             elif last_action == 'RAISE':
#                 model['hand_range'] = [p*1.5 if p > 0.7 else p*0.7 for p in model['hand_range']]
            
#             ranges[uuid] = model['hand_range']
#         return ranges
    
#     def calculate_bayesian_adjustment(self, round_state):
#         # Adjusts probabilities based on opponent actions
#         adjustment = 1.0
#         for action in round_state.get('action_histories', {}).get(self.current_street, []):
#             if action['uuid'] != self.uuid:
#                 opponent_model = self.opponent_models[action['uuid']]
#                 if action['action'] == 'RAISE':
#                     adjustment *= opponent_model['tendencies']['value_bet']
#                 elif action['action'] == 'CALL':
#                     adjustment *= 1 - opponent_model['tendencies']['bluff']
#         return adjustment

#     # --------------- MACHINE LEARNING COMPONENTS --------------- #
    
#     def build_hand_evaluator(self):
#         # In practice, this would be a neural network
#         # For this example, we'll use a simplified version
#         def evaluator(hole_cards, community_cards):
#             # Actual implementation would use real hand evaluation
#             return self._postflop_strength(hole_cards, community_cards)  # From previous example
#         return evaluator
    
#     def update_learning_models(self, round_state):
#         # Update opponent models based on new information
#         for street, actions in round_state.get('action_histories', {}).items():
#             for action in actions:
#                 uuid = action['uuid']
#                 if uuid != self.uuid:
#                     self.opponent_models[uuid]['action_sequence'].append(action['action'])
#                     self.update_opponent_tendencies(uuid, action, street)

#     def update_opponent_tendencies(self, uuid, action, street):
#         model = self.opponent_models[uuid]
#         action_type = action['action'].lower()
        
#         # Update basic tendencies
#         if action_type in model['tendencies'][street]:
#             model['tendencies'][street][action_type] = (
#                 0.9 * model['tendencies'][street][action_type] + 0.1
#             )
        
#         # Update aggression factor
#         if action_type == 'raise':
#             model['aggression_factor'] = min(1, model['aggression_factor'] + 0.1)
#         elif action_type == 'call':
#             model['aggression_factor'] = max(0, model['aggression_factor'] - 0.05)
            
#         # Update fold to raise
#         if action_type == 'fold' and model['action_sequence'][-2] == 'RAISE':
#             model['fold_to_raise'] = min(1, model['fold_to_raise'] + 0.15)

#     # --------------- HELPER METHODS --------------- #
    
#     def randomized_action(self, intended_action, valid_actions):
#         """Add unpredictability to our play"""
#         actions = ['fold', 'call', 'raise']
#         weights = [0.1, 0.3, 0.6]  # Default weights
        
#         if intended_action[0] == 'fold':
#             weights = [0.6, 0.3, 0.1]
#         elif intended_action[0] == 'call':
#             weights = [0.2, 0.5, 0.3]
            
#         chosen = random.choices(actions, weights=weights)[0]
        
#         if chosen == 'raise':
#             min_r = valid_actions[2]['amount']['min']
#             max_r = valid_actions[2]['amount']['max']
#             amount = random.randint(min_r, min(max_r, min_r*3))
#             return chosen, amount
#         return chosen, valid_actions[actions.index(chosen)]['amount']

#     def calculate_equity_against_ranges(self, hole_cards, opponent_ranges):
#         # Monte Carlo simulation would go here
#         # Simplified version for this example
#         our_strength = self.hand_evaluator(hole_cards, [])
#         avg_opp_strength = sum(sum(r) for r in opponent_ranges.values()) / (169 * len(opponent_ranges))
#         return our_strength / (our_strength + avg_opp_strength + 0.001)

#     # --------------- STANDARD POKERENGINE METHODS --------------- #
    
#     def receive_game_start_message(self, game_info):
#         self.uuid = game_info['seats'][0]['uuid']
#         self.effective_stack = game_info['rule']['initial_stack']
        
#     def receive_round_start_message(self, round_count, hole_card, seats):
#         self.hole_cards = hole_card
#         self.current_street = 'preflop'
#         self.hand_history = []
        
#     def receive_street_start_message(self, street, round_state):
#         self.current_street = street
#         self.update_learning_models(round_state)
        
#     def receive_game_update_message(self, action, round_state):
#         self.update_learning_models(round_state)
        
#     def receive_round_result_message(self, winners, hand_info, round_state):
#         # Learn from completed hand
#         self.update_ranges_from_showdown(winners, hand_info)
        
#     def update_ranges_from_showdown(self, winners, hand_info):
#         for uuid, cards in hand_info.items():
#             if uuid != self.uuid and uuid in self.opponent_models:
#                 # Update opponent's range based on shown cards
#                 hand_strength = self.hand_evaluator(cards, [])
#                 self.opponent_models[uuid]['hand_range'] = [
#                     max(0, p * (0.5 if hand_strength < 0.5 else 1.5))
#                     for p in self.opponent_models[uuid]['hand_range']
#                 ]

# def setup_ai():
#     return MillionDollarBot()