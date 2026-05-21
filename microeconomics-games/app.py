import streamlit as st
import pandas as pd
from dataclasses import dataclass

st.set_page_config(
    page_title="Market Games — Équilibre de Nash",
    page_icon="🎲",
    layout="wide",
)

EPS = 1e-6


# ============================================================
#  Modèle du jeu
# ============================================================

@dataclass
class GameScenario:
    title: str
    icon: str
    tagline: str
    action_1: str  # ex: "Casser les prix"
    action_2: str  # ex: "Maintenir les prix"
    payoffs: dict  # (i, j) -> (gain_A, gain_B), i = action de A, j = action de B
    real_world: str
    intuition: str

    def label(self, idx: int) -> str:
        return self.action_1 if idx == 0 else self.action_2

    def find_nash(self) -> list:
        """Équilibres de Nash en stratégie pure."""
        nash = []
        for i in (0, 1):
            for j in (0, 1):
                if self.payoffs[(1 - i, j)][0] > self.payoffs[(i, j)][0] + EPS:
                    continue
                if self.payoffs[(i, 1 - j)][1] > self.payoffs[(i, j)][1] + EPS:
                    continue
                nash.append((i, j))
        return nash

    def find_pareto(self) -> list:
        """Issues Pareto-optimales (non dominées)."""
        cells = [(i, j) for i in (0, 1) for j in (0, 1)]
        pareto = []
        for c in cells:
            a, b = self.payoffs[c]
            dominated = any(
                (self.payoffs[o][0] >= a - EPS and self.payoffs[o][1] >= b - EPS)
                and (self.payoffs[o][0] > a + EPS or self.payoffs[o][1] > b + EPS)
                for o in cells
                if o != c
            )
            if not dominated:
                pareto.append(c)
        return pareto

    def best_response_a(self, j: int) -> int:
        return 0 if self.payoffs[(0, j)][0] >= self.payoffs[(1, j)][0] else 1

    def best_response_b(self, i: int) -> int:
        return 0 if self.payoffs[(i, 0)][1] >= self.payoffs[(i, 1)][1] else 1


# ============================================================
#  Constructeurs de scénarios
# ============================================================

def build_price_war() -> GameScenario:
    st.sidebar.subheader("💰 Variables — Guerre des prix")
    st.sidebar.caption("Duopole de Bertrand : mêmes clients, peu de différenciation.")

    marge_normale = st.sidebar.slider(
        "Marge si entente tacite (M€)", 5, 20, 12,
        help="Profit si les deux maintiennent leurs prix hauts.",
    )
    perte_guerre = st.sidebar.slider(
        "Perte de marge si guerre des prix (M€)", 1, 10, 6,
        help="De combien la marge fond quand les deux baissent leurs prix.",
    )
    gain_monopole = st.sidebar.slider(
        "Gain si seul à baisser (M€)", 5, 25, 16,
        help="Profit si vous baissez vos prix et que le concurrent ne suit pas.",
    )
    perte_perdant = st.sidebar.slider(
        "Marge si vous maintenez et concurrent baisse (M€)", 0, 5, 1,
        help="Vous perdez vos clients au profit du moins cher.",
    )

    return GameScenario(
        title="La guerre des prix",
        icon="⚔️",
        tagline="Uber vs Bolt, Ryanair vs EasyJet : à qui le bras de fer profite-t-il ?",
        action_1="Casser les prix",
        action_2="Maintenir les prix",
        payoffs={
            (0, 0): (marge_normale - perte_guerre, marge_normale - perte_guerre),
            (0, 1): (gain_monopole, perte_perdant),
            (1, 0): (perte_perdant, gain_monopole),
            (1, 1): (marge_normale, marge_normale),
        },
        real_world=(
            "**Uber vs Bolt** à Paris (2018-2020) : courses à 5 €, des millions brûlés "
            "sans qu'aucun ne décroche durablement.\n\n"
            "**Ryanair vs EasyJet** : marges écrasées sur les lignes en concurrence, "
            "profits réels uniquement sur les lignes en monopole."
        ),
        intuition=(
            "Si vous maintenez vos prix et que le concurrent baisse, vous perdez tout. "
            "Pour s'en protéger, vous baissez aussi. **Résultat : tout le monde perd.** "
            "C'est le dilemme du prisonnier appliqué au pricing."
        ),
    )


def build_hotelling() -> GameScenario:
    st.sidebar.subheader("🎨 Variables — Innover vs copier")
    st.sidebar.caption("Modèle de Hotelling : différencier ou converger vers le centre.")

    marche_total = st.sidebar.slider(
        "Taille totale du marché (M€)", 10, 50, 24,
        help="Chiffre d'affaires total à se partager.",
    )
    cout_innovation = st.sidebar.slider(
        "Coût de R&D pour innover (M€)", 1, 15, 4,
        help="Investissement nécessaire pour développer un produit différencié.",
    )
    part_innovateur = st.sidebar.slider(
        "Part de marché de l'innovateur seul (%)", 50, 90, 70,
        help="Si vous innovez seul, quelle fraction du marché vous captez.",
    ) / 100.0

    return GameScenario(
        title="Innover ou copier",
        icon="🎨",
        tagline="Pourquoi tant de smartphones de milieu de gamme se ressemblent.",
        action_1="Copier (statu quo)",
        action_2="Innover (différencier)",
        payoffs={
            (0, 0): (marche_total / 2, marche_total / 2),
            (0, 1): (
                marche_total * (1 - part_innovateur),
                marche_total * part_innovateur - cout_innovation,
            ),
            (1, 0): (
                marche_total * part_innovateur - cout_innovation,
                marche_total * (1 - part_innovateur),
            ),
            (1, 1): (
                marche_total / 2 - cout_innovation,
                marche_total / 2 - cout_innovation,
            ),
        },
        real_world=(
            "**Smartphones milieu de gamme** : la plupart des Android se ressemblent → tout le monde copie.\n\n"
            "**Pizza Hut vs Domino's** : positionnement quasi identique.\n\n"
            "Quand quelqu'un innove vraiment (iPhone, Tesla), il rafle une rente temporaire — "
            "jusqu'à ce que les autres copient."
        ),
        intuition=(
            "Innover coûte cher et peut être copié. Copier est sûr mais le marché stagne. "
            "L'équilibre dépend du **ratio coût d'innovation / taille du marché**. "
            "Augmentez le coût : tout le monde copie. Réduisez-le : tout le monde innove."
        ),
    )


def build_rnd_race() -> GameScenario:
    st.sidebar.subheader("🧪 Variables — Course à la R&D")
    st.sidebar.caption("Pharma, semi-conducteurs, IA : investir ou être balayé.")

    valeur_brevet = st.sidebar.slider(
        "Valeur du brevet / blockbuster (M€)", 10, 50, 30,
        help="Profit total si vous êtes seul à sortir le produit.",
    )
    cout_recherche = st.sidebar.slider(
        "Coût d'entrée en R&D (M€)", 3, 20, 8,
        help="Investissement minimum pour rester dans la course.",
    )
    marge_residuelle = st.sidebar.slider(
        "Marge si vous abandonnez la R&D (M€)", 0, 5, 1,
        help="Vos miettes si vous laissez le concurrent rafler le brevet.",
    )
    marche_sans_rd = st.sidebar.slider(
        "Marché partagé si aucun n'investit (M€)", 2, 15, 6,
        help="Marché stagne, mais pas de coûts de R&D. Partagé 50/50.",
    )

    return GameScenario(
        title="Course à la R&D",
        icon="🧪",
        tagline="Pharma, IA, semi-conducteurs : investir ou disparaître.",
        action_1="Investir en R&D",
        action_2="Réduire la R&D",
        payoffs={
            (0, 0): (
                valeur_brevet / 2 - cout_recherche,
                valeur_brevet / 2 - cout_recherche,
            ),
            (0, 1): (valeur_brevet - cout_recherche, marge_residuelle),
            (1, 0): (marge_residuelle, valeur_brevet - cout_recherche),
            (1, 1): (marche_sans_rd / 2, marche_sans_rd / 2),
        },
        real_world=(
            "**Pfizer vs Moderna** sur les vaccins COVID : course folle, le premier rafle le marché.\n\n"
            "**NVIDIA vs AMD vs Intel** sur les puces IA : investissements colossaux, "
            "celui qui ralentit est balayé en 18 mois.\n\n"
            "**Big Pharma** : 80 % des projets échouent, mais le 1 blockbuster paie les 79 autres."
        ),
        intuition=(
            "Si l'un investit et l'autre pas, le perdant disparaît. "
            "Pour éviter ce risque, **tout le monde investit** — quitte à exploser ses coûts. "
            "Course aux armements : impossible de freiner unilatéralement."
        ),
    )


# ============================================================
#  Rendu
# ============================================================

st.title("📈 Market Games — l'équilibre de Nash en action")
st.markdown(
    "*La théorie des jeux appliquée aux stratégies d'entreprise. "
    "Ajustez les paramètres et observez l'équilibre se déplacer en temps réel.*"
)

with st.expander("🎓 Rappel — c'est quoi un équilibre de Nash ?"):
    st.markdown(
        """
Un **équilibre de Nash** est une situation où **aucun joueur n'a intérêt à changer
unilatéralement sa stratégie**, en supposant que l'autre garde la sienne.

**Comment le repérer dans la matrice ?**
1. Pour chaque case, demandez-vous : *« Si je suis A, est-ce que je gagnerais
   plus en changeant de ligne ? »*
2. Posez la même question pour B (changer de colonne).
3. Si **aucun des deux ne veut bouger** → c'est un équilibre de Nash.

**À ne pas confondre avec :**
- **L'optimum de Pareto** : la meilleure issue collective. Parfois différente du Nash !
- **Une stratégie dominante** : une stratégie meilleure quoi que fasse l'autre.

L'apport de Nash : montrer que **l'équilibre individuellement rationnel n'est
pas toujours collectivement optimal**.
"""
    )

st.markdown("---")

# Choix du scénario
SCENARIOS = {
    "⚔️ Guerre des prix": build_price_war,
    "🎨 Innover ou copier": build_hotelling,
    "🧪 Course à la R&D": build_rnd_race,
}

choice = st.radio(
    "🎯 Scénario de marché",
    list(SCENARIOS.keys()),
    horizontal=True,
)

game = SCENARIOS[choice]()
nash = game.find_nash()
pareto = game.find_pareto()

st.subheader(f"{game.icon} {game.title}")
st.caption(game.tagline)

# ---------- Layout principal ----------

left, right = st.columns([3, 2], gap="large")

with left:
    st.markdown("##### 🎲 Matrice des gains")
    st.caption(
        "Format : (gain de A, gain de B) en M€ — "
        "🔴 Nash • 🟢 Pareto-optimal • 🟣 les deux"
    )

    def cell_str(i: int, j: int) -> str:
        a, b = game.payoffs[(i, j)]
        markers = []
        is_nash = (i, j) in nash
        is_pareto = (i, j) in pareto
        if is_nash and is_pareto:
            markers.append("🟣")
        elif is_nash:
            markers.append("🔴")
        elif is_pareto:
            markers.append("🟢")
        marker = " ".join(markers)
        return f"({a:.1f} ; {b:.1f}) {marker}".strip()

    cols = {
        f"B : {game.action_1}": [cell_str(0, 0), cell_str(1, 0)],
        f"B : {game.action_2}": [cell_str(0, 1), cell_str(1, 1)],
    }
    df = pd.DataFrame(
        cols,
        index=[f"A : {game.action_1}", f"A : {game.action_2}"],
    )

    def style_cells(val: str) -> str:
        if "🟣" in val:
            return "background-color: #e9d5ff; font-weight: 700; color: #4c1d95;"
        if "🔴" in val:
            return "background-color: #fecaca; font-weight: 700; color: #7f1d1d;"
        if "🟢" in val:
            return "background-color: #bbf7d0; font-weight: 600; color: #14532d;"
        return "color: #475569;"

    st.dataframe(
        df.style.applymap(style_cells),
        use_container_width=True,
    )

    # Verdict synthétique
    if len(nash) == 1:
        i, j = nash[0]
        a, b = game.payoffs[(i, j)]
        if (i, j) in pareto:
            st.success(
                f"✅ **Équilibre de Nash unique = Optimum de Pareto** : "
                f"A joue *{game.label(i)}*, B joue *{game.label(j)}* "
                f"→ ({a:.1f} ; {b:.1f}) M€. Tout le monde est gagnant."
            )
        else:
            best_total = max(
                game.payoffs[c][0] + game.payoffs[c][1] for c in pareto
            )
            current_total = a + b
            gap = best_total - current_total
            st.warning(
                f"⚠️ **Piège du dilemme** : l'équilibre de Nash "
                f"(*{game.label(i)}*, *{game.label(j)}*) rapporte {current_total:.1f} M€ au total, "
                f"alors qu'une coopération atteindrait {best_total:.1f} M€ "
                f"({gap:.1f} M€ détruits par la rationalité individuelle)."
            )
    elif len(nash) > 1:
        st.info(
            f"🎯 **{len(nash)} équilibres de Nash** coexistent : "
            + ", ".join(f"*({game.label(i)}, {game.label(j)})*" for i, j in nash)
            + ". Le résultat dépendra de la coordination ou des croyances."
        )
    else:
        st.info("🔄 **Aucun équilibre en stratégie pure** : il existe un équilibre en stratégies mixtes.")

    with st.expander("🔎 Voir le raisonnement étape par étape"):
        st.markdown(f"**Meilleure réponse de A selon ce que joue B :**")
        for j in (0, 1):
            br = game.best_response_a(j)
            other = 1 - br
            st.write(
                f"• Si B joue *{game.label(j)}* → A préfère "
                f"**{game.label(br)}** ({game.payoffs[(br, j)][0]:.1f} M€) "
                f"plutôt que {game.label(other)} ({game.payoffs[(other, j)][0]:.1f} M€)"
            )
        st.markdown(f"**Meilleure réponse de B selon ce que joue A :**")
        for i in (0, 1):
            br = game.best_response_b(i)
            other = 1 - br
            st.write(
                f"• Si A joue *{game.label(i)}* → B préfère "
                f"**{game.label(br)}** ({game.payoffs[(i, br)][1]:.1f} M€) "
                f"plutôt que {game.label(other)} ({game.payoffs[(i, other)][1]:.1f} M€)"
            )
        st.markdown(
            "L'équilibre de Nash est l'intersection : une case où **les deux** "
            "meilleures réponses se rencontrent."
        )

with right:
    st.markdown("##### 💡 L'intuition")
    st.info(game.intuition)

    st.markdown("##### 🌍 Dans la vraie vie")
    st.markdown(game.real_world)

    if nash and pareto:
        st.markdown("##### 📊 Profit total — Nash vs coopération")
        nash_cell = nash[0]
        pareto_cell = max(pareto, key=lambda c: sum(game.payoffs[c]))
        bar_df = pd.DataFrame(
            {
                "A": [game.payoffs[nash_cell][0], game.payoffs[pareto_cell][0]],
                "B": [game.payoffs[nash_cell][1], game.payoffs[pareto_cell][1]],
            },
            index=["Nash", "Coopération"],
        )
        st.bar_chart(bar_df, height=220)

st.markdown("---")

# ---------- Mode interactif ----------

st.markdown("##### 🎮 À vous de jouer — vous êtes le CEO de l'entreprise A")
st.caption(
    "Choisissez votre stratégie. L'entreprise B joue sa **meilleure réponse** "
    "à votre choix (B est rationnelle)."
)

play_left, play_mid, play_right = st.columns([1, 1, 2])

with play_left:
    choice_label = st.radio(
        "Votre choix",
        [game.action_1, game.action_2],
        key=f"player_choice_{choice}",
    )

your_choice = 0 if choice_label == game.action_1 else 1
opp_choice = game.best_response_b(your_choice)
your_payoff, opp_payoff = game.payoffs[(your_choice, opp_choice)]

with play_mid:
    st.metric("Réponse de B", game.label(opp_choice))
    st.metric("Votre gain (A)", f"{your_payoff:.1f} M€")
    st.metric("Gain de B", f"{opp_payoff:.1f} M€")

with play_right:
    alt_choice = 1 - your_choice
    alt_opp = game.best_response_b(alt_choice)
    alt_payoff = game.payoffs[(alt_choice, alt_opp)][0]
    delta = alt_payoff - your_payoff

    if delta > EPS:
        st.error(
            f"💸 **Vous auriez gagné {delta:.1f} M€ de plus** en jouant "
            f"*{game.label(alt_choice)}* (B aurait répondu *{game.label(alt_opp)}*, "
            f"vous auriez touché {alt_payoff:.1f} M€).\n\n"
            f"👉 Votre choix actuel n'est **pas une meilleure réponse** au jeu de B."
        )
    elif delta < -EPS:
        st.success(
            f"✅ **Bon choix !** L'alternative (*{game.label(alt_choice)}*) "
            f"vous aurait coûté {-delta:.1f} M€. "
            f"Vous jouez votre meilleure réponse."
        )
    else:
        st.info("⚖️ Les deux choix donnent le même résultat — vous êtes indifférent.")

    if (your_choice, opp_choice) in nash:
        st.caption("🔴 Vous êtes sur l'équilibre de Nash.")
    if (your_choice, opp_choice) in pareto:
        st.caption("🟢 Vous êtes sur un optimum de Pareto.")

st.markdown("---")
st.caption(
    "💡 **Astuce :** jouez avec les sliders de la sidebar. "
    "Dans le scénario *Innover ou copier*, augmentez le coût de R&D : "
    "vous verrez l'équilibre basculer d'un marché d'innovateurs vers un marché de copieurs."
)
