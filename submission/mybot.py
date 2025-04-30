import random
from pypokerengine.players import BasePokerPlayer

# Notes
# All cards follow this format: Suit + Rank : 4 of Hearts = 4H, 10 of Spades = ST [2,3,4,5,6,7,8,9,T,J,Q,K,A] [S,C,D,H]

class RandomPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # for your convenience:
        community_card = round_state['community_card']                  # array, starting from [] to [] of 5 elems
        street = round_state['street']                                  # preflop, flop, turn, river
        pot = round_state['pot']                                        # dict : {'main': {'amount': int}, 'side': {'amount': int}}
        dealer_btn = round_state['dealer_btn']                          # int : user id of the player acting as the dealer
        next_player = round_state['next_player']                        # int : user id of next player
        small_blind_pos = round_state['small_blind_pos']                # int : user id of player with small blind (next player is big blind)
        big_blind_pos = round_state['big_blind_pos']                    # int : user id of player with big blind
        round_count = round_state['round_count']                        # int : round number
        small_blind_amount = round_state['small_blind_amount']          # int : amount of starting small blind
        seats = round_state['seats']                                    # {'name' : the AI name, 'uuid': their user id, 'stack': their stack/remaining money, 'state': participating/folded}
                                                                        # we recommend if you're going to try to find your own user id, name your own class name and ai name the same
        action_histories = round_state['action_histories']              # {'preflop': [{'action': 'SMALLBLIND', 'amount': 10, 'add_amount': 10, 'uuid': '1'}, {'action': 'BIGBLIND', 'amount': 20, 'add_amount': 10, 'uuid': '2'},
                                                                        #   {'action': 'CALL', 'amount': 20, 'paid': 20, 'uuid': '3'}, {'action': 'CALL', 'amount': 20, 'paid': 20, 'uuid': '0'}, 
                                                                        #   {'action': 'CALL', 'amount': 20, 'paid': 10, 'uuid': '1'}, {'action': 'FOLD', 'uuid': '2'}]}   -- sample action history for preflop
                                                                        # {'flop': [{'action': 'CALL', 'amount': 0, 'paid': 0, 'uuid': '1'}]}  -- sample for flop


        #print(community_card, street, pot, dealer_btn, next_player, small_blind_pos, big_blind_pos,
        #      round_count, small_blind_amount, seats, action_histories)
        print(community_card)
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        # [{'action': 'fold', 'amount': 0}, {'action': 'call', 'amount': 20}, {'action': 'raise', 'amount': {'min': 30, 'max': 100}}]
        action = random.choice(valid_actions)["action"]
        if action == "raise":
            action_info = valid_actions[2]
            amount = random.randint(action_info["amount"]["min"], action_info["amount"]["max"])
            if amount == -1: action = "call"
        if action == "call":
            return self.do_call(valid_actions)
        if action == "fold":
            return self.do_call(valid_actions)
        return self.do_raise(valid_actions, amount)   # action returned here is sent to the poker engine


    # Helper functions
    
    def do_fold(self, valid_actions):
        action_info = valid_actions[0]
        amount = action_info["amount"]
        return action_info['action'], amount

    def do_call(self, valid_actions):
        action_info = valid_actions[1]
        amount = action_info["amount"]
        return action_info['action'], amount
    
    def do_raise(self,  valid_actions, raise_amount):
        action_info = valid_actions[2]
        amount = max(action_info['amount']['min'], raise_amount)
        return action_info['action'], amount

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


def setup_ai():
    return RandomPlayer()
