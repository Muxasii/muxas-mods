import random
from random import choice
from re import sub

import i18n

from scripts.cat.sprites import sprites
from scripts.game_structure.game_essentials import game
from scripts.game_structure.localization import get_lang_config


class Pelt:
    sprites_names = {
        "SingleColour": "single",
        "TwoColour": "single",
        "Tabby": "tabby",
        "Marbled": "marbled",
        "Rosette": "rosette",
        "Smoke": "smoke",
        "Ticked": "ticked",
        "Speckled": "speckled",
        "Bengal": "bengal",
        "Mackerel": "mackerel",
        "Classic": "classic",
        "Sokoke": "sokoke",
        "Agouti": "agouti",
        "Singlestripe": "singlestripe",
        "Masked": "masked",
        "Tortie": None,
        "Calico": None,
    }

    # ATTRIBUTES, including non-pelt related
    pelt_colours = [
        "WHITE",
        "PALEGREY",
        "SILVER",
        "GREY",
        "DARKGREY",
        "GHOST",
        "BLACK",
        "CREAM",
        "PALEGINGER",
        "GOLDEN",
        "GINGER",
        "DARKGINGER",
        "SIENNA",
        "LIGHTBROWN",
        "LILAC",
        "BROWN",
        "GOLDEN-BROWN",
        "DARKBROWN",
        "CHOCOLATE",
    ]
    pelt_c_no_white = [
        "PALEGREY",
        "SILVER",
        "GREY",
        "DARKGREY",
        "GHOST",
        "BLACK",
        "CREAM",
        "PALEGINGER",
        "GOLDEN",
        "GINGER",
        "DARKGINGER",
        "SIENNA",
        "LIGHTBROWN",
        "LILAC",
        "BROWN",
        "GOLDEN-BROWN",
        "DARKBROWN",
        "CHOCOLATE",
    ]
    pelt_c_no_bw = [
        "PALEGREY",
        "SILVER",
        "GREY",
        "DARKGREY",
        "CREAM",
        "PALEGINGER",
        "GOLDEN",
        "GINGER",
        "DARKGINGER",
        "SIENNA",
        "LIGHTBROWN",
        "LILAC",
        "BROWN",
        "GOLDEN-BROWN",
        "DARKBROWN",
        "CHOCOLATE",
    ]
    # Tint categories are pulled from the json file - shade is hard coded in since it is referenced in code
    inheritance_categories = game.tint_inheritance[f"{game.inheritance_preset}"]["color_categories"]

    color_categories = sprites.cat_tints["tint_categories"]["color_categories"]
    color_weights = sprites.cat_tints["tint_categories"]["color_weights"]
    shade_categories = ["dark", "medium", "light"]
    shade_weights = sprites.cat_tints["tint_categories"]["shade_weights"]
    
    marking_color_categories = sprites.markings_tints["tint_categories"]["color_categories"]
    m_color_weights = sprites.markings_tints["tint_categories"]["color_weights"]
    marking_shade_categories = ["dark", "medium", "light"]
    m_shade_weights = sprites.markings_tints["tint_categories"]["shade_weights"]

    eye_color_categories = sprites.eye_tints["tint_categories"]["color_categories"]
    e_color_weights = sprites.eye_tints["tint_categories"]["color_weights"]
    eye_shade_categories = ["dark", "medium", "light"]
    e_shade_weights = sprites.eye_tints["tint_categories"]["shade_weights"]

    blend_modes = ["add", "multiply", None]

    # Overlay types
    underfur_types = [None, 'strong', 'medium', 'bubble', 'ash']
    overfur_types = [None, 'strong', 'medium', 'smoke', 'bubble', 'overcast', 'ash']

    overfur_weights = [1, 50, 70, 60, 30, 30, 20]
    underfur_weights = [1, 60, 80, 50, 40]

    tortiepatterns = [
        "ONE",
        "TWO",
        "THREE",
        "FOUR",
        "REDTAIL",
        "DELILAH",
        "MINIMALONE",
        "MINIMALTWO",
        "MINIMALTHREE",
        "MINIMALFOUR",
        "HALF",
        "OREO",
        "SWOOP",
        "MOTTLED",
        "SIDEMASK",
        "EYEDOT",
        "BANDANA",
        "PACMAN",
        "STREAMSTRIKE",
        "ORIOLE",
        "CHIMERA",
        "DAUB",
        "EMBER",
        "BLANKET",
        "ROBIN",
        "BRINDLE",
        "PAIGE",
        "ROSETAIL",
        "SAFI",
        "SMUDGED",
        "DAPPLENIGHT",
        "STREAK",
        "MASK",
        "CHEST",
        "ARMTAIL",
        "SMOKE",
        "GRUMPYFACE",
        "BRIE",
        "BELOVED",
        "BODY",
        "SHILOH",
        "FRECKLED",
        "HEARTBEAT",
    ]
    tortiebases = [
        "single",
        "tabby",
        "bengal",
        "marbled",
        "ticked",
        "smoke",
        "rosette",
        "speckled",
        "mackerel",
        "classic",
        "sokoke",
        "agouti",
        "singlestripe",
        "masked",
    ]

    pelt_length = ["short", "medium", "long"]
    eye_colours = [
        "YELLOW",
        "AMBER",
        "HAZEL",
        "PALEGREEN",
        "GREEN",
        "BLUE",
        "DARKBLUE",
        "GREY",
        "CYAN",
        "EMERALD",
        "PALEBLUE",
        "PALEYELLOW",
        "GOLD",
        "HEATHERBLUE",
        "COPPER",
        "SAGE",
        "COBALT",
        "SUNLITICE",
        "GREENYELLOW",
        "BRONZE",
        "SILVER",
        "ORANGE",
    ]
    yellow_eyes = [
        "YELLOW",
        "AMBER",
        "PALEYELLOW",
        "GOLD",
        "COPPER",
        "GREENYELLOW",
        "BRONZE",
        "SILVER",
        "ORANGE",
    ]
    blue_eyes = [
        "BLUE",
        "DARKBLUE",
        "CYAN",
        "PALEBLUE",
        "HEATHERBLUE",
        "COBALT",
        "SUNLITICE",
        "GREY",
    ]
    green_eyes = ["PALEGREEN", "GREEN", "EMERALD", "SAGE", "HAZEL"]

    # bite scars by @wood pank on discord

    # scars from other cats, other animals
    scars1 = [
        "ONE",
        "TWO",
        "THREE",
        "TAILSCAR",
        "SNOUT",
        "CHEEK",
        "SIDE",
        "THROAT",
        "TAILBASE",
        "BELLY",
        "LEGBITE",
        "NECKBITE",
        "FACE",
        "MANLEG",
        "BRIGHTHEART",
        "MANTAIL",
        "BRIDGE",
        "RIGHTBLIND",
        "LEFTBLIND",
        "BOTHBLIND",
        "BEAKCHEEK",
        "BEAKLOWER",
        "CATBITE",
        "RATBITE",
        "QUILLCHUNK",
        "QUILLSCRATCH",
        "HINDLEG",
        "BACK",
        "QUILLSIDE",
        "SCRATCHSIDE",
        "BEAKSIDE",
        "CATBITETWO",
        "FOUR",
    ]

    # missing parts
    scars2 = [
        "LEFTEAR",
        "RIGHTEAR",
        "NOTAIL",
        "HALFTAIL",
        "NOPAW",
        "NOLEFTEAR",
        "NORIGHTEAR",
        "NOEAR",
    ]

    # "special" scars that could only happen in a special event
    scars3 = [
        "SNAKE",
        "TOETRAP",
        "BURNPAWS",
        "BURNTAIL",
        "BURNBELLY",
        "BURNRUMP",
        "FROSTFACE",
        "FROSTTAIL",
        "FROSTMITT",
        "FROSTSOCK",
        "TOE",
        "SNAKETWO",
    ]

    # make sure to add plural and singular forms of new accs to acc_display.json so that they will display nicely
    # plant_accessories = ["MAPLE LEAF", "HOLLY", "BLUE BERRIES", "FORGET ME NOTS", "RYE STALK", "LAUREL",
    #                    "BLUEBELLS", "NETTLE", "POPPY", "LAVENDER", "HERBS", #"PETALS", "DRY HERBS",
    #                    "OAK LEAVES", "CATMINT", "MAPLE SEED", "JUNIPER"
    #                    ]
    #wild_accessories = ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS", "MOTH WINGS", "CICADA WINGS"]
    #tail_accessories = ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]
    collars = [
        "CRIMSON",
        "BLUE",
        "YELLOW",
        "CYAN",
        "RED",
        "LIME",
        "GREEN",
        "RAINBOW",
        "BLACK",
        "SPIKES",
        "WHITE",
        "PINK",
        "PURPLE",
        "MULTI",
        "INDIGO",
        "CRIMSONBELL",
        "BLUEBELL",
        "YELLOWBELL",
        "CYANBELL",
        "REDBELL",
        "LIMEBELL",
        "GREENBELL",
        "RAINBOWBELL",
        "BLACKBELL",
        "SPIKESBELL",
        "WHITEBELL",
        "PINKBELL",
        "PURPLEBELL",
        "MULTIBELL",
        "INDIGOBELL",
        "CRIMSONBOW",
        "BLUEBOW",
        "YELLOWBOW",
        "CYANBOW",
        "REDBOW",
        "LIMEBOW",
        "GREENBOW",
        "RAINBOWBOW",
        "BLACKBOW",
        "SPIKESBOW",
        "WHITEBOW",
        "PINKBOW",
        "PURPLEBOW",
        "MULTIBOW",
        "INDIGOBOW",
        "CRIMSONNYLON",
        "BLUENYLON",
        "YELLOWNYLON",
        "CYANNYLON",
        "REDNYLON",
        "LIMENYLON",
        "GREENNYLON",
        "RAINBOWNYLON",
        "BLACKNYLON",
        "SPIKESNYLON",
        "WHITENYLON",
        "PINKNYLON",
        "PURPLENYLON",
        "MULTINYLON",
        "INDIGONYLON",
    ]

    head_accessories = [
        "MOTH WINGS",
        "ROSY MOTH WINGS",
        "MORPHO BUTTERFLY",
        "MONARCH BUTTERFLY",
        "CICADA WINGS",
        "BLACK CICADA",
        "MAPLE LEAF",
        "HOLLY",
        "BLUE BERRIES",
        "FORGET ME NOTS",
        "RYE STALK",
        "CATTAIL",
        "POPPY",
        "ORANGE POPPY",
        "CYAN POPPY",
        "WHITE POPPY",
        "PINK POPPY",
        "BLUEBELLS",
        "LILY OF THE VALLEY",
        "SNAPDRAGON",
        "NETTLE",
        "HEATHER",
        "GORSE",
        "JUNIPER",
        "RASPBERRY",
        "LAVENDER",
        "OAK LEAVES",
        "CATMINT",
        "MAPLE SEED",
        "LAUREL",
        "BULB WHITE",
        "BULB YELLOW",
        "BULB ORANGE",
        "BULB PINK",
        "BULB BLUE",
        "DRY CATMINT",
        "DRY NETTLES",
        "DRY LAURELS",
        "ROSE MALLOW",
        "PICKLEWEED",
    ]

    body_accessories = [
        "HERBS",
        "PETALS",
        "DRY HERBS",
    ]

    # ACCESSORIES
    accessory_types = ["twoleg", "wild"]
    accessories = ["bow", "collar", "bell", "nylon"]
    accessory_patterns = {
        "bow": ["dots", "stripes", "gradient1", "gradient2", "gradient3", "gradient4"],
        "collar": False,
        "bell": False,
        "nylon": False,
        "berries": False,
        "petals": False,
        "catmint": False,
        "laurel": False,
        "nettle": False,
        "poppy": False,
        "flowers": False,
        "earleaves": False,
        "maple": False,
        "lavender": False,
        "bluebells": False,
        "leaves": False,
        "berries2": False,
        "seed": False,
        "stalk": False,
        "feathers": False,
        "moth": False,
        "largemoth": False,
        "cicada": False
    }

    twoleg_accessories = ["bow", "collar", "bell", "nylon"]
    wild_accessories = ["feathers", "moth", "cicada", "largemoth"]
    herb_accessories = ["leaves", "berries", "catmint", "laurel", "nettle", "poppy", "flowers", "earleaves", "maple", "lavender", "bluebells", "berries2", "seed", "stalk"]
    tail_accessories = ["feathers"]

    accessory_categories = {
        "leaf": ["catmint", "leaves", "laurel", "nettle", "maple", "earleaves"],
        "flower": ["bluebells", "lavender"],
        "flower_nl": ["poppy", "flowers", "petals"],
        "berry": ["berries", "berries2"],
        "seed": ["seed"],
        "stalk": ["stalk"],
        "cicada": ["cicada"],
        "moth": ["moth", "largemoth"],
        "feathers": ["feathers"],
        "twoleg": ["bow", "collar", "bell", "nylon"]
    }

    tabbies = ["Tabby", "Ticked", "Mackerel", "Classic", "Sokoke", "Agouti", "Wisp"]
    spotted = ["Speckled", "Rosette"]
    plain = [None, "Smoke", "Singlestripe"]
    exotic = ["Bengal", "Marbled", "Masked"]
    torties = ["Tortie", "Calico"]
    pelt_categories = [tabbies, spotted, plain, exotic, torties]
    marking_weights = [40, 30, 40, 5, 0]

    # SPRITE NAMES
    single_colours = [
        "WHITE",
        "PALEGREY",
        "SILVER",
        "GREY",
        "DARKGREY",
        "GHOST",
        "BLACK",
        "CREAM",
        "PALEGINGER",
        "GOLDEN",
        "GINGER",
        "DARKGINGER",
        "SIENNA",
        "LIGHTBROWN",
        "LILAC",
        "BROWN",
        "GOLDEN-BROWN",
        "DARKBROWN",
        "CHOCOLATE",
    ]
    ginger_colours = ["CREAM", "PALEGINGER", "GOLDEN", "GINGER", "DARKGINGER", "SIENNA"]
    black_colours = ["GREY", "DARKGREY", "GHOST", "BLACK"]
    white_colours = ["WHITE", "PALEGREY", "SILVER"]
    brown_colours = [
        "LIGHTBROWN",
        "LILAC",
        "BROWN",
        "GOLDEN-BROWN",
        "DARKBROWN",
        "CHOCOLATE",
    ]
    ginger_colours = ['CREAM', 'PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'SIENNA']
    black_colours = ['GREY', 'DARKGREY', 'GHOST', 'BLACK']
    white_colours = ['WHITE', 'PALEGREY', 'SILVER']
    brown_colours = ['LIGHTBROWN', 'LILAC', 'BROWN', 'GOLDEN-BROWN', 'DARKBROWN', 'CHOCOLATE']
    # color_categories = [ginger_colours, black_colours, white_colours, brown_colours]

    eye_sprites = [
        "YELLOW",
        "AMBER",
        "HAZEL",
        "PALEGREEN",
        "GREEN",
        "BLUE",
        "DARKBLUE",
        "BLUEYELLOW",
        "BLUEGREEN",
        "GREY",
        "CYAN",
        "EMERALD",
        "PALEBLUE",
        "PALEYELLOW",
        "GOLD",
        "HEATHERBLUE",
        "COPPER",
        "SAGE",
        "COBALT",
        "SUNLITICE",
        "GREENYELLOW",
        "BRONZE",
        "SILVER",
        "ORANGE",
    ]
    little_white = [
        "LITTLE",
        "LIGHTTUXEDO",
        "BUZZARDFANG",
        "TIP",
        "BLAZE",
        "BIB",
        "VEE",
        "PAWS",
        "BELLY",
        "TAILTIP",
        "TOES",
        "BROKENBLAZE",
        "LILTWO",
        "SCOURGE",
        "TOESTAIL",
        "RAVENPAW",
        "HONEY",
        "LUNA",
        "EXTRA",
        "MUSTACHE",
        "REVERSEHEART",
        "SPARKLE",
        "RIGHTEAR",
        "LEFTEAR",
        "ESTRELLA",
        "REVERSEEYE",
        "BACKSPOT",
        "EYEBAGS",
        "LOCKET",
        "BLAZEMASK",
        "TEARS",
    ]
    mid_white = [
        "TUXEDO",
        "FANCY",
        "UNDERS",
        "DAMIEN",
        "SKUNK",
        "MITAINE",
        "SQUEAKS",
        "STAR",
        "WINGS",
        "DIVA",
        "SAVANNAH",
        "FADESPOTS",
        "BEARD",
        "DAPPLEPAW",
        "TOPCOVER",
        "WOODPECKER",
        "MISS",
        "BOWTIE",
        "VEST",
        "FADEBELLY",
        "DIGIT",
        "FCTWO",
        "FCONE",
        "MIA",
        "ROSINA",
        "PRINCESS",
        "DOUGIE",
    ]
    high_white = [
        "ANY",
        "ANYTWO",
        "BROKEN",
        "FRECKLES",
        "RINGTAIL",
        "HALFFACE",
        "PANTSTWO",
        "GOATEE",
        "PRINCE",
        "FAROFA",
        "MISTER",
        "PANTS",
        "REVERSEPANTS",
        "HALFWHITE",
        "APPALOOSA",
        "PIEBALD",
        "CURVED",
        "GLASS",
        "MASKMANTLE",
        "MAO",
        "PAINTED",
        "SHIBAINU",
        "OWL",
        "BUB",
        "SPARROW",
        "TRIXIE",
        "SAMMY",
        "FRONT",
        "BLOSSOMSTEP",
        "BULLSEYE",
        "FINN",
        "SCAR",
        "BUSTER",
        "HAWKBLAZE",
        "CAKE",
    ]
    mostly_white = [
        "VAN",
        "ONEEAR",
        "LIGHTSONG",
        "TAIL",
        "HEART",
        "MOORISH",
        "APRON",
        "CAPSADDLE",
        "CHESTSPECK",
        "BLACKSTAR",
        "PETAL",
        "HEARTTWO",
        "PEBBLESHINE",
        "BOOTS",
        "COW",
        "COWTWO",
        "LOVEBUG",
        "SHOOTINGSTAR",
        "EYESPOT",
        "PEBBLE",
        "TAILTWO",
        "BUDDY",
        "KROPKA",
    ]
    point_markings = ["COLOURPOINT", "RAGDOLL", "SEPIAPOINT", "MINKPOINT", "SEALPOINT"]
    vit = [
        "VITILIGO",
        "VITILIGOTWO",
        "MOON",
        "PHANTOM",
        "KARPATI",
        "POWDER",
        "BLEACHED",
        "SMOKEY",
    ]
    white_sprites = [
        little_white,
        mid_white,
        high_white,
        mostly_white,
        point_markings,
        vit,
        "FULLWHITE",
    ]

    skin_sprites = [
        "BLACK",
        "PINK",
        "DARKBROWN",
        "BROWN",
        "LIGHTBROWN",
        "DARK",
        "DARKGREY",
        "GREY",
        "DARKSALMON",
        "SALMON",
        "PEACH",
        "DARKMARBLED",
        "MARBLED",
        "LIGHTMARBLED",
        "DARKBLUE",
        "BLUE",
        "LIGHTBLUE",
        "RED",
    ]

    """Holds all appearence information for a cat. """
    def __init__(self,
                 name:str="white",
                 length:str="short",
                 white_patches:str=None,
                 eye_color:str=None,
                 eye_shade:str=None,
                 eye_tint:str=None,
                 eye_s_color:str=None,
                 eye_s_shade:str=None,
                 eye_s_tint:str=None,
                 eye_p_color:str=None,
                 eye_p_shade:str=None,
                 eye_p_tint:str=None,
                 eye2_color:str=None,
                 eye2_shade:str=None,
                 eye2_tint:str=None,
                 eye2_s_color:str=None,
                 eye2_s_shade:str=None,
                 eye2_s_tint:str=None,
                 eye2_p_color:str=None,
                 eye2_p_shade:str=None,
                 eye2_p_tint:str=None,
                 tint:str=None,
                 tint_color:str=None,
                 tint_shade:str=None,
                 underfur:str=None,
                 underfur_tint:str=None,
                 overfur:str=None,
                 overfur_tint:str=None,
                 marking:str=None,
                 marking_shade:str=None,
                 marking_color:str=None,
                 marking_tint:str=None,
                 marking_blend:str=None,
                 pattern:str=None,
                 tortie_color:str=None,
                 tortie_shade:str=None,
                 tortie_tint:str=None,
                 tortiepattern:str=None,
                 tortie_marking_shade:str=None,
                 tortie_marking_color:str=None,
                 tortie_marking_tint:str=None,
                 tortie_underfur_tint:str=None,
                 tortie_overfur_tint:str=None,
                 vitiligo:str=None,
                 points:str=None,
                 accessory_category:str=None,
                 accessory_type:str=None,
                 accessory_color:str=None,
                 accessory_shade:str=None,
                 acc_accent_color:str=None,
                 accessory_pattern:list=None,
                 accessory_p_color:list=None,
                 accessory_p_shade:list=None,
                 paralyzed:bool=False,
                 opacity:int=100,
                 scars:list=None,
                 skin:str="BLACK",
                 white_patches_tint:str="none",
                 kitten_sprite:int=None,
                 adol_sprite:int=None,
                 adult_sprite:int=None,
                 senior_sprite:int=None,
                 para_adult_sprite:int=None,
                 reverse:bool=False,
                 ) -> None:
        self.name = name
        self.length = length
        self.white_patches = white_patches
        self.eye_color = eye_color
        self.eye_shade = eye_shade
        self.eye_tint = eye_tint
        self.eye_s_color = eye_s_color
        self.eye_s_shade = eye_s_shade
        self.eye_s_tint = eye_s_tint
        self.eye_p_color = eye_p_color
        self.eye_p_shade = eye_p_shade
        self.eye_p_tint = eye_p_tint
        self.eye2_color = eye2_color
        self.eye2_shade = eye2_shade
        self.eye2_tint = eye2_tint
        self.eye2_s_color = eye2_s_color
        self.eye2_s_shade = eye2_s_shade
        self.eye2_s_tint = eye2_s_tint
        self.eye2_p_color = eye2_p_color
        self.eye2_p_shade = eye2_p_shade
        self.eye2_p_tint = eye2_p_tint
        self.tint = tint
        self.tint_shade = tint_shade
        self.tint_color = tint_color
        self.underfur = underfur
        self.underfur_tint = underfur_tint
        self.overfur = overfur
        self.overfur_tint = overfur_tint
        self.marking = marking
        self.marking_shade = marking_shade
        self.marking_color = marking_color
        self.marking_tint = marking_tint
        self.marking_blend = marking_blend
        self.pattern = pattern
        self.tortie_shade = tortie_shade
        self.tortie_color = tortie_color
        self.tortie_tint = tortie_tint
        self.tortiepattern = tortiepattern
        self.tortie_marking_shade = tortie_marking_shade
        self.tortie_marking_color = tortie_marking_color
        self.tortie_marking_tint = tortie_marking_tint
        self.tortie_underfur_tint = tortie_underfur_tint
        self.tortie_overfur_tint = tortie_overfur_tint
        self.vitiligo = vitiligo
        self.length = length
        self.points = points
        # like if you cry everytime
        self.accessory_category = accessory_category
        self.accessory_type = accessory_type
        self.accessory_color = accessory_color
        self.accessory_shade = accessory_shade

        self.acc_accent_color = acc_accent_color

        self.accessory_pattern = accessory_pattern if isinstance(accessory_pattern, list) else []
        self.accessory_p_color = accessory_p_color if isinstance(accessory_p_color, list) else []
        self.accessory_p_shade = accessory_p_shade if isinstance(accessory_p_shade, list) else []

        self.paralyzed = paralyzed
        self.opacity = opacity
        self.scars = scars if isinstance(scars, list) else []
        self.white_patches_tint = white_patches_tint
        self.cat_sprites = {
            "kitten": kitten_sprite if kitten_sprite is not None else 0,
            "adolescent": adol_sprite if adol_sprite is not None else 0,
            "young adult": adult_sprite if adult_sprite is not None else 0,
            "adult": adult_sprite if adult_sprite is not None else 0,
            "senior adult": adult_sprite if adult_sprite is not None else 0,
            "senior": senior_sprite if senior_sprite is not None else 0,
            "para_adult": para_adult_sprite if para_adult_sprite is not None else 0,
            "newborn": 20,
            "para_young": 17,
            "sick_adult": 18,
            "sick_young": 19,
        }

        self.reverse = reverse
        self.skin = skin

    @staticmethod
    def generate_new_pelt(gender:str, parents:tuple=(), age:str="adult", missing_parent:dict=()):
        new_pelt = Pelt()
        
        pelt_white = new_pelt.init_pattern_color(parents, gender, missing_parent)
        new_pelt.init_white_patches(pelt_white, parents)
        new_pelt.init_sprite()
        new_pelt.init_scars(age)
        new_pelt.init_accessories(age)
        new_pelt.init_eyes(parents, missing_parent)
        new_pelt.init_tint()
        new_pelt.init_pattern()
        
        return new_pelt

    def check_and_convert(self, convert_dict):
        """Checks for old-type properties for the apperence-related properties
        that are stored in Pelt, and converts them. To be run when loading a cat in. """

        # Converts accessory to the new system :)
        # Also check for if accessory color and shade needs regenerated :> 
        if self.accessory_color == 0 and self.accessory_type:
            print("Converting accessory.")
            if self.accessory_type in ["BLUEBOW", "YELLOWBOW", "CYANBOW", "REDBOW", "LIMEBOW", "GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW", "WHITEBOW", "PINKBOW"]:
                self.accessory_type = "bow"
                self.accessory_category = "twoleg"
            if self.accessory_type in ["CRIMSON", "BLUE", "YELLOW", "CYAN", "RED", "LIME", "GREEN", "RAINBOW", "BLACK", "SPIKES", "WHITE", "PINK", "PURPLE", "MULTI", "INDIGO"]:
                self.accessory_type = "collar"
                self.accessory_category = "twoleg"
            if self.accessory_type in ["CRIMSONBELL", "BLUEBELL", "YELLOWBELL", "CYANBELL", "REDBELL", "LIMEBELL", "GREENBELL", "RAINBOWBELL", "BLACKBELL", "SPIKESBELL", "WHITEBELL", "PINKBELL", "PURPLEBELL"]:
                self.accessory_type = "bell"
                self.accessory_category = "twoleg"
            if self.accessory_type in ["CRIMSONNYLON", "BLUENYLON", "YELLOWNYLON", "CYANNYLON", "REDNYLON", "LIMENYLON", "GREENNYLON", "RAINBOWNYLON", "BLACKNYLON", "SPIKESNYLON", "WHITENYLON", "PINKNYLON", "PURPLENYLON", "MULTINYLON","INDIGONYLON"]:
                self.accessory_type = "nylon"
                self.accessory_category = "twoleg"
            if self.accessory_type in ["HOLLY", "BLUE BERRIES"]:
                self.accessory_type = "berries"
                self.accessory_category = "berry"
            if self.accessory_type == "FORGET ME NOTS":
                self.accessory_type = "flowers"
                self.accessory_category = "flower_nl"
            if self.accessory_type == "POPPY":
                self.accessory_type = "poppy"
                self.accessory_category = "flower_nl"
            if self.accessory_type == "LAVENDER":
                self.accessory_type = "lavender"
                self.accessory_category = "flower"
            if self.accessory_type == "BLUEBELLS":
                self.accessory_type = "bluebells"
                self.accessory_category = "flower"
            if self.accessory_type == "PETALS":
                self.accessory_type = "leaves"
                self.accessory_category = "flower"
            if self.accessory_type == "OAK LEAVES":
                self.accessory_type = "earleaves"
                self.accessory_category = "leaf"
            if self.accessory_type == "MAPLE LEAF":
                self.accessory_type = "maple"
                self.accessory_category = "leaf"
            if self.accessory_type == "RYE STALK":
                self.accessory_type = "stalk"
                self.accessory_category = "stalk"
            if self.accessory_type == "MAPLE SEED":
                self.accessory_type = "seed"
                self.accessory_category = "seed"
            if self.accessory_type == "JUNIPER":
                self.accessory_type = "berries2"
                self.accessory_category = "berry"
            if self.accessory_type == "CATMINT":
                self.accessory_type = "catmint"
                self.accessory_category = "leaf"
            if self.accessory_type == "NETTLE":
                self.accessory_type = "nettle"
                self.accessory_category = "leaf"
            if self.accessory_type == "LAUREL":
                self.accessory_type = "laurel"
                self.accessory_category = "leaf"
            if self.accessory_type in ["HERBS", "DRY HERBS"]:
                self.accessory_type = "leaves"
                self.accessory_category = "leaf"

            possible_colors = sprites.accessory_tints["possible_tints"][f"{self.accessory_category}"].copy()
            self.accessory_color = choice(possible_colors)

            if self.accessory_color in sprites.accessory_tints["possible_tints"][f"warm_{self.accessory_category}"]:
                possible_colors = sprites.accessory_tints["possible_tints"][f"warm_{self.accessory_category}"].copy()
                self.accessory_shade = choice(possible_colors)
            elif self.accessory_color in sprites.accessory_tints["possible_tints"][f"cool_{self.accessory_category}"]:
                possible_colors = sprites.accessory_tints["possible_tints"][f"cool_{self.accessory_category}"].copy()
                self.accessory_shade = choice(possible_colors)
            else:
                possible_colors = sprites.accessory_tints["possible_tints"][f"monochrome_{self.accessory_category}"].copy()
                self.accessory_shade = choice(possible_colors)

            pattern_list = Pelt.accessory_patterns[f"{self.accessory_type}"].copy()
            pattern_count = random.randint(0, len(Pelt.accessory_patterns[f"{self.accessory_type}"]))
            i = 1
            while i <= pattern_count:
                pattern_choice = choice(pattern_list)
                pattern_list.remove(pattern_choice) # remove from pattern list to ensure no duplicates

                p_color = choice(possible_colors)

                self.accessory_pattern.append(pattern_choice)
                self.accessory_p_color.append(p_color)

                if self.accessory_p_color in sprites.accessory_tints["possible_tints"][f"warm_{self.accessory_category}"]:
                    possible_colors = sprites.accessory_tints["possible_tints"][f"warm_{self.accessory_category}"].copy()
                    self.accessory_p_shade.append(choice(possible_colors))
                elif self.accessory_p_color in sprites.accessory_tints["possible_tints"][f"cool_{self.accessory_category}"]:
                    possible_colors = sprites.accessory_tints["possible_tints"][f"cool_{self.accessory_category}"].copy()
                    self.accessory_p_shade.append(choice(possible_colors))
                else:
                    possible_colors = sprites.accessory_tints["possible_tints"][f"monochrome_{self.accessory_category}"].copy()
                    self.accessory_p_shade.append(choice(possible_colors))

                i += 1

        if self.acc_accent_color == 0 and self.accessory_type:
            # accent color
            possible_colors = sprites.accessory_tints["possible_tints"][f"{self.accessory_category}_accent"].copy()
            self.acc_accent_color = choice(possible_colors)


        #First, convert from some old names that may be in white_patches. 
        if self.white_patches == 'POINTMARK':
            self.white_patches = "SEALPOINT"
        elif self.white_patches == "PANTS2":
            self.white_patches = "PANTSTWO"
        elif self.white_patches == "ANY2":
            self.white_patches = "ANYTWO"
        elif self.white_patches == "VITILIGO2":
            self.white_patches = "VITILIGOTWO"

        if self.vitiligo == "VITILIGO2":
            self.vitiligo = "VITILIGOTWO"
        
        
        # Move white_patches that should be in vit or points. 
        if self.white_patches in Pelt.vit:
            self.vitiligo = self.white_patches
            self.white_patches = None
        elif self.white_patches in Pelt.point_markings:
            self.points = self.white_patches
            self.white_patches = None

        if self.tortiepattern and "tortie" in self.tortiepattern:
            self.tortiepattern = sub("tortie", "", self.tortiepattern.lower())
            if self.tortiepattern == "solid":
                self.tortiepattern = "single"

        if self.white_patches in convert_dict["old_creamy_patches"]:
            self.white_patches = convert_dict["old_creamy_patches"][self.white_patches]
            self.white_patches_tint = "darkcream"
        elif self.white_patches in ("SEPIAPOINT", "MINKPOINT", "SEALPOINT"):
            self.white_patches_tint = "none"
        
        if self.length == 'long':
            if self.cat_sprites['adult'] not in [9, 10, 11]:
                if self.cat_sprites['adult'] == 0:
                    self.cat_sprites['adult'] = 9
                elif self.cat_sprites['adult'] == 1:
                    self.cat_sprites['adult'] = 10
                elif self.cat_sprites['adult'] == 2:
                    self.cat_sprites['adult'] = 11
                self.cat_sprites['young adult'] = self.cat_sprites['adult']
                self.cat_sprites['senior adult'] = self.cat_sprites['adult']
                self.cat_sprites['para_adult'] = 16
        else:
            self.cat_sprites['para_adult'] = 15
        if self.cat_sprites['senior'] not in [12, 13, 14]:
            if self.cat_sprites['senior'] == 3:
                self.cat_sprites['senior'] = 12
            elif self.cat_sprites['senior'] == 4:
                self.cat_sprites['senior'] = 13
            elif self.cat_sprites['senior'] == 5:
                self.cat_sprites['senior'] = 14
        if self.pattern in convert_dict["old_tortie_patches"]:
            old_pattern = self.pattern
            self.pattern = convert_dict["old_tortie_patches"][old_pattern][1]

            # If the pattern is old, there is also a chance the base color is stored in
            # tortiecolour. That may be different from the pelt color ("main" for torties)
            # generated before the "ginger-on-ginger" update. If it was generated after that update,
            # tortiecolour and pelt_colour will be the same. Therefore, lets also re-set the pelt color
            self.tint_color = self.tortiecolour
            self.tortiecolour = convert_dict["old_tortie_patches"][old_pattern][0]

        if self.pattern == "MINIMAL1":
            self.pattern = "MINIMALONE"
        elif self.pattern == "MINIMAL2":
            self.pattern = "MINIMALTWO"
        elif self.pattern == "MINIMAL3":
            self.pattern = "MINIMALTHREE"
        elif self.pattern == "MINIMAL4":
            self.pattern = "MINIMALFOUR"
        
    def init_eyes(self, parents, missing_parent):
        if not parents:
            self.eye_color = choice(Pelt.eye_color_categories)
            if sprites.eye_random:
                self.eye_s_color = choice(Pelt.eye_color_categories)
                self.eye_p_color = choice(Pelt.eye_color_categories)
            else:
                self.eye_s_color = self.eye_color
                self.eye_p_color = self.eye_color
        else:
            if missing_parent:
                
                self.eye_color = choice([i.pelt.eye_color for i in parents] + [missing_parent["eye_color"]] + [choice(Pelt.eye_color_categories)])

                if sprites.eye_random:
                    self.eye_s_color = choice([i.pelt.eye_s_color for i in parents] + [missing_parent["eye_s_color"]] + [choice(Pelt.eye_color_categories)])
                    self.eye_p_color = choice([i.pelt.eye_p_color for i in parents] + [missing_parent["eye_p_color"]] + [choice(Pelt.eye_color_categories)])
                else:
                    self.eye_s_color = self.eye_color
                    self.eye_p_color = self.eye_color
            else:
                self.eye_color = choice([i.pelt.eye_color for i in parents] + [choice(Pelt.eye_color_categories)])

                if sprites.eye_random:
                    self.eye_s_color = choice([i.pelt.eye_color for i in parents] + [choice(Pelt.eye_color_categories)])
                    self.eye_p_color = choice([i.pelt.eye_color for i in parents] + [choice(Pelt.eye_color_categories)])
                else:
                    self.eye_s_color = self.eye_color
                    self.eye_p_color = self.eye_color

        self.eye_shade = random.choices(Pelt.eye_shade_categories, weights=(sprites.eye_tints["tint_categories"]["shade_weights"]), k=1)[0]

        if self.eye_shade == "dark":
            weights = [100, 10, 0]
            self.eye_s_shade = random.choices(Pelt.eye_shade_categories, weights=weights, k=1)[0]
            weights = [1, 0, 0]
            self.eye_p_shade = random.choices(Pelt.eye_shade_categories, weights=weights, k=1)[0]
        elif self.eye_shade == "medium":
            weights = [50, 50, 0]
            self.eye_s_shade = random.choices(Pelt.eye_shade_categories, weights=weights, k=1)[0]
            weights = [1, 0, 0]
            self.eye_p_shade = random.choices(Pelt.eye_shade_categories, weights=weights, k=1)[0]
        else:
            weights = [30, 50, 20]
            self.eye_s_shade = random.choices(Pelt.eye_shade_categories, weights=weights, k=1)[0]
            weights = [1, 0, 0]
            self.eye_p_shade = random.choices(Pelt.eye_shade_categories, weights=weights, k=1)[0]

        # 
        #self.tint_color = random.choices(Pelt.color_categories, weights=(sprites.cat_tints["tint_categories"]["color_weights"]), k=1)[0]
        #self.tint_shade = random.choices(Pelt.shade_categories, weights=(sprites.cat_tints["tint_categories"]["shade_weights"]), k=1)[0]

        #White patches must be initalized before eye color. 
        num = game.config["cat_generation"]["base_heterochromia"]
        if self.white_patches in [Pelt.high_white, Pelt.mostly_white, 'FULLWHITE']:
            num = num - 90
        if self.white_patches == 'FULLWHITE':
            num -= 10
        for _par in parents:
            if _par.pelt.eye2_color:
                num -= 10

        if num < 0:
            num = 1
            
        if not random.randint(0, num):
            eye_options = Pelt.eye_color_categories.copy()
            eye_options.remove(self.eye_color)

            self.eye2_color = random.choices(eye_options, k=1)[0]
            self.eye2_shade = random.choices(Pelt.eye_shade_categories, weights=(sprites.eye_tints["tint_categories"]["shade_weights"]), k=1)[0]

            if sprites.eye_random:
                self.eye2_p_color = choice(eye_options)
                self.eye2_s_color = choice(eye_options)
            else:
                self.eye2_s_color = self.eye2_color
                self.eye2_p_color = self.eye2_color
            
            
            if self.eye2_shade == "dark":
                weights = [100, 10, 0]
                self.eye2_s_shade = random.choices(Pelt.eye_shade_categories, weights=weights, k=1)[0]
                weights = [1, 0, 0]
                self.eye2_p_shade = random.choices(Pelt.eye_shade_categories, weights=weights, k=1)[0]
            elif self.eye2_shade == "medium":
                weights = [50, 50, 0]
                self.eye2_s_shade = random.choices(Pelt.eye_shade_categories, weights=weights, k=1)[0]
                weights = [1, 0, 0]
                self.eye2_p_shade = random.choices(Pelt.eye_shade_categories, weights=weights, k=1)[0]
            else:
                weights = [30, 50, 20]
                self.eye2_s_shade = random.choices(Pelt.eye_shade_categories, weights=weights, k=1)[0]
                weights = [1, 0, 0]
                self.eye2_p_shade = random.choices(Pelt.eye_shade_categories, weights=weights, k=1)[0]


    def pattern_color_inheritance(self, parents: tuple=(), gender="female", missing_parent:dict=()):
        # setting parent pelt categories
        # We are using a set, since we don't need this to be ordered, and sets deal with removing duplicates.
        par_peltlength = set()
        par_peltmarkings = set()
        par_peltcolors = set()
        par_peltshades = set()
        par_markcolors = set()
        par_markshades = set()
        par_peltcategories = set()
        combo_peltcolors = list()
        combo_markcolors = list()
        par_pelts = []
        par_white = []
        
        for p in parents:
            if p:
                # Gather pelt markings
                par_peltmarkings.add(p.pelt.marking)

                # Gather pelt length
                par_peltlength.add(p.pelt.length)

                # Gather pelt tints
                par_peltcolors.add(p.pelt.tint_color)
                par_peltshades.add(p.pelt.tint_shade)

                # Gather tortie tints
                if p.pelt.name in Pelt.torties:
                    par_peltcolors.add(p.pelt.tortie_color)
                    par_peltshades.add(p.pelt.tortie_shade)

                combo_peltcolors.append(p.pelt.tint_color)
                combo_markcolors.append(p.pelt.marking_color)

                par_markcolors.add(p.pelt.marking_color)
                par_markshades.add(p.pelt.marking_shade)
                
                # Gather if they have white in their pelt.
                par_white.append(p.pelt.white)
            else:
                # If order for white patches to work correctly, we also want to randomly generate a "pelt_white"
                # for each "None" parent (missing or unknown parent)
                par_white.append(bool(random.getrandbits(1)))

                # Append None
                # Gather pelt color.
                par_peltlength.add(None)
                par_markcolors.add(None)
                par_markshades.add(None)
                par_peltcolors.add(None)
                par_peltlength.add(None)
                par_peltshades.add(None)

        # If this list is empty, something went wrong.
        if not par_peltcolors:
            print("Warning - no parents: pelt randomized")
            return self.randomize_pattern_color(gender)
        
        # check for missing parent to generate missing parent
        if missing_parent:
            # Gather pelt markings
            par_peltmarkings.add(str(missing_parent['marking']))

            # Gather pelt length
            par_peltlength.add(str(missing_parent["length"]))

            # Gather pelt tints
            par_peltcolors.add(str(missing_parent["tint_color"]))
            par_peltshades.add(str(missing_parent["tint_shade"]))

            combo_peltcolors.append(str(missing_parent["tint_color"]))
            combo_markcolors.append(str(missing_parent["marking_color"]))

            par_markcolors.add(str(missing_parent["marking_color"]))
            par_markshades.add(str(missing_parent["marking_shade"]))
            
            # Gather if they have white in their pelt.
            par_white.append(str(missing_parent["white"]))


        if game.config_inheritance == "true":
            if game.inheritance_type == "color_categories":

                for p_ in par_peltcolors:
                    for c in Pelt.inheritance_categories:
                        cat_sel = Pelt.inheritance_categories[f"{c}"]
                        category = set(game.tint_inheritance[f"{game.inheritance_preset}"]["color_categories"][f"{cat_sel}"])
                        if p_ in category:
                            par_peltcategories.update(category)

                par_peltcolors.update(par_peltcategories)
                par_peltcategories.clear
                
                for p_ in par_markcolors:
                    for c in Pelt.inheritance_categories:
                        cat_sel = Pelt.inheritance_categories[f"{c}"]
                        category = set(game.tint_inheritance[f"{game.inheritance_preset}"]["color_categories"][f"{cat_sel}"])
                        if p_ in category:
                            par_peltcategories.update(category)

                par_markcolors.update(par_peltcategories)

            elif game.inheritance_type == "color_lists":
                colors = set()
                for p_ in par_peltcolors:
                    colors.update(set(game.tint_inheritance[f"{game.inheritance_preset}"]["color_lists"][f"{p_}"]))

                par_peltcolors.update(colors)
                colors.clear
                
                for p_ in par_markcolors:
                    colors.update(set(game.tint_inheritance[f"{game.inheritance_preset}"]["color_lists"][f"{p_}"]))

                par_markcolors.update(colors)

            elif game.inheritance_type == "color_combos":
                c_colors = combo_peltcolors
                p1_color = c_colors[0]
                p2_color = c_colors[1]
                pelt_weights = game.tint_inheritance[f"{game.inheritance_preset}"]["color_combos"][f"{p1_color}"][f"{p2_color}"]["weights"]
                pelt_colors = game.tint_inheritance[f"{game.inheritance_preset}"]["color_combos"][f"{p1_color}"][f"{p2_color}"]["outcomes"]

                c_colors = combo_markcolors
                p1_color = c_colors[0]
                p2_color = c_colors[1]
                mark_weights = game.tint_inheritance[f"{game.inheritance_preset}"]["color_combos"][f"{p1_color}"][f"{p2_color}"]["weights"]
                mark_colors = game.tint_inheritance[f"{game.inheritance_preset}"]["color_combos"][f"{p1_color}"][f"{p2_color}"]["outcomes"]
            else:
                print("Incorrect inheritance type inputted.")
                

        # ------------------------------------------------------------------------------------------------------------#
        #   PELT COLOUR
        # ------------------------------------------------------------------------------------------------------------#
        # Shade weights [dark, medium, light]
        weights = [0, 0, 0]
        for p_ in par_peltshades:
            if p_ == "dark":
                add_weight = (40, 10, 0)
            if p_ == "medium":
                add_weight = (40, 10, 0)
            if p_ == "light":
                add_weight = (0, 10, 40)
            elif p_ is None:
                add_weight = (40, 40, 40)
            else:
                add_weight = (0, 0, 0)

            for x in range(0, len(weights)):
                weights[x] += add_weight[x]

            # A quick check to make sure all the weights aren't 0
            if all([x == 0 for x in weights]):
                weights = [1, 1, 1]

        if game.inheritance_type == "color_combos":
            self.tint_color = random.choices(pelt_colors, weights=pelt_weights, k=1)[0]
        else:
            self.tint_color = random.choices(list(par_peltcolors), k=1)[0]

        self.tint_shade = random.choices(Pelt.marking_shade_categories, weights=weights, k=1)[0]
        chosen_pelt = self.tint_color
        
        # ------------------------------------------------------------------------------------------------------------#
        #   MARKINGS
        # ------------------------------------------------------------------------------------------------------------#
        # Select blend
        marking_blend_weights = game.config["cat_generation"]["marking_blend_weights"]
        self.marking_blend = random.choices(Pelt.blend_modes, weights=marking_blend_weights, k=1)[0]

        # Select overlays
        self.overfur = random.choices(Pelt.overfur_types, weights=Pelt.overfur_weights, k=1)[0]
        self.underfur = random.choices(Pelt.underfur_types, weights=Pelt.underfur_weights, k=1)[0]
    
    
        weights = [0, 0, 0]
        for p_ in par_markshades:
            if p_ == "dark":
                add_weight = (40, 10, 0)
            if p_ == "medium":
                add_weight = (40, 10, 0)
            if p_ == "light":
                add_weight = (0, 10, 40)
            elif p_ is None:
                add_weight = (40, 40, 40)
            else:
                add_weight = (0, 0, 0)

        for x in range(0, len(weights)):
            weights[x] += add_weight[x]

        # A quick check to make sure all the weights aren't 0
        if all([x == 0 for x in weights]):
            weights = [1, 1, 1]
        
        # Marking color
        
        if game.inheritance_type == "color_combos" and game.tint_inheritance[f"{game.inheritance_preset}"]["marking_inheritance"] == "true":
            chosen_marking_color = random.choices(mark_colors, weights=mark_weights, k=1)[0]

            if game.tint_pools["use_color_pool"] == "true": 
                chosen_marking_shade = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]
            else:
                chosen_marking_shade = random.choices(Pelt.marking_shade_categories, weights=(sprites.markings_tints["tint_categories"]["shade_weights"]), k=1)[0]

                self.tortie_marking_color = random.choices(Pelt.marking_color_categories, weights=(sprites.markings_tints["tint_categories"]["color_weights"]), k=1)[0]
                self.tortie_marking_shade = random.choices(Pelt.marking_shade_categories, weights=(sprites.markings_tints["tint_categories"]["shade_weights"]), k=1)[0]
            
        elif game.tint_inheritance[f"{game.inheritance_preset}"]["marking_inheritance"] == "true":
            chosen_marking_color = random.choices(par_markcolors, k=1)[0]

            if game.tint_pools["use_color_pool"] == "true": 
                chosen_marking_shade = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]
            else:
                chosen_marking_shade = random.choices(Pelt.marking_shade_categories, weights=(sprites.markings_tints["tint_categories"]["shade_weights"]), k=1)[0]

                self.tortie_marking_color = random.choices(Pelt.marking_color_categories, weights=(sprites.markings_tints["tint_categories"]["color_weights"]), k=1)[0]
                self.tortie_marking_shade = random.choices(Pelt.marking_shade_categories, weights=(sprites.markings_tints["tint_categories"]["shade_weights"]), k=1)[0]
        else:
            if game.tint_pools["use_color_pool"] == "true":
                # Marking color
                possible_colors = game.tint_pools["color_presets"][f"{game.tint_preset}"]["color_pools"]["marking_pool"][f"{self.tint_color}"]
                chosen_marking_color = random.choices(possible_colors, k=1)[0]

                weights = game.tint_pools["color_presets"][f"{game.tint_preset}"]["shade_weights"]["marking_pool"][f"{self.tint_shade}"]

                # Tortie marking is picked in the pattern init
            else:

                # Marking color
                chosen_marking_color = random.choices(Pelt.marking_color_categories, weights=(sprites.markings_tints["tint_categories"]["color_weights"]), k=1)[0]
                chosen_marking_shade = random.choices(Pelt.marking_shade_categories, weights=(sprites.markings_tints["tint_categories"]["shade_weights"]), k=1)[0]

                # Tortie marking color
                self.tortie_marking_color = random.choices(Pelt.marking_color_categories, weights=(sprites.markings_tints["tint_categories"]["color_weights"]), k=1)[0]
                self.tortie_marking_shade = random.choices(Pelt.marking_shade_categories, weights=(sprites.markings_tints["tint_categories"]["shade_weights"]), k=1)[0]

        # Determine pelt.
        weights = [0, 0, 0, 0]  #Weights for each pelt group. It goes: (tabbies, spotted, plain, exotic)
        for p_ in par_peltmarkings:
            if p_ in Pelt.tabbies:
                add_weight = (50, 10, 5, 7)
            elif p_ in Pelt.spotted:
                add_weight = (10, 50, 5, 5)
            elif p_ in Pelt.plain:
                add_weight = (5, 5, 50, 0)
            elif p_ in Pelt.exotic:
                add_weight = (15, 15, 1, 45)
            elif (
                p_ is None
            ):  # If there is at least one unknown parent, a None will be added to the set.
                add_weight = (35, 20, 30, 15)
            else:
                add_weight = (0, 0, 0, 0)

            for x in range(0, len(weights)):
                weights[x] += add_weight[x]

        # A quick check to make sure all the weights aren't 0
        if all([x == 0 for x in weights]):
            weights = [1, 1, 1, 1]

        # Now, choose the pelt category and pelt. The extra 0 is for the tortie pelts,
        chosen_marking = choice(
            random.choices(Pelt.pelt_categories, weights=weights + [0], k = 1)[0]
        )

        # Tortie chance
        tortie_chance_f = game.config["cat_generation"][
            "base_female_tortie"
        ]  # There is a default chance for female tortie
        tortie_chance_m = game.config["cat_generation"]["base_male_tortie"]
        for p_ in par_pelts:
            if p_.name in Pelt.torties:
                tortie_chance_f = int(tortie_chance_f / 2)
                tortie_chance_m = tortie_chance_m - 1
                break

        # Determine tortie:
        if gender == "female":
            torbie = random.getrandbits(tortie_chance_f) == 1
        else:
            torbie = random.getrandbits(tortie_chance_m) == 1

        chosen_tortie_base = None
        if torbie:
            # If it is tortie, the chosen pelt above becomes the base pelt.
            chosen_tortie_base = chosen_pelt
            chosen_tortie_base = chosen_tortie_base.lower()
            chosen_pelt = random.choice(Pelt.torties)

        # ------------------------------------------------------------------------------------------------------------#
        #   PELT LENGTH
        # ------------------------------------------------------------------------------------------------------------#

        weights = [0, 0, 0]  # Weights for each length. It goes (short, medium, long)
        for p_ in par_peltlength:
            if p_ == "short":
                add_weight = (50, 10, 2)
            elif p_ == "medium":
                add_weight = (25, 50, 25)
            elif p_ == "long":
                add_weight = (2, 10, 50)
            elif p_ is None:
                add_weight = (10, 10, 10)
            else:
                add_weight = (0, 0, 0)

            for x in range(0, len(weights)):
                weights[x] += add_weight[x]

        # A quick check to make sure all the weights aren't 0
        if all([x == 0 for x in weights]):
            weights = [1, 1, 1]

        chosen_pelt_length = random.choices(Pelt.pelt_length, weights=weights, k=1)[0]

        # ------------------------------------------------------------------------------------------------------------#
        #   PELT WHITE
        # ------------------------------------------------------------------------------------------------------------#

        # There are 94 percentage points that can be added by
        # parents having white. If we have more than two, this
        # will keep that the same.
        percentage_add_per_parent = int(94 / len(par_white))
        chance = 3
        for p_ in par_white:
            if p_:
                chance += percentage_add_per_parent

        chosen_white = random.randint(1, 100) <= chance

        # Adjustments to pelt chosen based on if the pelt has white in it or not.
        if chosen_pelt == "Calico":
            if not chosen_white:
                chosen_pelt = "Tortie"

        # SET THE PELT
        self.name = chosen_pelt
        self.marking = chosen_marking
        self.marking_color = chosen_marking_color
        self.marking_shade = chosen_marking_shade
        self.length = chosen_pelt_length
        self.tortiebase = (
            chosen_tortie_base  # This will be none if the cat isn't a tortie.
        )
        return chosen_white

    def randomize_pattern_color(self, gender):
        # ------------------------------------------------------------------------------------------------------------#
        #   PELT
        # ------------------------------------------------------------------------------------------------------------#

        # Select blend
        marking_blend_weights = game.config["cat_generation"]["marking_blend_weights"]
        self.marking_blend = random.choices(Pelt.blend_modes, weights=marking_blend_weights, k=1)[0]

        # Determine pattern.
        chosen_marking = choice(
            random.choices(Pelt.pelt_categories, weights=Pelt.marking_weights, k=1)[0]
        )

        # Select overlays
        self.overfur = random.choices(Pelt.overfur_types, weights=Pelt.overfur_weights, k=1)[0]
        self.underfur = random.choices(Pelt.underfur_types, weights=Pelt.underfur_weights, k=1)[0]
            
        # Base color - must be picked before other colors for the tint pool
        self.tint_color = random.choices(Pelt.color_categories, weights=Pelt.color_weights, k=1)[0]
        self.tint_shade = random.choices(Pelt.shade_categories, weights=Pelt.shade_weights, k=1)[0]
    
        if game.tint_pools["use_color_pool"] == "true":
            # Marking color
            possible_colors = game.tint_pools["color_presets"][f"{game.tint_preset}"]["color_pools"]["marking_pool"][f"{self.tint_color}"]
            chosen_marking_color = random.choices(possible_colors, k=1)[0]

            weights = game.tint_pools["color_presets"][f"{game.tint_preset}"]["shade_weights"]["marking_pool"][f"{self.tint_shade}"]
            chosen_marking_shade = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]

            # Tortie marking is picked in the pattern init
        else:

            # Marking color
            chosen_marking_color = random.choices(Pelt.marking_color_categories, weights=(sprites.markings_tints["tint_categories"]["color_weights"]), k=1)[0]
            chosen_marking_shade = random.choices(Pelt.marking_shade_categories, weights=(sprites.markings_tints["tint_categories"]["shade_weights"]), k=1)[0]

            # Tortie marking color
            self.tortie_marking_color = random.choices(Pelt.marking_color_categories, weights=(sprites.markings_tints["tint_categories"]["color_weights"]), k=1)[0]
            self.tortie_marking_shade = random.choices(Pelt.marking_shade_categories, weights=(sprites.markings_tints["tint_categories"]["shade_weights"]), k=1)[0]

        
        # Tortie chance
        # There is a default chance for female tortie, slightly increased for completely random generation.
        tortie_chance_f = game.config["cat_generation"]["base_female_tortie"] - 1
        tortie_chance_m = game.config["cat_generation"]["base_male_tortie"]
        if gender == "female":
            torbie = random.getrandbits(tortie_chance_f) == 1
        else:
            torbie = random.getrandbits(tortie_chance_m) == 1

        chosen_pelt = self.tint_color
        chosen_tortie_base = None
        if torbie:
            # If it is tortie, the chosen pelt above becomes the base pelt.
            chosen_tortie_base = chosen_pelt
            if chosen_tortie_base in ("TwoColour", "SingleColour"):
                chosen_tortie_base = "Single"
            chosen_tortie_base = chosen_tortie_base.lower()
            chosen_pelt = random.choice(Pelt.torties)

        # ------------------------------------------------------------------------------------------------------------#
        #   PELT LENGTH
        # ------------------------------------------------------------------------------------------------------------#

        chosen_pelt_length = random.choice(Pelt.pelt_length)

        # ------------------------------------------------------------------------------------------------------------#
        #   PELT WHITE
        # ------------------------------------------------------------------------------------------------------------#

        chosen_white = random.randint(1, 100) <= 40

        # Adjustments to pelt chosen based on if the pelt has white in it or not.
        if chosen_pelt == "Calico":
            if not chosen_white:
                chosen_pelt = "Tortie"

        self.marking = chosen_marking
        self.name = chosen_pelt
        self.marking_shade = chosen_marking_shade
        self.marking_color = chosen_marking_color
        self.length = chosen_pelt_length
        self.tortiebase = (
            chosen_tortie_base  # This will be none if the cat isn't a tortie.
        )
        return chosen_white

    def init_pattern_color(self, parents, gender, missing_parent) -> bool:
        """Inits self.name, self.tint_color, self.length, 
            self.tortiebase and determines if the cat 
            will have white patche or not. 
            Return TRUE is the cat should have white patches, 
            false is not. """
        
        if parents:
            #If the cat has parents, use inheritance to decide pelt.
            chosen_white = self.pattern_color_inheritance(parents, gender, missing_parent)
        else:
            chosen_white = self.randomize_pattern_color(gender)

        return chosen_white

    def init_sprite(self):
        self.cat_sprites = {
            "newborn": 20,
            "kitten": random.randint(0, 2),
            "adolescent": random.randint(3, 5),
            "senior": random.randint(12, 14),
            "sick_young": 19,
            "sick_adult": 18,
        }
        self.reverse = bool(random.getrandbits(1))
        # skin chances
        self.skin = choice(Pelt.skin_sprites)

        if self.length != "long":
            self.cat_sprites["adult"] = random.randint(6, 8)
            self.cat_sprites["para_adult"] = 16
        else:
            self.cat_sprites["adult"] = random.randint(9, 11)
            self.cat_sprites["para_adult"] = 15
        self.cat_sprites["young adult"] = self.cat_sprites["adult"]
        self.cat_sprites["senior adult"] = self.cat_sprites["adult"]

    def init_scars(self, age):
        if age == "newborn":
            return

        if age in ("kitten", "adolescent"):
            scar_choice = random.randint(0, 50)  # 2%
        elif age in ("young adult", "adult"):
            scar_choice = random.randint(0, 20)  # 5%
        else:
            scar_choice = random.randint(0, 15)  # 6.67%

        if scar_choice == 1:
            self.scars.append(choice([choice(Pelt.scars1), choice(Pelt.scars3)]))

        if "NOTAIL" in self.scars and "HALFTAIL" in self.scars:
            self.scars.remove("HALFTAIL")

    def init_accessories(self, age):
        pattern_list = []
        if age == "newborn": 
            self.accessory_type = None
            self.accessory_color = None
            self.accessory_shade = None
            self.acc_accent_color = None
            return

        acc_display_choice = random.randint(0, 80)
        if age in ("kitten", "adolescent"):
            acc_display_choice = random.randint(0, 180)
        elif age in ("young adult", "adult"):
            acc_display_choice = random.randint(0, 100)

        if acc_display_choice == 1:
            self.accessory_type = choice([
                choice(Pelt.wild_accessories),
                choice(Pelt.herb_accessories)])

            if self.accessory_type in Pelt.accessory_categories["leaf"]:
                self.accessory_category = "leaf"
            elif self.accessory_type in Pelt.accessory_categories["flower"]:
                self.accessory_category = "flower"
            elif self.accessory_type in Pelt.accessory_categories["flower_nl"]:
                self.accessory_category = "flower_nl"
            elif self.accessory_type in Pelt.accessory_categories["stalk"]:
                self.accessory_category = "stalk"
            elif self.accessory_type in Pelt.accessory_categories["berry"]:
                self.accessory_category = "berry"
            elif self.accessory_type in Pelt.accessory_categories["seed"]:
                self.accessory_category = "seed"
            elif self.accessory_type in Pelt.accessory_categories["feathers"]:
                self.accessory_category = "feathers"
            elif self.accessory_type in Pelt.accessory_categories["moth"]:
                self.accessory_category = "moth"
            elif self.accessory_type in Pelt.accessory_categories["cicada"]:
                self.accessory_category = "cicada"
            else:
                print("failed")
    

            # the crying zone   
            possible_colors = sprites.accessory_tints["possible_tints"][f"{self.accessory_category}"].copy()
            self.accessory_color = choice(possible_colors)

            if self.accessory_color in sprites.accessory_tints["possible_tints"][f"warm_{self.accessory_category}"]:
                possible_colors = sprites.accessory_tints["possible_tints"][f"warm_{self.accessory_category}"].copy()
                self.accessory_shade = choice(possible_colors)
            elif self.accessory_color in sprites.accessory_tints["possible_tints"][f"cool_{self.accessory_category}"]:
                possible_colors = sprites.accessory_tints["possible_tints"][f"cool_{self.accessory_category}"].copy()
                self.accessory_shade = choice(possible_colors)
            else:
                possible_colors = sprites.accessory_tints["possible_tints"][f"monochrome_{self.accessory_category}"].copy()
                self.accessory_shade = choice(possible_colors)
            
            if Pelt.accessory_patterns[f"{self.accessory_type}"]:
                pattern_list.extend(Pelt.accessory_patterns[f"{self.accessory_type}"])
                totaloptions = len(Pelt.accessory_patterns[f"{self.accessory_type}"])
                pattern_count = random.randint(0, totaloptions)
                
                i = 0
                while i < pattern_count:
                    print(pattern_count)
                    pattern_choice = choice(pattern_list)
                    pattern_list.remove(pattern_choice) # remove from pattern list to ensure no duplicates
                    
                    possible_colors = sprites.accessory_tints["possible_tints"][f"{self.accessory_category}"].copy()

                    p_color = choice(possible_colors)

                    self.accessory_pattern.append(pattern_choice)
                    self.accessory_p_color.append(p_color)

                    if self.accessory_p_color[i] in sprites.accessory_tints["possible_tints"][f"warm_{self.accessory_category}"]:
                        possible_colors = sprites.accessory_tints["possible_tints"][f"warm_{self.accessory_category}"].copy()
                        self.accessory_p_shade.append(choice(possible_colors))
                    elif self.accessory_p_color[i] in sprites.accessory_tints["possible_tints"][f"cool_{self.accessory_category}"]:
                        possible_colors = sprites.accessory_tints["possible_tints"][f"cool_{self.accessory_category}"].copy()
                        self.accessory_p_shade.append(choice(possible_colors))
                    else:
                        possible_colors = sprites.accessory_tints["possible_tints"][f"monochrome_{self.accessory_category}"].copy()
                        self.accessory_p_shade.append(choice(possible_colors))

                    i += 1
                pattern_list.clear()
            # accent color
            possible_colors = sprites.accessory_tints["possible_tints"][f"{self.accessory_category}_accent"].copy()
            self.acc_accent_color = choice(possible_colors)
        else:
            self.accessory_type = None
            self.accessory_color = None
            self.accessory_shade = None
            self.acc_accent_color = None


    def create_accessory(self, acc):
        """
        Generates accessory 
        """
        pattern_list = []
        # honestly I have no idea if I could've just used init_accessories but then again... it would've been a bit too scuffed to add whatever was chosen in misc_events
        # I love programming
        self.accessory_type = choice(acc)

        print(self.accessory_type)

        if self.accessory_type in Pelt.accessory_categories["twoleg"]:
            self.accessory_category = "twoleg"
        elif self.accessory_type in Pelt.accessory_categories["leaf"]:
            self.accessory_category = "leaf"
        elif self.accessory_type in Pelt.accessory_categories["flower"]:
            self.accessory_category = "flower"
        elif self.accessory_type in Pelt.accessory_categories["flower_nl"]:
            self.accessory_category = "flower_nl"
        elif self.accessory_type in Pelt.accessory_categories["stalk"]:
            self.accessory_category = "stalk"
        elif self.accessory_type in Pelt.accessory_categories["berry"]:
            self.accessory_category = "berry"
        elif self.accessory_type in Pelt.accessory_categories["seed"]:
            self.accessory_category = "seed"
        elif self.accessory_type in Pelt.accessory_categories["feathers"]:
            self.accessory_category = "feathers"
        elif self.accessory_type in Pelt.accessory_categories["moth"]:
            self.accessory_category = "moth"
        elif self.accessory_type in Pelt.accessory_categories["cicada"]:
            self.accessory_category = "cicada"
        else:
            print("failed")
 
        possible_colors = sprites.accessory_tints["possible_tints"][f"{self.accessory_category}"]
        self.accessory_color = choice(possible_colors)

        if self.accessory_color in sprites.accessory_tints["possible_tints"][f"warm_{self.accessory_category}"]:
            possible_colors = sprites.accessory_tints["possible_tints"][f"warm_{self.accessory_category}"].copy()
            self.accessory_shade = choice(possible_colors)
        elif self.accessory_color in sprites.accessory_tints["possible_tints"][f"cool_{self.accessory_category}"]:
            possible_colors = sprites.accessory_tints["possible_tints"][f"cool_{self.accessory_category}"].copy()
            self.accessory_shade = choice(possible_colors)
        else:
            possible_colors = sprites.accessory_tints["possible_tints"][f"monochrome_{self.accessory_category}"].copy()
            self.accessory_shade = choice(possible_colors)

        if Pelt.accessory_patterns[f"{self.accessory_type}"]:
            pattern_list.extend(Pelt.accessory_patterns[f"{self.accessory_type}"])
            totaloptions = len(Pelt.accessory_patterns[f"{self.accessory_type}"])
            pattern_count = random.randint(0, totaloptions)

            i = 0
            while i < pattern_count:
                pattern_choice = choice(pattern_list)
                pattern_list.remove(pattern_choice) # remove from pattern list to ensure no duplicates

                self.accessory_pattern.append(pattern_choice)

                possible_colors = sprites.accessory_tints["possible_tints"][f"{self.accessory_category}"].copy()
                
                p_color = choice(possible_colors)
                self.accessory_p_color.append(p_color)

                if self.accessory_p_color[i] in sprites.accessory_tints["possible_tints"][f"warm_{self.accessory_category}"]:
                    possible_colors = sprites.accessory_tints["possible_tints"][f"warm_{self.accessory_category}"].copy()
                    self.accessory_p_shade.append(choice(possible_colors))
                elif self.accessory_p_color[i] in sprites.accessory_tints["possible_tints"][f"cool_{self.accessory_category}"]:
                    possible_colors = sprites.accessory_tints["possible_tints"][f"cool_{self.accessory_category}"].copy()
                    self.accessory_p_shade.append(choice(possible_colors))
                else:
                    possible_colors = sprites.accessory_tints["possible_tints"][f"monochrome_{self.accessory_category}"].copy()
                    self.accessory_p_shade.append(choice(possible_colors))
                

                i += 1

            pattern_list.clear()
        # accent color
        possible_colors = sprites.accessory_tints["possible_tints"][f"{self.accessory_category}_accent"].copy()
        self.acc_accent_color = choice(possible_colors)

        print(f"""
{self.accessory_category}

{self.accessory_pattern}
{self.accessory_p_color}
{self.accessory_p_shade}
""")

    def init_pattern(self):
        if self.name in Pelt.torties:
            if not self.tortiepattern:
                self.tortiepattern = choice(Pelt.tortiebases)
            if not self.pattern:
                self.pattern = choice(Pelt.tortiepatterns)

            wildcard_chance = game.config["cat_generation"]["wildcard_tortie"]
            if self.tint_color:
                # The "not wildcard_chance" allows users to set wildcard_tortie to 0
                # and always get wildcard torties.
                if not wildcard_chance or random.getrandbits(wildcard_chance) == 1:
                    # This is the "wildcard" chance, where you can get funky combinations.
                    # people are fans of the print message, so I'm putting it back
                    print("Wildcard tortie!")

                    # Allow any pattern:
                    self.tortiepattern = choice(Pelt.tortiebases)

                    # Allow any colors that aren't the base color.
                    self.tortie_color = choice(Pelt.color_categories)
                    self.tortie_shade = choice(Pelt.shade_categories)

                    if game.tint_pools["use_color_pool"] == "true":
                        possible_colors = sprites.cat_tints["possible_tints"][f"{self.tortie_color}_{self.tortie_shade}"].copy()
                        if self.tint in possible_colors:
                            possible_colors.remove(self.tint)

                        self.tortie_tint = choice(possible_colors)

                        possible_colors = game.tint_pools["color_presets"][f"{game.tint_preset}"]["color_pools"]["marking_pool"][f"{self.tortie_color}"]
                        self.tortie_marking_color = random.choices(possible_colors, k=1)[0]
                        
                        weights = game.tint_pools["color_presets"][f"{game.tint_preset}"]["shade_weights"]["marking_pool"][f"{self.tortie_shade}"]
                        self.tortie_marking_shade = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]
                            
                        color_tints = sprites.markings_tints["possible_tints"][f"{self.tortie_marking_color}_{self.tortie_marking_shade}"]
                        self.tortie_marking_tint = choice(color_tints)
                    
                    else:
                        possible_colors = sprites.cat_tints["possible_tints"][f"{self.tortie_color}_{self.tortie_shade}"].copy()
                        if self.tint in possible_colors:
                            possible_colors.remove(self.tint)

                        self.tortie_tint = choice(possible_colors)

                    # Underfur tint
                    weights = [0, 5, 2]
                    shade_selection = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]
                    color_tints = sprites.cat_tints["possible_tints"][f"{self.tortie_color}_{shade_selection}"]
                    self.tortie_underfur_tint = choice(color_tints)

                    # Overfur tint
                    if self.tortiepattern is None:
                        weights = [0, 5, 2]
                        shade_selection = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]
                        color_tints = sprites.cat_tints["possible_tints"][f"{self.tortie_marking_color}_{shade_selection}"]
                        self.tortie_overfur_tint = choice(color_tints)
                    else:
                        self.tortie_overfur_tint = self.tortie_marking_tint

                else:
                    # Normal generation
                    if self.tortiebase in ("singlestripe", "smoke", "single"):
                        self.tortiepattern = choice(
                            [
                                "tabby",
                                "mackerel",
                                "classic",
                                "single",
                                "smoke",
                                "agouti",
                                "ticked",
                            ]
                        )
                    else:
                        self.tortiepattern = choice(Pelt.tortiebases)


                    if game.tint_pools["use_color_pool"] == "true":
                            
                            possible_colors = game.tint_pools["color_presets"][f"{game.tint_preset}"]["color_pools"]["tortie_pool"][f"{self.tint_color}"]
                            self.tortie_color = random.choices(possible_colors, k=1)[0]

                            weights = game.tint_pools["color_presets"][f"{game.tint_preset}"]["shade_weights"]["tortie_pool"][f"{self.tint_shade}"]
                            self.tortie_shade = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]

                            possible_colors = game.tint_pools["color_presets"][f"{game.tint_preset}"]["color_pools"]["marking_pool"][f"{self.tortie_color}"]
                            self.tortie_marking_color = random.choices(possible_colors, k=1)[0]
                            
                            weights = game.tint_pools["color_presets"][f"{game.tint_preset}"]["shade_weights"]["marking_pool"][f"{self.tortie_shade}"]
                            self.tortie_marking_shade = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]
                            
                            color_tints = sprites.markings_tints["possible_tints"][f"{self.tortie_marking_color}_{self.tortie_marking_shade}"]
                            self.tortie_marking_tint = choice(color_tints)

                    else:
                        self.tortie_color = choice(Pelt.color_categories)

                        if self.tint_shade == "dark":
                            weights = (70, 30, 1)
                            self.tortie_shade = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]
                        if self.tint_shade == "medium":
                            weights = (50, 20, 1)
                            self.tortie_shade = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]
                        if self.tint_shade == "light":
                            weights = (1, 20, 70)
                            self.tortie_shade = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]

                    # Underfur tint
                    weights = [0, 5, 2]
                    shade_selection = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]
                    color_tints = sprites.cat_tints["possible_tints"][f"{self.tortie_color}_{shade_selection}"]
                    self.tortie_underfur_tint = choice(color_tints)

                    possible_colors = sprites.cat_tints["possible_tints"][f"{self.tortie_color}_{self.tortie_shade}"].copy()

                    if self.tint in possible_colors:
                        possible_colors.remove(self.tint)

                    self.tortie_tint = choice(possible_colors)

                    # Overfur tint
                    if self.tortiepattern is None:
                        weights = [0, 5, 2]
                        shade_selection = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]
                        color_tints = sprites.cat_tints["possible_tints"][f"{self.tortie_marking_color}_{shade_selection}"]
                        self.tortie_overfur_tint = choice(color_tints)
                    else:
                        self.tortie_overfur_tint = self.tortie_marking_tint

            else:
                self.tortie_color = "orange"
                self.tortie_shade = choice(Pelt.shade_categories)
                
                self.tortie_tint = sprites.cat_tints["possible_tints"][f"{self.tortie_color}_{self.tortie_shade}"]
        else:
            self.tortiepattern = None
            self.tortiecolour = None
            self.pattern = None

    def white_patches_inheritance(self, parents: tuple):
        par_whitepatches = set()
        par_points = []
        for p in parents:
            if p:
                if p.pelt.white_patches:
                    par_whitepatches.add(p.pelt.white_patches)
                if p.pelt.points:
                    par_points.append(p.pelt.points)

        if not parents:
            print("Error - no parents. Randomizing white patches.")
            self.randomize_white_patches()
            return

        # Direct inheritance. Will only work if at least one parent has white patches, otherwise continue on.
        if par_whitepatches and not random.randint(
            0, game.config["cat_generation"]["direct_inheritance"]
        ):
            # This ensures Torties and Calicos won't get direct inheritance of incorrect white patch types
            _temp = par_whitepatches.copy()
            if self.name == "Tortie":
                for p in _temp.copy():
                    if p in Pelt.high_white + Pelt.mostly_white + ["FULLWHITE"]:
                        _temp.remove(p)
            elif self.name == "Calico":
                for p in _temp.copy():
                    if p in Pelt.little_white + Pelt.mid_white:
                        _temp.remove(p)

            # Only proceed with the direct inheritance if there are white patches that match the pelt.
            if _temp:
                self.white_patches = choice(list(_temp))

                # Direct inheritance also effect the point marking.
                if par_points and self.name != "Tortie":
                    self.points = choice(par_points)
                else:
                    self.points = None

                return

        # dealing with points
        if par_points:
            chance = 10 - len(par_points)
        else:
            chance = 40
        # Chance of point is 1 / chance.
        if self.name != "Tortie" and not int(random.random() * chance):
            self.points = choice(Pelt.point_markings)
        else:
            self.points = None

        white_list = [
            Pelt.little_white,
            Pelt.mid_white,
            Pelt.high_white,
            Pelt.mostly_white,
            ["FULLWHITE"],
        ]

        weights = [0, 0, 0, 0, 0]  # Same order as white_list
        for p_ in par_whitepatches:
            if p_ in Pelt.little_white:
                add_weights = (40, 20, 15, 5, 0)
            elif p_ in Pelt.mid_white:
                add_weights = (10, 40, 15, 10, 0)
            elif p_ in Pelt.high_white:
                add_weights = (15, 20, 40, 10, 1)
            elif p_ in Pelt.mostly_white:
                add_weights = (5, 15, 20, 40, 5)
            elif p_ == "FULLWHITE":
                add_weights = (0, 5, 15, 40, 10)
            else:
                add_weights = (0, 0, 0, 0, 0)

            for x in range(0, len(weights)):
                weights[x] += add_weights[x]

        # If all the weights are still 0, that means none of the parents have white patches.
        if not any(weights):
            if not all(
                parents
            ):  # If any of the parents are None (unknown), use the following distribution:
                weights = [20, 10, 10, 5, 0]
            else:
                # Otherwise, all parents are known and don't have any white patches. Focus distribution on little_white.
                weights = [50, 5, 0, 0, 0]

        # Adjust weights for torties, since they can't have anything greater than mid_white:
        if self.name == "Tortie":
            weights = weights[:2] + [0, 0, 0]
            # Another check to make sure not all the values are zero. This should never happen, but better
            # safe than sorry.
            if not any(weights):
                weights = [2, 1, 0, 0, 0]
        elif self.name == "Calico":
            weights = [0, 0, 0] + weights[3:]
            # Another check to make sure not all the values are zero. This should never happen, but better
            # safe than sorry.
            if not any(weights):
                weights = [2, 1, 0, 0, 0]

        chosen_white_patches = choice(
            random.choices(white_list, weights=weights, k=1)[0]
        )

        self.white_patches = chosen_white_patches
        if self.points and self.white_patches in (
            Pelt.high_white,
            Pelt.mostly_white,
            "FULLWHITE",
        ):
            self.points = None

    def randomize_white_patches(self):
        # Points determination. Tortie can't be pointed
        if self.name != "Tortie" and not random.getrandbits(
            game.config["cat_generation"]["random_point_chance"]
        ):
            # Cat has colorpoint!
            self.points = choice(Pelt.point_markings)
        else:
            self.points = None

        # Adjust weights for torties, since they can't have anything greater than mid_white:
        if self.name == "Tortie":
            weights = (2, 1, 0, 0, 0)
        elif self.name == "Calico":
            weights = (0, 0, 20, 15, 1)
        else:
            weights = (10, 10, 10, 10, 1)

        white_list = [
            Pelt.little_white,
            Pelt.mid_white,
            Pelt.high_white,
            Pelt.mostly_white,
            ["FULLWHITE"],
        ]
        chosen_white_patches = choice(
            random.choices(white_list, weights=weights, k=1)[0]
        )

        self.white_patches = chosen_white_patches
        if self.points and self.white_patches in (
            Pelt.high_white,
            Pelt.mostly_white,
            "FULLWHITE",
        ):
            self.points = None

    def init_white_patches(self, pelt_white, parents: tuple):
        # Vit can roll for anyone, not just cats who rolled to have white in their pelt.
        par_vit = []
        for p in parents:
            if p:
                if p.pelt.vitiligo:
                    par_vit.append(p.pelt.vitiligo)

        vit_chance = max(game.config["cat_generation"]["vit_chance"] - len(par_vit), 0)
        if not random.getrandbits(vit_chance):
            self.vitiligo = choice(Pelt.vit)

        # If the cat was rolled previously to have white patches, then determine the patch they will have
        # these functions also handle points.
        if pelt_white:
            if parents:
                self.white_patches_inheritance(parents)
            else:
                self.randomize_white_patches()
        else:
            self.white_patches = None
            self.points = None

    def init_tint(self):
        """Sets tint for pelt and white patches"""

        # PELT TINT
        color_tints = sprites.cat_tints["possible_tints"][f"{self.tint_color}_{self.tint_shade}"]
        self.tint = choice(color_tints)

        if game.tint_pools["use_color_pool"] == "false":
            # TORTIE MARKING TINT
            color_tints = sprites.markings_tints["possible_tints"][f"{self.tortie_marking_color}_{self.tortie_marking_shade}"]
            self.tortie_marking_tint = choice(color_tints)

        # Eye tints
        color_tints = sprites.eye_tints["possible_tints"][f"{self.eye_color}_{self.eye_shade}"]
        self.eye_tint = choice(color_tints)

        color_tints = sprites.eye_tints["possible_tints"][f"{self.eye_s_color}_{self.eye_s_shade}"]
        self.eye_s_tint = choice(color_tints)

        color_tints = sprites.eye_tints["possible_tints"][f"{self.eye_p_color}_{self.eye_p_shade}"]
        self.eye_p_tint = choice(color_tints)

        if self.eye2_color is not None:
            color_tints = sprites.eye_tints["possible_tints"][f"{self.eye2_color}_{self.eye2_shade}"]
            self.eye2_tint = choice(color_tints)

            color_tints = sprites.eye_tints["possible_tints"][f"{self.eye2_s_color}_{self.eye2_s_shade}"]
            self.eye2_s_tint = choice(color_tints)

            color_tints = sprites.eye_tints["possible_tints"][f"{self.eye2_p_color}_{self.eye2_p_shade}"]
            self.eye2_p_tint = choice(color_tints)

        # Underfur tint
        weights = [0, 5, 2]
        shade_selection = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]
        color_tints = sprites.cat_tints["possible_tints"][f"{self.tint_color}_{shade_selection}"]
        self.underfur_tint = choice(color_tints)

        # MARKING TINT
        color_tints = sprites.markings_tints["possible_tints"][f"{self.marking_color}_{self.marking_shade}"]
        self.marking_tint = choice(color_tints)

        if self.marking is None:
            weights = [0, 5, 2]
            shade_selection = random.choices(Pelt.shade_categories, weights=weights, k=1)[0]
            color_tints = sprites.cat_tints["possible_tints"][f"{self.tint_color}_{shade_selection}"]
            self.overfur_tint = choice(color_tints)
        else:
            self.overfur_tint = self.marking_tint

        # WHITE PATCHES TINT
        if self.white_patches or self.points:
            # Now for white patches
            base_tints = sprites.white_patches_tints["possible_tints"]["basic"]
            
            """
            if self.tint_color in sprites.cat_tints["colour_groups"]:
                color_group = sprites.white_patches_tints["colour_groups"].get(self.tint_color, "white")
                color_tints = sprites.white_patches_tints["possible_tints"][color_group]
            else:
                color_tints = []

            if base_tints or color_tints:
                self.white_patches_tint = choice(base_tints + color_tints)
            else:
                self.white_patches_tint = "none"   """ 
        else:
            self.white_patches_tint = "none"

    @property
    def white(self):
        return self.white_patches or self.points

    @white.setter
    def white(self, val):
        print("Can't set pelt.white")
        return

    def describe_eyes(self):
        return (
            adjust_list_text(
                [
                    i18n.t(f"cat.eyes.{self.eye_color}"),
                    i18n.t(f"cat.eyes.{self.eye2_color}"),
                ]
            )
            if self.eye2_color
            else i18n.t(f"cat.eyes.{self.eye_color}")
        )

    @staticmethod
    def describe_appearance(cat, short=False):
        """Return a description of a cat

        :param Cat cat: The cat to describe
        :param bool short: Whether to return a heavily-truncated description, default False
        :return str: The cat's description
        """

        config = get_lang_config()["description"]
        ruleset = config["ruleset"]
        output = []
        pelt_pattern, pelt_color = _describe_pattern(cat, short)
        for rule, args in ruleset.items():
            temp = unpack_appearance_ruleset(cat, rule, short, pelt_pattern, pelt_color)

            if args == "" or temp == "":
                output.append(temp)
                continue

            # handle args
            argpool = {
                arg: unpack_appearance_ruleset(
                    cat, arg, short, pelt_pattern, pelt_color
                )
                for arg in args
            }
            argpool["key"] = temp
            argpool["count"] = 1 if short else 2
            output.append(i18n.t(**argpool))

        # don't forget the count argument!
        groups = []
        for grouping in config["groups"]:
            temp = ""
            items = [
                i18n.t(output[i], count=1 if short else 2)
                for i in grouping["values"]
                if output[i] != ""
            ]
            if len(items) == 0:
                continue
            if "pre_value" in grouping:
                temp = grouping["pre_value"]

            if grouping["format"] == "list":
                temp += adjust_list_text(items)
            else:
                temp += grouping["format"].join(items)

            if "post_value" in grouping:
                temp += grouping["post_value"]
            groups.append(temp)

        return "".join(groups)

    def get_sprites_name(self):
        return Pelt.sprites_names[self.name]


def _describe_pattern(cat, short=False):
    color_name = [f"cat.pelts.{str(cat.pelt.colour)}"]
    pelt_name = f"cat.pelts.{cat.pelt.name}{'' if short else '_long'}"
    if cat.pelt.name in Pelt.torties:
        pelt_name, color_name = _describe_torties(cat, color_name, short)

    color_name = [i18n.t(piece, count=1) for piece in color_name]
    color_name = "".join(color_name)

    if cat.pelt.white_patches:
        if cat.pelt.white_patches == "FULLWHITE":
            # If the cat is fullwhite, discard all other information. They are just white
            color_name = i18n.t("cat.pelts.FULLWHITE")
            pelt_name = ""
        elif cat.pelt.name != "Calico":
            white = i18n.t("cat.pelts.FULLWHITE")
            if i18n.t("cat.pelts.WHITE", count=1) in color_name:
                color_name = white
            elif cat.pelt.white_patches in Pelt.mostly_white:
                color_name = adjust_list_text([white, color_name])
            else:
                color_name = adjust_list_text([color_name, white])

    if cat.pelt.points:
        color_name = i18n.t("cat.pelts.point", color=color_name)
        if "ginger point" in color_name:
            color_name.replace("ginger point", "flame point")
            # look, I'm leaving this as a quirk of the english language, if it's a problem elsewhere lmk

    return pelt_name, color_name


def _describe_torties(cat, color_name, short=False) -> [str, str]:
    # Calicos and Torties need their own desciptions
    if short:
        # If using short, don't describe the colors of calicos and torties.
        # Just call them calico, tortie, or mottled
        if (
            cat.pelt.colour
            in Pelt.black_colours + Pelt.brown_colours + Pelt.white_colours
            and cat.pelt.tortiecolour
            in Pelt.black_colours + Pelt.brown_colours + Pelt.white_colours
        ):
            return "cat.pelts.mottled", ""
        else:
            return f"cat.pelts.{cat.pelt.name}", ""

    base = cat.pelt.tortiebase.lower()

    patches_color = f"cat.pelts.{cat.pelt.tortiecolour}"
    color_name.append("/")
    color_name.append(patches_color)

    if (
        cat.pelt.colour in Pelt.black_colours + Pelt.brown_colours + Pelt.white_colours
        and cat.pelt.tortiecolour
        in Pelt.black_colours + Pelt.brown_colours + Pelt.white_colours
    ):
        return "cat.pelts.mottled_long", color_name
    else:
        if base in (tabby.lower() for tabby in Pelt.tabbies) + [
            "bengal",
            "rosette",
            "speckled",
        ]:
            base = f"cat.pelts.{cat.pelt.tortiebase.capitalize()}_long"  # the extra space is intentional
        else:
            base = ""
        return base, color_name


_scar_details = [
    "NOTAIL",
    "HALFTAIL",
    "NOPAW",
    "NOLEFTEAR",
    "NORIGHTEAR",
    "NOEAR",
]


def unpack_appearance_ruleset(cat, rule, short, pelt, color):
    if rule == "scarred":
        if not short and len(cat.pelt.scars) >= 3:
            return "cat.pelts.scarred"
    elif rule == "fur_length":
        if not short and cat.pelt.length == "long":
            return "cat.pelts.long_furred"
    elif rule == "pattern":
        return pelt
    elif rule == "color":
        return color
    elif rule == "cat":
        if cat.genderalign in ("female", "trans female"):
            return "general.she-cat"
        elif cat.genderalign in ("male", "trans male"):
            return "general.tom"
        else:
            return "general.cat"
    elif rule == "vitiligo":
        if not short and cat.pelt.vitiligo:
            return "cat.pelts.vitiligo"
    elif rule == "amputation":
        if not short:
            scarlist = []
            for scar in cat.pelt.scars:
                if scar in _scar_details:
                    scarlist.append(i18n.t(f"cat.pelts.{scar}"))
            return (
                adjust_list_text(list(set(scarlist))) if len(scarlist) > 0 else ""
            )  # note: this doesn't preserve order!
    else:
        raise Exception(f"Unmatched ruleset item {rule} in describe_appearance!")
    return ""
