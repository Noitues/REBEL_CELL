class_name CardArt
extends RefCounted
## Card presentation data (ART_BIBLE 6.3, 7.3; W4): the card type a card's colour stands
## for, and the effect family its illustration is drawn from. Reads content only; pure
## presentation, deterministic, no RNG.

## Card types (ART_BIBLE 6.3: card colour means card type). The value is the ZineCard
## Variant the type is printed on: WHEEL cards on paper, SYSTEM cards on black, HACK cards
## on pink.
enum Type { WHEEL, SYSTEM, HACK }
## The sticker stock (ZineCard.Variant: PAPER 0, BLACK 1, PINK 2) of each type.
const TYPE_VARIANT := {Type.WHEEL: 0, Type.SYSTEM: 1, Type.HACK: 2}
## The type's name and its stock in words (the detail view and the codex say which).
const TYPE_WORDS := {Type.WHEEL: "WHEEL CARD", Type.SYSTEM: "SYSTEM CARD", Type.HACK: "HACK CARD"} # TR
const TYPE_STOCK_WORDS := {Type.WHEEL: "paper", Type.SYSTEM: "black", Type.HACK: "pink"} # TR
## What each type does, one line (the detail view's type row).
const TYPE_TEXT := {Type.WHEEL: "Moves wheels: spins, nudges, flips, snaps and freezes.", # TR
	Type.SYSTEM: "Runs your rig: block, shield, healing, RAM and cards.", # TR
	Type.HACK: "Attacks the target: damage, statuses, breaches and stripped resistance."} # TR

## The statuses that harm the slice they land on (a HACK card applies them).
const HARMFUL_STATUSES: Array[int] = [RC.Status.CORRUPTED, RC.Status.PARASITE]


## The card's type from its first effect (its primary one). Null or effectless: WHEEL.
static func type_of(card: CardData) -> int:
	if card == null:
		return Type.WHEEL
	for e in card.effects:
		if e == null:
			continue
		return _type_of_effect(e)
	return Type.WHEEL


static func _type_of_effect(e: EffectData) -> int:
	match e.type:
		RC.EffectType.DEAL_DAMAGE:
			return Type.SYSTEM if e.target == RC.EffectTarget.SELF else Type.HACK
		RC.EffectType.APPLY_STATUS:
			return Type.HACK if HARMFUL_STATUSES.has(e.status) else Type.SYSTEM
		RC.EffectType.HUB_BREACH, RC.EffectType.DRAIN_RAM:
			return Type.HACK
		RC.EffectType.MODIFY_RESISTANCE:
			return Type.HACK if e.amount < 0 else Type.SYSTEM
		RC.EffectType.GAIN_BLOCK, RC.EffectType.GAIN_SHIELD, RC.EffectType.EVADE, RC.EffectType.HEAL, \
				RC.EffectType.CLEANSE, RC.EffectType.GAIN_RAM, RC.EffectType.DRAW_CARDS, RC.EffectType.DEPLOY_DRONE, \
				RC.EffectType.MODIFY_HEAT, RC.EffectType.GAIN_CYCLES, RC.EffectType.GAIN_SCHEMATICS:
			return Type.SYSTEM
		RC.EffectType.CUSTOM:
			if e.custom_handler != null and e.custom_handler.resource_path.get_file().get_basename() == "steady_hand_handler":
				return Type.SYSTEM
	return Type.WHEEL


## The ZineCard.Variant (stock colour) a card is printed on.
static func variant_of(card: CardData) -> int:
	return int(TYPE_VARIANT[type_of(card)])
