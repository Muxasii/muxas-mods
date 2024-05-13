# pylint: disable=line-too-long
"""

TODO: Docs


"""  # pylint: enable=line-too-long

from random import choice, choices, randint, random, sample
import re
import pygame

from scripts.cat.history import History
from scripts.cat.names import names
from scripts.cat.pelts import Pelt

import ujson
import logging

logger = logging.getLogger(__name__)
from scripts.game_structure import image_cache

from sys import exit as sys_exit

from scripts.cat.sprites import sprites

from scripts.game_structure.game_essentials import game, screen_x, screen_y


# ---------------------------------------------------------------------------- #
#                              Counting Cats                                   #
# ---------------------------------------------------------------------------- #

def get_alive_clan_queens(cat_cls):
    """
    Returns a list with all cats with the 'status' queen.
    """
    queens = []
    for inter_cat in cat_cls.all_cats.values():
        if inter_cat.dead or inter_cat.outside:
            continue
        if str(inter_cat.status) != 'kitten' or inter_cat.parent1 is None:
            continue

        
        alive_parents = [cat_cls.fetch_cat(i) for i in inter_cat.get_parents() if 
                   isinstance(cat_cls.fetch_cat(i), cat_cls) and not 
                   (cat_cls.fetch_cat(i).dead or cat_cls.fetch_cat(i).outside)]

        if len(alive_parents) == 1:
            queens.append(alive_parents[0])
        elif len(alive_parents) == 2:
            if alive_parents[0].gender == "female":
                queens.append(alive_parents[0])
            elif alive_parents[1].gender == "female":
                queens.append(alive_parents[1])
            else:
                queens.append(alive_parents[0])
                
    return queens


def get_alive_kits(Cat):
    """
    returns a list of IDs for all living kittens in the clan
    """
    alive_kits = [i for i in Cat.all_cats.values() if
                  i.age in ['kitten', 'newborn'] and not i.dead and not i.outside]

    return alive_kits


def get_med_cats(Cat, working=True):
    """
    returns a list of all meds and med apps currently alive, in the clan, and able to work

    set working to False if you want all meds and med apps regardless of their work status
    """
    all_cats = Cat.all_cats.values()
    possible_med_cats = [i for i in all_cats if
                         i.status in ['medicine cat apprentice', 'medicine cat'] and not (i.dead or i.outside)]

    if working:
        possible_med_cats = [i for i in possible_med_cats if not i.not_working()]

    # Sort the cats by age before returning
    possible_med_cats = sorted(possible_med_cats, key=lambda cat: cat.moons, reverse=True)

    return possible_med_cats


def get_living_cat_count(Cat):
    """
    TODO: DOCS
    """
    count = 0
    for the_cat in Cat.all_cats.values():
        if the_cat.dead:
            continue
        count += 1
    return count


def get_living_clan_cat_count(Cat):
    """
    TODO: DOCS
    """
    count = 0
    for the_cat in Cat.all_cats.values():
        if the_cat.dead or the_cat.exiled or the_cat.outside:
            continue
        count += 1
    return count


def get_cats_same_age(cat, range=10):  # pylint: disable=redefined-builtin
    """Look for all cats in the Clan and returns a list of cats, which are in the same age range as the given cat."""
    cats = []
    for inter_cat in cat.all_cats.values():
        if inter_cat.dead or inter_cat.outside or inter_cat.exiled:
            continue
        if inter_cat.ID == cat.ID:
            continue

        if inter_cat.ID not in cat.relationships:
            cat.create_one_relationship(inter_cat)
            if cat.ID not in inter_cat.relationships:
                inter_cat.create_one_relationship(cat)
            continue

        if inter_cat.moons <= cat.moons + range and inter_cat.moons <= cat.moons - range:
            cats.append(inter_cat)

    return cats


def get_free_possible_mates(cat):
    """Returns a list of available cats, which are possible mates for the given cat."""
    cats = []
    for inter_cat in cat.all_cats.values():
        if inter_cat.dead or inter_cat.outside or inter_cat.exiled:
            continue
        if inter_cat.ID == cat.ID:
            continue

        if inter_cat.ID not in cat.relationships:
            cat.create_one_relationship(inter_cat)
            if cat.ID not in inter_cat.relationships:
                inter_cat.create_one_relationship(cat)
            continue

        if inter_cat.is_potential_mate(cat, for_love_interest=True):
            cats.append(inter_cat)
    return cats


# ---------------------------------------------------------------------------- #
#                          Handling Outside Factors                            #
# ---------------------------------------------------------------------------- #
def get_current_season():
    """
    function to handle the math for finding the Clan's current season
    :return: the Clan's current season
    """

    if game.config['lock_season']:
        game.clan.current_season = game.clan.starting_season
        return game.clan.starting_season

    modifiers = {
        "Newleaf": 0,
        "Greenleaf": 3,
        "Leaf-fall": 6,
        "Leaf-bare": 9
    }
    index = game.clan.age % 12 + modifiers[game.clan.starting_season]

    if index > 11:
        index = index - 12

    game.clan.current_season = game.clan.seasons[index]

    return game.clan.current_season

def change_clan_reputation(difference):
    """
    will change the Clan's reputation with outsider cats according to the difference parameter.
    """
    game.clan.reputation += difference


def change_clan_relations(other_clan, difference):
    """
    will change the Clan's relation with other clans according to the difference parameter.
    """
    # grab the clan that has been indicated
    other_clan = other_clan
    # grab the relation value for that clan
    y = game.clan.all_clans.index(other_clan)
    clan_relations = int(game.clan.all_clans[y].relations)
    # change the value
    clan_relations += difference
    # making sure it doesn't exceed the bounds
    if clan_relations > 30:
        clan_relations = 30
    elif clan_relations < 0:
        clan_relations = 0
    # setting it in the Clan save
    game.clan.all_clans[y].relations = clan_relations

def create_new_cat(Cat,
                   Relationship,
                   new_name:bool=False,
                   loner:bool=False,
                   kittypet:bool=False,
                   kit:bool=False,
                   litter:bool=False,
                   other_clan:bool=None,
                   backstory:bool=None,
                   status:str=None,
                   age:int=None,
                   gender:str=None,
                   thought:str='Is looking around the camp with wonder',
                   alive:bool=True,
                   outside:bool=False,
                   parent1:str=None,
                   parent2:str=None
	) -> list:
    """
    This function creates new cats and then returns a list of those cats
    :param Cat: pass the Cat class
    :params Relationship: pass the Relationship class
    :param new_name: set True if cat(s) is a loner/rogue receiving a new Clan name - default: False
    :param loner: set True if cat(s) is a loner or rogue - default: False
    :param kittypet: set True if cat(s) is a kittypet - default: False
    :param kit: set True if the cat is a lone kitten - default: False
    :param litter: set True if a litter of kittens needs to be generated - default: False
    :param other_clan: if new cat(s) are from a neighboring clan, set true
    :param backstory: a list of possible backstories.json for the new cat(s) - default: None
    :param status: set as the rank you want the new cat to have - default: None (will cause a random status to be picked)
    :param age: set the age of the new cat(s) - default: None (will be random or if kit/litter is true, will be kitten.
    :param gender: set the gender (BIRTH SEX) of the cat - default: None (will be random)
    :param thought: if you need to give a custom "welcome" thought, set it here
    :param alive: set this as False to generate the cat as already dead - default: True (alive)
    :param outside: set this as True to generate the cat as an outsider instead of as part of the Clan - default: False (Clan cat)
    :param parent1: Cat ID to set as the biological parent1
    :param parent2: Cat ID object to set as the biological parert2
    """
    accessory = None
    if isinstance(backstory, list):
        backstory = choice(backstory)

    if backstory in (
            BACKSTORIES["backstory_categories"]["former_clancat_backstories"] or BACKSTORIES["backstory_categories"]["otherclan_categories"]):
        other_clan = True

    created_cats = []

    if not litter:
        number_of_cats = 1
    else:
        number_of_cats = choices([2, 3, 4, 5], [5, 4, 1, 1], k=1)[0]
    
    
    if not isinstance(age, int):
        if status == "newborn":
            age = 0
        elif litter or kit:
            age = randint(1, 5)
        elif status in ('apprentice', 'medicine cat apprentice', 'mediator apprentice'):
            age = randint(6, 11)
        elif status == 'warrior':
            age = randint(23, 120)
        elif status == 'medicine cat':
            age = randint(23, 140)
        elif status == 'elder':
            age = randint(120, 130)
        else:
            age = randint(6, 120)
    
    # setting status
    if not status:
        if age == 0:
            status = "newborn"
        elif age < 6:
            status = "kitten"
        elif 6 <= age <= 11:
            status = "apprentice"
        elif age >= 12:
            status = "warrior"
        elif age >= 120:
            status = 'elder'

    # cat creation and naming time
    for index in range(number_of_cats):
        # setting gender
        if not gender:
            _gender = choice(['female', 'male'])
        else:
            _gender = gender

        # other Clan cats, apps, and kittens (kittens and apps get indoctrinated lmao no old names for them)
        if other_clan or kit or litter or age < 12:
            new_cat = Cat(moons=age,
                          status=status,
                          gender=_gender,
                          backstory=backstory,
                          parent1=parent1,
                          parent2=parent2)
        else:
            # grab starting names and accs for loners/kittypets
            if kittypet:
                name = choice(names.names_dict["loner_names"])
                if choice([1, 2]) == 1:
                    accessory = choice(Pelt.collars)
            elif loner and choice([1, 2]) == 1:  # try to give name from full loner name list
                name = choice(names.names_dict["loner_names"])
            else:
                name = choice(
                    names.names_dict["normal_prefixes"])  # otherwise give name from prefix list (more nature-y names)

            # now we make the cats
            if new_name:  # these cats get new names
                if choice([1, 2]) == 1:  # adding suffix to OG name
                    spaces = name.count(" ")
                    if spaces > 0:
                        # make a list of the words within the name, then add the OG name back in the list
                        words = name.split(" ")
                        words.append(name)
                        new_prefix = choice(words)  # pick new prefix from that list
                        name = new_prefix
                    new_cat = Cat(moons=age,
                                  prefix=name,
                                  status=status,
                                  gender=_gender,
                                  backstory=backstory,
                                  parent1=parent1,
                                  parent2=parent2)
                else:  # completely new name
                    new_cat = Cat(moons=age,
                                  status=status,
                                  gender=_gender,
                                  backstory=backstory,
                                  parent1=parent1,
                                  parent2=parent2)
            # these cats keep their old names
            else:
                new_cat = Cat(moons=age,
                              prefix=name,
                              suffix="",
                              status=status,
                              gender=_gender,
                              backstory=backstory,
                              parent1=parent1,
                              parent2=parent2)

        # give em a collar if they got one
        if accessory:
            new_cat.pelt.accessory = accessory

        # give apprentice aged cat a mentor
        if new_cat.age == 'adolescent':
            new_cat.update_mentor()

        # Remove disabling scars, if they generated.
        not_allowed = ['NOPAW', 'NOTAIL', 'HALFTAIL', 'NOEAR', 'BOTHBLIND', 'RIGHTBLIND', 
                       'LEFTBLIND', 'BRIGHTHEART', 'NOLEFTEAR', 'NORIGHTEAR', 'MANLEG']
        for scar in new_cat.pelt.scars:
            if scar in not_allowed:
                new_cat.pelt.scars.remove(scar)

        # chance to give the new cat a permanent condition, higher chance for found kits and litters
        if game.clan.game_mode != 'classic':
            if kit or litter:
                chance = int(game.config["cat_generation"]["base_permanent_condition"] / 11.25)
            else:
                chance = game.config["cat_generation"]["base_permanent_condition"] + 10
            if not int(random() * chance):
                possible_conditions = []
                for condition in PERMANENT:
                    if (kit or litter) and PERMANENT[condition]['congenital'] not in ['always', 'sometimes']:
                        continue
                    # next part ensures that a kit won't get a condition that takes too long to reveal
                    age = new_cat.moons
                    leeway = 5 - (PERMANENT[condition]['moons_until'] + 1)
                    if age > leeway:
                        continue
                    possible_conditions.append(condition)
                    
                if possible_conditions:
                    chosen_condition = choice(possible_conditions)
                    born_with = False
                    if PERMANENT[chosen_condition]['congenital'] in ['always', 'sometimes']:
                        born_with = True

                    new_cat.get_permanent_condition(chosen_condition, born_with)
                    if new_cat.permanent_condition[chosen_condition]["moons_until"] == 0:
                        new_cat.permanent_condition[chosen_condition]["moons_until"] = -2

                    # assign scars
                    if chosen_condition in ['lost a leg', 'born without a leg']:
                        new_cat.pelt.scars.append('NOPAW')
                    elif chosen_condition in ['lost their tail', 'born without a tail']:
                        new_cat.pelt.scars.append("NOTAIL")

        if outside:
            new_cat.outside = True
        if not alive:
            new_cat.die()

        # newbie thought
        new_cat.thought = thought

        # and they exist now
        created_cats.append(new_cat)
        game.clan.add_cat(new_cat)
        history = History()
        history.add_beginning(new_cat)

        # create relationships
        new_cat.create_relationships_new_cat()
        # Note - we always update inheritance after the cats are generated, to
        # allow us to add parents. 
        #new_cat.create_inheritance_new_cat() 

    return created_cats


def create_outside_cat(Cat, status, backstory, alive=True, thought=None):
    """
        TODO: DOCS
        """
    suffix = ''
    if backstory in BACKSTORIES["backstory_categories"]["rogue_backstories"]:
        status = 'rogue'
    elif backstory in BACKSTORIES["backstory_categories"]["former_clancat_backstories"]:
        status = "former Clancat"
    if status == 'kittypet':
        name = choice(names.names_dict["loner_names"])
    elif status in ['loner', 'rogue']:
        name = choice(names.names_dict["loner_names"] +
                      names.names_dict["normal_prefixes"])
    elif status == 'former Clancat':
        name = choice(names.names_dict["normal_prefixes"])
        suffix = choice(names.names_dict["normal_suffixes"])
    else:
        name = choice(names.names_dict["loner_names"])
    new_cat = Cat(prefix=name,
                  suffix=suffix,
                  status=status,
                  gender=choice(['female', 'male']),
                  backstory=backstory)
    if status == 'kittypet':
        new_cat.pelt.accessory = choice(Pelt.collars)
    new_cat.outside = True

    if not alive:
        new_cat.die()

    thought = "Wonders about those Clan cats they just met"
    new_cat.thought = thought

    # create relationships - only with outsiders
    # (this function will handle, that the cat only knows other outsiders)
    new_cat.create_relationships_new_cat()
    new_cat.create_inheritance_new_cat()

    game.clan.add_cat(new_cat)
    game.clan.add_to_outside(new_cat)
    name = str(name + suffix)

    return name


# ---------------------------------------------------------------------------- #
#                             Cat Relationships                                #
# ---------------------------------------------------------------------------- #


def get_highest_romantic_relation(relationships, exclude_mate=False, potential_mate=False):
    """Returns the relationship with the highest romantic value."""
    max_love_value = 0
    current_max_relationship = None
    for rel in relationships:
        if rel.romantic_love < 0:
            continue
        if exclude_mate and rel.cat_from.ID in rel.cat_to.mate:
            continue
        if potential_mate and not rel.cat_to.is_potential_mate(rel.cat_from, for_love_interest=True):
            continue
        if rel.romantic_love > max_love_value:
            current_max_relationship = rel
            max_love_value = rel.romantic_love

    return current_max_relationship


def check_relationship_value(cat_from, cat_to, rel_value=None):
    """
    returns the value of the rel_value param given
    :param cat_from: the cat who is having the feelings
    :param cat_to: the cat that the feelings are directed towards
    :param rel_value: the relationship value that you're looking for,
    options are: romantic, platonic, dislike, admiration, comfortable, jealousy, trust
    """
    if cat_to.ID in cat_from.relationships:
        relationship = cat_from.relationships[cat_to.ID]
    else:
        relationship = cat_from.create_one_relationship(cat_to)

    if rel_value == "romantic":
        return relationship.romantic_love
    elif rel_value == "platonic":
        return relationship.platonic_like
    elif rel_value == "dislike":
        return relationship.dislike
    elif rel_value == "admiration":
        return relationship.admiration
    elif rel_value == "comfortable":
        return relationship.comfortable
    elif rel_value == "jealousy":
        return relationship.jealousy
    elif rel_value == "trust":
        return relationship.trust


def get_personality_compatibility(cat1, cat2):
    """Returns:
        True - if personalities have a positive compatibility
        False - if personalities have a negative compatibility
        None - if personalities have a neutral compatibility
    """
    personality1 = cat1.personality.trait
    personality2 = cat2.personality.trait

    if personality1 == personality2:
        if personality1 is None:
            return None
        return True

    lawfulness_diff = abs(cat1.personality.lawfulness - cat2.personality.lawfulness)
    sociability_diff = abs(cat1.personality.sociability - cat2.personality.sociability)
    aggression_diff = abs(cat1.personality.aggression - cat2.personality.aggression)
    stability_diff = abs(cat1.personality.stability - cat2.personality.stability)
    list_of_differences = [lawfulness_diff, sociability_diff, aggression_diff, stability_diff]

    running_total = 0
    for x in list_of_differences:
        if x <= 4:
            running_total += 1
        elif x >= 6:
            running_total -= 1

    if running_total >= 2:
        return True
    if running_total <= -2:
        return False

    return None


def get_cats_of_romantic_interest(cat):
    """Returns a list of cats, those cats are love interest of the given cat"""
    cats = []
    for inter_cat in cat.all_cats.values():
        if inter_cat.dead or inter_cat.outside or inter_cat.exiled:
            continue
        if inter_cat.ID == cat.ID:
            continue

        if inter_cat.ID not in cat.relationships:
            cat.create_one_relationship(inter_cat)
            if cat.ID not in inter_cat.relationships:
                inter_cat.create_one_relationship(cat)
            continue
        
        # Extra check to ensure they are potential mates
        if inter_cat.is_potential_mate(cat, for_love_interest=True) and cat.relationships[inter_cat.ID].romantic_love > 0:
            cats.append(inter_cat)
    return cats


def get_amount_of_cats_with_relation_value_towards(cat, value, all_cats):
    """
    Looks how many cats have the certain value 
    :param cat: cat in question
    :param value: value which has to be reached
    :param all_cats: list of cats which has to be checked
    """

    # collect all true or false if the value is reached for the cat or not
    # later count or sum can be used to get the amount of cats
    # this will be handled like this, because it is easier / shorter to check
    relation_dict = {
        "romantic_love": [],
        "platonic_like": [],
        "dislike": [],
        "admiration": [],
        "comfortable": [],
        "jealousy": [],
        "trust": []
    }

    for inter_cat in all_cats:
        if cat.ID in inter_cat.relationships:
            relation = inter_cat.relationships[cat.ID]
        else:
            continue

        relation_dict['romantic_love'].append(relation.romantic_love >= value)
        relation_dict['platonic_like'].append(relation.platonic_like >= value)
        relation_dict['dislike'].append(relation.dislike >= value)
        relation_dict['admiration'].append(relation.admiration >= value)
        relation_dict['comfortable'].append(relation.comfortable >= value)
        relation_dict['jealousy'].append(relation.jealousy >= value)
        relation_dict['trust'].append(relation.trust >= value)

    return_dict = {
        "romantic_love": sum(relation_dict['romantic_love']),
        "platonic_like": sum(relation_dict['platonic_like']),
        "dislike": sum(relation_dict['dislike']),
        "admiration": sum(relation_dict['admiration']),
        "comfortable": sum(relation_dict['comfortable']),
        "jealousy": sum(relation_dict['jealousy']),
        "trust": sum(relation_dict['trust'])
    }

    return return_dict


def change_relationship_values(cats_to: list,
                               cats_from: list,
                               romantic_love:int=0,
                               platonic_like:int=0,
                               dislike:int=0,
                               admiration:int=0,
                               comfortable:int=0,
                               jealousy:int=0,
                               trust:int=0,
                               auto_romance:bool=False,
                               log:str=None
                               ):
    """
    changes relationship values according to the parameters.

    cats_from - a list of cats for the cats whose rel values are being affected
    cats_to - a list of cat IDs for the cats who are the target of that rel value
            i.e. cats in cats_from lose respect towards the cats in cats_to
    auto_romance - if this is set to False (which is the default) then if the cat_from already has romantic value
            with cat_to then the platonic_like param value will also be used for the romantic_love param
            if you don't want this to happen, then set auto_romance to False
    log - string to add to relationship log. 

    use the relationship value params to indicate how much the values should change.
    
    This is just for test prints - DON'T DELETE - you can use this to test if relationships are changing
    changed = False
    if romantic_love == 0 and platonic_like == 0 and dislike == 0 and admiration == 0 and \
            comfortable == 0 and jealousy == 0 and trust == 0:
        changed = False
    else:
        changed = True"""

    # pick out the correct cats
    for kitty in cats_from:
        relationships = [i for i in kitty.relationships.values() if i.cat_to.ID in cats_to]

        # make sure that cats don't gain rel with themselves
        for rel in relationships:
            if kitty.ID == rel.cat_to.ID:
                continue

            # here we just double-check that the cats are allowed to be romantic with each other
            if kitty.is_potential_mate(rel.cat_to, for_love_interest=True) or rel.cat_to.ID in kitty.mate:
                # if cat already has romantic feelings then automatically increase romantic feelings
                # when platonic feelings would increase
                if rel.romantic_love > 0 and auto_romance:
                    romantic_love = platonic_like

                # now gain the romance
                rel.romantic_love += romantic_love

            # gain other rel values
            rel.platonic_like += platonic_like
            rel.dislike += dislike
            rel.admiration += admiration
            rel.comfortable += comfortable
            rel.jealousy += jealousy
            rel.trust += trust

            '''# for testing purposes - DON'T DELETE - you can use this to test if relationships are changing
            print(str(kitty.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                  "Romantic: " + str(romantic_love) +
                  " /Platonic: " + str(platonic_like) +
                  " /Dislike: " + str(dislike) +
                  " /Respect: " + str(admiration) +
                  " /Comfort: " + str(comfortable) +
                  " /Jealousy: " + str(jealousy) +
                  " /Trust: " + str(trust)) if changed else print("No relationship change")'''
                  
            if log and isinstance(log, str):
                rel.log.append(log)


# ---------------------------------------------------------------------------- #
#                               Text Adjust                                    #
# ---------------------------------------------------------------------------- #

def pronoun_repl(m, cat_pronouns_dict, raise_exception=False):
    """ Helper function for add_pronouns. If raise_exception is 
    False, any error in pronoun formatting will not raise an 
    exception, and will use a simple replacement "error" """
    
    # Add protection about the "insert" sometimes used
    if m.group(0) == "{insert}":
        return m.group(0)
    
    inner_details = m.group(1).split("/")
    
    try:
        d = cat_pronouns_dict[inner_details[1]][1]
        if inner_details[0].upper() == "PRONOUN":
            pro = d[inner_details[2]]
            if inner_details[-1] == "CAP":
                pro = pro.capitalize()
            return pro
        elif inner_details[0].upper() == "VERB":
            return inner_details[d["conju"] + 1]
        
        if raise_exception:
            raise KeyError(f"Pronoun tag: {m.group(1)} is not properly"
                           "indicated as a PRONOUN or VERB tag.")
        
        print("Failed to find pronoun:", m.group(1))
        return "error1"
    except (KeyError, IndexError) as e:
        if raise_exception:
            raise
        
        logger.exception("Failed to find pronoun: " + m.group(1))
        print("Failed to find pronoun:", m.group(1))
        return "error2"


def name_repl(m, cat_dict):
    ''' Name replacement '''
    return cat_dict[m.group(0)][0]


def process_text(text, cat_dict, raise_exception=False):
    """ Add the correct name and pronouns into a string. """
    adjust_text = re.sub(r"\{(.*?)\}", lambda x: pronoun_repl(x, cat_dict, raise_exception),
                                                              text)

    name_patterns = [r'(?<!\{)' + re.escape(l) + r'(?!\})' for l in cat_dict]
    adjust_text = re.sub("|".join(name_patterns), lambda x: name_repl(x, cat_dict), adjust_text)
    return adjust_text


def adjust_list_text(list_of_items):
    """
    returns the list in correct grammar format (i.e. item1, item2, item3 and item4)
    this works with any number of items
    :param list_of_items: the list of items you want converted
    :return: the new string
    """
    if len(list_of_items) == 1:
        insert = f"{list_of_items[0]}"
    elif len(list_of_items) == 2:
        insert = f"{list_of_items[0]} and {list_of_items[1]}"
    else:
        item_line = ", ".join(list_of_items[:-1])
        insert = f"{item_line}, and {list_of_items[-1]}"

    return insert


def adjust_prey_abbr(patrol_text):
    """
    checks for prey abbreviations and returns adjusted text
    """
    for abbr in PREY_LISTS["abbreviations"]:
        if abbr in patrol_text:
            chosen_list = PREY_LISTS["abbreviations"].get(abbr)
            chosen_list = PREY_LISTS[chosen_list]
            prey = choice(chosen_list)
            patrol_text = patrol_text.replace(abbr, prey)

    return patrol_text


def get_special_snippet_list(chosen_list, amount, sense_groups=None, return_string=True):
    """
    function to grab items from various lists in snippet_collections.json
    list options are:
    -prophecy_list - sense_groups = sight, sound, smell, emotional, touch
    -omen_list - sense_groups = sight, sound, smell, emotional, touch
    -clair_list  - sense_groups = sound, smell, emotional, touch, taste
    -dream_list (this list doesn't have sense_groups)
    -story_list (this list doesn't have sense_groups)
    :param chosen_list: pick which list you want to grab from
    :param amount: the amount of items you want the returned list to contain
    :param sense_groups: list which senses you want the snippets to correspond with:
     "touch", "sight", "emotional", "sound", "smell" are the options. Default is None, if left as this then all senses
     will be included (if the list doesn't have sense categories, then leave as None)
    :param return_string: if True then the function will format the snippet list with appropriate commas and 'ands'.
    This will work with any number of items. If set to True, then the function will return a string instead of a list.
    (i.e. ["hate", "fear", "dread"] becomes "hate, fear, and dread") - Default is True
    :return: a list of the chosen items from chosen_list or a formatted string if format is True
    """
    biome = game.clan.biome.casefold()

    # these lists don't get sense specific snippets, so is handled first
    if chosen_list in ["dream_list", "story_list"]:

        if chosen_list == 'story_list':  # story list has some biome specific things to collect
            snippets = SNIPPETS[chosen_list]['general']
            snippets.extend(SNIPPETS[chosen_list][biome])
        elif chosen_list == 'clair_list':  # the clair list also pulls from the dream list
            snippets = SNIPPETS[chosen_list]
            snippets.extend(SNIPPETS["dream_list"])
        else:  # the dream list just gets the one
            snippets = SNIPPETS[chosen_list]

    else:
        # if no sense groups were specified, use all of them
        if not sense_groups:
            if chosen_list == 'clair_list':
                sense_groups = ["taste", "sound", "smell", "emotional", "touch"]
            else:
                sense_groups = ["sight", "sound", "smell", "emotional", "touch"]

        # find the correct lists and compile them
        snippets = []
        for sense in sense_groups:
            snippet_group = SNIPPETS[chosen_list][sense]
            snippets.extend(snippet_group["general"])
            snippets.extend(snippet_group[biome])

    # now choose a unique snippet from each snip list
    unique_snippets = []
    for snip_list in snippets:
        unique_snippets.append(choice(snip_list))

    # pick out our final snippets
    final_snippets = sample(unique_snippets, k=amount)

    if return_string:
        text = adjust_list_text(final_snippets)
        return text
    else:
        return final_snippets


def find_special_list_types(text):
    """
    purely to identify which senses are being called for by a snippet abbreviation
    returns adjusted text, sense list, and list type
    """
    senses = []
    if "omen_list" in text:
        list_type = "omen_list"
    elif "prophecy_list" in text:
        list_type = "prophecy_list"
    elif "dream_list" in text:
        list_type = "dream_list"
    elif "clair_list" in text:
        list_type = "clair_list"
    elif "story_list" in text:
        list_type = "story_list"
    else:
        return text, None, None

    if "_sight" in text:
        senses.append("sight")
        text = text.replace("_sight", "")
    if "_sound" in text:
        senses.append("sound")
        text = text.replace("_sight", "")
    if "_smell" in text:
        text = text.replace("_smell", "")
        senses.append("smell")
    if "_emotional" in text:
        text = text.replace("_emotional", "")
        senses.append("emotional")
    if "_touch" in text:
        text = text.replace("_touch", "")
        senses.append("touch")
    if "_taste" in text:
        text = text.replace("_taste", "")
        senses.append("taste")

    return text, senses, list_type


def history_text_adjust(text,
                        other_clan_name,
                        clan,other_cat_rc=None):
    """
    we want to handle history text on its own because it needs to preserve the pronoun tags and cat abbreviations.
    this is so that future pronoun changes or name changes will continue to be reflected in history
    """
    if "o_c" in text:
        text = text.replace("o_c", other_clan_name)
    if "c_n" in text:
        text = text.replace("c_n", clan.name)
    if "r_c" in text and other_cat_rc:
        text = selective_replace(text, "r_c", str(other_cat_rc.name))
    return text

def selective_replace(text, pattern, replacement):
    i = 0
    while i < len(text):
        index = text.find(pattern, i)
        if index == -1:
            break
        start_brace = text.rfind('{', 0, index)
        end_brace = text.find('}', index)
        if start_brace != -1 and end_brace != -1 and start_brace < index < end_brace:
            i = index + len(pattern)
        else:
            text = text[:index] + replacement + text[index + len(pattern):]
            i = index + len(replacement)

    return text

def ongoing_event_text_adjust(Cat, text, clan=None, other_clan_name=None):
    """
    This function is for adjusting the text of ongoing events
    :param Cat: the cat class
    :param text: the text to be adjusted
    :param clan: the name of the clan
    :param other_clan_name: the other Clan's name if another Clan is involved
    """
    cat_dict = {}
    if "lead_name" in text:
        kitty = Cat.fetch_cat(game.clan.leader)
        cat_dict["lead_name"] = (str(kitty.name), choice(kitty.pronouns))
    if "dep_name" in text:
        kitty = Cat.fetch_cat(game.clan.deputy)
        cat_dict["dep_name"] = (str(kitty.name), choice(kitty.pronouns))
    if "med_name" in text:
        kitty = choice(get_med_cats(Cat, working=False))
        cat_dict["med_name"] = (str(kitty.name), choice(kitty.pronouns))

    if cat_dict:
        text = process_text(text, cat_dict)

    if other_clan_name:
        text = text.replace("o_c", other_clan_name)
    if clan:
        clan_name = str(clan.name)
    else:
        if game.clan is None:
            clan_name = game.switches["clan_list"][0]
        else:
            clan_name = str(game.clan.name)

    text = text.replace("c_n", clan_name + "Clan")

    return text


def event_text_adjust(Cat,
                      text,
                      cat,
                      other_cat=None,
                      other_clan_name=None,
                      new_cat=None,
                      clan=None,
                      murder_reveal=False,
                      victim=None):
    """
    This function takes the given text and returns it with the abbreviations replaced appropriately
    :param Cat: Always give the Cat class
    :param text: The text that needs to be changed
    :param cat: The cat taking the place of m_c
    :param other_cat: The cat taking the place of r_c
    :param other_clan_name: The other clan involved in the event
    :param new_cat: The cat taking the place of n_c
    :param clan: The player's Clan
    :param murder_reveal: Whether or not this event is a murder reveal
    :return: the adjusted text
    """

    cat_dict = {}

    if cat:
        cat_dict["m_c"] = (str(cat.name), choice(cat.pronouns))
        cat_dict["p_l"] = cat_dict["m_c"]
    if "acc_plural" in text:
        text = text.replace("acc_plural", str(ACC_DISPLAY[cat.pelt.accessory]["plural"]))
    if "acc_singular" in text:
        text = text.replace("acc_singular", str(ACC_DISPLAY[cat.pelt.accessory]["singular"]))

    if other_cat:
        cat_dict["r_c"] = (str(other_cat.name), choice(other_cat.pronouns))

    if new_cat:
        cat_dict["n_c_pre"] = (str(new_cat.name.prefix), None)
        cat_dict["n_c"] = (str(new_cat.name), choice(new_cat.pronouns))

    if other_clan_name:
        text = text.replace("o_c", other_clan_name)
    if clan:
        clan_name = str(clan.name)
    else:
        if game.clan is None:
            clan_name = game.switches["clan_list"][0]
        else:
            clan_name = str(game.clan.name)

    text = text.replace("c_n", clan_name + "Clan")

    if murder_reveal and victim:
        victim_cat = Cat.fetch_cat(victim)
        text = text.replace("mur_c", str(victim_cat.name))

    # Dreams and Omens
    text, senses, list_type = find_special_list_types(text)
    if list_type:
        chosen_items = get_special_snippet_list(list_type, randint(1, 3), sense_groups=senses)
        text = text.replace(list_type, chosen_items)

    adjust_text = process_text(text, cat_dict)

    return adjust_text


def leader_ceremony_text_adjust(Cat,
                                text,
                                leader,
                                life_giver=None,
                                virtue=None,
                                extra_lives=None, ):
    """
    used to adjust the text for leader ceremonies
    """
    replace_dict = {
        "m_c_star": (str(leader.name.prefix + "star"), choice(leader.pronouns)),
        "m_c": (str(leader.name.prefix + leader.name.suffix), choice(leader.pronouns)),
    }

    if life_giver:
        replace_dict["r_c"] = (str(Cat.fetch_cat(life_giver).name), choice(Cat.fetch_cat(life_giver).pronouns))

    text = process_text(text, replace_dict)

    if virtue:
        virtue = process_text(virtue, replace_dict)
        text = text.replace("[virtue]", virtue)

    if extra_lives:
        text = text.replace('[life_num]', str(extra_lives))

    text = text.replace("c_n", str(game.clan.name) + "Clan")

    return text


def ceremony_text_adjust(Cat,
                         text,
                         cat,
                         old_name=None,
                         dead_mentor=None,
                         mentor=None,
                         previous_alive_mentor=None,
                         random_honor=None,
                         living_parents=(),
                         dead_parents=()):
    clanname = str(game.clan.name + "Clan")

    random_honor = random_honor
    random_living_parent = None
    random_dead_parent = None

    adjust_text = text

    cat_dict = {
        "m_c": (str(cat.name), choice(cat.pronouns)) if cat else ("cat_placeholder", None),
        "(mentor)": (str(mentor.name), choice(mentor.pronouns)) if mentor else ("mentor_placeholder", None),
        "(deadmentor)": (str(dead_mentor.name), choice(dead_mentor.pronouns)) if dead_mentor else (
            "dead_mentor_name", None),
        "(previous_mentor)": (
            str(previous_alive_mentor.name), choice(previous_alive_mentor.pronouns)) if previous_alive_mentor else (
            "previous_mentor_name", None),
        "l_n": (str(game.clan.leader.name), choice(game.clan.leader.pronouns)) if game.clan.leader else (
            "leader_name", None),
        "c_n": (clanname, None),
    }
    
    if old_name:
        cat_dict["(old_name)"] = (old_name, None)

    if random_honor:
        cat_dict["r_h"] = (random_honor, None)

    if "p1" in adjust_text and "p2" in adjust_text and len(living_parents) >= 2:
        cat_dict["p1"] = (str(living_parents[0].name), choice(living_parents[0].pronouns))
        cat_dict["p2"] = (str(living_parents[1].name), choice(living_parents[1].pronouns))
    elif living_parents:
        random_living_parent = choice(living_parents)
        cat_dict["p1"] = (str(random_living_parent.name), choice(random_living_parent.pronouns))
        cat_dict["p2"] = (str(random_living_parent.name), choice(random_living_parent.pronouns))

    if "dead_par1" in adjust_text and "dead_par2" in adjust_text and len(dead_parents) >= 2:
        cat_dict["dead_par1"] = (str(dead_parents[0].name), choice(dead_parents[0].pronouns))
        cat_dict["dead_par2"] = (str(dead_parents[1].name), choice(dead_parents[1].pronouns))
    elif dead_parents:
        random_dead_parent = choice(dead_parents)
        cat_dict["dead_par1"] = (str(random_dead_parent.name), choice(random_dead_parent.pronouns))
        cat_dict["dead_par2"] = (str(random_dead_parent.name), choice(random_dead_parent.pronouns))

    adjust_text = process_text(adjust_text, cat_dict)

    return adjust_text, random_living_parent, random_dead_parent


def shorten_text_to_fit(name, length_limit, font_size=None, font_type="resources/fonts/NotoSans-Medium.ttf"):
    length_limit = length_limit//2 if not game.settings['fullscreen'] else length_limit
    # Set the font size based on fullscreen settings if not provided
    # Text box objects are named by their fullscreen text size so it's easier to do it this way
    if font_size is None:
        font_size = 30
    font_size = font_size//2 if not game.settings['fullscreen'] else font_size
    # Create the font object
    font = pygame.font.Font(font_type, font_size)
    
    # Add dynamic name lengths by checking the actual width of the text
    total_width = 0
    short_name = ''
    for index, character in enumerate(name):
        char_width = font.size(character)[0]
        ellipsis_width = font.size("...")[0]
        
        # Check if the current character is the last one and its width is less than or equal to ellipsis_width
        if index == len(name) - 1 and char_width <= ellipsis_width:
            short_name += character
        else:
            total_width += char_width
            if total_width + ellipsis_width > length_limit:
                break
            short_name += character

    # If the name was truncated, add '...'
    if len(short_name) < len(name):
        short_name += '...'

    return short_name

# ---------------------------------------------------------------------------- #
#                                    Sprites                                   #
# ---------------------------------------------------------------------------- #

def scale(rect):
    rect[0] = round(rect[0] / 1600 * screen_x) if rect[0] > 0 else rect[0]
    rect[1] = round(rect[1] / 1400 * screen_y) if rect[1] > 0 else rect[1]
    rect[2] = round(rect[2] / 1600 * screen_x) if rect[2] > 0 else rect[2]
    rect[3] = round(rect[3] / 1400 * screen_y) if rect[3] > 0 else rect[3]

    return rect


def scale_dimentions(dim):
    dim = list(dim)
    dim[0] = round(dim[0] / 1600 * screen_x) if dim[0] > 0 else dim[0]
    dim[1] = round(dim[1] / 1400 * screen_y) if dim[1] > 0 else dim[1]
    dim = tuple(dim)

    return dim


def update_sprite(cat):
    # First, check if the cat is faded.
    if cat.faded:
        # Don't update the sprite if the cat is faded.
        return

    # apply
    cat.sprite = generate_sprite(cat)
    # update class dictionary
    cat.all_cats[cat.ID] = cat


def generate_sprite(cat, life_state=None, scars_hidden=False, acc_hidden=False, always_living=False, 
                    no_not_working=False) -> pygame.Surface:
    """Generates the sprite for a cat, with optional arugments that will override certain things. 
        life_stage: sets the age life_stage of the cat, overriding the one set by it's age. Set to string. 
        scar_hidden: If True, doesn't display the cat's scars. If False, display cat scars. 
        acc_hidden: If True, hide the accessory. If false, show the accessory.
        always_living: If True, always show the cat with living lineart
        no_not_working: If true, never use the not_working lineart.
                        If false, use the cat.not_working() to determine the no_working art. 
        """
    
    if life_state is not None:
        age = life_state
    else:
        age = cat.age
    
    if always_living:
        dead = False
    else:
        dead = cat.dead
        
    # setting the cat_sprite (bc this makes things much easier)
    if not no_not_working and cat.not_working() and age != 'newborn' and game.config['cat_sprites']['sick_sprites']:
        if age in ['kitten']:
            cat_sprite = str(21)
        elif age in ['adolescent']:
            cat_sprite = str(19)
        else:
            cat_sprite = str(18)
    elif cat.pelt.paralyzed and age != 'newborn':
        if age in ['kitten', 'adolescent']:
            cat_sprite = str(17)
        else:
            if cat.pelt.length == 'long':
                cat_sprite = str(16)
            else:
                cat_sprite = str(15)
    else:
        if age == 'elder' and not game.config['fun']['all_cats_are_newborn']:
            age = 'senior'
        
        if game.config['fun']['all_cats_are_newborn']:
            cat_sprite = str(cat.pelt.cat_sprites['newborn'])
        else:
            cat_sprite = str(cat.pelt.cat_sprites[age])

    new_sprite = pygame.Surface((sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA)

    # draw base
    new_sprite.blit(sprites.sprites['base' + cat_sprite], (0, 0))

    # generating the sprite
    try:
        # copying kori's awoogen thanks kori (I would've done this route anyway)
        # base, underfur, overfur, markings fade, markings, marking inside
        # i cried typing all of this out lol help me
        color_dict = {
            "solid": {
                "WHITE": [
                    '#EFFAFC',
                    '#F6FBF9',
                    '#EEF9FC',
                    '#A7B9BF',
                    '#C6D6DB',
                    '#D0DEE1'],
                "PALEGREY": [
                    '#C6D7D3',
                    '#D7E0D1',
                    '#C2D5D3',
                    '#788B8B',
                    '#8FA6A6',
                    '#A2B1B0'],
                "SILVER": [
                    '#B6C8CA',
                    '#CAD6C7',
                    '#9FB8BD',
                    '#2C383F',
                    '#4C626D',
                    '#859A9D'],
                "GREY": [
                    '#92A1A1',
                    '#AFB8AE',
                    '#92A1A1',
                    '#3F514F',
                    '#637674',
                    '#B1AEB0'],
                "DARKGREY": [
                    '#697879',
                    '#8F978F',
                    '#5B6C6F',
                    '#0B1110',
                    '#223734',
                    '#39484B'],
                "GHOST": [
                    '#3C404C',
                    '#3A3F4B',
                    '#4D5056',
                    '#5D6B6F',
                    '#515E64',
                    '#4D4E59'],
                "BLACK": [
                    '#353A42',
                    '#46494E',
                    '#31383F',
                    '#0A0D15',
                    '#141720',
                    '#202427'],
                "CREAM": [
                    '#F4DAB5',
                    '#F4E8CB',
                    '#F3D7B4',
                    '#D4A57D',
                    '#E9B68B',
                    '#F5CE9A'],
                "PALEGINGER": [
                    '#E7C498',
                    '#E7C69A',
                    '#E5BD92',
                    '#C68B5B',
                    '#DA9C68',
                    '#E8B479'],
                "GOLDEN": [
                    '#EECB84',
                    '#ECD69F',
                    '#E5B374',
                    '#775441',
                    '#CB906F',
                    '#D9A859'],
                "GINGER": [
                    '#F2AE71',
                    '#F4C391',
                    '#F0AC73',
                    '#AC5A2C',
                    '#DB7338',
                    '#DB9355'],
                "DARKGINGER": [
                    '#D2713D',
                    '#E0A67A',
                    '#D1703C',
                    '#6F2E18',
                    '#A34323',
                    '#BC5D2A'],
                "SIENNA": [
                    '#AA583E',
                    '#B36F50',
                    '#A9563D',
                    '#502A2D',
                    '#87413C',
                    '#BA6D4C'],
                "LIGHTBROWN": [
                    '#DAC7A4',
                    '#E6D7B6',
                    '#CEC6B8',
                    '#6F5D46',
                    '#BCA07B',
                    '#C2AF8C'],
                "LILAC": [
                    '#B49890',
                    '#D0BBAC',
                    '#A6A4A5',
                    '#655252',
                    '#8B696B',
                    '#AD898A'],
                "BROWN": [
                    '#A4856C',
                    '#BEAA8D',
                    '#93887E',
                    '#2D221D',
                    '#674F43',
                    '#957961'],
                "GOLDEN-BROWN": [
                    '#A86D59',
                    '#D2A686',
                    '#836B5B',
                    '#432E2C',
                    '#7B5248',
                    '#A86F59'],
                "DARKBROWN": [
                    '#754E3C',
                    '#B09479',
                    '#6C625D',
                    '#130B0A',
                    '#3B2420',
                    '#5F483C'],
                "CHOCOLATE": [
                    '#704642',
                    '#855953',
                    '#484145',
                    '#1E1719',
                    '#5A3134',
                    '#705153'],
                "LAVENDER": [
                    '#C0B8C8',
                    '#F7F6FA',
                    '#B2AAB7',
                    '#92848E',
                    '#ADA1B2',
                    '#CDBFC6'],
                "ASH": [
                    '#272120',
                    '#6C5240',
                    '#090707',
                    '#030202',
                    '#231A19',
                    '#3D312E'],
                "PALECREAM": [
                    '#FFFBF0',
                    '#FFFFFF',
                    '#FFEED8',
                    '#F7D1B5',
                    '#FFF5E6',
                    '#FFFCF3']
            },
            
            "special": {
                "SINGLESTRIPE": {
                    "WHITE": [
                        '#EEF9FC',
                        '#F4FBF4',
                        '#EEF9FC',
                        '#B4D1DB',
                        '#B4D1DB',
                        '#D0DEE1'],
                    "PALEGREY": [
                        '#C2D5D3',
                        '#D9E1D1',
                        '#C1D5D3',
                        '#89A9A2',
                        '#89A9A2',
                        '#A2B1B0'],
                    "SILVER": [
                        '#A6BFC1',
                        '#C5D3C6',
                        '#9FBBC0',
                        '#436A6F',
                        '#436A6F',
                        '#859A9D'],
                    "GREY": [
                        '#94A3A2',
                        '#92A1A1',
                        '#92A1A1',
                        '#324242',
                        '#324242',
                        '#B1AEB0'],
                    "DARKGREY": [
                        '#5E6D70',
                        '#828E8C',
                        '#5B6C6F',
                        '#0C1315',
                        '#0C1315',
                        '#39484B'],
                    "GHOST": [
                        '#3E424E',
                        '#5C5E63',
                        '#3A3F4B',
                        '#8B93A5',
                        '#8B93A5',
                        '#4D4E59'],
                    "BLACK": [
                        '#2F353A',
                        '#3D4247',
                        '#2F353A',
                        '#050708',
                        '#050708',
                        '#202427'],
                    "CREAM": [
                        '#F3D6B2',
                        '#F4E8CB',
                        '#F3D6B2',
                        '#E1A568',
                        '#E1A568',
                        '#F5CE9A'],
                    "PALEGINGER": [
                        '#E7C498',
                        '#E7C69A',
                        '#E5BD92',
                        '#C1763E',
                        '#C1763E',
                        '#E8B479'],
                    "GOLDEN": [
                        '#EBC27D',
                        '#ECD49B',
                        '#E6B576',
                        '#C16A27',
                        '#C16A27',
                        '#D9A859'],
                    "GINGER": [
                        '#F2A96B',
                        '#F4C594',
                        '#F0AC73',
                        '#DB6126',
                        '#DB6126',
                        '#DB9355'],
                    "DARKGINGER": [
                        '#D57D4B',
                        '#E0A67A',
                        '#D1703C',
                        '#9A230A',
                        '#9A230A',
                        '#BC5D2A'],
                    "SIENNA": [
                        '#A9563D',
                        '#B47353',
                        '#A9563D',
                        '#3F2529',
                        '#743A38',
                        '#BA6D4C'],
                    "LIGHTBROWN": [
                        '#DDCCAE',
                        '#E6D7B7',
                        '#D0C6B5',
                        '#9E8867',
                        '#9E8867',
                        '#C2AF8C'],
                    "LILAC": [
                        '#B3968F',
                        '#D0BCAD',
                        '#A6A4A5',
                        '#6E5859',
                        '#8D6B6C',
                        '#AD898A'],
                    "BROWN": [
                        '#AA9682',
                        '#BDA78E',
                        '#93887E',
                        '#4D3625',
                        '#4D3625',
                        '#957961'],
                    "GOLDEN-BROWN": [
                        '#A76B57',
                        '#D2A685',
                        '#886C5D',
                        '#473130',
                        '#795047',
                        '#A86F59'],
                    "DARKBROWN": [
                        '#7A5948',
                        '#927C6A',
                        '#6B5C54',
                        '#311910',
                        '#311910',
                        '#5F483C'],
                    "CHOCOLATE": [
                        '#6E4642',
                        '#875B54',
                        '#4A3F46',
                        '#281E1F',
                        '#513133',
                        '#705153'],
                    "LAVENDER": [
                        '#C8C2CD',
                        '#F7F6FA',
                        '#BEB5C8',
                        '#6C5A6A',
                        '#A798AE',
                        '#CDBFC6'],
                    "ASH": [
                        '#352D2C',
                        '#8E7156',
                        '#090707',
                        '#030202',
                        '#231A1A',
                        '#3D312E'],
                    "PALECREAM": [
                        '#FFFBF0',
                        '#FFFFFF',
                        '#FFEED8',
                        '#EDB690',
                        '#FFDFB9',
                        '#FFFCF3']
                }
            },
            
            "bengal": {
                "WHITE": [
                    '#F5F5F5',
                    '#FFFFFF',
                    '#E7E6EB',
                    '#BEBDBE',
                    '#D4D3D3',
                    '#CDCCCE',
                    '#D7D6D6'],
                "PALEGREY": [
                    '#C4C9CE',
                    '#F8F8F5',
                    '#959AA0',
                    '#1A1A20',
                    '#403F4A',
                    '#47494F',
                    '#7D7C81'],
                "SILVER": [
                    '#C0C6CF',
                    '#F8F8F5',
                    '#7D828A',
                    '#43464D',
                    '#5F6571',
                    '#595C64',
                    '#92969C'],
                "GREY": [
                    '#8B919C',
                    '#F2F2DB',
                    '#6B7078',
                    '#43464D',
                    '#666B75',
                    '#53565E',
                    '#939594'],
                "DARKGREY": [
                    '#A0A2A9',
                    '#F8F8F5',
                    '#4F5155',
                    '#1E1E24',
                    '#403F4A',
                    '#1E1E24',
                    '#403F4A'],
                "GHOST": [
                    '#525D65',
                    '#8899A9',
                    '#2F353A',
                    '#0A0D15',
                    '#0F0F12',
                    '#171B24',
                    '#171B24'],
                "BLACK": [
                    '#7E7878',
                    '#C7C3BA',
                    '#35353A',
                    '#0E0E11',
                    '#1E1E24',
                    '#0E0E11',
                    '#1E1E24'],
                "CREAM": [
                    '#F3D6B2',
                    '#FEFDFD',
                    '#EFBC8E',
                    '#D3A17A',
                    '#EFBC8E',
                    '#DCAA82',
                    '#F0CEAF'],
                "PALEGINGER": [
                    '#C4C9CE',
                    '#EBDDD3',
                    '#E2A36F',
                    '#C5875A',
                    '#E2A36F',
                    '#CF9162',
                    '#E3B590'],
                "GOLDEN": [
                    '#EECB83',
                    '#F3ECD9',
                    '#E6B575',
                    '#6C4C3A',
                    '#CD9170',
                    '#98724F',
                    '#D2AB90'],
                "GINGER": [
                    '#F2A96B',
                    '#FFF0B6',
                    '#DB8A51',
                    '#A8582B',
                    '#EF884C',
                    '#BA6A38',
                    '#EEA76D'],
                "DARKGINGER": [
                    '#D37642',
                    '#FFEFB6',
                    '#BD5629',
                    '#6F2E17',
                    '#AC4825',
                    '#8B3C1E',
                    '#9B5837'],
                "SIENNA": [
                    '#AC5D43',
                    '#D4C498',
                    '#A9563D',
                    '#482628',
                    '#743839',
                    '#89433C',
                    '#89433C'],
                "LIGHTBROWN": [
                    '#E0CFAD',
                    '#F8F7F4',
                    '#B4A07E',
                    '#877358',
                    '#BCA07B',
                    '#978366',
                    '#BEA887'],
                "LILAC": [
                    '#B79088',
                    '#DEC3A6',
                    '#AA9F9E',
                    '#654749',
                    '#876162',
                    '#8C7475',
                    '#8C7475'],
                "BROWN": [
                    '#A5856B',
                    '#F3ECDA',
                    '#8D6A4E',
                    '#46362E',
                    '#644C41',
                    '#604839',
                    '#938173'],
                "GOLDEN-BROWN": [
                    '#A26655',
                    '#DECBA5',
                    '#896C5D',
                    '#281B17',
                    '#7F5548',
                    '#65443B',
                    '#6B473D'],
                "DARKBROWN": [
                    '#685E57',
                    '#EAE1C9',
                    '#2F2A27',
                    '#110B0A',
                    '#3B2723',
                    '#110B0A',
                    '#3B2723'],
                "CHOCOLATE": [
                    '#774D48',
                    '#C1A79D',
                    '#473F46',
                    '#241A1C',
                    '#382021',
                    '#523133',
                    '#523133'],
                "LAVENDER": [
                    '#E3DFE7',
                    '#F9FBFF',
                    '#C0B9C0',
                    '#6B5F7A',
                    '#8A829B',
                    '#9D96AB',
                    '#AE9FB2'],
                "ASH": [
                    '#392F2D',
                    '#7D5A4C',
                    '#110D0D',
                    '#030202',
                    '#231A19',
                    '#060404',
                    '#231A19'],
                "PALECREAM": [
                    '#FFFBF0',
                    '#FFFFFF',
                    '#FFF2E0',
                    '#F6D1B6',
                    '#F9DFCD',
                    '#F9DCC8',
                    '#FCEDE4']
            }
        }
        # to handle the ones with more special coloration - special are for overridden colors for that specific marking and then bengal is just... sharing bengal lol
        # why am I explaining... who knows
        color_type_dict = {
            "special": ["SINGLESTRIPE"],
            "bengal": ["BENGAL", "MARBLED"]
        }

        # waeh
        skin_dict = {
            "BLACK": "#5E504B",
            "RED": "#BE4E32",
            "PINK": "#FABFB7",
            "DARKBROWN": "#5A4235",
            "BROWN": "#816559",
            "LIGHTBROWN": "#977A67",
            "DARK": "#24211E",
            "DARKGREY": "#4F4A48",
            "GREY": "#736B64",
            "DARKSALMON": "#A55C43",
            "SALMON": "#D29777",
            "PEACH": "#F9C0A2",
            "DARKMARBLED": "#2A1F1D",
            "MARBLED": "#CC9587",
            "LIGHTMARBLED": "#433130",
            "DARKBLUE": "#3B474C",
            "BLUE": "#4E5B61",
            "LIGHTBLUE": "#5B666B",
        }

        wing_scars = []

        # Get colors - makes things easier for later lol
        if cat.pelt.name not in ['Tortie', 'Calico']:
            # Get dict
            if cat.pelt.name.upper() in color_type_dict['special']:
                color_type = "special"
            elif cat.pelt.name.upper() in color_type_dict['bengal']:
                color_type = "bengal"
            else:
                color_type = 0

            cat_marking = cat.pelt.name.upper()
            if color_type == "special":

                base_pelt = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][0]
                base_underfur_pelt = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][1]
                base_overfur_pelt = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][2]
                marking_base = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][3]
                marking_fade = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][4]
                marking_inside = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][5]
            elif color_type == 0:
                base_pelt = color_dict['solid'][f'{cat.pelt.colour}'][0]
                base_underfur_pelt = color_dict['solid'][f'{cat.pelt.colour}'][1]
                base_overfur_pelt = color_dict['solid'][f'{cat.pelt.colour}'][2]
                marking_base = color_dict['solid'][f'{cat.pelt.colour}'][3]
                marking_fade = color_dict['solid'][f'{cat.pelt.colour}'][4]
                marking_inside = color_dict['solid'][f'{cat.pelt.colour}'][5]
            else:
                base_pelt = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][0]
                base_underfur_pelt = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][1]
                base_overfur_pelt = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][2]
                marking_base = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][3]
                marking_fade = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][4]
                marking_inside = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][5]
                marking_inside_fade = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][6]
        else:
            cat_marking = cat.pelt.tortiebase.upper()
            # Get dict
            if cat.pelt.tortiebase.upper() in color_type_dict['special']:
                color_type = "special"
            elif cat.pelt.tortiebase.upper() in color_type_dict['bengal']:
                color_type = "bengal"
            else:
                color_type = 0

            # Get dict of tortie
            if cat.pelt.tortiepattern.upper() in color_type_dict['special']:
                tortie_color_type = "special"
            elif cat.pelt.tortiepattern.upper() in color_type_dict['bengal']:
                tortie_color_type = "bengal"
            else:
                tortie_color_type = 0
            
            if color_type == "special":

                base_pelt = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][0]
                base_underfur_pelt = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][1]
                base_overfur_pelt = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][2]
                marking_base = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][3]
                marking_fade = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][4]
                marking_inside = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][5]
            elif color_type == 0:
                base_pelt = color_dict['solid'][f'{cat.pelt.colour}'][0]
                base_underfur_pelt = color_dict['solid'][f'{cat.pelt.colour}'][1]
                base_overfur_pelt = color_dict['solid'][f'{cat.pelt.colour}'][2]
                marking_base = color_dict['solid'][f'{cat.pelt.colour}'][3]
                marking_fade = color_dict['solid'][f'{cat.pelt.colour}'][4]
                marking_inside = color_dict['solid'][f'{cat.pelt.colour}'][5]
            else:
                base_pelt = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][0]
                base_underfur_pelt = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][1]
                base_overfur_pelt = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][2]
                marking_base = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][3]
                marking_fade = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][4]
                marking_inside = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][5]
                marking_inside_fade = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][6]

            if tortie_color_type == "special":
                tortie_base_pelt = color_dict['special'][f'{cat.pelt.tortiebase}'][f'{cat.pelt.tortiecolour}'][0]
                tortie_base_underfur_pelt = color_dict['special'][f'{cat.pelt.tortiebase}'][f'{cat.pelt.tortiecolour}'][1]
                tortie_base_overfur_pelt = color_dict['special'][f'{cat.pelt.tortiebase}'][f'{cat.pelt.tortiecolour}'][2]
                tortie_marking_base = color_dict['special'][f'{cat.pelt.tortiebase}'][f'{cat.pelt.tortiecolour}'][3]
                tortie_marking_fade = color_dict['special'][f'{cat.pelt.tortiebase}'][f'{cat.pelt.tortiecolour}'][4]
                tortie_marking_inside = color_dict['special'][f'{cat.pelt.tortiebase}'][f'{cat.pelt.tortiecolour}'][5]
            elif tortie_color_type == 0:
                tortie_base_pelt = color_dict['solid'][f'{cat.pelt.tortiecolour}'][0]
                tortie_base_underfur_pelt = color_dict['solid'][f'{cat.pelt.tortiecolour}'][1]
                tortie_base_overfur_pelt = color_dict['solid'][f'{cat.pelt.tortiecolour}'][2]
                tortie_marking_base = color_dict['solid'][f'{cat.pelt.tortiecolour}'][3]
                tortie_marking_fade = color_dict['solid'][f'{cat.pelt.tortiecolour}'][4]
                tortie_marking_inside = color_dict['solid'][f'{cat.pelt.tortiecolour}'][5]
            else:
                tortie_base_pelt = color_dict[f'{tortie_color_type}'][f'{cat.pelt.tortiecolour}'][0]
                tortie_base_underfur_pelt = color_dict[f'{tortie_color_type}'][f'{cat.pelt.tortiecolour}'][1]
                tortie_base_overfur_pelt = color_dict[f'{tortie_color_type}'][f'{cat.pelt.tortiecolour}'][2]
                tortie_marking_base = color_dict[f'{tortie_color_type}'][f'{cat.pelt.tortiecolour}'][3]
                tortie_marking_fade = color_dict[f'{tortie_color_type}'][f'{cat.pelt.tortiecolour}'][4]
                tortie_marking_inside = color_dict[f'{tortie_color_type}'][f'{cat.pelt.tortiecolour}'][5]
                tortie_marking_inside_fade = color_dict[f'{tortie_color_type}'][f'{cat.pelt.tortiecolour}'][6]

        # draw pelt
        base_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        base_tint.fill(base_pelt)

        new_sprite.blit(base_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        # draw overlays
        underfur_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        underfur_tint.fill(base_underfur_pelt)

        overfur_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        overfur_tint.fill(base_overfur_pelt)

        if cat_marking in ['BENGAL', 'MARBLED']:
            underfur = sprites.sprites['underfur' + 'BENGAL' + cat_sprite].copy()
            underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            underfur.blit(sprites.sprites['underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        elif cat_marking in ['SINGLESTRIPE']:
            underfur = sprites.sprites['underfur' + 'SOLID' + cat_sprite].copy()
            underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            underfur.blit(sprites.sprites['underfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            underfur = sprites.sprites['underfur' + 'BASIC' + cat_sprite].copy()
            underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            underfur.blit(sprites.sprites['underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        new_sprite.blit(underfur, (0, 0))
            

        if cat_marking in ['BENGAL', 'MARBLED']:
            overfur = sprites.sprites['overfur' + 'BENGAL' + cat_sprite].copy()
            overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            overfur.blit(sprites.sprites['overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        elif cat_marking in ['SINGLESTRIPE']:
            overfur = sprites.sprites['overfur' + 'SOLID' + cat_sprite].copy()
            overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            overfur.blit(sprites.sprites['overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            overfur = sprites.sprites['overfur' + 'BASIC' + cat_sprite].copy()
            overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            overfur.blit(sprites.sprites['overfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        new_sprite.blit(overfur, (0, 0))

        # draw markings

        if cat_marking not in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
            markings_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            markings_tint.fill(marking_base)

            mark_fade_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            mark_fade_tint.fill(marking_fade)

            markings = sprites.sprites['markings' + cat_marking + cat_sprite].copy().convert_alpha()
            markings.blit(markings_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            # uh...
            if cat_marking in ['BENGAL', 'MARBLED']:
                mark_fade = sprites.sprites['underfur' + 'BENGAL' + cat_sprite].copy()
                mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                mark_fade.blit(sprites.sprites['underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            elif cat_marking in ['SINGLESTRIPE']:
                mark_fade = sprites.sprites['overfur' + 'SOLID' + cat_sprite].copy()
                mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                mark_fade.blit(sprites.sprites['overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
            else:
                mark_fade = sprites.sprites['underfur' + 'BASIC' + cat_sprite].copy()
                mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                mark_fade.blit(sprites.sprites['underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            mark_fade.blit(sprites.sprites['markings' + cat_marking + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            markings.blit(mark_fade, (0, 0))

            if cat_marking in ['SOKOKE', 'MARBLED', 'BENGAL', 'ROSETTE', 'MASKED']:
                markings_inside_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                markings_inside_tint.fill(marking_inside)


                markings_inside = sprites.sprites['markinside' + cat_marking + cat_sprite].copy().convert_alpha()
                markings_inside.blit(markings_inside_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                # i am thirsty i should get water
                if cat_marking in ['BENGAL', 'MARBLED']:
                    markings_inside_fade = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                    try:
                        markings_inside_fade.fill(marking_inside_fade)
                    except:
                        print(cat_marking)
                        print(cat.pelt.colour)
                        print(cat.pelt.name)
                        print(color_type)

                    mark_inside_fade = sprites.sprites['underfur' + 'BENGAL' + cat_sprite].copy()
                    mark_inside_fade.blit(markings_inside_fade, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    mark_inside_fade.blit(sprites.sprites['underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    markings_inside.blit(mark_inside_fade, (0, 0))

                    mark_inside_fade.blit(sprites.sprites['markinside' + cat_marking + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    markings_inside.blit(mark_inside_fade, (0, 0))
                
                markings_inside.blit(sprites.sprites['markinside' + cat_marking + cat_sprite], (0,0), special_flags=pygame.BLEND_RGBA_MULT)
                markings.blit(markings_inside, (0, 0))
        
            # appear.
            new_sprite.blit(markings, (0, 0))

        # draw tortie
        if cat.pelt.name in ['Tortie', 'Calico']:
            patches = sprites.sprites["tortiemask" + cat.pelt.pattern + cat_sprite].copy()

            tortie_base_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            tortie_base_tint.fill(tortie_base_pelt)

            # draw base
            patches.blit(tortie_base_tint, (0,0), special_flags=pygame.BLEND_RGB_MULT)
            
            # draw overlays aa
            tortie_underfur_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            tortie_underfur_tint.fill(tortie_base_underfur_pelt)

            tortie_overfur_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            tortie_overfur_tint.fill(tortie_base_overfur_pelt)

            if cat.pelt.tortiepattern.upper() in ['BENGAL', 'MARBLED']:
                tortie_underfur = sprites.sprites['underfur' + 'BENGAL' + cat_sprite].copy()
                tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_underfur.blit(sprites.sprites['underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                patches.blit(tortie_underfur, (0, 0))
            elif cat.pelt.tortiepattern.upper() in ['SINGLESTRIPE']:
                tortie_underfur = sprites.sprites['underfur' + 'SOLID' + cat_sprite].copy()
                tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_underfur.blit(sprites.sprites['underfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                patches.blit(tortie_underfur, (0, 0))
            else:
                tortie_underfur = sprites.sprites['underfur' + 'BASIC' + cat_sprite].copy()
                tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_underfur.blit(sprites.sprites['underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                patches.blit(tortie_underfur, (0, 0))
                

            if cat.pelt.tortiepattern.upper() in ['BENGAL', 'MARBLED']:
                tortie_overfur = sprites.sprites['overfur' + 'BENGAL' + cat_sprite].copy()
                tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_overfur.blit(sprites.sprites['overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            elif cat.pelt.tortiepattern.upper() in ['SINGLESTRIPE']:
                tortie_overfur = sprites.sprites['overfur' + 'SOLID' + cat_sprite].copy()
                tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_overfur.blit(sprites.sprites['overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            else:
                tortie_overfur = sprites.sprites['overfur' + 'BASIC' + cat_sprite].copy()
                tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_overfur.blit(sprites.sprites['overfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            patches.blit(tortie_overfur, (0, 0))

            # draw markings

            if cat.pelt.tortiepattern.upper() not in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
                tortie_markings_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tortie_markings_tint.fill(tortie_marking_base)

                tortie_mark_fade_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tortie_mark_fade_tint.fill(tortie_marking_fade)

                tortie_markings = sprites.sprites['markings' + cat.pelt.tortiepattern.upper() + cat_sprite].copy().convert_alpha()
                tortie_markings.blit(tortie_markings_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                # uh...
                if cat.pelt.tortiepattern.upper() in ['BENGAL', 'MARBLED']:
                    tortie_mark_fade = sprites.sprites['underfur' + 'BENGAL' + cat_sprite].copy()
                    tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    tortie_mark_fade.blit(sprites.sprites['underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                elif cat.pelt.tortiepattern.upper() in ['SINGLESTRIPE']:
                    tortie_mark_fade = sprites.sprites['overfur' + 'SOLID' + cat_sprite].copy()
                    tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    tortie_mark_fade.blit(sprites.sprites['overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    
                else:
                    tortie_mark_fade = sprites.sprites['underfur' + 'BASIC' + cat_sprite].copy()
                    tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    tortie_mark_fade.blit(sprites.sprites['underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                tortie_mark_fade.blit(sprites.sprites['markings' + cat.pelt.tortiepattern.upper() + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                tortie_markings.blit(tortie_mark_fade, (0, 0))

                if cat.pelt.tortiepattern.upper() in ['SOKOKE', 'MARBLED', 'BENGAL', 'ROSETTE', 'MASKED']:
                    tortie_markings_inside_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                    tortie_markings_inside_tint.fill(tortie_marking_inside)

                    tortie_markings_inside = sprites.sprites['markinside' + cat.pelt.tortiepattern.upper() + cat_sprite].copy().convert_alpha()
                    tortie_markings_inside.blit(tortie_markings_inside_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    # my eyes are dry - inside markings
                    if cat.pelt.tortiepattern.upper() in ['BENGAL', 'MARBLED']:
                        tortie_markings_inside_fade = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                        try:
                            tortie_markings_inside_fade.fill(tortie_marking_inside_fade)
                        except:
                            print(cat_marking)
                            print(cat.pelt.tortiecolour)
                            print(cat.pelt.tortiepattern)
                            print(tortie_color_type)
                        

                        tortie_mark_inside_fade = sprites.sprites['underfur' + 'BENGAL' + cat_sprite].copy()
                        tortie_mark_inside_fade.blit(tortie_markings_inside_fade, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        tortie_mark_inside_fade.blit(sprites.sprites['underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                        tortie_markings_inside.blit(tortie_mark_inside_fade, (0, 0))

                        tortie_mark_inside_fade.blit(sprites.sprites['markinside' + cat_marking + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                        tortie_markings_inside.blit(tortie_mark_inside_fade, (0, 0))
                        
                    tortie_markings_inside.blit(sprites.sprites['markinside' + cat.pelt.tortiepattern.upper() + cat_sprite], (0,0), special_flags=pygame.BLEND_RGBA_MULT)
                    tortie_markings.blit(tortie_markings_inside, (0, 0))
        
                # appear.
                patches.blit(tortie_markings, (0, 0))

            # *microwave.sfx*
            patches.blit(sprites.sprites["tortiemask" + cat.pelt.pattern + cat_sprite], (0,0), special_flags=pygame.BLEND_RGBA_MULT)

            new_sprite.blit(patches, (0, 0))

        # TINT because tints still exist lol
        if cat.pelt.tint != "none" and cat.pelt.tint in sprites.cat_tints["tint_colours"]:
            # Multiply with alpha does not work as you would expect - it just lowers the alpha of the
            # entire surface. To get around this, we first blit the tint onto a white background to dull it,
            # then blit the surface onto the sprite with pygame.BLEND_RGB_MULT
            tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            tint.fill(tuple(sprites.cat_tints["tint_colours"][cat.pelt.tint]))
            new_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        # draw white patches
        if cat.pelt.white_patches is not None:
            white_patches = sprites.sprites['white' + cat.pelt.white_patches + cat_sprite].copy()

            # Apply tint to white patches.
            if cat.pelt.white_patches_tint != "none" and cat.pelt.white_patches_tint in sprites.white_patches_tints[
                "tint_colours"]:
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(tuple(sprites.white_patches_tints["tint_colours"][cat.pelt.white_patches_tint]))
                white_patches.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            new_sprite.blit(white_patches, (0, 0))

        # draw vit & points

        if cat.pelt.points:
            points = sprites.sprites['white' + cat.pelt.points + cat_sprite].copy()
            if cat.pelt.white_patches_tint != "none" and cat.pelt.white_patches_tint in sprites.white_patches_tints[
                "tint_colours"]:
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(tuple(sprites.white_patches_tints["tint_colours"][cat.pelt.white_patches_tint]))
                points.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            new_sprite.blit(points, (0, 0))

        if cat.pelt.vitiligo:
            new_sprite.blit(sprites.sprites['white' + cat.pelt.vitiligo + cat_sprite], (0, 0))

        # draw eyes & scars1
        eyes = sprites.sprites['eyes' + cat.pelt.eye_colour + cat_sprite].copy()
        if cat.pelt.eye_colour2 != None:
            eyes.blit(sprites.sprites['eyes2' + cat.pelt.eye_colour2 + cat_sprite], (0, 0))
        new_sprite.blit(eyes, (0, 0))

        if not scars_hidden:
            for scar in cat.pelt.scars:
                if scar in cat.pelt.scars1:
                    new_sprite.blit(sprites.sprites['scars' + scar + cat_sprite], (0, 0))
                if scar in cat.pelt.scars3:
                    new_sprite.blit(sprites.sprites['scars' + scar + cat_sprite], (0, 0))

        # draw line art
        if game.settings['shaders'] and not dead:
            new_sprite.blit(sprites.sprites['shaders' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            new_sprite.blit(sprites.sprites['lighting' + cat_sprite], (0, 0))

        if not dead:
            new_sprite.blit(sprites.sprites['lines' + cat_sprite], (0, 0))
        elif cat.df:
            new_sprite.blit(sprites.sprites['lineartdf' + cat_sprite], (0, 0))
        elif dead:
            new_sprite.blit(sprites.sprites['lineartdead' + cat_sprite], (0, 0))
        # draw skin and scars2
        blendmode = pygame.BLEND_RGBA_MIN
        new_sprite.blit(sprites.sprites['skin' + cat.pelt.skin + cat_sprite], (0, 0))
        
        if not scars_hidden:
            for scar in cat.pelt.scars:
                if scar in cat.pelt.scars2:
                    new_sprite.blit(sprites.sprites['scars' + scar + cat_sprite], (0, 0), special_flags=blendmode)

        # draw accessories
        if not acc_hidden:        
            if cat.pelt.accessory in cat.pelt.plant_accessories:
                new_sprite.blit(sprites.sprites['acc_herbs' + cat.pelt.accessory + cat_sprite], (0, 0))
            elif cat.pelt.accessory in cat.pelt.wild_accessories:
                new_sprite.blit(sprites.sprites['acc_wild' + cat.pelt.accessory + cat_sprite], (0, 0))
            elif cat.pelt.accessory in cat.pelt.collars:
                new_sprite.blit(sprites.sprites['collars' + cat.pelt.accessory + cat_sprite], (0, 0))

        # draw wings oh boy this will be fun :3c hahaaa

        ########################################################################
        #                                                                      #
        # wing start lol lmao love this                                        #
        #                                                                      #
        ########################################################################

        if cat.species != "earth cat":
            
            # draw base
            wings = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            wings.blit(sprites.sprites[f'{cat.species}' + 'base' + cat_sprite], (0, 0))

            wings.blit(base_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            if cat_marking in ['BENGAL', 'MARBLED']:
                w_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                w_underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                w_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                new_sprite.blit(w_underfur, (0, 0))
            elif cat_marking in ['SINGLESTRIPE']:
                w_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite].copy()
                w_underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                w_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                wings.blit(w_underfur, (0, 0))
            else:
                w_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                w_underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                w_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                wings.blit(w_underfur, (0, 0))
                

            if cat_marking in ['BENGAL', 'MARBLED']:
                w_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite].copy()
                w_overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                w_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            elif cat_marking in ['SINGLESTRIPE']:
                w_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite].copy()
                w_overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                w_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            else:
                w_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'BASIC' + cat_sprite].copy()
                w_overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                w_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            wings.blit(w_overfur, (0, 0))

            # draw markings

            if cat_marking not in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:

                w_markings = sprites.sprites[f'{cat.species}' + 'markings' + cat_marking + cat_sprite].copy().convert_alpha()
                w_markings.blit(markings_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                # uh...
                if cat_marking in ['BENGAL', 'MARBLED']:
                    w_mark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                    w_mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                elif cat_marking in ['SINGLESTRIPE']:
                    w_mark_fade = sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite].copy()
                    w_mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    
                else:
                    w_mark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                    w_mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                w_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'markings' + cat_marking + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                w_markings.blit(w_mark_fade, (0, 0))

                if cat_marking in ['SOKOKE', 'MARBLED', 'BENGAL', 'ROSETTE']:

                    w_markings_inside = sprites.sprites[f'{cat.species}' + 'markinside' + cat_marking + cat_sprite].copy().convert_alpha()
                    w_markings_inside.blit(markings_inside_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    # I hate how many times this needs done
                    if cat_marking in ['BENGAL', 'MARBLED']:
                        w_markings_inside_fade = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                        w_markings_inside_fade.fill(marking_inside_fade)

                        w_mark_inside_fade = sprites.sprites['underfur' + 'BENGAL' + cat_sprite].copy()
                        w_mark_inside_fade.blit(w_markings_inside_fade, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        w_mark_inside_fade.blit(sprites.sprites['underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                        w_markings_inside.blit(w_mark_inside_fade, (0, 0))

                        w_mark_inside_fade.blit(sprites.sprites['markinside' + cat_marking + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                        w_markings_inside.blit(w_mark_inside_fade, (0, 0))
                    
                    w_markings_inside.blit(sprites.sprites[f'{cat.species}' + 'markinside' + cat_marking + cat_sprite], (0,0), special_flags=pygame.BLEND_RGBA_MULT)
                    w_markings.blit(w_markings_inside, (0, 0))
            
                # appear.
                wings.blit(w_markings, (0, 0))

            # draw tortie
            if cat.pelt.name in ['Tortie', 'Calico']:
                w_patches = sprites.sprites["tortiemask" + cat.pelt.pattern + cat_sprite].copy()

                # draw base
                w_patches.blit(tortie_base_tint, (0,0), special_flags=pygame.BLEND_RGB_MULT)

                if cat.pelt.tortiepattern.upper() in ['BENGAL', 'MARBLED']:
                    w_tortie_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                    w_tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    tortie_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    w_patches.blit(w_tortie_underfur, (0, 0))
                elif cat.pelt.tortiepattern.upper() in ['SINGLESTRIPE']:
                    w_tortie_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite].copy()
                    w_tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_tortie_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    w_patches.blit(w_tortie_underfur, (0, 0))
                else:
                    w_tortie_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                    w_tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_tortie_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    w_patches.blit(w_tortie_underfur, (0, 0))
                    

                if cat.pelt.tortiepattern.upper() in ['BENGAL', 'MARBLED']:
                    w_tortie_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite].copy()
                    w_tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_tortie_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                elif cat.pelt.tortiepattern.upper() in ['SINGLESTRIPE']:
                    w_tortie_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite].copy()
                    w_tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_tortie_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                else:
                    w_tortie_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'BASIC' + cat_sprite].copy()
                    w_tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_tortie_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                w_patches.blit(w_tortie_overfur, (0, 0))

                # draw markings

                if cat.pelt.tortiepattern.upper() not in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:

                    w_tortie_markings = sprites.sprites[f'{cat.species}' + 'markings' + cat.pelt.tortiepattern.upper() + cat_sprite].copy().convert_alpha()
                    w_tortie_markings.blit(tortie_markings_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    # uh...
                    if cat.pelt.tortiepattern.upper() in ['BENGAL', 'MARBLED']:
                        w_tortie_mark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                        w_tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        w_tortie_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    elif cat.pelt.tortiepattern.upper() in ['SINGLESTRIPE']:
                        w_tortie_mark_fade = sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite].copy()
                        w_tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        w_tortie_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        
                    else:
                        w_tortie_mark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                        w_tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        w_tortie_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    w_tortie_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'markings' + cat.pelt.tortiepattern.upper() + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    w_tortie_markings.blit(w_tortie_mark_fade, (0, 0))

                    if cat.pelt.tortiepattern.upper() in ['SOKOKE', 'MARBLED', 'BENGAL', 'ROSETTE']:
                        w_tortie_markings_inside_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                        w_tortie_markings_inside_tint.fill(tortie_marking_inside)

                        w_tortie_markings_inside = sprites.sprites[f'{cat.species}' + 'markinside' + cat.pelt.tortiepattern.upper() + cat_sprite].copy().convert_alpha()
                        w_tortie_markings_inside.blit(tortie_markings_inside_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        # marking inside for tortie
                        if cat_marking in ['BENGAL', 'MARBLED']:
                            w_tortie_markings_inside_fade = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                            w_tortie_markings_inside_fade.fill(tortie_marking_inside_fade)

                            w_tortie_mark_inside_fade = sprites.sprites['underfur' + 'BENGAL' + cat_sprite].copy()
                            w_tortie_mark_inside_fade.blit(tortie_markings_inside_fade, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                            w_tortie_mark_inside_fade.blit(sprites.sprites['underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                            w_tortie_markings_inside.blit(w_tortie_mark_inside_fade, (0, 0))

                            w_tortie_mark_inside_fade.blit(sprites.sprites['markinside' + cat_marking + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                            w_tortie_markings_inside.blit(w_tortie_mark_inside_fade, (0, 0))
                        
                        w_tortie_markings_inside.blit(sprites.sprites[f'{cat.species}' + 'markinside' + cat.pelt.tortiepattern.upper() + cat_sprite], (0,0), special_flags=pygame.BLEND_RGBA_MULT)
                        w_tortie_markings.blit(w_tortie_markings_inside, (0, 0))
                
                    # appear.
                    w_patches.blit(w_tortie_markings, (0, 0))

                # *microwave.sfx*
                w_patches.blit(sprites.sprites["tortiemask" + cat.pelt.pattern + cat_sprite], (0,0), special_flags=pygame.BLEND_RGBA_MULT)

                wings.blit(w_patches, (0, 0))

            # TINT because tints still exist lol
            if cat.pelt.tint != "none" and cat.pelt.tint in sprites.cat_tints["tint_colours"]:
                # Multiply with alpha does not work as you would expect - it just lowers the alpha of the
                # entire surface. To get around this, we first blit the tint onto a white background to dull it,
                # then blit the surface onto the sprite with pygame.BLEND_RGB_MULT
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(tuple(sprites.cat_tints["tint_colours"][cat.pelt.tint]))
                wings.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            # draw white patches
            if cat.pelt.white_patches is not None:
                white_patches = sprites.sprites['white' + cat.pelt.white_patches + cat_sprite].copy()

                # Apply tint to white patches.
                if cat.pelt.white_patches_tint != "none" and cat.pelt.white_patches_tint in sprites.white_patches_tints[
                    "tint_colours"]:
                    tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                    tint.fill(tuple(sprites.white_patches_tints["tint_colours"][cat.pelt.white_patches_tint]))
                    white_patches.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                #wings.blit(white_patches, (0, 0))

            # draw vit & points

            if cat.pelt.points:
                points = sprites.sprites['white' + cat.pelt.points + cat_sprite].copy()
                if cat.pelt.white_patches_tint != "none" and cat.pelt.white_patches_tint in sprites.white_patches_tints[
                    "tint_colours"]:
                    tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                    tint.fill(tuple(sprites.white_patches_tints["tint_colours"][cat.pelt.white_patches_tint]))
                    points.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                wings.blit(points, (0, 0))

            if cat.pelt.vitiligo:
                wings.blit(sprites.sprites['white' + cat.pelt.vitiligo + cat_sprite], (0, 0))

            wings.blit(sprites.sprites[f'{cat.species}' + 'base' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            # scars here whenever I do that...

            # draw line art
            if game.settings['shaders'] and not dead:
                wings.blit(sprites.sprites['shaders' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                wings.blit(sprites.sprites['lighting' + cat_sprite], (0, 0))

            if not dead:
                wings.blit(sprites.sprites[f'{cat.species}' + 'lines' + cat_sprite], (0, 0))
            elif cat.df:
                wings.blit(sprites.sprites[f'{cat.species}' + 'lineartdf' + cat_sprite], (0, 0))
            elif dead:
                wings.blit(sprites.sprites[f'{cat.species}' + 'lineartdead' + cat_sprite], (0, 0))
            # draw scars2
            blendmode = pygame.BLEND_RGBA_MIN
            # draw skin
            if cat.species == "bat cat":
                skin_color = skin_dict[f'{cat.pelt.skin}']
                membrane = sprites.sprites['batskin' + cat_sprite]

                membrane_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                membrane_tint.fill(skin_color)
                membrane.blit(membrane_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                membrane_tint2 = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                membrane_tint2.fill(base_underfur_pelt)

                membrane.blit(membrane_tint2, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

                wings.blit(membrane, (0, 0))
            
            if not scars_hidden:
                for scar in cat.pelt.scars:
                    if scar in cat.pelt.scars2:
                        wings.blit(sprites.sprites['scars' + scar + cat_sprite], (0, 0), special_flags=blendmode)
            
            new_sprite.blit(wings, (0, 0))
        
        ########################################################################
        #                                                                      #
        #end wings because I will get confused as hell if I don't put this here#
        #                                                                      #
        ########################################################################


        # Apply fading fog
        if cat.pelt.opacity <= 97 and not cat.prevent_fading and game.clan.clan_settings["fading"] and dead:

            stage = "0"
            if 80 >= cat.pelt.opacity > 45:
                # Stage 1
                stage = "1"
            elif cat.pelt.opacity <= 45:
                # Stage 2
                stage = "2"

            new_sprite.blit(sprites.sprites['fademask' + stage + cat_sprite],
                            (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            if cat.df:
                temp = sprites.sprites['fadedf' + stage + cat_sprite].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp
            else:
                temp = sprites.sprites['fadestarclan' + stage + cat_sprite].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp

        # reverse, if assigned so
        if cat.pelt.reverse:
            new_sprite = pygame.transform.flip(new_sprite, True, False)

    except (TypeError, KeyError):
        logger.exception("Failed to load sprite")

        # Placeholder image
        new_sprite = image_cache.load_image(f"sprites/error_placeholder.png").convert_alpha()

    return new_sprite

def apply_opacity(surface, opacity):
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            pixel = list(surface.get_at((x, y)))
            pixel[3] = int(pixel[3] * opacity / 100)
            surface.set_at((x, y), tuple(pixel))
    return surface


# ---------------------------------------------------------------------------- #
#                                     OTHER                                    #
# ---------------------------------------------------------------------------- #

def chunks(L, n):
    return [L[x: x + n] for x in range(0, len(L), n)]

def is_iterable(y):
    try:
        0 in y
    except TypeError:
        return False


def get_text_box_theme(theme_name=""):
    """Updates the name of the theme based on dark or light mode"""
    if game.settings['dark mode']:
        if theme_name == "":
            return "#default_dark"
        else:
            return theme_name + "_dark"
    else:
        if theme_name == "":
            return "#text_box"
        else:
            return theme_name


def quit(savesettings=False, clearevents=False):
    """
    Quits the game, avoids a bunch of repeated lines
    """
    if savesettings:
        game.save_settings()
    if clearevents:
        game.cur_events_list.clear()
    game.rpc.close_rpc.set()
    game.rpc.update_rpc.set()
    pygame.display.quit()
    pygame.quit()
    if game.rpc.is_alive():
        game.rpc.join(1)
    sys_exit()


PERMANENT = None
with open(f"resources/dicts/conditions/permanent_conditions.json", 'r') as read_file:
    PERMANENT = ujson.loads(read_file.read())

ACC_DISPLAY = None
with open(f"resources/dicts/acc_display.json", 'r') as read_file:
    ACC_DISPLAY = ujson.loads(read_file.read())

SNIPPETS = None
with open(f"resources/dicts/snippet_collections.json", 'r') as read_file:
    SNIPPETS = ujson.loads(read_file.read())

PREY_LISTS = None
with open(f"resources/dicts/prey_text_replacements.json", 'r') as read_file:
    PREY_LISTS = ujson.loads(read_file.read())

with open(f"resources/dicts/backstories.json", 'r') as read_file:
    BACKSTORIES = ujson.loads(read_file.read())
