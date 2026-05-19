import logging
import pygame
import ujson

from scripts.cat.enums import CatGroup
from scripts.clan_package.settings.clan_settings import get_clan_setting
from scripts.game_structure import image_cache, constants

from scripts.game_structure.game.settings.settings import game_setting_get
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.cat.sprites.load_sprites import sprites
from scripts.ui.scale import ui_scale_dimensions

logger = logging.getLogger(__name__)

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
        cat_layers_tortie = {}
        wing_markings_tortie = {}
        wing_markings = {}
        cat_layers = {}
        
        cat_traits = {
            "bat_mane": f"{cat.pelt.mane_marks}"
        }

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

            cat_layers = sprites.pelt_colors["pelt_list"][cat_marking]["layers"]
        else:
            if cat.pelt.tortie_base.upper() in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
                cat_marking = "SINGLECOLOUR"
            else:
                cat_marking = cat.pelt.tortie_base.upper()
            
            if cat.pelt.tortie_pattern.upper() in ['SINGLECOLOUR', 'TWOCOLOUR', 'SINGLE']:
                tortie_pattern = "SINGLECOLOUR"
            else:
                tortie_pattern = cat.pelt.tortie_pattern.upper()
            
            color_type = sprites.pelt_colors["pelt_list"][cat_marking]["color_type"]
            cat_colors = sprites.pelt_colors["pelt_colors_list"][color_type][cat.pelt.colour]

            color_type = sprites.pelt_colors["pelt_list"][tortie_pattern]["color_type"]
            cat_colors_tortie = sprites.pelt_colors["pelt_colors_list"][color_type][cat.pelt.tortie_colour]

            cat_layers = sprites.pelt_colors["pelt_list"][cat_marking]["layers"]
            cat_layers_tortie = sprites.pelt_colors["pelt_list"][tortie_pattern]["layers"]

        if cat.species == "bird cat" and cat.pelt.wing_marks != "NONE":
            wing_markings = {
                "sprite_name": f"wingmarks{cat.pelt.wing_marks}",
                "overfur": cat_layers["markings"]["overfur"] if "markings" in cat_layers else False,
                "underfur": cat_layers["markings"]["underfur"] if "markings" in cat_layers else False
            }
            if cat_layers_tortie:
                wing_markings_tortie = {
                    "sprite_name": f"wingmarks{cat.pelt.wing_marks}",
                    "overfur": cat_layers_tortie["markings"]["overfur"] if "markings" in cat_layers_tortie else False,
                    "underfur": cat_layers_tortie["markings"]["underfur"] if "markings" in cat_layers_tortie else False
                }
            #print(wing_markings)
        

        #-----------------
        # create base
        #-----------------
        new_sprite.blit(create_base(cat_sprite, cat_colors, cat_layers, cat.pelt, cat_colors_tortie, cat_layers_tortie))

        # draw eye colors
        for num, eye in enumerate(eye_colors, start=1):
            new_sprite.blit(create_eyes(cat_sprite, eye_colors[eye], num))

        # draw scars
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
        if cat.display_wing_count == 2 and not wing_hidden and not cat.species == "earth cat":
            back_wing = pygame.Surface((sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA)
            back_wing.blit(create_wings(cat_sprite, cat_colors, cat_layers, cat.pelt, cat.species, 0, wing_markings, wing_markings_tortie, cat_colors_tortie, cat_layers_tortie, dead=dead, df=df))

            if cat.clipped_wings():
                back_wing.blit(
                    sprites.sprites[cat.species + "backscar" + "CLIPPED" + cat_sprite],
                    (0, 0),
                    special_flags=pygame.BLEND_RGBA_MIN,
                )
            new_sprite.blit(back_wing)
        #-----------------
        # create bat fluff
        #-----------------

        if cat.pelt.mane:
            bat_mane = pygame.Surface((sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA)
            bat_mane.blit(create_trait(dead, df, cat.pelt, cat_sprite, cat_colors, "bat_mane", sprites.extra_traits["bat_mane"], cat_traits, True))

            new_sprite.blit(bat_mane)

        #-----------------
        # create accessories middle
        #-----------------

        new_sprite.blit(create_accessories(cat_sprite, cat.pelt.accessory, acc_hidden, "middle"))

        #-----------------
        # create front wing
        #-----------------
        if cat.display_wing_count in [1, 2] and not wing_hidden and not cat.species == "earth cat":
            front_wing = pygame.Surface((sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA)
            front_wing.blit(create_wings(cat_sprite, cat_colors, cat_layers, cat.pelt, cat.species, 1, wing_markings, wing_markings_tortie, cat_colors_tortie, cat_layers_tortie, dead=dead, df=df))
            
            if cat.clipped_wings():
                front_wing.blit(
                    sprites.sprites[cat.species + "scar" + "CLIPPED" + cat_sprite],
                    (0, 0),
                    special_flags=pygame.BLEND_RGBA_MIN,
                )
            new_sprite.blit(front_wing)

        
        #-----------------
        # create accessories top
        #-----------------

        new_sprite.blit(create_accessories(cat_sprite, cat.pelt.accessory, acc_hidden, "top"))

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

def create_base(cat_sprite, colors, markings, cat, tortie_colors=None, tortie_markings=None, tortie=False):
    finished_sprite = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )

    finished_sprite.blit(sprites.sprites['base' + cat_sprite], (0, 0))
    base_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
    base_tint.fill(colors["base"])
    finished_sprite.blit(base_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    for layer_name, layer in markings.items():
        if layer_name.lower() == "none":
            return 
        finished_sprite.blit(create_layer(cat_sprite, layer_name, layer, colors))

    if (cat.name in ["Tortie", "Calico"] and not tortie):
        tortie_sprite = pygame.Surface(
            (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
        )
        tortie_sprite.blit(create_base(cat_sprite, tortie_colors, tortie_markings, cat, tortie=True))
        tortie_sprite.blit(sprites.sprites["tortiemask" + cat.tortie_marking + cat_sprite], (0, 0),  special_flags=pygame.BLEND_RGBA_MULT)

        finished_sprite.blit(tortie_sprite)

    if not tortie:
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
    from scripts.cat.pelts import plant_accessories, wild_accessories, collars

    if not acc_hidden and accessories:
        categories = ["collars", "tail_accessories", "body_accessories", "head_accessories"]
        for category in categories:
            for accessory in accessories:
                if (accessory in sprites.accessories["accessory_layers"][layer]):
                    if accessory in plant_accessories:
                        finished_sprite.blit(
                            sprites.sprites["acc_herbs" + accessory + cat_sprite],
                            (0, 0),
                        )
                    elif accessory in wild_accessories:
                        finished_sprite.blit(
                            sprites.sprites["acc_wild" + accessory + cat_sprite],
                            (0, 0),
                        )
                    elif accessory in collars:
                        finished_sprite.blit(
                            sprites.sprites["collars" + accessory + cat_sprite], (0, 0)
                        )

    return finished_sprite

def create_layer(cat_sprite, layer_name, layer, colors, layer_sprite_override=None, prefix="", disable_suffix=False):
    finished_layer = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )
    
    if layer_sprite_override:
        layer_sprite = layer_sprite_override
    else:
        layer_sprite = layer["sprite_name"]
    overfur_sprite = layer["overfur"]
    underfur_sprite = layer["underfur"]

    cat_layer_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
    cat_layer_tint.fill(colors[layer_name])

    cat_layer = sprites.sprites[prefix + layer_sprite + cat_sprite].copy()
    cat_layer.blit(cat_layer_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    if underfur_sprite:
        underfur_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        if disable_suffix:
            underfur_tint.fill(colors[layer_name])
        else:
            underfur_tint.fill(colors[f"{layer_name}_underfur"])

        underfur = sprites.sprites[prefix + underfur_sprite + cat_sprite].copy()
        underfur.blit(underfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        underfur.blit(sprites.sprites[prefix + layer_sprite + cat_sprite], special_flags=pygame.BLEND_RGBA_MULT)
        cat_layer.blit(underfur)

    if overfur_sprite:
        overfur_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        if disable_suffix:
            overfur_tint.fill(colors[layer_name])
        else:
            overfur_tint.fill(colors[f"{layer_name}_overfur"])

        overfur = sprites.sprites[prefix + overfur_sprite + cat_sprite].copy()
        overfur.blit(overfur_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        overfur.blit(sprites.sprites[prefix + layer_sprite + cat_sprite], special_flags=pygame.BLEND_RGBA_MULT)

        cat_layer.blit(overfur)
    
    cat_layer.blit(sprites.sprites[prefix + layer_sprite + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    finished_layer.blit(cat_layer, (0, 0))

    return finished_layer

def create_trait(dead, df, cat, cat_sprite, colors, trait_name, trait_info, cat_traits, add_tint=False):
    finished_sprite = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )
    for layer_name, layer in trait_info["layers"].items():
        if layer_name == "markings" and cat_traits[trait_name].upper() == "NONE":
            continue
        
        finished_sprite.blit(create_layer(
            cat_sprite, layer_name, layer, colors, 
            f"{trait_name}{layer_name}{cat_traits[trait_name]}" if layer["sprite_name"] == "cat" else False,
            disable_suffix=True if layer_name == "base" else False))
        
    if add_tint:
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

    # draw line art and shading
    if game_setting_get("shaders") and not dead:
        finished_sprite.blit(sprites.sprites[f'{trait_name}shaders' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        finished_sprite.blit(sprites.sprites[f'{trait_name}lighting' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    if not dead:
        finished_sprite.blit(sprites.sprites[f'{trait_name}lines' + cat_sprite], (0, 0))
    elif df:
        finished_sprite.blit(sprites.sprites[f'{trait_name}lineartdf' + cat_sprite], (0, 0))
    elif dead:
        finished_sprite.blit(sprites.sprites[f'{trait_name}lineartdead' + cat_sprite], (0, 0))
    

    return finished_sprite

def create_wings(cat_sprite, colors, markings, cat, species, layer, wing_marks, tortie_wing_marks=None, tortie_colors=None, tortie_markings=None, tortie=False, dead=False, df=False):
    finished_sprite = pygame.Surface(
        (sprites.size, sprites.size), pygame.SRCALPHA
    )
    marking_sprites = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )
    white_sprites = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )
    
    finished_sprite.blit(sprites.sprites[f'{species}_{layer}_base' + cat_sprite], (0, 0))
    base_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
    base_tint.fill(colors["base"])
    finished_sprite.blit(base_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    for layer_name, mark_layer in markings.items():
        marking_sprites.blit(create_layer(cat_sprite, layer_name, mark_layer, colors, prefix=species), (0, 0))
    
    finished_sprite.blit(marking_sprites)
    
    if wing_marks:
        #print(f"Creating layer: {wing_marks}")
        finished_sprite.blit(create_layer(cat_sprite, "markings", wing_marks, colors, prefix=species))

    if (cat.name in ["Tortie", "Calico"] and not tortie):
        tortie_sprite = pygame.Surface(
            (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
        )
        tortie_sprite.blit(create_wings(cat_sprite, tortie_colors, tortie_markings, cat, species, layer, tortie_wing_marks, tortie=True))
        tortie_sprite.blit(sprites.sprites[species + "tortiemask" + cat.tortie_marking + cat_sprite], (0, 0),  special_flags=pygame.BLEND_RGBA_MULT)

        finished_sprite.blit(tortie_sprite)

    if not tortie:
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

        finished_sprite.blit(white_sprites)
        # draw skin
        if species == "bat cat":
            skin_color = sprites.skin_colors[f'{cat.skin}']
            membrane = sprites.sprites['batskin' + cat_sprite]

            membrane_tint = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            membrane_tint.fill(skin_color)
            membrane.blit(membrane_tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            membrane_tint2 = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
            membrane_tint2.fill(colors["underfur"])

            membrane.blit(membrane_tint2, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

            finished_sprite.blit(membrane, (0, 0))

        # draw line art and shading
        if game_setting_get("shaders") and not dead:
            finished_sprite.blit(sprites.sprites[f'{species}shaders' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            finished_sprite.blit(sprites.sprites[f'{species}lighting' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        # mask
        finished_sprite.blit(sprites.sprites[species + f"_{layer}_base" + cat_sprite],(0,0), special_flags=pygame.BLEND_RGBA_MULT)

        if not dead:
            finished_sprite.blit(sprites.sprites[f'{species}_{layer}_lines' + cat_sprite], (0, 0))
        elif df:
            finished_sprite.blit(sprites.sprites[f'{species}_{layer}_lineartdf' + cat_sprite], (0, 0))
        elif dead:
            finished_sprite.blit(sprites.sprites[f'{species}_{layer}_lineartdead' + cat_sprite], (0, 0))

    return finished_sprite

def create_eyes(cat_sprite, colors, num):
    finished_sprite = pygame.Surface(
        (sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA
    )
    eye_base = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
    eye_base.fill(colors["base"])

    eye_s = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
    eye_s.fill(colors["shade"])

    eye_p = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
    eye_p.fill(colors["pupil"])

    if "shine" in colors:
        eye_sh = pygame.Surface((sprites.size, sprites.size)).convert_alpha()
        eye_sh.fill(colors["shine"])
    else:
        eye_sh = False


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

    # draw shine
    if eye_sh:
        eye_shine = sprites.sprites[f'eyes{num}' + 'shine' + cat_sprite].copy()
        eye_shine.blit(eye_sh, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        eye_shine.blit(sprites.sprites[f'eyes{num}' + 'shine' + cat_sprite], (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        eyes.blit(eye_shine, (0, 0))

    finished_sprite.blit(eyes, (0, 0))

    return finished_sprite

def update_sprite(cat):
    # First, check if the cat is faded.
    if cat.faded:
        # Don't update the sprite if the cat is faded.
        return

    # apply
    cat.sprite = generate_sprite(cat)
    # update class dictionary
    cat.all_cats[cat.ID] = cat


def update_mask(cat):
    if cat.faded or cat.dead:
        # should never need a mask since they can't appear on the Clan screen
        cat.sprite_mask = None
        return

    val = pygame.mask.from_surface(
        pygame.transform.scale(cat.sprite, ui_scale_dimensions((50, 50))), threshold=250
    )

    inflated_mask = pygame.Mask(
        (
            val.get_size()[0] + 10,
            val.get_size()[1] + 10,
        )
    )
    inflated_mask.draw(val, (5, 5))
    for _ in range(3):
        outline = inflated_mask.outline()
        for point in outline:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    try:
                        inflated_mask.set_at((point[0] + dx, point[1] + dy), 1)
                    except IndexError:
                        continue
    cat.sprite_mask = inflated_mask
