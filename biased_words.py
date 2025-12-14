import re


biased_dict_raw = {
    ("career girl", "career man"): ["professional", "manager", "executive"],
    "chairman": ["chairperson", "chair"],
    "mankind": ["humankind"],
    "cleaning lady": ["cleaner"],
    "delivery boy": ["courier", "messenger"],
    "manpower": ["workforce"],
    "salesman": ["salesperson", "sales associate"]
}


biased_dict = {}
for k, v in biased_dict_raw.items():
    if isinstance(k, tuple):
        for phrase in k:
            biased_dict[phrase] = v
    else:
        biased_dict[k] = v


sorted_keys = sorted(biased_dict.keys(), key=len, reverse=True)

parts = []
group_to_key = {}
for i, key in enumerate(sorted_keys):

    escaped = re.escape(key).replace(r'\ ', r'\s+')
    group_name = f"K{i}"
    parts.append(fr"(?<!\w)(?P<{group_name}>{escaped})(?!\w)")
    group_to_key[group_name] = key


pattern = re.compile("|".join(parts), flags=re.IGNORECASE)



def highlight_text(text):
    """
    Highlight biased words/phrases and return:
    - highlighted HTML string
    - set of suggestions (dictionary key, replacements)
    """
    suggestions = set()

    def _repl(match):
        g = match.lastgroup
        key = group_to_key[g]
        matched = match.group(0)

        replacement = biased_dict[key]
        suggestions.add((key, tuple(replacement)))

        return f"<span style='background-color: yellow; font-weight:bold;'>{matched}</span>"

    highlighted = pattern.sub(_repl, text)
    return highlighted, suggestions
