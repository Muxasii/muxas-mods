import logging
import pygame
import ujson

from scripts.cat.enums import CatGroup
from scripts.clan_package.settings.clan_settings import get_clan_setting
from scripts.game_structure import image_cache, constants

from scripts.game_structure.game.settings.settings import game_setting_get
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.cat.sprites import sprites

logger = logging.getLogger(__name__)

accessory_layers = {
    "middle": ["MAPLE LEAF", "HOLLY", "BLUE BERRIES", "FORGET ME NOTS", 
        "RYE STALK", "CATTAIL", "POPPY", "ORANGE POPPY", "CYAN POPPY", 
        "WHITE POPPY", "PINK POPPY", "BLUEBELLS", "LILY OF THE VALLEY", 
        "SNAPDRAGON", "HERBS", "PETALS", "NETTLE", "HEATHER", "GORSE", 
        "JUNIPER", "RASPBERRY", "LAVENDER", "OAK LEAVES", "CATMINT", 
        "MAPLE SEED", "LAUREL", "BULB WHITE", "BULB YELLOW", "BULB ORANGE", 
        "BULB PINK", "BULB BLUE", "CLOVER", "DAISY", "DRY HERBS", "DRY CATMINT", 
        "DRY NETTLES", "DRY LAURELS", "RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS",
    "GULL FEATHERS", "SPARROW FEATHERS", "MOTH WINGS", "ROSY MOTH WINGS", 
    "MORPHO BUTTERFLY", "MONARCH BUTTERFLY", "CICADA WINGS", "BLACK CICADA", 
    "CRIMSONBELL", "BLUEBELL", "YELLOWBELL", "CYANBELL", "REDBELL", "LIMEBELL", 
    "GREENBELL", "RAINBOWBELL", "BLACKBELL", "SPIKESBELL", "WHITEBELL", "PINKBELL", 
    "PURPLEBELL", "MULTIBELL", "INDIGOBELL", "CRIMSONBOW", "BLUEBOW", "YELLOWBOW", 
    "CYANBOW", "REDBOW", "LIMEBOW", "GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW", 
    "WHITEBOW", "PINKBOW", "PURPLEBOW", "MULTIBOW", "INDIGOBOW", "CRIMSONNYLON", 
    "BLUENYLON", "YELLOWNYLON", "CYANNYLON", "REDNYLON", "LIMENYLON", "GREENNYLON", 
    "RAINBOWNYLON", "BLACKNYLON", "SPIKESNYLON", "WHITENYLON", "PINKNYLON", "PURPLENYLON",
    "MULTINYLON", "INDIGONYLON",
    
        "WISTERIA",
        "ROSE MALLOW",
        "PICKLEWEED",
        "GOLDEN CREEPING JENNY", "CLOVER", "DAISY"
    ],
    "top": 
    []
}

def generate_sprite(
    cat,
    life_state=None,
    scars_hidden=False,
    acc_hidden=False,
    wing_hidden=False,
    always_living=False,
    disable_sick_sprite=False,
) -> pygame.Surface:
    """
    Generates the sprite for a cat, with optional arguments that will override certain things.

    :param life_state: sets the age life_stage of the cat, overriding the one set by its age. Set to string.
    :param scars_hidden: If True, doesn't display the cat's scars. If False, display cat scars.
    :param acc_hidden: If True, hide the accessory. If false, show the accessory.
    :param always_living: If True, always show the cat with living lineart
    :param disable_sick_sprite: If true, never use the not_working lineart.
                    If false, use the cat.not_working() to determine the no_working art.
    """

    if life_state is not None:
        age = life_state
    else:
        age = cat.age.value

    if always_living:
        dead = False
    else:
        dead = cat.dead
    
    if cat.status.group == CatGroup.DARK_FOREST:
        df = True
    else:
        df = False
        
    # setting the cat_sprite (bc this makes things much easier)
    if (
        not disable_sick_sprite
        and cat.not_working()
        and age != "newborn"
        and constants.CONFIG["cat_sprites"]["sick_sprites"]
    ):
        if age in ['kitten']:
            cat_sprite = str(21)
        elif age in ['adolescent']:
            cat_sprite = str(19)
        else:
            cat_sprite = str(18)
    elif cat.pelt.paralyzed and age != "newborn":
        if age in ["kitten", "adolescent"]:
            cat_sprite = str(17)
        else:
            if cat.pelt.length == "long":
                cat_sprite = str(16)
            else:
                cat_sprite = str(15)
    else:
        if age == "elder" and not constants.CONFIG["fun"]["all_cats_are_newborn"]:
            age = "senior"

        if constants.CONFIG["fun"]["all_cats_are_newborn"]:
            cat_sprite = str(cat.pelt.cat_sprites["newborn"])
        else:
            cat_sprite = str(cat.pelt.cat_sprites[age])

    new_sprite = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )
    
    # generating the sprite
    try:
        #-----------------
        # init variables
        #-----------------
        wing_scars = []
        cat_colors = {}
        eye_colors = {}
        cat_colors_tortie = {}

        # these are checked if they are something in the code
        back_wing = False
        front_wing = False

        #-----------------
        # get colors
        #-----------------
        eye_colors[cat.pelt.eye_colour] = sprites.eye_colors["eye_color_list"][cat.pelt.eye_colour]
        if cat.pelt.eye_colour2 is not None:
            eye_colors[cat.pelt.eye_colour2] = sprites.eye_colors["eye_color_list"][cat.pelt.eye_colour2]
        
        # tortie and calico use the pelt.name which is smelly
        if cat.pelt.name not in ['Tortie', 'Calico']:
            if cat.pelt.name.upper() in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
                cat_marking = "SINGLECOLOUR"
            else:
                cat_marking = cat.pelt.name.upper()
            
            color_type = sprites.pelt_colors["pelt_list"][cat_marking]["color_type"]
            cat_colors = sprites.pelt_colors["pelt_colors_list"][color_type][cat.pelt.colour]
        else:
            if cat.pelt.tortiebase.upper() in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
                cat_marking = "SINGLECOLOUR"
            else:
                cat_marking = cat.pelt.tortiebase.upper()
            
            if cat.pelt.tortiepattern.upper() in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
                tortie_pattern = "SINGLECOLOUR"
            else:
                tortie_pattern = cat.pelt.tortiepattern.upper()
            
            color_type = sprites.pelt_colors["pelt_list"][cat_marking]["color_type"]
            cat_colors = sprites.pelt_colors["pelt_colors_list"][color_type][cat.pelt.colour]

            color_type = sprites.pelt_colors["pelt_list"][tortie_pattern]["color_type"]
            cat_colors_tortie = sprites.pelt_colors["pelt_colors_list"][color_type][cat.pelt.tortiecolour]

        cat_layers = sprites.pelt_colors["pelt_list"][cat_marking]["layers"]
                
        #-----------------
        # create base
        #-----------------
        new_sprite.blit(create_base(cat_sprite, cat_colors, cat_colors_tortie, cat_layers, cat.pelt))

        # draw eye colors
        for num, eye in enumerate(eye_colors, start=1):
            new_sprite.blit(create_eyes(cat_sprite, eye_colors[eye], num))

        # draw lineart & shading
        if game_setting_get("shaders") and not dead:
            new_sprite.blit(
                sprites.sprites["shaders" + cat_sprite],
                (0, 0),
                special_flags=pygame.BLEND_RGB_MULT,
            )
            new_sprite.blit(sprites.sprites["lighting" + cat_sprite], (0, 0),
                special_flags=pygame.BLEND_RGB_ADD)

        if not dead:
            new_sprite.blit(sprites.sprites["lines" + cat_sprite], (0, 0))
        elif df:
            new_sprite.blit(sprites.sprites["lineartdf" + cat_sprite], (0, 0))
        elif dead:
            new_sprite.blit(sprites.sprites["lineartdead" + cat_sprite], (0, 0))

        # draw skin and scars2
        blendmode = pygame.BLEND_RGBA_MIN
        new_sprite.blit(sprites.sprites["skin" + cat.pelt.skin + cat_sprite], (0, 0))

        if not scars_hidden:
            for scar in cat.pelt.scars:
                if scar in cat.pelt.scars2:
                    new_sprite.blit(
                        sprites.sprites["scars" + scar + cat_sprite],
                        (0, 0),
                        special_flags=blendmode,
                    )

        #-----------------
        # create back wing
        #-----------------
        if cat.display_wing_count in [1, 2] and not wing_hidden:
            back_wing = pygame.Surface((sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA)
            back_wing.blit(create_wings(dead, df, cat_sprite, cat_colors, cat_colors_tortie, cat_layers, cat.pelt, cat.display_wing_count, cat.species, 0))

            # draw line art and shading
            if game_setting_get("shaders") and not dead:
                back_wing.blit(sprites.sprites[f'{cat.species}shaders' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                back_wing.blit(sprites.sprites[f'{cat.species}lighting' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGB_ADD)

            # mask
            back_wing.blit(sprites.sprites[cat.species + "_0_base" + cat_sprite],(0,0), special_flags=pygame.BLEND_RGBA_MULT)

            if not dead:
                back_wing.blit(sprites.sprites[f'{cat.species}_0_lines' + cat_sprite], (0, 0))
            elif df:
                back_wing.blit(sprites.sprites[f'{cat.species}_0_lineartdf' + cat_sprite], (0, 0))
            elif dead:
                back_wing.blit(sprites.sprites[f'{cat.species}_0_lineartdead' + cat_sprite], (0, 0))

            if cat.clipped_wings():
                back_wing.blit(
                    sprites.sprites[cat.species + "backscar" + "CLIPPED" + cat_sprite],
                    (0, 0),
                    special_flags=pygame.BLEND_RGBA_MIN,
                )
            new_sprite.blit(back_wing)
        
        #-----------------
        # create accessories
        #-----------------

        new_sprite.blit(create_accessories(cat_sprite, cat.pelt.accessory, acc_hidden, "middle"))

        #-----------------
        # create front wing
        #-----------------
        if cat.display_wing_count == 2 and not wing_hidden:
            front_wing = pygame.Surface((sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA)
            front_wing.blit(create_wings(dead, df, cat_sprite, cat_colors, cat_colors_tortie, cat_layers, cat.pelt, cat.display_wing_count, cat.species, 1))

            # draw line art and shading
            if game_setting_get("shaders") and not dead:
                front_wing.blit(sprites.sprites[f'{cat.species}shaders' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                front_wing.blit(sprites.sprites[f'{cat.species}lighting' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGB_ADD)

            # mask
            front_wing.blit(sprites.sprites[cat.species + "_1_base" + cat_sprite],(0,0), special_flags=pygame.BLEND_RGBA_MULT)

            if not dead:
                front_wing.blit(sprites.sprites[f'{cat.species}_1_lines' + cat_sprite], (0, 0))
            elif df:
                front_wing.blit(sprites.sprites[f'{cat.species}_1_lineartdf' + cat_sprite], (0, 0))
            elif dead:
                front_wing.blit(sprites.sprites[f'{cat.species}_1_lineartdead' + cat_sprite], (0, 0))
            
            if cat.clipped_wings():
                front_wing.blit(
                    sprites.sprites[cat.species + "scar" + "CLIPPED" + cat_sprite],
                    (0, 0),
                    special_flags=pygame.BLEND_RGBA_MIN,
                )
            new_sprite.blit(front_wing)

        #-----------------
        # fading fog
        #-----------------
        if (
            cat.pelt.opacity <= 97
            and not cat.prevent_fading
            and get_clan_setting("fading")
            and dead
        ):
            stage = "0"
            if 80 >= cat.pelt.opacity > 45:
                # Stage 1
                stage = "1"
            elif cat.pelt.opacity <= 45:
                # Stage 2
                stage = "2"

            new_sprite.blit(
                sprites.sprites["fademask" + stage + cat_sprite],
                (0, 0),
                special_flags=pygame.BLEND_RGBA_MULT,
            )

            if cat.status.group == CatGroup.DARK_FOREST:
                temp = sprites.sprites["fadedf" + stage + cat_sprite].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp
            else:
                temp = sprites.sprites["fadestarclan" + stage + cat_sprite].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp

        #-----------------
        # flip that cat
        #-----------------
        if cat.pelt.reverse:
            new_sprite = pygame.transform.flip(new_sprite, True, False)

    except (TypeError, KeyError):
        logger.exception("Failed to load sprite")
        print(cat)

        # Placeholder image
        new_sprite = image_cache.load_image(
            f"sprites/error_placeholder.png"
        ).convert_alpha()

    return new_sprite

def create_base(cat_sprite, colors, tortie_colors, markings, cat):
    
    finished_sprite = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )

    finished_sprite.blit(sprites.sprites['base' + cat_sprite], (0, 0))
    base_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
    base_tint.fill(colors["base"])
    finished_sprite.blit(base_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    for layer_name, layer in markings.items():
        finished_sprite.blit(create_layer(cat_sprite, layer_name, layer, colors))

    # TINTS
    if (
        cat.tint != "none"
        and cat.tint in sprites.cat_tints["tint_colours"]
    ):
        # Multiply with alpha does not work as you would expect - it just lowers the alpha of the
        # entire surface. To get around this, we first blit the tint onto a white background to dull it,
        # then blit the surface onto the sprite with pygame.BLEND_RGB_MULT
        tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        tint.fill(tuple(sprites.cat_tints["tint_colours"][cat.tint]))
        finished_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    if (
        cat.tint != "none"
        and cat.tint in sprites.cat_tints["dilute_tint_colours"]
    ):
        tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        tint.fill(tuple(sprites.cat_tints["dilute_tint_colours"][cat.tint]))
        finished_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # draw white patches
    if cat.white_patches is not None:
        white_patches = sprites.sprites[
            "white" + cat.white_patches + cat_sprite
        ].copy()

        # Apply tint to white patches.
        if (
            cat.white_patches_tint != "none"
            and cat.white_patches_tint
            in sprites.white_patches_tints["tint_colours"]
        ):
            tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            tint.fill(
                tuple(
                    sprites.white_patches_tints["tint_colours"][
                        cat.white_patches_tint
                    ]
                )
            )
            white_patches.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        finished_sprite.blit(white_patches, (0, 0))

    # draw vit & points

    if cat.points:
        points = sprites.sprites["white" + cat.points + cat_sprite].copy()
        if (
            cat.white_patches_tint != "none"
            and cat.white_patches_tint
            in sprites.white_patches_tints["tint_colours"]
        ):
            tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            tint.fill(
                tuple(
                    sprites.white_patches_tints["tint_colours"][
                        cat.white_patches_tint
                    ]
                )
            )
            points.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        finished_sprite.blit(points, (0, 0))

    if cat.vitiligo:
        finished_sprite.blit(
            sprites.sprites["white" + cat.vitiligo + cat_sprite], (0, 0)
        )

    return finished_sprite

def create_accessories(cat_sprite, accessories, acc_hidden, layer):
    finished_sprite = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )

    # draw accessories
    from scripts.cat.pelts import Pelt

    if not acc_hidden and accessories:
        categories = ["collars", "tail_accessories", "body_accessories", "head_accessories"]
        for category in categories:
            for accessory in accessories:
                if accessory in getattr(Pelt, category) and accessory in accessory_layers[layer]:
                    if accessory in Pelt.plant_accessories:
                        finished_sprite.blit(
                            sprites.sprites["acc_herbs" + accessory + cat_sprite],
                            (0, 0),
                        )
                    elif accessory in Pelt.wild_accessories:
                        finished_sprite.blit(
                            sprites.sprites["acc_wild" + accessory + cat_sprite],
                            (0, 0),
                        )
                    elif accessory in Pelt.collars:
                        finished_sprite.blit(
                            sprites.sprites["collars" + accessory + cat_sprite], (0, 0)
                        )

    return finished_sprite

def create_layer(cat_sprite, layer_name, layer, colors, species=""):
    finished_layer = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )

    layer_sprite = layer["sprite_name"]
    overfur_sprite = layer["overfur"]
    underfur_sprite = layer["underfur"]

    cat_layer_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
    cat_layer_tint.fill(colors[layer_name])

    cat_layer = sprites.sprites[species + layer_sprite + cat_sprite].copy()
    cat_layer.blit(cat_layer_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    if underfur_sprite:
        underfur_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        underfur_tint.fill(colors[f"{layer_name}_underfur"])

        underfur = sprites.sprites[species + underfur_sprite + cat_sprite].copy()
        underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        underfur.blit(sprites.sprites[layer_sprite + cat_sprite], special_flags=pygame.BLEND_RGBA_MULT)
        cat_layer.blit(underfur)

    if overfur_sprite:
        overfur_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        overfur_tint.fill(colors[f"{layer_name}_overfur"])

        overfur = sprites.sprites[species + overfur_sprite + cat_sprite].copy()
        overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        overfur.blit(sprites.sprites[layer_sprite + cat_sprite], special_flags=pygame.BLEND_RGBA_MULT)

        cat_layer.blit(overfur)
    
    cat_layer.blit(sprites.sprites[species + layer_sprite + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    finished_layer.blit(cat_layer, (0, 0))

    return finished_layer

def create_fluff(cat, cat_sprite, colors, markings):
    # TODO: used for any extra traits relating to adding more fur
    return

def create_trait(cat, cat_sprite, colors):
    # TODO: make function work in most scenarios, at least with things like antlers, horns, etc
    return

def create_wings(dead, df, cat_sprite, colors, tortie_colors, markings, cat, wing_count, species, layer):
    finished_wing_sprite = pygame.Surface(
        (sprites.size, sprites.size), pygame.SRCALPHA
    )
    marking_sprites = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )
    white_sprites = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )
    
    finished_wing_sprite.blit(sprites.sprites[f'{species}_{layer}_base' + cat_sprite], (0, 0))
    base_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
    base_tint.fill(colors["base"])
    finished_wing_sprite.blit(base_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    for layer_name, mark_layer in markings.items():
        marking_sprites.blit(create_layer(cat_sprite, layer_name, mark_layer, colors,species), (0, 0))
    
    finished_wing_sprite.blit(marking_sprites)
    # TINTS
    if (
        cat.tint != "none"
        and cat.tint in sprites.cat_tints["tint_colours"]
    ):
        # Multiply with alpha does not work as you would expect - it just lowers the alpha of the
        # entire surface. To get around this, we first blit the tint onto a white background to dull it,
        # then blit the surface onto the sprite with pygame.BLEND_RGB_MULT
        tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        tint.fill(tuple(sprites.cat_tints["tint_colours"][cat.tint]))
        finished_wing_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    if (
        cat.tint != "none"
        and cat.tint in sprites.cat_tints["dilute_tint_colours"]
    ):
        tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        tint.fill(tuple(sprites.cat_tints["dilute_tint_colours"][cat.tint]))
        finished_wing_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # draw white patches
    if cat.wing_white_patches is not None:
        wing_white_patches = sprites.sprites[species + 'white' + cat.wing_white_patches + cat_sprite].copy()

        # Apply tint to white patches.
        if cat.white_patches_tint != "none" and cat.white_patches_tint in sprites.white_patches_tints[
            "tint_colours"]:
            tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            tint.fill(tuple(sprites.white_patches_tints["tint_colours"][cat.white_patches_tint]))
            wing_white_patches.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        white_sprites.blit(wing_white_patches, (0, 0))

    # draw vit & points

    if cat.points:
        wing_points = sprites.sprites[species + 'white' + cat.points + cat_sprite].copy()
        if cat.white_patches_tint != "none" and cat.white_patches_tint in sprites.white_patches_tints[
            "tint_colours"]:
            tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            tint.fill(tuple(sprites.white_patches_tints["tint_colours"][cat.white_patches_tint]))
            wing_points.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        white_sprites.blit(wing_points, (0, 0))

    if cat.vitiligo:
        white_sprites.blit(sprites.sprites[species + 'white' + cat.vitiligo + cat_sprite], (0, 0))

    finished_wing_sprite.blit(white_sprites)
    # draw skin
    if cat.species == "bat cat":
        skin_color = sprites.skin_colors[f'{cat.skin}']
        membrane = sprites.sprites['batskin' + cat_sprite]

        membrane_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        membrane_tint.fill(skin_color)
        membrane.blit(membrane_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        membrane_tint2 = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        membrane_tint2.fill(colors["underfur"])

        membrane.blit(membrane_tint2, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        finished_wing_sprite.blit(membrane, (0, 0))

    return finished_wing_sprite

def create_eyes(cat_sprite, colors, num):
    finished_sprite = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )
    eye_base = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
    eye_base.fill(colors[0])

    eye_s = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
    eye_s.fill(colors[1])

    eye_p = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
    eye_p.fill(colors[2])

    # base
    eyes = sprites.sprites[f'eyes{num}' + 'base' + cat_sprite].copy()
    eyes.blit(eye_base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    eyes.blit(sprites.sprites[f'eyes{num}' + 'base' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # draw eye shade
    eye_shade = sprites.sprites[f'eyes{num}' + 'shade' + cat_sprite].copy()
    eye_shade.blit(eye_s, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    eye_shade.blit(sprites.sprites[f'eyes{num}' + 'shade' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # draw pupil
    eye_pupil = sprites.sprites[f'eyes{num}' + 'pupil' + cat_sprite].copy()
    eye_pupil.blit(eye_p, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    eye_pupil.blit(sprites.sprites[f'eyes{num}' + 'pupil' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # combine
    eyes.blit(eye_shade, (0, 0))
    eyes.blit(eye_pupil, (0, 0))

    finished_sprite.blit(eyes, (0, 0))

    return finished_sprite

def old_generate_sprite(
    cat,
    life_state=None,
    scars_hidden=False,
    acc_hidden=False,
    wing_hidden=False,
    always_living=False,
    disable_sick_sprite=False,
) -> pygame.Surface:
    """
    Generates the sprite for a cat, with optional arguments that will override certain things.

    :param life_state: sets the age life_stage of the cat, overriding the one set by its age. Set to string.
    :param scars_hidden: If True, doesn't display the cat's scars. If False, display cat scars.
    :param acc_hidden: If True, hide the accessory. If false, show the accessory.
    :param always_living: If True, always show the cat with living lineart
    :param disable_sick_sprite: If true, never use the not_working lineart.
                    If false, use the cat.not_working() to determine the no_working art.
    """

    if life_state is not None:
        age = life_state
    else:
        age = cat.age.value

    if always_living:
        dead = False
    else:
        dead = cat.dead
        
    # setting the cat_sprite (bc this makes things much easier)
    if (
        not disable_sick_sprite
        and cat.not_working()
        and age != "newborn"
        and constants.CONFIG["cat_sprites"]["sick_sprites"]
    ):
        if age in ['kitten']:
            cat_sprite = str(21)
        elif age in ['adolescent']:
            cat_sprite = str(19)
        else:
            cat_sprite = str(18)
    elif cat.pelt.paralyzed and age != "newborn":
        if age in ["kitten", "adolescent"]:
            cat_sprite = str(17)
        else:
            if cat.pelt.length == "long":
                cat_sprite = str(16)
            else:
                cat_sprite = str(15)
    else:
        if age == "elder" and not constants.CONFIG["fun"]["all_cats_are_newborn"]:
            age = "senior"

        if constants.CONFIG["fun"]["all_cats_are_newborn"]:
            cat_sprite = str(cat.pelt.cat_sprites["newborn"])
        else:
            cat_sprite = str(cat.pelt.cat_sprites[age])

    new_sprite = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )

    # draw base
    new_sprite.blit(sprites.sprites['base' + cat_sprite], (0, 0))

    # generating the sprite
    try:

        accessory_layers = {
            "middle": 
            ["MAPLE LEAF", "HOLLY", "BLUE BERRIES", "FORGET ME NOTS", 
             "RYE STALK", "CATTAIL", "POPPY", "ORANGE POPPY", "CYAN POPPY", 
             "WHITE POPPY", "PINK POPPY", "BLUEBELLS", "LILY OF THE VALLEY", 
             "SNAPDRAGON", "HERBS", "PETALS", "NETTLE", "HEATHER", "GORSE", 
             "JUNIPER", "RASPBERRY", "LAVENDER", "OAK LEAVES", "CATMINT", 
             "MAPLE SEED", "LAUREL", "BULB WHITE", "BULB YELLOW", "BULB ORANGE", 
             "BULB PINK", "BULB BLUE", "CLOVER", "DAISY", "DRY HERBS", "DRY CATMINT", 
             "DRY NETTLES", "DRY LAURELS", "RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS",
            "GULL FEATHERS", "SPARROW FEATHERS", "MOTH WINGS", "ROSY MOTH WINGS", 
            "MORPHO BUTTERFLY", "MONARCH BUTTERFLY", "CICADA WINGS", "BLACK CICADA", 
            "CRIMSONBELL", "BLUEBELL", "YELLOWBELL", "CYANBELL", "REDBELL", "LIMEBELL", 
            "GREENBELL", "RAINBOWBELL", "BLACKBELL", "SPIKESBELL", "WHITEBELL", "PINKBELL", 
            "PURPLEBELL", "MULTIBELL", "INDIGOBELL", "CRIMSONBOW", "BLUEBOW", "YELLOWBOW", 
            "CYANBOW", "REDBOW", "LIMEBOW", "GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW", 
            "WHITEBOW", "PINKBOW", "PURPLEBOW", "MULTIBOW", "INDIGOBOW", "CRIMSONNYLON", 
            "BLUENYLON", "YELLOWNYLON", "CYANNYLON", "REDNYLON", "LIMENYLON", "GREENNYLON", 
            "RAINBOWNYLON", "BLACKNYLON", "SPIKESNYLON", "WHITENYLON", "PINKNYLON", "PURPLENYLON",
            "MULTINYLON", "INDIGONYLON",
            
                "WISTERIA",
                "ROSE MALLOW",
                "PICKLEWEED",
                "GOLDEN CREEPING JENNY", "CLOVER", "DAISY"
            ],
            "top": 
            []
        }

        wing_scars = []

        # Get colors - makes things easier for later lol

        marking_fade_over = None
        tortie_marking_fade_over = None

        birdwing_markings = cat.pelt.wing_marks

        eye_base_color = sprites.eye_colors["colors"][cat.pelt.eye_colour][0]
        eye_shade_color = sprites.eye_colors["colors"][cat.pelt.eye_colour][1]
        eye_pupil_color = sprites.eye_colors["colors"][cat.pelt.eye_colour][2]
            
        if cat.pelt.eye_colour2 != None:
            eye2_base_color = sprites.eye_colors["colors"][cat.pelt.eye_colour2][0]
            eye2_shade_color = sprites.eye_colors["colors"][cat.pelt.eye_colour2][1]
            eye2_pupil_color = sprites.eye_colors["colors"][cat.pelt.eye_colour2][2]
        
        # Set cat_marking
        if cat.pelt.name not in ['Tortie', 'Calico']:
            if cat.pelt.name.upper() in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
                cat_marking = "SINGLECOLOUR"
            else:
                cat_marking = cat.pelt.name.upper()
        else:
            
            if cat.pelt.tortiebase.upper() in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
                cat_marking = "SINGLECOLOUR"
            else:
                cat_marking = cat.pelt.tortiebase.upper()
            
            if cat.pelt.tortiepattern.upper() in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
                tortie_pattern = "SINGLECOLOUR"
            else:
                tortie_pattern = cat.pelt.tortiepattern.upper()

        # Set color type
        color_type = sprites.pelt_colors["pelt_list"][cat_marking]["color_type"]

        if cat.pelt.name not in ['Tortie', 'Calico']:
            # Get dict
            if cat.pelt.name.upper() in color_type_dict['special']:
                color_type = "special"
            elif cat.pelt.name.upper() in color_type_dict['bengal']:
                color_type = "bengal"
            elif cat.pelt.name.upper() in color_type_dict['special_overfur']:
                color_type = "special_overfur"
            else:
                color_type = 0

            if cat.pelt.name.upper() in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
                # because they are essentially the same thing
                cat_marking = "SINGLECOLOUR"
            else:
                cat_marking = cat.pelt.name.upper()

            if color_type == "special":
                base_pelt = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][0]
                base_underfur_pelt = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][1]
                base_overfur_pelt = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][2]
                marking_base = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][3]
                marking_fade = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][4]
                marking_inside = color_dict['special'][f'{cat_marking}'][f'{cat.pelt.colour}'][5]
            elif color_type == "solid":
                base_pelt = color_dict['solid'][f'{cat.pelt.colour}'][0]
                base_underfur_pelt = color_dict['solid'][f'{cat.pelt.colour}'][1]
                base_overfur_pelt = color_dict['solid'][f'{cat.pelt.colour}'][2]
                marking_base = color_dict['solid'][f'{cat.pelt.colour}'][3]
                marking_fade = color_dict['solid'][f'{cat.pelt.colour}'][4]
                marking_inside = color_dict['solid'][f'{cat.pelt.colour}'][5]
            elif color_type == "special_overfur":
                base_pelt = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.colour}'][0]
                base_underfur_pelt = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.colour}'][1]
                base_overfur_pelt = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.colour}'][2]
                marking_fade = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.colour}'][3]
                marking_base = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.colour}'][4]
                marking_fade_over = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.colour}'][5]
            else:
                base_pelt = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][0]
                base_underfur_pelt = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][1]
                base_overfur_pelt = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][2]
                marking_base = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][3]
                marking_fade = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][4]
                marking_inside = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][5]
                marking_inside_fade = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][6]
        else:
            # Get dict
            if cat.pelt.tortiebase.upper() in color_type_dict['special']:
                color_type = "special"
            elif cat.pelt.tortiebase.upper() in color_type_dict['bengal']:
                color_type = "bengal"
            elif cat.pelt.tortiebase.upper() in color_type_dict['special_overfur']:
                color_type = "special_overfur"
            else:
                color_type = 0

            # Get dict of tortie
            if cat.pelt.tortiepattern.upper() in color_type_dict['special']:
                tortie_color_type = "special"
            elif cat.pelt.tortiepattern.upper() in color_type_dict['bengal']:
                tortie_color_type = "bengal"
            elif cat.pelt.tortiepattern.upper() in color_type_dict['special_overfur']:
                tortie_color_type = "special_overfur"
            else:
                tortie_color_type = 0
            
            if cat.pelt.tortiebase.upper() in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
                # because they are essentially the same thing
                cat_marking = "SINGLECOLOUR"
            else:
                cat_marking = cat.pelt.tortiebase.upper()
            
            if cat.pelt.tortiepattern.upper() in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
                # because they are essentially the same thing
                tortie_pattern = "SINGLECOLOUR"
            else:
                tortie_pattern = cat.pelt.tortiepattern.upper()

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
            elif color_type == "special_overfur":
                base_pelt = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.colour}'][0]
                base_underfur_pelt = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.colour}'][1]
                base_overfur_pelt = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.colour}'][2]
                marking_fade = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.colour}'][3]
                marking_base = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.colour}'][4]
                marking_fade_over = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.colour}'][5]
            else:
                base_pelt = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][0]
                base_underfur_pelt = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][1]
                base_overfur_pelt = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][2]
                marking_base = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][3]
                marking_fade = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][4]
                marking_inside = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][5]
                marking_inside_fade = color_dict[f'{color_type}'][f'{cat.pelt.colour}'][6]

            if tortie_color_type == "special":
                tortie_base_pelt = color_dict['special'][f'{tortie_pattern}'][f'{cat.pelt.tortiecolour}'][0]
                tortie_base_underfur_pelt = color_dict['special'][f'{tortie_pattern}'][f'{cat.pelt.tortiecolour}'][1]
                tortie_base_overfur_pelt = color_dict['special'][f'{tortie_pattern}'][f'{cat.pelt.tortiecolour}'][2]
                tortie_marking_base = color_dict['special'][f'{tortie_pattern}'][f'{cat.pelt.tortiecolour}'][3]
                tortie_marking_fade = color_dict['special'][f'{tortie_pattern}'][f'{cat.pelt.tortiecolour}'][4]
                tortie_marking_inside = color_dict['special'][f'{tortie_pattern}'][f'{cat.pelt.tortiecolour}'][5]
            elif tortie_color_type == 0:
                tortie_base_pelt = color_dict['solid'][f'{cat.pelt.tortiecolour}'][0]
                tortie_base_underfur_pelt = color_dict['solid'][f'{cat.pelt.tortiecolour}'][1]
                tortie_base_overfur_pelt = color_dict['solid'][f'{cat.pelt.tortiecolour}'][2]
                tortie_marking_base = color_dict['solid'][f'{cat.pelt.tortiecolour}'][3]
                tortie_marking_fade = color_dict['solid'][f'{cat.pelt.tortiecolour}'][4]
                tortie_marking_inside = color_dict['solid'][f'{cat.pelt.tortiecolour}'][5]
            elif tortie_color_type == "special_overfur":
                tortie_base_pelt = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.tortiecolour}'][0]
                tortie_base_underfur_pelt = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.tortiecolour}'][1]
                tortie_base_overfur_pelt = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.tortiecolour}'][2]
                tortie_marking_fade = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.tortiecolour}'][3]
                tortie_marking_base = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.tortiecolour}'][4]
                tortie_marking_fade_over = color_dict['special_overfur'][f'{cat_marking}'][f'{cat.pelt.tortiecolour}'][5]
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
        
        markings_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        markings_tint.fill(marking_base)

        mark_fade_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        mark_fade_tint.fill(marking_fade)

        if marking_fade_over:
            mark_fade_over_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            mark_fade_over_tint.fill(marking_fade_over)

        if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED']:
            underfur = sprites.sprites['underfur' + 'BENGAL' + cat_sprite].copy()
            underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        elif cat_marking in ['SINGLESTRIPE', 'DUOTONE']:
            underfur = sprites.sprites['underfur' + 'SOLID' + cat_sprite].copy()
            underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        elif cat_marking in ['SINGLECOLOUR']:
            underfur = sprites.sprites['underfur' + 'BASIC' + cat_sprite].copy()
            underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        elif cat_marking in ['SMOKE']:
            underfur = sprites.sprites['underfur' + 'SMOKE' + cat_sprite].copy()
            underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        else:
            underfur = sprites.sprites['underfur' + 'TABBY' + cat_sprite].copy()
            underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)


        new_sprite.blit(underfur, (0, 0))
            

        if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED']:
            overfur = sprites.sprites['overfur' + 'BENGAL' + cat_sprite].copy()
            overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        elif cat_marking in ['SINGLESTRIPE', 'DUOTONE']:
            overfur = sprites.sprites['overfur' + 'SOLID' + cat_sprite].copy()
            overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        elif cat_marking in ['SINGLECOLOUR', 'SMOKE']:
            overfur = sprites.sprites['overfur' + 'BASIC' + cat_sprite].copy()
            overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        else:
            overfur = sprites.sprites['overfur' + 'TABBY' + cat_sprite].copy()
            overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        new_sprite.blit(overfur, (0, 0))

        # draw markings

        if cat_marking not in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
            markings = sprites.sprites['markings' + cat_marking + cat_sprite].copy().convert_alpha()
            markings.blit(markings_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            # uh...
            if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED']:
                mark_fade = sprites.sprites['underfur' + 'BENGAL' + cat_sprite].copy()
                mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            
            elif cat_marking in ['DUOTONE']:
                mark_fade = sprites.sprites['overfur' + 'SOLID' + cat_sprite].copy()
                mark_fade.blit(mark_fade_over_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            elif cat_marking in ['SINGLESTRIPE']:
                mark_fade = sprites.sprites['overfur' + 'SOLID' + cat_sprite].copy()
                mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                
            else:
                mark_fade = sprites.sprites['underfur' + 'BASIC' + cat_sprite].copy()
                mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            markings.blit(mark_fade, (0, 0))

            if cat_marking in ['DUOTONE']:
                
                mark_fade_under = sprites.sprites['underfur' + 'SOLID' + cat_sprite].copy()
                mark_fade_under.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                markings.blit(mark_fade_under, (0,0))

            markings.blit(sprites.sprites['markings' + cat_marking + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            if cat_marking in ['SOKOKE', 'MARBLED', 'BENGAL', 'ROSETTE', 'MASKED', 'BRAIDED']:
                markings_inside_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                markings_inside_tint.fill(marking_inside)

                markings_inside = sprites.sprites['markinside' + cat_marking + cat_sprite].copy().convert_alpha()
                markings_inside.blit(markings_inside_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                # i am thirsty i should get water
                if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED']:
                    markings_inside_fade = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                    markings_inside_fade.fill(marking_inside_fade)

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

            if tortie_pattern in ['BENGAL', 'MARBLED', 'BRAIDED']:
                tortie_underfur = sprites.sprites['underfur' + 'BENGAL' + cat_sprite].copy()
                tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_underfur.blit(sprites.sprites['underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            elif tortie_pattern in ['SINGLESTRIPE', 'DUOTONE']:
                tortie_underfur = sprites.sprites['underfur' + 'SOLID' + cat_sprite].copy()
                tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_underfur.blit(sprites.sprites['underfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            elif tortie_pattern in ['SINGLECOLOUR']:
                tortie_underfur = sprites.sprites['underfur' + 'BASIC' + cat_sprite].copy()
                tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_underfur.blit(sprites.sprites['underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            elif tortie_pattern in ['SMOKE']:
                tortie_underfur = sprites.sprites['underfur' + 'SMOKE' + cat_sprite].copy()
                tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_underfur.blit(sprites.sprites['underfur' + 'SMOKE' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            else:
                tortie_underfur = sprites.sprites['underfur' + 'TABBY' + cat_sprite].copy()
                tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_underfur.blit(sprites.sprites['underfur' + 'TABBY' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            patches.blit(tortie_underfur, (0, 0))
                

            if tortie_pattern in ['BENGAL', 'MARBLED', 'BRAIDED']:
                tortie_overfur = sprites.sprites['overfur' + 'BENGAL' + cat_sprite].copy()
                tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_overfur.blit(sprites.sprites['overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            elif tortie_pattern in ['SINGLESTRIPE', 'DUOTONE']:
                tortie_overfur = sprites.sprites['overfur' + 'SOLID' + cat_sprite].copy()
                tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_overfur.blit(sprites.sprites['overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            elif tortie_pattern in ['SINGLECOLOUR']:
                tortie_overfur = sprites.sprites['overfur' + 'BASIC' + cat_sprite].copy()
                tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_overfur.blit(sprites.sprites['overfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            else:
                tortie_overfur = sprites.sprites['overfur' + 'TABBY' + cat_sprite].copy()
                tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                tortie_overfur.blit(sprites.sprites['overfur' + 'TABBY' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            patches.blit(tortie_overfur, (0, 0))

            # draw markings

            if tortie_pattern not in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
                tortie_markings_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tortie_markings_tint.fill(tortie_marking_base)

                tortie_mark_fade_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tortie_mark_fade_tint.fill(tortie_marking_fade)

                if tortie_marking_fade_over:
                    tortie_mark_fade_over_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                    tortie_mark_fade_over_tint.fill(tortie_marking_fade_over)

                tortie_markings = sprites.sprites['markings' + cat.pelt.tortiepattern.upper() + cat_sprite].copy().convert_alpha()
                tortie_markings.blit(tortie_markings_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                # uh...
                if cat.pelt.tortiepattern.upper() in ['BENGAL', 'MARBLED', 'BRAIDED']:
                    tortie_mark_fade = sprites.sprites['underfur' + 'BENGAL' + cat_sprite].copy()
                    tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    tortie_mark_fade.blit(sprites.sprites['underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                elif cat.pelt.tortiepattern.upper() in ['DUOTONE']:
                    tortie_mark_fade = sprites.sprites['overfur' + 'SOLID' + cat_sprite].copy()
                    tortie_mark_fade.blit(mark_fade_over_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    tortie_mark_fade.blit(sprites.sprites['overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                elif cat.pelt.tortiepattern.upper() in ['SINGLESTRIPE']:
                    tortie_mark_fade = sprites.sprites['overfur' + 'SOLID' + cat_sprite].copy()
                    tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    tortie_mark_fade.blit(sprites.sprites['overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    
                else:
                    tortie_mark_fade = sprites.sprites['underfur' + 'BASIC' + cat_sprite].copy()
                    tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    tortie_mark_fade.blit(sprites.sprites['underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                tortie_markings.blit(tortie_mark_fade, (0, 0))

                if cat.pelt.tortiepattern.upper() in ['DUOTONE']:
                
                    tortie_mark_fade_under = sprites.sprites['underfur' + 'SOLID' + cat_sprite].copy()
                    tortie_mark_fade_under.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    tortie_markings.blit(mark_fade_under, (0,0))

                tortie_markings.blit(sprites.sprites['markings' + cat.pelt.tortiepattern.upper() + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                if cat.pelt.tortiepattern.upper() in ['SOKOKE', 'MARBLED', 'BENGAL', 'ROSETTE', 'MASKED', 'BRAIDED']:
                    tortie_markings_inside_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                    tortie_markings_inside_tint.fill(tortie_marking_inside)

                    tortie_markings_inside = sprites.sprites['markinside' + cat.pelt.tortiepattern.upper() + cat_sprite].copy().convert_alpha()
                    tortie_markings_inside.blit(tortie_markings_inside_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    # my eyes are dry - inside markings
                    if cat.pelt.tortiepattern.upper() in ['BENGAL', 'MARBLED', 'BRAIDED']:
                        tortie_markings_inside_fade = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                        tortie_markings_inside_fade.fill(tortie_marking_inside_fade)
                        

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

        # TINTS
        if (
            cat.pelt.tint != "none"
            and cat.pelt.tint in sprites.cat_tints["tint_colours"]
        ):
            # Multiply with alpha does not work as you would expect - it just lowers the alpha of the
            # entire surface. To get around this, we first blit the tint onto a white background to dull it,
            # then blit the surface onto the sprite with pygame.BLEND_RGB_MULT
            tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            tint.fill(tuple(sprites.cat_tints["tint_colours"][cat.pelt.tint]))
            new_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        if (
            cat.pelt.tint != "none"
            and cat.pelt.tint in sprites.cat_tints["dilute_tint_colours"]
        ):
            tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            tint.fill(tuple(sprites.cat_tints["dilute_tint_colours"][cat.pelt.tint]))
            new_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        # draw white patches
        if cat.pelt.white_patches is not None:
            white_patches = sprites.sprites[
                "white" + cat.pelt.white_patches + cat_sprite
            ].copy()

            # Apply tint to white patches.
            if (
                cat.pelt.white_patches_tint != "none"
                and cat.pelt.white_patches_tint
                in sprites.white_patches_tints["tint_colours"]
            ):
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(
                    tuple(
                        sprites.white_patches_tints["tint_colours"][
                            cat.pelt.white_patches_tint
                        ]
                    )
                )
                white_patches.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            new_sprite.blit(white_patches, (0, 0))

        # draw vit & points

        if cat.pelt.points:
            points = sprites.sprites["white" + cat.pelt.points + cat_sprite].copy()
            if (
                cat.pelt.white_patches_tint != "none"
                and cat.pelt.white_patches_tint
                in sprites.white_patches_tints["tint_colours"]
            ):
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(
                    tuple(
                        sprites.white_patches_tints["tint_colours"][
                            cat.pelt.white_patches_tint
                        ]
                    )
                )
                points.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            new_sprite.blit(points, (0, 0))

        if cat.pelt.vitiligo:
            new_sprite.blit(
                sprites.sprites["white" + cat.pelt.vitiligo + cat_sprite], (0, 0)
            )

        # draw eyes & scars1
        """eyes = sprites.sprites["eyes" + cat.pelt.eye_colour + cat_sprite].copy()
        if cat.pelt.eye_colour2 != None:
            eyes.blit(
                sprites.sprites["eyes2" + cat.pelt.eye_colour2 + cat_sprite], (0, 0)
            )
        new_sprite.blit(eyes, (0, 0))"""

        # prepare tints
        eye_base = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        eye_base.fill(eye_base_color)

        eye_s = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        eye_s.fill(eye_shade_color)

        eye_p = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        eye_p.fill(eye_pupil_color)

        # base
        eyes = sprites.sprites['eyes' + 'base' + cat_sprite].copy()
        eyes.blit(eye_base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        eyes.blit(sprites.sprites['eyes' + 'base' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # draw eye shade
        eye_shade = sprites.sprites['eyes' + 'shade' + cat_sprite].copy()
        eye_shade.blit(eye_s, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        eye_shade.blit(sprites.sprites['eyes' + 'shade' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # draw pupil
        eye_pupil = sprites.sprites['eyes' + 'pupil' + cat_sprite].copy()
        eye_pupil.blit(eye_p, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        eye_pupil.blit(sprites.sprites['eyes' + 'pupil' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # combine
        eyes.blit(eye_shade, (0, 0))
        eyes.blit(eye_pupil, (0, 0))

        new_sprite.blit(eyes, (0, 0))

        if cat.pelt.eye_colour2 != None:
            # prepare tints
            eye2_base = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            eye2_base.fill(eye2_base_color)

            eye2_s = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            eye2_s.fill(eye2_shade_color)

            eye2_p = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            eye2_p.fill(eye2_pupil_color)

            # base
            eyes2 = sprites.sprites['eyes2' + 'base' + cat_sprite].copy()
            eyes2.blit(eye2_base, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            eyes2.blit(sprites.sprites['eyes2' + 'base' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            # draw eye2 shade
            eye2_shade = sprites.sprites['eyes2' + 'shade' + cat_sprite].copy()
            eye2_shade.blit(eye2_s, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            eye2_shade.blit(sprites.sprites['eyes2' + 'shade' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            # draw pupil
            eye2_pupil = sprites.sprites['eyes2' + 'pupil' + cat_sprite].copy()
            eye2_pupil.blit(eye2_p, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            eye2_pupil.blit(sprites.sprites['eyes2' + 'pupil' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            # combine
            eyes2.blit(eye2_shade, (0, 0))
            eyes2.blit(eye2_pupil, (0, 0))

            new_sprite.blit(eyes2, (0, 0))

        if not scars_hidden:
            for scar in cat.pelt.scars:
                if scar in cat.pelt.scars1:
                    new_sprite.blit(
                        sprites.sprites["scars" + scar + cat_sprite], (0, 0)
                    )
                if scar in cat.pelt.scars3:
                    new_sprite.blit(
                        sprites.sprites["scars" + scar + cat_sprite], (0, 0)
                    )

        # draw line art
        if game_setting_get("shaders") and not dead:
            new_sprite.blit(
                sprites.sprites["shaders" + cat_sprite],
                (0, 0),
                special_flags=pygame.BLEND_RGB_MULT,
            )
            new_sprite.blit(sprites.sprites["lighting" + cat_sprite], (0, 0),
                special_flags=pygame.BLEND_RGB_ADD)

        if not dead:
            new_sprite.blit(sprites.sprites["lines" + cat_sprite], (0, 0))
        elif cat.status.group == CatGroup.DARK_FOREST:
            new_sprite.blit(sprites.sprites["lineartdf" + cat_sprite], (0, 0))
        elif dead:
            new_sprite.blit(sprites.sprites["lineartdead" + cat_sprite], (0, 0))
        # draw skin and scars2
        blendmode = pygame.BLEND_RGBA_MIN
        new_sprite.blit(sprites.sprites["skin" + cat.pelt.skin + cat_sprite], (0, 0))

        if not scars_hidden:
            for scar in cat.pelt.scars:
                if scar in cat.pelt.scars2:
                    new_sprite.blit(
                        sprites.sprites["scars" + scar + cat_sprite],
                        (0, 0),
                        special_flags=blendmode,
                    )

        

        # back wings
        
        ########################################################################
        #                                                                      #
        # back wing start lol lmao love this                                        #
        #                                                                      #
        ########################################################################

        if cat.display_wing_count == 2 and not wing_hidden:
            
            # draw base
            back_wings = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            back_wings.blit(sprites.sprites[f'{cat.species}' + 'backbase' + cat_sprite], (0, 0))

            back_wings.blit(base_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED']:
                b_w_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                b_w_underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                b_w_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            elif cat_marking in ['SINGLESTRIPE']:
                b_w_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite].copy()
                b_w_underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                b_w_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            else:
                b_w_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                b_w_underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                b_w_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            back_wings.blit(b_w_underfur, (0, 0))
                

            if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED', 'DUOTONE']:
                b_w_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite].copy()
                b_w_overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                b_w_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            elif cat_marking in ['SINGLESTRIPE']:
                b_w_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite].copy()
                b_w_overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                b_w_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            else:
                b_w_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'BASIC' + cat_sprite].copy()
                b_w_overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                b_w_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            back_wings.blit(b_w_overfur, (0, 0))

            # draw markings

            if cat_marking not in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:

                b_w_markings = sprites.sprites[f'{cat.species}' + 'markings' + cat_marking + cat_sprite].copy().convert_alpha()
                b_w_markings.blit(markings_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                # uh...
                if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED']:
                    b_w_mark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                    b_w_mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    b_w_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                elif cat_marking in ['SINGLESTRIPE']:
                    b_w_mark_fade = sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite].copy()
                    b_w_mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    b_w_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                elif cat_marking in ['DUOTONE']:
                    b_w_mark_fade = sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite].copy()
                    b_w_mark_fade.blit(mark_fade_over_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    b_w_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    
                else:
                    b_w_mark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                    b_w_mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    b_w_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                b_w_markings.blit(b_w_mark_fade, (0, 0))            
                if cat_marking in ['DUOTONE']:
                
                    b_w_under = sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite].copy()
                    b_w_under.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                    
                    b_w_markings.blit(b_w_under, (0,0))

                b_w_markings.blit(sprites.sprites[f'{cat.species}' + 'markings' + cat_marking + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                if cat_marking in ['SOKOKE', 'MARBLED', 'BENGAL', 'ROSETTE', 'BRAIDED']:

                    b_w_markings_inside = sprites.sprites[f'{cat.species}' + 'markinside' + cat_marking + cat_sprite].copy().convert_alpha()
                    b_w_markings_inside.blit(markings_inside_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    # I hate how many times this needs done
                    if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED']:
                        b_w_markings_inside_fade = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                        b_w_markings_inside_fade.fill(marking_inside_fade)

                        b_w_mark_inside_fade = sprites.sprites['underfur' + 'BENGAL' + cat_sprite].copy()
                        b_w_mark_inside_fade.blit(b_w_markings_inside_fade, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        b_w_mark_inside_fade.blit(sprites.sprites['underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                        b_w_markings_inside.blit(b_w_mark_inside_fade, (0, 0))

                        b_w_mark_inside_fade.blit(sprites.sprites['markinside' + cat_marking + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                        b_w_markings_inside.blit(b_w_mark_inside_fade, (0, 0))
                    
                    b_w_markings_inside.blit(sprites.sprites[f'{cat.species}' + 'markinside' + cat_marking + cat_sprite], (0,0), special_flags=pygame.BLEND_RGBA_MULT)
                    b_w_markings.blit(b_w_markings_inside, (0, 0))
            
                # appear.
                back_wings.blit(b_w_markings, (0, 0))

            # draw bird cat markings - i honestly want to weep
            if birdwing_markings != "NONE" and cat.species == "bird cat":

                b_w_birdmarkings = sprites.sprites['wingmarks' + birdwing_markings + cat_sprite].copy().convert_alpha()
                b_w_birdmarkings.blit(markings_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                # uh...
                if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED']:
                    b_w_birdmark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                    b_w_birdmark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    b_w_birdmark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                elif cat_marking in ['SINGLESTRIPE']:
                    b_w_birdmark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite].copy()
                    b_w_birdmark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    b_w_birdmark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                elif cat_marking in ['DUOTONE']:
                    b_w_birdmark_fade = sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite].copy()
                    b_w_birdmark_fade.blit(mark_fade_over_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    b_w_birdmark_fade.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    
                else:
                    b_w_birdmark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                    b_w_birdmark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    b_w_birdmark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                b_w_birdmarkings.blit(b_w_birdmark_fade, (0, 0))
                
                if cat_marking in ['DUOTONE']:
                    b_w_under_birdmark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                    b_w_under_birdmark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    b_w_under_birdmark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    b_w_birdmarkings.blit(b_w_under_birdmark_fade, (0, 0))

                b_w_birdmarkings.blit(sprites.sprites['wingmarks' + birdwing_markings + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
                # appear.
                back_wings.blit(b_w_birdmarkings, (0, 0))

            # draw tortie
            if cat.pelt.name in ['Tortie', 'Calico']:
                b_w_patches = sprites.sprites[cat.species + "tortiemask" + cat.pelt.pattern + cat_sprite].copy()

                # draw base
                b_w_patches.blit(tortie_base_tint, (0,0), special_flags=pygame.BLEND_RGB_MULT)

                if tortie_pattern in ['BENGAL', 'MARBLED', 'BRAIDED', 'DUOTONE']:
                    b_w_tortie_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                    b_w_tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    tortie_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    b_w_patches.blit(b_w_tortie_underfur, (0, 0))
                elif tortie_pattern in ['SINGLESTRIPE']:
                    b_w_tortie_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite].copy()
                    b_w_tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    b_w_tortie_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    b_w_patches.blit(b_w_tortie_underfur, (0, 0))
                else:
                    b_w_tortie_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                    b_w_tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    b_w_tortie_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    b_w_patches.blit(b_w_tortie_underfur, (0, 0))
                    

                if tortie_pattern in ['BENGAL', 'MARBLED', 'BRAIDED', 'DUOTONE']:
                    b_w_tortie_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite].copy()
                    b_w_tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    b_w_tortie_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                elif tortie_pattern in ['SINGLESTRIPE']:
                    b_w_tortie_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite].copy()
                    b_w_tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    b_w_tortie_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                else:
                    b_w_tortie_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'BASIC' + cat_sprite].copy()
                    b_w_tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    b_w_tortie_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                b_w_patches.blit(b_w_tortie_overfur, (0, 0))

                # draw markings

                if tortie_pattern not in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:

                    b_w_tortie_markings = sprites.sprites[f'{cat.species}' + 'markings' + cat.pelt.tortiepattern.upper() + cat_sprite].copy().convert_alpha()
                    b_w_tortie_markings.blit(tortie_markings_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    # uh...
                    if cat.pelt.tortiepattern.upper() in ['BENGAL', 'MARBLED', 'BRAIDED']:
                        b_w_tortie_mark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                        b_w_tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        b_w_tortie_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    elif cat.pelt.tortiepattern.upper() in ['SINGLESTRIPE']:
                        b_w_tortie_mark_fade = sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite].copy()
                        b_w_tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        b_w_tortie_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    elif cat.pelt.tortiepattern.upper() in ['DUOTONE']:

                        b_w_tortie_mark_fade = sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite].copy()
                        b_w_tortie_mark_fade.blit(tortie_mark_fade_over_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        b_w_tortie_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        
                    else:
                        b_w_tortie_mark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                        b_w_tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        b_w_tortie_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    b_w_tortie_markings.blit(b_w_tortie_mark_fade, (0, 0))
                    if cat.pelt.tortiepattern.upper() in ['DUOTONE']:
                
                        b_w_tortie_under = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                        b_w_tortie_under.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                        
                        b_w_tortie_markings.blit(b_w_tortie_under, (0,0))

                    b_w_tortie_markings.blit(sprites.sprites[f'{cat.species}' + 'markings' + cat.pelt.tortiepattern.upper() + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    if cat.pelt.tortiepattern.upper() in ['SOKOKE', 'MARBLED', 'BENGAL', 'ROSETTE', 'BRAIDED']:
                        b_w_tortie_markings_inside_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                        b_w_tortie_markings_inside_tint.fill(tortie_marking_inside)

                        b_w_tortie_markings_inside = sprites.sprites[f'{cat.species}' + 'markinside' + cat.pelt.tortiepattern.upper() + cat_sprite].copy().convert_alpha()
                        b_w_tortie_markings_inside.blit(tortie_markings_inside_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        # marking inside for tortie
                        if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED']:
                            b_w_tortie_markings_inside_fade = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                            b_w_tortie_markings_inside_fade.fill(tortie_marking_inside_fade)

                            b_w_tortie_mark_inside_fade = sprites.sprites['underfur' + 'BENGAL' + cat_sprite].copy()
                            b_w_tortie_mark_inside_fade.blit(tortie_markings_inside_fade, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                            b_w_tortie_mark_inside_fade.blit(sprites.sprites['underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                            b_w_tortie_markings_inside.blit(b_w_tortie_mark_inside_fade, (0, 0))

                            b_w_tortie_mark_inside_fade.blit(sprites.sprites['markinside' + cat_marking + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                            b_w_tortie_markings_inside.blit(b_w_tortie_mark_inside_fade, (0, 0))
                        
                        b_w_tortie_markings_inside.blit(sprites.sprites[f'{cat.species}' + 'markinside' + cat.pelt.tortiepattern.upper() + cat_sprite], (0,0), special_flags=pygame.BLEND_RGBA_MULT)
                        b_w_tortie_markings.blit(b_w_tortie_markings_inside, (0, 0))
                
                    # appear.
                    b_w_patches.blit(b_w_tortie_markings, (0, 0))

                    # HERE WE GO AGAIN wing MARKINGS agaiN these variables keep getting longer
                    if birdwing_markings != "NONE" and cat.species == "bird cat":

                        b_w_bird_tortiemarkings = sprites.sprites['wingmarks' + birdwing_markings + cat_sprite].copy().convert_alpha()
                        b_w_bird_tortiemarkings.blit(tortie_markings_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        # uh...
                        if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED', 'DUOTONE']:
                            b_w_bird_tortiemark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                            b_w_bird_tortiemark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                            b_w_bird_tortiemark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        elif cat_marking in ['SINGLESTRIPE']:
                            b_w_bird_tortiemark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite].copy()
                            b_w_bird_tortiemark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                            b_w_bird_tortiemark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        elif cat_marking in ['DUOTONE']:

                            b_w_bird_tortiemark_fade = sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite].copy()
                            b_w_bird_tortiemark_fade.blit(tortie_mark_fade_over_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                            b_w_bird_tortiemark_fade.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                            
                        else:
                            b_w_bird_tortiemark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                            b_w_bird_tortiemark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                            b_w_bird_tortiemark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                        b_w_bird_tortiemarkings.blit(b_w_bird_tortiemark_fade, (0, 0))
                        
                        if cat_marking in ['DUOTONE']:
                            b_w_under_tortiebirdmark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                            b_w_under_tortiebirdmark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                            b_w_under_tortiebirdmark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                            b_w_bird_tortiemarkings.blit(b_w_under_tortiebirdmark_fade, (0, 0))

                        b_w_bird_tortiemarkings.blit(sprites.sprites['wingmarks' + birdwing_markings + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    
                        # appear.
                        b_w_patches.blit(b_w_bird_tortiemarkings, (0, 0))

                # *microwave.sfx*
                b_w_patches.blit(sprites.sprites[cat.species + "tortiemask" + cat.pelt.pattern + cat_sprite], (0,0), special_flags=pygame.BLEND_RGBA_MULT)

                back_wings.blit(b_w_patches, (0, 0))

            # TINT because tints still exist lol
            if (
                    cat.pelt.tint != "none"
                    and cat.pelt.tint in sprites.cat_tints["tint_colours"]
            ):
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(tuple(sprites.cat_tints["tint_colours"][cat.pelt.tint]))
                back_wings.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            if (
                    cat.pelt.tint != "none"
                    and cat.pelt.tint in sprites.cat_tints["dilute_tint_colours"]
            ):
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(tuple(sprites.cat_tints["dilute_tint_colours"][cat.pelt.tint]))
                back_wings.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

            # draw white patches
            if cat.pelt.wing_white_patches is not None:
                b_wing_white_patches = sprites.sprites[f'{cat.species}' + 'white' + cat.pelt.wing_white_patches + cat_sprite].copy()

                # Apply tint to white patches.
                if cat.pelt.white_patches_tint != "none" and cat.pelt.white_patches_tint in sprites.white_patches_tints[
                    "tint_colours"]:
                    tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                    tint.fill(tuple(sprites.white_patches_tints["tint_colours"][cat.pelt.white_patches_tint]))
                    b_wing_white_patches.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                back_wings.blit(b_wing_white_patches, (0, 0))

            # draw vit & points

            if cat.pelt.points:
                back_wing_points = sprites.sprites[cat.species + 'white' + cat.pelt.points + cat_sprite].copy()
                if cat.pelt.white_patches_tint != "none" and cat.pelt.white_patches_tint in sprites.white_patches_tints[
                    "tint_colours"]:
                    tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                    tint.fill(tuple(sprites.white_patches_tints["tint_colours"][cat.pelt.white_patches_tint]))
                    back_wing_points.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                back_wings.blit(back_wing_points, (0, 0))

            if cat.pelt.vitiligo:
                back_wings.blit(sprites.sprites[cat.species + 'white' + cat.pelt.vitiligo + cat_sprite], (0, 0))
            # draw line art
            if game_setting_get("shaders") and not dead:
                back_wings.blit(sprites.sprites[f'{cat.species}shaders' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                back_wings.blit(sprites.sprites[f'{cat.species}lighting' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGB_ADD)

            back_wings.blit(sprites.sprites[f'{cat.species}' + 'backbase' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)



            if not dead:
                back_wings.blit(sprites.sprites[f'{cat.species}' + 'backlines' + cat_sprite], (0, 0))
            elif cat.df:
                back_wings.blit(sprites.sprites[f'{cat.species}' + 'backlineartdf' + cat_sprite], (0, 0))
            elif dead:
                back_wings.blit(sprites.sprites[f'{cat.species}' + 'backlineartdead' + cat_sprite], (0, 0))
            # draw skin
            if cat.species == "bat cat":
                skin_color = sprites.skin_colors[f'{cat.pelt.skin}']
                b_membrane = sprites.sprites['batskin' + cat_sprite]

                b_membrane_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                b_membrane_tint.fill(skin_color)
                b_membrane.blit(b_membrane_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                b_membrane_tint2 = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                b_membrane_tint2.fill(base_underfur_pelt)

                b_membrane.blit(b_membrane_tint2, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

                back_wings.blit(b_membrane, (0, 0))
            
            # scars here whenever I do that...
            
            # clipped back_wings
            if cat.clipped_wings():
                back_wings.blit(
                    sprites.sprites[cat.species + "backscar" + "CLIPPED" + cat_sprite],
                    (0, 0),
                    special_flags=pygame.BLEND_RGBA_MIN,
                )
            
            back_wings.blit(sprites.sprites[f'{cat.species}' + 'backbase' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            new_sprite.blit(back_wings, (0, 0))
        
        ########################################################################
        #                                                                      #
        #end back wings because I will get confused as hell if I don't put this here#
        #                                                                      #
        ########################################################################

        # draw bat cat mane
        if cat.species == "bat cat" and cat.pelt.mane:
            # draw base
            bat_mane = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            bat_mane.blit(sprites.sprites['mane' + 'base' + cat_sprite], (0, 0))

            bat_mane.blit(base_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            # draw overlays
            mane_overfur = sprites.sprites['mane' + 'overfur' + cat_sprite].copy()
            mane_overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            mane_overfur.blit(sprites.sprites['mane' + 'overfur' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            mane_underfur = sprites.sprites['mane' + 'underfur' + cat_sprite].copy()
            mane_underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            mane_underfur.blit(sprites.sprites['mane' + 'underfur' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            bat_mane.blit(mane_overfur, (0, 0))
            bat_mane.blit(mane_underfur, (0, 0))

            # draw markings

            if cat.pelt.mane_marks != "NONE" and cat.pelt.mane_marks:
                # draw markings
                mane_markings = sprites.sprites['manemarks' + cat.pelt.mane_marks + cat_sprite].copy().convert_alpha()
                mane_markings.blit(markings_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                
                mane_mark_fade = sprites.sprites['mane' + 'overfur' + cat_sprite].copy()
                mane_mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                mane_mark_fade.blit(sprites.sprites['mane' + 'overfur' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                mane_mark_fade = sprites.sprites['mane' + 'underfur' + cat_sprite].copy()
                mane_mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                mane_mark_fade.blit(sprites.sprites['mane' + 'underfur' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        
                mane_markings.blit(mane_mark_fade, (0, 0))
                mane_markings.blit(sprites.sprites['manemarks' + cat.pelt.mane_marks + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                # appear.
                bat_mane.blit(mane_markings, (0, 0))


            # TINTS
            if (
                cat.pelt.tint != "none"
                and cat.pelt.tint in sprites.cat_tints["tint_colours"]
            ):
                # Multiply with alpha does not work as you would expect - it just lowers the alpha of the
                # entire surface. To get around this, we first blit the tint onto a white background to dull it,
                # then blit the surface onto the sprite with pygame.BLEND_RGB_MULT
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(tuple(sprites.cat_tints["tint_colours"][cat.pelt.tint]))
                bat_mane.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            if (
                cat.pelt.tint != "none"
                and cat.pelt.tint in sprites.cat_tints["dilute_tint_colours"]
            ):
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(tuple(sprites.cat_tints["dilute_tint_colours"][cat.pelt.tint]))
                bat_mane.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

            bat_mane.blit(sprites.sprites['mane' + 'base' + cat_sprite], (0,0), special_flags=pygame.BLEND_RGBA_MULT)

            new_sprite.blit(bat_mane, (0, 0))

            if game_setting_get("shaders") and not dead:
                new_sprite.blit(
                    sprites.sprites["maneshaders" + cat_sprite],
                    (0, 0),
                    special_flags=pygame.BLEND_RGB_MULT,
                )
                new_sprite.blit(sprites.sprites["manelighting" + cat_sprite], (0, 0),
                    special_flags=pygame.BLEND_RGB_ADD)

            if not dead:
                new_sprite.blit(sprites.sprites["manelines" + cat_sprite], (0, 0))
            elif cat.df:
                new_sprite.blit(sprites.sprites["manelineartdf" + cat_sprite], (0, 0))
            elif dead:
                new_sprite.blit(sprites.sprites["manelineartdead" + cat_sprite], (0, 0))

        # draw accessories
        from scripts.cat.pelts import Pelt

        if not acc_hidden and cat.pelt.accessory:
            cat_accessories = cat.pelt.accessory
            
            categories = ["collars", "tail_accessories", "body_accessories", "head_accessories"]
            for category in categories:
                for accessory in cat_accessories:
                    if accessory in getattr(Pelt, category) and accessory in accessory_layers["middle"]:
                        if accessory in cat.pelt.plant_accessories:
                            new_sprite.blit(
                                sprites.sprites["acc_herbs" + accessory + cat_sprite],
                                (0, 0),
                            )
                        elif accessory in cat.pelt.wild_accessories:
                            new_sprite.blit(
                                sprites.sprites["acc_wild" + accessory + cat_sprite],
                                (0, 0),
                            )
                        elif accessory in cat.pelt.collars:
                            new_sprite.blit(
                                sprites.sprites["collars" + accessory + cat_sprite], (0, 0)
                            )

        # draw the FRONT wings oh boy this will be fun :3c hahaaa

        ########################################################################
        #                                                                      #
        # wing start lol lmao love this                                        #
        #                                                                      #
        ########################################################################

        if cat.display_wing_count != 0 and not wing_hidden:
            
            # draw base
            wings = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            wings.blit(sprites.sprites[f'{cat.species}' + 'base' + cat_sprite], (0, 0))

            wings.blit(base_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED', 'DUOTONE']:
                w_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                w_underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                w_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            elif cat_marking in ['SINGLESTRIPE']:
                w_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite].copy()
                w_underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                w_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            else:
                w_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                w_underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                w_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            wings.blit(w_underfur, (0, 0))
                

            if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED', 'DUOTONE']:
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
                if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED']:
                    w_mark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                    w_mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                elif cat_marking in ['SINGLESTRIPE']:
                    w_mark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite].copy()
                    w_mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                elif cat_marking in ['DUOTONE']:
                    w_mark_fade = sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite].copy()
                    w_mark_fade.blit(mark_fade_over_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                else:
                    w_mark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                    w_mark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                w_markings.blit(w_mark_fade, (0, 0))
                
                if cat_marking in ['DUOTONE']:
                
                    w_under = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                    w_under.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                    
                    w_markings.blit(w_under, (0,0))

                w_markings.blit(sprites.sprites[f'{cat.species}' + 'markings' + cat_marking + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                if cat_marking in ['SOKOKE', 'MARBLED', 'BENGAL', 'ROSETTE', 'BRAIDED']:

                    w_markings_inside = sprites.sprites[f'{cat.species}' + 'markinside' + cat_marking + cat_sprite].copy().convert_alpha()
                    w_markings_inside.blit(markings_inside_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    # I hate how many times this needs done
                    if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED']:
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

            # draw bird cat markings - i honestly want to weep
            if birdwing_markings != "NONE" and cat.species == "bird cat":

                w_birdmarkings = sprites.sprites['wingmarks' + birdwing_markings + cat_sprite].copy().convert_alpha()
                w_birdmarkings.blit(markings_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                # uh...
                if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED']:
                    w_birdmark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                    w_birdmark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_birdmark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                elif cat_marking in ['SINGLESTRIPE']:
                    w_birdmark_fade = sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite].copy()
                    w_birdmark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_birdmark_fade.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                elif cat_marking in ['DUOTONE']:
                    w_birdmark_fade = sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite].copy()
                    w_birdmark_fade.blit(mark_fade_over_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_birdmark_fade.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                else:
                    w_birdmark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                    w_birdmark_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_birdmark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                w_birdmarkings.blit(w_birdmark_fade, (0, 0))

                if cat_marking in ['DUOTONE']:
                    w_birdmark_under_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                    w_birdmark_under_fade.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_birdmark_under_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    w_birdmarkings.blit(w_birdmark_under_fade, (0, 0))

                w_birdmarkings.blit(sprites.sprites['wingmarks' + birdwing_markings + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
                # appear.
                wings.blit(w_birdmarkings, (0, 0))

            # draw tortie
            if cat.pelt.name in ['Tortie', 'Calico']:
                w_patches = sprites.sprites[cat.species + "tortiemask" + cat.pelt.pattern + cat_sprite].copy()

                # draw base
                w_patches.blit(tortie_base_tint, (0,0), special_flags=pygame.BLEND_RGB_MULT)

                if tortie_pattern in ['BENGAL', 'MARBLED', 'BRAIDED', 'DUOTONE']:
                    w_tortie_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                    w_tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    tortie_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    w_patches.blit(w_tortie_underfur, (0, 0))
                elif tortie_pattern in ['SINGLESTRIPE']:
                    w_tortie_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite].copy()
                    w_tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_tortie_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    w_patches.blit(w_tortie_underfur, (0, 0))
                else:
                    w_tortie_underfur = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                    w_tortie_underfur.blit(tortie_underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_tortie_underfur.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    w_patches.blit(w_tortie_underfur, (0, 0))
                    

                if tortie_pattern in ['BENGAL', 'MARBLED', 'BRAIDED', 'DUOTONE']:
                    w_tortie_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite].copy()
                    w_tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_tortie_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                elif tortie_pattern in ['SINGLESTRIPE']:
                    w_tortie_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite].copy()
                    w_tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_tortie_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                else:
                    w_tortie_overfur = sprites.sprites[f'{cat.species}' + 'overfur' + 'BASIC' + cat_sprite].copy()
                    w_tortie_overfur.blit(tortie_overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    w_tortie_overfur.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                w_patches.blit(w_tortie_overfur, (0, 0))

                # draw markings

                if tortie_pattern not in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:

                    w_tortie_markings = sprites.sprites[f'{cat.species}' + 'markings' + cat.pelt.tortiepattern.upper() + cat_sprite].copy().convert_alpha()
                    w_tortie_markings.blit(tortie_markings_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                    # uh...
                    if cat.pelt.tortiepattern.upper() in ['BENGAL', 'MARBLED', 'BRAIDED']:
                        w_tortie_mark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                        w_tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        w_tortie_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    elif cat.pelt.tortiepattern.upper() in ['SINGLESTRIPE']:
                        w_tortie_mark_fade = sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite].copy()
                        w_tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        w_tortie_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        
                    elif cat.pelt.tortiepattern.upper() in ['DUOTONE']:
                        w_tortie_mark_fade = sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite].copy()
                        w_tortie_mark_fade.blit(mark_fade_over_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        w_tortie_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    else:
                        w_tortie_mark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                        w_tortie_mark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        w_tortie_mark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


                    w_tortie_markings.blit(w_tortie_mark_fade, (0, 0))

                    if cat.pelt.tortiepattern.upper() in ['DUOTONE']:
                
                        w_tortie_under = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                        w_tortie_under.blit(mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                        
                        w_tortie_markings.blit(w_tortie_under, (0,0))

                    w_tortie_markings.blit(sprites.sprites[f'{cat.species}' + 'markings' + cat.pelt.tortiepattern.upper() + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    if cat.pelt.tortiepattern.upper() in ['SOKOKE', 'MARBLED', 'BENGAL', 'ROSETTE', 'BRAIDED']:
                        w_tortie_markings_inside_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                        w_tortie_markings_inside_tint.fill(tortie_marking_inside)

                        w_tortie_markings_inside = sprites.sprites[f'{cat.species}' + 'markinside' + cat.pelt.tortiepattern.upper() + cat_sprite].copy().convert_alpha()
                        w_tortie_markings_inside.blit(tortie_markings_inside_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        # marking inside for tortie
                        if cat.pelt.tortiepattern.upper() in ['BENGAL', 'MARBLED', 'BRAIDED']:
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

                    # HERE WE GO AGAIN wing MARKINGS agaiN these variables keep getting longer
                    if birdwing_markings != "NONE" and cat.species == "bird cat":

                        w_bird_tortiemarkings = sprites.sprites['wingmarks' + birdwing_markings + cat_sprite].copy().convert_alpha()
                        w_bird_tortiemarkings.blit(tortie_markings_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                        # uh...
                        if cat_marking in ['BENGAL', 'MARBLED', 'BRAIDED', 'DUOTONE']:
                            w_bird_tortiemark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                            w_bird_tortiemark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                            w_bird_tortiemark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        elif cat_marking in ['SINGLESTRIPE']:
                            w_bird_tortiemark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite].copy()
                            w_bird_tortiemark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                            w_bird_tortiemark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'SOLID' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        elif cat_marking in ['DUOTONE']:

                            w_bird_tortiemark_fade = sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite].copy()
                            w_bird_tortiemark_fade.blit(tortie_mark_fade_over_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                            w_bird_tortiemark_fade.blit(sprites.sprites[f'{cat.species}' + 'overfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                            
                        else:
                            w_bird_tortiemark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite].copy()
                            w_bird_tortiemark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                            w_bird_tortiemark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BASIC' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                        w_bird_tortiemarkings.blit(w_bird_tortiemark_fade, (0, 0))
                        
                        if cat_marking in ['DUOTONE']:
                            w_under_tortiebirdmark_fade = sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite].copy()
                            w_under_tortiebirdmark_fade.blit(tortie_mark_fade_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                            w_under_tortiebirdmark_fade.blit(sprites.sprites[f'{cat.species}' + 'underfur' + 'BENGAL' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                            w_bird_tortiemarkings.blit(w_under_tortiebirdmark_fade, (0, 0))

                        w_bird_tortiemarkings.blit(sprites.sprites['wingmarks' + birdwing_markings + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    
                        # appear.
                        w_patches.blit(w_bird_tortiemarkings, (0, 0))

                # *microwave.sfx*
                w_patches.blit(sprites.sprites[cat.species + "tortiemask" + cat.pelt.pattern + cat_sprite], (0,0), special_flags=pygame.BLEND_RGBA_MULT)

                wings.blit(w_patches, (0, 0))

            # TINT because tints still exist lol
            if (
                    cat.pelt.tint != "none"
                    and cat.pelt.tint in sprites.cat_tints["tint_colours"]
            ):
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(tuple(sprites.cat_tints["tint_colours"][cat.pelt.tint]))
                wings.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            if (
                    cat.pelt.tint != "none"
                    and cat.pelt.tint in sprites.cat_tints["dilute_tint_colours"]
            ):
                tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                tint.fill(tuple(sprites.cat_tints["dilute_tint_colours"][cat.pelt.tint]))
                wings.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

            # draw white patches
            if cat.pelt.wing_white_patches is not None:
                wing_white_patches = sprites.sprites[f'{cat.species}' + 'white' + cat.pelt.wing_white_patches + cat_sprite].copy()

                # Apply tint to white patches.
                if cat.pelt.white_patches_tint != "none" and cat.pelt.white_patches_tint in sprites.white_patches_tints[
                    "tint_colours"]:
                    tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                    tint.fill(tuple(sprites.white_patches_tints["tint_colours"][cat.pelt.white_patches_tint]))
                    wing_white_patches.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

                wings.blit(wing_white_patches, (0, 0))

            # draw vit & points

            if cat.pelt.points:
                wing_points = sprites.sprites[cat.species + 'white' + cat.pelt.points + cat_sprite].copy()
                if cat.pelt.white_patches_tint != "none" and cat.pelt.white_patches_tint in sprites.white_patches_tints[
                    "tint_colours"]:
                    tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
                    tint.fill(tuple(sprites.white_patches_tints["tint_colours"][cat.pelt.white_patches_tint]))
                    wing_points.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                wings.blit(wing_points, (0, 0))

            if cat.pelt.vitiligo:
                wings.blit(sprites.sprites[cat.species + 'white' + cat.pelt.vitiligo + cat_sprite], (0, 0))
            # draw line art
            if game_setting_get("shaders") and not dead:
                wings.blit(sprites.sprites[f'{cat.species}shaders' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGB_MULT)
                wings.blit(sprites.sprites[f'{cat.species}lighting' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGB_ADD)

            wings.blit(sprites.sprites[f'{cat.species}' + 'base' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            if not dead:
                wings.blit(sprites.sprites[f'{cat.species}' + 'lines' + cat_sprite], (0, 0))
            elif cat.status.group == CatGroup.DARK_FOREST:
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
            
            # scars here whenever I do that...
            
            # clipped wings
            if cat.clipped_wings():
                wings.blit(
                    sprites.sprites[cat.species + "scar" + "CLIPPED" + cat_sprite],
                    (0, 0),
                    special_flags=pygame.BLEND_RGBA_MIN,
                )
            wings.blit(sprites.sprites[f'{cat.species}' + 'base' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            new_sprite.blit(wings, (0, 0))
        
        ########################################################################
        #                                                                      #
        #end wings because I will get confused as hell if I don't put this here#
        #                                                                      #
        ########################################################################

        # draw accessories top
        if not acc_hidden and cat.pelt.accessory:
            cat_accessories = cat.pelt.accessory
            
            categories = ["collars", "tail_accessories", "body_accessories", "head_accessories"]
            for category in categories:
                for accessory in cat_accessories:
                    if accessory in getattr(Pelt, category) and accessory in accessory_layers["top"]:
                        if accessory in cat.pelt.plant_accessories:
                            new_sprite.blit(
                                sprites.sprites["acc_herbs" + accessory + cat_sprite],
                                (0, 0),
                            )
                        elif accessory in cat.pelt.wild_accessories:
                            new_sprite.blit(
                                sprites.sprites["acc_wild" + accessory + cat_sprite],
                                (0, 0),
                            )
                        elif accessory in cat.pelt.collars:
                            new_sprite.blit(
                                sprites.sprites["collars" + accessory + cat_sprite],
                                (0, 0),
                            )

        # Apply fading fog
        if (
            cat.pelt.opacity <= 97
            and not cat.prevent_fading
            and get_clan_setting("fading")
            and dead
        ):
            stage = "0"
            if 80 >= cat.pelt.opacity > 45:
                # Stage 1
                stage = "1"
            elif cat.pelt.opacity <= 45:
                # Stage 2
                stage = "2"

            new_sprite.blit(
                sprites.sprites["fademask" + stage + cat_sprite],
                (0, 0),
                special_flags=pygame.BLEND_RGBA_MULT,
            )

            if cat.status.group == CatGroup.DARK_FOREST:
                temp = sprites.sprites["fadedf" + stage + cat_sprite].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp
            else:
                temp = sprites.sprites["fadestarclan" + stage + cat_sprite].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp

        # reverse, if assigned so
        if cat.pelt.reverse:
            new_sprite = pygame.transform.flip(new_sprite, True, False)

    except (TypeError, KeyError):
        logger.exception("Failed to load sprite")

        # Placeholder image
        new_sprite = image_cache.load_image(
            f"sprites/error_placeholder.png"
        ).convert_alpha()

    return new_sprite
