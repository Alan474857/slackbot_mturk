import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import typer
import numpy as np
from collections import Counter

app = typer.Typer()

def get_setting(
    series: pd.Series
) -> str:
    """
    Get the experiment setting name from the series

    q_id: 1-20, user_id: 4-11, mode: A => MultiSlack (N=5), High Converasbility
    q_id: 1-20, user_id: 12-19, mode: A => MultiSlack (N=7), High Converasbility
    q_id: 1-20, user_id: 20-27, mode: A  => MultiSlack (N=3), High Converasbility
    q_id: 1-20, user_id: 4-27, mode: B => SlackVanilla (No Conversation), High Converasbility
    q_id: 21-40, user_id: 4-11, mode: A => MultiSlack (N=5), Low Converasbility
    q_id: 21-40, user_id: 12-19, mode: A => MultiSlack (N=7), Low Converasbility
    q_id: 21-40, user_id: 20-27, mode: A => MultiSlack (N=3), Low Converasbility
    q_id: 21-40, user_id: 4-27, mode: B => SlackVanilla (No Conversation), Low Converasbility
    
    A	N=5	4-11
	    N=7	12-19
	    N=3	20-27
    B	N=1	
    """
    q_id = series["q_id"]
    user_id = series["user_id"]
    mode = series["mode"]

    conversation_type = "[High]" if q_id <= 20 else "[Low]"
    if mode == "A":
        if 4 <= user_id <= 11:
            return f"MultiSlack (N=5) {conversation_type}"
        elif 12 <= user_id <= 19:
            return f"MultiSlack (N=7) {conversation_type}"
        elif 20 <= user_id <= 27:
            return f"MultiSlack (N=3) {conversation_type}"
        else:
            raise ValueError(f"Invalid user_id: {user_id}")
    elif mode == "B":
        return f"SlackVanilla {conversation_type}"
    else:
        raise ValueError(f"Invalid mode: {mode}")


    # conversation_type = "High Converasbility" if q_id <= 20 else "Low Converasbility"
    # if mode == "A":
    #     if 4 <= user_id <= 11:
    #         return f"MultiSlack (N=5), {conversation_type}"
    #     elif 12 <= user_id <= 19:
    #         return f"MultiSlack (N=7), {conversation_type}"
    #     elif 20 <= user_id <= 27:
    #         return f"MultiSlack (N=3), {conversation_type}"
    #     else:
    #         raise ValueError(f"Invalid user_id: {user_id}")
    # elif mode == "B":
    #     return f"SlackVanilla (No Conversation), {conversation_type}"
    # else:
    #     raise ValueError(f"Invalid mode: {mode}")

@app.command()
def draw(
    input_path: Path = typer.Option(..., help="Path to input file"),
    output_path: Path = typer.Option(..., help="Path to output file"),
    aspect: str = typer.Option("helpfulness", help="Aspect to draw"),
):
    """
    helpfulness	quantity	relevance	repetitiveness	clarity	ambiguity
    """
    table = pd.read_excel(input_path)
    table["setting"] = table.apply(get_setting, axis=1)
    # turn to percentage with the order [1, 5]
    results = table.groupby(["setting"])[aspect].agg(list)
    def compute_percentage(ratings):
        count = Counter(ratings)
        print(count)
        x = np.array([count[i] for i in range(0, 5)])
        precentage = 100.0 * x / np.sum(x)
        # do rounding to no decimal but make sure it sums to 100
        precentage = np.round(precentage, 0)
        precentage[-1] = 100 - np.sum(precentage[:-1])
        return precentage
    
    results = results.apply(compute_percentage)
    # sort by the setting put high converasbility first, and then slackVanilla, and then multislack
    score_mapping = {
        "SlackVanilla": 0,
        "MultiSlack (N=3)": 1,
        "MultiSlack (N=5)": 2,
        "MultiSlack (N=7)": 3,
    }
    # results = results.sort_index(
    #     key=lambda x: x.str.contains("High")*(-100) + score_mapping[" ".join(str(x).split(" ")[:-1])],
    #     ascending=True,
    # )

    print(results)
    print(results.to_dict())
    results = results.to_dict()
    # reorder results
    results = {
        **{k: results[k] for k in results if "SlackVanilla" in k},
        **{k: results[k] for k in results if "SlackVanilla" not in k},
    }
    results = {
        **{k: results[k] for k in results if "High" in k},
        **{k: results[k] for k in results if "Low" in k},
    }


    if aspect == "quantity":
        category_names = ["Too Little", "Insufficient", "Appropriate", "Sufficient", "Too Much"]
    else:
        category_names = ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree']
    fig, ax = survey(results, category_names)
    plt.title(aspect.capitalize(), y=0.95, fontsize=20, fontweight='bold')
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.05)


def survey(results, category_names):
    """
    Parameters
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*.
    category_names : list of str
        The category labels.
    """
    plt.style.use('seaborn-v0_8-whitegrid')
    matplotlib.rcParams.update({
        "font.size": 16,
        "font.weight": "600",
    })

    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.colormaps['RdYlGn'](
        np.linspace(0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())
    ax.set_xlabel("Percentage of Responses")
    # remove border
    for spine in ax.spines.values():
        print(spine)
        spine.set_visible(False)

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        # print(colname, color)
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        current_labels = labels
        # current_labels = [
        #     f"{label}%"
        #     for label, width in zip(labels, widths)
        #     if width > 0
        # ]
        # widths = [
        #     width
        #     for width in widths
        #     if width > 0
        # ]
        # starts = [
        #     start
        #     for start, width in zip(starts, widths)
        #     if width > 0
        # ]
        rects = ax.barh(
            y=current_labels,
            width=widths,
            left=starts,
            height=0.90,
            label=colname,
            color=color,
        )

        r, g, b, _ = color
        text_color = 'black'
        for rect in rects:
            width = rect.get_width()
            if width > 3:
                x = rect.get_x() + rect.get_width() / 2
                y = rect.get_y() + rect.get_height() / 2
                ax.text(
                    x,
                    y,
                    f"{int(width)}%",
                    ha='center',
                    va='center',
                    color=text_color,
                    fontsize='small',
                )
        # ax.bar_label(rects, label_type='center', color=text_color)

    ax.legend(
        ncols=len(category_names),
        # bbox_to_anchor=(-0.02, 1),
        bbox_to_anchor=(-0.3, -0.07),
        loc='lower left',
        # fontsize='small'
        prop={'size': 13},
        frameon=True,
        fancybox=True,
    )

    return fig, ax




if __name__ == "__main__":
    app()