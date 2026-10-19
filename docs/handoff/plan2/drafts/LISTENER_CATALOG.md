# Listener catalog (plan 2 N6 draft; content lands in W2)

The mini-boss listeners CONTENT_DESIGN_V2 names, as N6's `ListenerData` would author them. Rulings: Q8 a (Echo is a
percent of the landed slice, Clawback is flat, each fires once per Perfect slice at resolve, at most once per turn per
listener; Shadow mirrors nudges only; no Favor while a Verdict is active), Q39 (SANDBOX charges negate listener
damage), N1b (FLAT listener damage x the tier factor). Unauthored per-turn cap: `listener_max_per_turn_default` (1).

| Listener | Owner (phase) | Trigger | Effect | Caps | Gap before W2 can author it |
|---|---|---|---|---|---|
| Late Fee | Account Manager (P1) | ON_RAM_SPENT | GAIN_BLOCK 2, SELF (FLAT x tier factor) | per turn: default 1 (or authored) | "per paid nudge": ON_RAM_SPENT also hears cards and respins. Either accept any RAM spend, or add a nudge-only filter (context has `action`). |
| Clawback | Account Manager (P2, on the P2 Hub) | ON_PERFECT | DEAL_DAMAGE 4, TARGET_WHEEL (FLAT x tier factor) | per turn: 1 (Q8 a) | none: buildable now (P2 `hub_override` carries it). |
| Echo | The Handler (P2) | ON_PERFECT | DEAL_DAMAGE 50 % of the landed slice | per turn: 1 (Q8 a) | an amount source reading the ON_PERFECT context `trigger_amount` (the landed output); PERCENT today reads the owner's max HP. |
| Shadow | The Handler (P1) | ON_NUDGE | NUDGE OWN_WHEEL, direction of the player's nudge | per turn: authored (one per nudge) | own-wheel only: the context carries `action` (direction, wheel id); a filter "player nudged its own wheel" is not built. |
| Favor / Verdict | Aurelian HQ (meter) | n/a | run meter, not a combat listener | n/a | its own pass (Q8 a: no Favor gain while a Verdict is active). |
